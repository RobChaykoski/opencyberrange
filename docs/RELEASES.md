# Release tags

This page maps the tags in the repository to the release they actually
represent. It exists because the history contains several naming eras.

## Release preparation checklist

Run from the repository root before tagging:

1. Bump the version in `versions.yaml`, `platform/backend/app/version.py`,
   `platform/frontend/package.json`, and the manual pages.
2. `python scripts/supply_chain.py --update`
3. `python scripts/generate-integrity-manifest.py`
4. `python scripts/supply_chain.py --update`
5. Run `python scripts/generate-integrity-manifest.py` twice and confirm the
   file hash is unchanged between runs.
6. On development, run `docker exec -i ocr-backend python - < scripts/check-tenant-isolation.py`
   and confirm `PASSED`.
7. Sign the lock, verify it, then tag.

Steps 2 and 3 order matters: the manifest copies the lock's `release` field.
Releases 5.46.0 and 5.46.1 skipped step 3, so the committed manifest still said
`5.45.0` and the CI integrity gate failed.

## Release 5.52.8

| Tag | Release | Status |
|---|---|---|
| `v5.52.8` | SWOCTS Cyber Range Release 5.52.8 | Signed annotated tag: curated DShield, Blocklist.de, abuse.ch Feodo Tracker, OffSeq Mirage, and IPsum feeds in the threat-awareness snapshot, plus the split-layout release-data sync fix. |

Deliverables: [Release 5.52.8 deliverables](RELEASE-5.52.8-DELIVERABLES.md).

## Release 5.52.7

| Tag | Release | Status |
|---|---|---|
| `v5.52.7` | SWOCTS Cyber Range Release 5.52.7 | Signed annotated tag: refreshed threat-awareness snapshots from FireHOL (DB-IP Lite 2026-11) and RansomLook, with a shorter RansomLook refresh cadence. |

Deliverables: [Release 5.52.7 deliverables](RELEASE-5.52.7-DELIVERABLES.md).

## Release 5.52.6

| Tag | Release | Status |
|---|---|---|
| `v5.52.6` | SWOCTS Cyber Range Release 5.52.6 | Signed annotated tag: backend proxy reattach on the allocated `/29`, automatic TLS `:8443` workbook origin when `wiki_origin` is empty, dynamic `frame-ancestors` for enrolled and admin course wikis, regenerated API manual, and publication-audit cleanup. |

Deliverables: [Release 5.52.6 deliverables](RELEASE-5.52.6-DELIVERABLES.md).

## Release 5.52.5

| Tag | Release | Status |
|---|---|---|
| `v5.52.5` | SWOCTS Cyber Range Release 5.52.5 | Signed annotated tag: RangeBox proxy-network allocator that survives a rapid stop/start or a second lab, subnet-derived VNC peer addresses, tests for the allocator, and the production workbook origin split on 8443. |

Deliverables: [Release 5.52.5 deliverables](RELEASE-5.52.5-DELIVERABLES.md).

## Release 5.52.4

| Tag | Release | Status |
|---|---|---|
| `v5.52.4` | SWOCTS Cyber Range Release 5.52.4 | Signed annotated tag: workbook "Open in new tab" opens synchronously instead of being treated as a blocked popup, plus the workspace regression now confirms Stop and verifies framed workbook content. |

Deliverables: [Release 5.52.4 deliverables](RELEASE-5.52.4-DELIVERABLES.md).

## Release 5.52.3

| Tag | Release | Status |
|---|---|---|
| `v5.52.3` | SWOCTS Cyber Range Release 5.52.3 | Signed annotated tag: warning-text contrast token, Exercises heading level, and the evidence from a three-role automated accessibility pass at desktop and mobile widths. |

Deliverables: [Release 5.52.3 deliverables](RELEASE-5.52.3-DELIVERABLES.md).

## Release 5.52.2

| Tag | Release | Status |
|---|---|---|
| `v5.52.2` | SWOCTS Cyber Range Release 5.52.2 | Signed annotated tag: workbook beside the desktop with the lower pane matching the RangeBox width, workbook iframe auth ordering, feedback held until completion, a single Tools menu, and column scope on admin/instructor tables. |

Deliverables: [Release 5.52.2 deliverables](RELEASE-5.52.2-DELIVERABLES.md).

## Release 5.52.1

| Tag | Release | Status |
|---|---|---|
| `v5.52.1` | SWOCTS Cyber Range Release 5.52.1 | Signed annotated tag: WireGuard route-verifier fix and peer resync, a global visible focus ring, and the accent hero/contrast treatment for administrator and instructor dashboards. Deployed to development and production on 26 November 2026; VPN verification passed for 11 clients across 217 labs. |

Deliverables: [Release 5.52.1 deliverables](RELEASE-5.52.1-DELIVERABLES.md).

## Release 5.52.0

| Tag | Release | Status |
|---|---|---|
| `v5.52.0` | SWOCTS Cyber Range Release 5.52.0 | Signed annotated tag: consistent quiz navigation and final-submission flow across exercise knowledge checks and level quizzes, shared `QuizQuestionDots` / `QuizNavigation` / `QuizSubmitPanel` components, component tests, and a new student-guide page covering both quiz types. Deployed to development and production on 25 November 2026; 217 registered labs, production wiki rebuilt, and pre/post backups recorded. |

Deliverables: [Release 5.52.0 deliverables](RELEASE-5.52.0-DELIVERABLES.md).

## Release 5.51.2

| Tag | Release | Status |
|---|---|---|
| `v5.51.2` | SWOCTS Cyber Range Release 5.51.2 | Signed annotated tag: learner UI clarity for practice-exam navigation and final submission, a searchable track-grouped analyst-answer library, theme-safe Journey & mission panels with a fuller current-mission card, and matching manual/README/SECURITY/LICENSING updates. Deployed to development and production on 25 November 2026; 217 registered labs, production wiki rebuilt, and pre/post backups recorded. |

Deliverables: [Release 5.51.2 deliverables](RELEASE-5.51.2-DELIVERABLES.md).

## Release 5.51.1

| Tag | Release | Status |
|---|---|---|
| `v5.51.1` | SWOCTS Cyber Range Release 5.51.1 | Signed annotated tag: the 5.51.0 navigation, tools, threat-map and lab release, with the tools catalogue moved from `/tools` to `/toolbox` after nginx served the static `/tools/` directory as a 403. Deployed to development and production on 25 November 2026; 217 labs registered, post-deploy backup, restore drill and restore-drift gate at `0` passed. |

Deliverables: [Release 5.51.1 deliverables](RELEASE-5.51.1-DELIVERABLES.md).

## Release 5.51.0

| Tag | Release | Status |
|---|---|---|
| `v5.51.0` | SWOCTS Cyber Range Release 5.51.0 | Signed annotated tag: regrouped learner/instructor/admin navigation, the shared `/tools` catalogue with the OWASP ZAP scan planner, an interactive privacy-safe threat map, the Arkime DET-08 lab, and the `web-11-11-zap-baseline-triage` Web lab. Development-only; superseded by 5.51.1 before production because `/tools` collided with the static tool directory. |

Deliverables: [Release 5.51.0 deliverables](RELEASE-5.51.0-DELIVERABLES.md).

## Release 5.50.1

| Tag | Release | Status |
|---|---|---|
| `v5.50.1` | SWOCTS Cyber Range Release 5.50.1 | Signed annotated tag: live FireHOL snapshot with DB-IP Lite country attribution (`469,828` entries across `148` countries), the `--require-geoip` guard, and the threat-awareness operations runbook. Deployed to development and production on 24 November 2026; restore drill and zero-drift gate passed. |

Deliverables: [Release 5.50.1 deliverables](RELEASE-5.50.1-DELIVERABLES.md).

## Release 5.50.0

| Tag | Release | Status |
|---|---|---|
| `v5.50.0` | SWOCTS Cyber Range Release 5.50.0 | Signed annotated tag: tenant-isolation audit and two-tenant pilot tooling, the competency campaign plan with production drafts, the `ocr-labd` status/stop harness, and a live RansomLook snapshot. Deployed to development and production on 24 November 2026; tenant audit, restore drill, and zero-drift gate passed. |

Deliverables: [Release 5.50.0 deliverables](RELEASE-5.50.0-DELIVERABLES.md).

## Release 5.49.0

| Tag | Release | Status |
|---|---|---|
| `v5.49.0` | SWOCTS Cyber Range Release 5.49.0 | Signed annotated tag: migration `0067_course_content_rls` scopes the six course-owned content tables to the tenant with forced RLS and the four policies, bringing the enforced set to 47 tables. Deployed to development and production on 24 November 2026; restore drill and zero-drift gate passed. |

Deliverables: [Release 5.49.0 deliverables](RELEASE-5.49.0-DELIVERABLES.md).

## Release 5.48.0

| Tag | Release | Status |
|---|---|---|
| `v5.48.0` | SWOCTS Cyber Range Release 5.48.0 | Signed annotated tag: migration `0066_tenant_baseline` moves the 20 runtime `institution_id` columns and indexes into the migration graph, the models declare the missing columns, and Alembic drift reaches **0** with the restore-drift gate defaulting to 0. Deployed to development and production on 24 November 2026; post-deploy backup, restore drill, and restore-drift gate at 0 passed. |

Deliverables: [Release 5.48.0 deliverables](RELEASE-5.48.0-DELIVERABLES.md).

## Release 5.47.0

| Tag | Release | Status |
|---|---|---|
| `v5.47.0` | SWOCTS Cyber Range Release 5.47.0 | Signed annotated tag: `ocr-labd` read-only status plus an opt-in stop, aggregated ransomware activity from RansomLook with ADR 0009, and model alignment that reduces Alembic drift from 48 to 38 operations. Deployed to development and production on 24 November 2026; post-deploy backup, restore drill, and restore-drift gate passed. |

Deliverables: [Release 5.47.0 deliverables](RELEASE-5.47.0-DELIVERABLES.md).

## Release 5.46.2

| Tag | Release | Status |
|---|---|---|
| `v5.46.2` | SWOCTS Cyber Range Release 5.46.2 | Signed annotated tag: regenerates the runtime integrity manifest for the current release and adds the release-preparation checklist. Deployed to development and production on 24 November 2026. |

Deliverables: [Release 5.46.2 deliverables](RELEASE-5.46.2-DELIVERABLES.md).

## Release 5.46.1

| Tag | Release | Status |
|---|---|---|
| `v5.46.1` | SWOCTS Cyber Range Release 5.46.1 | Signed annotated tag: threat-awareness panel alignment with the OpenCyberRange design tokens, accessible progress bars, empty/loading/error states, and dark/light/high-contrast verification. Deployed to development and production on 24 November 2026. |

Deliverables: [Release 5.46.1 deliverables](RELEASE-5.46.1-DELIVERABLES.md).

## Release 5.46.0

| Tag | Release | Status |
|---|---|---|
| `v5.46.0` | SWOCTS Cyber Range Release 5.46.0 | Signed annotated tag: the `ocr-labd` host-agent spike, the first-party aggregated Threat Awareness panel with ADR 0008, the restore-drift gate, the weekly dependency-currency report, the 25 seeded legacy contract drafts, and the `psycopg 3.3.9` / `redis 8.2.0` patch bump. Deployed to development and production on 24 November 2026. |

Deliverables: [Release 5.46.0 deliverables](RELEASE-5.46.0-DELIVERABLES.md).

## Release 5.45.0

| Tag | Release | Status |
|---|---|---|
| `v5.45.0` | SWOCTS Cyber Range Release 5.45.0 | Signed annotated tag: database schema alignment with migrations `0063`-`0065`, removal of 24 redundant `id` index declarations, the 10 missing FK indexes, WebSocket ticket table ownership, legacy Kali column removal, descending index alignment, and the Docker host-isolation ADR and Alembic drift inventory. Deployed to development and production on 24 November 2026; post-deploy backup and restore drill passed. |

Deliverables: [Release 5.45.0 deliverables](RELEASE-5.45.0-DELIVERABLES.md).

## Release 5.44.0

| Tag | Release | Status |
|---|---|---|
| `v5.44.0` | SWOCTS Cyber Range Release 5.44.0 | Signed annotated tag: shared login-failure throttling through Valkey/Redis with a bounded memory fallback, cross-tenant admin scoping regression tests, and the Alembic autogenerate guard with the baseline drift guide. Deployed to development and production on 24 November 2026; post-deploy backup and restore drill passed. |

Deliverables: [Release 5.44.0 deliverables](RELEASE-5.44.0-DELIVERABLES.md).

## Release 5.43.1

| Tag | Release | Status |
|---|---|---|
| `v5.43.1` | SWOCTS Cyber Range Release 5.43.1 | Signed annotated tag: patch that makes the in-place deploy and installer run the pinned `ocr-lab/netprobe:1.0` helper build by path with bash, and marks the build script executable. Deployed to development and production on 24 November 2026; post-deploy backup and restore drill passed. |

Deliverables: [Release 5.43.1 deliverables](RELEASE-5.43.1-DELIVERABLES.md).

## Release 5.43.0

| Tag | Release | Status |
|---|---|---|
| `v5.43.0` | SWOCTS Cyber Range Release 5.43.0 | Signed annotated tag: FastAPI 0.165.0, SQLAlchemy 2.1.9, Pydantic 2.14.4, and pydantic-settings 2.16.3, plus the pinned `ocr-lab/netprobe:1.0` helper image that removes runtime package installation from the privileged network helpers. Deployed to development and production; superseded by 5.43.1 for the helper build path. |

Deliverables: [Release 5.43.0 deliverables](RELEASE-5.43.0-DELIVERABLES.md).

## Release 5.42.0

| Tag | Release | Status |
|---|---|---|
| `v5.42.0` | SWOCTS Cyber Range Release 5.42.0 | Signed annotated tag: learner-visible competency contract status on exercises and My Evidence, the signed-review export manifest and offline gate, the workbook cookie fix, security hardening for run state, Fernet keys, and topology input, and migrations `0061` and `0062` for index hygiene. Deployed to development and production on 24 November 2026; post-deploy backup and restore drill passed. |

Deliverables: [Release 5.42.0 deliverables](RELEASE-5.42.0-DELIVERABLES.md).

## Release 5.41.0

| Tag | Release | Status |
|---|---|---|
| `v5.41.0` | SWOCTS Cyber Range Release 5.41.0 | Signed annotated tag: the instructor contract-review dashboard with sign-off and a 6/12/24-month review cycle, the competency catalogue endpoint, evidence-review analytics and decision-flow corrections, lab framing and console fixes, and migration `0060_competency_reviews`. Deployed to development and production on 24 November 2026; post-deploy backup and restore drill passed. |

Deliverables: [Release 5.41.0 deliverables](RELEASE-5.41.0-DELIVERABLES.md).

## Release 5.40.0

| Tag | Release | Status |
|---|---|---|
| `v5.40.0` | SWOCTS Cyber Range Release 5.40.0 | Signed annotated tag: Release 6 object coverage audit, quiz competency mappings, learner-visible unmeasured rule, competency review packets, and the deterministic Capstone Builder with saved plans, versioning, and approval. Includes migration `0059_capstone_plans`. Deployed to development and production on 24 November 2026; post-deploy backup and restore drill passed. |

Deliverables: [Release 5.40.0 deliverables](RELEASE-5.40.0-DELIVERABLES.md).

## Release 5.39.0

| Tag | Release | Status |
|---|---|---|
| `v5.39.0` | SWOCTS Cyber Range Release 5.39.0 | Signed annotated tag: evidence appeals, learner journeys and the eight traditions, the Cyber Legacy contribution ledger and recognition, the Living Archive, standalone certification practice, and the expanded evidence operations summary. Includes migrations `0054`-`0058` and 158 reviewed question-bank items. Deployed to development and production on 24 November 2026; post-deploy backup, restore drill, and smoke tests passed. |

Deliverables: [Release 5.39.0 deliverables](RELEASE-5.39.0-DELIVERABLES.md).

## Release 5.38.0

| Tag | Release | Status |
|---|---|---|
| `v5.38.0` | SWOCTS Cyber Range Release 5.38.0 | Signed annotated tag: Release 6 evidence ledger and review API, recency-weighted multi-path career affinity, OSINT03 canary-token lab "Noise in the Nest", curriculum-manifest reconciliation, and the fresh-install README section. Deployed to development and production. |

## Release 5.37.1

| Tag | Release | Status |
|---|---|---|
| `v5.37.1` | SWOCTS Cyber Range Release 5.37.1 | Patch: normalize lab permissions during in-place deployment and fix the runtime integrity check for unreadable lab trees. Deployed to development and production. |

## Release 5.37.0

| Tag | Release | Status |
|---|---|---|
| `v5.37.0` | SWOCTS Cyber Range Release 5.37.0 | Signed annotated tag: Admin competency quality tab, review queue and packets, versioned rubrics, the separate `health.swocts.com` monitoring stack, Authentik OIDC, email alerts, and the in-place production deploy script. Deployed to development and production. |

## Release 5.36.0

| Tag | Release | Status |
|---|---|---|
| `v5.36.0` | SWOCTS Cyber Range Release 5.36.0 | Signed annotated tag: signed-update gate, backup and monitoring hardening, lab freshness/canary, dynamic reporting periods and forecasts, admin bundle split, and i18n/API-error groundwork. |
| `v5.35.0` | SWOCTS Cyber Range Release 5.35.0 | Previous feature release (signed annotated tag): production Authentik SSO, the AI02 multi-agent capstone, the metadata/DLP context service, DFIR-13 Velociraptor, and the publication metadata audit. |
| `v5.34.0` | SWOCTS Cyber Range Release 5.34.0 | Previous feature release (signed annotated tag): the Trailline non-human identity lab and leaked `svc-trailguard-bot` token exercise |
| `v5.33.0` | SWOCTS Cyber Range Release 5.33.0 | Previous feature release (signed annotated tag): the Trailline Security & GRC universe, a reframed AI01 stream, and the agent-hijacking lab `ai-2-1` |
| `v5.32.1` | SWOCTS Cyber Range Release 5.32.1 | Previous patch release (signed annotated tag): serve the admin QR generator from a non-static API path |
| `v5.32.0` | SWOCTS Cyber Range Release 5.32.0 | Previous feature release (signed annotated tag): registration source and QR attribution, a public usage tracker, and admin lab-completion telemetry |
| `v5.31.0` | SWOCTS Cyber Range Release 5.31.0 | Previous feature release (signed annotated tag): Cyber DNA v3 learner surface (Career affinity), consent and feature states, and clearer affinity explanations |
| `v5.30.2` | SWOCTS Cyber Range Release 5.30.2 | Previous patch release (signed annotated tag): the Cyber DNA completion backfill applies the consent gate, so a revoked learner's evidence cannot be recreated |
| `v5.30.1` | SWOCTS Cyber Range Release 5.30.1 | Previous patch release (signed annotated tag): LTI launches no longer depend on the deployment-wide SSO switch |
| `v5.30.0` | SWOCTS Cyber Range Release 5.30.0 | Previous feature release (signed annotated tag): self-service password reset, pilot workspace and RangeBox fixes, a career-target switcher, the tools drawer, privacy-first account defaults with age bands, and LTI instructor-role mapping |
| `v5.29.1` | SWOCTS Cyber Range Release 5.29.1 | Previous patch release (signed annotated tag): strip the PostgreSQL 17-only `transaction_timeout` setting from plain SQL backups so restores work on the supported PostgreSQL 15 line |
| `v5.29.0` | SWOCTS Cyber Range Release 5.29.0 | Previous feature release (signed annotated tag): lab preflight and admin health action, ECharts instructor analytics, restore and ZIP upload hardening, 211-lab content refresh |
| `v5.28.6` | SWOCTS Cyber Range Release 5.28.6 | Previous patch release (signed annotated tag): accessible admin dialogs, labelled copy controls, honest dismiss/badge affordances |
| `v5.28.5` | SWOCTS Cyber Range Release 5.28.5 | Previous patch release (signed annotated tag): topology-aware lab harness, scoped `fwctl` firewall helper, network lab test fixes |
| `v5.28.4` | SWOCTS Cyber Range Release 5.28.4 | Previous patch release (signed annotated tag): correct TRITON workstation filter in the ICS lab test |
| `v5.28.3` | SWOCTS Cyber Range Release 5.28.3 | Previous patch release (signed annotated tag): startup-time settings validation, modern declarative base, BOM and tail cleanup |
| `v5.28.2` | SWOCTS Cyber Range Release 5.28.2 | Previous patch release (signed annotated tag): Pydantic models for the remaining admin request bodies |
| `v5.28.1` | SWOCTS Cyber Range Release 5.28.1 | Previous patch release (signed annotated tag): side-effect-free user listing, single-query retention counts, request models, and generic admin errors |
| `v5.28.0` | SWOCTS Cyber Range Release 5.28.0 | Previous feature release (signed annotated tag): offline ICS/OT PCAP forensics lab plus admin event-loop, audit, reauth, and restore-safety fixes |
| `v5.27.8` | SWOCTS Cyber Range Release 5.27.8 | Previous lab-readiness patch (signed annotated tag): corrected the DevFest workbook path and refreshed the lab integrity manifest |
| `v5.27.7` | SWOCTS Cyber Range Release 5.27.7 | Previous performance patch (signed annotated tag): one JWT decode per mutation, cached middleware settings, request-scoped user reuse, and per-user spawn limits |
| `v5.27.6` | SWOCTS Cyber Range Release 5.27.6 | Previous security patch (signed annotated tag): login timing/throttling hardening, fail-closed security startup, no default LDAP admin password, and opt-in socket-proxy `EXEC` |
| `v5.27.5` | SWOCTS Cyber Range Release 5.27.5 | Previous patch release (signed annotated tag): configurable `WG_SERVER_ADDRESS` for two-host WireGuard addressing and a routed gretap mirror |
| `v5.27.4` | SWOCTS Cyber Range Release 5.27.4 | Previous patch release (signed annotated tag): homepage **Take a quiz** entry point and the `next_quiz` dashboard field |
| `v5.27.3` | SWOCTS Cyber Range Release 5.27.3 | Previous performance patch (signed annotated tag): blocking-call removal, query batching, indexes, and immutable asset caching |
| `v5.27.2` | SWOCTS Cyber Range Release 5.27.2 | Previous patch release (signed annotated tag): export/download button fix and an inline export reason |
| `v5.27.1` | SWOCTS Cyber Range Release 5.27.1 | Previous patch release (signed annotated tag): NICE provisional-mapping review action in Admin > Exercises, plus dev-only training-lab tooling and evidence |
| `v5.27.0` | SWOCTS Cyber Range Release 5.27.0 | Previous feature release (signed annotated tag): provisional NICE coverage for all 210 labs, manual navigation fix, and a dev-only training ecosystem with Moodle, Authentik, NetBox, Ralph, and Fleet |
| `v5.26.0` | SWOCTS Cyber Range Release 5.26.0 | Previous feature release (signed annotated tag): course staff assignments, privacy and audit governance dashboards, and network/platform curriculum additions |
| `v5.25.0` | SWOCTS Cyber Range Release 5.25.0 | Previous feature release (signed annotated tag): report access policy, privacy labels, small-cell suppression, and network engineering curriculum scaffold |
| `v5.24.2` | SWOCTS Cyber Range Release 5.24.2 | Previous patch release (signed annotated tag): idempotent `0044` readiness migration for the production `0043 -> 0045` jump |
| `v5.24.1` | SWOCTS Cyber Range Release 5.24.1 | Previous patch release (signed annotated tag): idempotent `0045` NICE migration for startup-created tables |
| `v5.24.0` | SWOCTS Cyber Range Release 5.24.0 | Previous feature release (signed annotated tag): NICE Framework v2.2.0 ingestion, validated lab mapping picker, and IAM/VM/SOC/platform curriculum scaffolds |
| `v5.23.0` | SWOCTS Cyber Range Release 5.23.0 | Previous feature release (signed annotated tag): live SWOCTS Hub community calendar and feed hardening |
| `v5.22.0` | SWOCTS Cyber Range Release 5.22.0 | Previous feature release (signed annotated tag): instructor calibration reviews of the provisional readiness band, review coverage, agreement by band, and band-changed signals |
| `v5.21.0` | SWOCTS Cyber Range Release 5.21.0 | Previous feature release (signed annotated tag): readiness case ownership, priority, follow-up view, and a fix for admin snapshots under forced row-level security |
| `v5.20.0` | SWOCTS Cyber Range Release 5.20.0 | Previous feature release (signed annotated tag): pilot instructor readiness calibration workflow with context flags, support actions and outcomes, flag acknowledge/snooze/dismiss, lab-health review history, and a calibration view |
| `v5.19.0` | SWOCTS Cyber Range Release 5.19.0 | Previous feature release (signed annotated tag): pilot instructor readiness dashboard with a provisional CWRS support queue, on-demand capability detail, and lab health |
| `v5.18.0` | SWOCTS Cyber Range Release 5.18.0 | Previous feature release (signed annotated tag): account email notifications and templates, career-direction check, expanded question bank and collection achievements, simulated-cloud reference stack, manual/export and RangeBox fixes |
| `v5.17.7` | SWOCTS Cyber Range Release 5.17.7 | Previous patch release (signed annotated tag): routes admin course management to the working enrollment workspace and adds a Review column for competency-contract status in Admin > Exercises |
| `v5.17.6` | SWOCTS Cyber Range Release 5.17.6 | Current patch release (signed annotated tag): production settings-ticket UX for the ceiling test, workbook Analysis Questions for all 19 pathway labs, `ad_pathfinder` and `appsec_architect` completion badges, and privacy-safe manual screenshots |
| `v5.17.5` | SWOCTS Cyber Range Release 5.17.5 | Previous documentation and verification release (signed annotated tag): documentation skill, archive and category hubs, GitHub policy files, reconciled counts, password-prompt regression suite, and bounded login input |
| `v5.17.4` | SWOCTS Cyber Range Release 5.17.4 | Previous patch release (signed annotated tag): lab discovery creates missing levels so the level-11 AD and modern-appsec labs register on an existing install; UTF-8 lab reads |
| `v5.17.3` | SWOCTS Cyber Range Release 5.17.3 | Content/security release (signed annotated tag): extends forced tenant RLS to 16 legacy learner tables (25 total) and implements the 9 Active Directory and 10 modern application-security pathway labs (210 labs total) |
| `v5.17.2` | SWOCTS Cyber Range Release 5.17.2 | Previous patch release (signed annotated tag): fixes the re-authentication dialog double-`/api` path that returned 404 and blocked re-auth-gated actions; records the completed production cutover |
| `v5.17.1` | SWOCTS Cyber Range Release 5.17.1 | Previous security/configuration release (signed annotated tag): fail-closed authorization, explicit production configuration, mandatory WireGuard key encryption, opt-in Cyber DNA/GPS/portfolio defaults, lab-outcomes contract, API manual, Code of Conduct, and release-governance documents |
| `v5.17.0` | SWOCTS Cyber Range Release 5.17 | Previous feature release (signed annotated tag): admin release/update indicator, RBAC/PBAC role editing and Moves/Adds/Changes, ATT&CK Navigator, report-based DFIR pathway, open dataset registry, and OWASP API/web/agentic validation and lab plans |
| `v5.16.0` | SWOCTS Cyber Range Release 5.16 | Previous feature release (signed annotated tag): OpenWrt appliance segmentation lab, persisted learner report snapshots, checked manual publishing |
| `v5.15.0` | SWOCTS Cyber Range Release 5.15 | Previous feature release (signed annotated tag): RangeBox launch choice and stop dialog, auth states, Cyber DNA discovery, OT scan assistant and gateway lab, Python 3.13, weekly built-image scan |
| `v5.14.0` | SWOCTS Cyber Range Release 5.14 | Previous feature release (signed annotated tag): strict cohorts, certificate design consistency, documentation click fix |
| `v5.13.1` | SWOCTS Cyber Range Release 5.13.1 | Previous patch (signed annotated tag): browser signature verification and public badge CORS |
| `v5.13.0` | SWOCTS Cyber Range Release 5.13 | Previous feature release (signed annotated tag): RemnuxBox KasmVNC, export label content, event badges and badge artwork |
| `v5.12.0` | SWOCTS Cyber Range Release 5.12 | Previous feature release (signed annotated tag): KasmVNC UbuntuBox |
| `v5.11.0` | SWOCTS Cyber Range Release 5.11 | Previous feature release (signed annotated tag): KasmVNC Kali, single-pane workspace, role-aware navigation, export data labels |
| `v5.10.0` | SWOCTS Cyber Range Release 5.10 | Previous feature release (signed annotated tag): profile badge list, name sharing, issuer URL guard |
| `v5.9.1` | SWOCTS Cyber Range Release 5.9.1 | Previous patch (signed annotated tag): badge revocation UI |
| `v5.9.0` | SWOCTS Cyber Range Release 5.9 | Previous feature release (signed annotated tag): badge admin, key rotation, public viewer |
| `v5.8.1` | SWOCTS Cyber Range Release 5.8.1 | Previous patch (signed annotated tag): badge eligibility fix |
| `v5.8.0` | SWOCTS Cyber Range Release 5.8 | Previous feature release (signed annotated tag): Open Badges 3.0 level credentials |
| `v5.7.0` | SWOCTS Cyber Range Release 5.7 | Previous feature release (signed annotated tag): real host package status in About |
| `v5.6.0` | SWOCTS Cyber Range Release 5.6 | Previous feature release (signed annotated tag): cohort enforcement, student filter, platform maintenance |
| `v5.5.0` | SWOCTS Cyber Range Release 5.5 | Previous feature release (signed annotated tag): course cohorts, exercise sets, and requirements |
| `v5.4.0` | SWOCTS Cyber Range Release 5.4 | Previous feature release (signed annotated tag): instructor cross-course overview and trends |
| `v5.3.1` | SWOCTS Cyber Range Release 5.3.1 | Previous UI patch (signed annotated tag): grouped admin navigation, Academy workbooks, IA proposal |
| `v5.3.0` | SWOCTS Cyber Range Release 5.3 | Previous feature release (signed annotated tag): System metrics and graphs |
| `v5.2.2` | SWOCTS Cyber Range Release 5.2.2 | Previous security patch (signed annotated tag): egress rule persistence |
| `v5.2.1` | SWOCTS Cyber Range Release 5.2.1 | Previous security patch (signed annotated tag): default-deny lab egress |
| `v5.2.0` | SWOCTS Cyber Range Release 5.2 | Previous production feature release (signed annotated tag): interaction audit, impersonation records, backup transports |
| `v5.1.2` | SWOCTS Cyber Range Release 5.1.2 | Previous operations patch (signed annotated tag): alert hook, SMB backup path |
| `v5.1.1` | SWOCTS Cyber Range Release 5.1.1 | Previous production patch (signed annotated tag): encrypted off-host backups, monitoring, LDAP dev fix |
| `v5.1.0` | SWOCTS Cyber Range Release 5.1 | Previous production feature release (signed annotated tag): IdP settings transfer |
| `v5.0.1` | SWOCTS Cyber Range Release 5 security patch | Previous production patch (signed annotated tag): SSO hardening and workbook framing |
| `v5.0.0` | SWOCTS Cyber Range Release 5 | Release 5 baseline (signed annotated tag) |
| `v4.0.2` | SWOCTS Cyber Range Release 4 production hotfix | Previous production hotfix (signed annotated tag): RangeBox workspace tabs |
| `v4.0.1` | SWOCTS Cyber Range Release 4 hotfix | Release 4 hotfix (signed annotated tag): login reload loop |
| `v4` | SWOCTS Cyber Range Release 4 | Release 4 baseline (signed annotated tag) |
| `v3` | SWOCTS Cyber Range Release 3 | Previous supported release (signed annotated tag) |
| `v2.7.0` | SWOCTS Cyber Range 2.7.0 | Previous release; upgrade to Release 4 (unsigned tag; documented exception) |
| `v2.6.0` | SWOCTS Cyber Range 2.6.0 | Previous release; upgrade to Release 3 |
| `v2.5.5` | SWOCTS Cyber Range 2.5.5 | Previous release; upgrade to Release 3 |
| `v2.5.4` | SWOCTS Cyber Range 2.5.4 | Previous release; upgrade to Release 3 |
| `v2.5.3` | SWOCTS Cyber Range 2.5.3 | Previous release; upgrade to Release 3 |
| `v2.5.2` | SWOCTS Cyber Range 2.5.2 | Previous release; upgrade to Release 3 |
| `v2.5.1` | SWOCTS Cyber Range 2.5.1 | Previous release; upgrade to Release 3 |
| `v2.4.1` | SWOCTS Cyber Range 2.4.1 | Previous release; upgrade to Release 3 |
| `v2.4.0` | SWOCTS Cyber Range 2.4.0 | Feature release before the 2.4.1 remediation; upgrade to Release 3 |
| `v2.1.4-professional`, `v2.1.4` | Professional 2.1.4 | Previous current line; upgrade to Release 3 |
| `v1.1.x` | Community / Academic 1.1.3 | Maintenance line for existing single-host installs |

`v5.14.0` and later releases are signed with the current release key
`68A817762C831475F00DB54E775050A4C4921814`. The public key is
`docs/release-signing-key.asc`.

## Release 5.30.2 tag record

| Item | Value |
|---|---|
| Tag | `v5.30.2` (signed annotated tag) |
| Commit | `50dde8c1` |
| Signature | **Good**, key `68A817762C831475F00DB54E775050A4C4921814` |
| Released | 22 November 2026 |
| CI | CI, Quality checks, CodeQL, Trivy, Security delta review, and OpenSSF Scorecard passed |
| Deployed | Dev and production on `5.30.2`, Alembic `0050_child_privacy_defaults` |
| Cleanup | Cyber DNA backfill now applies the consent gate; 230 rows for 12 non-consenting learners were purged |

## Release 5.30.1 tag record

| Item | Value |
|---|---|
| Tag | `v5.30.1` (signed annotated tag) |
| Commit | `b9c662ff` |
| Signature | **Good**, key `68A817762C831475F00DB54E775050A4C4921814` |
| Released | 22 November 2026 |
| CI | CI, Quality checks, CodeQL, Trivy, Security delta review, and OpenSSF Scorecard passed |
| Deployed | Dev and production on `5.30.1`, Alembic `0050_child_privacy_defaults` |
| Cleanup | `sso_enabled=false`; Moodle cURL blocked hosts narrowed to the NPM JWKS host; Cyber DNA v3 backfilled and gate-verified |

## Release 5.30.0 tag record

| Item | Value |
|---|---|
| Tag | `v5.30.0` (signed annotated tag) |
| Commit | `298ef1e1` |
| Signature | **Good**, key `68A817762C831475F00DB54E775050A4C4921814` |
| Released | 22 November 2026 |
| CI | CI, Quality checks, CodeQL, Trivy, Security delta review, and OpenSSF Scorecard passed |
| Deployed | Dev and production on `5.30.0`, Alembic `0050_child_privacy_defaults` |

## Release 5.26.0 tag record

| Item | Value |
|---|---|
| Tag | `v5.26.0` (signed annotated tag) |
| Commit | `3e8eadff` |
| Signature | **Good**, key `68A817762C831475F00DB54E775050A4C4921814` |
| Released | 19 November 2026 |
| GitHub release | https://github.com/RobChaykoski/opencyberrange/releases/tag/v5.26.0 |
| CI | CI, Quality checks, CodeQL, Trivy, and OpenSSF Scorecard passed |
| Deployed | Dev and production both on `5.26.0`, Alembic `0046_course_staff` |

## Release 5.25.0 tag record

| Item | Value |
|---|---|
| Tag | `v5.25.0` (signed annotated tag) |
| Commit | `3f20f5b7` |
| Signature | **Good**, key `68A817762C831475F00DB54E775050A4C4921814` |
| Released | 19 November 2026 |
| GitHub release | https://github.com/RobChaykoski/opencyberrange/releases/tag/v5.25.0 |
| CI | CI, Quality checks, CodeQL, Trivy, and OpenSSF Scorecard passed |
| Deployed | Dev and production both on `5.25.0`, Alembic `0045_nice_framework` |

## Release 5.24.2 tag record

| Item | Value |
|---|---|
| Tag | `v5.24.2` (signed annotated tag) |
| Commit | `2825ef54` |
| Signature | **Good**, key `68A817762C831475F00DB54E775050A4C4921814` |
| Released | 19 November 2026 |
| GitHub release | https://github.com/RobChaykoski/opencyberrange/releases/tag/v5.24.2 |
| CI | CI, Quality checks, CodeQL, Trivy, and OpenSSF Scorecard passed |
| Deployed | Dev and production both on `5.24.2`, Alembic `0045_nice_framework` |

## Release 5.24.1 tag record

| Item | Value |
|---|---|
| Tag | `v5.24.1` (signed annotated tag) |
| Commit | `52ab322e` |
| Signature | **Good**, key `68A817762C831475F00DB54E775050A4C4921814` |
| Released | 19 November 2026 |
| GitHub release | https://github.com/RobChaykoski/opencyberrange/releases/tag/v5.24.1 |
| CI | CI, Quality checks, CodeQL, Trivy, and OpenSSF Scorecard passed |
| Deployed | Dev on `5.24.1`; superseded by `5.24.2` |

## Release 5.24.0 tag record

| Item | Value |
|---|---|
| Tag | `v5.24.0` (signed annotated tag) |
| Commit | `feade54b` |
| Signature | **Good**, key `68A817762C831475F00DB54E775050A4C4921814` |
| Released | 19 November 2026 |
| GitHub release | https://github.com/RobChaykoski/opencyberrange/releases/tag/v5.24.0 |
| CI | CI, Quality checks, CodeQL, Trivy, and OpenSSF Scorecard passed |
| Deployed | Superseded by `5.24.2` after migration hardening |

## Release 5.23.0 tag record

| Item | Value |
|---|---|
| Tag | `v5.23.0` (signed annotated tag) |
| Commit | `4410d915` |
| Signature | **Good**, key `68A817762C831475F00DB54E775050A4C4921814` |
| Released | 19 November 2026 |
| GitHub release | https://github.com/RobChaykoski/opencyberrange/releases/tag/v5.23.0 |
| CI | CI, Quality checks, CodeQL, Trivy, and OpenSSF Scorecard passed |
| Deployed | Superseded by `5.24.2` |

## Release 5.22.0 tag record

| Item | Value |
|---|---|
| Tag | `v5.22.0` (signed annotated tag) |
| Commit | `a172789f` |
| Signature | **Good**, key `68A817762C831475F00DB54E775050A4C4921814` |
| Released | 19 November 2026 |
| GitHub release | https://github.com/RobChaykoski/opencyberrange/releases/tag/v5.22.0 |
| CI | CI, Quality checks, CodeQL, Trivy, and OpenSSF Scorecard passed |
| Deployed | Dev and production both on `5.22.0`, Alembic `0044_readiness_case_owner` |

## Release 5.21.0 tag record

| Item | Value |
|---|---|
| Tag | `v5.21.0` (signed annotated tag) |
| Commit | `5500f30d` |
| Signature | **Good**, key `68A817762C831475F00DB54E775050A4C4921814` |
| Released | 19 November 2026 |
| GitHub release | https://github.com/RobChaykoski/opencyberrange/releases/tag/v5.21.0 |
| CI | CI, Quality checks, CodeQL, Trivy, and OpenSSF Scorecard passed |
| Deployed | Dev and production both on `5.21.0`, Alembic `0044_readiness_case_owner` |

## Release 5.20.0 tag record

| Item | Value |
|---|---|
| Tag | `v5.20.0` (signed annotated tag) |
| Commit | `0db34282` |
| Signature | **Good**, key `68A817762C831475F00DB54E775050A4C4921814` |
| Released | 19 November 2026 |
| GitHub release | https://github.com/RobChaykoski/opencyberrange/releases/tag/v5.20.0 |
| CI | CI, Quality checks, CodeQL, Trivy, and OpenSSF Scorecard passed |
| Deployed | Dev and production both on `5.20.0`, Alembic `0043_readiness_tenant_fix` |

## Release 5.19.0 tag record

| Item | Value |
|---|---|
| Tag | `v5.19.0` (signed annotated tag) |
| Commit | `21d42407` |
| Signature | **Good**, key `68A817762C831475F00DB54E775050A4C4921814` |
| Released | 19 November 2026 |
| GitHub release | https://github.com/RobChaykoski/opencyberrange/releases/tag/v5.19.0 |
| CI | CI, Quality checks, CodeQL, Trivy, and OpenSSF Scorecard passed |

## Release 5.18.0 tag record

| Item | Value |
|---|---|
| Tag | `v5.18.0` (signed annotated tag) |
| Commit | `8b8aae72` |
| Signature | **Good**, key `68A817762C831475F00DB54E775050A4C4921814` |
| Released | 19 November 2026 |
| GitHub release | https://github.com/RobChaykoski/opencyberrange/releases/tag/v5.18.0 |
| CI | CI, Quality checks, CodeQL, Trivy, and OpenSSF Scorecard passed |

Key custody: the current release key has no passphrase. The private key exists
only on the offline signing workstation, and that host's disk must stay
encrypted and the machine powered off when not signing. Do not copy the private
key to a CI runner, a server, or a backup that is stored with the releases. If
the signing host is lost, retire the key and publish a replacement rather than
reusing it.

`v5.13.1`, `v5.13.0`, `v5.12.0`, `v5.11.0`, `v5.10.0`, `v5.9.1`, `v5.9.0`, `v5.8.1`, `v5.8.0`, `v5.7.0`, `v5.6.0`, `v5.5.0`, `v5.4.0`, `v5.3.1`, `v5.3.0`, `v5.2.2`, `v5.2.1`, `v5.2.0`, `v5.1.2`, `v5.1.1`, `v5.1.0`, `v5.0.1`, `v5.0.0`, `v4.0.2`, `v4` and `v4.0.1` are signed with the previous release key
`8E81B5F3FDC5F5A62B0C258791FD6FBC4ADAFDA2`, retained for historical
verification at `docs/release-signing-key-previous.asc`. The previous key's
passphrase was unavailable, so it was retired rather than revoked. `v2.7.0`
is the last unsigned annotated tag, points at `ce7c25bb`, and remains a
documented exception from before the signing gate.

## Release tag checklist

1. Confirm `versions.yaml`, `README.md`, and `/api/version` agree on the release.
2. Confirm CI, Quality checks, CodeQL, Trivy, and the supply-chain lock are green.
3. Create a signed annotated tag on the release commit:
   `git tag -s vX.Y.Z -m "SWOCTS Cyber Range X.Y.Z"`.
4. Verify the signature locally: `git tag -v vX.Y.Z`.
5. Push the tag: `git push origin vX.Y.Z`.
6. Record the tag, commit, and signature status in this file and in the release
   notes.

## Legacy wave tags

Tags `v2.1.5` through `v2.3.2` are historical wave/build tags from before the
current single-platform release model. They are not newer than `2.7.0` and
should not be used to choose a deployment. The current release number is
recorded in `versions.yaml` and returned by `/api/version`.

## Enterprise branch tags

Tags `v3.0.0` through `v3.1.2` belong to the experimental Enterprise/HA branch
and are historical. They are **not** the supported single-host platform
release. The current platform releases are the `v5.x` tags on `main`; `v5.45.0`
is the newest.
Release 4 added OIDC, SAML, and LDAP SSO. Multi-tenancy, LMS/LTI,
the per-student accommodation engine, and weekly Jeopardy-style challenge quizzes
that feed Cyber DNA are Release 5.

## Choosing a version

1. Use `main` or the latest `v5.x` tag (currently `v5.45.0`) for new installs.
2. Keep `1.1.x` only for an existing Community / Academic maintenance install.
3. Do not deploy a `v2.2.x`, `v2.3.x`, or `v3.x` tag as the current platform.
4. Check `docs/SUPPORTED-VERSIONS.md` before changing a dependency or host OS.
