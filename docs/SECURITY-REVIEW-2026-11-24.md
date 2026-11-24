# Security review log: 24 November 2026

Status: **review triage**. This page records the findings from the latest
security/design read of the authentication, admin, Docker, topology, and
password-reset surfaces. It is not a claim that every item is fixed.

A broader code, database, dependency, and host-currency review is in
[Code and database review, 24 November 2026](CODE-AND-DATABASE-REVIEW-2026-11-24.md).

## Fixed in this pass

| Area | Fix |
|---|---|
| Lab target frame | `frame-src` now permits the dynamic lab-target origins. The workbook stays pinned to the `:8443` origin; lab targets are internal IPs that CSP cannot express as a host list. |
| Shared VM console | The placeholder no longer shows a yellow "Connecting..." pill, no longer claims a live session, uses a real button class, and explains the direct-connect fallback when `window.close()` is blocked. |
| Auth revocation | The `_check_token_revocation` docstring now states the fail-closed behaviour. WebSocket ticket expiry converts aware timestamps with `astimezone` instead of replacing the offset. |
| Cross-worker state | Exercise-tester, impersonation, and stress-run state moved from `/tmp` to `/app/run-state` (mode 750). |
| WireGuard key format | `WG_ENCRYPTION_KEY` and previous rotation keys are validated as Fernet keys at startup. |
| Topology input | `security_opt` must be a list of strings keeping `no-new-privileges`; `http_port` is range-checked. |
| Password-breach digest | The HIBP SHA-1 lookup is marked `usedforsecurity=False`; storage remains Argon2id. |
| Index hygiene | Migrations `0061` and `0062` remove redundant indexes and add the instructor and lab-session hot-path indexes. |

## High-priority backlog

| Area | Finding | Next action |
|---|---|---|
| `docker_manager.py` | The backend talks to the Docker socket and runs privileged/host-network helper containers with runtime `apk add`. Backend code execution is host-root-equivalent. | Pre-bake a pinned helper image; remove runtime package installation; document that the backend is host-root-equivalent; consider a host-side agent. |
| `admin.py` | Several user/session/audit endpoints use the platform-admin dependency without the institution scope used by the core user endpoints. | Audit every admin action for institution scope; platform-only actions must say so explicitly. |
| `admin.py` | `OCR_DEV_TOOLS` defaults on; stress-run state now lives under `/app/run-state`, but a new run still deletes prior run files. | Default dev tools off outside development; retain prior runs. |
| `main.py` | Middleware order and early error/CORS behaviour need a live check; inline DDL and Alembic both own schema. | Add a middleware-order contract test; move inline startup DDL to Alembic where possible. |
| `auth.py` | Login failure counters are in-process, so multiple workers multiply the limit; trusted-proxy IP extraction must be verified. | Move throttling to a shared store; assert `X-Forwarded-For` is only trusted from the proxy. |
| `config.py` | Fixed: `WG_ENCRYPTION_KEY` and previous rotation keys are validated as Fernet keys at startup. | Covered by `f35fa608` and tests. |
| `topology_engine.py` | Fixed: `security_opt` must be a string list keeping `no-new-privileges`; `http_port` is range-checked and rejects booleans. | Covered by `e60eb51a` and tests. |
| `reauth.py` | Failed reauth events omit IP, user agent, and request id. | Pass request context into `security_events.record`. |
| `password_reset.py` | Docstring claims no issuer/audience; implementation uses both. Token TTL and session revocation depend on the caller. | Update the docstring; confirm the caller revokes sessions and checks account state. |
| Cyber DNA service | Several scoring paths load every observation into memory; timezone stripping assumes UTC. | Move to SQL aggregation or cache; convert aware datetimes to UTC before stripping. |

## Review rule

A finding is not closed by a comment. Close it with a test, a migration, or a
documented operational control. The highest-risk item remains the Docker socket
and privileged helper-container path in `docker_manager.py`; treat that as a
host-isolation decision, not a code-style cleanup.
