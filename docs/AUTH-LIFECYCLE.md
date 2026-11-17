# Authentication lifecycle

This page documents session, refresh-token, MFA, reauthentication, and password
hash controls. It is the operator and engineering reference for
`app/services/auth_sessions.py`, `app/services/mfa.py`,
`app/services/reauth.py`, and `app/auth.py`.

## Sessions and refresh-token rotation

A successful login creates a server-side `auth_sessions` row and a rotating
refresh token. The access JWT carries the session id (`sid`). The session binds
the tenant captured at login, the MFA timestamp, the reauthentication timestamp,
and device metadata.

- Access tokens are short-lived JWTs.
- Refresh tokens are opaque `ocr_rt_<id>_<secret>` values. Only the SHA-256 hash
  is stored.
- `POST /api/auth/refresh` consumes the presented refresh token and issues a new
  access/refresh pair. The new refresh token belongs to the same rotation family.
- A refresh token is single-use. Presenting a rotated token is treated as theft:
  the **whole family and the bound session are revoked**, a `critical`
  `auth.refresh_reuse` event is written, and the request returns `401`.
- `POST /api/auth/logout` revokes the session and its refresh family.
- `GET /api/auth/sessions` lists active sessions; `DELETE
  /api/auth/sessions/{id}` revokes one; `POST /api/auth/sessions/revoke-all`
  revokes all.

Token lifetime settings:

| Setting | Default | Purpose |
|---|---|---|
| `JWT_EXPIRATION_HOURS` | 24 | Access-token lifetime |
| `refresh_token_days` | 30 | Session and refresh-token lifetime |
| `SESSION_MAX_PER_USER` | 10 | Oldest sessions are revoked beyond this |

## Session-bound tenant context

The tenant is **not** read from the JWT. `get_current_user()` loads the session
and uses `session.institution_id`. If the account's `users.institution_id` has
changed since the session was created, the session is revoked and the request
returns `401` with `X-Session-Invalid: true`.

Legacy tokens without a `sid` claim remain valid only until their short access
token expires; they do not satisfy a reauthentication check.

## TOTP recovery-code lifecycle

Recovery codes:

- are generated in sets of 10 by default (`mfa_recovery_code_count`);
- are stored only as SHA-256 hashes;
- are single-use and consumed under a row lock;
- expire after `mfa_recovery_code_ttl_days` (default 365);
- are replaced as a set when regenerated, invalidating every old code;
- are cleared when MFA is disabled or reset;
- return a `remaining` count and a `rotate_recommended` hint at 2 or fewer.

Generation requires a recent password + MFA reauthentication. The response
contains `codes`, `remaining`, and `expires_at`; the plaintext codes are shown
exactly once.

## MFA brute-force throttling

MFA failures use a separate counter from password lockout:

| Setting | Default | Purpose |
|---|---|---|
| `mfa_max_failed_attempts` | 5 | Bad TOTP/recovery attempts before lock |
| `mfa_lockout_minutes` | 15 | Lock duration |

`429 Too Many Requests` is returned with `Retry-After` and
`X-MFA-Locked: true`. A successful challenge resets the counter. A lock event
(`auth.mfa_locked`) is written at the threshold. This prevents a stolen password
from exhausting the account's password lockout with bad second-factor guesses.

## MFA reset authorization

`POST /api/admin/users/{id}/mfa/reset` is the supported lost-authenticator path.

It requires:

- the `mfa.reset` permission (admin only by default);
- the operator's current password and MFA code (reauthentication);
- a reason of at least 10 characters;
- same-tenant visibility for institution admins.

It clears the target's TOTP secret, MFA flag, recovery codes, and MFA counters,
revokes every target session and refresh family, revokes outstanding JWTs, and
writes a `critical` `auth.mfa_reset` event plus the admin audit action. There is
no unauthenticated MFA reset endpoint.

## Forced reauthentication

A login starts a `reauth_at` window (`reauth_window_minutes`, default 15).
`POST /api/auth/reauth` verifies the current password and, when enabled, a TOTP
or recovery code, then refreshes that timestamp.

The following operations require a recent reauthentication and return `403` with
`X-Reauth-Required: true` and `X-Reauth-Purpose` otherwise:

- account export and account deletion;
- consent grant/revoke;
- portfolio share creation/revocation;
- MFA enrollment, disable, and recovery-code generation;
- role permission changes, role assignment, user creation/update;
- service-identity creation/revocation;
- break-glass request/approve/revoke/review;
- every export handled by the data-label middleware.

The frontend opens a reauthentication dialog on the `X-Reauth-Required` header.

## Argon2id parameters and recurring rehash

New passwords use Argon2id with explicit parameters:

| Parameter | Value |
|---|---|
| `time_cost` | 3 |
| `memory_cost` | 65536 KiB (64 MiB) |
| `parallelism` | 4 |
| `hash_len` | 32 bytes |
| `salt_len` | 16 bytes |

They are configurable through `ARGON2_*` environment variables. Bcrypt remains a
verification-only legacy adapter.

On successful login:

1. A bcrypt or legacy hash is upgraded to Argon2id.
2. `pwdlib` checks whether the existing Argon2id hash needs rehashing because a
   parameter changed.
3. A hash older than `password_rehash_days` (default 365) is rehashed.
4. `users.password_rehashed_at` is stamped and an `auth.password_rehashed`
   event records the parameter set.

All password writes (registration, admin create/reset, change password, setup,
SSO provisioning, service identities) stamp the policy timestamp.

## Rate limits and event windows

Per-IP login and registration limits apply at the router. Normally:

| Endpoint | Per-IP limit |
|---|---|
| Login | 10/minute |
| Registration | 5/minute; 30/hour; 100/day |

An active, non-archived competition is the platform's scheduled event. From
`EVENT_BURST_BUFFER_MINUTES` (default 30) before `start_at` until the same
margin after `end_at`, the limits relax to:

| Endpoint | Event-window limit |
|---|---|
| Login | 40/minute |
| Registration | 20/minute; 120/hour; 400/day |

The check runs per request and is cached per worker for 20 seconds, so moving a
competition in the admin UI takes effect without a restart. A database failure
falls back to the strict limits. `LOGIN_RATE_LIMIT` and
`LOGIN_BURST_RATE_LIMIT` override the login values; the invite-code and
approval gates still decide who may register.

## Tests

`tests/test_auth_lifecycle.py` covers refresh rotation/reuse, tenant-bound
sessions, export reauthentication, recovery-code single-use/expiry, MFA
brute-force lock, admin MFA reset authorization, and Argon2id rehash.

`tests/test_mfa.py` covers enrollment, QR generation, and login enforcement.
