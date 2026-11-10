# Deployment status

Generated: `2026-11-10T01:58:20+00:00`

**Overall:** `healthy` — all OCR deployments are up and on the expected version.

| Environment | Role | URL | Up | API | Version | Expected | Users | Setup | Build asset | Response |
|---|---|---|---:|---:|---|---|---:|---|---|---:|
| OCR | production | https://ocr.swocts.com | yes | yes | `2.5.4` | `2.5.4 (OCR public deployment)` | yes | yes | `index-CYERGwfp.js` | 301 ms |
| CTFd host OCR | internal | https://172.16.16.41 | yes | yes | `2.5.4` | `2.5.4 (OCR stack on the CTFd host)` | yes | yes | `index-Xm7MfkTM.js` | 46 ms |

Checks use public endpoints only: `/api/version`, `/api/setup/status`, and `/`.
No login, learner records, secrets, or private data are read.

## Host notes

- `ocr.swocts.com` is the public OCR deployment at `172.16.16.44`.
- `172.16.16.41` is the CTFd host. It also runs an OCR stack; that stack is
  reported separately above.
- `ctfd.swocts.com` is the CTFd application itself and is not an OCR release
  target.
- Container and Docker host state are not exposed by the public API; confirm
  them with `docker compose ps` on each host.
