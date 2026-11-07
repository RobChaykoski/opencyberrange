# Deployment status

Generated: `2026-11-07T20:47:17+00:00`

**Overall:** `healthy` - All deployments are up and on the expected version.

| Environment | Role | URL | Up | API | Version | Expected | Users | Setup | Build asset | Response |
|---|---|---|---:|---:|---|---|---:|---|---|---:|
| Prod | production | https://172.16.16.41 | yes | yes | `1.1.3` | `1.1.3 (Community / Academic maintenance line)` | yes | yes | `index-D8XbUsZI.js` | 52 ms |
| Dev | development | https://172.16.16.44 | yes | yes | `2.1.4` | `2.1.4 (Professional current platform release)` | yes | yes | `index-CJWOh6S5.js` | 35 ms |

Checks use public endpoints only: `/api/version`, `/api/setup/status`, and `/`.
No login, learner records, secrets, or private data are read.
Container and Docker host state are not exposed by the public API; confirm
them with `docker compose ps` on each host.
