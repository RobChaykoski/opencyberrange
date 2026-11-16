# Release 5 production readiness

Status: **`v5.17.1` is released and deployed.** Development `172.16.16.44` and
production `172.16.16.41` both run `main` at `7c0d0603` (`v5.17.1`) with Alembic
`0040_settings_change_control`. The release tags `v5.0.0`, `v5.0.1`,
`v5.1.0`, `v5.1.1`, `v5.1.2`, `v5.2.0`, `v5.2.1`, `v5.2.2`, `v5.3.0`,
`v5.3.1`, `v5.4.0`, `v5.5.0`, `v5.6.0`, `v5.7.0`, `v5.8.0`, `v5.8.1`,
`v5.9.0`, `v5.9.1`, `v5.10.0`, `v5.11.0`, `v5.12.0`, `v5.13.0`, `v5.13.1`,
`v5.14.0`, `v5.15.0`, `v5.16.0`, `v5.17.0`, and `v5.17.1` record the feature
releases, security patches, and operations patches.

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
- Migrations `0015`–`0040`, all idempotent and applied on dev and production.

## 5.17.1 deployment record - 2026-11-16

- Deployed from `main` at `7c0d0603` (`v5.17.1`). Backend and frontend were
  rebuilt from the release tree.
- Pre-deploy backup: `~/backups/ocr-backup-20261116-181526.dump` (checksum and
  platform env recorded alongside it).
- Restore drill on that backup: **PASSED** (users, labs, courses, enrollments,
  completions, achievements, review requests, and activity events matched).
- Alembic remained at `0040_settings_change_control`; no schema migration was
  required.
- Verified: backend, frontend, database, and Valkey healthy; `/api/version`
  returns `5.17.1`; `/health` returns 200; 191 labs registered.
- Production guards verified: `ENVIRONMENT=production`,
  `OCR_DEPLOYMENT_MODE=production`, `OCR_AUTHZ_STRICT=true`, WireGuard key set.
- Consent defaults verified: Cyber DNA, Cyber GPS, and portfolio are opt-in
  (`default_granted=false`).
- Admin release status reports **Up to date** against `v5.17.1`.
- This is a code deployment. Database `deployment_mode` remains `development`
  and `data_collection_mode` remains `sample`; the one-way cutover has not run.
- Tag `v5.17.1` is signed with the release key
  `68A817762C831475F00DB54E775050A4C4921814` at commit `7c0d0603`.

## 5.17.0 deployment record - 2026-11-16

- Deployed from `main` at `291d831b` (`v5.17.0`). Backend and frontend were
  rebuilt from the release tree; the integrity manifest and About licence
  inventory were re-stamped for 5.17.0 before the final backend rebuild.
- Pre-deploy backup: `~/backups/ocr-backup-20261116-172935.dump` (1.68 MB),
  plus `ocr-backup-20261116-172935.dump.sha256` and
  `platform-env-20261116-172935`.
- Alembic remained at `0040_settings_change_control`; no schema migration or
  manual SQL was required.
- Verified: backend, frontend, database, and Valkey healthy; `/api/version`
  returns `5.17.0` with the Release 5.17 name; `/health` returns 200; 191 labs
  are registered.
- The admin **Release status** panel is installed and reports the installed
  version against the latest GitHub release/tag, with the upgrade path and
  rollback note. The signed `v5.17.0` tag makes the release comparison current.
- This is a code deployment. The one-way production cutover remains a separate
  password-confirmed change.
- Tag `v5.17.0` is signed with the release key
  `68A817762C831475F00DB54E775050A4C4921814`.

## 5.16.0 deployment record - 2026-11-15

- Deployed from `main` at `6c94ad52` (`v5.16.0`). Backend rebuilt from the
  release commit; the frontend was unchanged and not recreated.
- Pre-deploy backup: `~/backups/ocr-backup-20261115-225613.dump` (1.3 MB,
  858 objects), plus `erasure-ledger-20261115-225613.jsonl` and
  `platform-env-20261115-225613`.
- Alembic upgraded `0030_cohort_strict` → `0031_learner_snapshots` on backend
  startup. No data migration or manual SQL was required.
- Lab discovery picked up `network-12-6-appliance-segment` after the post-pull
  `chmod -R a+rX platform/labs` (the 027 umask otherwise left `lab.yaml`
  unreadable to the non-root backend). 191 labs are registered.
- Wiki tree rebuilt from the release commit with the `wiki-builder` profile;
  exercise 12.5 is served at
  `/wiki/range/netfor/CH_NET12_Device_Topology/05_Network_Appliance_Segment/`.
- `ocr-lab/network-12-6-appliance-segment-protected:latest` prebuilt on the
  host; `openwrt/rootfs@sha256:46c1…` pulled for the appliance.
- Verified: backend, frontend, database, and Valkey healthy; `/api/version` = 5
  with the Release 5 name; Alembic `0031_learner_snapshots`; the new lab is
  active; the workbook page renders. 87 GB remains free at 54% used.
- Tag `v5.16.0` is signed with the release key
  `68A817762C831475F00DB54E775050A4C4921814` at commit `6c94ad52`.

## 5.15.0 deployment record - 2026-11-15

- Both hosts had already been rebuilt from the 5.15.0 code on 2026-11-15
  (development 20:20 UTC, production 20:24 UTC). The backend source inside both
  images matches the release tree exactly, so `v5.15.0` needed no image rebuild
  and no migration.
- Fast-forwarded the development and production checkouts to `e645be91`
  (`v5.15.0`). Only documentation and workbook text changed after the image
  builds, so the running containers were not recreated.
- Rebuilt the development wiki tree from the release commit with
  `ocr-wiki-builder:latest` (14 sites). Production already carried the updated
  workbook text from its 20:28 UTC build.
- Verified: backend, frontend, database, and Valkey healthy on both hosts with
  the remaining services up; `/api/version` = 5 with the Release 5 name; Alembic
  unchanged at `0030_cohort_strict`; 195 built workbook pages carry the
  "RangeBox or the VPN" wording on each host.
- Tag `v5.15.0` is signed with the release key
  `68A817762C831475F00DB54E775050A4C4921814` at commit `e645be91`.
- Verified the production RangeBox `lite` wordlist paths inside the image:
  `common.txt` (4,751 lines) and `directory-list-2.3-medium.txt` (220,559
  lines), at both the SecLists and the dirb/dirbuster paths the workbooks use.

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
  `/dev/kvm` exists and falls back to QEMU TCG when it does not. Production's VM
  CPU type was changed to expose `vmx`; `/dev/kvm` is now present.
- Production smoke test: spawned `metasploit-1-1-workspace-and-modules` with a
  Kali RangeBox. The target log reported `KVM acceleration enabled`, the KVM
  device was present in the target container, and the RangeBox retrieved
  `OCR{msf_workspace_7c1a}` from `http://target/flag.txt`. The temporary user and
  session were removed.
- LVM: the root LV was 99 GiB inside a 198 GiB volume group. Extended the LV to
  198 GiB and grew ext4 online; root is now 195 GiB with about 97 GiB free (43%
  used). The root filesystem had reached 100% during the target image build,
  which prompted the expansion.
- The older Release 4 rollback images were removed to make room before the
  expansion. The 5.13.1 rollback images remain.

## Live memory forensics lab - 2026-11-15

- Added Forensics level 3 with the `forensics-3-1-live-linux-memory` lab.
  The target is an Ubuntu 22.04 guest with AVML 0.21.0, reached over SSH.
- Production imported lab row 190 with `validation_status=ok` and
  `requires_kvm=false`; the platform injects `/dev/kvm` when the host probe
  succeeds.
- Built `ocr-ubuntu-memory:latest` on production and ran the lab with a Kali
  RangeBox. The target used KVM acceleration, the student acquired a 2.0 GiB
  memory image, transferred it with `scp`, and recovered
  `MEMFLAG=OCR{live_mem_4f8c2a}`.
- The SHA-256 matched after transfer. Temporary user, completions, session, and
  containers were removed. Production had about 82 GiB free after the image
  build.
- Ubuntu cloud images are downloaded on demand; AVML is MIT licensed. Neither
  the guest image nor the AVML binary is committed to the repository.

## Image hardening and lab spawn fix - 2026-11-15

- Fixed the lab launcher regression introduced by the process-limit hardening.
  Compose rejects a service that carries both `pids_limit` and
  `deploy.resources.limits.pids`; the override now writes the limit in the
  same shape the lab's compose file uses. Verified on development with a
  `deploy` lab (`linux-1-1-ssh-service-detection`) and a plain lab
  (`ai-1-1-prompt-injection-basics`), then on production with `linux-1-1`
  (session 242). Temporary users and sessions were erased afterwards.
- Rebuilt backend and frontend from `54d3013b` with pinned base digests,
  `apt-get upgrade` / `apk upgrade`, and a smaller backend runtime: no `curl`,
  `gnupg`, `pip`, `setuptools`, or `wheel`. Production reports revision
  `54d3013b`, HTTPS returns 200, and HTTP redirects to HTTPS.
- Grype counts after the rebuild: backend 345 matches (1 critical, 105 high),
  frontend 3 matches (0 critical, 0 high). The remaining critical is a Debian
  `wont-fix` `libxml2` entry. The full triage is in
  [`SECURITY-SCANNING.md`](SECURITY-SCANNING.md).
- Development `/workbook` was owned by UID 10001 while the dev backend runs as
  UID 1000, so the erasure ledger could not be written there. Re-owned the
  volume to 1000; production was already correct.
- The signed supply-chain lock was refreshed for the Dockerfile changes and
  re-signed with release key `68A817762C831475F00DB54E775050A4C4921814`.

## OT setpoint tampering lab - 2026-11-15

- Added `ot-1-2-modbus-setpoint-tampering` to the OT track. The target is the
  original pymodbus controller, extended with a process simulation: holding
  register 10 is a writable setpoint, register 11 reports the measured value,
  and a setpoint of 250 or more trips the interlock and exposes the marker.
- Development imported the lab as row 207 and production as row 191, both
  `validation_status=ok`. The target image was built on both hosts as
  `ocr-lab/ot-1-2-modbus-setpoint-tampering-plc:latest`.
- End-to-end checks on both hosts: spawn with a temporary learner, run the
  three manifest test steps from a sidecar on the lab network (service
  reachable, setpoint writes and reads back as 250, marker decodes to
  `OCR{m0dbu5_wr1t3_c0ntr0l}`), submit the flag, then erase the learner and
  session. The workbook page builds and serves on both hosts.
- OpenPLC was evaluated for this lab and deferred. The maintained OpenPLC
  Runtime v4 image starts but exposes no Modbus registers without a program ZIP
  produced by the OpenPLC Editor, and the v3 runtime repository is archived
  upstream. The pymodbus controller is original content and stays consistent
  with exercise 1.1.

## OT setpoint and gateway labs - 2026-11-15

- Added `ot-1-2-modbus-setpoint-tampering` and
  `ot-1-3-modbus-gateway-bypass`. The gateway lab places the PLC on an internal
  control network behind a proxy that filters only function code 0x06; students
  bypass it with 0x10.
- Development imported 1.2 as row 207 and 1.3 as row 208. Production imported
  1.2 as row 191 and 1.3 as row 192, both `validation_status=ok`.
- End-to-end on both hosts: spawn with a temporary learner, confirm the PLC is
  unreachable from the lab network, read through the gateway, observe the
  blocked 0x06 write, bypass with 0x10, recover the marker, submit the flag,
  then erase the learner. The workbook wiki builds on both hosts.
- Permission fix: after the 027 umask hardening, `git pull` wrote new lab files
  as `rw-rw----`. The production backend runs as UID 10001 and could not read
  the new `lab.yaml`, so discovery reported "no lab.yaml". The deploy scripts
  now normalise read permissions on `platform/labs` and `templates`.

## Python 3.13 runtime - 2026-11-15

- Backend runtime and CI moved from Python 3.11 to 3.13. The base is pinned to
  `python:3.13-slim@sha256:e48f59cd…`; CI, pip-audit, quality, and
  security-delta workflows run the same minor.
- Pre-flight: the full backend suite (630 tests) passed on 3.13 against
  PostgreSQL 17 before the image change was merged.
- Deployed to development and production. Both report Python 3.13.18, no `pip`
  in the runtime image, and healthy backend/frontend endpoints. A real lab
  spawn plus stop succeeded on both hosts and the temporary learners were
  erased.
- Grype on the production backend: 339 matches (1 critical, 105 high), matching
  the local rebuild. The remaining interpreter findings are fixed only on
  3.15/3.16, which are not stable.
- Added `deploy/host-hardening.sh`, which applies the two low-risk Lynis items
  (umask 027, disabled core dumps). Applied on both hosts: development moved
  from 62 to 64 with one reboot warning, production from 63 to 65 with no
  warnings. `AUTH-9328` and `KRNL-5820` no longer appear in either report.

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

Released on 2026-11-14 as `v5.0.0` and maintained through `v5.15.0` on
2026-11-15 for the implemented scope above.
Do **not** describe the deferred items as shipped. A real Canvas/Brightspace
staging test and the external accessibility/security assessments remain
institutional or later-release work.



















