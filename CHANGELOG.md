# Changelog

All notable changes to OpenCyberRange are recorded here.

## [Unreleased]

### Tenant isolation

- Added `scripts/check-tenant-isolation.py`: it audits the column, index, forced RLS, four policies, and derivation trigger on all 47 tenant tables, then probes every table as a foreign tenant that owns nothing.
- The audit passes on development and production as the runtime role with zero leaked rows.
- Added the two-tenant pilot runbook and classified `users` as the tenant source outside RLS by design.
- Added ADR 0010: the consent-subsystem RLS design, gated on the pilot, with pre-read tenant stamping and the subject-only suppression exception.
- Added `scripts/check-tenant-pilot-api.py` for two-token course, evidence, catalogue, and admin cross-tenant probes.
- Added the `ocr-labd` host harness: disposable container, status, stop, invalid ids, and audit-log checks.

## [5.49.0] - 2026-11-24

Course-owned content row-level security.

### Course-owned RLS

- Added migration `0067_course_content_rls`: `institution_id` on the six course-owned content tables, derived from `course_id`, with forced RLS and the four tenant policies.
- Extended the two-institution probe to a course-owned table; the enforced set is now 47 tables.
- Documented the consent subsystem as the next RLS wave; auth tables stay outside RLS by design.

## [5.48.0] - 2026-11-24

Tenant baseline migration and a fully reconciled schema.

### Tenant baseline

- Added migration `0066_tenant_baseline`: idempotent `institution_id` columns, defaults, `NOT NULL`, and indexes for the 20 runtime tenant tables.
- Added `institution_id` to the 18 models that lacked it and declared the two remaining readiness indexes.
- Alembic drift is **0** on development and production; the restore-drift gate now defaults to 0.
- Triggers and RLS policies remain runtime-managed pending the multi-tenant rollout.

## [5.47.0] - 2026-11-24

Threat intelligence, host-agent operations, and database model alignment.

### Threat awareness

- Added an aggregated ransomware-activity section sourced from RansomLook `/api/stats` and `/api/hot`: totals and top group names/counts only, with CC BY 4.0 attribution.
- Added `scripts/fetch-ransomware-feed.py` and `GET /api/ransomware-activity`; the service reads only allow-listed aggregate fields, so victim names, post links, crypto addresses, and peer addresses cannot reach the UI.
- Added ADR 0009: Global Threat Map rejected, RansomLook aggregate data accepted, Violations Watch rejected on legal and safeguarding grounds.

### Database

- Declared the seven runtime/legacy indexes in the models, including the partial unique one-active-session guard on `lab_sessions`.
- Aligned `portfolio_share_tokens`, `readiness_lab_reviews`, and `readiness_student_notes` to the database's `NOT NULL DEFAULT 'default'` `institution_id`.
- Development Alembic drift falls from 48 to a planned 38 operations; the remainder is tenant `institution_id` DDL.

### Host agent

- Implemented read-only `GET /v1/status/<lab_id>` in `ocr-labd`: validated lab id, fixed `docker inspect`, mapped state, and audited denials/failures.
- Implemented `POST /v1/stop` behind an explicit `--enable-stop` flag; it is refused with `501` by default and treats an already-stopped container as idempotent success.
- Expanded the CI smoke check with fake-runtime and mocked-Docker cases for status, stop, invalid ids, missing containers, disabled mutations, and runtime failures.
- Spawn, isolation, and mirror routes remain `501` until validated against the lab harness.

## [5.46.2] - 2026-11-24

Release metadata fix.

### Release engineering

- Regenerated `software-integrity.json` so its `release` field matches the tagged release. The 5.46.0 and 5.46.1 manifests still reported `5.45.0`, which failed the CI integrity gate.
- Added a release-preparation checklist covering the integrity manifest, supply-chain lock, and signature order.

## [5.46.1] - 2026-11-24

Threat-awareness panel design-system alignment.

### Design

- Replaced ad-hoc surfaces with the platform tokens (`--bg-secondary`, `--border-color`, `--text-secondary`, `--accent-bg`, `--warning-bg`) so the panel renders correctly in dark, light, and high-contrast themes.
- Bars now scale to the largest row for legibility and expose `role="progressbar"` with `aria-valuenow`, `aria-valuemin`, `aria-valuemax`, and a per-row label.
- Added an empty state, a 1080px reading column, a 640px responsive rule, focus-visible outlines, and reduced-motion handling.
- Moved counts and percentages to readable text roles instead of muted body copy.

## [5.46.0] - 2026-11-24

Host-agent spike, aggregated threat awareness, restore-drift gate, and
dependency currency.

### Operations

- Added `scripts/check-restore-drift.sh`, which restores the newest backup into a scratch database, migrates it, and enforces the 48-operation drift budget.
- Added the weekly dependency-currency report and documented the patch, base-image, and major-upgrade cadence.
- Seeded 25 unsigned legacy contract drafts on development for subject-matter sign-off.

### Host-agent spike

- Added `platform/labd/ocr_labd.py`, a loopback, token-authenticated agent skeleton with a fixed operation list and no arbitrary exec. Mutating routes return `501` until validated.
- Added the `ocr-labd.service` systemd unit, a CI boundary check, and ADR 0007 acceptance for the spike.
- Production remains on the pre-baked helper image and restricted socket proxy until the lab harness passes.

### Threat awareness

- Added a first-party, aggregated Threat Awareness panel at `/threat-awareness` and `GET /api/threat-awareness`. It returns country and feed counts only, with no individual address, hostname, or simulated attack path.
- Added `scripts/fetch-threat-feed.py` for offline refresh with a minimum bucket size, and [ADR 0008](docs/decisions/0008-threat-awareness.md) rejecting the GPL-3.0 Global Threat Map integration.
- Ships with a labelled sample snapshot; a live refresh is an explicit operations action.

## [5.45.0] - 2026-11-24

Database schema alignment: model index cleanup, missing FK indexes, the
WebSocket ticket model, legacy Kali column removal, descending index alignment,
and the host-isolation ADR and drift inventory.

### Alembic model alignment

- Added the `WebSocketTicket` model and migration `0064_ws_tickets`; removed the runtime `ws_tickets` DDL from startup.
- Removed 24 redundant `id` index declarations from the models and added migration `0063_missing_fk_indexes` for the 10 model-declared FK indexes missing from restored databases.
- Added the Docker host-isolation ADR and the classified Alembic drift inventory.

## [5.44.0] - 2026-11-24

Security verification and hardening: shared login-failure throttling, admin
tenant-isolation regression coverage, and an Alembic autogenerate guard.

### Alembic safety guard

- Added `scripts/check-alembic-safety.py` and the Alembic baseline guide. CI rejects autogenerate usage and verifies one linear head.

### Shared login throttle

- Login-failure backoff now uses the configured Valkey/Redis store with a bounded in-process fallback, so multiple workers share the same limit.

### Admin tenant isolation

- Added cross-tenant regression tests for the pending and locked account lists, user details, and activity log. The user, stats, activity, and course admin reads are now covered by tests.

## [5.43.1] - 2026-11-24

Patch: the in-place deploy and installer now run the helper-image build script
by path with bash, and the script is marked executable. A fresh deploy can no
longer skip the pinned `ocr-lab/netprobe:1.0` image.

## [5.43.0] - 2026-11-24

Dependency refresh and Docker helper hardening: current patch-level backend
packages and a pinned helper image that removes runtime package installation
from the privileged network helpers.

### Dependency refresh

- Updated FastAPI to `0.165.0`, SQLAlchemy to `2.1.9`, Pydantic to `2.14.4`, and pydantic-settings to `2.16.3`. The full backend suite passes.

### Docker helper image

- Added `ocr-lab/netprobe:1.0`, a digest-pinned Alpine image with `iproute2`, `iptables`, and `bridge-utils`.
- Replaced the runtime `alpine:latest` / `alpine:3.19` pulls and `apk add` calls in the Docker network helpers.
- Build the helper image during in-place deploy, development sync, and fresh install.

## [5.42.0] - 2026-11-24

Release 6 review operations, learner-visible contract state, workbook reliability,
security hardening, and database index hygiene.

### Competency review export

- Added `scripts/export-contract-reviews.py` with a pseudonymous signed-review
  manifest, a private administrator export, an overrides writer, and an offline
  `--check` gate that refuses a reviewed YAML entry without a matching signed
  review.
- Added `app.services.competency_contract_integrity` so the review service and
  the offline gate share the contract, lab, and taxonomy hashing rules.
- The contract generator now accepts a full signed `evidence` list and
  `assessment_criteria` from the overrides file and round-trips them.

### Learner-visible contract status

- The exercise page now marks the competency mapping provisional when the
  contract is pending, stale, overdue, or changes-requested. The notice does not
  block the lab or expose reviewer details. A compact **Mapping review** badge
  marks stale, overdue, and changes-requested labs in the exercise list.
- **My Evidence** now marks each record provisional when its lab contract is
  pending, stale, overdue, or changes-requested.

### Workbook reader

- The workbook link now opens a blank window, refreshes the HttpOnly wiki cookie,
  and then navigates. Opening the wiki first raced the cookie request and could
  land on the SPA login on a slow connection.

### Security and database hardening

- Cross-worker exercise-tester, impersonation, and stress-run state now lives
  under `/app/run-state` (mode 750), not the shared `/tmp`.
- `WG_ENCRYPTION_KEY` and previous rotation keys are validated as Fernet keys at
  startup.
- Topology `security_opt` must be a string list keeping `no-new-privileges`, and
  `http_port` rejects booleans, non-integers, and values outside 1-65535.
- The HIBP password lookup digest is marked `usedforsecurity=False`.
- Migrations `0061` and `0062` remove redundant indexes and add indexes for the
  instructor course filter and lab-session FK.
- Added the code, database, dependency, and host-currency review record.

## [5.41.0] - 2026-11-24

Contract-review operations and evidence-reporting corrections: the instructor
contract-review dashboard with sign-off and cycle tracking, evidence-review
analytics and decision-flow fixes, lab framing and console corrections, and
migration `0060_competency_reviews`.

### Contract review

- Added `/contract-review` for instructors and administrators: a cycle queue
  with status chips and filters, competency and evidence weight editors,
  reliability and criteria, a 6/12/24-month cycle selector, attestation, draft
  save, sign-off, history, and an administrator export-ready panel.
- Added `GET /api/competency-reviews/catalogue` with the taxonomy domains,
  competencies, evidence types, and cycle lengths.
- Added migration `0060_competency_reviews` with tenant scope, one active signed
  review per institution and lab, and an immutable-signature guard.

### Evidence review

- Corrected the analytics denominators: minors are excluded for non-admin
  viewers, superseded evidence is excluded, accepted-of-decided rates replace
  raw acceptance, and suppressed rates return null rather than zero.
- Weakest and strongest competency slices require at least five learners.
- The review queue accepts an optional `learner_id` filter without changing its
  oldest-first order.
- Fixed the post-decision state so a successful decision no longer shows a stale
  error, and the workbench advances to the next item.

### Security and reliability

- The SPA document, HTTPS server, and shared security-header snippet now agree on
  `frame-src` for dynamic lab targets while the workbook stays pinned to :8443.
- The shared-VM console placeholder is neutral and explains the manual-close
  fallback instead of showing a false "Connecting" state.
- Corrected the revocation docstring (the policy fails closed) and WebSocket
  ticket expiry timezone handling.
- Login-streak awards now retry on deadlock; recent completion ordering has a
  deterministic tie-breaker.

## [5.40.0] - 2026-11-24

Release 6 foundation and capstone planning: object coverage audit, quiz
competency mappings, learner-visible unmeasured rule, capstone planner with
saved plans and approval, and migration `0059_capstone_plans`.

### Release 6 foundation

- Added `scripts/audit-release6-coverage.py`, which audits every lab contract,
  certification quiz pathway, exercise quiz, capstone, and badge. CI runs it with
  `--fail-on-gaps`; `--require-reviewed` is the 6.0 gate.
- Added competency mappings to all nine certification quiz pathways.
- Added `scripts/competency-review-packet.py` and the competency review guide.
  Reviews are recorded in `competency-contract-overrides.yaml`, not the generated
  contract file.
- Applied the learner-visible rule to Cyber DNA, the portfolio, the competency
  taxonomy, and the instructor readiness panel. A null score renders as
  unmeasured, not zero, with a component regression test.
- Added the admin question-bank per-domain count and thin-domain highlight.

### Capstone planning

- Added `GET /api/capstones/profiles` and `POST /api/capstones/plan`, a
  deterministic planner over reviewed contracts with a validation gate.
- Added saved plans, versioning, approval, and archive at
  `/api/capstones/plans`. Approval requires the validation gate to pass and does
  not publish anything.
- Added migration `0059_capstone_plans` with forced tenant RLS.

## [5.39.0] - 2026-11-24

Release 6 foundations: evidence appeals, learner journeys, the Cyber Legacy
layer (impact, recognition, and the Living Archive), standalone certification
practice, programme analytics, and migrations `0054`–`0058`.

### Evidence review workflow

- Added the evidence reviewer surface at `/evidence-review` for instructors and
  administrators: queue, learner identity, source, rubric criteria and levels,
  prior decisions, and the accept / request-more / reject form.
- Added `GET /api/evidence/rubrics` to expose the versioned rubric registry and
  included the learner identity in the evidence payload for authorized
  reviewers.
- Added the `automatic-check` rubric and background adapters for correct flags
  and passed exercise knowledge checks. The adapters use the reviewed lab
  contract, append a system review, and are idempotent.
- Added workbook answer capture at `/workbook-answers`. Each distinct answer
  version is snapshotted into the evidence ledger with the `analyst-answer`
  rubric and waits in the instructor review queue; the review surface shows the
  submitted text.
- Added an evidence operations summary to the review surface: status totals,
  backlog age, source and rubric mix, strongest and weakest competencies,
  workbook/documentation coverage, a 30-day confidence trend, accepted rate,
  evidence per learner, and recent decisions. Aggregates below five learners are
  suppressed for non-admin reviewers.
- Added the program-layer design for persistent organizations, the scenario
  engine, the Cyber Transcript, and programme analytics, with strongest/weakest
  competency, graduation readiness, and programme-effectiveness definitions.
- Added evidence appeals: a learner can request one second review of a rejected
  record; a reviewer accepts or rejects the appeal with notes, and an accepted
  appeal returns the evidence to `in_review`. Added the learner **My Evidence**
  page and the reviewer appeal queue.
- Added learner-chosen journeys at `/journey` and `GET/PUT /api/journeys`. A
  journey maps a mission to existing competencies and a first step; switching
  direction keeps all evidence. Added the eight traditions (Protection,
  Creation, Discovery, Stewardship, Illumination, Connection, Service, Judgment)
  and mission filtering on the journey page.
- Added the impact ledger at `/impact` and `/api/impact`: build, protect, teach,
  and serve contributions, reviewer verification, logarithmic reach, a quality
  floor, diminishing repeats, decay for unused work, a Legacy Score, a Meaning
  Index, stewardship bands, and a self-view legacy class. There is no learner
  ranking endpoint.
- Added values-based recognition at `/api/recognition` and the **Your Impact**
  board: earned awards, clue-only secret achievements, sealed mythic awards, a
  rotating whisper, an idempotent rule engine, and audited manual awards with an
  evidence reference. Recognition never changes the Legacy Score. Earned awards
  present as historical markers, grouped by tradition.
- Added the Living Archive at `GET /api/archive/me`: traditions are inferred from
  verified contribution, never selected. The archive stays undetermined until
  there is breadth, returns narrative notes and counts rather than percentages,
  and never changes a score or permission. Removed the tradition selector from
  the journey page and replaced it with the observed archive.
- Added standalone certification practice at `/practice` and `/api/practice`:
  timed mock exams, domain drills, per-question option shuffling, a server-held
  answer key, spaced-repetition selection, attempt history, and per-domain
  accuracy. A practice pass is a study signal, not a credential.
- Added 30 original certification practice items across all nine pathways,
  concentrated on the thinnest domains, with public https references. The bank
  now carries 158 reviewed items.
- Added migration `0058_practice_sessions` with forced tenant RLS.
- Added the **Cyber Legacy** frame: the Age of Foundations, the First
  Generation, the eight traditions, and historical markers, linked from the
  programme docs and the learner manual.
- Added migrations `0055_learner_journeys`, `0056_impact_ledger`, and
  `0057_achievement_awards`, all tenant-scoped with forced RLS.
- Updated the i18n baseline for the new review surface, workbook answer page,
  journey, impact, recognition, and navigation entries.

### User manual and frameworks

- Updated the manual for 5.38.0: current install prerequisites, 215-lab and
  170-public counts, Authentik production identity, LTI 1.3 status, tenant
  isolation count, and the new evidence and workbook workflows.
- Added **Workbook Answers**, **Evidence Review**, and **External Skills
  Frameworks** pages to the manual navigation.
- Added the [SFIA 9 ingestion plan](docs/SFIA-9-INGESTION.md): licensing gate,
  proposed data model, mapping rules, review criteria, and the requirement for a
  licensed snapshot before any SFIA content or mapping is committed.
- Recorded that the SFIA **Personal Licence** does not permit product use,
  redistribution, or published mappings. The RDF converter repository's MIT
  licence covers the converter code, not the SFIA content. SFIA integration is
  blocked until a commercial or academic product licence is recorded.

## [5.38.0] - 2026-11-24

### Release 6 evidence ledger

- Added the append-only evidence ledger: `evidence_records`,
  `evidence_competencies`, and `evidence_reviews` (migration
  `0052_evidence_engine`).
- Added idempotent evidence creation with a rubric version, taxonomy
  competencies, artifact SHA-256, provenance, confidence, and visibility.
- Added instructor review decisions with per-criterion scores and a weighted
  result. Reviews are appended; evidence content remains immutable.
- Added tenant row-level security for the evidence tables, with child rows
  deriving their tenant from the parent evidence record.
- Added the evidence API: create, list, read, review queue, review, and
  competency evidence. Access is learner-, course-, or tenant-scoped.
- Added tests for idempotency, scope, scoring, queue filtering, validation, and
  append-only enforcement.

### Career affinity

- Added recency weighting to affinity ranking: practice in the last 365 days
  counts at full weight and older practice at half weight. Lifetime evidence
  remains visible, so a learner can change direction without losing history.
- Marked every affinity with growing or strong evidence as recommended, with a
  separate `primary` direction for the compact overview card. A multi-talented
  learner is no longer collapsed to one label.
- Removed course enrolment and advanced technical labs from the leadership
  affinity. Leadership now counts teaching and event success, so an active
  student is not misread as a programme lead.
- Added `recent_count` and `rank_count` to the affinity payload and used the
  weighted count in Career Atlas matching.

### OSINT canary lab

- Added the OSINT03 "Canary Tokens and Deception" chapter and lab 3.1
  "Noise in the Nest". The lab runs a synthetic public portal and canary
  console, records token hits, and asks the learner to separate a human
  navigation from link-preview, scanner, and uptime-monitor noise.
- Added the lab workbook, quiz, competency contract, tester manifest, and
  automated flag checks. The catalogue is now **215 labs**.

### Documentation

- Added a fresh-install requirements table and the `setup-range-server.sh`
  command near the top of the README, with the platform-only and post-install
  paths.

## [5.37.1] - 2026-11-23

### Deployment integrity

- Normalized `platform/labs` permissions during in-place deployment so the
  backend user (UID 10001) can read every lab file. Lab builds can leave
  root-owned or group-only files behind; the deploy script now runs
  `chmod -R a+rX` through the Docker group before rebuilding.
- Fixed the production software-integrity check reporting 208 of 214 labs as
  mismatches when the files were present but unreadable. The deployed content
  was unchanged; the backend could not read it.

## [5.37.0] - 2026-11-23

### Release 6 foundation

- Added the Admin **Learning → Quality** tab and
  `GET /api/admin/competency-coverage`: contract totals, reviewed and pending
  counts, per-track coverage, and the next 25 labs awaiting review.
- Added the competency-contract review queue, per-track review packets, and a
  structural validator for all 214 contracts (taxonomy ids, weight sums,
  evidence types, one contract per lab).
- Added a versioned rubric registry with `blue-team-timeline`,
  `vulnerability-report`, and `capstone-brief`, a loader, validation, and tests.
- Updated the i18n bare-string baseline for the Quality tab and documented the
  increase.

### Monitoring and operations

- Added the separate `deploy/monitoring` stack for `health.swocts.com`:
  Prometheus, Blackbox Exporter, Alertmanager, Pushgateway, Grafana, and an
  optional local `node_exporter`.
- Added provisioned Grafana dashboards, alert rules, private target files, and a
  per-host agent for Linux hosts.
- Added Authentik OIDC for the dashboard, a platform-admin policy binding, and
  Grafana role mapping.
- Wired Alertmanager to the existing platform SMTP settings with a private,
  gitignored config and Docker secret. Email delivery is verified.
- Added `scripts/deploy-inplace.sh` for the production `platform/` +
  `docker-compose.prod.yml` layout. It verifies the signed tag and supply-chain
  lock, takes a backup, tags rollback images, rebuilds the application and wiki,
  and verifies the deployed version.
- Added private, gitignored Prometheus target files so production addresses stay
  out of the public repository.

## [5.36.0] - 2026-11-23

### Security and deployment

- Removed the deprecated `X-XSS-Protection` header, scoped `frame-src` to the
  wiki origin, and added an nginx `rangebox_handshake` rate limit. The RangeBox
  WebSocket handshake now has an explicit budget instead of relying on headers.
- Scoped upload body limits to the routes that need them: lab import, workbook
  upload, instructor lab upload, report verification, user import, and restore.
  The default API limit is no longer lower than the backend's 10 MB default.
- `deploy-updates.sh` now fetches tags, proves the release key matches the
  pinned fingerprint, verifies the signed tag, checks out that tag, and only
  then runs the supply-chain check and applies the update. It refuses an
  unsigned `main` or ZIP update unless the development override is explicit.
- Install and update paths verify the Docker Compose download's SHA-256 before
  installing it. The host-script threat model and review checklist are in
  `docs/HOST-SCRIPT-SECURITY.md`.
- Backup snapshots are forced to directory mode `700` and file mode `600`;
  download and delete require recent re-authentication. The local plaintext
  decision, encrypted-volume requirement, and offsite GPG path are recorded in
  `docs/BACKUP-SECURITY.md`.
- `monitor-deployment.sh` supports an external dead-man switch and failure ping.
  `deploy/systemd/ocr-monitor.service` and `.timer` run the deep host checks,
  while `docs/OPERATIONS-MONITORING.md` defines the external uptime check and
  the host-down test.

### Labs and curriculum

- Reworked the Ping, Multiple Port Discovery, and OT workbook pages with the
  RangeBox/VPN access diagram, directional clipboard labels, target chips, and
  device inventories. The fictional company is consistently **Trailline**.
- Added `scripts/check-lab-freshness.py` and `scripts/select-lab-canary.py`.
  Quality fails on missing or stale reviews, and the weekly harness now covers a
  deterministic 20% canary so the whole fleet is exercised every five weeks.
- Catalogue counts remain **214 labs**, **204 workbook-mapped**, and **13
  tracks**. The generated manifest, contracts, outcomes, and coverage files were
  regenerated. The Cloud IAM lab is deferred to 5.37.0; it is not part of this
  release.

### Instructor analytics and reporting

- Added a shared period control with a dynamic default of **7 days** across the
  instructor dashboard, My Exercises, Reports & Analytics, and Learning
  Analytics.
- Added projections to the learning, activity, and Pulse charts, a live
  freshness/error state, per-period activity columns, and export metadata. A
  slow or empty feed is now visible instead of silently rendering zero.

### Admin, localization, and policy

- Split the largest admin panels with `defineAsyncComponent`; the Admin chunk
  dropped from roughly 396 KB to 286 KB. Added a 600 KB per-chunk / 200 KB entry
  bundle gate.
- Added the Vue bare-string budget gate at **4,943** strings, documented the
  English-first release and the Release 6.5 localization wave, and added
  `X-Error-Code` headers for migrated API errors.
- Added the Windows artifact policy and legal notice: institutions supply
  licensed media, and the repository ships no ISOs, images, or activation keys.
- Cloudflare DDNS settings are deferred to **5.37.0**. The supported 5.36.0
  path remains the firewall DDNS client or the `deploy/cloudflare-ddns`
  container.

## [5.35.0] - 2026-11-22

### Production identity

- Added the production Authentik stack and public OIDC provider, with learner
  and instructor login verification and correct group-to-role mapping.
- Normalized ID-token issuer validation for providers that sign a trailing
  slash, while keeping signature, audience, nonce, and algorithm checks.
- Local password login remains independent of `sso_enabled`; the break-glass
  administrator path is unchanged.

### Agentic AI capstone and DFIR

- Added `ai-2-2-multi-agent-privilege-escalation`, a two-service intake and
  audit-vault capstone with a workbook, CTF template, investigation evidence,
  and a remediation rubric. The catalogue is now 214 labs and 204 workbook
  pages.
- Added `DFIR-13 Enterprise Endpoint Hunting with Velociraptor`, including a
  synthetic hunt dataset, VQL/artifact objectives, custody requirements, and a
  peer-reviewed report requirement.

### Metadata, DLP, and policy

- Added `POST /scan` and `POST /scan-and-decide` to the context service, with
  detectors for private/public addresses, internal hosts, cloud metadata
  endpoints, assessment answer keys, and secret assignments.
- Added OPA rules for secret material, answer-key publication, unsafe
  publication, and infrastructure-metadata export.
- Added OpenDiscoveryEngine publication detectors and OpenGRC `PUB-001` through
  `PUB-004` classifications, policies, and `PublicationDlpSeeder`.
- Documented the ecosystem roles for DefectDojo, Steampipe/Powerpipe, Cloud
  Custodian, Sigstore, OpenMetadata, OPA, and Velociraptor, including the
  observation/decision/enforcement boundaries.

### Publication privacy

- Added `scripts/audit-publication.py`, the publication metadata policy, and the
  Quality CI gate. The audit indexes all lab flags and fails on answer keys or
  real infrastructure metadata in public files.
- Redacted real addresses, hostnames, deployment accounts, and answer keys from
  docs, workbooks, lab READMEs, generated manifests, tests, templates, and the
  CTF pack.
- Test manifests now store `{flag}` and `lab_harness.py` resolves it from
  `lab.yaml`; the public contract no longer contains answer keys.
- Deployment defaults bind to loopback or `*.example.com`; seed scripts require
  explicit origins and fail closed without them.
- Added proposed automotive/aerospace and drone MAVLink pathway designs.

### Fixes

- `status-dashboard.py` now requires `OCR_STATUS_PROD_URL` / `OCR_STATUS_DEV_URL`
  or a config file instead of a built-in deployment address.
- `setup-sso.py`, `seed_lti.py`, and `seed_lti.sh` require an explicit origin.
- Restored safe certificate filenames and loopback defaults in the Moodle seed
  and trust scripts.

## [5.34.0] - 2026-11-22

### Non-human identity lab

- Added `identity-1-3-nhi-oauth-abuse`: TrailGuard's debug logs leak an
  `svc-trailguard-bot` bearer token, and the internal audit API trusts it. The
  learner finds the token, reads the LumenPay audit exceptions, and maps the
  missing redaction, scope, workload-binding, and rotation controls.
- Added the **Non-Human Identity** exercise to `IAM01` with workbook
  walkthrough, review questions, four automated checks, and a `nhi` mock mode in
  the identity target.
- Regenerated competency contracts, outcomes, coverage, NICE mappings, integrity
  manifest, and the signed supply-chain lock. The catalogue is now 213 labs.

## [5.33.0] - 2026-11-22

### Trailline universe and agentic AI lab

- Established the **Trailline Security & GRC** fictional organisation as the
  shared setting for the Release 6 AI, identity, and GRC exercises. The
  [Trailline universe](../Workbook/TRAILLINE-UNIVERSE.md) page defines the
  domains, personas, data classes, and recurring service identity.
- Refactored `AI01` (prompt injection, jailbreak policy bypass, and indirect
  injection) to the TrailGuard AI / Trailline setting so the stream has one
  cast and one data model.
- Added `AI02: Agentic AI Security` and lab
  `ai-2-1-agent-hijacking`: a poisoned LumenPay vendor report causes TrailGuard
  AI to call an audit-export tool through `svc-trailguard-bot`. The lab
  includes a workbook chapter, three automated checks, and the deterministic
  `agent_hijack` mock mode.
- Added a provisional NICE mapping for the new lab, regenerated competency
  contracts and outcomes, and refreshed the curriculum, framework, coverage,
  and workbook navigation documents. The lab count is now 212.

## [5.32.1] - 2026-11-22

### Usage tracker

- The admin QR generator is served at `/api/usage/admin/qr` instead of a
  `.png` path. The frontend static-file rule intercepted the dotted path before
  the API proxy, so the image request returned the SPA 404. The response is
  still `image/png`.

## [5.32.0] - 2026-11-22

### Usage tracker and registration attribution

- Registration records a normalized source and campaign from `?src=` /
  `?utm_source=` and `?campaign=` / `?utm_campaign=`. Known sources are GDG,
  LinkedIn, SWOCTS, and direct; unfamiliar values are sanitized and kept.
- Added tracked QR landing links (`/api/public/qr/<source>`) that record a scan
  before redirecting to registration, plus an admin QR generator.
- Added the public usage tracker at `/usage`: daily registrations, QR scans, and
  lab completions; week-over-week cards; source and campaign breakdowns; top
  movers; latest aggregate activity; searchable lab telemetry; and JSON/CSV
  exports.
- Added the admin detail at `/admin/usage` with exact counts, source/campaign
  QR generation, and a labs CSV export.
- Public data never includes learner identities. Source and per-lab learner
  counts below the configured cohort threshold are suppressed.
- Migration `0051_registration_attribution` adds the source and campaign
  columns and the source index.

## [5.31.0] - 2026-11-22

### Cyber DNA v3 learner UI

- Added a **Career affinity** tab to the profile for learner accounts. It shows
  the affinity gate with text progress, pathway cards with score components and
  next steps, competency evidence, behavior signals, and the voluntary-interest
  vector.
- Consent-required, role-scoped, feature-disabled, loading, empty, and error
  states are handled explicitly. The tab is hidden for instructor and admin
  roles, which do not carry the learner-scoped `career_affinity.view.self`
  permission.
- Clarified the affinity explanation: evidence coverage and practitioner-level
  coverage are now separate statements, so "0% at practitioner level" no longer
  reads as "no evidence".
- Added `app/scripts/seed_dna_fixtures.py` for development: it creates a
  synthetic above-gate learner and grants consent only to that fixture and to
  the existing demo learner, then backfills through the consent-aware adapter.

## [5.30.2] - 2026-11-22

### Cyber DNA consent

- The completion backfill now applies the same consent gate as the live
  completion path. A completion that predates a revocation can no longer
  recreate evidence after the purge. The production backfill had bypassed this
  check; the rows written for learners without granted consent were removed and
  the backfill was re-run against consenting learners only.

### Moodle LTI networking

- Production Moodle's `curlsecurityblockedhosts` is narrowed from a blanket
  `172.16.0.0/12` omission to the default private ranges plus a carve-out that
  admits only the NPM address `<npm-host-ip>`. The tool JWKS fetch was verified
  through Moodle's own cURL wrapper, and other private targets are rejected.
  The dev-only seed path keeps its explicit private-URL relaxation.

### Deployment tooling

- Added `scripts/tag-release-images.sh`, which tags the images used by running
  platform containers before a rebuild. Docker's containerd image store can
  collect the replaced image during a build even while its container is
  running, which left the 5.30.0 deployment without a pre-release rollback tag.

## [5.30.1] - 2026-11-22

### LTI launches no longer depend on the SSO switch

- The one-time ticket exchange accepts a ticket that was already issued when
  the deployment-wide SSO switch is off. Disabling SSO still hides the provider
  list and rejects new provider logins, but it no longer blocks LTI launches,
  which use the same exchange. This removes the pilot-only requirement to leave
  `sso_enabled=true` on a local-login deployment.

## [5.30.0] - 2026-11-22

### Pilot feedback fixes

- RangeBox clipboard now works across the embedded iframe: the SPA, LTI, and
  KasmVNC responses allow `clipboard-read`/`clipboard-write`, and the existing
  iframe `allow` attribute can take effect. Browsers still prompt for clipboard
  access on first use.
- Workspace splitters use pointer capture and release on blur, so dragging the
  desktop/workbook dividers no longer sticks when the pointer crosses the
  RangeBox iframe.
- Stopping an exercise now shows a full-panel stopping state while the desktop
  and lab are released. A stopped RangeBox reports "This desktop has been
  stopped" instead of freezing silently.
- The exercise details pane collapses objectives, ATT&CK mappings, hostnames,
  the workbook link, and the review request behind disclosures, and clamps long
  scenarios. The flag, network targets, and hints stay visible.
- Wrong-flag feedback now points at look-alike characters (`0/o`, `1/l/i`,
  `3/e`, `5/s`, `7/t`) when a near-miss would otherwise match, which addresses
  the common manual-transcription failures seen in the pilot.
- Added Safari-style fallbacks for `100dvh` and prefixed `backdrop-filter`.
- Instructor stats aggregate assignment completions in one query instead of an
  assignment × learner nested loop.
- Workbook cards now open the workbook page for the exercise the learner is
  currently on in that track (a running session wins), or the first exercise
  when they have not started.

### Self-service password reset

- Added `POST /api/auth/forgot-password` and `POST /api/auth/reset-password`.
  The emailed link is a 30-minute, purpose-scoped token bound to the current
  password hash, so it stops working after any password change. Requests are
  rate-limited, the response never reveals whether an address exists, and SSO-only
  accounts are skipped.
- Reset mail is a configurable template (`mail_template_password_reset_*`) with
  its own notification preference. A successful reset unlocks the account,
  clears a forced change, and revokes every existing session.
- The login form now has a **Forgot password?** link with dedicated request and
  new-password pages.

### Tools drawer

- The ATT&CK Navigator and other tools now toggle from the sidebar, show a
  labelled **Close** action, and close automatically when the route changes. The
  panel footer explains the exit, which matters because Escape inside a
  cross-origin iframe is delivered to the frame rather than the platform.

### Career target

- Added a target-role switcher to the student dashboard and the profile header so
  learners can change their career goal without opening the portfolio tab. The
  choice still drives readiness, gap analysis, and aligned evidence.

### Privacy and age defaults

- New accounts now start private: public scoreboards, public certificate
  verification, and optional account email are opt-in. Minor accounts force
  scoreboards and public certificate verification off.
- Registration now collects a privacy-preserving age band instead of a single
  under-18 checkbox. Under-13 self-registration is blocked; an instructor must
  create an institution-managed account with a parental/guardian consent
  reference.
- SSO and LTI auto-provisioned accounts start private. A first-login privacy
  acknowledgement links to a new plain-language youth notice.
- The privacy notice, in-app privacy page, and student manual now correctly say
  Cyber DNA, Cyber GPS, and the professional portfolio are off until opted in.

### LTI 1.3

- A verified launch grant now opens the deep-linked course-only exercise even
  when the provisioned LMS user has no local course enrolment. The grant stays
  scoped to one user and one lab and does not bypass inactive, draft-owner, or
  minor/OSINT rules.
- The LTI platforms admin panel renders the saved NRPS roster as a minimum-field
  table instead of raw JSON.
- Added a screenshot-backed Moodle LTI 1.3 showcase and a launch-grant
  visibility regression test.
- LTI teacher launches now map the `membership#Instructor` role to the local
  instructor role. LMS administrators are not promoted.
- Added the production pilot readiness review covering public ingress, all 201
  workbook pages, 137 assets, 385 internal links, accounts, grade passback, and
  backups.
- The generated wiki serves a public empty sitemap for embedded workbook
  frames, removing the CORS/login console error without exposing page URLs.
- Moodle production HSTS is set at the Apache origin so it survives without an
  NPM admin change.
- Added the pilot event runbook: pre-flight checks, participant flow,
  troubleshooting, rollback, and the post-event cleanup list.
- Cloudflare DDNS is deployed and verified for the two public pilot records.

## [5.29.1] - 2026-11-21

### Backup compatibility

- Plain SQL backups now remove the PostgreSQL 17-only
  `SET transaction_timeout = 0;` line emitted by the newer pg_dump client.
  PostgreSQL 15 rejects that setting, so a restore with `ON_ERROR_STOP` could
  abort before loading any data. Existing backups remain readable; the rewrite
  is applied to new dumps.

## [5.29.0] - 2026-11-21

### Lab launch preflight

- When on-demand lab builds are disabled, an unbuilt lab is refused before a
  session is created. Students see a plain "still being prepared" message, and
  the exact `scripts/prebuild-labs.sh --lab <slug>` command is recorded for the
  admin health panel.
- The spawn-status fallback uses the same learner-facing message instead of a
  generic environment error.

### Analytics

- Added a shared ECharts wrapper and adopted it for the instructor pulse chart
  and course completion chart. Charts keep accessible data tables and load only
  in instructor-only chunks.

### Security and data handling

- Uploaded SQL dumps are validated before restore; `psql` runs as the migrator
  role with `-X` and `--no-psqlrc`.
- ZIP lab uploads reject symlinks, encrypted entries, duplicate paths,
  backslash/absolute paths, excessive entry counts, oversized entries, and
  suspicious compression ratios. Extraction is streamed and bounded.
- Refreshed Trivy waivers for the non-root backend and digest-pinned RangeBox.

### Content and contracts

- Added the 211th lab, regenerated competency contracts and outcomes, and
  refreshed the workbook coverage, API manual, data dictionary, and signed
  supply-chain lock.

## [5.27.3] - 2026-11-19

### Performance before HA

- Removed the blocking Peer Manager lookup from `/api/auth/me`, which nginx uses as the auth request target for every page and asset.
- Added a short TTL cache for Peer Manager peer lists and invalidated it on peer changes.
- Moved blocking admin session-health, user, stats, VPN, and activity routes to FastAPI's threadpool.
- Batched activity-log actor lookups and joined VPN config users instead of one query per row.
- Grouped analytics per-lab learning and first-attempt data in one pass instead of scanning all pairs per lab.
- Loaded only the lab columns needed by progress and catalogue views.
- Added indexes for achievements, lab sessions, assignments, assignment labs, and lab-completion trends.
- Served content-hashed Vite assets as immutable year-long cache entries and added SVG to gzip types.
- Deferred NICE coverage and curriculum loads to the Exercises tab and stopped repeating the modules request.
- Reduced the instructor dashboard poll from 15 s to 30 s and removed a duplicate profile VPN refresh.

## [5.27.2] - 2026-11-19

### Export downloads

- Fixed export/download buttons that revoked the object URL before the browser could start the download.
- Moved the instructor operations-report reason into an inline field instead of a blocking browser prompt.
- Applied the shared download helper to reports, admin activity/users/exercises/reports/backups, student and class reports, career profile, privacy data, portfolio, identity providers, VPN config, SBOM, and course reports.
- Added frontend tests for the shared download helper.

## [5.28.6] - 2026-11-20

### Admin signifiers and dialog behaviour

- New `v-modal-dialog` directive: every admin overlay now declares `role="dialog"` and `aria-modal`, wires `aria-labelledby` to its title, closes on Escape, moves focus inside on open, traps Tab, and restores focus on close.
- `ConfirmDialog` closes on Escape.
- Invite codes are a real copy button (`CopyCode.vue`) with a label, copy icon, and inline "Copied" confirmation instead of clickable text with no keyboard path.
- The exercise-tester "Report" badge is a `<button>` with an aria-label, so it is reachable and no longer reads as part of the row checkbox.
- Scan-warning headers no longer dismiss the whole list from a bare click; the `×` is a labelled button.
- The `scan-warnings` and tester badge styles were adjusted for native button rendering.

## [5.28.5] - 2026-11-20

### Network lab harness and topology fixes

- `scripts/lab_harness.py` expands `x-ocr-topology` before starting a lab: it allocates a free `/29` per link inside `10.128.0.0/9` and injects the node role, links, routes, flag, and training credentials. The five container-topology labs are now validated by the offline harness instead of failing right after start.
- `{target.NAME}` also resolves from `topology.nodes[].id` through its `ip_offset`, so a diagram id such as `webserver` reaches the `web-server` service.
- `topology-node`: new `fwctl` helper. The node keeps `no-new-privileges`; the root entrypoint serves a Unix socket that accepts only `show` and `apply <file under /srv/fw>`, so the firewall lab works without sudo or setuid.
- `network-12-1`: the traffic check now waits for an `ALLOW`/`DROPPED` line instead of cutting the monitor banner with `head`.
- `network-12-4`: applies its policy through `fwctl`; hints and workbook chapter updated.
- `network-12-6`: declares only the appliance SSH as an expected service.
- Generated the missing `ot-3-1-ics-pcap-forensics` manifest; all 211 labs now have a tester contract.

## [5.28.4] - 2026-11-20

### ICS lab test fix

- The TRITON workstation test now excludes the controller's listening port (`udp.srcport != 1502`), so it returns the engineering workstation (`192.168.1.88`) instead of the controller.
- Added the same guidance to the hints and case brief.

## [5.28.3] - 2026-11-20

### Startup and code hygiene

- `validate_settings()` no longer runs at import time; the application lifespan calls it at startup, so tooling can import `app.config` without a full deployment environment while the server still fails fast.
- Removed the UTF-8 BOM from `database.py` and switched to `sqlalchemy.orm.declarative_base`.
- Trimmed the trailing blank block in `labs.py`.

## [5.28.2] - 2026-11-20

### Admin request validation

- Impersonation launch, compose update, and stress-test start/cancel now take Pydantic models with length and range bounds instead of raw dictionaries.
- Removed the manual `request.json()` parsing from the impersonation launch path.

## [5.28.1] - 2026-11-20

### Admin follow-ups

- `GET /admin/users` no longer calls Peer Manager or writes `vpn_registered`; the dedicated `/vpn/sync` endpoint and scheduler own that refresh.
- Retention counts use one database round trip, and due courses are filtered in SQL instead of loading every course with a retention date.
- Restore and bulk-toggle endpoints take Pydantic request models with field limits.
- Remaining optional query parameters use `str | None`.
- Remaining admin error responses return generic messages and log the detail server-side.

## [5.28.0] - 2026-11-20

### New lab: ICS/OT PCAP forensics

- Added `ot-3-1-ics-pcap-forensics`, a fully offline lab built on 17 guided challenges from the MIT-licensed ICS-PCAP-Challenges range.
- Bundles 22 MB of redistributable captures: TRITON/TRISIS (BSD-3-Clause), Industroyer2 (CC BY 4.0), GOOSE false-data injection (CC BY 4.0), and the CISA ICSNPP test traces (BSD-3-Clause).
- Ships an SSH analyst workstation with tshark and the evidence, plus a guide service serving the trimmed challenge range. Includes the datasets' license notices and attribution.

### Admin reliability and safety

- Terminating one session or all sessions, stale-session reset, VPN resync, lab approve/reject/toggle, VPN peer removal, image/prune, backup/restore, and Docker maintenance endpoints now run in the threadpool instead of blocking the event loop during synchronous Docker work.
- Single-session termination now writes an audit record.
- Recent reauthentication is required for account erasure, database restore, terminate-all, and VPN peer removal.
- A database restore creates a safety snapshot first and refuses to overwrite if that snapshot fails.
- Lab compose is validated when an instructor creates or updates it, not only at spawn time.
- `impersonate/launch` is rate limited to 10/minute.

## [5.27.8] - 2026-11-20

### Lab readiness

- Corrected the High School DevFest lab workbook path to the built chapter (`01_DevFest_Community_Portal`), removing the last dead workbook link found by `verify-lab-builds.sh`.
- Rebuilt the supply-chain lock and software-integrity manifest for the corrected lab content.

## [5.27.7] - 2026-11-20

### Request-path performance

- Mutating authenticated requests now decode the JWT once: the impersonation guard validates the signature and passes the payload to `get_current_user`, which performs the single revocation check with the request session.
- `get_current_user` publishes the authenticated user on `request.state` for downstream middleware.
- Wiki frame-ancestor and module-gate settings are cached briefly, removing a database session from every `/api/auth/me` and gated module request.
- Export labeling and security-event coverage reuse the authenticated user instead of resolving and decoding the token again.
- Lab spawn and standalone RangeBox launch are rate limited to 10/minute per user (IP fallback).

## [5.27.6] - 2026-11-20

### Security hardening

- Login now performs a dummy Argon2 verification for unknown and SSO-only usernames, removing the response-time oracle.
- Failed logins are throttled per (username, client IP) with exponential backoff. They no longer auto-lock the account globally, which removes the cross-IP lockout DoS; administrator locks still apply.
- Production startup fails closed when the integrity ledger, tenant RLS, database invariants, RBAC catalog, or security-event RLS cannot be installed.
- The SSO demo profile no longer ships a default LDAP administrator password and requires an explicit `LDAP_TLS` choice.
- Docker socket proxy `EXEC` is opt-in through `OCR_DOCKER_PROXY_EXEC`; production sets it to `1` because the exercise tester needs it.

## [5.27.5] - 2026-11-20

### WireGuard HA addressing

- Added `WG_SERVER_ADDRESS` (default `10.0.0.1`) so companion HA hosts can use distinct `wg0` addresses.
- Replaced the hardcoded server tunnel address in client configuration generation and the server-side GRETAP mirror.
- Added the server's `wg0` host route to the client `AllowedIPs` so the gretap mirror has a path through the tunnel.

## [5.27.4] - 2026-11-20

### Homepage knowledge check

- Added a **Take a quiz** action to the student dashboard hero. It deep-links into the optional knowledge check for the nearest visible, unfinished exercise that actually has a question bank, and is hidden when no quiz remains.
- Added `next_quiz` to the student dashboard payload so the UI does not have to guess which labs ship a `quiz.yaml`.

### Training lab content and operations

- Added synthetic scenario packs to the single-student and cohort Moodle courses.
- Added `docs/TRAINING-INSTRUCTOR-GUIDE.md` and `scripts/ecosystem_seed/reset_training_lab.sh`.
- Recorded the Fleet 4.95.0 enroll-secret panic as a known dev-only limitation.

## [Unreleased]

## [5.27.1] - 2026-11-19

### NICE review and training tooling

- Added a **Mark reviewed** action to the NICE coverage card in Admin > Exercises and `POST /api/nice/labs/{lab_id}/review` for provisional mappings that do not need edits.
- Added an **Open** action so a reviewer can inspect a lab and its mapping picker before approving.
- Added a dev-only Caddy TLS front for Moodle and verified an LTI 1.3 launch into the development range.
- Added Fleet administrator setup, Ralph migration and administrator setup, and a second OCR course for cross-course scope checks.
- Added Authentik training groups/users, Moodle capstone briefs, and privacy/auditor accounts.
- Recorded the verified role and cross-course access matrix in `docs/TRAINING-CAPSTONES.md`.
- Documented the OpenIAM fetch and its Swarm-based setup, which is intentionally not auto-started.
- Added `scripts/run-openiam-test-stack.sh` and `docs/OPENIAM-TEST-STACK.md` for a dedicated identity lab host.
- Added Moodle TLS validation to the training validator and recorded the results in `docs/TRAINING-VALIDATION.md`.

This is a patch release for the production NICE review action; the training-stack changes are development-only and are not deployed to production.

## [5.27.0] - 2026-11-19

### NICE lab coverage and manual navigation

- Added provisional NICE v2.2.0 mappings for all 210 repository labs, generated from competency and category policy.
- Added `lab_nice_metadata` for review status, provenance, confidence, and reviewer.
- Added `GET /api/nice/coverage`, the provisional review queue, and `POST /api/nice/labs/seed`.
- Added NICE coverage status and a seed action to Admin > Exercises.
- Rebuilt the user manual with the full manual stylesheet and fixed the navigation rail/TOC scrolling and accent border at the page bottom.
- Added NAPALM, Open vSwitch, Mininet, Cilium/Hubble, Calico, Istio, self-hosted GitLab CI, SonarQube, OWASP Dependency-Check, and ScanCode Toolkit to the planned network and platform tracks.
- Added Nikto web-server scanning, OWASP ZAP web scanning, Lynis host hardening, and Fail2Ban host defense to the vulnerability-management and SOC tracks.

### Ecosystem tooling and dev-only training stack

- Added `docs/ECOSYSTEM-TOOLING-MAP.md` and the `ecosystem-tooling-and-reporting` skill, copied into OpenGRC, OpenDetectionEngine, and OpenEMR.
- Added project integration notes for OpenGRC, OpenDetectionEngine/OpenDLP, and OpenEMR/DRButler.
- Added `deploy/ecosystem-test/`, a dev-only compose stack with Moodle, Authentik, NetBox, Ralph, and Fleet, all bound to loopback by default.
- Added fake-data seeders for Moodle courses, cohorts, staff, and learners and for a synthetic NetBox inventory.
- Added a validator that refuses to run when `OCR_ENV` is production or prod, and documented the training ecosystem in `docs/TRAINING-ECOSYSTEM.md`.
- The training stack never receives production credentials, identity providers, or records.

## [5.26.0] - 2026-11-19

### Course staff and governance dashboards

- Added `course_staff` for mentor, teaching-assistant, and co-instructor course assignments, with tenant RLS and erasure cleanup.
- Report scope now reads course-staff assignments instead of requiring course ownership for mentor and teaching-assistant roles.
- Added privacy-office dashboard endpoints and page: aggregate learners, minors, consent, retention, erasure, report access, data inventory, and classification evidence.
- Added auditor dashboard endpoints and page: report manifests, report access, integrity ledger, security events, retention, erasure, certificates, and review evidence.
- Governance views are role-restricted and audited with `GOVERNANCE_VIEWED`.
- Added a `/governance` route and sidebar entry for privacy officers, auditors, institution administrators, and administrators.
- Added course-staff management to Admin > Courses > Manage.
- Extended the planned network and platform tracks with NAPALM automation, Oxidized configuration backup, Open vSwitch and Mininet virtual networks, Cilium eBPF networking, security, and Hubble observability, Calico network policy and eBPF comparison, Istio service mesh, self-hosted GitLab CI, and a SonarQube quality gate.

## [5.25.0] - 2026-11-19

### Report access policy and privacy labels

- Added a single report-to-role access policy for course reports.
- Added `403` enforcement, catalog filtering, and `REPORT_VIEWED`, `REPORT_EXPORTED`, and `REPORT_ACCESS_DENIED` audit events.
- Added small-cell suppression for aggregate exercise rows and a `suppressed` column in CSV exports.
- Added report purpose, owner, audience, retention, and expiry headers; manifests now carry `expires_at`.
- Added CSV purpose/owner/audience/retention comment rows.
- Added institution-defined classification framework references for export labels; labels are no longer treated as a universal standard.
- Added privacy, auditor, mentor, teaching-assistant, and institution-administrator roles to the assignable role list.

## [5.24.2] - 2026-11-19

### Readiness migration fix for the production jump

- Made `0044_readiness_case_owner` idempotent when startup `create_all` has already added `owner_id`, `priority`, the owner foreign key, or the index.
- Validated the full `0043 -> 0044 -> 0045` upgrade on a database with the current ORM schema already created.
- This allows production to move directly from `0043` to the current head without a duplicate-column or duplicate-constraint rollback.

## [5.24.1] - 2026-11-19

### Schema migration fix

- Made `0045_nice_framework` idempotent when `create_all` has already created the NICE tables during startup.
- The migration now inspects each table before creating it, so existing installs stamp the correct Alembic head without a `DuplicateTable` rollback.
- Added a migration regression check against a database that already contains the NICE tables at `0044`.

## [5.24.0] - 2026-11-19

### NICE Framework ingestion and curriculum scaffold

- Added NICE Framework v2.2.0 ingestion from the official NIST JSON, with a bundled compressed snapshot for first boot and offline installs.
- Added `nice_components`, `nice_links`, `nice_framework_meta`, and `lab_nice_components`, plus the `0045_nice_framework` migration.
- Added instructor component search, lab mapping, admin refresh, and a NICE status endpoint.
- Added a NICE mapping picker to the exercise create and edit forms. Selections are validated against the installed component catalogue.
- Add the IAM, Vulnerability Management, Security Operations, Platform Engineering, and Network Engineering tracks to the curriculum manifest with NICE v2.2.0 role alignment and a content lifecycle.
- Added OpenIAM to the IAM governance sequence, the network engineering identity integration chapter, and the 2027 track build order.
- Recorded ADR 0006: Authentik is the operational SSO platform, Keycloak is the advanced enterprise-IAM lab, and OpenIAM is the identity-governance lab.

## [5.23.0] - 2026-11-19

### Live community events calendar

- The events page now fetches the public SWOCTS Hub calendar instead of relying only on a saved event list.
- The backend parses the public iCalendar feed, expands recurrences, handles all-day events and folded lines, strips HTML from descriptions, and caches the result for 15 minutes.
- The endpoint falls back to the last cached copy when the feed is unavailable, and the frontend keeps saved events as a final fallback.
- Added `GET /api/public/community-events` and `OCR_SWOCTS_CALENDAR_ID`.
- Hardened the feed reader with a 5 MB body cap, a recurrence-frequency allowlist, per-event and total event caps, and a short failure backoff. A malformed event is skipped instead of dropping the feed.
- Production configuration now rejects a `BACKUP_DATABASE_URL` that reuses the RLS-constrained runtime role.
- Added parser, endpoint, component, and merge tests, plus the community calendar operations note.

## [5.22.0] - 2026-11-19

### Readiness calibration outcomes

- Added an instructor review of the provisional band: confirmed, partly confirmed, not confirmed, or needs more context.
- Added calibration counts, review coverage, agreement by reviewed band, and a recent-review table.
- Added a band-changed signal when the learner's band no longer matches the band that was reviewed.
- Added `band` to the readiness note request and stored the reviewed band with the note.
- Regenerated the API manual.

## [5.21.0] - 2026-11-19

### Readiness case ownership and follow-ups

- Added an open/closed case per learner with an owner, priority, and next follow-up date.
- Added a Follow-ups view with overdue, due-soon, unassigned, and closed counts.
- Added case summaries to the calibration view.
- Preserved support records when an instructor account is erased; author and owner links are nulled instead.
- Fixed admin database snapshots to dump with a `BYPASSRLS` identity instead of the RLS-constrained runtime role. `BACKUP_DATABASE_URL` is preferred, then `MIGRATOR_DATABASE_URL`, then `DATABASE_URL`.
- Added migration `0044_readiness_case_owner`.

## [5.20.0] - 2026-11-19

### Readiness calibration workflow

- Added context flags, support actions, flag acknowledgements, snoozes, and dismissals to the instructor readiness queue.
- Added calibration evidence: band distribution, flags, actions, outcomes, flag states, and lab reviews.
- Added lab-health review records with finding, action, and outcome.
- Added append-only readiness tables with tenant RLS and learner erasure cleanup.
- Updated the data dictionary and tenant-isolation inventory.

## [5.19.0] - 2026-11-19

### Instructor readiness dashboard

- Added a pilot **Readiness and lab health** panel to the instructor dashboard.
- The support queue shows a provisional CWRS, band, confidence, component risk,
  flags, and on-demand capability detail for one course.
- Lab health separates degraded, warning, no-data, and healthy labs and hides
  healthy labs by default.
- Under-18 learners remain excluded from the course cohort view, and every score
  is labelled provisional pending calibration.

## [5.18.0] - 2026-11-19

### Account email and notifications

- Added **Admin → Settings → Notifications** with platform-wide controls for
  registration, approval, rejection, and username-reminder email.
- Added **Admin → Settings → Email templates** for editable subjects and bodies,
  placeholder help, and built-in defaults.
- Pending accounts now receive an email when an administrator approves or
  rejects them.
- Registration and reminder email respect the notification preferences.
- Email rendering uses escaped text and lazy PDF assets where relevant.

### Career direction and learner evidence

- Added an eight-question **Career direction check** to the learner profile,
  scored across discovery, construction, operations, and people clusters.
- Expanded the certification question bank from **81 to 128** questions across
  nine pathways.
- Added collection achievements for AI, identity, OT, malware, Metasploit,
  Grade 9 foundations, all digital-forensics labs, and OSINT.
- Hardened collection awards so a missing lab cannot silently shorten a badge.

### Simulated cloud range

- Added a local **simulated cloud** reference stack: Keycloak, OpenLDAP, MinIO,
  Vault, OpenSearch, Dashboards, n8n, optional LocalStack, Azurite, and Wazuh.
- Added OpenTofu examples validated with OpenTofu 1.9.0, Kubernetes RBAC and
  network-policy labs, Sigma rules, a posture scanner, and four incident labs.
- Added the workforce readiness, job matching, transcript, CWRS, LDV,
  competency matrix, lab health, multi-student, AI governance, supply-chain,
  and progressive-disclosure design notes.

### Manuals, workbooks, and RangeBox

- Redesigned the user-manual navigation rail and footer.
- Replaced the manual/workbook PDF button with an export menu: PDF, print,
  Word, HTML, and copy link.
- Lazy-loaded the PDF library so it downloads only when PDF export is chosen.
- Fixed the workspace divider so it stops at the workbook boundary.
- Hardened native fullscreen with a focus-mode fallback and explicit
  `Permissions-Policy`.
- Fixed the deployment monitor's semantic-version check.
- Fixed a multi-worker startup race when seeding new platform settings.

### Validation

- Backend targeted suites pass; frontend lint and production build pass.
- MkDocs manual and workbook builds pass.
- OpenTofu `fmt`, `init`, and `validate` pass.
- Simulated-cloud Compose configuration validates.
- Manual export menu tested in Edge at desktop and mobile widths with no
  console errors or mobile overflow.

## [5.17.7] - 2026-11-17

### Course management

- Fixed the admin course-management dead end: **Manage** now opens the
  Instructor Panel course workspace directly at the selected course, where the
  working **Enroll Students** flow lives. The learner-facing course page remains
  a separate view.
- The admin panel now says **Manage students** and **View course page** instead
  of sending administrators to a page with no enrollment controls.
- Verified from the admin path: the selected course opens, the enrollable-user
  list loads, and enrollment returns **1 student enrolled**.

### Exercise review status

- Added a **Review** column to Admin > Exercises. It shows the competency
  contract state (`Reviewed`, `Pathway`, `Baseline`, `Pending`, `Unmapped`),
  with content version, review date, and flag presence in the tooltip.
- This is a review-record indicator, not a live harness result. A separate
  **Run exercise tester** action remains available per exercise.

### Validation

- 8/8 Playwright checks for admin course navigation and enrollment.
- 25 review badges render on the exercises page.
- Backend curriculum admin tests pass; frontend lint and production build pass.

## [5.17.6] - 2026-11-17

### Production settings UX

- **Run ceiling test** now checks the production ticket gate before the
  confirmation prompt. With no ticket, it shows an inline hint beside the
  RangeBox capacity card, highlights Production change control, scrolls it into
  view, and focuses the missing ticket or reason field. A valid ticket and
  reason show the normal confirmation.
- The inline hint is visible on load in production, so the requirement is
  discoverable before the operator clicks the test.
- Added a regression test for the full gate, and verified the production
  presentation on dev with **16/16** Playwright checks at desktop and mobile
  widths.

### Workbook and achievements

- Added the required **Analysis Questions** section to all 19 level-11 pathway
  workbook pages.
- Added two range-wide completion badges: **Directory Pathfinder**
  (`ad_pathfinder`, all nine Active Directory exercises) and **AppSec Architect**
  (`appsec_architect`, all ten Modern Application Security exercises). Both are
  in the achievement catalogue, the manual, and a regression test.
- Clarified the lab counts: **210** registered labs, of which **170** are in the
  public catalogue and **40** are course-scoped. The student dashboard correctly
  shows 170.

### Manual and evidence

- Refreshed **52** manual screenshots from dev with Privacy Mode explicitly on
  for admin and instructor captures. Replaced the stale locked-accounts image
  and populated the pending and locked states with synthetic demo accounts.
- Recorded the demo-account workflow and the `UI_MANUAL_PRIVACY=1` requirement
  in `docs/MANUAL-SCREENSHOTS.md`.

### Validation

- Backend: **909 passed** on a clean PostgreSQL database.
- Frontend: lint, tests, and production build pass.
- Links, document assets, workbook coverage, lab metadata, quiz banks, and the
  security-delta review pass.
- The previous full-suite errors were test-database contamination (duplicate
  track slugs); a clean schema run passes.

## [5.17.5] - 2026-11-16

### Documentation and repository cleanup

- Added the documentation skill, a documentation index, category hubs
  (`architecture`, `operations`, `curriculum`, `security`, `integrations`,
  `compliance`), an archive index, `CODEOWNERS`, `SUPPORT.md`, and `PRIVACY.md`.
- Archived completed cutover, upgrade, Release 4, and Wave records; merged the
  repository-move record into the cutover record; removed one unreferenced
  screenshot.
- Reconciled current-state values: **210 labs, 182 workbook-mapped, 13 tracks,
  Python 3.13, 25 tenant-RLS tables, 5.17.5**. Labelled the AI agentic, API,
  Juice Shop, and OWASP plan documents as plan or partly implemented.
- Added curriculum drift, MkDocs governance, repository hygiene, and
  open-source readiness reports.
- Audited the manual screenshots: they use synthetic data and contain no real
  learner data. A refresh to the current build is pending demo credentials.

### Security and input validation

- Bounded and log-sanitised the login form: oversized input and control
  characters are rejected with the same generic error as a wrong password.
- Added `maxlength` and correct `autocomplete` to every password prompt.
- Added regression tests for login, re-authentication, change-password, account
  deletion, admin password reset, MFA disable, and the production cutover gate.
  Each accepts the correct password and rejects a wrong one, plus oversized,
  control-character, and injection-shaped input.

### Validation

- Backend: **908 passed** on a clean PostgreSQL database.
- Frontend: **6 passed**; build passed; lint 0 errors.
- Labs: **210** with **0 failed checks**; manifests, contracts, outcomes, links,
  assets, API manual, metadata, licences, and strict MkDocs build pass.

## [5.17.4] - 2026-11-16

### Fixed

- **Lab discovery skipped new levels.** The CLI discovery script now creates
  missing tracks and levels before scanning (the admin route already did). An
  existing install therefore registers the level-11 Active Directory and modern
  application-security labs instead of silently skipping them.
- The seed curriculum defines level 11 for the `windows` and `web` tracks, so a
  fresh install has the structure before discovery runs.
- Discovery reads `lab.yaml` and compose files as UTF-8, so a non-UTF-8 host
  locale no longer skips the pre-existing `network-1-2-http-traffic-analysis`
  lab.
- Added a regression test that asserts the seeded curriculum covers both
  level-11 pathways.

## [5.17.3] - 2026-11-16

### Tenant isolation

- Migration `0041_tenant_rls_legacy` extends forced PostgreSQL row-level
  security to 16 legacy learner-owned tables: `flag_attempts`,
  `review_requests`, `survey_responses`, `user_accommodations`,
  `accommodation_events`, `exercise_quiz_attempts`, `exercise_quiz_feedback`,
  `exercise_reactions`, `exercise_pulse_surveys`, `course_feedback`,
  `course_completion_resets`, `course_cohort_members`, `quiz_attempts`,
  `open_badge_credentials`, `lti_scores`, and `activity_events`.
- Enforced tenant tables: **25**. Each has a derived `institution_id`, a trigger,
  forced RLS, and select/insert/update/delete policies. The tenant migration now
  skips tables that do not exist yet at an earlier revision, so a fresh database
  upgrades cleanly.
- New regression tests assert the column, forced RLS, and four policies on every
  table and probe two newly migrated tables across two institutions.
- Authentication, secret, consent, platform-operation, and shared-definition
  tables are classified in `docs/TENANT-ISOLATION-STATUS.md` rather than
  force-scoped.

### Curriculum

- Implemented all 19 pathway labs: 9 Active Directory (`windows-11-*`) and 10
  modern application-security (`web-11-*`) exercises.
- Every new lab has a `lab.yaml`, a runnable container definition, a competency
  contract, and a tester manifest. AD labs use the proven OpenLDAP base; the
  appsec labs use a small Flask service with one mode per exercise.
- Lab counts are **210 definitions, 210 tester manifests, 210 contracts, 182
  workbook-mapped**; `docs/COUNTS.md` is the source of truth.

## [5.17.2] - 2026-11-16

### Fixed

- **Re-authentication dialog request path.** The dialog posted to
  `/api/auth/reauth` through an HTTP client whose base URL is already `/api`,
  so the request went to `/api/api/auth/reauth` and returned `404 Not Found`.
  This blocked every re-authentication-gated action, including the production
  cutover, account export, role changes, and consent revocation. The dialog now
  posts to `/auth/reauth`. The regression test asserts the corrected path.

### Operations

- Production completed the one-way cutover on 16 November 2026 under ticket
  `123456`, approved by Robert Chaykoski. Deployment mode and data collection
  mode are `production`, settings changes require a ticket, and the cutover
  evidence hash is recorded in the deployment statement.

## [5.17.1] - 2026-11-16

### Release hardening

- **Fail-closed authorization:** production Compose sets `OCR_AUTHZ_STRICT=1`;
  the backend refuses production startup when a protected route lacks an
  authorization dependency.
- **Explicit production configuration:** `ENVIRONMENT` is validated, and an
  `OCR_DEPLOYMENT_MODE=production` intent with a non-production environment
  fails startup.
- **WireGuard key requirement:** production and VPN-enabled deployments now
  refuse startup without `WG_ENCRYPTION_KEY`. The old warning was not enough.
- **Opt-in profiling:** Cyber DNA, Cyber GPS, and the professional portfolio
  now default to **not granted**. A learner must opt in before those surfaces
  process or display derived data.
- **Lab outcomes contract:** `platform/backend/app/data/lab-outcomes.yaml`
  gives every lab skills earned, competencies proven, knowledge domains,
  evidence artifacts, and a confidence score.
- **API manual:** the user manual now includes a generated, complete API
  reference from the OpenAPI schema.
- **Code of Conduct:** added a formal policy with lab-safety, privacy,
  minor-safety, reporting, enforcement, and appeal procedures.
- **Release and governance documents:** added the production deployment
  statement, validation report, backup/restore test, topology and sizing guide,
  contributor/branch inventory, tenant-isolation status, and independent-testing
  status. Lab counts are now reconciled in `docs/COUNTS.md`.
- **New pathways:** added the Active Directory attack/remediation pathway and
  the modern application-security pathway (API, GraphQL, JWT, OAuth, DevSecOps,
  containers, Kubernetes, supply chain).

## [5.17.0] - 2026-11-16

### Release 5.17 highlights

- **Admin release status** — admin-only comparison with the latest GitHub
  release or semantic tag, a dashboard update banner, and a System health panel
  with installed/latest versions, release notes, backup/build/migrate/verify
  commands, runbook links, and the rollback note. The check is cached, works
  offline with a stale result, and never deploys anything by itself.
- **RBAC/PBAC editing** — the Security → Roles tab now edits explicit
  Allow/Deny grants with a required reason, shows Adds/Denies/Unchanged before
  saving, and records the reason in the security event. The Moves, Adds,
  Changes panel supports adding an expiring extra role, moving a primary role,
  and removing an extra role. Sensitive private permissions remain
  owner/share/break-glass only.
- **MITRE ATT&CK Navigator** — added to the Tools sidebar and active-lab panel
  as an allow-listed external tool with an exact-origin CSP frame allowance,
  sandbox, timeout, and new-tab fallback.
- **DFIR pathway** — expanded to twelve report-based modules, each requiring a
  short analyst finding plus an analyst report or reviewed evidence artifact;
  added the synthetic evidence pack, report template, and validator coverage.
- **External datasets and lab resources** — added a reviewed registry for
  Security Datasets (MIT), UNB CIC (citation required), Splunk attack_data
  (Apache-2.0), theZoo and vx-underground (reference-only live malware),
  PCAP-ATTACK (no licence), the Aman Hardikar forensics map, OpenCRE, OWASP
  API Security Top 10 2023, OWASP Top 10 2025, OWASP Agentic Skills Top 10,
  and the OWASP cheat sheets. A fetch script verifies pinned hashes; reference
  sources are never vendored.
- **OWASP validation and labs** — added one baseline for API, web, and agentic
  security with category status, platform controls, regression evidence, and
  ten-lab plans for each. Added the pinned OWASP Juice Shop lab application and
  API/web lab blueprints.
- **Detection and malware governance** — added the defensive detection pathway
  and the malware-lab inventory/isolation contract with no live samples in the
  public repository.

### Authentication lifecycle
- Added server-side `auth_sessions` and `refresh_tokens` (migration `0037`).
  Access JWTs carry a session id; sessions bind the tenant captured at login.
- Added opaque, hashed, rotating refresh tokens with reuse detection: replaying
  a rotated token revokes the whole family and session.
- Added `POST /api/auth/refresh`, `POST /api/auth/reauth`, real session listing,
  per-session revocation, and session-bound tenant checks.
- Added TOTP recovery-code lifecycle: 10 hashed codes by default, single-use,
  TTL-limited, regenerated as a set, cleared on disable/reset, with remaining
  count and expiry metadata.
- Added MFA brute-force throttling with a separate counter and lock from
  password lockout (`mfa_max_failed_attempts`, `mfa_lockout_minutes`).
- Added authorised MFA reset for lost authenticators: `mfa.reset` permission,
  operator password + MFA, written reason, tenant visibility, session/token
  revocation, and a `critical` event.
- Added forced reauthentication for privacy, role, MFA, break-glass,
  service-identity, session-revocation, and export operations. The SPA opens a
  reauthentication dialog on `X-Reauth-Required`.
- Added explicit Argon2id parameters (64 MiB, 3 iterations, 4 lanes, 32-byte
  hash, 16-byte salt) and a recurring rehash policy (`password_rehash_days`,
  `users.password_rehashed_at`, `auth.password_rehashed`).
- Updated the SPA to store refresh tokens, retry one request after a refresh,
  and clear refresh state on logout/session failure.
- Added `tests/test_auth_lifecycle.py` and `docs/AUTH-LIFECYCLE.md`.

### Tenant RLS, security operations, and service identities
- Added `institution_id` to `courses`, `course_enrollments`, `lab_sessions`,
  `lab_completions`, `achievements`, `learner_snapshots`,
  `portfolio_share_tokens`, `dna_evidence_records`, and `dna_snapshots`
  (migration `0035`). Triggers derive the tenant from the owner; clients cannot
  choose it.
- Enabled and forced PostgreSQL RLS on those tables. Authenticated requests use
  their tenant, unauthenticated requests see the default institution, and
  background jobs run as the system principal. Public certificate verification
  performs an explicit global lookup for its public fields.
- Added institution-admin scoping for user list/detail/create/update, statistics,
  course list/detail, activity log, course analytics, reports, and course audit
  views. Institution admins cannot promote an account to platform admin or move
  an account between institutions.
- Added the admin **Security** console: event summary and filters, break-glass
  request/approve/revoke/review, service-identity creation/revocation, and role
  catalog.
- Added a five-minute security-operations loop: stale break-glass expiry and
  deduplicated threshold alerts for repeated login failures, denied requests,
  export denials, and break-glass use.
- Added hashed, scoped service credentials with expiry, revocation, no password
  login, and per-request attribution (migration `0036`).
- JSON exports (`/api/auth/export`, identity provider export, career dossier,
  portfolio, and snapshots) now participate in data-label enforcement; routes
  may mark any JSON response with `X-OCR-Export`.
- Added `tests/test_tenant_rls.py`, `tests/test_service_identities.py`, and
  `tests/test_institution_admin.py`, plus JSON export and alert tests.

### Enforceable data labels
- Added institutional label schemes (custom JSON levels), path-based minimum
  classification, role/region ceilings, non-exportable levels, and
  Restricted-export blocking.
- Export authorization now requires `export.data`, the atomic permission for
  the effective label rank, and the institution's role/region ceiling.
- Added `GET /api/admin/data-labels/policy` to preview a decision and show
  warnings. Denied exports are recorded as security events.
- Documented the policy in `docs/DATA-LABELS.md`.

### Authorization Service and RBAC tables
- Replaced role-string checks on new/high-risk surfaces with
  `app.services.authorization.AuthorizationService`: RBAC + tenant + owner/share
  scope + learner consent + optional break-glass.
- Made `app/security/permissions.yaml` the authoritative reviewed catalog with
  sensitivity, scope, read-only, and break-glass metadata. Startup validates it;
  `python -m app.scripts.review_permissions --check` is the release gate.
- Added persisted `rbac_roles`, `rbac_permissions`, `rbac_role_permissions`, and
  expiring `rbac_user_roles` tables (migration `0034`). Seeding preserves an
  administrator's reviewed changes across restarts.
- Added server-loaded `User.institution_id` tenant isolation. `institution_admin`
  is not a system administrator; `admin` is the only cross-tenant role.
- Added owner and tenant helpers that return 404 on a foreign record, plus
  owner/non-owner regression tests for profile, portfolio, report snapshots,
  Cyber DNA snapshots, sessions, and consent.
- Added a startup route audit for protected endpoints without an
  auth/permission dependency, with optional strict fail-fast.
- Split private signals: faculty never receive `career_affinity.view.self`,
  `recommendation.view.self`, or private DNA/GPS/AI permissions. Hidden
  achievements are excluded from course and celebration walls.
- Restricted instructor learner enumeration to learners already in the
  instructor's own courses, in the same tenant.

### Security event store
- Added append-only `security_events` for security, audit, and privacy actions,
  with PostgreSQL RLS: INSERT and tenant-scoped SELECT only; UPDATE and DELETE
  affect zero rows. No delete API. Runtime superuser bypass is warned at startup.
- Added explicit events for sign-in success/failure, MFA failure, password
  change, registration, consent grant/revoke, export allow/deny, RBAC changes,
  break-glass workflow, portfolio share use, and an admin-action mirror.
- Added a sensitive-HTTP fallback, admin query/summary APIs, and redaction of
  secret-like detail keys.
- Documented the store in `docs/SECURITY-EVENTS.md` and retention in
  `docs/RETENTION-POLICIES.md`.

### Break-glass access
- Added time-bound emergency grants for private DNA/GPS/AI, Restricted export,
  and audit access. Off by default; MFA-gated; reasoned; scoped to one learner
  or course; optionally second-operator approved; no extension; post-use review.
- Every use is a `critical` security event. Consent revocation cannot be
  overridden by break-glass.

### Portfolio share links
- Added hashed bearer tokens with a 30-day default lifetime, revocation,
  single-use/max-use limits, live consent gating, and audit events. The raw
  token is returned once and never stored.

### PIA/TRA evidence
- Added `docs/PIA-TRA-FINDINGS.md` with Completed/Partial/Planned status and
  code/test evidence for every PIA and TRA finding.

### Lab metadata contract
- Added `platform/backend/lab_metadata.schema.json` (draft 2020-12) and
  `scripts/validate_lab_metadata.py`. Unknown keys, missing required fields, and
  invalid enum values now fail CI. All 191 labs validate; the loader's legacy
  `name`/`duration_minutes`/`objectives` fallbacks were removed.

### Cyber DNA v3 — Phase 1
- Added the Cyber DNA bounded context (`app/cyber_dna`) with its own
  `dna_evidence_records` and `dna_snapshots` tables (migration `0032`). It does
  not read exercise tables and has no foreign keys into them; the exercise
  platform emits a versioned `ActivityCompleted` event.
- Evidence is append-only and idempotent per event and competency. Competency
  scores, a five-signal behavior profile, and a voluntary interest vector are
  derived from it.
- Career affinity is **gated** until a learner has 30+ labs, 3+ domains, and
  100+ competency observations. It is descriptive, never a probability.
- Added owner-only `/api/dna/v3/...` endpoints behind
  `cyber_dna_v3_enabled=false`, plus behavior/interest/affinity snapshots.
- Added `scripts/backfill-evidence.py`, an exercise-side adapter for existing
  completions, and explicit DNA erasure in the account-deletion path.
- The design is in `docs/CYBER-DNA-V3.md`.

### Consent revocation and authorization
- Added the `app/consent` bounded context: versioned consent state, immutable
  revocation events, a durable PostgreSQL purge/verify queue, proof-only audits,
  and a file-backed suppression ledger (migration `0033_consent_revocation`).
- Revocation blocks the feature immediately, deletes derived intelligence in one
  transaction, verifies at 0h/24h/7d, and preserves completions, transcripts,
  certificates, achievements, and course progress. `enforce_suppressions()`
  blocks replay and re-applies the ledger after a backup restore.
- Added central consent middleware (`app/consent/middleware.py`) that maps
  derived-data API paths to a consent domain and rejects revoked/purging
  requests before the service runs. DNA ingestion also checks consent and the
  suppression ledger.
- Added the learner UI at **Profile → Security & privacy → AI and career data**
  with per-feature cards, removal progress, audit IDs, retained educational
  records, and consent history.
- Added `app/security/` with an atomic permission catalog, seeded role grants,
  and deny-by-default self/course/shared/read-only policy checks. Auditors are
  read-only, privacy officers can execute revocation work, and administrators do
  not receive private AI/DNA/GPS data by default.
- Added `docs/CONSENT-REVOCATION.md`, `docs/RBAC-PBAC.md`, and expanded the
  privacy notice, security policy, architecture, and user/admin manuals.

### Password breach checks
- Added opt-in checking against the Have I Been Pwned Pwned Passwords range API.
  Only the first five characters of a locally computed SHA-1 digest leave the
  server; the full password and full hash are never sent.
- Wired the check into registration, password change, admin user creation,
  admin password reset, and first-run setup. The setting is off by default;
  network failure fails open. Added service and endpoint tests.
- Documented the control in the security policy, privacy notice, architecture,
  admin settings manual, and student password guide.

### Exercise reuse
- Added exercise ZIP export and admin import. Exports include the lab source,
  compose file, containers, manifest, and README; flags are replaced with a
  placeholder by default. Imports run the existing ZIP validator, preserve the
  metadata header, generate a new flag unless supplied, and create a draft.
- Added row-level export to Admin and Instructor exercise lists and an **Import
  Exercise** modal to the Admin Exercises header.

### Admin and workspace fixes
- Restored **Scan for Exercises** for administrators when `OCR_DEV_TOOLS=0`.
- Fixed **Disk Management** by enabling read-only `SYSTEM` accounting on the
  Docker socket proxy; `BUILD` remains off. The live dev check now returns
  image, container, volume, and build-cache usage.
- Added drag-to-resize dividers to the wide-screen RangeBox workspace, with a
  persisted per-browser split and **Reset layout**.

### Test and documentation updates
- Added consent/revocation, middleware, policy, exercise-transfer, and Docker
  disk-usage tests. The backend suite passes 703 tests; `ruff check app tests` is
  clean. Refreshed the signed supply-chain lock after the proxy change.
- Added `profile-consent.png` and `admin-import-exercise.png` to the manual and
  extended the Playwright manual screenshot script to capture the new panels.

## [5.16.0] - 2026-11-15

### Labs
- Added `network-12-6-appliance-segment`: a dual-homed OpenWrt 24.10.5
  appliance on the training network and an internal control segment. The
  protected service stays off the student lab network, the forward chain is
  default-deny, and the learner pivots with an SSH local forward. Includes the
  workbook page and the NET04 framework mapping.

### Reports
- Added the `learner_snapshots` table (migration `0031`). A career-dossier or
  portfolio export stores its payload, schema and formula versions, factor
  weights, and a content hash. Stored reports re-render from the snapshot, so a
  later scoring change cannot rewrite an old report. Snapshots are owner-only
  and deleted with the account.

### Documentation
- Added `docs-publish.yml`: it builds the user manual (or every site for
  inspection), checks the built tree, and publishes a tarball with
  `SHA256SUMS` and a manifest. Workbook and course sites stay unpublished; see
  `docs/MANUAL-PUBLISHING.md`.

## [5.15.0] - 2026-11-15

### Lab access and stop controls
- Beginner labs now launch a Kali RangeBox by default, and the exercise panel
  offers an explicit **Start with desktop** or **Start with VPN** choice. The
  workbooks say RangeBox or VPN instead of assuming a tunnel.
- Stop Exercise and Stop RangeBox use an accessible in-app confirmation dialog
  with a **Stopping...** state. The previous `window.confirm` silently returned
  false in embedded browsers, so no stop request was sent.
- Unknown routes and `/challenges` redirect to the dashboard or login instead of
  rendering a blank page.
- Registration states that an administrator reviews new accounts, and the public
  config exposes whether approval is required.

### Cyber DNA and Career GPS
- Added an interest-based "Discover your Cyber DNA" first-run flow. New
  learners pick what they enjoy (building, investigating, breaking, defending,
  or not sure) and get three starter exercises instead of an empty dashboard.
- Added a Cyber DNA band to the student dashboard: starter-path progress, class
  and strongest branch, growth-velocity signals, 30/60/90-day trend, and the
  next opportunity.
- Added 30/60/90-day windows to the student learning-analytics chart and to the
  instructor Pulse chart, with a privacy note that instructor charts aggregate
  activity and never rank learners.
- Added growth velocity: completions, hint discipline, challenge stretch, and
  consistency compared with the prior 30 days, exposed with confidence labels
  and minimum-evidence gates. Percentages require 3 completions; career roles
  require 8. The data is personal and never ranked.
- Surfaced Cyber DNA and Career GPS in the sidebar and on the sign-in preview.
- Documented the four-layer model and the anti-gaming/privacy rules in
  `docs/CYBER-GPS-SCHEMA.md`.

### User manual
- Regenerated every manual screenshot from the current Release 5 interface:
  student dashboard and profile tabs, lab workspace, course pages, instructor
  panel and course manager, and the admin console.
- Corrected the navigation, dashboard, lab workspace, course, instructor, and
  admin instructions to match the current UI, including the moved course
  manager, the Live activity and System tabs, and the Exercise plan cohorts.
- Redesigned the manual footer: previous/next page links, a framed meta bar,
  a bottom-right back-to-top control, and figure styling that keeps screenshots
  inside the reading column.
- Removed the synthetic Career Atlas/Momentum preview generator; the manual now
  uses live captures.
- Added `scripts/ui-manual-screenshots.mjs` and
  `docs/MANUAL-SCREENSHOTS.md` so the screenshot set can be regenerated with
  demo credentials instead of ad-hoc scripts.
- Lab discovery and target builds now work after the 027 host hardening:
  deploy pulls grant read access to the bind-mounted lab content, so the
  non-root backend can read `lab.yaml` and `docker-compose.yml`.

### OT/ICS track
- Added `docs/OT-SCANNING-SAFETY.md` and applied the procedure across the OT
  workbooks and hints: written authorization, ARP discovery (`-sn -PR`), a
  delay with `--max-parallelism 1`, specific industrial ports, and identification
  scripts only.
- Added an offline **OT Scan** assistant to the Tools panel and to the running
  exercise header. It validates an IPv4/CIDR target, builds a slow nmap command
  for Modbus, S7, EtherNet/IP, or DNP3, and gates copying on the authorization
  checklist. It never sends a scan.
- Added `ot-1-3-modbus-gateway-bypass`: the PLC sits on an internal control
  network behind a gateway whose write allow-list inspects only function code
  0x06. Students confirm the segmentation, watch a single-register write fail,
  bypass the filter with 0x10, and recover the interlock marker. Includes a
  workbook and defensive guidance on filtering every write opcode.
- Added the missing OT 1.2 and 1.3 workbook entries to the OT wiki navigation
  and refreshed the chapter introduction.
- Added `ot-1-2-modbus-setpoint-tampering`: students write an unauthenticated
  setpoint with function code 0x06, confirm the write, and recover a marker
  exposed after the simulated safety interlock trips. Includes a process
  simulation, a workbook, and write-detection guidance.
- The lab uses the same original pymodbus controller as 1.1. An OpenPLC-based
  target was evaluated and deferred: OpenPLC v4 exposes no Modbus registers
  without an editor-generated program ZIP, and OpenPLC v3 is archived upstream.

### Metasploit Operations track
- Added an original eight-exercise Metasploit track covering workspaces,
  auxiliary discovery, validation, exploitation, Meterpreter, database access,
  pivoting, persistence, and cleanup.
- Added a Metasploitable 2 target image with KVM acceleration when available,
  a TCG software-emulation fallback, read-only snapshots, restricted egress,
  per-exercise flags, and a separate provisioning script. `/dev/kvm` is passed
  into the target only when the host actually exposes it.
- Added student workbooks and a dedicated `msfpt` workbook wiki.
- Documented the independent-content position, OffSec attribution, and Hackers
  For Charity donation information in `docs/METASPLOIT-TRACK.md`.

### Security and performance hardening
- Login now distinguishes "waiting for administrator approval" and "account
  inactive" from a wrong password. The password is verified first, so the
  message does not reveal whether an account exists; wrong passwords keep the
  generic error.
- Added a weekly built-image scan: pinned Syft and Grype build both images,
  publish a CycloneDX SBOM and SARIF, and fail on a fixable critical. The
  dependency audits stay advisory; this gate covers the OS packages in the
  images.
- Audit rows now use uvicorn's proxy-sanitised client address instead of the
  first, client-controlled `X-Forwarded-For` value.
- The supply-chain lock is now verified against a pinned release fingerprint in
  CI and the install/update scripts, using a throwaway GnuPG keyring.
- Authentication dependencies run in the threadpool and reuse the request
  database session for the revocation check instead of opening a second
  connection per request.
- The instructor course list uses grouped count queries rather than three
  queries per course.
- Lab spawns now reject privileged containers, host networking, host bind
  mounts, unexpected devices, and dangerous capabilities at runtime.
- Lab services receive a default process limit and drop host-level
  capabilities; SETUID/SETGID remain available for privilege-escalation labs.
  The process limit is written as `pids_limit`, or as
  `deploy.resources.limits.pids` when the compose file already has a `deploy`
  block, so Compose accepts both shapes.
- Container bases are pinned by digest and refreshed with `apt-get upgrade` or
  `apk upgrade` at build time. The backend runtime no longer carries `curl`,
  `gnupg`, `pip`, `setuptools`, or `wheel`.
- The backend runtime and CI moved from Python 3.11 to 3.13, which clears the
  interpreter findings that only had fixes on newer minor branches. The full
  suite passes against PostgreSQL 17 on 3.13.
- Added `deploy/host-hardening.sh` for the two low-risk Lynis items (umask 027
  and disabled core dumps). It is idempotent and previewable with `--dry-run`;
  applying it needs root on each host.
- Added `docs/SECURITY-SCANNING.md` with the Syft, Grype, and Lynis procedure,
  before/after image counts, and the triage of the findings that remain.
- The image builds make copied source and static tool files readable by the
  runtime user and the nginx worker after the 027 host umask, without making
  code writable.

### Live memory forensics
- Added Forensics level 3 with a KVM/TCG Ubuntu 22.04 target, AVML acquisition,
  and a student workbook for memory analysis with Volatility and strings.
- Documented the Ubuntu cloud image and MIT-licensed AVML sources; neither the
  guest image nor the acquisition binary is committed.
- Fixed the workbook wiki builder to fall back to the repository `.env` and to
  infer the running compose project, so a rebuild targets the volume the
  frontend actually serves.

## [5.14.0] - 2026-11-14

### Course cohorts and certification
- Added opt-in **strict cohort access** for a course. When enabled and at least
  one cohort has an exercise-set requirement, course detail, scoreboard, and
  course-scoped achievements use only the learner's cohort labs.
- Added a **default cohort** and **Sync enrollments** action; new enrollments
  are placed in the default cohort when strict mode is on.
- Course-scoped Clean Sweep and custom `course_completed` achievements now use
  the same visible lab set as the course page.
- Reviewed the certification question banks (81 items, 9 pathways, 69
  references) and recorded the 14 November review.
- Fixed certificate PDFs ignoring the selected design; the PDF now uses the
  same classic/executive/modern/minimal design as the page.
- Reloading a certificate route now replaces the previous recipient, level, and
  certificate ID instead of leaving stale data on screen.

### Security
- Rotated the release signing key. `v5.14.0` is signed with
  `68A817762C831475F00DB54E775050A4C4921814`; the previous key remains
  published for verifying older tags.

### Documentation
- Workbook and documentation links now open synchronously from the click, so
  browsers do not block them as popups after the auth-cookie request.
- The Workbooks page refreshes the wiki auth cookie on mount.

## [5.13.1] - 2026-11-14

### Open Badges
- The public credential viewer now verifies the Ed25519 JWT signature against
  the issuer JWKS and reports verified, invalid, or unavailable.
- Public issuer, achievement, subject, and credential endpoints allow
  browser-based third-party viewers through an explicit CORS policy.
- Added a regression test for the Open Badges 3.0 compatibility fields
  (`vc.id`, `criteria.id`, image, issuer profile, credential schema).

## [5.13.0] - 2026-11-14

### RangeBox
- RemnuxBox now uses KasmVNC (Ubuntu 24.04 package), completing the transport
  migration for Kali, Ubuntu, and REMnux. All three images pin `publicIP` to
  loopback so they start on isolated lab networks without STUN/internet.
- The platform's transport probe keeps noVNC available for older images.

### Lab operations
- Backend composes now set `DOCKER_CONFIG=/tmp/.docker`, so on-demand lab
  builds by the non-root backend no longer fail with
  `mkdir /.docker: permission denied`.
- The sidebar compacts its brand and nav rhythm on shorter laptop windows so
  Teaching and Operations links are not pushed below the fold.

### Export labels
- CSV reports and activity exports prepend visible classification/owner/
  handling comments; Markdown and HTML dossiers/portfolios carry a visible
  label block in addition to the `X-Data-*` response headers.

### Open Badges
- Event awards can be issued as hosted Open Badges from the event certificate
  page; eligibility and event-end rules match the PDF certificate.
- Hosted achievements now expose deterministic PNG badge artwork, referenced
  from the credential's achievement and issuer `image` fields.
- Credentials add `criteria.id`, `credentialSchema`, issuer profile type, and
  a raw JWT endpoint (`/api/badges/credentials/{jti}/jwt`) for third-party
  viewers. The credential viewer displays the badge artwork.

## [5.12.0] - 2026-11-14

### RangeBox
- UbuntuBox now uses KasmVNC (Xvnc plus its built-in web server) instead of
  Xvfb + x11vnc + websockify, matching the Kali RangeBox. It is pinned to the
  Ubuntu 22.04 KasmVNC 1.5.2 package with a SHA-256 check.
- The platform's existing transport probe selects the KasmVNC client for
  UbuntuBox automatically; RemnuxBox remains on noVNC until its image is
  rebuilt.
- Both KasmVNC images pin `publicIP` to the loopback address so they start on
  isolated lab networks without STUN/internet.

## [5.11.0] - 2026-11-14

### RangeBox and learning workspace
- The Kali RangeBox now runs KasmVNC (Xvnc plus its built-in web server)
  instead of Xvfb + x11vnc + websockify. KasmVNC provides native dynamic
  resize, clipboard, and its own control bar.
- The platform serves a pinned, unmodified KasmVNC 1.5.2 browser client from
  `/kasm/` and proxies only the WebSocket. The client is never loaded from the
  student's container.
- `/api/rangebox/transport` probes each running container and selects KasmVNC
  or noVNC per image, so mixed and rolling rebuilds keep working. UbuntuBox and
  RemnuxBox remain on noVNC until rebuilt.
- Wide screens now present the desktop, exercise briefing/flag, and workbook in
  one workspace instead of three tabs. The exercise flag card is sticky, has
  Paste/Enter submission, and links directly to hints.
- Beginner exercises open the workbook taller and show a workbook-led callout;
  compact screens keep the tab shell.
- For KasmVNC sessions, the platform hides its noVNC-only quality, clipboard,
  and Ctrl+Alt+Del controls and offers **Reload desktop** with a fresh
  WebSocket ticket. Admin "View As" remains read-only at the proxy.
- KasmVNC is GPL-2.0; package, SHA-256, source, and the custom CSP are recorded
  in `docs/KASMVNC.md` and `THIRD_PARTY_NOTICES.md`.

### Role-aware navigation
- Administrators now land on the Admin interface and no longer see the learner
  Ops Center, Academy, Tools, or RangeBox navigation. The Admin sections are
  split into Administration and Operations.
- Instructors keep the learner menu (including RangeBox and workbooks) plus a
  Teaching section for their courses, exercises, reports, and surveys.
- The sidebar shows the signed-in role beside the account name. Administrators
  keep profile, privacy mode, logout, and the manual; the admin RangeBox
  capacity and stress tools remain under Admin settings.
- Admin live-activity rows show RangeBox status without opening the student
  desktop.

### Export data labels
- New **Settings → Data labels** option controls a classification (Public,
  Internal, Confidential, Restricted), export owner, optional handling note,
  and generation timestamp.
- A response middleware labels every attachment, PDF, and CSV download with
  `X-Data-Classification`, `X-Data-Organisation`, `X-Data-Handling`,
  `X-Data-Source`, and `X-Export-Generated-At`.
- PDF report, transcript, certificate, event-certificate, analytics, and
  exercise-test exports write the label into document properties.
- Personal-data and provider JSON exports include an `export_metadata` object.
  The admin settings panel previews the label before saving.

## [5.10.0] - 2026-11-14

### Open Badges
- The profile now lists issued Open Badges with status, issue date, name-sharing
  state, viewer links, copy-link, and a toggle to include or omit the display
  name on the public credential. Name-sharing changes are audited, and a
  revoked credential cannot be changed.
- Changing the issuer URL after credentials exist now requires explicit
  confirmation; older credentials keep their original issuer and status URL.
  The issuer form stays disabled until the current settings load.

## [5.9.1] - 2026-11-14

### Open Badges
- The admin Open Badges panel can revoke an active credential with a reason; the
  action is audited and the list refreshes to show the new status.

## [5.9.0] - 2026-11-14

### Open Badges
- Added an admin **Open Badges** settings panel: issuer name and URL, current
  key ID, signing-key count, credential count, recent credentials, and key
  rotation.
- Key rotation publishes the old public key in the JWKS so credentials signed
  before rotation still verify.
- Added a public `/badges/:jti` credential viewer: achievement, issuer, status,
  recipient (or pseudonymous subject), JWKS link, JWT copy/download, and raw
  claims. The certificate page now links to the viewer.
- Added admin-only badge settings/list/rotate endpoints; changes are audited.

## [5.8.1] - 2026-11-14

### Fixes
- Badge eligibility now evaluates only the labs in the requested level, not every
  lab in the track. The first build incorrectly required all track labs before
  issuing a level credential.

## [5.8.0] - 2026-11-14

### Open Badges 3.0
- Hosted **JWT-VC** credentials for completed level certificates, signed with
  Ed25519. The issuer key is generated on first use and stored encrypted; the
  public issuer profile and JWKS are published.
- Learners issue a badge from the certificate page, see the credential link, and
  can copy it. Sharing is opt-in; the credential subject is pseudonymous by
  default, with an optional display name.
- Credentials expose a status endpoint and an audited admin revocation path.
  Migration `0029_open_badges`.
- Phase 1 covers level certificates; event awards, badge images, and third-party
  viewer compatibility testing remain follow-ups.

## [5.7.0] - 2026-11-14

### About
- Added real host package/reboot status. `scripts/collect-host-health.sh` records
  the OS, kernel, uptime, upgradable/security package counts, reboot-required
  flag, and disk free space into the backend's backup volume; About reads it and
  adds an **OS packages** maintenance row and a checked-at summary.
- The collector runs at boot and every six hours from the deploy user's crontab;
  it needs no root and no new mounts.
- Added a **Platform maintenance** browser pass across Admin groups, System
  metrics, About, the instructor overview, and Exercise plan in dark and light
  themes; no console errors.

## [5.6.0] - 2026-11-14

### Cohort enforcement
- Labs in an exercise set required for a learner's cohort now count as course
  access and open without the sequential-track prerequisite lock. The course
  detail listing includes those labs. Cohort-specific access is additive; it does
  not remove anything assigned course-wide.

### Instructor reporting
- The instructor Overview can filter to one student inside a selected course.
  Cards and trends then reflect that learner only; cross-course student filtering
  is intentionally not offered.

### About
- The About page has a **Platform maintenance** section: live host OS, kernel,
  Docker, Python, PostgreSQL, schema, and build toolchain versions with supported/
  target status and the upgrade path. It also shows the operator upgrade and
  rollback commands and the readiness/runbook references.

## [5.5.0] - 2026-11-14

### Course planning
- Added cohorts, exercise sets, and requirements to a course, with migration
  `0028_course_planning`.
- Instructor course workspace has an **Exercise plan** tab: create cohorts and
  pick members from the enrolled roster, build exercise sets from the course
  labs, attach a completion rule (all / percent / count) with a due date and
  note, and see coverage by cohort.
- Coverage shows learners, met/missing counts, overdue state, and per-learner
  completion for the instructor. Usernames respect privacy mode.
- Requirements are planning and coverage in this phase; platform-wide exercise
  access is unchanged. Enforcement of cohort-specific access is a later change.

## [5.4.0] - 2026-11-14

### Instructor
- Added a cross-course **Overview** to the instructor panel: cards for courses,
  unique learners, active learners, completion, completed pairs, and pending
  reviews; a completion/active-learner trend chart; and a course table.
- Filters: 7/30/90-day windows, custom start/end dates, and a single-course
  filter. Course rates are suppressed below five learners; no learner is ranked
  or named. Existing course management tabs are unchanged.

## [5.3.1] - 2026-11-14

### Navigation
- Admin tabs are grouped into People, Learning, Operations, and Configuration
  instead of one flat row; tab keys and routes are unchanged.
- Workbooks moved into the Academy sidebar section for every role; the admin
  Resources section keeps the user manual.
- Added the Academy/instructor/reporting information-architecture proposal
  (`docs/ACADEMY-INSTRUCTOR-REPORTING-IA.md`), including cohorts, exercise sets,
  requirements, trend metrics, and privacy thresholds.

## [5.3.0] - 2026-11-14

### System view
- Added a **Metrics** sub-tab to Admin → System with CPU load, memory, disk,
  active lab sessions, DB connections, live RangeBoxes, and container/image
  counts. Each card shows the current value and an inline history graph, with
  1-hour, 6-hour, 24-hour, and 7-day windows.
- Metrics are sampled every minute from host load/memory/disk, PostgreSQL, and
  the container runtime, retained for 30 days. Admin-only
  `/api/admin/system/metrics` and a manual "Sample now" action back the view.

## [5.2.2] - 2026-11-14

### Fixes
- The startup lab-egress pass now installs `iptables` in its helper container;
  `alpine:latest` does not include it, so the pass had been failing on both
  hosts while the manually applied rules stayed in place.
- The egress policy is also re-applied at boot and every five minutes from the
  deploy user's crontab on development and production.

## [5.2.1] - 2026-11-14

### Security
- Lab and RangeBox egress is default-deny: the host LAN and published platform
  ports, lab gateways (including SSH), the internet, and link-local metadata are
  blocked. Same-lab ranges, the shared target network, and QEMU guests keep
  working. Host-local services are dropped in a dedicated `OCR-LAB-INPUT` chain.
- The backend reattaches to live RangeBox proxy networks on startup, so a
  redeploy no longer breaks VNC for sessions that stay running.

## [5.2.0] - 2026-11-14

### Audit and impersonation
- Admins can open any user's interaction history; instructors can open it for a
  student enrolled in their course. The report combines activity events with the
  impersonation sessions involving that user, and every view is itself audited.
- Impersonation is now recorded server-side for its full lifetime, with
  **live**, **ended**, and **expired** status. The admin Activity tab shows live
  sessions and accepts a username lookup for the full history.
- `impersonation_sessions` migration `0026`, with start/exit audit detail that
  names the target and session.

### Operations
- Backup transports can now write the encrypted set to an SSH/rsync target, an
  already-mounted NFS directory, an SMB share via curl, an rclone remote, or a
  custom command. Off-host copies are encrypted by default; plaintext requires
  the explicit `BACKUP_ALLOW_PLAINTEXT=1` override.

## [5.1.2] - 2026-11-14

### Operations
- The deployment monitor now supports an `ALERT_COMMAND` hook and writes
  `last-failure.txt`, so failures are actionable without a webhook.
- The backup script can upload the encrypted set to an SMB/NAS target via curl
  (`BACKUP_SMB_URL`, `BACKUP_SMB_NETRC`). The NAS copy remains disabled until a
  service account is provided.

## [5.1.1] - 2026-11-14

### Operations
- Off-host backups are encrypted to the **OCR Offsite Backup** key before
  transfer (dump, erasure ledger, and platform env); the local plaintext dump is
  retained for the weekly restore drill. Verified by decrypting the off-host
  copy and matching the SHA-256.
- `scripts/monitor-deployment.sh` runs every 10 minutes and checks the API
  version, backend health, 8443 workbook origin, containers, disk, local and
  off-host backup age, and certificate expiry. Optional Slack-compatible webhook
  via `~/.ocr-monitor.env`.

### Fixes
- The dev-only LDAP plaintext escape hatch now honors
  `SSO_ALLOW_INSECURE_HTTP`, matching the provider validator. This restores the
  local Dex/OpenLDAP stack without weakening production defaults.

## [5.1.0] - 2026-11-14

### Identity
- Identity provider settings export/import: versioned bundle, fixed dry-run
  first, existing names skipped unless requested, missing secrets force a
  provider disabled, admin-only and audited. Secret values are never exported.
- Removed the unused `meta.module` router branch; modules remain enforced by the
  backend middleware and feature flags.

### Operations
- Production backups now push off-host to `ocr-offsite:/home/<dev-user>/backups/prod`
  after the nightly dump; the weekly restore drill is unchanged.

### Next
- Open Badges 3.0 hosted credentials are planned for 5.2; the build plan is in
  `docs/OPEN-BADGES-3.0-SCOPE.md` and nothing is claimed as shipped.

## [5.0.1] - 2026-11-14

Security and compliance patch on top of Release 5.

### Security hardening
- LDAP: referral chasing is disabled, and plaintext `ldap://` requires an
  explicit `allow_plaintext` opt-in; `ldaps://` or StartTLS is the default.
- OIDC: ID-token signing algorithms are restricted to an asymmetric allowlist;
  a provider advertising only `HS*`/`none` fails closed. Nonce comparison is
  constant-time.
- SSO: post-login `return_to` rejects backslash and control-character forms in
  both the backend and the SPA.
- Production: `wiki_frame_ancestor` is set for the real app origins so workbooks
  frame on `https://<prod-host-ip>`, `https://<platform-host>`, and the public IP.

### Review record
- Added `docs/SECURITY-REVIEW-5.0.1.md` covering the SSO review, route-guard and
  bundle exposure check, frontend licence scan, and IdP export assessment.

## [5] - 2026-11-14

Release 5. LTI 1.3 Advantage, per-student accommodations, human review, the
tabbed workspace, and the associated procurement evidence. Production and
development both run this release from `main`.

### LTI 1.3 Advantage
- Platform registry, OIDC third-party login (GET and form POST), signed
  `id_token` validation, single-use state, external-identity linking, and the
  SPA ticket exchange.
- AGS 2.0: private_key_jwt token exchange, line items, reviewed score passback,
  result retrieval, and an append-only ledger.
- NRPS 2.0: explicit roster sync with the minimum subject/role/status/context
  fields and LIS 2.0 membership parsing.
- Deep Linking 2.0: single-use picker, signed response, lab launch content
  items, selection limits, and an embeddable picker/callback.
- Public tool JWKS with an RFC 7638 `kid` on every signed message.
- Verified end to end against Moodle 5.0.2, including a grade reaching the
  Moodle gradebook and NRPS returning the course roster.

### Accommodations
- Per-student 1.0x–3.0x timed-session multiplier and 0–365 day due-date
  extension, managed by instructors and audited.
- Learner pause/resume clock with a reason, a frozen expiry, scheduler
  exclusion, and paused-time credit on resume.
- Append-only `accommodation_events` and activity-log records.

### Learning workspace
- The exercise view uses full-size **Desktop**, **Exercise**, and **Workbook**
  tabs instead of a split grid. The desktop stays mounted across tab switches
  so the VNC session is not dropped. The briefing, flag, hints, and workbook
  remain one click away.
- The same tabs appear for every lab. The Desktop tab shows RangeBox, VPN
  connection guidance, a start prompt, or the mobile notice instead of
  changing the whole page layout. The selected lab and tab persist in the URL
  across refresh and back/forward.
- The RangeBox toolbar is the single desktop bar: the duplicate pane header is
  gone, and connection/clipboard/fullscreen/quality controls stay in one place.
  Left/right arrow keys move between tabs.
- Workbooks can be served from a dedicated wiki origin. Dev uses
  `https://<dev-host-ip>:8443`, so the framed workbook keeps its own storage and
  search without access to the SPA token; the SPA CSP allows that frame.
- The workbook iframe loads only when the Workbook tab is first opened. It
  stays mounted afterwards, so switching tabs does not reload it or lose its
  scroll position.

### Human review
- The exercise result panel states that flag matching is deterministic and
  offers a human-review request. Learners see pending/approved/rejected status
  and the instructor's note.
- Instructors review pending requests per course, approve or reject with a note,
  and every request/decision is audited.

### Minor accounts
- Minor enrollments can record the institution's parental/guardian consent
  reference and the staff member who recorded it. The roster flags missing
  consent, and changes are audited. Identity documents are not stored.
- Each course has a retention date and note. Administrators can preview the
  learner records in scope and record an append-only completion reference after
  the documented backup-and-purge runbook step.

### RangeBox
- Pinned the Kali base image digest and the SecLists commit.
- Baked the wordlists the labs reference at their documented paths: `common.txt`
  (also at `/usr/share/wordlists/dirb/common.txt`), the DirBuster medium list
  (also at `/usr/share/wordlists/dirbuster/`), the DNS top-5000 list, and two
  password shortlists. The upstream medium-list filename moved; the download now
  uses the pinned path that resolves.
- Documented the root-inside-caged-container model and the Firefox content
  sandbox rationale in `RangeBox/SECURITY-MODEL.md`.

### Operations
- Migrations `0015`–`0025`.
- Development `<dev-host-ip>` tracks `main`; live lab spawn, pause/resume,
  accommodation read-back, 10-lab sampling, and an authenticated page pass all
  verified.
- Production `<prod-host-ip>` deployed on 2026-11-14: version 5, Alembic
  `0025_review_requests`, 179 labs, backend/frontend healthy, 8443 workbook
  origin responding.

## [4.0.2] - 2026-11-14

Release 4 production hotfix. Frontend only; schema and API remain Release 4.

### RangeBox workspace
- Desktop, Exercise, and Workbook are full-size tabs instead of a split grid.
- RangeBox stays mounted across tab switches.
- The desktop toolbar wraps in narrow panels instead of clipping controls.
- See [`RELEASE-4-HOTFIX-4.0.2.md`](docs/RELEASE-4-HOTFIX-4.0.2.md).

## [4] - 2026-11-12

Release 4. Enterprise single sign-on, the optional Dex/OpenLDAP test stack, and
the privacy, accessibility, and API-exposure corrections.

### Enterprise SSO
- OIDC authorization-code login with PKCE, state, nonce, discovery, JWKS, and
  issuer/audience/signature validation.
- SAML 2.0 SP-initiated login with signed assertion validation and shared
  RelayState/AuthnRequest state.
- LDAP/Active Directory sign-in with a service bind, user rebind, filter
  escaping, StartTLS, and certificate verification.
- One provisioning/linking service for all adapters: verified-email linking,
  administrator-link refusal, SSO-only accounts, and instructor group mapping.
- Directory role mapping is refreshed on every SSO login, so a group change takes
  effect without an administrator editing the account.
- Optional `sso` compose profile with Dex (OIDC) and OpenLDAP, a generated Dex
  config, LDAP bootstrap users, and an `/idp/` nginx proxy for local testing.
- The local administrator password login remains as break-glass access.

### Security
- The backend now trusts `X-Forwarded-For`/`X-Forwarded-Proto` only from
  loopback and private Docker bridges. Per-IP rate limits and audit rows use the
  real client address instead of the nginx container address.
- SSO states and tickets remain single-use, provider-bound, and short-lived.
- The API-docs and module gates read their setting fresh on every request, so an
  administrator disabling either takes effect immediately instead of after the
  settings cache expires.
- nginx returns 404 for `/docs`, `/redoc`, and `/openapi.json` on the public
  origin; API documentation is never served through the learner-facing host.
- SSO callback failures now render curated user messages instead of raw backend
  error details.
- The CI CSP-hash check fails on both missing and stale inline-script hashes;
  the `v-html` exception remains limited to the two reviewed DOMPurify sites.
- Workbook and launch links go through `safeHttpUrl` and open with
  `noopener,noreferrer`.
- Documented the HttpOnly session-cookie migration roadmap, including CSRF,
  refresh/revocation, wiki-gate, and acceptance criteria.

### Privacy
- Subject-access export now includes external identity links and SSO session
  metadata, without the encrypted ID token or provider secrets.
- Account erasure explicitly removes external identities, SSO sessions, and SSO
  tickets and records the counts in the erasure result.
- Added identity-federation data to the privacy and procurement documentation.

### Accessibility
- The institution sign-in panel is a labelled section with a heading, visible
  directory-field labels, per-provider accessible button names, error
  associations, `aria-busy` state, and visible focus styles.
- Cyber DNA and Cyber GPS use one scale (`/99` for DNA), an accessible
  "How this is calculated" disclosure, and a zero-evidence start card instead of
  an empty radar chart. Career GPS labels each family's evidence band.

### Network device topology
- Added `x-ocr-topology` to Compose: nodes, roles, and point-to-point links are
  validated as data, then expanded into per-session `/29` networks with static
  addresses, forwarding, routes, and node environment.
- Added the reviewed `ocr-lab/topology-node` image with `router`, `host`, and
  `service` roles, SSH, a status endpoint, and a flag service.
- Rejected privileged containers, arbitrary images, host networking, bind
  mounts, hostile capabilities, and reserved environment keys.
- Added the routed-path demo lab plus two-router transit, firewall service path,
  and multi-service router labs, with workbook chapters, engine unit tests, and
  image-only topology support in the static validator.
- Added a guided and an independent Forensics variant on the same engine, with a
  decoy service in the independent version, so learners can choose their pace.
- Added YARA fundamentals and a YARA + incident-log triage scenario, and a
  Windows AD fundamentals lab plus an AD-to-SMB credential-reuse scenario.

### Learner experience
- Dashboard and profile now use the same visible-exercise denominator, and the
  dashboard course matrix, course card, course detail, and profile all use the
  same enrolment-aware completion rule. The course-card percentage rounds
  half-up so it matches the course page.
- New learners see an evidence-first profile: five tabs, no Cyber GPS or
  Portfolio tab, no zero-evidence career affinity, and a progress-only Learning
  record with **Show all tracks** for the rest.
- Experienced learners can focus the profile on a course, track, certification,
  or career goal, with course/track/certificate progress lenses and a searchable
  focus list. The career target is promoted to the top of the Portfolio tab.
- The title collection is collapsed by default with an **Unlocked only** filter,
  and achievement badges use the shared SVG icon system instead of emoji.
- Workbook actions and profile status badges use the shared colour tokens.
  Track difficulty chips, VM status dots, and the safe admin/track status
  surfaces use the same tokens; custom-achievement authoring now uses the SVG
  icon picker.

### Documentation
- Added the compliance posture, procurement traceability, accessibility
  statement, automated-scoring statement, HECVAT answer pack, LTI design
  contract, DPA template, and Release 5 scope.
- Release 4 does not claim LTI, multi-tenancy, a per-student accommodation
  engine, a TA role, a signed VPAT, SOC 2, or ISO 27001.

### Fixed
- Event certificates now transliterate characters the built-in PDF fonts
  cannot encode, so an event date with an en dash (or an accented name) no
  longer fails certificate generation.

## [3.1.1] - 2026-11-05

Enterprise SSO adapter release.

### SAML 2.0 sign-in
- SP-initiated SAML login with signed assertion validation, audience/recipient
  checks, and AuthnRequest ID validation through `python3-saml`.
- Shared PostgreSQL state stores the RelayState and AuthnRequest ID, so the ACS
  can run on a different API replica from the login start.
- ACS endpoint at `/api/auth/sso/saml/{id}/acs`; the SP entity ID and ACS URL
  are shown in the provider card.
- Optional signed AuthnRequests with an SP certificate and private key.
- Attribute mapping for email, username, name, and groups, with an optional
  instructor group.

### LDAP and Active Directory sign-in
- Service bind, user search, and a user rebind to verify the password.
- LDAP filter escaping, StartTLS, certificate verification, and a configurable
  server timeout.
- Attribute mapping for email, username, name, and groups, with an optional
  instructor group.
- Direct institution-account form on the login page; failures distinguish bad
  credentials from a directory outage.

### Shared identity policy
- OIDC, SAML, and LDAP now use one provisioning and linking service.
- Verified-email linking, administrator-link refusal, and SSO-only accounts are
  identical across adapters.
- New accounts can be provisioned as student or instructor through group
  mapping. External identities never receive administrator access.
- Provider test actions validate OIDC discovery, LDAP service bind, and SAML
  settings.

### Documentation
- Added `docs/SSO-SAML-LDAP.md`; updated the OIDC guide, ADR 0004, the
  Enterprise manual supplement, editions, and supported versions.

### Limits
- SAML RP-initiated logout/SLO remains local; OIDC logout remains the only
  IdP-initiated logout path.
- A formal SSO security review remains.

## [3.1.0] - 2026-11-05

Enterprise single sign-on release.

### OIDC SSO
- Authorization-code login with PKCE, state, nonce, discovery, JWKS, and
  issuer/audience/signature validation.
- Shared PostgreSQL flow state and one-time SPA exchange tickets. Any API
  replica can complete a callback started on another replica; no sticky
  sessions are required.
- Stable public callback URL derived from `PUBLIC_BASE_URL`.
- Auto-provisioning, auto-approval, verified-email linking, and SSO-only
  accounts. Administrator accounts are never auto-linked.
- A local break-glass administrator remains available.
- Provider test endpoint for OIDC discovery and JWKS reachability.
- The provider card shows the exact redirect URI to register at the IdP.
- Activity and audit events for SSO login, provisioning, and linking.
- RP-initiated logout when the provider advertises an end-session endpoint.
  The ID token is stored encrypted and removed after use.
- New `password_login_disabled` account flag and `external_identities`,
  `sso_login_states`, `sso_login_tickets`, and `sso_sessions` tables.

### Documentation
- Added ADR 0004 (SSO HA contract) and `docs/SSO-OIDC.md`.
- Updated the Enterprise manual supplement and login guide.
- Moved the Enterprise version line to **3.1.x**.

### Limits
- SAML and LDAP login adapters are not part of 3.1.0; their settings remain.
- A formal SSO security review remains.

## [3.0.3] - 2026-11-05

### Learner profile
- Added **Skill DNA**: five activity-based traits (Explorer, Builder, Defender,
  Investigator, Leader), a class, a tier, and a certification alignment card on
  the profile.
- Added achievement **titles**. Unlocked titles can be equipped or cleared; the
  class title returns when no achievement title is equipped. Hidden titles stay
  secret until unlocked.
- Added the **Title collection** and the equipped-title badge on the profile.
- Added explicit course, competition, advanced-lab, and teaching signals to the
  Leader trait.
- Added the metric model in `docs/SKILL-DNA.md`.

## [3.0.2] - 2026-11-05

Maintenance release for the Enterprise line.

### Admin user management
- The Users table shows the last sign-in time, with a relative label and the
  exact timestamp on hover.
- Added filters for status, role, last sign-in window, and VPN registration,
  plus a sort control, result range, clear-filters action, and empty state.
- Role and account status are separate columns; the table has accessible
  headers and a stacked layout on narrow screens.

### Reliability
- Rate limiting now degrades to in-process limits when Redis is unavailable
  instead of returning HTTP 500 on login.

### Design and release
- Added the OpenCyberRange Design Tester skill for light/dark, layout, filter,
  and accessibility reviews.

## [3.0.0] - 2026-11-04

Enterprise release line.

- LDAP, OIDC, and SAML identity-provider settings with encrypted secrets and
  audit logging (settings-only; login federation remains in the Enterprise HA
  workstream).
- Enterprise inherits the Professional 2.1 analytics, reporting, competency,
  feedback, certification guidance, and admin security changes.
- Multi-host HA, gateway failover, multi-tenancy, LMS integration, and
  regulatory reporting remain in the Enterprise programme; see
  `docs/V3-HA-LAB-POOL.md` and `docs/EDITIONS.md`.

## Edition model

- **Community / Academic 1.1** — supported single-host teaching platform, lab
  and workbook improvements, exercise authoring, maintenance, and security.
- **Professional 2.0** — Community / Academic plus analytics, reporting, cohort
  analysis, competency evidence, accreditation support, and research exports.
- **Enterprise 3.0** — Professional plus HA, SSO, enterprise reporting,
  multi-tenant support, LMS integration, and compliance reporting. See
  `docs/EDITIONS.md`, `docs/decisions/0002-edition-model.md`, and
  `docs/decisions/0003-edition-scope-refinement.md`.

### Professional and Enterprise priorities

- Competency Framework Engine.
- Student Feedback Engine.
- Radar / Spider Web Reporting.
- Exercise Health Analytics.
- Instructor Intervention Dashboard.

These five priorities are Professional 2.0 and Enterprise 3.0 only. See
`docs/PROFESSIONAL-PRIORITIES.md` and `docs/PROGRAMME-REPORTS.md`.

## [Release 3] - 2026-11-12

### Cyber DNA 2026.14
- Branch and overall scores are capped at **99**, never 100.
- Each branch decays from its own last practice date (99% at 15-30 days, 97%
  at 31-60, 94% at 61-90, 90% after 90) and a new completion in that branch
  restores it.
- The profile reports a **40-hour continuing-education** target over the
  trailing 12 months and a **30-day directional trend** rebuilt from completion
  and quiz timestamps.
- Spider-chart points scale with **evidence strength**: clean, unaided,
  advanced, assessment, and high-scoring quiz work weighs more.
- The public `signals` payload is JSON-safe, so a populated profile no longer
  returns 500 on serialization.

### Cyber GPS signal
- The GPS shows an active or fading practice signal from completions in the last
  30 days. Active domains shimmer; quiet domains fade and appear as **fading
  interest signals** with a prompt to revisit.

### RangeBox and workbook
- The workbook pane hides MkDocs chrome, uses the full width, scrolls
  independently, and grows to 58vh with **Expand**.
- The RangeBox can **pop out** into its own resizable window while the main tab
  keeps the briefing, notes, and workbook.
- noVNC gains a stream-quality selector, Ctrl+Alt+Del, native fullscreen, focus
  on connect, and clearer security/credential failure messages.
- The flag field captures `OCR{...}` from the desktop clipboard, cleans pasted
  text, and offers **Paste**, **Read clipboard**, and **Use as flag**.
- The RangeBox is **text-only**: file drops, file pastes, and drag-out are
  rejected. No files leave or enter the desktop.
- The user manual adds **Navigating your Cyber DNA** with dev screenshots; the
  admin guide adds **Cyber DNA and RangeBox Operations**.

### Community events
- The **Events** tab keeps platform events at the top and adds an **Around the
  area** calendar underneath.
- The calendar combines internal platform events with community events and
  lists upcoming entries, with source links for SWOCTS Hub and Cyber Hive YXU.
- Community events are explicitly outside Cyber DNA, course credit, and platform
  scoring. The user manual adds **Community Events**.

### Tools
- CyberChef 11.5.0 is now a pinned, SHA256-verified static build served from
  the frontend image at `/tools/cyberchef/`. The Tools panel loads it
  same-origin, so it works on isolated ranges and no longer depends on
  `gchq.github.io` or a widened `frame-src` policy. The location carries a
  tailored CSP with the release's inline-script hashes pinned.

### Reliability
- The expired-session cleanup pass now runs in a worker thread. It performs
  synchronous SQLAlchemy and Docker teardown, so running it on the event loop
  could freeze every request in the single-worker deployment (symptom: every
  page stuck on "Loading…", `/health` timing out).
- Startup schema and ledger advisory locks now time out after 30 seconds
  instead of waiting indefinitely, and Alembic no longer disables existing
  loggers, which had hidden all startup output after the migration step.

## [2.7.0] - 2026-11-11

### Learning
- Added `has_quiz` to each track level and show the level **Quiz** button only
  when the level is complete and an active quiz bank exists.
- Seeded the Beginner level quiz banks: 5 questions for Stage 1, 5 for Stage 2,
  4 for Stage 3, and 4 for Stage 4, with a passing score of 70. The seed script
  is `platform/backend/app/scripts/seed_level_quizzes.py`.
- Added `scripts/ui-learning-smoke.mjs`, which compares the rendered Quiz and
  Certificate buttons with the track API for every level.

### Labs and network
- VPN-only sessions now reveal target IP addresses and the hosts-file mapping;
  RangeBox sessions keep addresses hidden unless `show_target_ips` is set.
- Installed and persisted the WireGuard client-pool route
  `10.255.0.0/16 dev wg0` in `scripts/setup-range-server.sh`, with
  `scripts/fix-wireguard-client-route.sh` for existing hosts.
- Lab cleanup now preserves networks owned by a session that is still
  `starting` or `running`, so a stop/relaunch no longer removes the live
  environment.

### Operations
- Added `docs/DEPLOYMENT-RUNBOOK.md` with pull, rebuild, prebuild, quiz-seed,
  and health commands for development and production.
- The status dashboard reads its host map from `docs/status-hosts.json`.
- Added the public verification smoke and event-certificate PDF layout test.

## [2.6.0] - 2026-11-10

### Events and certificates
- Added event certificates for participation, placement (1st, 2nd, 3rd), and
  trophy challenges (First Blood, Clean Sweep, Perfect Event).
- Certificates render the event logo and gold/silver/bronze sponsor marks in the
  app and in the PDF, and use deterministic `OCR-EVT-` IDs with a SHA-256
  digest.
- Added `/api/competitions/{id}/certificates` and
  `/api/competitions/{id}/certificate/{award}?format=json|pdf`; certificates are
  issued only after the event ends to approved, opted-in participants, and
  placement/trophy awards require the matching event achievement.
- Public verification now accepts event IDs and returns event/award metadata
  without scores or account identifiers. The verification form validates both
  track and event ID formats before enabling submission.
- Added certificate links to the competition detail page and an event mode to
  the certificate view. Certificate opt-out also hides the event verification
  URL and QR code.
- Documented the award model, ID format, API, privacy rules, and tests in
  `docs/EVENT-CERTIFICATES.md`.

### Reporting
- Added a decision-led instructor report library: course health brief, exercise
  diagnostics, coaching queue, and the full student record pack.
- Reports carry a report ID, SHA-256 checksum, and HMAC-SHA256 manifest
  signature; PDFs print the ID and CSV files include it.
- Added cohort mean/median solve-time and hint-use baselines, plus an
  engagement signal for unusually fast, hint-free completion. The signal is a
  support prompt, not an AI accusation or ranking.

### Privacy
- Added under-18 reporting privacy. When enabled, the learner is excluded from
  instructor reports, course analytics, coaching queues, public leaderboards,
  and competition scoreboards; their own dashboard still works.
- Added public certificate verification opt-out. When disabled, the public
  verifier returns the generic invalid result and the certificate payload omits
  the verification URL and QR code.
- Added public `/about` for first-time visitors; detailed installation inventory
  moved to `/about/installation`.
- Added `Cache-Control: no-store` to `/api/about` so a stale release version is
  not cached after deployment.

### Labs and tools
- Added CyberChef to the student Tools menu and the active-lab panel.
- Added three entry-level High School Grade 9 CyberChef labs: Base64 decode,
  Caesar shift/ROT13, and a two-layer Base64 + ROT13 message, with workbook
  pages.
- Added three Grade 9 digital-safety labs: read a lookalike link without
  clicking it, identify a disguised file before opening it, and a capstone that
  combines both, with workbook pages.
- Added a Grade 10 email-metadata lab covering envelope and display headers,
  `Received` chains, SPF/DKIM/DMARC results, and custom `X-` headers.
- Added three Grade 10-12 Digital Frontier labs: lost-phone MFA recovery, media
  provenance verification, and a crypto rug-pull investigation, with workbook
  pages, quizzes, badges, titles, certification pathways, and NICE mappings.
- Added the Identity & Access track with three labs: secure authentication and
  session forgery, OAuth/OIDC redirect and token trust, and joiner/mover/leaver
  lifecycle and access review.
- Hardened the shared High School target with a restrictive CSP, `nosniff`,
  `no-referrer`, frame denial, and a permissions policy.
- Added student-tester and inclusive-curriculum reviews at
  `docs/reviews/CYBERCHEF-LABS-REVIEW.md` and
  `docs/reviews/DIGITAL-SAFETY-LABS-REVIEW.md`.

### Integrity and access
- Added an audited review workflow for unattributed integrity-ledger writes.
  Reviews require an administrator, a decision, a note, and confirmation; the
  review is written to the audit log and append-only ledger.
- Serialized startup schema initialization across workers and made the new
  privacy columns idempotent.
- Refreshed the login/registration pages for AODA: skip links, focus
  management, Caps Lock warnings, password-strength text, target sizes, contrast,
  reduced motion, and explicit privacy/under-18 acknowledgment.
- Redesigned the public certificate verification page with clearer trust,
  privacy, and ID-location guidance.

### Operations
- Deployment, curriculum-seed, discovery, and installer scripts now emit ASCII
  status markers so logs render correctly in Windows terminals and CI.
- Shrunk the WireGuard client footprint: the interface address is `/32`, the
  client routes only its own lab `/24`, and the client pool moved to
  `10.255.x.y`. Existing VPN configs must be re-downloaded; a reallocation
  script and route verifier are included.
- Updated Cyber DNA to formula `2026.13`: raw event joins no longer add Leader.
  Event exercises still count as normal labs, and event success badges (first
  blood, clean sweep, perfect event, placement) still count through
  achievements. Event participation certificates are credentials, not Cyber DNA
  signals.
- Recorded the `v2.6.0` release tag as annotated but unsigned; it points at
  `2835303b`, the commit deployed to production and development on
  11 November 2026. The supply-chain lock remains signed by the release key.

### Security
- Strengthened the shared password policy for registration, password changes,
  and admin resets. It now rejects common bases with a number or symbol appended
  (`Password1!`, `P@ssw0rd2026!`), account-specific words (username, email local
  part, first/last name), repeated patterns, and simple sequences. The
  registration and change-password fields mirror the same checks before submit.
- Added password-policy regression tests covering common-password shortcuts,
  context words, repeats, sequences, and strong passphrases.
- RangeBox launch failures now report the actual cause. A missing desktop image
  returns a specific `409` response instead of a generic server error, and the
  launcher disables images that are not installed on the host.
- The orientation tour now stores its "seen" state on the user account as well
  as in browser storage. It no longer reappears after a change of hostname or
  port, cleared site data, or a second tab racing the first.

### Exercise workspace
- Desktop RangeBox exercises now open in a combined workspace: RangeBox
  top-left, scenario/details and the flag panel on the right, and the workbook
  as a framed pane along the bottom. Phones keep the existing stacked panel.
- The workbook pane has an Expand/Restore control and an open-in-new-tab
  fallback; the flag panel stays visible while the details scroll.
- Launching from the exercise panel now honours the lab's desktop image, and a
  lab whose tools list says `rangebox` launches a Kali desktop instead of
  starting VPN-only.
- Fixed lab-attached RangeBox VNC: the proxy network used the Docker gateway
  address (`.1` on a `/30`) for the desktop, so the viewer stayed on
  "Connecting". It now uses a `/29` with the desktop at `.2` and the backend at
  `.3`, and replaces legacy `/30` networks.
- Student-tested on the High School RangeBox First Steps lab: desktop connected,
  workbook loaded, flag completed the exercise, and the mobile view remained
  single-column without horizontal overflow.
- **Open in new tab** now opens the resolved `/rangebox?...` URL in a new tab.
  It previously routed the exercise tab in place, despite the button label.
- The workbook CSP now allows the Material for MkDocs Google Fonts stylesheet
  and font files. The SPA policy stays strict.
- Added `scripts/ui-workspace-regression.mjs`, which walks the workspace as a
  dedicated test student and test instructor, exercises Expand/Restore, both
  new-tab controls, hint request, invalid-flag handling, and Stop, and records
  JSON evidence plus screenshots. Final run: **44/44 checks passed**.
- Fixed a stop/relaunch race: background cleanup for an old session could remove
  the network and RangeBox created by a newer session for the same lab, which
  silently launched the new lab VPN-only. Cleanup now defers to a newer
  starting/running session and only marks the old row stopped.

### Curriculum and documentation
- Reorganized **WEB01 Web Reconnaissance** into a 12-page beginner-readiness
  chapter: scope preflight, HTTP orientation, browser observation, technology
  fingerprinting, bounded discovery, virtual hosts, public metadata, inputs and
  sessions, TLS and headers, findings, comprehensive reconnaissance, and review.
  The six existing labs keep their targets, flags, and behaviour; their
  `workbook:` paths now point at the new pages.
- Added **Educational material provenance** (`docs/EDUCATIONAL-PROVENANCE.md`)
  covering ownership, source-of-truth files, review status, framework references,
  synthetic content, AI assistance disclosure, licensing, and change control.
- Updated the README, Lite quickstart, platform overview, interface guide,
  exercise and RangeBox review, UI verification, privacy notice, and data
  deletion runbook for the combined workspace and the beginner track.
- Added desktop, light-theme, and mobile workspace screenshots to the docs.

### Licensing
- Added CyberChef attribution (Apache-2.0, external tool) to the third-party
  notices, About lab toolchains, and licence bundle.

## [2.5.5] - 2026-11-10

### Security
- Resolved the full open code-scanning set (595 alerts: 69 CodeQL, 526 Trivy).
- Fixed platform path handling in About, stress-test state, exercise testing,
  workbook chapters, and lab uploads; stack traces and daemon details are no
  longer returned to clients.
- Seed scripts now require their development passwords from the environment and
  never print or write them. Audit details redact password, secret, token, and
  key fields.
- Replaced the Admin VNC page's `innerHTML` interpolation with DOM/text nodes.
- Excluded intentionally vulnerable lab target applications from CodeQL; lab
  structure remains gated by `validate-lab.py` and `lab-release-proof.py`.
- Added path-scoped, documented Trivy suppressions for privileged lab images and
  the platform components that need root, privileged ports, or raw sockets.
- Removed `EXPOSE 22` and `RUN cd` from lab builds and replaced fake Stripe,
  Plaid, SendGrid, internal-API, and JWT values with explicit `FAKE_*` markers.

### Data integrity
- Added **Admin → System → Integrity** with a live ledger summary: entries,
  last write, unattributed writes in the last seven days, and covered tables.
- Added `scripts/db-integrity-check.sh` and `deploy/systemd/` units for daily
  quality, ledger, and checksum evidence and weekly signed manifests.
- Added an `occurred_at` index for the ledger status query.

### Upgrade
- Existing 2.5.4 databases upgrade in place. No destructive migration.
- No dependency or image pins changed in this release.

## [2.5.4] - 2026-11-10

### Lab metadata and curriculum
- Standardized all 149 lab manifests on the canonical `title`, `category`,
  `difficulty`, `estimated_time`, `prerequisites`, `learning_outcomes`,
  `mapped_skills`, `assessment_criteria`, and `mitre_attack` header.
- Replaced legacy `name`, `duration_minutes`, `objectives`, and
  `learning_objectives` keys with canonical keys while keeping legacy loading
  fallbacks for existing uploads and records.
- Generated `prerequisites` from the sequential unlock graph and added
  `mapped_skills` using the eight competency axes.
- Added a repeatable standardizer and static schema test for the full catalog.

### Learning outcomes
- Every lab now opens its outcomes with
  `# By completion students will be able to:` and lists 3-5 measurable
  outcomes.
- Rewrote vague openers such as `understand` and `learn` to observable actions;
  removed flag capture from learning outcomes and placed it under assessment.
- The learner exercise brief uses the same heading.

### MITRE ATT&CK
- Added at least one `tactic`, `technique`, `technique_name`, and `detection`
  mapping to every lab.
- Added an ATT&CK panel to the learner brief and exposed the mapping through
  the curriculum API.
- Added validation, a mapping service, and Alembic migration
  `0008_mitre_attack`.

### Instructor and student dashboards
- Added an instructor **Teaching focus** panel for learners one lab from a
  certificate, learners inactive 7+ days, and recent wins.
- Added a seven-day instructor learning snapshot: active students, labs
  completed, average score, and struggling students.
- Added per-course completion progress to student course cards and a workspace
  completion summary.
- Added a course readiness panel with a single next action for invite,
  exercises, assignments, or roster.
- Made student course cards real links with keyboard focus and accessible
  labels.

### Basic learning analytics
- Documented the five minimum metrics: lab started, lab completed, completion
  time, pass/fail, and retry count.
- Defined the instructor score as a transparent 0-100 participation score,
  adjusted for retries and hints.
- Reused existing session, completion, flag-attempt, and activity data rather
  than adding new learner tracking.

### Security and privacy
- Sanitized scenario markdown and validated external URLs to prevent stored
  XSS and unsafe link targets.
- Hardened report and certificate export privacy tests, CSV formula handling,
  and scoped instructor report exports.
- Closed leaked DB sessions, background tasks, and sockets during shutdown.
- Retried achievement writes after deadlocks and preserved the scheduler
  advisory lock without leaving an idle transaction.

### Reliability and performance
- Sized DB pools for worker count, added hot-path indexes, and dropped redundant
  primary-key indexes.
- Fixed the scheduler leader lock so background jobs do not run twice.
- Excluded runtime backend backups from deployment sync.
- Stripped byte-order marks from JSON and YAML release inputs.
- Added deployment performance guidance for the edge proxy.
- On the CTFd-hosted OCR stack at `.41`: increased the backend pool from 4+4 to
  6+6, tuned PostgreSQL planner settings, ran `VACUUM (ANALYZE)`, and reclaimed
  Docker build-cache and dangling-image space.

### Versions and migrations
- Platform, backend image, `/api/version`, and frontend package version:
  **2.5.4**.
- Alembic: `0007_lab_metadata`, `0008_mitre_attack`.
- Runtime pins remain Python 3.11, Node 22 build, PostgreSQL 15, Redis 7.2.

## [2.5.3] - 2026-11-08

### Competency radar
- Added a versioned eight-axis competency model and per-completion mapping
  snapshots.
- Added individual Baseline / Current / Target radar overlays and cohort
  median / interquartile / target overlays.
- Added per-axis evidence drill-down, separate self-confidence, provisional
  labels, mapping versions, and small-cohort suppression.
- Added the 50% assessment / 25% independent / 15% retained / 10% instructor
  scoring model with explicit weight coverage.

### Analytics privacy
- Added `analytics_min_cohort_size` and explicit available, suppressed, and
  no-evidence states to course and exercise analytics.
- Suppressed small cohorts in course feedback summaries and survey responses
  without exposing learner identities.

### Labs
- Recorded difficulty evidence for all 149 labs using platform analytics when
  `n>=5` and a labelled provisional static review otherwise.
- Added workbook and hint exemptions for instructor-led assessments.
- Added ADR 0005 accepting the lab bridge egress risk for 2.5.3.

### Accessibility
- Added PDF title, author, subject, keyword, and language metadata.
- Added the `session_accommodation_percent` timed-exercise accommodation.
- Fixed contrast defects in the skill matrix and analytics RAG badges and made
  activity and analytics table regions keyboard-focusable.
- Verified the competency radar with axe WCAG 2.2 AA at desktop and 320px.

### Supply chain
- Added OCI image version and revision labels.
- Refreshed and signed the supply-chain lock and signed the release tag.

### Privacy
- Added a public PIPEDA-aligned privacy notice at `/privacy`, linked from the
  footer and registration form. The notice uses `privacy@swocts.com` as the
  privacy contact and supplements the SWOCTS Privacy Policy.
- Added `docs/PRIVACY-NOTICE.md` and linked it from the privacy, erasure, and
  backup documentation and README.

### Reviews
- Added the v2.5.3 maintenance plan with the production analytics
  reconciliation, findings register, and release-health targets.
- Added `platform/backend/app/scripts/validate_analytics.py` for repeatable
  dashboard-to-source reconciliation.

## [2.5.2] - 2026-11-08

### Privacy settings
- Added a `privacy_default_on` platform setting under **Admin > Settings >
  Security**. Administrators can now set whether new admin browsers start with
  privacy mode enabled instead of relying on the hard-coded default.
- Added the current-browser privacy toggle to the same settings screen. The
  sidebar toggle remains available.
- Explicit per-browser choices still win. Legacy auto-written `"on"` values are
  treated as unset so a changed platform default reaches browsers that never
  made a choice.
- Documented the new location in the build notice, admin manual, release notes,
  and architecture settings table.

### Fixes
- Updated the analytics report test to expect the current six Skill DNA
  dimensions (the `leader` branch was added in 2.5.0).

## [2.5.1] - 2026-11-08

### Licence compliance
- Pinned Redis to `7.2-alpine` (BSD-3-Clause). Redis 7.4+ is RSALv2/SSPLv1 and
  is not a drop-in replacement without a licence review.
- Replaced `mysqlclient` (GPL-2.0) with MIT-licensed PyMySQL in the two web
  labs, and added SPDX GPL-2.0 headers to the Scapy-based PCAP generators with a
  documented mixed-licence exception.
- Removed the vendored Microsoft symbol table; the memory lab now generates it
  at image-build time from Microsoft's public symbol server.
- Pinned the third-party INetSim image to a reviewed digest and removed the
  breach-derived RockYou download from RangeBox.
- Rebuilt `THIRD_PARTY_NOTICES.md` and `THIRD_PARTY_LICENSES/`, corrected the
  psycopg and fpdf2 entries, and added the missing container, toolchain,
  vendored-binary, icon, and skill notices.
- Added `scripts/check-licences.py` and wired it into the quality workflow.

### About and build information
- Added an authenticated `/about` page with release, platform, branding,
  component, licence, and SBOM inventory.
- Added the generated `app/data/about` inventory, CycloneDX SBOMs, and
  `scripts/generate-about.py`.
- Documented the SWOCTS mark ownership and Avery Chaykoski design credit in
  `BRANDING.md`, the licence notices, and the About page.

### Privacy controls
- Admin accounts now default to privacy mode on when no explicit preference is
  stored.
- Usernames, emails, display names, and student IDs are masked consistently in
  admin tables, pending approvals, sessions, VPN peers, the user-details and
  edit-account dialogs, instructor tables, and activity actor names.
- Hovering or focusing a masked value reveals it. Administrators manage the
  current-browser toggle and the default for new admin browsers under
  **Admin > Settings > Security**.

### Course workspace cleanup
- Removed the Content, Achievements, and hidden Assignments panes from the
  course workspace. Overview, Feedback, and the instructor Analytics tab remain.
- Course links from an exercise now return to the course Overview.

## [2.5.0] - 2026-11-08

### Organizational course health
- Redesigned Academy → Courses around organizational course health: student
  satisfaction, instructor engagement, response rate, knowledge-check
  participation, and a prioritized action list.
- Added a private two-way feedback loop: students use the existing survey engine
  for a course check-in, instructors add coaching notes, and the summary
  aggregates check-ins, exercise pulse surveys, reactions, and coaching.
- Removed the public scoreboard from the course workspace. Detailed metrics
  remain private and descriptive; no ranking is shown.
- Added minimum-sample and data-source labels so a small response set is not
  presented as a trend.

### Optional knowledge checks
- Added optional exercise benchmarks with 2–3 randomized questions per attempt,
  unlimited re-attempts, explanations, and primary references.
- Added 10 certification-aligned lab banks and 11 track fallback banks, covering
  every exercise without making the check a gate.
- Added four benchmark achievements: Quiz Ace, Quiz Explorer, Quiz Scholar, and
  Quiz Comeback.
- Added quiz evidence to Cyber DNA (Builder and Explorer) and a Knowledge checks
  card on the profile.
- Added post-quiz experience ratings for satisfaction, relevance, usefulness,
  and ease of use; these feed the course health report.
- Added a CI validator for question banks and a documented expansion format.

### Certificates
- Added a server-rendered certificate PDF, copy-verification-link and LinkedIn
  share actions, a share panel, and Open Graph/Twitter metadata.
- Added a warning when a certificate still uses the login handle, with a link to
  set the printed name.
- Preserved earned certificates when bonus labs are added by excluding
  non-certificate labs from the level requirement.

### Labs and host validation
- Added the EXIF Metadata Investigation lab and beginner workbook.
- Certified Ubuntu 24.04 LTS for 2.4.1; 2.5.0 inherits the certified baseline.
- Fixed VPN forwarding by moving the VPN accepts into `DOCKER-USER`, added the
  missing Docker bridge UFW rule, and added the `ocr-network-tap` image.
- Raised the MS-SQL lab `max_connect_errors` threshold, corrected the remote
  credentials, and removed the trailing newline from the flag file.

## [2.4.1] - 2026-11-08

### Review remediation
- Rejected placeholder `JWT_SECRET` and `SETUP_TOKEN` values at startup.
- Added a shared security-headers snippet to the SPA entry point and deep-link
  fallback, including CSP, HSTS, frame, MIME, referrer, permissions, and robots
  controls.
- Made the installer copy the checked-in production Compose stack, aligned the
  systemd project name, and raised the start timeout.
- Made host isolation fail closed when firewall rules cannot be verified.
- Added the mobile notice/opt-in to exercise-attached RangeBox, a Close action,
  `100dvh`, and safe-area padding.
- Added a mobile drawer focus trap, skip link, contrast-safe navigation tokens,
  and a guest theme control.
- Moved RangeBoxHome onto the shared token palette and added a stop confirmation.
- Fixed the zero-evidence career recommendation and added evidence counts to
  practice affinities.
- Added CPU and disk headroom to RangeBox admission.
- Removed scope tokens from logs.
- Refreshed manual screenshots, publication labels, sizing guidance, VPN key
  guidance, and the architecture diagrams.
- Added CI regression checks for placeholder secrets, SPA security headers,
  local documentation assets, and RangeBox spawn-lock serialization, plus an
  optional deployment UI smoke workflow.
- Added a sticky Briefing / Targets / Flag / Hints jump bar to the mobile
  Active Lab.
- Added generated `Workbook/COVERAGE.md` from lab metadata and a CI check that
  it stays current.
- Configured the scheduled UI smoke workflow against the public production URL
  with a dedicated smoke account.

### Patch release
- This patch follows the 2.4.0 feature release and contains the security, mobile, capacity, and documentation remediation above.
- Verified a database restore into a temporary database and a production reboot
  with `ocr-platform.service` active and all containers healthy.

## [2.4.0] - 2026-11-08

> **Tag note:** the legacy history already contains published `v2.2.0` through
> `v2.3.2` tags. This release uses `v2.4.0` so no existing tag is moved.

### Branding
- Rebranded the user-facing platform as **SWOCTS Cyber Range** with the SWOCTS
  crest as the primary mark and title.
- Added **Powered by OpenCyberRange** attribution with the OpenCyberRange shield
  across the sidebar, login, footer, certificates, emails, PDF reports, and
  documentation.
- Updated MkDocs site names, logos, favicons, and copyright lines, plus the
  frontend title, favicon, and meta description.
- Kept internal package names, API paths, data formats, environment variables,
  and upstream attribution unchanged for compatibility and licensing.

### Learner profile and career discovery
- Split the profile into five focused tabs: **Overview**, **Skill tree**,
  **Learning record**, **Account**, and **Security & privacy**. The selected tab
  is kept in the URL.
- Added a visual **skill tree** to the Skill tree tab, built from the five Cyber
  DNA trait scores, with branch scores, evidence cards, and next steps.
- Added **Practice affinities** to Cyber DNA: positive, evidence-based role
  families for Offensive Security / Penetration Testing, Defensive Security /
  SOC, DFIR / Investigation, and Security Leadership / Education.
- An offensive-security affinity is recognised from completed web, exploitation,
  privilege-escalation, post-exploitation, and credential-attack labs, with
  supporting reconnaissance and enumeration evidence. It is framed as practice,
  not a job label, certification, or testing authorisation.
- Added development-only **career discovery profiles** and a dossier exporter.
  `seed_career_profiles.py` creates a well-versed learner, a starting learner,
  and a career-changer, then exports JSON, Markdown, and printable HTML with
  Cyber DNA, learning evidence, reflection questions, and external resources.
- Added external references for MalOps, Hack The Box Academy, PacketLabs,
  Cisco Networking Academy, and LabShock for IoT/OT training. Links are
  references only; third-party content is not copied or reproduced.

### Admin navigation
- Renamed the admin **Monitoring** tab to **Live activity** in the sidebar and
  panel heading. The tab still holds Sessions, VPN Peers, and the Activity Log,
  and `/admin?tab=monitoring` and the legacy sub-tab links are unchanged.

### RangeBox
- Moved the standalone RangeBox launcher and viewer from the student dashboard
  to its own **RangeBox** tab in the sidebar.
- The tab shows the number of deployed boxes and refreshes it immediately after
  launch or stop. A box is counted from container creation, so the meter does
  not briefly read zero while the desktop is starting.
- RangeBox status now waits for the VNC port before reporting ready, and the
  desktop retries the first connection if websockify is still starting.
- Added `websocket-client` to the backend requirements so the Level 4 RangeBox
  stress test can run, and made its pre-spawn and VNC connect steps wait for the
  desktop to accept connections.

### Mobile student shell
- Added automatic phone-width detection and a dedicated mobile shell: a compact
  top bar, an off-canvas navigation drawer, and a bottom tab bar for Home,
  Exercises, RangeBox, Courses, and Profile.
- The drawer closes on navigation, the backdrop, or Escape, and the mobile shell
  keeps page-level horizontal overflow at zero.
- The embedded RangeBox viewer is replaced on phones with a desktop-recommended
  notice and an explicit full-screen opt-in.

### Events rename
- Renamed the user-facing **Competitions** area to **Events** across the
  sidebar, list, detail, registration, profile, and manuals.
- Added canonical `/events` and `/events/:id` routes. The existing
  `/competitions` routes redirect for older bookmarks, and the API/model names
  remain unchanged for data compatibility.

### Version policy
- Adopted **one platform release number** for this tree on 2.1.4; 2.4.0 continues the same policy. Community /
  Academic, Professional, and Enterprise are edition profiles, not three
  separate version lines. See `docs/decisions/0004-single-platform-release-version.md`.
- Kept Community / Academic 1.1.3 as the supported maintenance line for existing
  single-host installs.
- Described Enterprise as a **preview profile on the current release** until the HA workstream
  ships; the separate HA repository has its own version and compatibility
  statement.

### Course workspace and feedback
- Redesigned the Academy course page around **Overview**, **Content**,
  **Feedback**, and **Achievements**. The public scoreboard is no longer
  presented; scoring data remains available to private reports.
- Added a private two-way feedback loop: students use the existing survey engine
  for a one-minute course check-in, instructors add coaching notes, and the
  summary aggregates check-ins, exercise pulse surveys, reactions, and
  coaching. Existing pulse data feeds the metrics on first load.
- Added optional exercise knowledge checks: 2–3 randomised questions per
  attempt, unlimited re-attempts, explanations and primary references, four
  benchmark achievements, and Cyber DNA evidence. Ten certification-aligned
  lab banks plus track fallbacks cover every exercise. Post-quiz ratings feed
  course satisfaction, relevance, usefulness, and ease-of-use metrics.
- Added an EXIF metadata investigation lab with a safe evidence image, GPS,
  device, author, and free-text metadata, plus a full beginner workbook.

### Host OS validation
- Certified Ubuntu 24.04 LTS for 2.4.1 after WireGuard, firewall persistence,
  KVM, restore, and the full lab matrix passed on 24.04.5.
- Fixed VPN forwarding on hosts where Docker's per-network `DOCKER-FORWARD`
  drops shadowed the `FORWARD` ACCEPT rules. The accepts now live at the top of
  `DOCKER-USER`, and duplicate copies from concurrent startup workers collapse.
- Allowed the Docker bridge pool to reach the Peer Manager on TCP/5000 so the
  backend can re-apply VPN rules on UFW-enabled hosts after a reboot.
- Added the missing `ocr-network-tap` build context and wired it into the
  installer. Capture labs no longer spawn without a tap, and the tap and GRETAP
  mirrors share one TC filter so both receive traffic.

### Dependencies and maintenance
- Applied safe patch updates within declared ranges: FastAPI 0.162.2,
  SQLAlchemy 2.1.8, Pydantic 2.14.3, psycopg 3.3.8, Vue 3.5.45, Chart.js 4.6.1,
  marked 18.1.3, Vite 8.3.6, and globals 17.14.0.
- Confirmed `npm audit` reports 0 vulnerabilities and `pip-audit` reports no known
  vulnerabilities. Upgraded the frontend majors: Vue Router 5.4.0, ESLint
  10.14.0, `@eslint/js` 10.0.1, `eslint-plugin-vue` 10.12.0, and
  `vue-eslint-parser` 10.4.2.
- Reconciled `versions.yaml` and `docs/SUPPORTED-VERSIONS.md` with the installed
  backend and frontend dependency set.

### CI and security scanning
- CodeQL skips analysis on private development mirrors, where code scanning is
  unavailable without GitHub Advanced Security. The public canonical repository
  continues to run it.
- Trivy always runs and uploads a SARIF artifact, but uploads to code scanning
  only where that feature is enabled.
- Removed new CodeQL findings from the career-profile seed and test fixtures.

### Reliability
- Fixed the instructor and admin dashboard Pulse chart on PostgreSQL. The
  `date_trunc` bucket expression is now identical in `SELECT` and `GROUP BY`,
  so PostgreSQL no longer raises a grouping error for `/api/dashboard/instructor/pulse`.
- Repaired double-encoded UTF-8 in user-facing text. The profile avatar-border
  label now shows `Solid · Blue` instead of the old double-encoded middle dot, and dashes,
  ellipses, multiplication signs, and bullets render correctly across the
  profile and admin views.

### Operations
- Added `scripts/status-dashboard.py`, a small API-based dev/prod status
  dashboard. It checks `/api/version`, `/api/setup/status`, and the SPA index,
  writes HTML/Markdown/JSON snapshots, and never logs in or reads learner data.
- Added generated deployment status snapshots under `docs/`.

### Reporting and navigation
- Restored **Reports & analytics** to the sidebar after the link was dropped in
  the Skill DNA navigation change. Administrators see it in the **Admin**
  section; instructors see it in the **Instructor** section. It opens `/reports`
  as a separate route, so the Admin tab is preserved.
- Restored the **Surveys** link for instructors and administrators. Both routes
  existed but had no visible navigation entry.
- Updated the admin guide, navigation guide, instructor report guide, README,
  and analytics documentation for the reporting entry point.
- Added reusable screen-reader-only styles and a caption for the reports table,
  so visually hidden labels stay hidden and table structure is announced by
  assistive technology.
- Report export audit records now include the export scope, and PDF exports also
  record the course count.

### Administration
- Added **Admin → Users → Import / Export Users**: portable user JSON export,
  preview-before-import, optional update of matching usernames, and optional
  avatar export.
- User imports now never overwrite an existing administrator. The signed-in
  administrator is protected by user ID and other administrators are skipped
  with a warning.
- Added **Admin → System → Backups → Restore from another system**: upload a
  plain `.sql` snapshot and restore it or stage it as a local snapshot. Uploads
  are administrator-only, extension-checked, and capped at 512 MB.

### Privacy and security
- Every data export now requires a reason of at least five characters. The
  reason, exporter, format, and scope are written to the audit log.
- Applied the reason requirement to user, activity-log, backup-download,
  learning-report, course/student/assignment-report, and exercise/stress-test
  exports. Self-service account and transcript exports record fixed purposes.
- Export responses use `Cache-Control: no-store`; administrative user exports
  embed `reason` and `exported_by` in the JSON.
- Added `docs/PRIVACY-AND-DATA-DELETION.md`, `SECURITY.md`, OWASP evidence, and
  admin-guide coverage for user migration, cross-system restore, and export
  accountability.

## [2.1.4] - 2026-11-05

### Reporting
- Added the **skill tree radar** to Learning reports. The chart maps assigned and
  completed exercises across the five Skill DNA branches: Explorer, Builder,
  Defender, Investigator, and Leader.
- Added an **All courses** view plus a per-course scope selector, with an
  accessible table fallback beside the chart.
- Extended CSV export with per-course skill-tree mixes and added a skill-tree
  coverage table to the PDF export.
- The reporting API now returns a `skill_tree` object on each course row and in
  report totals.

### Notes
- The radar describes the **mix of exercises**, not learner scores. Completed
  exercises are distinct exercises with at least one completion.
- Learner-level and cohort competency radar remain planned.

## [2.1.3] - 2026-11-05

### Learner profile
- Added **Skill DNA**: five activity-based traits (Explorer, Builder, Defender,
  Investigator, Leader), a class, a tier, and a certification alignment card on
  the profile.
- Added achievement **titles**. Unlocked titles can be equipped or cleared; the
  class title returns when no achievement title is equipped. Hidden titles stay
  secret until unlocked.
- Added the **Title collection** and the equipped-title badge on the profile.
- Added explicit course, competition, advanced-lab, and teaching signals to the
  Leader trait.
- Added the metric model in `docs/SKILL-DNA.md`.

## [2.1.2] - 2026-11-05

Maintenance release for the Professional line.

### Admin user management
- The Users table shows the last sign-in time, with a relative label and the
  exact timestamp on hover.
- Added filters for status, role, last sign-in window, and VPN registration,
  plus a sort control, result range, clear-filters action, and empty state.
- Role and account status are separate columns; the table has accessible
  headers and a stacked layout on narrow screens.

### Reliability
- Rate limiting now degrades to in-process limits when Redis is unavailable
  instead of returning HTTP 500 on login.

### Design and release
- Added the OpenCyberRange Design Tester skill for light/dark, layout, filter,
  and accessibility reviews.

## [2.1.0] - 2026-11-04

### Login experience
- The login preview shows a sample learner certificate and SWOCTS branding, with
  links to the SWOCTS website and LinkedIn page.
- The exercise like/dislike control now sits at the top of the active exercise
  instead of below the scenario and flag form.

### Admin experience
- The admin user record preview now has an account hero, learning summary,
  searchable completion evidence, active-session cards, and a clear separation
  between read-only review and destructive resets.
- The edit-user dialog now groups identity, access, and password recovery, with
  keyboard-visible focus, inline help, and mobile layouts.
- Admin password reset is a separate privileged action: the admin must
  re-authenticate, the target's sessions are revoked, a password change is
  forced, and the action is audited. The general profile update endpoint now
  rejects password changes.

### Learning and career guidance
- Each track now shows a certification pathway panel with entry, core, and
  advanced vendor certifications, role direction, and links to the Security
  Certification Roadmap, the CISO MindMap 2026, and SWOCTS resources.
- The community/academic backlog records the CISO MindMap-informed curriculum
  breadth and the in-workspace exercise brief pop-out.

### Security
- Serve a deny-all `robots.txt`, send `noindex`/`nofollow` metadata and
  `X-Robots-Tag`, and return `403` to known search and AI crawler user agents.
- Preserve an upstream `X-Forwarded-Proto` so certificate and mail links keep
  the public HTTPS scheme behind a TLS-terminating proxy.
- Document Nginx Proxy Manager WebSocket, SSE, upload, forwarded-header, and
  crawler settings in `docs/REVERSE-PROXY.md`.

### 2.x feature scope
- Reporting, learning analytics, cohort analysis, competency evidence, and
  survey insight are the active Professional feature workstreams. The five
  Professional priorities are defined in `docs/PROFESSIONAL-PRIORITIES.md`.
  Multi-host HA, SSO, multi-tenancy, LMS integration, and compliance reporting
  are Enterprise 3.0; see `docs/V2-PROGRAM-CHARTER.md`,
  `docs/V3-PARKING-LOT.md`, and `docs/V3-HA-LAB-POOL.md`.
- The OWASP Top 10 is the 2.x security baseline for the interface, data, and
  delivery process, with required tests and a documented exception process. See
  `docs/V2-SECURITY-OWASP-TOP-10.md`.

### 2.x analytics and reporting
- Learning hours: tracked time on completed exercises, with bounded session
  time for started exercises that have no completion, shown in student and
  course analytics and in the cross-course report.
- Per-exercise like/dislike feedback for learners, aggregated as likes,
  dislikes, and positive rate in course analytics and reports. Learner identities
  are not shown in the aggregate views.
- Global achievements for learning hours (1, 5, 15, and 30 hours) and sign-in
  streaks (3, 7, and 30 consecutive days).
- Cross-course report PDF export, alongside the existing CSV export.
- Optional competition event marks, validated and stored with the same image
  safety rules as sponsor logos.
- Login now records a UTC calendar-day streak without changing the
  authentication decision path.

### Carried forward from 1.1
- SMTP settings in Admin → Settings → Email, including a save-then-test flow.
- Registration email for new accounts, with separate approved and pending-approval messages. The registration form exposes it as an opt-in checkbox with transactional-email privacy language.
- Profile email preferences in Privacy and data, with PIPEDA consent withdrawal language and an auditable consent version/timestamp.

### Maintenance and fixes
- Exercise catalogue and exercise panel responsive pass: visible Completed,
  In progress, Next up, and Locked labels; a retry state when a track fails to
  load; a real keyboard toggle for level headers instead of nested buttons;
  mobile-safe action rows and active-lab headers; and reduced-motion support.
- Fresh installs now include the Redis rate-limit service, and existing
  deployments receive a Redis override during update.
- Public `GET /api/version` and a footer build-version label.
- Certificate verification now rejects non-ASCII digits, emoji, kanji, whitespace, and malformed IDs before any database lookup.
- Documentation now records the Ubuntu 22.04 baseline for 1.1, the Ubuntu 24.04 target for 2.0, the v3 multi-host lab pool plan, and the 2.x program charter.

## [1.0.0] - 2026-11-04

First supported self-hosted teaching release.

### Learning and recognition
- Certificates with selectable designs, verification links, QR codes, and SWOCTS trust marks.
- Certificate achievements are scoped to the certificate's level, course, or related competition.
- Profile course-achievement summaries grouped by course, with competition and range-wide badges separated.
- Celebration Wall avatars, profile photos, and configurable avatar border styles and colours.
- Competition-specific achievements, including participation, first blood, clean sweep, perfect event, and placements.
- Multi-sponsor competitions with Gold, Silver, and Bronze tiers, descriptions, website links, and uploaded logos.

### Teaching and administration
- Course enrollment, invite codes, scoreboards, achievements, and PDF reports.
- Exercise completion matrix redesigned as a course-by-level progress view.
- Activity-log export and audited clearing.
- User transfer, account erasure, suppression-ledger support, and personal-data export timestamps.
- Persistent database snapshots with daily automatic collection and 30-day retention.
- Snapshot heatmap now reflects actual snapshot files rather than audit events.

### Security and accessibility
- Unicode-aware password policy with control-character rejection.
- Server-side avatar and sponsor-logo validation with size and dimension limits.
- NFKC-normalised, case-insensitive course invite-code lookup.
- Accessibility improvements across progress bars, password controls, admin selects, and track rows.
- Onboarding tour shown once per user rather than on every login.

### Fixed
- Profile summary JSON serialization failure for certificate achievements.
- Celebration Wall avatars missing from the public payload.
- Personal-data panel permanently showing "Checking your last download…" with no prior export.
- Snapshots disappearing after backend container recreation.
- Certificate achievements leaking awards from unrelated exercises, courses, or events.

## [Pre-1.0]

Earlier development builds established the lab catalogue, WireGuard access, Docker lab orchestration, curriculum, authentication, MFA, privacy tooling, and deployment automation. They are superseded by 1.0.0.
