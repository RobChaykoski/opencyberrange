# Deployment status

Generated: `2026-11-23T00:42:05+00:00`

**Overall:** `healthy` - All deployments are up and on the expected version.

| Environment | Role | URL | Up | API | Version | Expected | Users | Setup | Build asset | Response |
|---|---|---|---:|---:|---|---|---:|---|---|---:|
| OCR | production | https://<platform-host> | yes | yes | `5.30.2` | `5.30.2 (OCR production deployment)` | yes | yes | `index-BVKF_BDO.js` | 77 ms |
| OCR dev | development | https://<dev-host-ip> | yes | yes | `5.30.2` | `5.30.2 (OCR development deployment)` | yes | yes | `index-BVKF_BDO.js` | 46 ms |

Checks use public endpoints only: `/api/version`, `/api/setup/status`, and `/`.
No login, learner records, secrets, or private data are read.
Container and Docker host state are not exposed by the public API; confirm
them with `docker compose ps` on each host.
