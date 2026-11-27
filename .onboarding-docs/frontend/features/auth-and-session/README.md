# Auth and session (frontend)

## Purpose

Render the login, registration, recovery, SSO callback, and first-run setup
screens; keep the browser session alive with one refresh path; and redirect
safely when the backend rejects a token.

## Routes and views

| Route | View | Notes |
|---|---|---|
| `/login` | `views/Login.vue` | form login, SSO buttons, reauth entry |
| `/register` | `views/Register.vue` | age band, privacy acknowledgment, invite code |
| `/forgot-password` | `views/ForgotPassword.vue` | request reset |
| `/reset-password` | `views/ResetPassword.vue` | consume reset token |
| `/sso/callback` | `views/SsoCallback.vue` | exchange one-time code |
| `/lti/callback` | `views/LtiCallback.vue` | LTI launch exchange |
| `/setup` | `views/Setup.vue` | first-run wizard |

## API calls

| Action | Endpoint |
|---|---|
| Login | `POST /api/auth/login` (form encoded) |
| Refresh | `POST /api/auth/refresh` |
| Current user | `GET /api/auth/me` |
| Logout | `POST /api/auth/logout` |
| Reauth | `POST /api/auth/reauth` |
| Register | `POST /api/auth/register` |
| SSO providers | `GET /api/auth/sso/providers` |
| SSO exchange | `POST /api/auth/sso/exchange` |

## Storage

| Store | Key | Purpose |
|---|---|---|
| `localStorage` | `token` | access token |
| `localStorage` | `refresh_token` | rotating refresh token |
| `localStorage` | `user` | cached display identity |
| `sessionStorage` | `ocr_impersonating` | impersonation flag |
| `sessionStorage` | `ocr_original_session` | restore token on exit |

`src/api/axios.js` adds the token, retries once after refresh, clears the session
on failure, and redirects to `/login`. A `403` with `X-Reauth-Required` opens
the reauth flow instead of logging the user out.

## Run and test

```bash
cd platform/frontend
npm run dev
npm test
npm run lint
```

Backend tests that cover the same contract:

```bash
cd platform/backend
python -m pytest tests/test_auth.py tests/test_auth_lifecycle.py \
  tests/test_jwt_validation.py tests/test_login_throttle.py -q
```

## Extension checklist

- Add the route and the guard together.
- Keep the token in the Axios interceptor; do not read it in every component.
- Add a loading and an error state for every auth call.
- Do not log a token or a password.
- Do not redirect to an external `next` URL without an allow-list.
- Update the blackbox login suite if the form contract changes.

## Related

- [Backend login](../../../backend/features/login/README.md)
- [Backend registration](../../../backend/features/registration/README.md)
- [Frontend overview](../../subsystem-overview.md)
