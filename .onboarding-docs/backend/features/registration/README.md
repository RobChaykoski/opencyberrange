# Registration

## Purpose

Create a learner account with explicit privacy acknowledgment, an age band, an
optional invite code, and an approval gate. Registration must not reveal whether
an account already exists.

## Code map

| Concern | Location |
|---|---|
| Router | `platform/backend/app/routers/auth.py` (`POST /register`) |
| Request model | `RegisterRequest` in `routers/auth.py` |
| Input safety | `platform/backend/app/services/input_safety.py` |
| Network/email gate | `platform/backend/app/services/network_access.py` |
| Password breach | `platform/backend/app/services/password_breach.py` |
| Invite codes | `platform/backend/app/models/auth.py`, admin invite routes |
| Approval | `platform/backend/app/routers/admin.py` (`/users/approve`, `/users/create`) |

## API surface

| Method | Path | Notes |
|---|---|---|
| POST | `/api/auth/register` | JSON; username, email, password, age band, privacy acknowledgment |
| POST | `/api/admin/users/approve` | admin approves pending accounts |
| POST | `/api/admin/users/create` | admin-created account, including institution-managed minors |
| GET | `/api/admin/users/pending` | approval queue |

## Behaviour that matters

- **Privacy acknowledgment is mandatory.** `privacy_acknowledged: false` returns
  `400`.
- **Under-13 self-registration is refused.** It returns `403`; an instructor or
  institution admin must create the account with a parental/guardian consent
  reference.
- **Age band.** `18_plus`, `16_17`, `13_15`, `under_13`. The older `is_minor`
  flag maps to `13_15` for compatibility.
- **Invite gate.** Off by default. When `require_invite_code=true`, a valid,
  unused, unexpired code is required. Email-pinned codes only register their own
  address.
- **Approval gate.** On by default. When `require_approval=false`, the account
  is auto-approved. The account still starts private: no scoreboard, no public
  certificates.
- **Enumeration.** Existing username, email, or student id returns one generic
  `account_exists` error. It does reveal that one of the three exists; treat that
  as a residual privacy finding, not a secret.
- **Input safety.** Control characters, bidi overrides, invisible characters,
  null bytes, and overlong fields are rejected or normalised.
- **Breach check.** Optional; an unavailable API fails open so sign-up is not
  blocked by a third party.

## Persistent state

| Store | Data |
|---|---|
| `users` | account, profile fields, age band, privacy timestamps, role, approval |
| `invite_codes` | code, creator, email pin, used_by/used_at, expiry |
| `activity_events` | `USER_REGISTERED` |
| `security_events` | registration outcome and approval requirement |
| Email | optional registration message if the learner opts in |

## Fixtures and tests

- `seed_demo_class.py` creates students and an instructor for development.
- Admin-created accounts use `POST /api/admin/users/create`.
- Focused tests:

```bash
cd platform/backend
python -m pytest tests/test_auth_lifecycle.py tests/test_input_safety.py \
  tests/test_password_policy.py tests/test_login_approval.py \
  tests/test_minor_safe.py tests/test_public_config_api.py -q
```

## Extension checklist

- Add the field to `RegisterRequest`, the model, and the response schema.
- Add validation and a test for the hostile form.
- Update the privacy notice and data dictionary if you collect a new field.
- Keep the approval and invite gates independent.
- Never allow a new account to become public by default.

## Related

- [Login](../login/README.md)
- [Privacy and consent](../privacy-and-consent/README.md)
- [Roles and admin](../roles-and-admin/README.md)
- [Minor-safe defaults](../../../../docs/MINOR-SAFE-DEFAULTS.md)
