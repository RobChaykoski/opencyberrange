# Deployment status

Generated: `2026-11-10T08:31:00+00:00`

**Overall:** `healthy` - All deployments are up and on the expected version.

| Environment | Role | URL | Up | API | Version | Expected | Users | Setup | Build asset | Response |
|---|---|---|---:|---:|---|---|---:|---|---|---:|
| OCR | production | https://ocr.swocts.com | yes | yes | `2.6.0` | `2.6.0 (OCR public deployment)` | yes | yes | `index-Dx733NF9.js` | 68 ms |
| CTFd host OCR | internal | https://172.16.16.41 | yes | yes | `2.6.0` | `2.6.0 (OCR stack on the CTFd host)` | yes | yes | `index-Dx733NF9.js` | 49 ms |

Checks use public endpoints only: `/api/version`, `/api/setup/status`, and `/`.
No login, learner records, secrets, or private data are read.
Container and Docker host state are not exposed by the public API; confirm
them with `docker compose ps` on each host.
