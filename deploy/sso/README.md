# Local SSO test stack (Dex + OpenLDAP)

This directory is a **development and integration-test** stack for the
enterprise single sign-on feature. It is not a production identity provider.

- **Dex** (`ghcr.io/dexidp/dex:v2.42.0`, Apache-2.0) is the OIDC provider.
- **OpenLDAP** (`osixia/openldap:1.5.0`, MIT image; OpenLDAP Public License 2.8
  server) is the directory behind Dex and the direct LDAP provider.
- The compose services are profile-gated as `sso`, so a normal install never
  starts them.

## Prerequisites

Set the public origin the browser and the backend will use. It must match the
URL in the browser, including a non-default port:

```bash
export PUBLIC_BASE_URL="https://172.16.16.44"
```

## Generate the Dex configuration

Run from the repository root:

```bash
python3 scripts/setup-sso.py
```

The script writes:

- `deploy/sso/dex/runtime/config.yaml` — issuer
  `${PUBLIC_BASE_URL}/idp`, client `opencyberrange`, redirect
  `${PUBLIC_BASE_URL}/api/auth/sso/oidc/1/callback`.
- `deploy/sso/dex/runtime/client-secret.txt` — generated OIDC client secret.

Both are ignored by Git. Do not commit them.

## Start the stack

```bash
docker compose --profile sso up -d ldap dex
```

The platform's nginx proxies `/idp/` to Dex. Dex derives its route prefix from
the issuer path, so the prefix is forwarded unchanged.

## Seed the providers

The OIDC provider must have ID `1` for the Dex redirect URI. Run the idempotent
seed script inside the backend container:

```bash
docker compose exec -T \
  -e PYTHONPATH=/app \
  -e SSO_OIDC_ISSUER="$PUBLIC_BASE_URL/idp" \
  -e SSO_OIDC_CLIENT_SECRET="$(cat deploy/sso/dex/runtime/client-secret.txt)" \
  -e SSO_LDAP_ADMIN_PASSWORD='SsoDemoAdmin!2026' \
  backend python /app/app/scripts/seed_sso_demo.py
```

The script creates:

| Provider | Kind | ID | Notes |
|---|---|---|---|
| Institution SSO (Dex) | oidc | 1 | Default provider |
| Institution LDAP | ldap | 2 | Direct directory form |

## Demo directory

The bootstrap LDIF creates `dc=example,dc=org`:

| User | Password | Group |
|---|---|---|
| `sso.student` | `SsoDemo!2026` | — |
| `sso.instructor` | `SsoDemo!2026` | `cn=instructors,ou=groups,dc=example,dc=org` |

The instructor group maps to the `instructor` role. Change these credentials
before exposing the stack beyond a test host.

## Verify

1. Open `PUBLIC_BASE_URL/login`.
2. Use **Sign in with Institution SSO (Dex)**, then the LDAP connector form.
3. Use the direct **Institution LDAP** form with `sso.student`.
4. Confirm the profile role. `sso.instructor` is an instructor; a directory
   group change applies on the next login.

API checks:

```bash
curl -sk "$PUBLIC_BASE_URL/api/auth/sso/providers"
curl -sk "$PUBLIC_BASE_URL/idp/.well-known/openid-configuration"
```

## Security notes

- This stack is for testing. Use the institution's IdP in production.
- Set `SSO_ALLOW_INSECURE_HTTP=true` only for a self-signed HTTPS test host.
- The backend trusts `X-Forwarded-For` only from loopback and private Docker
  bridges; do not widen that list to lab ranges.
- Provider secrets are encrypted at rest by the backend. None of the demo
  secrets belong in a production deployment.

## Licences

Dex is Apache-2.0. The osixia image is MIT; OpenLDAP is under the OpenLDAP
Public License 2.8. See `THIRD_PARTY_NOTICES.md` and
`THIRD_PARTY_LICENSES/OpenLDAP-2.8.txt`.
