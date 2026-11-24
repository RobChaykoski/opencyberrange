# Production deployment statement

**Statement date:** 24 November 2026

This is the authoritative statement for the current production deployment. If
another document disagrees, this page and the signed tag win.

> **Public copy.** Real addresses, hostnames, and deployment accounts are
> replaced with placeholders. The private deployment inventory holds the live
> values. See [`PUBLICATION-METADATA-POLICY.md`](PUBLICATION-METADATA-POLICY.md).

## 5.47.0 deployment verification

| Check | Result |
|---|---|
| `/api/version` | `5.47.0` on production and development |
| Alembic | **`0065_legacy_kali_columns` (head)** |
| Health | `200` |
| Alembic drift | `38` operations (down from `48`) |
| Runtime manifest | release `5.47.0` |
| Threat-awareness route | `/threat-awareness` returns `200` |
| Ransomware API | `401` without a token; snapshot `sample`, `285` posts, `10` groups |
| Existing routes | `/contract-review`, `/my-evidence`, `/evidence-review` return `200` |
| SSO | Authentik OIDC provider present; `sso_enabled` is true |
| Pre-deploy backup | `~/backups/ocr-backup-20261124-201516.dump` |
| Post-deploy backup | `~/backups/ocr-backup-20261124-201850.dump` |
| Rollback images | `opencyberrange-backend:pre-v5.47.0`, `ocr-frontend:pre-v5.47.0` |
| Restore drill | **PASSED** (69 users, 215 labs, 2 courses, 64 enrollments, 134 completions, 497 achievements, 1,575 activity events) |
| Restore-drift gate | **PASSED** at `38` operations |

## 5.46.2 deployment verification

| Check | Result |
|---|---|
| `/api/version` | `5.46.2` on production and development |
| Alembic | **`0065_legacy_kali_columns` (head)** |
| Health | `200` |
| Alembic drift | `48` operations |
| Runtime integrity | `ok: true`, `215 / 215` labs, release `5.46.2` |
| Manifest release | `5.46.2` |
| Threat-awareness API | `401` without a token; `/threat-awareness` returns `200` |
| Existing routes | `/contract-review`, `/my-evidence`, `/evidence-review` return `200` |
| SSO | Authentik OIDC provider present; `sso_enabled` is true |
| Pre-deploy backup | `~/backups/ocr-backup-20261124-191033.dump` |
| Post-deploy backup | `~/backups/ocr-backup-20261124-191400.dump` |
| Rollback images | `opencyberrange-backend:pre-v5.46.2`, `ocr-frontend:pre-v5.46.2` |
| Restore drill | **PASSED** (69 users, 215 labs, 2 courses, 64 enrollments, 134 completions, 497 achievements, 1,575 activity events) |
| Restore-drift gate | **PASSED** at `48` operations |

## 5.46.1 deployment verification

| Check | Result |
|---|---|
| `/api/version` | `5.46.1` on production and development |
| Alembic | **`0065_legacy_kali_columns` (head)** |
| Health | `200` |
| Alembic drift | `48` operations |
| Threat-awareness panel | `/threat-awareness` returns `200`; `/api/threat-awareness` returns `401` without a token |
| Snapshot | `sample` mode, `17,980` reported entries across `13` countries |
| Existing routes | `/contract-review`, `/my-evidence`, `/evidence-review` return `200` |
| SSO | Authentik OIDC provider present; `sso_enabled` is true |
| Pre-deploy backup | `~/backups/ocr-backup-20261124-190258.dump` |
| Post-deploy backup | `~/backups/ocr-backup-20261124-190626.dump` |
| Rollback images | `opencyberrange-backend:pre-v5.46.1`, `ocr-frontend:pre-v5.46.1` |
| Restore drill | **PASSED** (69 users, 215 labs, 2 courses, 64 enrollments, 134 completions, 497 achievements, 1,575 activity events) |
| Restore-drift gate | **PASSED** at `48` operations |

## 5.46.0 deployment verification

| Check | Result |
|---|---|
| `/api/version` | `5.46.0` on production |
| Alembic | **`0065_legacy_kali_columns` (head)** |
| Health | `200` |
| Alembic drift | `48` operations |
| Host agent | `ocr-labd` spike installed; mutating routes return `501` |
| Pre-deploy backup | `~/backups/ocr-backup-20261124-185419.dump` |
| Rollback images | `opencyberrange-backend:pre-v5.46.0`, `ocr-frontend:pre-v5.46.0` |
| Follow-up | 5.46.1 aligns the threat-awareness panel with the design tokens |

## 5.45.0 deployment verification

| Check | Result |
|---|---|
| `/api/version` | `5.45.0` on production |
| Alembic | **`0065_legacy_kali_columns` (head)** |
| Health | `200` |
| Schema cleanup | Legacy Kali columns: `0`; missing FK indexes: `10` |
| Alembic drift | `48` operations (down from `93`) |
| Existing routes | `/contract-review`, `/my-evidence`, `/evidence-review`, `/journey`, `/impact`, `/practice` return `200` |
| SSO | Authentik OIDC provider present; `sso_enabled` is true |
| Pre-deploy backup | `~/backups/ocr-backup-20261124-181940.dump` |
| Post-deploy backup | `~/backups/ocr-backup-20261124-182316.dump` |
| Rollback images | `opencyberrange-backend:pre-v5.45.0`, `ocr-frontend:pre-v5.45.0` |
| Restore drill | **PASSED** (69 users, 215 labs, 2 courses, 64 enrollments, 134 completions, 497 achievements, 1,575 activity events) |

## 5.44.0 deployment verification

| Check | Result |
|---|---|
| `/api/version` | `5.44.0` on production and development |
| Alembic | **`0062_index_dedupe` (head)** |
| Health | `200` |
| Shared login throttle | Valkey/Redis connected; record `1-5`, retry `1`, clear `0` |
| Existing routes | `/contract-review`, `/my-evidence`, `/evidence-review`, `/journey`, `/impact`, `/practice` return `200` |
| SSO | Authentik OIDC provider present; `sso_enabled` is true |
| Pre-deploy backup | `~/backups/ocr-backup-20261124-173551.dump` |
| Post-deploy backup | `~/backups/ocr-backup-20261124-173923.dump` |
| Rollback images | `opencyberrange-backend:pre-v5.44.0`, `ocr-frontend:pre-v5.44.0` |
| Restore drill | **PASSED** (69 users, 215 labs, 2 courses, 64 enrollments, 134 completions, 497 achievements, 1,575 activity events) |

## 5.43.1 deployment verification

| Check | Result |
|---|---|
| `/api/version` | `5.43.1` on production and development |
| Alembic | **`0062_index_dedupe` (head)** |
| Health | `200` |
| Helper image | `ocr-lab/netprobe:1.0` present; `ip`, `iptables`, `bridge`, `tc`, and `conntrack` verified |
| Dependencies | FastAPI `0.165.0`, SQLAlchemy `2.1.9`, Pydantic `2.14.4`, pydantic-settings `2.16.3` |
| Existing routes | `/contract-review`, `/my-evidence`, `/evidence-review`, `/journey`, `/impact`, `/practice` return `200` |
| SSO | Authentik OIDC provider present; `sso_enabled` is true |
| Pre-deploy backup | `~/backups/ocr-backup-20261124-170800.dump` |
| Post-deploy backup | `~/backups/ocr-backup-20261124-171127.dump` |
| Rollback images | `opencyberrange-backend:pre-v5.43.1`, `ocr-frontend:pre-v5.43.1` |
| Restore drill | **PASSED** (69 users, 215 labs, 2 courses, 64 enrollments, 134 completions, 497 achievements, 1,575 activity events) |

## 5.42.0 deployment verification

| Check | Result |
|---|---|
| `/api/version` | `5.42.0` on production and development |
| Alembic | **`0062_index_dedupe` (head)**; migrations `0061`-`0062` applied |
| Health | `200` |
| Learner contract status | `/contract-review` returns `200`; `/api/competency-reviews/catalogue` is gated (`401` unauthenticated) |
| Existing routes | `/journey`, `/impact`, `/practice`, `/my-evidence`, `/evidence-review` return `200` |
| SSO | Authentik OIDC provider present; `sso_enabled` is true |
| CSP | `frame-src` includes dynamic lab targets; `frame-ancestors 'self'` |
| Database index hygiene | Duplicate exact index sets: `0`; hot indexes present: `2` |
| Cross-worker state | `/app/run-state` exists with mode `750`, owned by `ocr` |
| Host | Kernel `6.8.0-151`, Docker `29.10.0`; no reboot required |
| Pre-deploy backup | `~/backups/ocr-backup-20261124-161705.dump` |
| Post-deploy backup | `~/backups/ocr-backup-20261124-162049.dump` |
| Rollback images | `opencyberrange-backend:pre-v5.42.0`, `ocr-frontend:pre-v5.42.0` |
| Restore drill | **PASSED** (69 users, 215 labs, 2 courses, 64 enrollments, 134 completions, 497 achievements, 1,575 activity events) |

## 5.41.0 deployment verification

| Check | Result |
|---|---|
| `/api/version` | `5.41.0` on production and development |
| Alembic | **`0060_competency_reviews` (head)**; migration `0060` applied |
| Health | `200` |
| Contract review | `/contract-review` returns `200`; `/api/competency-reviews/catalogue` is gated (`401` unauthenticated) |
| Existing routes | `/journey`, `/impact`, `/practice`, `/my-evidence`, `/evidence-review` return `200` |
| SSO | Authentik OIDC provider present; `sso_enabled` is true |
| Pre-deploy backup | `~/backups/ocr-backup-20261124-060903.dump` |
| Post-deploy backup | `~/backups/ocr-backup-20261124-061257.dump` |
| Rollback images | `opencyberrange-backend:pre-v5.41.0`, `ocr-frontend:pre-v5.41.0` |
| Restore drill | **PASSED** (69 users, 215 labs, 2 courses, 64 enrollments, 134 completions, 497 achievements, 1,575 activity events) |

## 5.40.0 deployment verification

| Check | Result |
|---|---|
| `/api/version` | `5.40.0` on production and development |
| Alembic | **`0059_capstone_plans` (head)**; migration `0059` applied |
| Health | `200` |
| Capstone API | `/api/capstones/profiles` is gated (`401` unauthenticated) |
| Existing routes | `/journey`, `/impact`, `/practice`, `/my-evidence`, `/evidence-review` return `200` |
| SSO | Authentik OIDC provider present; `sso_enabled` is true |
| Pre-deploy backup | `~/backups/ocr-backup-20261124-043101.dump` |
| Post-deploy backup | `~/backups/ocr-backup-20261124-043218.dump` |
| Rollback images | `opencyberrange-backend:pre-5.40.0`, `ocr-frontend:pre-5.40.0` |
| Restore drill | **PASSED** (69 users, 215 labs, 2 courses, 64 enrollments, 134 completions, 497 achievements, 1,575 activity events) |

## 5.39.0 deployment verification

| Check | Result |
|---|---|
| `/api/version` | `5.39.0` on production and development |
| Alembic | **`0058_practice_sessions` (head)**; migrations `0054`-`0058` applied |
| Health | `200` |
| New routes | `/journey`, `/impact`, `/practice`, `/my-evidence`, `/evidence-review` return `200` |
| SSO | Authentik OIDC provider present; `sso_enabled` is true |
| Development smoke | login, journey, contribution, archive, recognition, practice, scoring, and progress passed |
| Pre-deploy backup | `~/backups/ocr-backup-20261124-033307.dump` |
| Post-deploy backup | `~/backups/ocr-backup-20261124-033536.dump` |
| Rollback images | `opencyberrange-backend:pre-5.39.0`, `ocr-frontend:pre-5.39.0` |
| Restore drill | **PASSED** (69 users, 215 labs, 2 courses, 64 enrollments, 134 completions, 497 achievements, 1,575 activity events) |

## Release identity

| Item | Value |
|---|---|
| Edition | **Community / Academic** (`lite` entitlement, single-host) |
| Release | **5.45.0** |
| Signed tag | **`v5.45.0`** |
| Runtime code commit | `a50305fb` (signed tag `v5.45.0`) |
| Previous release | `5.44.0` (signed tag `v5.44.0` at `47146529`) |
| Alembic revision | **`0065_legacy_kali_columns`** |
| Development host | `<dev-host-ip>` |
| Production host | `<prod-host-ip>` / `https://<platform-host>` |
| Repository | `RobChaykoski/opencyberrange` (`main`) |
| Pre-5.45.0 backup | `~/backups/ocr-backup-20261124-181940.dump` |
| Post-5.45.0 backup | `~/backups/ocr-backup-20261124-182316.dump` |
| Pre-5.44.0 backup | `~/backups/ocr-backup-20261124-173551.dump` |
| Post-5.44.0 backup | `~/backups/ocr-backup-20261124-173923.dump` |
| Pre-5.43.1 backup | `~/backups/ocr-backup-20261124-170800.dump` |
| Post-5.43.1 backup | `~/backups/ocr-backup-20261124-171127.dump` |
| Pre-5.42.0 backup | `~/backups/ocr-backup-20261124-161705.dump` |
| Post-5.42.0 backup | `~/backups/ocr-backup-20261124-162049.dump` |
| Pre-5.41.0 backup | `~/backups/ocr-backup-20261124-060903.dump` |
| Post-5.41.0 backup | `~/backups/ocr-backup-20261124-061257.dump` |
| Pre-5.40.0 backup | `~/backups/ocr-backup-20261124-043101.dump` |
| Post-5.40.0 backup | `~/backups/ocr-backup-20261124-043218.dump` |
| Pre-5.39.0 backup | `~/backups/ocr-backup-20261124-033307.dump` |
| Post-5.39.0 backup | `~/backups/ocr-backup-20261124-033536.dump` |
| Pre-5.30.2 backup | `~/backups/ocr-backup-20261123-004045.dump` |
| Pre-5.30.1 backup | `~/backups/ocr-backup-20261122-194312.dump` |
| Pre-5.30.0 backup | `~/backups/ocr-backup-20261122-191455.dump` |
| Pre-5.29.1 backup | `~/backups/ocr-backup-20261121-065211.dump` |
| 5.29.0 pre-deploy backup | `~/backups/ocr-backup-20261121-064246.dump` |
| Pre-cutover backup | `~/backups/ocr-backup-20261116-181526.dump` |
| Post-cutover backup | `~/backups/ocr-backup-20261116-192307.dump` |
| 5.17.5 backup | `~/backups/ocr-backup-20261116-223835.dump` |
| Final backup (post-cleanup) | `~/backups/ocr-backup-20261117-012455.dump` |
| 5.17.6 backup | `~/backups/ocr-backup-20261117-025053.dump` |
| 5.17.7 backup | `~/backups/ocr-backup-20261117-035821.dump` |
| 19 November deploy backup | `~/backups/ocr-backup-20261119-024418.dump` |
| 5.19.0 backup | `~/backups/ocr-backup-20261119-034307.dump` |
| 5.20.0 backup | `~/backups/ocr-backup-20261119-042354.dump` |
| 5.21.0 backup | `~/backups/ocr-backup-20261119-045654.dump` |
| 5.22.0 backup | `~/backups/ocr-backup-20261119-051707.dump` |
| 5.24.2 backup | `~/backups/ocr-backup-20261119-062853.dump` |
| 5.25.0 backup | `~/backups/ocr-backup-20261119-065728.dump` |
| 5.26.0 backup | `~/backups/ocr-backup-20261119-072711.dump` |
| 5.27.0 backup | `~/backups/ocr-backup-20261119-083401.dump` |
| 5.27.1 backup | `~/backups/ocr-backup-20261119-194808.dump` |
| 5.27.2 backup | `~/backups/ocr-backup-20261119-201613.dump` |
| 5.27.3 backup | `~/backups/ocr-backup-20261119-205049.dump` |
| 5.27.4 backup | `~/backups/ocr-backup-20261120-003040.dump` |
| 5.27.5 backup | `~/backups/ocr-backup-20261120-010356.dump` |
| 5.27.6 backup | `~/backups/ocr-backup-20261120-011049.dump` |
| 5.27.7 backup | `~/backups/ocr-backup-20261120-011640.dump` |
| 5.28.0 backup | `~/backups/ocr-backup-20261120-014044.dump` |
| 5.28.1 backup | `~/backups/ocr-backup-20261120-014655.dump` |
| 5.28.2 backup | `~/backups/ocr-backup-20261120-015031.dump` |
| 5.28.3 backup | `~/backups/ocr-backup-20261120-015521.dump` |
| 5.28.4 backup | `~/backups/ocr-backup-20261120-020748.dump` |
| 5.28.5 backup | `~/backups/ocr-backup-20261120-025933.dump` |
| 5.28.6 backup | `~/backups/ocr-backup-20261120-033403.dump` |
| Restore drills | **PASSED** (pre-cutover through 5.39.0) |

## 5.30.1 deployment verification

Patch release: the LTI ticket exchange no longer depends on the deployment-wide
SSO switch, so production now runs with `sso_enabled=false`. Deployed on
22 November 2026 to development and production.

| Check | Result |
|---|---|
| CI, Quality checks, CodeQL, Trivy, Security delta review, and OpenSSF Scorecard | **passed** |
| `/api/version` | `5.30.1` on production and development |
| Backend and frontend health | **healthy** |
| Alembic | **`0050_child_privacy_defaults` (head)**; no new migration |
| Registered labs | **211** |
| `deployment_mode` | **`production`** |
| SSO switch | **`sso_enabled=false`**; `/api/auth/sso/providers` returns an empty provider list |
| LTI JWKS | **200** |
| Moodle cURL blocked hosts | **Narrowed** to the default ranges plus only `<npm-host-ip>` in `172.16.0.0/12`; JWKS fetch through Moodle's cURL wrapper **200**; `<prod-host-ip>` and `10.0.0.1` rejected |
| Pre-deploy backup | `~/backups/ocr-backup-20261122-194312.dump` |
| Restore drill | **PASSED**, same counts as 5.30.0 (67 users, 211 labs, 2 courses, 64 enrollments, 134 completions, 497 achievements, 1,567 activity events) |
| Rollback images | `ocr-backend:pre-5.30.1`, `ocr-frontend:pre-5.30.1` |

A full interactive Moodle launch was not repeated after the switch change. The
exchange endpoint is covered by `tests/test_sso_gate.py`, which proves an
already-issued ticket is accepted with `sso_enabled=false`; provider login
endpoints still reject new SSO logins. The JWKS path Moodle needs was exercised
through Moodle's own cURL wrapper after the blocked-host narrowing and returned
`200`. The pre-change blocked-host value is kept at
`~/moodle-prod/curlsecurityblockedhosts.pre-narrow.txt`.

The Cyber DNA v3 backfill run after this deployment initially bypassed the
consent gate. 5.30.2 fixes the adapter and records the purge of the rows
belonging to learners without granted consent; see the 5.30.2 section.

## 5.30.2 deployment verification

Patch release: the Cyber DNA completion backfill applies the same consent gate
as the live completion path. Deployed on 22 November 2026 (23 November UTC).

| Check | Result |
|---|---|
| CI, Quality checks, CodeQL, Trivy, Security delta review, and OpenSSF Scorecard | **passed** |
| `/api/version` | `5.30.2` on production and development |
| Backend and frontend health | **healthy** |
| Alembic | **`0050_child_privacy_defaults` (head)**; no new migration |
| Consent purge | **230 rows removed** for 12 learners without granted consent |
| Remaining evidence | **44 rows** for 3 consenting learners (13, 1, 194), 11 activities, 3 domains |
| Backfill re-run | **0 new rows**, 117 completions blocked by consent, 3 consenting learners |
| Affinity gate | **not met** by any consenting learner yet (learner 13: 38 observations, 3 domains, 11 activities) |
| HTTP consent/RBAC | consenting student: four `/api/dna/v3/*` reads **200**, `available: false` (1/30 labs, 2/3 domains, 3/100 observations); revoked learner: **403 `ConsentRequired`** |
| Pre-deploy backup | `~/backups/ocr-backup-20261123-004045.dump` |
| Restore drill | **PASSED** (67 users, 211 labs, 2 courses, 64 enrollments, 134 completions, 497 achievements, 1,567 activity events) |
| Rollback images | `opencyberrange-backend:pre-5.30.2`, `ocr-frontend:pre-5.30.2` (created before the build) |

## 5.30.0 deployment verification

Post-pilot feature release: self-service password reset, pilot workspace and
RangeBox fixes, workbook cards that open the learner's current exercise, the
career-target switcher, the sidebar tools drawer, privacy-first account
defaults with age bands, and LTI instructor-role mapping. Deployed on
22 November 2026 to development and production.

| Check | Result |
|---|---|
| CI, Quality checks, CodeQL, Trivy, Security delta review, and OpenSSF Scorecard | **passed** |
| `/api/version` | `5.30.0` on production and development |
| Backend and frontend health | **healthy** |
| Alembic | **`0050_child_privacy_defaults` (head)**; no new migration |
| Registered labs | **211** |
| `deployment_mode` | **`production`** |
| Workbook origin (8443) | **200** |
| Pre-deploy backup | `~/backups/ocr-backup-20261122-191455.dump`, SHA-256 **OK** |
| Restore drill | **PASSED**, `psql` exit 0 |
| Restored counts | 67 users, 211 labs, 2 courses, 64 enrollments, 134 completions, 497 achievements, 1,567 activity events |
| Rollback images | `ocr-backend:5.30.0`, `ocr-frontend:5.30.0`; `pre-5.29.1` tags retained |

The local image store had already discarded the images used by the running
containers (unreferenced images are garbage-collected under the containerd
store), so new `pre-5.30.0` rollback tags could not be created from them.
Rollback is by checking out `f3caa331` and rebuilding; the 5.30.0 release commit
changes only version metadata, the About inventory, generated documentation, and
the supply-chain lock relative to that tree. `scripts/tag-release-images.sh`
now tags the running images before a build; it is part of the deployment
runbook.

## 5.29.1 deployment verification

Lab preflight, ECharts instructor analytics, restore/ZIP hardening, the
211-lab content refresh, and the PostgreSQL 15 backup compatibility hotfix.
Deployed on 21 November 2026.

| Check | Result |
|---|---|
| CI, Quality checks, CodeQL, Trivy, and Security delta review | **passed** |
| `/api/version` | `5.29.1` on production |
| Backend and frontend health | **healthy** |
| Alembic | **`0050_child_privacy_defaults` (head)** |
| Registered labs | **211** |
| `deployment_mode` | **`production`** |
| Runtime / migrator roles | `ocr_runtime` / `ocr_migrator` (no superuser warning) |
| ECharts assets | `echartsTheme` and `CourseAnalytics` chunks served |
| Pre-deploy backup | `~/backups/ocr-backup-20261121-065211.dump` |
| Application backup | `ocr_backup_20261121_065350.sql` |
| PG17-only setting | **absent** from the new application backup |
| Restore drill | **PASSED**, `psql` exit 0 |
| Restored counts | 50 users, 211 labs, 125 completions, 476 achievements, 1,409 activity events |
| Rollback tags | `ocr-backend:pre-5.29.1`, `ocr-frontend:pre-5.29.1` |

The 5.29.0 deploy on `cb2f7278` was healthy and served 5.29.0, but its restore
drill exposed the PostgreSQL 17 client setting described in the 5.29.1
changelog. 5.29.1 replaces it before the production statement was finalised.

## 5.28.6 deployment verification

Admin signifier and dialog fixes, deployed on 20 November 2026.

| Check | Result |
|---|---|
| `/api/version` | `5.28.6` on prod and dev |
| Frontend unit tests | 10 files, 20 tests **passed** |
| ESLint on changed files | 0 errors |
| Production build | **succeeded** |
| Deployed bundle | `ocr-dialog-title` present in the served `index` chunk on both hosts |
| `verify-lab-builds.sh` | **0 errors** on prod and dev |
| Security delta review | **PASS** |

No schema change. Backup `~/backups/ocr-backup-20261120-033403.dump`; restore
drill passed.

## 5.28.5 deployment verification

Network-lab harness and topology fixes, deployed on 20 November 2026.

| Check | Result |
|---|---|
| `/api/version` | `5.28.5` on prod and dev |
| Offline harness, `network-12-1` … `network-12-6` | **6/6 PASS** (build, start, health, isolation, solve twice, flag, teardown) |
| `lab_harness.py --validate-all` | 211 manifests valid |
| `generate-lab-manifests.py --check` | current (211 labs, includes the previously missing ICS manifest) |
| `validate-lab.py` on the changed labs | OK |
| `security-delta-review.py` | **PASS** |
| `verify-lab-builds.sh` | **0 errors** on prod and dev |
| Workbook wiki republished | `fwctl` chapter live on prod and dev |

No schema change. Backup `~/backups/ocr-backup-20261120-025933.dump`; restore
drill passed. Deployed with `docker build` of `ocr-lab/topology-node` and the
`ocr-wiki-builder` on both hosts.

## 5.28.4 deployment verification

Clean-build test for the ICS lab, performed on 20 November 2026.

| Check | Result |
|---|---|
| No-cache prebuild | **55 s**; analyst 487 MB, guide 97.5 MB |
| SSH to analyst | connected |
| Guide | title served; 17 challenges |
| Evidence | present |
| tshark | 3.6.2 |
| TRITON workstation | `192.168.1.88` (ephemeral source port) |
| TriStation frames | `896` |
| Flag | `<flag>` |
| `verify-lab-builds.sh` | **0 errors** on dev and prod |

No schema change. Backup `~/backups/ocr-backup-20261120-020748.dump`; restore
drill passed.

## 5.28.3 deployment verification

Deployed on 20 November 2026 to development and production.

| Check | Development | Production |
|---|---|---|
| `/api/version` | `5.28.3` | `5.28.3` |
| Startup validation | `validate_settings()` ran at lifespan start | same |
| Labs registered | 211 | 211 |
| `verify-lab-builds.sh` | **0 errors** | **0 errors** |

No schema change. Backup `~/backups/ocr-backup-20261120-015521.dump`; restore
drill passed.

## 5.28.2 deployment verification

Deployed on 20 November 2026 to development and production.

| Check | Development | Production |
|---|---|---|
| `/api/version` | `5.28.2` | `5.28.2` |
| Labs registered | 211 | 211 |
| Admin request bodies | Pydantic models for restore, bulk toggle, compose, impersonation launch, stress start/cancel | same |
| `verify-lab-builds.sh` | standby prebuild running | **0 errors** |

No schema change. Backup `~/backups/ocr-backup-20261120-015031.dump`; restore
drill passed.

## 5.28.1 deployment verification

Deployed on 20 November 2026 to development and production.

| Check | Development | Production |
|---|---|---|
| `/api/version` | `5.28.1` | `5.28.1` |
| Labs registered | 211 | 211 |
| Retention counts | course 1: 6/42/37/95/0/2/61; course 2: zeros | same query |
| `GET /admin/users` side effects | none (Peer Manager sync removed) | same |
| `verify-lab-builds.sh` | standby prebuild running | **0 errors** |
| Public entry | — | `200` |

No schema change. Backup `~/backups/ocr-backup-20261120-014655.dump`; restore
drill passed with 211 labs, 46 enrolments, 124 completions, 465 achievements,
and 1,386 activity events.

## 5.28.0 deployment verification

Deployed on 20 November 2026 to development and production.

| Check | Development | Production |
|---|---|---|
| `/api/version` | `5.28.0` | `5.28.0` |
| Labs registered | 211 | 211 |
| ICS lab | `ot-3-1-ics-pcap-forensics`, OT level 3, public | same |
| `verify-lab-builds.sh` | standby prebuild running | **0 errors** (211 labs) |
| Public entry | — | `200` |

The new lab carries 17 guided challenges over 22 MB of licensed captures
(TRITON/TRISIS BSD-3-Clause, Industroyer2 CC BY 4.0, GOOSE FDI CC BY 4.0,
CISA ICSNPP BSD-3-Clause). Its analyst image was verified over SSH with
`tshark` returning the 896 TriStation frames, and the guide serves 17
challenges.

The standby prebuild continues to close the remaining lab-image gap; run
`bash scripts/verify-lab-builds.sh` on `.44` when it completes.

## 5.27.7 deployment verification

Deployed on 20 November 2026 to development and production.

| Check | Development | Production |
|---|---|---|
| `/api/version` | `5.27.7` | `5.27.7` |
| Alembic | `0048_performance_indexes` (head) | `0048_performance_indexes` (head) |
| Authenticated smoke | login → `/api/auth/me` `200` → mutation `404` | same code path |
| Mutating request decode | 1 signature decode + 1 revocation check | same |
| Spawn limits | 10/minute per user (IP fallback) | same |
| Public entry | — | `200` |

No schema change. Backup `~/backups/ocr-backup-20261120-011640.dump`; restore
drill passed with 67 users, 210 labs, 2 courses, 46 enrolments, 124
completions, 465 achievements, and 1,386 activity events.

## 5.27.6 deployment verification

Deployed on 20 November 2026 to development and production.

| Check | Development | Production |
|---|---|---|
| `/api/version` | `5.27.6` | `5.27.6` |
| Alembic | `0048_performance_indexes` (head) | `0048_performance_indexes` (head) |
| Unknown-user login | 5 × `401`, then `429` with `Retry-After: 1` | same code path |
| Production startup guards | — | completed; RLS, invariants, RBAC, ledger all installed |
| Socket proxy `EXEC` | `1` (explicit) | `1` (explicit) |
| Public entry | — | `200` |

No schema change. Backup `~/backups/ocr-backup-20261120-011049.dump`; restore
drill passed with 67 users, 210 labs, 2 courses, 46 enrolments, 124
completions, 465 achievements, and 1,386 activity events.

## 5.27.5 deployment verification

Deployed on 20 November 2026 to development and production.

| Check | Development | Production |
|---|---|---|
| `/api/version` | `5.27.5` | `5.27.5` |
| Alembic | `0048_performance_indexes` (head) | `0048_performance_indexes` (head) |
| `WG_SERVER_ADDRESS` | `10.1.0.1` | `10.0.0.1` |
| `wg0` address | `10.1.0.1/24` | `10.0.0.1/24` |
| Client `AllowedIPs` | lab `/24` + `10.1.0.1/32` | lab `/24` + `10.0.0.1/32` |
| Public entry | — | `200` |

No schema change. Backup `~/backups/ocr-backup-20261120-010356.dump`; restore
drill passed with 67 users, 210 labs, 2 courses, 46 enrolments, 124
completions, 465 achievements, and 1,386 activity events.

Existing downloaded VPN configs must be re-downloaded to pick up the server
host route; the dev configs also change to the `10.1.0.1` server address.

## 5.27.4 deployment verification

Deployed on 20 November 2026 to development and production.

| Check | Development | Production |
|---|---|---|
| `/api/version` | `5.27.4` | `5.27.4` |
| Alembic | `0048_performance_indexes` (head) | `0048_performance_indexes` (head) |
| `next_quiz` in dashboard payload | present | present |
| Built bundle contains **Take a quiz** | yes | yes |
| Public entry `https://<platform-host>` | — | `200` |
| Redis rate-limit store | replica of production | `NOAUTH` without password |

No schema change. The backup was taken immediately after the deploy and the
restore drill passed with 67 users, 210 labs, 2 courses, 46 enrolments, 124
completions, 465 achievements, and 1,386 activity events.

## 5.27.3 deployment verification

Deployed on 19 November 2026 to development and production.

| Check | Development | Production |
|---|---|---|
| `/api/version` | `5.27.3` | `5.27.3` |
| Alembic | `0048_performance_indexes` (head) | `0048_performance_indexes` (head) |
| Performance indexes | 5 present | 5 present |
| Build asset | `index-Da4XZRrW.js` | `index-Da4XZRrW.js` |
| Asset cache | `public, max-age=31536000, immutable` | same |

Warm dev measurements before/after the change: `/api/labs` 77 ms → 45 ms,
student dashboard 99 ms → 77 ms, `/api/auth/me` remains around 28 ms without a
Peer Manager round-trip.

The pre-deploy production backup is
`~/backups/ocr-backup-20261119-205049.dump` (2.4 MB, 1,700 objects). The restore
drill passed with 67 users, 210 labs, 46 enrolments, 124 completions, 465
achievements, and 1,386 activity events.

## 5.27.2 deployment verification

Deployed on 19 November 2026 to development and production.

| Check | Development | Production |
|---|---|---|
| `/api/version` | `5.27.2` | `5.27.2` |
| Alembic | `0047_lab_nice_metadata` (head) | `0047_lab_nice_metadata` (head) |
| Build asset | `index-ddrlmI9g.js` | `index-ddrlmI9g.js` |
| Export fix | shared download helper present | shared download helper present |

The pre-deploy production backup is
`~/backups/ocr-backup-20261119-201613.dump` (2.4 MB, 1,700 objects). The restore
drill passed with 68 users, 210 labs, 47 enrolments, 124 completions, 465
achievements, and 1,383 activity events.

## 5.27.1 deployment verification

Deployed on 19 November 2026 to development and production.

| Check | Development | Production |
|---|---|---|
| `/api/version` | `5.27.1` | `5.27.1` |
| Alembic | `0047_lab_nice_metadata` (head) | `0047_lab_nice_metadata` (head) |
| NICE review endpoint | present (`401` unauthenticated) | present (`401` unauthenticated) |
| NICE lab metadata rows | 210 | 210 |
| Manual API reference | includes `POST /api/nice/labs/{lab_id}/review` | includes the same endpoint |
| Build asset | `index-fNwqPTTY.js` | `index-fNwqPTTY.js` |
| Training-stack containers | expected dev stack | none |

The pre-deploy production backup is
`~/backups/ocr-backup-20261119-194808.dump` (2.4 MB, 1,700 objects). The restore
drill passed with 68 users, 210 labs, 47 enrolments, 124 completions, 465
achievements, and 1,383 activity events.

## 5.27.0 deployment verification

Deployed on 19 November 2026 to development and production.

| Check | Development | Production |
|---|---|---|
| `/api/version` | `5.27.0` | `5.27.0` |
| Alembic | `0047_lab_nice_metadata` (head) | `0047_lab_nice_metadata` (head) |
| NICE lab metadata rows | 210 | 210 |
| NICE lab mappings | 2,484 | 2,484 |
| Manual stylesheet | 18,073 bytes | 18,073 bytes |
| Build asset | `index-DLCEIH0n.js` | `index-DLCEIH0n.js` |

The pre-deploy production backup is
`~/backups/ocr-backup-20261119-083401.dump` (2.3 MB, 1,694 objects).

## Production cutover: COMPLETE

The one-way production cutover was executed on **16 November 2026 at
19:21:54 UTC** by the `swocts` administrator.

| Item | Value |
|---|---|
| Change ticket | `123456` |
| Approver | Robert Chaykoski |
| Actor | `swocts` |
| Cutover record | `production_cutovers` id 1, `password_confirmed=true` |
| Evidence hash | `4f76c44efa7a30f70cb098e8da333013ce1aca79db5aee30a53bc78329afcfdf` |
| Ticket hash (SHA-256 of `123456`) | `8d969eef6ecad3c29a3a629280e686cf0c3f5d5a86aff3ca12020c923adc6c92` |
| Security event | `production.cutover` #395 (critical, success) |
| Audit action | `PRODUCTION_CUTOVER` |

Post-cutover platform settings:

| Setting | Value |
|---|---|
| `deployment_mode` | **`production`** |
| `data_collection_mode` | **`production`** |
| `settings_change_ticket_mode` | **`required`** |

Settings changes now require a ticket and are recorded as revertible change
sets. The cutover cannot be reversed from the application.

## Test-account cleanup

Three unambiguous QA accounts were erased through the product erasure path
before the cutover. Real users and learner data were preserved.

| Account | Role | Result |
|---|---|---|
| `qa_tester_1114` | student | erased |
| `qa_tester_1115` | student | erased |
| `qa_release_check_20261116` | admin | erased |

- Accounts: **50 → 47**; administrators: **2 → 1** (`swocts`).
- Suppression ledger: 3 `committed` entries with hashed identities.
- Audit: 3 × `USER_DELETED` under ticket `123456` / approver Robert Chaykoski.
- Security event: `production.test_account_cleanup` #366.

Two accounts were deliberately retained by the operator: `smoke_tester`
(`smoke@swocts.com`, deployment smoke account) and `tester`
(`sgcloudca@gmail.com`, ambiguous one-off). They are not real-user data loss
risks, but they are not production identities; remove `smoke_tester` in
Admin → Users when convenient.

## Deployment state

- Backend: healthy, `/health` returns `200`.
- Frontend: healthy.
- Database and Valkey: healthy.
- `/api/version` returns `5.17.5`.
- Registered labs: **210**.
- Admin **System → Health → Release status** reports **Up to date** against
  `v5.17.5`.
- `ENVIRONMENT=production`.
- `OCR_DEPLOYMENT_MODE=production`.
- `OCR_AUTHZ_STRICT=true`.
- WireGuard encryption key is set.
- Cyber DNA, Cyber GPS, and portfolio consent defaults are **false** (opt-in).
- API docs remain disabled (`enable_api_docs=false`).

## 5.17.2 fix

`ReauthDialog.vue` posted to `/api/auth/reauth` through a client whose base URL
is already `/api`, so every re-authentication attempt hit
`/api/api/auth/reauth` and returned `404 Not Found`. This blocked the cutover's
re-auth challenge and every other re-authentication-gated action. 5.17.2 posts
to `/auth/reauth` and the regression test asserts the corrected path.

## 5.17.7 additions

- Fixed admin course management: **Manage students** now opens the Instructor
  Panel course workspace at the selected course, where the working Enroll
  Students flow lives. **View course page** opens the learner-facing page.
- Added a **Review** column to Admin > Exercises for the competency-contract
  state, with content version, review date, and flag presence in the tooltip.
- Verified with 8/8 Playwright checks from the admin path and 38/38 general UI
  smoke checks.
- Production data after the load test: the **40 `stresstest_*` accounts** were
  erased through the normal erasure path on 2026-11-17 (suppression ledger
  updated), leaving **47 accounts** (44 students, 2 instructors, 1 admin),
  **2 courses**, and **46 enrollments**.

### Saturday readiness tuning (2026-11-17)

- PostgreSQL now runs with `shared_buffers=2GB`, `effective_cache_size=24GB`,
  `work_mem=32MB`, `maintenance_work_mem=1GB`, `max_connections=200`, and
  `random_page_cost=1.1`. The running container had been using stock defaults
  because the compose override replaces the tuned `postgres` command.
- Backend scaled from **1 to 4 uvicorn workers**; the 20+20 pool keeps the
  ceiling at 160 connections under the new 200 limit. Rate-limit counters are
  shared through Valkey, so limits stay global across workers.
- A fresh pre-change backup `ocr-backup-20261117-041146.dump` was taken and
  synced off-host before the cleanup and restart.
- Prebuilt the **22 missing lab images** (3 Identity, 10 Web-11 application
  security, and 9 Windows-11 Active Directory) so a first spawn does not wait
  for an image build.
- Login and registration limits now follow the live competition window
  automatically: **40/minute** login and **20/minute** registration per IP from
  `EVENT_BURST_BUFFER_MINUTES` (default 30) before the DevFest event until the
  same margin after it, with the strict limits outside it. The check is cached
  per worker and falls back to strict limits if the database read fails.
- The RangeBox live cap is pinned to **15** (the measured ceiling) for the
  mixed-desktop event. Clear `MAX_CONCURRENT_RANGEBOXES` to return to the 75%
  setting.

## 5.17.6 additions

- Production settings UX: **Run ceiling test** now checks the ticket and reason
  before the confirmation prompt, shows an inline hint beside the RangeBox
  capacity card, highlights Production change control, and focuses the missing
  field. Verified with 16/16 Playwright checks on the production presentation.
- Workbook: added the required Analysis Questions to all 19 level-11 pathway
  pages. Coverage remains **201 of 210**.
- Achievements: `ad_pathfinder` (all nine AD exercises) and
  `appsec_architect` (all ten AppSec exercises) are live global completion
  badges, visible in the catalogue and manual.
- Manual: 53 screenshots refreshed on dev with Privacy Mode explicitly on for
  admin and instructor views; populated pending and locked demo states.
- Counts clarified: **210 registered labs** = **170 public** + **40
  course-scoped**.
- Removed the revoked `Test-api` service identity and its service credential
  (ticket `123456`); users returned to **47**.
- Validation: 909 backend tests, frontend lint/tests/build, 38/38 UI smoke
  checks, link/doc-asset/workbook/lab/quiz/security checks pass.

### Post-release content update

- Commit `e9b2c602` adds original study material for browser-side trust
  boundaries (XSS/CSRF), API security, and IoT/embedded security, plus seven
  original Web track knowledge-check questions. External platforms remain
  references only; no scenarios, questions, answers, flags, screenshots, or
  assets were copied.
- This is a content and documentation update on the 5.17.6 runtime; it does not
  change the schema, migrations, or application code.

## 5.17.5 additions

- Documentation cleanup: documentation skill, docs index, category hubs,
  archive, CODEOWNERS, SUPPORT, and PRIVACY. Current-state counts reconciled to
  **210 labs, 13 tracks, 25 tenant-RLS tables**.
- Password-prompt verification: login, re-authentication, change-password,
  account deletion, admin reset, MFA disable, and the cutover gate accept the
  correct password and reject wrong, oversized, control-character, and
  injection-shaped input.
- Live deployed check on development: correct login, re-authentication, and
  change-password returned `200`; wrong, oversized, and newline inputs returned
  `401`; the temporary verification account was removed.
- Bounded, log-safe login input and `maxlength` on password prompts.
- Manual screenshots audited for synthetic data; a refresh to the current build
  is pending demo credentials.
- Workbook: `CH_WIN11_AD_Pathway` and `CH_WEB11_AppSec_Pathway` added, raising
  coverage to **201 of 210** labs; the workbook wiki was rebuilt and the new
  chapters are served. Each of the 19 pages includes the required Analysis
  Questions.
- Pathway achievements: `ad_pathfinder` (all nine AD exercises) and
  `appsec_architect` (all ten AppSec exercises) are global completion badges,
  registered in the catalogue and covered by a regression test.
- Live harness: all **19 new pathway labs** pass one clean run. The AD solver now
  waits for the LDAP bootstrap and disables LDIF line wrapping.
- Residual smoke-test account `smoke_tester` removed; users 48 → 47, real users
  and learner data preserved.

## 5.17.3 additions

- Migration `0041_tenant_rls_legacy` extends forced tenant RLS to 16 legacy
  learner tables (25 enforced tables total).
- The 9 Active Directory (`windows-11-*`) and 10 modern application-security
  (`web-11-*`) pathway labs are implemented; the catalogue is 210 labs.
- The Community / Academic edition keeps a single `default` institution while
  the RLS backstop remains edition-agnostic.

## Verification record

- `GET /api/version` → `5.17.7`
- `GET /health` → `200`
- `alembic current` → `0041_tenant_rls_legacy (head)`
- Registered labs → `210` (170 public, 40 course-scoped)
- Release status → `current` / `v5.17.7`
- Cutover → `deployment_mode=production`, `data_collection_mode=production`
- 5.17.7 backup/restore → **PASSED** (87 users, 2 courses, 210 labs, 41 enrollments, 124 completions, 463 achievements)

## Related documents

- [Release 5 production readiness](RELEASE-5-PRODUCTION-READINESS.md)
- [Deployment runbook](DEPLOYMENT-RUNBOOK.md)
- [Validation report](VALIDATION-REPORT.md)
- [Backup and restore test](BACKUP-RESTORE-TEST.md)
- [Deployment topology and sizing](DEPLOYMENT-TOPOLOGY-AND-SIZING.md)
