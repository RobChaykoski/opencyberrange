"""V3-only LDAP/SSO identity provider settings.

This module stores provider configuration and encrypted secrets. It does not
implement the login flow yet; it is the settings and validation layer that the
v3 authentication adapters will consume.
"""
from __future__ import annotations

import json

from fastapi import APIRouter, Depends, HTTPException, Request
from pydantic import BaseModel, Field, field_validator
from sqlalchemy.orm import Session

from app.auth import get_current_admin_user
from app.config import settings
from app.crypto import decrypt_secret, encrypt_secret
from app.database import get_db
from app.models import IdentityProvider, User
from app.services import oidc
from app.services.audit import log_admin_action

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


def _json(value: str | None) -> dict:
    if not value:
        return {}
    try:
        data = json.loads(value)
        return data if isinstance(data, dict) else {}
    except (TypeError, ValueError):
        return {}


def _validate_config(kind: str, config: dict) -> dict:
    config = {str(key): value for key, value in (config or {}).items()}
    if kind == "ldap":
        server = str(config.get("server_url", "")).strip()
        if not server.startswith(("ldap://", "ldaps://")):
            raise HTTPException(status_code=400, detail="LDAP server_url must start with ldap:// or ldaps://")
        if not str(config.get("base_dn", "")).strip():
            raise HTTPException(status_code=400, detail="LDAP base_dn is required")
        config.setdefault("user_search_filter", "(uid={username})")
        config.setdefault("start_tls", False)
        config.setdefault("tls_verify", True)
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
        config.setdefault("auto_provision", True)
        config.setdefault("auto_approve", True)
        config.setdefault("link_existing_by_email", True)
        config.setdefault("default_role", "student")
        config.setdefault("username_claim", "preferred_username")
        config.setdefault("email_claim", "email")
        config.setdefault("name_claim", "name")
        if str(config["default_role"]).lower() not in {"student", "instructor"}:
            raise HTTPException(
                status_code=400,
                detail="OIDC default_role must be student or instructor",
            )
        config["default_role"] = str(config["default_role"]).lower()
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
        for key in ("idp_entity_id", "sso_url", "sp_entity_id", "acs_url"):
            if not str(config.get(key, "")).strip():
                raise HTTPException(status_code=400, detail=f"SAML {key} is required")
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
    return data


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
    """Validate an OIDC discovery document and JWKS reachability."""
    row = db.query(IdentityProvider).filter(IdentityProvider.id == provider_id).first()
    if not row:
        raise HTTPException(status_code=404, detail="Identity provider not found")
    if row.kind != "oidc":
        raise HTTPException(status_code=400, detail="Only OIDC providers can be tested yet")
    try:
        result = oidc.test_provider(row)
    except oidc.OIDCError as exc:
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
