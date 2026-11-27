# Login

## Purpose

Authenticate a local account, issue a short-lived access token and a rotating
refresh token, bind the token to a server-side session, and expose the current
identity to the SPA.

## Code map

| Concern | Location |
|---|---|
| Router | `platform/backend/app/routers/auth.py` (`/login`, `/refresh`, `/reauth`, `/me`, `/logout`, `/sessions`, `/mfa/*`) |
| Core auth | `platform/backend/app/auth.py` (JWT decode, current-user dependencies, password hashing) |
| Sessions | `platform/backend/app/services/auth_sessions.py` |
| Reauth | `platform/backend/app/services/reauth.py` |
| MFA | `platform/backend/app/services/mfa.py`, `totp.py` |
| Throttle / lockout | `platform/backend/app/services/login_throttle.py`, `event_burst.py` |
| Model | `platform/backend/app/models/auth.py` (`users`, session and revocation models) |

## API surface

| Method | Path | Notes |
|---|---|---|
| POST | `/api/auth/login` | `application/x-www-form-urlencoded`, `username` + `password`; returns `access_token`, `refresh_token`, `session_id`, `user` |
| POST | `/api/auth/refresh` | rotates the refresh token; replay revokes the family |
| POST | `/api/auth/reauth` | opens the short reauthentication window for sensitive actions |
| GET | `/api/auth/me` | current identity; no password fields |
| POST | `/api/auth/logout` | revokes the session |
| GET | `/api/auth/sessions` | session list for the current user |
| DELETE | `/api/auth/sessions/{id}` | revoke one session; requires recent reauth |
| POST | `/api/auth/sessions/revoke-all` | revoke every session for the user |
| POST | `/api/auth/mfa/enroll`, `/mfa/verify`, `/mfa/disable` | TOTP lifecycle |
| POST | `/api/auth/change-password` | rehash and revoke sessions |
| POST | `/api/auth/forgot-password`, `/reset-password` | reset flow |

## Behaviour that matters

- **Generic errors.** Unknown user, wrong password, and locked account return
  the same `401` body: `Incorrect username or password`.
- **Bounded input.** Username is capped at 150 characters and password at 128
  before hashing; control characters are rejected with the same generic error.
- **Rate limit and lockout.** Per-IP limits come from slowapi; per
  `(username, IP)` backoff and account lockout come from `login_throttle.py`.
- **Session-bound tokens.** A normal login token contains `sid`, `sec`, and the
  user claims. `get_current_user` checks the session and the security version.
- **Refresh rotation.** A rotated token is single-use; replay revokes the
  rotation family and returns `401` with `X-Refresh-Reuse`.
- **MFA.** TOTP and recovery codes are verified after the password. A second
  factor change bumps `security_version` and revokes sessions.
- **Reauth.** Sensitive operations (session revocation, consent changes,
  deletion) require a recent password reauthentication.

## Persistent state

| Store | Data |
|---|---|
| PostgreSQL `users` | hash, role, active/approved/locked, failed attempts, last login |
| PostgreSQL session tables | session id, tenant, refresh-token hash, revocation |
| PostgreSQL security events | login success/failure, lockout, refresh reuse, MFA events |
| Browser `localStorage` | `token`, `refresh_token`, `user` |

## Fixtures and tests

- Create the first admin through the setup wizard; the setup token comes from
  `SETUP_TOKEN`.
- Development demo accounts: `seed_demo_class.py` (requires demo passwords).
- Focused tests:

```bash
cd platform/backend
python -m pytest tests/test_auth.py tests/test_auth_lifecycle.py \
  tests/test_jwt_validation.py tests/test_login_throttle.py \
  tests/test_mfa.py tests/test_token_revocation.py -q
```

## Extension checklist

- Keep the generic error contract.
- Add a session or revocation check if you add a new token type.
- Add a security event for every new authentication outcome.
- Never log or return a password, hash, TOTP secret, or recovery code.
- Update the blackbox suite at `security-tests/karate/features/01-auth-owasp.feature`
  when the login contract changes.

## Related

- [Registration](../registration/README.md)
- [Roles and admin](../roles-and-admin/README.md)
- [Privacy and consent](../privacy-and-consent/README.md)
- [Auth lifecycle](../../../../docs/AUTH-LIFECYCLE.md)
