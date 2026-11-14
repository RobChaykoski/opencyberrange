"""V3-only LDAP/OIDC/SAML identity provider settings.

This module stores provider configuration and encrypted secrets, validates the
settings each adapter needs, and exposes admin-only test actions. The login
flows live in ``app.routers.sso``.
"""
from __future__ import annotations

import json
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, Request
from pydantic import BaseModel, Field, field_validator
from sqlalchemy.orm import Session

from app.auth import get_current_admin_user
from app.config import settings
from app.crypto import decrypt_secret, encrypt_secret
from app.database import get_db
from app.models import IdentityProvider, User
from app.services import ldap_auth, oidc, saml_auth
from app.services.audit import log_admin_action
from app.services.external_identity import SSOError, truthy

router = APIRouter()

SUPPORTED_KINDS = {"ldap", "oidc", "saml"}
SECRET_KEYS = {
    "ldap": {"bind_password"},
    "oidc": {"client_secret"},
    "saml": {"private_key"},
}


class IdentityProviderCreate(BaseModel):
    name: str = Field(..., min_length=2, max_length=120)
    kind: str
    enabled: bool = False
    is_default: bool = False
    config: dict = Field(default_factory=dict)
    secrets: dict | None = None

    @field_validator("kind")
    @classmethod
    def valid_kind(cls, value: str) -> str:
        value = value.lower().strip()
        if value not in SUPPORTED_KINDS:
            raise ValueError("kind must be ldap, oidc, or saml")
        return value


class IdentityProviderUpdate(BaseModel):
    name: str | None = Field(None, min_length=2, max_length=120)
    enabled: bool | None = None
    is_default: bool | None = None
    config: dict | None = None
    secrets: dict | None = None


class IdentityProviderImportItem(BaseModel):
    name: str = Field(..., min_length=2, max_length=120)
    kind: str
    enabled: bool = False
    is_default: bool = False
    config: dict = Field(default_factory=dict)
    secrets: dict | None = None

    @field_validator("kind")
    @classmethod
    def valid_kind(cls, value: str) -> str:
        value = value.lower().strip()
        if value not in SUPPORTED_KINDS:
            raise ValueError("kind must be ldap, oidc, or saml")
        return value


class IdentityProviderImport(BaseModel):
    providers: list[IdentityProviderImportItem]
    dry_run: bool = True
    update_existing: bool = False


def _json(value: str | None) -> dict:
    if not value:
        return {}
    try:
        data = json.loads(value)
        return data if isinstance(data, dict) else {}
    except (TypeError, ValueError):
        return {}


def _apply_common(config: dict) -> dict:
    """Apply the shared provisioning and role-mapping defaults."""
    config.setdefault("auto_provision", True)
    config.setdefault("auto_approve", True)
    config.setdefault("link_existing_by_email", True)
    config.setdefault("default_role", "student")
    config.setdefault("instructor_group", "")
    for key in ("auto_provision", "auto_approve", "link_existing_by_email"):
        config[key] = truthy(config[key])
    role = str(config["default_role"]).strip().lower()
    if role not in {"student", "instructor"}:
        raise HTTPException(
            status_code=400,
            detail="default_role must be student or instructor",
        )
    config["default_role"] = role
    config["instructor_group"] = str(config.get("instructor_group") or "").strip()
    return config


def _validate_config(kind: str, config: dict) -> dict:
    config = {str(key): value for key, value in (config or {}).items()}
    if kind == "ldap":
        server = str(config.get("server_url", "")).strip()
        if not server.startswith(("ldap://", "ldaps://")):
            raise HTTPException(status_code=400, detail="LDAP server_url must start with ldap:// or ldaps://")
        if not str(config.get("base_dn", "")).strip():
            raise HTTPException(status_code=400, detail="LDAP base_dn is required")
        config["server_url"] = server
        config.setdefault("user_search_filter", "(uid={username})")
        config.setdefault("start_tls", False)
        config.setdefault("tls_verify", True)
        config["start_tls"] = truthy(config["start_tls"])
        config["tls_verify"] = truthy(config["tls_verify"])
        config.setdefault("email_attribute", "mail")
        config.setdefault("username_attribute", "uid")
        config.setdefault("first_name_attribute", "givenName")
        config.setdefault("last_name_attribute", "sn")
        config.setdefault("display_name_attribute", "cn")
        config.setdefault("group_attribute", "memberOf")
        config.setdefault("timeout_seconds", settings.SSO_HTTP_TIMEOUT_SECONDS)
        config.setdefault("allow_plaintext", False)
        config["allow_plaintext"] = truthy(config["allow_plaintext"])
        if (
            server.startswith("ldap://")
            and not bool(config.get("start_tls", False))
            and not bool(config.get("allow_plaintext", False))
            and not settings.SSO_ALLOW_INSECURE_HTTP
        ):
            raise HTTPException(
                status_code=400,
                detail="LDAP server_url must use ldaps://, StartTLS, or explicit allow_plaintext",
            )
        _apply_common(config)
    elif kind == "oidc":
        issuer = str(config.get("issuer", "")).rstrip("/")
        secure_issuer = issuer.startswith("https://")
        local_issuer = settings.SSO_ALLOW_INSECURE_HTTP and issuer.startswith("http://")
        if not (secure_issuer or local_issuer):
            raise HTTPException(
                status_code=400,
                detail="OIDC issuer must be an https:// URL",
            )
        if not str(config.get("client_id", "")).strip():
            raise HTTPException(status_code=400, detail="OIDC client_id is required")
        config["issuer"] = issuer
        config.setdefault("scopes", "openid email profile")
        config.setdefault("username_claim", "preferred_username")
        config.setdefault("email_claim", "email")
        config.setdefault("name_claim", "name")
        config.setdefault("groups_claim", "groups")
        _apply_common(config)
        discovery_url = str(config.get("discovery_url", "")).strip()
        if discovery_url:
            if discovery_url.startswith("http://") and not settings.SSO_ALLOW_INSECURE_HTTP:
                raise HTTPException(
                    status_code=400,
                    detail="OIDC discovery_url must use https://",
                )
            if not discovery_url.startswith(("https://", "http://")):
                raise HTTPException(
                    status_code=400,
                    detail="OIDC discovery_url must be an http(s) URL",
                )
            config["discovery_url"] = discovery_url
    elif kind == "saml":
        for key in ("idp_entity_id", "sso_url", "sp_entity_id", "idp_x509_cert"):
            if not str(config.get(key, "")).strip():
                raise HTTPException(status_code=400, detail=f"SAML {key} is required")
        sso_url = str(config["sso_url"]).strip()
        if sso_url.startswith("http://") and not settings.SSO_ALLOW_INSECURE_HTTP:
            raise HTTPException(status_code=400, detail="SAML sso_url must use https://")
        if not sso_url.startswith(("https://", "http://")):
            raise HTTPException(status_code=400, detail="SAML sso_url must be an http(s) URL")
        acs_url = str(config.get("acs_url", "")).strip()
        if acs_url and not acs_url.startswith(("https://", "http://")):
            raise HTTPException(status_code=400, detail="SAML acs_url must be an http(s) URL")
        config["sso_url"] = sso_url
        config["acs_url"] = acs_url
        config["idp_x509_cert"] = str(config["idp_x509_cert"]).strip()
        config.setdefault("name_id_format", saml_auth.DEFAULT_NAME_ID_FORMAT)
        config.setdefault("email_attribute", "email")
        config.setdefault("username_attribute", "uid")
        config.setdefault("first_name_attribute", "givenName")
        config.setdefault("last_name_attribute", "sn")
        config.setdefault("display_name_attribute", "displayName")
        config.setdefault("group_attribute", "groups")
        config.setdefault("subject_attribute", "")
        config.setdefault("sp_x509_cert", "")
        config.setdefault("slo_url", "")
        _apply_common(config)
    else:
        raise HTTPException(status_code=400, detail="Unsupported identity provider kind")
    return config


def _validate_secret_keys(kind: str, secrets: dict | None) -> dict:
    cleaned = {str(key): value for key, value in (secrets or {}).items()}
    unknown = set(cleaned) - SECRET_KEYS[kind]
    if unknown:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported secret fields for {kind}: {sorted(unknown)}",
        )
    return cleaned


def _secret_keys(value: str | None) -> list[str]:
    try:
        data = json.loads(decrypt_secret(value)) if value else {}
    except Exception:
        return []
    return sorted(data.keys()) if isinstance(data, dict) else []


def _serialize(row: IdentityProvider) -> dict:
    data = {
        "id": row.id,
        "name": row.name,
        "kind": row.kind,
        "enabled": bool(row.enabled),
        "is_default": bool(row.is_default),
        "config": _json(row.config),
        "secret_keys": _secret_keys(row.secrets),
        "has_secrets": bool(row.secrets),
        "created_at": row.created_at,
        "updated_at": row.updated_at,
    }
    if row.kind == "oidc":
        data["resolved_redirect_uri"] = oidc.redirect_uri(row.id)
    elif row.kind == "saml":
        data["resolved_acs_url"] = saml_auth.resolved_acs_url(row)
    return data


def _export_provider(row: IdentityProvider) -> dict:
    """Portable provider settings without secret values."""
    return {
        "name": row.name,
        "kind": row.kind,
        "enabled": bool(row.enabled),
        "is_default": bool(row.is_default),
        "config": _json(row.config),
        "secret_keys": _secret_keys(row.secrets),
        "has_secrets": bool(row.secrets),
    }


def _merge_secrets(row: IdentityProvider, updates: dict) -> None:
    existing: dict = {}
    if row.secrets:
        try:
            existing = json.loads(decrypt_secret(row.secrets))
        except Exception:
            existing = {}
    for key, value in updates.items():
        if value in (None, ""):
            existing.pop(key, None)
        else:
            existing[key] = value
    row.secrets = encrypt_secret(json.dumps(existing)) if existing else None


def _set_default(db: Session, row: IdentityProvider) -> None:
    db.query(IdentityProvider).filter(IdentityProvider.id != row.id).update(
        {IdentityProvider.is_default: False}, synchronize_session=False
    )
    row.is_default = True


def _audit(request: Request, current_user: User, action: str, row: IdentityProvider):
    log_admin_action(
        action,
        current_user.id,
        current_user.username,
        "identity_provider",
        target_id=row.id,
        target_identifier=row.name,
        details={"kind": row.kind, "enabled": bool(row.enabled)},
        ip_address=request.client.host if request.client else None,
    )


@router.get("/providers")
def list_identity_providers(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user),
):
    rows = db.query(IdentityProvider).order_by(IdentityProvider.name).all()
    return {"providers": [_serialize(row) for row in rows]}


@router.get("/providers/export")
def export_identity_providers(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user),
):
    """Export portable provider settings. Secret values are never included."""
    rows = db.query(IdentityProvider).order_by(IdentityProvider.name).all()
    return {
        "format": "ocr-identity-providers",
        "version": 1,
        "exported_at": datetime.now(timezone.utc).isoformat(),
        "secrets_exported": False,
        "providers": [_export_provider(row) for row in rows],
    }


@router.post("/providers/import")
def import_identity_providers(
    payload: IdentityProviderImport,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user),
):
    """Validate or import an exported provider bundle.

    The default is a dry run. Secret values may be supplied on import; they are
    encrypted at rest and never echoed back. A provider whose required secrets
    are absent is imported disabled rather than enabled in a broken state.
    """
    if not payload.providers:
        raise HTTPException(status_code=400, detail="No providers in the import bundle")
    if sum(1 for item in payload.providers if item.is_default) > 1:
        raise HTTPException(status_code=400, detail="Only one provider may be default")

    prepared = []
    seen: set[str] = set()
    for item in payload.providers:
        name = item.name.strip()
        if name.lower() in seen:
            raise HTTPException(
                status_code=400, detail=f"Duplicate provider name in bundle: {name}"
            )
        seen.add(name.lower())
        config = _validate_config(item.kind, item.config)
        secrets = _validate_secret_keys(item.kind, item.secrets)
        existing = (
            db.query(IdentityProvider)
            .filter(IdentityProvider.name == name)
            .first()
        )
        if existing is not None and existing.kind != item.kind:
            raise HTTPException(
                status_code=409,
                detail=f"Provider {name} exists with kind {existing.kind}",
            )
        if existing is not None and not payload.update_existing:
            action = "skip"
        else:
            action = "create" if existing is None else "update"

        required = SECRET_KEYS[item.kind]
        has_existing_secrets = bool(existing and existing.secrets)
        missing = sorted(required - set(secrets))
        enabled = bool(item.enabled)
        forced_disabled = False
        if action != "skip" and enabled and missing and not has_existing_secrets:
            enabled = False
            forced_disabled = True
        is_default = bool(item.is_default) and enabled
        prepared.append(
            {
                "item": item,
                "name": name,
                "config": config,
                "secrets": secrets,
                "existing": existing,
                "action": action,
                "enabled": enabled,
                "forced_disabled": forced_disabled,
                "is_default": is_default,
                "missing_secrets": missing if action != "skip" else [],
            }
        )

    if payload.dry_run:
        return {
            "dry_run": True,
            "providers": [
                {
                    "name": entry["name"],
                    "kind": entry["item"].kind,
                    "action": entry["action"],
                    "enabled": (
                        entry["enabled"]
                        if entry["action"] != "skip"
                        else bool(entry["existing"].enabled)
                    ),
                    "missing_secrets": entry["missing_secrets"],
                }
                for entry in prepared
            ],
        }

    results = []
    try:
        for entry in prepared:
            item = entry["item"]
            row = entry["existing"]
            if entry["action"] == "skip":
                results.append({"name": entry["name"], "action": "skipped"})
                continue
            if row is None:
                row = IdentityProvider(
                    name=entry["name"],
                    kind=item.kind,
                    enabled=entry["enabled"],
                    is_default=False,
                    config=json.dumps(entry["config"]),
                    secrets=(
                        encrypt_secret(json.dumps(entry["secrets"]))
                        if entry["secrets"]
                        else None
                    ),
                )
                db.add(row)
                db.flush()
            else:
                row.config = json.dumps(entry["config"])
                row.enabled = entry["enabled"]
                if entry["secrets"]:
                    _merge_secrets(row, entry["secrets"])
                db.flush()
            if entry["is_default"]:
                _set_default(db, row)
            _audit(
                request,
                current_user,
                "IDENTITY_PROVIDER_IMPORTED",
                row,
            )
            results.append(
                {
                    "name": entry["name"],
                    "action": entry["action"],
                    "enabled": bool(row.enabled),
                }
            )
        db.commit()
    except Exception:
        db.rollback()
        raise
    return {
        "dry_run": False,
        "created": sum(1 for r in results if r["action"] == "create"),
        "updated": sum(1 for r in results if r["action"] == "update"),
        "skipped": sum(1 for r in results if r["action"] == "skipped"),
        "providers": results,
    }


@router.post("/providers", status_code=201)
def create_identity_provider(
    payload: IdentityProviderCreate,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user),
):
    if db.query(IdentityProvider).filter(IdentityProvider.name == payload.name.strip()).first():
        raise HTTPException(status_code=409, detail="An identity provider with that name already exists")
    config = _validate_config(payload.kind, payload.config)
    secrets = _validate_secret_keys(payload.kind, payload.secrets)
    if payload.is_default and not payload.enabled:
        raise HTTPException(status_code=400, detail="The default provider must be enabled")
    row = IdentityProvider(
        name=payload.name.strip(),
        kind=payload.kind,
        enabled=payload.enabled,
        is_default=False,
        config=json.dumps(config),
        secrets=encrypt_secret(json.dumps(secrets)) if secrets else None,
    )
    db.add(row)
    db.flush()
    if payload.is_default:
        _set_default(db, row)
    db.commit()
    db.refresh(row)
    _audit(request, current_user, "IDENTITY_PROVIDER_CREATED", row)
    return _serialize(row)


@router.patch("/providers/{provider_id}")
def update_identity_provider(
    provider_id: int,
    payload: IdentityProviderUpdate,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user),
):
    row = db.query(IdentityProvider).filter(IdentityProvider.id == provider_id).first()
    if not row:
        raise HTTPException(status_code=404, detail="Identity provider not found")

    if payload.name is not None:
        name = payload.name.strip()
        duplicate = db.query(IdentityProvider).filter(
            IdentityProvider.name == name, IdentityProvider.id != row.id
        ).first()
        if duplicate:
            raise HTTPException(status_code=409, detail="An identity provider with that name already exists")
        row.name = name
    if payload.config is not None:
        row.config = json.dumps(_validate_config(row.kind, payload.config))
    if payload.secrets is not None:
        cleaned = _validate_secret_keys(row.kind, payload.secrets)
        existing = {}
        if row.secrets:
            try:
                existing = json.loads(decrypt_secret(row.secrets))
            except Exception:
                existing = {}
        for key, value in cleaned.items():
            if value in (None, ""):
                existing.pop(key, None)
            else:
                existing[key] = value
        row.secrets = encrypt_secret(json.dumps(existing)) if existing else None
    if payload.enabled is not None:
        row.enabled = payload.enabled
    if payload.is_default is not None:
        if payload.is_default:
            if not row.enabled:
                raise HTTPException(status_code=400, detail="The default provider must be enabled")
            _set_default(db, row)
        else:
            row.is_default = False
    if row.is_default and not row.enabled:
        raise HTTPException(status_code=400, detail="The default provider must be enabled")

    db.commit()
    db.refresh(row)
    _audit(request, current_user, "IDENTITY_PROVIDER_UPDATED", row)
    return _serialize(row)


@router.post("/providers/{provider_id}/default")
def make_default_identity_provider(
    provider_id: int,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user),
):
    row = db.query(IdentityProvider).filter(IdentityProvider.id == provider_id).first()
    if not row:
        raise HTTPException(status_code=404, detail="Identity provider not found")
    if not row.enabled:
        raise HTTPException(status_code=400, detail="Enable the provider before making it the default")
    _set_default(db, row)
    db.commit()
    db.refresh(row)
    _audit(request, current_user, "IDENTITY_PROVIDER_DEFAULTED", row)
    return _serialize(row)


@router.post("/providers/{provider_id}/test")
def test_identity_provider(
    provider_id: int,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user),
):
    """Validate provider settings and reachability for its adapter."""
    row = db.query(IdentityProvider).filter(IdentityProvider.id == provider_id).first()
    if not row:
        raise HTTPException(status_code=404, detail="Identity provider not found")
    try:
        if row.kind == "oidc":
            result = oidc.test_provider(row)
        elif row.kind == "ldap":
            result = ldap_auth.test_provider(row)
        elif row.kind == "saml":
            result = saml_auth.test_provider(row)
        else:
            raise HTTPException(
                status_code=400, detail="Unsupported identity provider kind"
            )
    except SSOError as exc:
        _audit(request, current_user, "IDENTITY_PROVIDER_TEST_FAILED", row)
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    _audit(request, current_user, "IDENTITY_PROVIDER_TESTED", row)
    return {"ok": True, **result}


@router.delete("/providers/{provider_id}")
def delete_identity_provider(
    provider_id: int,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user),
):
    row = db.query(IdentityProvider).filter(IdentityProvider.id == provider_id).first()
    if not row:
        raise HTTPException(status_code=404, detail="Identity provider not found")
    _audit(request, current_user, "IDENTITY_PROVIDER_DELETED", row)
    db.delete(row)
    db.commit()
    return {"message": "Identity provider deleted"}
