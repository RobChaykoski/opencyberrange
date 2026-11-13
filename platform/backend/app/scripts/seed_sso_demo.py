"""Seed the local Dex/OpenLDAP SSO demo providers.

Run inside the backend container after the optional SSO stack is up:

    docker compose --profile sso up -d ldap dex
    docker compose exec -T -e PYTHONPATH=/app backend \\
      python /app/app/scripts/seed_sso_demo.py

The script is idempotent. It creates or updates one OIDC provider (default)
and one LDAP provider. The OIDC provider must have id 1 because the Dex config
uses the fixed redirect URI ``/api/auth/sso/oidc/1/callback``.
"""
from __future__ import annotations

import json
import os

from app.crypto import encrypt_secret
from app.database import SessionLocal
from app.models import IdentityProvider

OIDC_NAME = "Institution SSO (Dex)"
LDAP_NAME = "Institution LDAP"


def _upsert(db, name: str, kind: str, config: dict, secrets: dict, desired_id: int):
    row = db.query(IdentityProvider).filter(IdentityProvider.name == name).first()
    if row is None:
        row = IdentityProvider(id=desired_id, name=name, kind=kind)
        existing = db.query(IdentityProvider).filter(IdentityProvider.id == desired_id).first()
        if existing is not None:
            row.id = None
        db.add(row)
    row.name = name
    row.kind = kind
    row.enabled = True
    row.config = json.dumps(config, sort_keys=True)
    row.secrets = encrypt_secret(json.dumps(secrets, sort_keys=True)) if secrets else None
    db.flush()
    return row


def main() -> int:
    oidc_issuer = os.environ.get("SSO_OIDC_ISSUER", "https://172.16.16.44/idp").rstrip("/")
    oidc_secret = os.environ.get("SSO_OIDC_CLIENT_SECRET", "").strip()
    if not oidc_secret:
        raise SystemExit("SSO_OIDC_CLIENT_SECRET is required")
    ldap_password = os.environ.get("SSO_LDAP_ADMIN_PASSWORD", "SsoDemoAdmin!2026")

    db = SessionLocal()
    try:
        oidc = _upsert(
            db,
            OIDC_NAME,
            "oidc",
            {
                "issuer": oidc_issuer,
                "client_id": "opencyberrange",
                "scopes": "openid email profile",
                "username_claim": "preferred_username",
                "email_claim": "email",
                "name_claim": "name",
                "groups_claim": "groups",
                "auto_provision": True,
                "auto_approve": True,
                "link_existing_by_email": True,
                "default_role": "student",
                "instructor_group": "",
            },
            {"client_secret": oidc_secret},
            1,
        )
        ldap = _upsert(
            db,
            LDAP_NAME,
            "ldap",
            {
                "server_url": "ldap://ldap:389",
                "base_dn": "ou=people,dc=example,dc=org",
                "bind_dn": "cn=admin,dc=example,dc=org",
                "user_search_filter": "(uid={username})",
                "start_tls": False,
                "tls_verify": False,
                "email_attribute": "mail",
                "username_attribute": "uid",
                "first_name_attribute": "givenName",
                "last_name_attribute": "sn",
                "display_name_attribute": "cn",
                "group_attribute": "memberOf",
                "instructor_group": "cn=instructors,ou=groups,dc=example,dc=org",
                "auto_provision": True,
                "auto_approve": True,
                "link_existing_by_email": True,
                "default_role": "student",
            },
            {"bind_password": ldap_password},
            2,
        )
        db.query(IdentityProvider).filter(IdentityProvider.id != oidc.id).update(
            {"is_default": False}, synchronize_session=False
        )
        oidc.is_default = True
        db.commit()
        print(f"OIDC provider id={oidc.id} name={oidc.name!r}")
        print(f"LDAP provider id={ldap.id} name={ldap.name!r}")
        print(f"OIDC redirect URI: /api/auth/sso/oidc/{oidc.id}/callback")
    finally:
        db.close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
