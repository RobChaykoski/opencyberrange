# SWOCTS Cyber Range 2.5.3

SWOCTS Cyber Range is powered by OpenCyberRange.

Edition: **Professional** — Community / Academic plus analytics, reporting,
cohort analysis, competency evidence, accreditation support, and research
exports.
Status: **maintenance release**. 2.5.3 closes the analytics small-group
suppression finding, adds the versioned eight-axis competency radar, records
lab difficulty evidence for all 149 labs, and closes the accessibility and
supply-chain evidence gaps recorded against 2.5.2.

## Competency radar

- Eight stable competency axes: Network & Systems, Web & API, Identity &
  Access, Incident & Forensics, OSINT, Malware Analysis, OT/ICS, and AI
  Security.
- Individual view shows Baseline, Current, and Target overlays.
- Cohort view shows median, interquartile band, and target, and suppresses
  cohorts below the configured minimum size.
- Every axis opens a drill-down with contributing labs, assessments, recency,
  evidence count, model/mapping version, and observed / self-reported /
  instructor source counts.
- Scoring uses 50% assessment, 25% independent completion, 15% retained, and
  10% instructor evidence. Missing components stay visible as provisional with
  weight coverage rather than being silently redistributed.
- Self-confidence is displayed separately and is not part of the competency
  score.
- Per-completion mapping snapshots are stored so historical reports keep the
  mapping that was current when the completion happened.

## Analytics privacy

- Added `analytics_min_cohort_size` (default 5) and explicit **available**,
  **suppressed**, and **no_evidence** states to course and exercise analytics.
- Course feedback summaries and survey responses suppress small cohorts and do
  not expose learner usernames or emails in suppressed payloads.
- Reports and exports exclude suppressed cohorts from aggregate totals.

## Labs and evidence

- `validate-lab.py --all`: **149 labs, 0 errors, 0 warnings**.
- `lab-release-proof.py`: **149 pass, 0 review, 0 fail**.
- Difficulty evidence is observed platform analytics when `n>=5`; otherwise it
  is a labelled provisional student-tester review. The source, sample size,
  quality, and review date are recorded in each `lab.yaml`.
- Instructor-led assessments carry explicit workbook and hint exemptions.
- Added ADR 0005: the lab bridge egress risk is explicitly accepted for 2.5.3,
  with per-lab allowlisting deferred to the next release.

## Accessibility

- Added `/lang`, title, author, subject, and keyword metadata to report and
  certificate PDFs. Full PDF/UA tagging remains open.
- Added the `session_accommodation_percent` setting (100–300%) for timed
  exercises. It scales both the initial session length and extensions.
- Fixed WCAG AA contrast defects in the skill matrix and analytics RAG badges.
- Made activity and analytics table regions keyboard-focusable.
- Competency radar routes pass axe WCAG 2.2 AA at 1280×900 and 320×800 with no
  page-level overflow at 200% text. Report data tables scroll horizontally at
  200% text, which WCAG 1.4.10 permits for two-dimensional data.

## Supply chain and release engineering

- Added OCI image labels for title, description, version, revision, source, and
  licence.
- Refreshed and signed `supply-chain.lock.json`; the release tag is signed with
  the same release key.
- Development and production run the same commit and report `2.5.3`.
- Demo feature-test data remains development-only and is absent from
  production.

## Upgrade notes

1. Take a database snapshot before upgrading.
2. Pull the current `main` commit or the `v2.5.3` tag.
3. Rebuild the backend and frontend images.
4. Restart the backend once so the competency snapshot columns, mapping
   backfill, and new platform settings are applied. The migration is
   idempotent and additive.
5. Confirm `/health` and `/api/version` report `2.5.3`.
6. Open **Admin > Settings > Labs** and review **Timed Exercise
   Accommodation**; leave it at `100%` unless a learner has an approved plan.
7. Open **Admin > Settings > Security** and confirm **Analytics Minimum
   Cohort** is `5` or the value required by local policy.
8. If the host uses the prebuild workflow, run `scripts/prebuild-labs.sh` to
   refresh stable `ocr-lab/*:latest` images.
9. Rebuild the workbook wiki and user manual after pulling the documentation.

## Previous releases

2.5.2 added the administrator privacy default and corrected the analytics
report test for the six-dimension Skill DNA model. 2.5.1 added the
licence-compliance, About/build-info, privacy-control, and course-workspace
cleanup changes. 2.5.0 added organizational course health, two-way feedback,
optional knowledge checks, certificates, the Cyber DNA tester trait, the
celebration wall, database integrity, and deleted-user resilience. See
`CHANGELOG.md` for the complete history.
