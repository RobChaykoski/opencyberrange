"""SAML 2.0 service-provider adapter built on python3-saml.

The platform is the service provider. Login is SP-initiated: the AuthnRequest
ID and RelayState are stored in PostgreSQL so any API replica can process the
assertion at the ACS.
"""

from __future__ import annotations

import logging
from urllib.parse import urlparse

from onelogin.saml2.auth import OneLogin_Saml2_Auth
from onelogin.saml2.errors import OneLogin_Saml2_Error
from onelogin.saml2.settings import OneLogin_Saml2_Settings

from app.config import settings
from app.models import IdentityProvider
from app.services.external_identity import (
    SSOError,
    ExternalUser,
    provider_config,
    provider_secrets,
)
from app.services.sso_flow import public_base_url

logger = logging.getLogger(__name__)

SSO_BINDING = "urn:oasis:names:tc:SAML:2.0:bindings:HTTP-Redirect"
SLO_BINDING = "urn:oasis:names:tc:SAML:2.0:bindings:HTTP-Redirect"
ACS_BINDING = "urn:oasis:names:tc:SAML:2.0:bindings:HTTP-POST"
DEFAULT_NAME_ID_FORMAT = "urn:oasis:names:tc:SAML:1.1:nameid-format:emailAddress"


def _value(config: dict, key: str, default: str = "") -> str:
    value = config.get(key, default)
    return str(value).strip() if value is not None else default


def resolved_acs_url(provider: IdentityProvider) -> str:
    config = provider_config(provider)
    configured = _value(config, "acs_url")
    if configured:
        return configured
    return f"{public_base_url()}/api/auth/sso/saml/{provider.id}/acs"


def settings_dict(provider: IdentityProvider) -> dict:
    """Build the python3-saml settings object for one provider."""
    config = provider_config(provider)
    secrets_ = provider_secrets(provider)
    acs_url = resolved_acs_url(provider)
    sp_cert = _value(config, "sp_x509_cert")
    private_key = str(secrets_.get("private_key") or "").strip()
    idp_cert = _value(config, "idp_x509_cert")
    idp_slo_url = _value(config, "slo_url")

    sp = {
        "entityId": _value(config, "sp_entity_id"),
        "assertionConsumerService": {"url": acs_url, "binding": ACS_BINDING},
        "NameIDFormat": _value(config, "name_id_format", DEFAULT_NAME_ID_FORMAT),
    }
    if sp_cert:
        sp["x509cert"] = sp_cert
    if private_key:
        sp["privateKey"] = private_key

    idp = {
        "entityId": _value(config, "idp_entity_id"),
        "singleSignOnService": {
            "url": _value(config, "sso_url"),
            "binding": SSO_BINDING,
        },
        "x509cert": idp_cert,
    }
    if idp_slo_url:
        idp["singleLogoutService"] = {"url": idp_slo_url, "binding": SLO_BINDING}

    security = {
        "authnRequestsSigned": bool(sp_cert and private_key),
        "wantAssertionsSigned": True,
        "wantMessagesSigned": False,
        "rejectDeprecatedAlgorithm": True,
    }
    if settings.SSO_ALLOW_INSECURE_HTTP:
        # Local harness only: allow http:// and single-label hosts such as
        # https://localhost. Production origins are always full DNS names.
        security["allowSingleLabelDomains"] = True

    return {
        "strict": True,
        "debug": False,
        "sp": sp,
        "idp": idp,
        "security": security,
    }


def _request_data(provider: IdentityProvider, post_data: dict | None = None) -> dict:
    """Create the request shape python3-saml expects from the public ACS URL."""
    parsed = urlparse(resolved_acs_url(provider))
    secure = parsed.scheme == "https"
    host = parsed.hostname or "localhost"
    http_host = f"{host}:{parsed.port}" if parsed.port else host
    return {
        "https": "on" if secure else "off",
        "http_host": http_host,
        "script_name": parsed.path or "/",
        "get_data": {},
        "post_data": dict(post_data or {}),
    }


def start_login(provider: IdentityProvider, relay_state: str) -> tuple[str, str]:
    """Return the IdP redirect URL and the AuthnRequest ID to validate later."""
    try:
        auth = OneLogin_Saml2_Auth(
            _request_data(provider), old_settings=settings_dict(provider)
        )
        url = auth.login(return_to=relay_state)
        request_id = auth.get_last_request_id()
    except OneLogin_Saml2_Error as exc:
        raise SSOError(f"Could not build the SAML AuthnRequest: {exc}") from exc
    except Exception as exc:
        logger.warning("SAML login start failed for %s: %s", provider.name, exc)
        raise SSOError("Could not build the SAML AuthnRequest.") from exc
    if not url or not request_id:
        raise SSOError("Could not build the SAML AuthnRequest.")
    return url, request_id


def _attribute_values(attributes: dict, name: str) -> list[str]:
    if not name:
        return []
    for key, values in (attributes or {}).items():
        if str(key).lower() != name.lower():
            continue
        if isinstance(values, (list, tuple)):
            return [str(value).strip() for value in values if str(value).strip()]
        value = str(values).strip()
        return [value] if value else []
    return []


def _first(attributes: dict, name: str) -> str:
    values = _attribute_values(attributes, name)
    return values[0] if values else ""


def _identity_from_attributes(
    provider: IdentityProvider, attributes: dict, name_id: str | None
) -> ExternalUser:
    config = provider_config(provider)
    email = _first(attributes, _value(config, "email_attribute", "email"))
    if not email:
        raise SSOError("The SAML assertion does not contain an email address.")
    first_name = _first(
        attributes, _value(config, "first_name_attribute", "givenName")
    ) or None
    last_name = _first(
        attributes, _value(config, "last_name_attribute", "sn")
    ) or None
    display_name = _first(
        attributes, _value(config, "display_name_attribute", "displayName")
    ) or None
    subject = (
        (name_id or "").strip()
        or _first(attributes, _value(config, "subject_attribute"))
        or email
    )
    if not subject:
        raise SSOError("The SAML assertion does not contain a subject.")
    username_hint = (
        _first(attributes, _value(config, "username_attribute", "uid"))
        or email.split("@", 1)[0]
    )
    groups = _attribute_values(
        attributes, _value(config, "group_attribute", "groups")
    )
    return ExternalUser(
        subject=subject,
        email=email,
        email_verified=True,
        username_hint=username_hint,
        first_name=first_name,
        last_name=last_name,
        name=display_name,
        groups=groups,
    )


def process_response(
    provider: IdentityProvider,
    post_data: dict,
    request_id: str,
) -> tuple[ExternalUser, dict]:
    """Validate an ACS response and return the identity plus session details."""
    try:
        auth = OneLogin_Saml2_Auth(
            _request_data(provider, post_data),
            old_settings=settings_dict(provider),
        )
        auth.process_response(request_id=request_id or None)
        errors = auth.get_errors()
        if errors:
            reason = auth.get_last_error_reason() or ", ".join(errors)
            raise SSOError(f"SAML response validation failed: {reason}")
        if not auth.is_authenticated():
            raise SSOError("SAML authentication did not complete.")
        identity = _identity_from_attributes(
            provider, auth.get_attributes() or {}, auth.get_nameid()
        )
        return identity, {
            "name_id": auth.get_nameid(),
            "session_index": auth.get_session_index(),
        }
    except SSOError:
        raise
    except OneLogin_Saml2_Error as exc:
        raise SSOError(f"SAML response validation failed: {exc}") from exc
    except Exception as exc:
        logger.warning("SAML response processing failed for %s: %s", provider.name, exc)
        raise SSOError("SAML response validation failed.") from exc


def test_provider(provider: IdentityProvider) -> dict:
    """Validate the generated SAML settings without contacting the IdP."""
    config = provider_config(provider)
    try:
        OneLogin_Saml2_Settings(settings_dict(provider))
    except OneLogin_Saml2_Error as exc:
        raise SSOError(f"SAML settings are invalid: {exc}") from exc
    except Exception as exc:
        logger.warning("SAML settings check failed for %s: %s", provider.name, exc)
        raise SSOError("SAML settings are invalid.") from exc
    acs_url = resolved_acs_url(provider)
    return {
        "message": (
            f"SAML settings OK · IdP {_value(config, 'idp_entity_id')} · "
            f"ACS {acs_url}"
        ),
        "idp_entity_id": _value(config, "idp_entity_id"),
        "sp_entity_id": _value(config, "sp_entity_id"),
        "sso_url": _value(config, "sso_url"),
        "acs_url": acs_url,
    }
