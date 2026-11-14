# Release 5 production readiness

Status: **release candidate prepared; production not yet deployed.**
Development `172.16.16.44` is running Release 5 (backend `893fbcfe`, frontend
`29603dad`, Alembic `0024`). Production remains on the signed Release 4 hotfix
`v4.0.2`.

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
- **Exercise workspace** — one tabbed shell for every lab (Desktop / Exercise /
  Workbook), URL-persisted lab and tab, mobile layout, one RangeBox toolbar.
- **Workbook origin** — dedicated HTTPS origin on 8443, its own storage/search,
  CSP frame allowance, lazy loading.
- Migrations `0015`–`0024`, all idempotent and applied on dev.

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
3. Apply migrations `0015`–`0024` during a maintenance window. Dev upgraded
   cleanly from `0014` to `0024`; the migration is additive.
4. Open **TCP 8443** in the host firewall. The frontend container exposes it; the
   browser must reach it for workbooks.
5. Set the `wiki_origin` platform setting to `https://<production-host>:8443`.
6. Set `PLATFORM_VERSION=5` for the frontend build and confirm `/api/version`
   reports 5.
7. Register the production LTI platforms (Canvas/Moodle/Brightspace) with the
   login URL, launch/redirect URI, tool JWKS URL, and each LMS's issuer/client/
   deployment values.
8. Confirm RangeBox capacity: production live cap 15, event ceiling 15.

## Verification checklist

- `/api/version` = 5; `/health` database up.
- `alembic current` = `0024_retention`; no failed migrations.
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

- Production currently has the `v4.0.2` frontend image tagged for rollback and
  a database backup. For Release 5, keep the previous backend/frontend image
  tags and the pre-deploy database dump.
- The schema migrations are additive; a rollback before traffic should restore
  the database dump, not run destructive downgrades in place.

## Release gate

Go for a controlled Release 5 deployment of the implemented scope above.
Do **not** describe the deferred items as shipped. A real Canvas/Brightspace
staging test and the external accessibility/security assessments remain
institutional or later-release work.
