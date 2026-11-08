# Deployment status

Generated: `2026-11-08T02:24:47+00:00`

**Overall:** `healthy` - All deployments are up and on the expected version.

| Environment | Role | URL | Up | API | Version | Expected | Users | Setup | Build asset | Response |
|---|---|---|---:|---:|---|---|---:|---|---|---:|
| Prod | production | https://172.16.16.41 | yes | yes | `2.2.0` | `2.2.0 (Production platform release)` | yes | yes | `index-Bq9uVjxq.js` | 54 ms |
| Dev | development | https://172.16.16.44 | yes | yes | `2.2.0` | `2.2.0 (Professional current platform release)` | yes | yes | `index-Bq9uVjxq.js` | 52 ms |

Checks use public endpoints only: `/api/version`, `/api/setup/status`, and `/`.
No login, learner records, secrets, or private data are read.
Container and Docker host state are not exposed by the public API; confirm
them with `docker compose ps` on each host.
