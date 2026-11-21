# Moodle LTI pilot — event runbook

Use this for the first production pilot session on 2026-11-21. The detailed
verification record is in
[`PILOT-READINESS-REVIEW.md`](PILOT-READINESS-REVIEW.md); deployment details are
in [`deploy/moodle-prod/README.md`](../deploy/moodle-prod/README.md).

## At a glance

| Item | Value |
|---|---|
| Moodle | `https://moodle.swocts.com` |
| OpenCyberRange | `https://ctfd.swocts.com` |
| Course | `PILOT-101` — “SWOCTS Moodle Pilot Course” |
| Activity | “OpenCyberRange Pilot Lab” (`/mod/lti/view.php?id=2`) |
| Accounts | `ocr-prod:~/moodle-prod/pilot-accounts.csv` (mode `600`) |
| Admin credentials | `ocr-prod:~/moodle-prod/.env` (mode `600`) |
| Backups | `~/moodle-prod/backups` and `~/backups` |
| Public IP | `70.54.16.7` for both hostnames |
| DDNS | `~/cloudflare-ddns`, updates every 5 minutes |

Never paste the accounts CSV, `.env`, or the Cloudflare token into chat, email,
or the course.

## 15-minute pre-flight

```bash
# Public reachability and HSTS
curl -sSI https://moodle.swocts.com/login/index.php | grep -i strict-transport
curl -sSI https://ctfd.swocts.com/ | grep -i strict-transport

# LTI JWKS
curl -sS https://ctfd.swocts.com/api/lti/jwks | head -c 200; echo

# DNS and DDNS
getent hosts moodle.swocts.com ctfd.swocts.com
ssh ocr-prod 'cd ~/cloudflare-ddns && docker compose ps && docker compose logs --tail 5 --no-log-prefix'
```

Then:

1. Log in to Moodle as `pilot.student01`.
2. Open **PILOT-101 → OpenCyberRange Pilot Lab**.
3. Select **Start Exercise**, then **Workbook**. Confirm “Exercise 0.1 — Ping
   Basics” renders.
4. Check the student gradebook shows the prior LTI score (`80.00 / 100`).
5. Log in as `pilot.instructor` and confirm the OpenCyberRange dashboard shows
   “Teaching & operations”.

## Participant flow

1. Sign in at `https://moodle.swocts.com` with the supplied pilot account.
2. Open **My courses → PILOT-101**.
3. Open **OpenCyberRange Pilot Lab**.
4. Select **Start Exercise**; the desktop, exercise, and workbook panes load in
   the embedded platform.
5. Read the workbook, submit the flag, and use the feedback controls.
6. Select **Exit** when finished.

Participants do not need VPN for this pilot.

Instructor accounts are editing teachers. The OpenCyberRange instructor
dashboard is intentionally empty until Moodle courses are mapped to platform
courses; the LTI activity and gradebook are the pilot surfaces.

## Troubleshooting

| Symptom | Check |
|---|---|
| Workbook pane blank | Hard refresh (`Ctrl+Shift+R`), then copy the frame URL. Confirm it is `/wiki/range/netfor/...` and returns `200`. |
| `frame-ancestors` error | `wiki_frame_ancestor` must contain `https://moodle.swocts.com`; the backend caches it for 30 seconds. |
| `sitemap.xml` CORS error | Confirm the generated public sitemap route is present in the frontend container; see the workbook section in the prod README. |
| Launch loops back to login | Clear cookies for `moodle.swocts.com` and `ctfd.swocts.com`, then relaunch. |
| “Workbook opens when you select this tab” | The pane loads on tab selection in narrow layouts; select the Workbook tab again. |
| Grade not in Moodle | Scores post after the platform review gate. Check `lti_scores` and the Moodle gradebook; use the LTI panel to re-send if needed. |
| Roster looks stale | NRPS sync is on demand; refresh the roster from the LTI panel. |
| Moodle `500 Invalid permissions` | Run CLI commands as `daemon`, never root; restore `daemon:daemon` ownership on `/bitnami/moodledata/cache` and `/bitnami/moodledata/localcache`. |

## Do not do during the event

- Do not rebuild the backend or frontend.
- Do not change DNS, NPM upstreams, or TLS certificates.
- Do not run Moodle CLI commands as root.
- Do not apply database migrations.
- Do not revert the pilot-only networking exceptions until the session ends.

## Rollback

Take a backup before any change, then:

```bash
# Moodle database + data
cd ~/moodle-prod
# restore from the latest mysql dump and moodledata archive in ./backups

# OpenCyberRange
# restore ~/backups/ocr-backup-<timestamp>.dump with the normal restore procedure
```

If the Moodle host itself is the problem, point the NPM proxy host for
`moodle.swocts.com` back to the staging upstream. Do not delete the production
stack.

## After the event

1. Collect feedback and record the release decision.
2. Rotate the Cloudflare token; update `~/cloudflare-ddns/.env` and run
   `docker compose up -d`.
3. Deploy the LTI instructor-role mapping (already in the repository) with a
   backend rebuild.
4. Restrict `ocr-pg-gateway` (`172.16.16.41:5432`) to the lab network or
   localhost.
5. Revert the pilot-only exceptions: `sso_enabled=true`, the relaxed Moodle
   cURL allow-list, and the broad `wiki_frame_ancestor` list.
6. Rebuild the high-school wiki so the four restored links ship.
7. Decide whether Workbooks cards should open the track’s first exercise rather
   than the shared workbook landing page.
8. Remove the `pilot.instructor` local role workaround once role mapping is
   deployed.
