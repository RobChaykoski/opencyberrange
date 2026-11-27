# SSO

## Purpose

Let an institution authenticate users through its own identity provider. Local
accounts remain available as break-glass access.

## Protocols

| Protocol | Adapter | Notes |
|---|---|---|
| OIDC | `services/oidc.py`, `sso_flow.py` | state, nonce, PKCE where supported, short-lived exchange code |
| SAML 2.0 | `services/saml_auth.py` | signature, audience, recipient, time window, replay cache |
| LDAP / AD | `services/ldap_auth.py` | bind, group mapping, explicit TLS |

## Configuration

1. Set `PUBLIC_BASE_URL` to the stable browser origin.
2. In **Admin -> Settings -> Identity providers**, add the provider.
3. Copy the callback or ACS URL into the IdP registration.
4. Test, then enable.
5. Keep at least one local administrator.

Optional demo stack:

```bash
docker compose --env-file .env -f docker-compose.dev.yml --profile sso up -d ldap dex
python scripts/seed_sso_demo.py
```

The demo stack is not a production IdP.

## Account linking

- The provider subject is the stable key.
- Link to an existing local user by a verified email or an explicit admin link.
- Do not create a duplicate account on every login.
- Record link, unlink, and failure as security events.

## Tests

```bash
cd platform/backend
python -m pytest tests/test_sso_oidc.py tests/test_sso_saml_ldap.py \
  tests/test_sso_hardening.py tests/test_sso_gate.py \
  tests/test_identity_providers.py -q
```

## Rules

- No silent TLS downgrade.
- No token, assertion, or client secret in a log.
- No automatic administrator creation from an IdP claim.
- `SSO_ALLOW_INSECURE_HTTP=true` is test-only.

## Related

- [Backend SSO and LTI](../../backend/features/sso-and-lti/README.md)
- [SSO OIDC](../../../docs/SSO-OIDC.md)
- [SSO SAML/LDAP](../../../docs/SSO-SAML-LDAP.md)
- [Authentik deployment](../../../deploy/authentik/docker-compose.yml)
