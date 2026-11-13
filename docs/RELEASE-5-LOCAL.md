# Release 5 local development stack

Status: **development only.** Production remains on Release 4.

This guide brings up the Release 5 branch on a workstation without touching the
development or production hosts.

## Images

Built locally from the `release5` branch:

```bash
cd platform
docker compose -p ocr-r5 \
  -f docker-compose.dev.yml \
  -f docker-compose.release5-local.yml \
  --env-file /path/to/ocr-r5.env \
  build backend frontend
```

Tags: `opencyberrange-backend:release5`,
`opencyberrange-frontend:release5`.

The local override publishes:

| Service | URL |
|---|---|
| Frontend | `http://localhost:18081` |
| Backend | `http://localhost:18080` |

The default 80/443 ports are left free for an existing local stack.

## Environment

The local env file is disposable and must not be committed. Required values:

- `JWT_SECRET` and `WG_ENCRYPTION_KEY` generated for this stack only.
- `SETUP_TOKEN` for the first-run wizard (`local-r5-setup-token` in the local
  test).
- `DATABASE_URL`, `POSTGRES_PASSWORD`, and the usual Compose values.
- `LABS_HOST_PATH` pointing at `platform/labs` on the host.
- `PUBLIC_BASE_URL` / `FRONTEND_BASE_URL` = `http://localhost:18081`.

## First run

```bash
curl -X POST http://localhost:18081/api/setup/complete \
  -H "Content-Type: application/json" \
  --data-binary @ocr-r5-setup.json

docker exec ocr-r5-backend python /app/app/scripts/init_platform.py
```

The example-course seed requires an admin user; create the admin through setup
first, then rerun the initializer.

## Wiki

Build the workbook wiki into the local volume:

```bash
docker build -t ocr-wiki-builder:release5 wiki-builder
docker run --rm \
  -v "$PWD/..:/repo:ro" \
  -v ocr-r5_wiki_data:/out \
  ocr-wiki-builder:release5
```

## Verified on this stack

- `/api/version` = **5**, release name **Release 5 (Development)**.
- Platform initialization imported **179 labs** and **12 tracks**.
- Ten randomly selected labs passed validation and API discoverability:
  High School, AI, Windows, Malware, Web, Identity, OSINT, Linux, Forensics,
  and OT.
- Authenticated page pass: dashboard, exercises, workbooks, courses, profile,
  admin users, admin settings, and the Wiki settings tab.
- Backend: **335 passed, 219 skipped**.
- Frontend build and lint: clean (existing warnings only).
- Licence, safe-URL, CSP, and signed supply-chain guards pass on the branch.

## Known local limitations

- Lab spawning requires the host firewall/network setup and the RangeBox image.
  The local override sets `HOST_NETWORK=192.168.65.0/24` (Docker Desktop's host
  network), but Docker Desktop still cannot execute the privileged iptables
  verification (`'NoneType' object has no attribute 'decode'`). The local stack
  therefore verifies the platform, content, wiki, and pages but does not
  complete a live RangeBox launch. Live workspace regression is run on
  development (`172.16.16.44`), where host isolation works.
- The local stack uses HTTP on port 18081. Production keeps TLS and the
  custom-hostname settings.

## Skills and templates used

- `opencyberrange-student-tester` — ten-lab content and discoverability pass.
- `opencyberrange-design-tester` — page hierarchy, themes, responsive workspace,
  and admin settings review.
- `opencyberrange-software-security` — safe-URL bindings and the security delta
  review.
- `opencyberrange-inclusive-curriculum` — minor-account and high-school framing.
- `opencyberrange-learning-impact` — analytics and retention planning.
- `opencyberrange-course-content-management` — course/lab relationship checks.
- `opencyberrange-ha-architecture` and `opencyberrange-program-management` —
  local-versus-deployed boundaries and release gating.
- Existing `platform/templates` and the Compose templates; no new lab template
  or content pattern was introduced for the local stack.

## Do not deploy

Do not promote `release5` to development or production until the Release 5
exit criteria in [`RELEASE-5-SCOPE.md`](RELEASE-5-SCOPE.md) are met. Production
must stay on the signed `v4` tag.
