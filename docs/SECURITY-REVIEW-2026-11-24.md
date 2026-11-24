# Security review log: 24 November 2026

Status: **review triage**. This page records the findings from the latest
security/design read of the authentication, admin, Docker, topology, and
password-reset surfaces. It is not a claim that every item is fixed.

## Fixed in this pass

| Area | Fix |
|---|---|
| Lab target frame | `frame-src` now permits the dynamic lab-target origins. The workbook stays pinned to the `:8443` origin; lab targets are internal IPs that CSP cannot express as a host list. |
| Shared VM console | The placeholder no longer shows a yellow "Connecting..." pill, no longer claims a live session, uses a real button class, and explains the direct-connect fallback when `window.close()` is blocked. |
| Auth revocation | The `_check_token_revocation` docstring now states the fail-closed behaviour. WebSocket ticket expiry converts aware timestamps with `astimezone` instead of replacing the offset. |

## High-priority backlog

| Area | Finding | Next action |
|---|---|---|
| `docker_manager.py` | The backend talks to the Docker socket and runs privileged/host-network helper containers with runtime `apk add`. Backend code execution is host-root-equivalent. | Pre-bake a pinned helper image; remove runtime package installation; document that the backend is host-root-equivalent; consider a host-side agent. |
| `admin.py` | Several user/session/audit endpoints use the platform-admin dependency without the institution scope used by the core user endpoints. | Audit every admin action for institution scope; platform-only actions must say so explicitly. |
| `admin.py` | `OCR_DEV_TOOLS` defaults on; stress-run state lives in `/tmp`; a new run deletes prior run files. | Default dev tools off outside development; move state to a service-owned directory; retain prior runs. |
| `main.py` | Middleware order and early error/CORS behaviour need a live check; inline DDL and Alembic both own schema. | Add a middleware-order contract test; move inline startup DDL to Alembic where possible. |
| `auth.py` | Login failure counters are in-process, so multiple workers multiply the limit; trusted-proxy IP extraction must be verified. | Move throttling to a shared store; assert `X-Forwarded-For` is only trusted from the proxy. |
| `config.py` | `WG_ENCRYPTION_KEY` is required but not validated as a Fernet key at startup. | Validate Fernet format and previous-key format during `validate_settings`. |
| `topology_engine.py` | `http_port` is not range-checked; `security_opt` type is not enforced. | Reject non-list `security_opt`; require `1 <= port <= 65535` and reject booleans. |
| `reauth.py` | Failed reauth events omit IP, user agent, and request id. | Pass request context into `security_events.record`. |
| `password_reset.py` | Docstring claims no issuer/audience; implementation uses both. Token TTL and session revocation depend on the caller. | Update the docstring; confirm the caller revokes sessions and checks account state. |
| Cyber DNA service | Several scoring paths load every observation into memory; timezone stripping assumes UTC. | Move to SQL aggregation or cache; convert aware datetimes to UTC before stripping. |

## Review rule

A finding is not closed by a comment. Close it with a test, a migration, or a
documented operational control. The highest-risk item remains the Docker socket
and privileged helper-container path in `docker_manager.py`; treat that as a
host-isolation decision, not a code-style cleanup.
