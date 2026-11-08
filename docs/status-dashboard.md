# Deployment status

Generated: `2026-11-08T19:39:34+00:00`

**Overall:** `healthy` - All deployments are up and on the expected version.

| Environment | Role | URL | Up | API | Version | Expected | Users | Setup | Build asset | Response |
|---|---|---|---:|---:|---|---|---:|---|---|---:|
| Prod | production | https://192.168.120.41 | yes | yes | `2.5.2` | `2.5.2 (Production platform release)` | yes | yes | `index-BByiXsta.js` | 50 ms |
| Dev | development | https://192.168.120.44 | yes | yes | `2.5.2` | `2.5.2 (Professional current platform release)` | yes | yes | `index-BByiXsta.js` | 51 ms |

Checks use public endpoints only: `/api/version`, `/api/setup/status`, and `/`.
No login, learner records, secrets, or private data are read.
Container and Docker host state are not exposed by the public API; confirm
them with `docker compose ps` on each host.
