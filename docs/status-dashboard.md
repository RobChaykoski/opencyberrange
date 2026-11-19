# Deployment status

Generated: `2026-11-19T19:51:32+00:00`

**Overall:** `healthy` - All deployments are up and on the expected version.

| Environment | Role | URL | Up | API | Version | Expected | Users | Setup | Build asset | Response |
|---|---|---|---:|---:|---|---|---:|---|---|---:|
| OCR | production | https://ctfd.swocts.com | yes | yes | `5.27.1` | `5.27.1 (OCR production deployment)` | yes | yes | `index-fNwqPTTY.js` | 8 ms |
| OCR dev | development | https://172.16.16.44 | yes | yes | `5.27.1` | `5.27.1 (OCR development deployment)` | yes | yes | `index-fNwqPTTY.js` | 8 ms |

Checks use public endpoints only: `/api/version`, `/api/setup/status`, and `/`.
No login, learner records, secrets, or private data are read.
Container and Docker host state are not exposed by the public API; confirm
them with `docker compose ps` on each host.
