#!/usr/bin/env python3
"""Generate the local Dex OIDC configuration for the SSO demo stack.

Run from the repository root after setting PUBLIC_BASE_URL (or SSO_BASE_URL)
for the host that serves the platform. The generated config is ignored by Git.
"""
from __future__ import annotations

import os
import secrets
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RUNTIME = ROOT / "deploy" / "sso" / "dex" / "runtime"
TEMPLATE = ROOT / "deploy" / "sso" / "dex" / "config.template.yaml"

base = (
    os.environ.get("PUBLIC_BASE_URL")
    or os.environ.get("SSO_BASE_URL")
    or "https://172.16.16.44"
).rstrip("/")

RUNTIME.mkdir(parents=True, exist_ok=True)
secret_file = RUNTIME / "client-secret.txt"
client_secret = os.environ.get("SSO_OIDC_CLIENT_SECRET", "").strip()
if not client_secret:
    if secret_file.exists():
        client_secret = secret_file.read_text(encoding="utf-8").strip()
    if not client_secret:
        client_secret = secrets.token_urlsafe(32)
        secret_file.write_text(client_secret, encoding="utf-8")
        try:
            secret_file.chmod(0o600)
        except OSError:
            pass

ldap_password = os.environ.get("SSO_LDAP_ADMIN_PASSWORD", "SsoDemoAdmin!2026")
redirect_uri = f"{base}/api/auth/sso/oidc/1/callback"

config = TEMPLATE.read_text(encoding="utf-8")
for key, value in {
    "${DEX_ISSUER}": f"{base}/idp",
    "${DEX_REDIRECT_URI}": redirect_uri,
    "${DEX_CLIENT_SECRET}": client_secret,
    "${LDAP_BIND_DN}": "cn=admin,dc=example,dc=org",
    "${LDAP_BIND_PASSWORD}": ldap_password,
    "${LDAP_BASE_DN}": "ou=people,dc=example,dc=org",
}.items():
    config = config.replace(key, value)

out = RUNTIME / "config.yaml"
out.write_text(config, encoding="utf-8")
print(f"wrote {out.relative_to(ROOT)}")
print(f"issuer: {base}/idp")
print(f"redirect: {redirect_uri}")
print(f"client secret: {secret_file.relative_to(ROOT)}")
print("Start the stack with: docker compose --profile sso up -d ldap dex")
