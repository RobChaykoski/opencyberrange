"""LDAP and Active Directory authentication adapter.

The adapter performs a service bind, searches for exactly one user, then
rebinds as that user to verify the supplied password. The user's DN is the
stable subject used for account linking.
"""

from __future__ import annotations

import logging
import ssl
from urllib.parse import urlparse

from ldap3 import NONE, SUBTREE, Connection, Server, Tls
from ldap3.core.exceptions import LDAPException
from ldap3.utils.conv import escape_filter_chars

from app.config import settings
from app.models import IdentityProvider
from app.services.external_identity import (
    SSOError,
    ExternalUser,
    provider_config,
    provider_secrets,
)

logger = logging.getLogger(__name__)

BASE_ATTRIBUTES = (
    "cn",
    "displayName",
    "givenName",
    "sn",
    "mail",
    "uid",
    "sAMAccountName",
    "userPrincipalName",
    "memberOf",
)


def _config_value(config: dict, key: str, default: str = "") -> str:
    value = config.get(key, default)
    return str(value).strip() if value is not None else default


def _timeout(config: dict) -> int:
    try:
        return max(1, min(60, int(config.get("timeout_seconds", settings.SSO_HTTP_TIMEOUT_SECONDS))))
    except (TypeError, ValueError):
        return settings.SSO_HTTP_TIMEOUT_SECONDS


def _connection(provider: IdentityProvider) -> Connection:
    config = provider_config(provider)
    secrets_ = provider_secrets(provider)
    raw_url = _config_value(config, "server_url")
    parsed = urlparse(raw_url)
    if parsed.scheme not in {"ldap", "ldaps"} or not parsed.hostname:
        raise SSOError("The LDAP server URL is not valid.", code="unavailable")

    use_ssl = parsed.scheme == "ldaps"
    try:
        port = parsed.port or (636 if use_ssl else 389)
    except ValueError as exc:
        raise SSOError("The LDAP server URL is not valid.", code="unavailable") from exc
    if (
        not use_ssl
        and not bool(config.get("start_tls", False))
        and not bool(config.get("allow_plaintext", False))
        and not settings.SSO_ALLOW_INSECURE_HTTP
    ):
        raise SSOError(
            "LDAP requires ldaps:// or StartTLS. Set allow_plaintext only for an "
            "isolated lab network.",
            code="unavailable",
        )
    verify = bool(config.get("tls_verify", True))
    tls = Tls(validate=ssl.CERT_REQUIRED if verify else ssl.CERT_NONE)
    bind_dn = _config_value(config, "bind_dn")
    bind_password = str(secrets_.get("bind_password") or "")

    connection: Connection | None = None
    try:
        server = Server(
            parsed.hostname,
            port=port,
            use_ssl=use_ssl,
            get_info=NONE,
            connect_timeout=_timeout(config),
            tls=tls,
        )
        connection = Connection(
            server,
            user=bind_dn or None,
            password=bind_password or None,
            auto_bind=False,
            auto_referrals=False,
            receive_timeout=_timeout(config),
            raise_exceptions=False,
        )
        connection.open()
        if connection.closed:
            raise SSOError("Could not connect to the LDAP server.", code="unavailable")
        if bool(config.get("start_tls", False)):
            if use_ssl:
                raise SSOError(
                    "StartTLS cannot be used with an ldaps:// URL.", code="unavailable"
                )
            if not connection.start_tls():
                raise SSOError(
                    "Could not start TLS on the LDAP connection.", code="unavailable"
                )
    except SSOError:
        if connection is not None:
            try:
                connection.unbind()
            except Exception:
                pass
        raise
    except Exception as exc:
        if connection is not None:
            try:
                connection.unbind()
            except Exception:
                pass
        raise SSOError("Could not connect to the LDAP server.", code="unavailable") from exc
    return connection


def _attribute_names(config: dict) -> list[str]:
    names = {
        *BASE_ATTRIBUTES,
        _config_value(config, "email_attribute", "mail"),
        _config_value(config, "username_attribute", "uid"),
        _config_value(config, "first_name_attribute", "givenName"),
        _config_value(config, "last_name_attribute", "sn"),
        _config_value(config, "display_name_attribute", "cn"),
        _config_value(config, "group_attribute", "memberOf"),
    }
    return sorted({name for name in names if name})


def _attribute_map(entry) -> dict[str, list[str]]:
    try:
        raw = entry.entry_attributes_as_dict or {}
    except Exception:
        raw = {}
    result: dict[str, list[str]] = {}
    for name, values in raw.items():
        key = str(name).lower()
        if values is None:
            result[key] = []
        elif isinstance(values, (list, tuple)):
            result[key] = [str(value) for value in values if value is not None]
        else:
            result[key] = [str(values)]
    return result


def _first(attributes: dict[str, list[str]], name: str) -> str:
    if not name:
        return ""
    values = attributes.get(name.lower()) or []
    return str(values[0]).strip() if values else ""


def _search_user(connection: Connection, config: dict, username: str) -> dict | None:
    base_dn = _config_value(config, "base_dn")
    template = _config_value(config, "user_search_filter", "(uid={username})")
    search_filter = template.replace("{username}", escape_filter_chars(username))
    try:
        found = connection.search(
            search_base=base_dn,
            search_filter=search_filter,
            search_scope=SUBTREE,
            attributes=_attribute_names(config),
            size_limit=2,
            time_limit=_timeout(config),
        )
    except LDAPException as exc:
        raise SSOError("The LDAP user search failed.", code="unavailable") from exc
    if not found or not connection.entries:
        return None
    if len(connection.entries) > 1:
        raise SSOError(
            "The LDAP search matched more than one account. "
            "Make the user search filter more specific."
        )
    entry = connection.entries[0]
    return {"dn": entry.entry_dn, "attributes": _attribute_map(entry)}


def authenticate(
    provider: IdentityProvider,
    username: str,
    password: str,
) -> ExternalUser:
    """Verify a username/password against the directory and return its identity."""
    username = (username or "").strip()
    password = password or ""
    if not username or not password:
        raise SSOError("Enter your username and password.", code="invalid_credentials")

    config = provider_config(provider)
    connection = _connection(provider)
    try:
        if not connection.bind():
            raise SSOError(
                "The LDAP service account could not bind.", code="unavailable"
            )
        entry = _search_user(connection, config, username)
        if entry is None:
            raise SSOError("Invalid username or password.", code="invalid_credentials")
        try:
            if not connection.rebind(user=entry["dn"], password=password):
                raise SSOError(
                    "Invalid username or password.", code="invalid_credentials"
                )
        except LDAPException as exc:
            raise SSOError(
                "Invalid username or password.", code="invalid_credentials"
            ) from exc

        attributes = entry["attributes"]
        email = _first(attributes, _config_value(config, "email_attribute", "mail"))
        if not email:
            raise SSOError("The LDAP account does not have an email address.")
        first_name = _first(
            attributes, _config_value(config, "first_name_attribute", "givenName")
        ) or None
        last_name = _first(
            attributes, _config_value(config, "last_name_attribute", "sn")
        ) or None
        display_name = _first(
            attributes, _config_value(config, "display_name_attribute", "cn")
        ) or None
        username_hint = _first(
            attributes, _config_value(config, "username_attribute", "uid")
        ) or username
        groups = attributes.get(
            _config_value(config, "group_attribute", "memberOf").lower(), []
        )
        return ExternalUser(
            subject=entry["dn"],
            email=email,
            email_verified=True,
            username_hint=username_hint,
            first_name=first_name,
            last_name=last_name,
            name=display_name,
            groups=list(groups),
        )
    except SSOError:
        raise
    except LDAPException as exc:
        logger.warning("LDAP login failed for provider %s: %s", provider.name, exc)
        raise SSOError("The LDAP directory is unavailable.", code="unavailable") from exc
    finally:
        try:
            connection.unbind()
        except Exception:
            pass


def test_provider(provider: IdentityProvider) -> dict:
    """Bind with the configured service account and report basic directory facts."""
    config = provider_config(provider)
    connection = _connection(provider)
    try:
        if not connection.bind():
            raise SSOError(
                "The LDAP service account could not bind.", code="unavailable"
            )
        base_dn = _config_value(config, "base_dn")
        searched = False
        try:
            searched = bool(
                connection.search(
                    search_base=base_dn,
                    search_filter="(objectClass=*)",
                    search_scope=SUBTREE,
                    attributes=["objectClass"],
                    size_limit=1,
                    time_limit=_timeout(config),
                )
            )
        except LDAPException:
            searched = False
        if not searched:
            raise SSOError(
                "The LDAP service account could not search the base DN.",
                code="unavailable",
            )
        return {
            "message": (
                f"LDAP bind OK · {_config_value(config, 'server_url')} · "
                f"base {base_dn}"
            ),
            "server_url": _config_value(config, "server_url"),
            "base_dn": base_dn,
            "search_ok": searched,
        }
    except SSOError:
        raise
    except LDAPException as exc:
        logger.warning("LDAP provider test failed for %s: %s", provider.name, exc)
        raise SSOError("The LDAP directory is unavailable.") from exc
    finally:
        try:
            connection.unbind()
        except Exception:
            pass
