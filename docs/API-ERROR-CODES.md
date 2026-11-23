# API error codes

Status: **convention and first migrations.** The frontend still renders
`detail`, so every migrated endpoint keeps its human-readable message. New and
migrated endpoints add a stable `X-Error-Code` header that a client can
translate.

## Contract

```http
HTTP/1.1 400 Bad Request
X-Error-Code: username_taken
Content-Type: application/json

{"detail": "Username already exists"}
```

- `detail` stays human-readable for compatibility and for clients that do not
  read the header.
- `X-Error-Code` is stable, lower_snake_case, and never changes meaning.
- The code is for the client, not for logging. The server still logs the
  request and the actor.
- Do not put a translated sentence in `detail` as the only signal. Add the code
  first, then translate on the client.
- CORS exposes `X-Error-Code` and the existing re-authentication/session
  headers.

## Helper

```python
from app.api_errors import api_error

raise api_error(400, "username_taken", "Username already exists")
```

The helper returns an `HTTPException` with the code header. Existing
`raise HTTPException(...)` sites can migrate incrementally; do not change the
message and the status in the same change.

## Initial codes

| Code | Status | Meaning |
|---|---|---|
| `username_taken` | 400 | The requested username is already in use |
| `email_taken` | 400 | The requested email is already in use |
| `student_id_taken` | 400 | The requested student ID is already in use |
| `account_exists` | 400 | Registration matches an existing account |
| `lab_slug_taken` | 400 | The exercise slug is already in use |
| `reauth_required` | 403 | A recent re-authentication is required |
| `session_invalid` | 401 | The session is expired, revoked, or bound elsewhere |
| `security_version_stale` | 401 | The account security version changed; sign in again |
| `impersonation_read_only` | 403 | A mutating action was blocked during View As |
| `consent_required` | 403 | A consent gate blocks the requested derived-data service |

The existing `X-Reauth-Required`, `X-Session-Invalid`, `X-Security-Version`, and
`X-Impersonating` headers remain. Do not duplicate them with a code unless the
endpoint needs a more specific reason.

## Migration order

1. Authentication and registration.
2. Course and exercise authoring validation.
3. Consent and privacy-request flows.
4. Export and report validation.
5. Everything else as a file is touched.

## Frontend use

The shared axios client can read `error.response.headers['x-error-code']` and
map it to a locale key. Until the mapping exists, keep the current `detail`
rendering. Do not show the raw code to a learner.

## Rules

- A code is a contract. Rename it only with a versioned API change.
- A code must be specific enough to choose a different next step.
- Do not use a code for a server error that the user cannot act on.
- Do not include PII, a username, an email, or a secret in a code.
