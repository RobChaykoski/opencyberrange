# Deployment status

Generated: `2026-11-08T08:44:15+00:00`

**Overall:** `healthy` - All deployments are up and on the expected version.

| Environment | Role | URL | Up | API | Version | Expected | Users | Setup | Build asset | Response |
|---|---|---|---:|---:|---|---|---:|---|---|---:|
| Prod | production | https://172.16.16.41 | yes | yes | `2.4.1` | `2.4.1 (Production platform release)` | yes | yes | `index-DYdG2FHQ.js` | 50 ms |
| Dev | development | https://172.16.16.44 | yes | yes | `2.4.1` | `2.4.1 (Professional current platform release)` | yes | yes | `index-Cg_AXJ6x.js` | 52 ms |

Checks use public endpoints only: `/api/version`, `/api/setup/status`, and `/`.
No login, learner records, secrets, or private data are read.
Container and Docker host state are not exposed by the public API; confirm
them with `docker compose ps` on each host.
