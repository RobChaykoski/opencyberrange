# Deployment status

Generated: `2026-11-11T21:23:28+00:00`

**Overall:** `healthy` - All deployments are up and on the expected version.

| Environment | Role | URL | Up | API | Version | Expected | Users | Setup | Build asset | Response |
|---|---|---|---:|---:|---|---|---:|---|---|---:|
| OCR | production | https://ctfd.swocts.com | yes | yes | `2.7.0` | `2.7.0 (OCR production deployment)` | yes | yes | `index-D9M93U6G.js` | 54 ms |
| OCR dev | development | https://172.16.16.44 | yes | yes | `2.7.0` | `2.7.0 (OCR development deployment)` | yes | yes | `index-D9M93U6G.js` | 45 ms |

Checks use public endpoints only: `/api/version`, `/api/setup/status`, and `/`.
No login, learner records, secrets, or private data are read.
Container and Docker host state are not exposed by the public API; confirm
them with `docker compose ps` on each host.
