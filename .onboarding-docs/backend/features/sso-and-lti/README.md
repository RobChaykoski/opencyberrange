# SSO and LTI

## Purpose

Let an institution use its own identity provider and let a learning management
system launch the platform without a second password. Local accounts remain the
break-glass path.

## Code map

| Concern | Location |
|---|---|
| SSO router | `platform/backend/app/routers/sso.py` |
| Identity providers | `platform/backend/app/routers/identity.py` |
| LTI router | `platform/backend/app/routers/lti.py` |
| OIDC | `platform/backend/app/services/oidc.py`, `sso_flow.py` |
| SAML | `platform/backend/app/services/saml_auth.py` |
| LDAP / AD | `platform/backend/app/services/ldap_auth.py` |
| External identities | `platform/backend/app/services/external_identity.py` |
| Models | `platform/backend/app/models/lti.py`, `models/auth.py` |

## API surface

| Method | Path | Notes |
|---|---|---|
| GET | `/api/auth/sso/providers` | enabled providers |
| GET | `/api/auth/sso/oidc/{provider}/login` | start OIDC |
| GET | `/api/auth/sso/oidc/{provider}/callback` | OIDC callback |
| GET/POST | `/api/auth/sso/saml/{provider}/login`, `/acs` | SAML |
| POST | `/api/auth/sso/ldap/{provider}/login` | LDAP bind |
| POST | `/api/auth/sso/exchange` | exchange a one-time code for a session |
| GET/POST | `/api/identity/providers` | admin provider configuration |
| POST | `/api/lti/login`, `/launch`, `/jwks` | LTI 1.3 |

## Behaviour that matters

- **Local admin remains.** Do not remove the last local administrator; SSO must
  not lock the institution out.
- **State and nonce.** OIDC uses state, nonce, PKCE where supported, and a
  short-lived exchange code.
- **SAML assertions.** Validate signature, audience, recipient, time window, and
  replay cache.
- **LDAP.** Bind is read-only; TLS is explicit; no silent downgrade.
- **Callback origin.** `PUBLIC_BASE_URL` must be the stable external origin used
  in the IdP registration.
- **Account linking.** An external identity maps to a local user; do not create
  a duplicate on every login.
- **LTI.** Treat the LMS as a launch context, not as a source of truth for
  grades. Deep linking is explicit.
- **Insecure HTTP is test-only.** `SSO_ALLOW_INSECURE_HTTP=true` must not be
  used in production.

## Persistent state

| Store | Data |
|---|---|
| Identity provider config | issuer, client id, secret reference, enabled |
| External identities | provider subject to local user mapping |
| SSO state / replay cache | short-lived |
| LTI registrations | platform, client, deployment, keys |
| Security events | login, link, failure |

## Fixtures and tests

- Optional demo stack: `docker compose --profile sso up -d ldap dex` and
  `scripts/seed_sso_demo.py`.
- Focused tests:

```bash
cd platform/backend
python -m pytest tests/test_sso_oidc.py tests/test_sso_saml_ldap.py \
  tests/test_sso_hardening.py tests/test_sso_gate.py \
  tests/test_identity_providers.py tests/test_lti.py -q
```

## Extension checklist

- Add the provider config and a migration if needed.
- Add tests for success, invalid signature, expired assertion, replay, and
  disabled provider.
- Add a security event for link, unlink, and failure.
- Update the admin identity provider page and the docs.
- Never log a token, assertion, or client secret.

## Related

- [SSO OIDC](../../../../docs/SSO-OIDC.md)
- [SSO SAML/LDAP](../../../../docs/SSO-SAML-LDAP.md)
- [LTI](../../../../docs/LTI.md)
- [Moodle LTI showcase](../../../../docs/MOODLE-LTI-SHOWCASE.md)
- [ADR 0006 identity platform roles](../../../../docs/decisions/0006-identity-platform-roles.md)
