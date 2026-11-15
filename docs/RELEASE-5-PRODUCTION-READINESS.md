# Release 5 production readiness

Status: **released and deployed to production on 2026-11-14 (`v5.14.0`).**
Development `172.16.16.44` and production `172.16.16.41` both track `main`;
Alembic `0030_cohort_strict`. Production application images were built from the
`1c5a0d9e` commit; `v5.0.0`, `v5.0.1`, `v5.1.0`, `v5.1.1`, `v5.1.2`, `v5.2.0`, `v5.2.1`, `v5.2.2`, `v5.3.0`, `v5.3.1`, `v5.4.0`, `v5.5.0`, `v5.6.0`, `v5.7.0`, `v5.8.0`, `v5.8.1`, `v5.9.0`, `v5.9.1`, `v5.10.0`, `v5.11.0`, `v5.12.0`, `v5.13.0`, `v5.13.1`, and `v5.14.0` record the release,
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
  documented in `RangeBox/SECURITY-MODEL.md`. noVNC was the 5.0 path; the Kali
  image now uses KasmVNC with a pinned platform-served client (5.11 line), and
  terminal-only mode remains.
- Migrations `0015`–`0030`, all idempotent and applied on dev and production.

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

## 5.14.0 deployment record - 2026-11-14

- Deployed from `main` at `1c5a0d9e` with `PLATFORM_VERSION=5`; backend and
  frontend rebuilt, and Alembic upgraded `0029_open_badges` to
  `0030_cohort_strict`.
- Pre-deploy backup: `~/opencyberrange/backups/pre-5.14.0-20261114-230150.sql.gz`
  (796 KB, `gzip -t` clean), with the environment copy
  `platform-env-pre-5.14.0-20261114-230150`.
- Rollback images: `ocr-backend:rollback-5.13.1-20261114-230150` and
  `ocr-frontend:rollback-5.13.1-20261114-230150`.
- Tag `v5.14.0` is signed with the replacement release key
  `68A817762C831475F00DB54E775050A4C4921814` at commit `1c5a0d9e`.
  The previous key remains published for verifying older tags.
- Verified: backend and frontend healthy, `/api/version` = 5, database up,
  Alembic `0030_cohort_strict`, 179 active labs, 12 tracks, the SPA returned
  200, the workbook origin returned the 302 session gate, and the certificate
  PDF endpoint returned 401 without a token.
- Docker build cache was pruned (about 2 GB); 14 GB remains free at 86% used.
  The 55 GB of reclaimable images are active-lab prebuilds retained for fast
  spawning, not stale layers.
- The production git tree was pulled to `045efe38` (documentation, key rotation,
  and a test-only change) while the running images remain those built from
  `1c5a0d9e`.
- Certificate PDFs now honor the selected design. On development, classic,
  executive, modern, and minimal returned distinct sizes and SHA-256 hashes;
  an unknown design falls back to classic.
- Strict cohort mode was exercised end to end on development with a temporary
  course, two cohorts, two exercise sets, a default cohort, and an enrolled
  learner. Default sync placed the learner, cohort A saw two of four assigned
  labs, cohort B saw the other two, and removing the requirements or disabling
  strict mode restored all four. The learner course page reported "0 of 2
  assigned exercises". The temporary course, user, and completions were
  deleted afterwards.
- Strict cohort mode was also smoke-tested on production with a temporary
  course, user, two cohorts, two exercise sets, and a default cohort. Cohort A
  returned labs 1-2, cohort B returned labs 3-4, and disabling strict mode or
  removing the requirements returned all four labs. The course page reported
  "0 of 2 assigned exercises" for the filtered cohort. The course, user, and
  related rows were deleted; production returned to its single course.

## Metasploit track and LVM expansion - 2026-11-15

- Deployed `main` at `bbb7fe9d` to production; backend and frontend rebuilt and
  healthy.
- Seeded the `Metasploit Operations` track (8 labs) and imported it. Production
  lab rows 182-189 validate `ok`; `requires_kvm` is false so the platform does
  not refuse the spawn on this host.
- Built `ocr-metasploitable2:latest` on production. The target uses KVM when
  `/dev/kvm` exists and falls back to QEMU TCG when it does not. Production is a
  KVM guest without nested virtualization, so it uses TCG.
- Production smoke test: spawned `metasploit-1-1-workspace-and-modules` with a
  Kali RangeBox. The target booted under TCG, injected its flag, and the
  RangeBox retrieved `OCR{msf_workspace_7c1a}` from
  `http://target/flag.txt`. The temporary user and session were removed.
- LVM: the root LV was 99 GiB inside a 198 GiB volume group. Extended the LV to
  198 GiB and grew ext4 online; root is now 195 GiB with about 97 GiB free (43%
  used). The root filesystem had reached 100% during the target image build,
  which prompted the expansion.
- The older Release 4 rollback images were removed to make room before the
  expansion. The 5.13.1 rollback images remain.

## Deliberately deferred

- **KasmVNC** - evaluated for 5.0 and deferred, then adopted for the Kali
  RangeBox in the 5.11 line. KasmVNC's own client is required for input and
  resize; the platform serves a pinned copy and proxies only the WebSocket. See
  [`KASMVNC.md`](KASMVNC.md). All three desktop images use KasmVNC; noVNC
  remains available for older images.
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
3. Apply migrations `0015`–`0030` during a maintenance window. Dev upgraded
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
- `alembic current` = `0030_cohort_strict`; no failed migrations.
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

- Production retains the 5.13.1 rollback images
  (`ocr-frontend:rollback-5.13.1-20261114-230150` and
  `ocr-backend:rollback-5.13.1-20261114-230150`), plus the pre-deploy database
  dump and erasure-ledger copy listed above. The older Release 4 rollback images
  were retired on 2026-11-15 during the LVM expansion.
- The schema migrations are additive; a rollback before traffic should restore
  the database dump, not run destructive downgrades in place.

## Release gate

Released on 2026-11-14 as `v5.0.0` for the implemented scope above.
Do **not** describe the deferred items as shipped. A real Canvas/Brightspace
staging test and the external accessibility/security assessments remain
institutional or later-release work.



















