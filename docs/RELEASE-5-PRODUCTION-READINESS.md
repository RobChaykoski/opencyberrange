# Release 5 production readiness

Status: **released and deployed to production on 2026-11-14 (`v5.7.0`).**
Development `172.16.16.44` and production `172.16.16.41` both track `main`;
Alembic `0028_course_planning`. Production application images were built from the `v5.7.0`
commit; `v5.0.0`, `v5.0.1`, `v5.1.0`, `v5.1.1`, `v5.1.2`, `v5.2.0`, `v5.2.1`, `v5.2.2`, `v5.3.0`, `v5.3.1`, `v5.4.0`, `v5.5.0`, `v5.6.0`, and `v5.7.0` record the release,
security patch, IdP settings feature, and operations patch.

## Ready for production

- **LTI 1.3 Advantage** — platform registry, OIDC login, launch validation,
  account linking, AGS 2.0, NRPS 2.0, Deep Linking 2.0, tool JWKS, framed
  picker/callback. Verified end to end against Moodle 5.0.2, including a grade
  in the Moodle gradebook and NRPS roster sync.
- **Accommodations** — per-student time multiplier, due-date extension, and
  pause/resume clock; instructor management and learner controls; audited.
- **Minor accounts** — enrollment consent reference, consent-needed flags,
  restricted leaderboards/celebrations/analytics, and a per-course retention
  policy with preview counts and append-only completion evidence.
- **Human review** — deterministic-result notice, learner review requests,
  instructor approve/reject decisions with notes, and audited status.
- **Exercise workspace** — one tabbed shell for every lab (Desktop / Exercise /
  Workbook), URL-persisted lab and tab, mobile layout, one RangeBox toolbar.
- **Workbook origin** — dedicated HTTPS origin on 8443, its own storage/search,
  CSP frame allowance, lazy loading.
- **RangeBox** — Kali base digest and SecLists commit pinned; only the
  wordlists the exercises reference are baked in, at their documented paths;
  the root-inside-caged-container model and Firefox sandbox rationale are
  documented in `RangeBox/SECURITY-MODEL.md`. noVNC is the selected path;
  terminal-only mode remains.
- Migrations `0015`–`0025`, all idempotent and applied on dev and production.

## Production deployment record — 2026-11-14

- Deployed from `main` at `bf3f6a2c` with `PLATFORM_VERSION=5`; Alembic upgraded
  `0024_retention` → `0025_review_requests`.
- Pre-deploy backups: `~/backups/ocr-pre-r5-20261114-044349.dump` (992 KB,
  629 objects), `~/backups/erasure-ledger-pre-r5-20261114-044349.jsonl`, and
  `~/backups/platform-env-pre-r5-20261114-044349`.
- Rollback images: `ocr-frontend:release4-rollback-20261114-044349` and
  `ocr-backend:release4-rollback-20261114-044349`.
- `wiki_origin` set to `https://172.16.16.41:8443`; the 8443 listener serves the
  main HTTPS server, `/wiki/` enforces the session gate (302), and the SPA CSP
  allows `frame-src https://*:8443`.
- `wiki_frame_ancestor` set to
  `https://172.16.16.41 https://ctfd.swocts.com https://70.54.16.7` after the
  5.0.0 smoke test showed the workbook was blocked when the app was opened on
  the direct host or the public domain.
- `opencyberrange/rangebox:lite` rebuilt on the host from the pinned Kali digest
  and SecLists commit; a fresh container served noVNC in 11 s and the documented
  wordlist paths exist inside the image.
- Verified: `/api/version` = 5 with release name **Release 5 (Powered by
  OpenCyberRange)**, backend `/health` database up, 179 labs, new review /
  accommodation / LTI / retention endpoints return 401 without a token, and the
  served `TrackDetail` bundle contains the workspace tabs and review panel.
- **5.0.1 patch (same day)** deployed from `9b943b41`: LDAP referral and
  plaintext hardening, OIDC algorithm allowlist, SSO redirect guard. Backend and
  frontend rebuilt, both healthy, Alembic unchanged at `0025`.
- **5.1.0 feature release (same day)** deployed from `318699e6`: identity
  provider settings export/import (dry-run first, secrets never exported,
  missing secrets force a provider disabled, audited), the unused `meta.module`
  router branch removed, nightly backups pushed off-host. Verified on
  development with a temporary admin: export, create, re-import skip, and
  cleanup all passed. Open Badges 3.0 remains planned for a later 5.x release.
- **5.2.0 feature release (same day)** deployed from `51cb9faa`: admin and
  course-scoped interaction history, server-side impersonation sessions with
  live/ended/expired status, migration `0026`, and encrypted multi-transport
  backups. Audit flow verified on development with a temporary admin.
- **5.2.1 security patch (same day)** deployed from `ea518981`: default-deny lab
  egress. Testing had found lab containers could reach the platform frontend
  (80/443/8443), host SSH, and lab gateways; those paths are now dropped while
  same-lab, shared targets, and QEMU guests keep working.
- **5.2.2 patch (same day)** fixes the startup egress helper (it now installs
  `iptables`) and schedules the egress script at boot and every five minutes.
- **5.3.0 feature release (same day)** adds the System → Metrics view and
  migration `0027_system_metrics`: per-minute samples of CPU load, memory, disk,
  active sessions, DB connections, RangeBoxes, and container/image counts, with
  inline SVG history graphs and 1h/6h/24h/7d windows.

## Deliberately deferred

- **KasmVNC** — evaluated as a transport replacement, not selected for 5.0.
  noVNC is stable on dev; the shell and workbook consistency problems were not
  caused by the VNC transport. Revisit after 5.0 with latency, resize, and
  reconnect measurements.
- **Distroless/Chainguard frontend** — nginx:alpine remains the serving base.
  A distroless migration would remove the shell entrypoint that selects the
  HTTP/HTTPS config and risks the production serving path. Defer to a dedicated
  5.1 serving-layer change with header/auth parity tests.
- **Multi-tenancy and the TA role** — Release 5 is a documented single-tenant
  appliance; one database per institution. Do not represent it as shared
  multi-tenant.
- **Weekly challenge quizzes / Cyber DNA** — not in this release candidate.
- **VPAT 2.5/ACR, SOC 2, ISO 27001, completed HECVAT** — not certifications
  held by this release.

## Production preconditions

1. Take and verify a database backup and a copy of the erasure ledger.
2. Deploy backend + frontend images from the release commit, or pull `main`
   after the release merge.
3. Apply migrations `0015`–`0025` during a maintenance window. Dev upgraded
   cleanly from `0014` to `0025`; the migration is additive.
4. Confirm **TCP 8443** reaches the frontend. Probed on 2026-11-14: production
   UFW is disabled (`/etc/ufw/ufw.conf` `ENABLED=no`), and 8443 resets rather
   than drops from both the workstation and development, so no host firewall
   change is required. Release 4 does not publish the port yet; after deploying,
   confirm a browser can open `https://<production-host>:8443`.
5. Set the `wiki_origin` platform setting to `https://<production-host>:8443`.
6. Set `PLATFORM_VERSION=5` for the frontend build and confirm `/api/version`
   reports 5.
7. Register the production LTI platforms (Canvas/Moodle/Brightspace) with the
   login URL, launch/redirect URI, tool JWKS URL, and each LMS's issuer/client/
   deployment values.
8. Confirm RangeBox capacity: production live cap 15, event ceiling 15.
9. Rebuild `opencyberrange/rangebox:lite` from the release commit and confirm
   the documented wordlist paths exist inside it. Production's current image
   predates the pinned base and wordlist fixes.

## Verification checklist

- `/api/version` = 5; backend `/health` reports the database up (`/health` on the
  SPA origin is a client route, so probe the backend on port 8000).
- `alembic current` = `0028_course_planning`; no failed migrations.
- 179 labs discovered; ten random lab detail checks pass.
- Authenticated pages: dashboard, exercises, Windows track, workbooks, courses,
  profile, instructor, admin, admin settings.
- Exercise workspace: Desktop/Exercise/Workbook tabs; RangeBox connects;
  reload restores the tab; workbook loads from 8443 with no console errors.
- Pause/resume credits paused time; accommodation multiplier and due-date
  extension read back for the learner.
- LTI: login redirect, launch, Deep Linking picker, JWKS fetch, AGS line item +
  reviewed score, NRPS sync.
- Admin course retention: save, preview counts, completion reference, run list.
- Rollback images retained; database backup path recorded.

## Rollback

- Production has the Release 4 rollback images tagged
  `ocr-frontend:release4-rollback-20261114-044349` and
  `ocr-backend:release4-rollback-20261114-044349`, plus the pre-deploy database
  dump and erasure-ledger copy listed above.
- The schema migrations are additive; a rollback before traffic should restore
  the database dump, not run destructive downgrades in place.

## Release gate

Released on 2026-11-14 as `v5.0.0` for the implemented scope above.
Do **not** describe the deferred items as shipped. A real Canvas/Brightspace
staging test and the external accessibility/security assessments remain
institutional or later-release work.











