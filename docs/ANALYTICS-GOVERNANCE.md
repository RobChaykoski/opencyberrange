# Analytics governance

Status: **v2.5.2 release contract**
Owner: Curriculum / Privacy
Applies to: Community, Academic, Professional, and Enterprise profiles
Related: [Data dictionary](DATA-DICTIONARY.md),
[Learning analytics](V2-LEARNING-ANALYTICS.md),
[Programme reports](PROGRAMME-REPORTS.md),
[Privacy notice](PRIVACY-NOTICE.md),
[Analytics event schema](ANALYTICS-EVENT-SCHEMA.md)

This page defines what the platform measures, who may use it, how long it is
kept, when it is suppressed, and how research and exports are approved. The UI,
API, CSV/PDF exports, and tests share these rules.

## 1. Purpose and boundaries

Analytics exists to help a learner see their own progress, help an instructor
improve a course, and give an approved researcher de-identified evidence about
learning. It is **not** a gradebook, a prediction engine, a public ranking, or a
disciplinary system.

| Use | Allowed | Boundary |
|---|---|---|
| Learner progress | Yes | Learner sees their own evidence and can request correction. |
| Instructor course improvement | Yes | Assigned course only; aggregate above the minimum cohort. |
| Programme and accreditation reporting | Yes | Aggregate; no learner ranking. |
| Security and abuse investigation | Yes | Authorised administrators; audit-logged. |
| Optional surveys and research | Yes, with consent | Separate consent; purpose-limited; ethics approval where required. |
| Advertising, sale, or unrelated profiling | No | Prohibited. |
| Automated high-stakes decisions | No | No automated grade, sanction, admission, or employment decision. |

## 2. Consent boundaries

| Data / use | Basis | Who can see it | Export boundary |
|---|---|---|---|
| Account and course delivery | Service / institutional authority | Learner; assigned instructor; admin | Self-service export; course reports |
| Security logs and audit | Security / legitimate interest | Admin; privacy officer; auditor | Activity export with a reason; no learner analytics |
| Pulse surveys (`survey_opt_in`) | Explicit consent | Learner; instructor aggregate above the minimum cohort; admin | Aggregate only; free text only to the assigned instructor above the minimum cohort |
| Course check-in and coaching notes | Service for the check-in; consent for optional free text | Learner's own check-in; assigned instructor aggregate; admin | Aggregate; no cross-course free text |
| Public celebration wall | Voluntary public action | Signed-in community | Count only; never joined to analytics |
| Competition leaderboard | Opt-in; learner chooses name mode | Competition participants and organisers | Leaderboard scope only |
| Research participation | Separate explicit consent plus ethics approval | Approved researcher; privacy officer | De-identified extract under an approved protocol |
| Certificate verification | Public verification of the certificate ID | Anyone with the ID | Minimal validity and display-name fields |

Withdrawal of optional consent stops new optional collection and removes the
optional data from future aggregates. It does not delete core learning records
where the institution must retain them, and it does not revoke a certificate a
third party already downloaded.

## 3. Metric definitions

Every metric is defined once here and used by the API, UI, exports, and tests.
Every percentage carries its denominator. A missing denominator is
**insufficient evidence**, never a measured zero.

| Metric | Definition | Denominator / exclusions | Minimum evidence | Notes |
|---|---|---|---|---|
| Assigned learners | Distinct learners enrolled in the course and assigned the exercise | Course enrolment | 1 | Roster count, not activity |
| Started learners | Distinct learners with at least one lab session | Assigned learners | 5 for a percentage | A start is a session, not a page view |
| Completed learners | Distinct learners with a valid completion | Assigned learners | 5 for a percentage | Reset completions are excluded until re-completed |
| Completion rate | Completed learners / assigned learners | Assigned learners | 5 | Learner-based, not started-pair based |
| Started completion rate | Completed learners / started learners | Started learners | 5 | Do not compare with the learner-based rate |
| Abandonment rate | (Started learners − completed learners) / started learners | Started learners | 5 | A learner may return later |
| Active time | Bounded session time per learner-exercise pair | Sessions with usable timestamps | 3 for a median | Idle gaps are capped; report median and IQR |
| Time over estimate | Completions above `duration_minutes` / timed completions | Timed completions | 5 | Uses the lab's estimated duration |
| First-attempt success | Completions with `attempts = 1` / completions | Completions | 5 | Attempts are flag submissions |
| Median attempts | Median flag attempts per completion | Completions | 3 | Report the distribution, not just the median |
| Reattempt recovery | Completions with more than one attempt / completions | Completions | 5 | Shows persistence, not failure |
| Hint-use rate | Completions with at least one hint / completions | Completions | 5 | Also called hint pressure |
| Hints per completion | Total hints / completions | Completions | 5 | Counts, not unique hints |
| Time to first hint | First hint timestamp − session start | Sessions with hint events | 10 | Not available until hint events are timestamped; show null, not zero |
| Reset rate | Instructor resets / learners with a session | Learners with a session | 5 | Separates resets from learner failure |
| Technical failure rate | Sessions with `status = error` / sessions | Sessions | 5 | Separates platform failure from learning difficulty |
| Abandonment point | Last completed step or event before stop | Step-level events | 10 | Not available until step events are collected; show null and a reason |
| Difficulty rating | Mean pulse difficulty (1–5) | Pulse responses | 5 | Self-reported; show response count |
| Instruction clarity | Mean clarity rating (1–5) | Clarity responses | 5 | Course-level until per-exercise clarity ships |
| Learning value | Mean pulse learning rating (1–5) | Pulse responses | 5 | Self-reported; not a mastery claim |
| Free-text themes | Coded themes and counts from comments | Comments above the minimum cohort | 5 comments | Never expose raw comments across courses |
| Lab version | Content version or hash of the exercise | Lab metadata | 1 | Required to avoid mixing revisions |
| Sample size | Distinct learners with evidence | — | — | Always displayed with the metric |

### Exercise Health status model

The panel reports the components, not one opaque score. Each component is
green, amber, red, or grey; the overall status is the worst component, and grey
means insufficient evidence.

| Status | Meaning |
|---|---|
| **Green** | Technically reliable, clear, appropriate difficulty, strong learning value. |
| **Amber** | Mixed evidence, strained experience, or a component near its threshold. |
| **Red** | Technical failures, unclear instructions, severe abandonment, or low learning value. |
| **Grey** | Insufficient evidence; no judgement is made. |

Example: a lab with high difficulty and high learning value is not automatically
red. A lab with a high completion rate and low learning value is not
automatically green. The component statuses show why.

## 4. Reporting suppression

Small-cell suppression protects learners from re-identification. The platform
uses `analytics_min_cohort_size` (default **5**) and applies it consistently to
course overview, exercise rows, pulse comments, cross-course reports, CSV, and
PDF.

| State | Meaning | What is shown |
|---|---|---|
| **available** | Cohort meets the minimum | Counts, rates, medians, feedback, and confidence with `n` |
| **suppressed** | Cohort is between 1 and the minimum | Counts may remain; rates, medians, feedback, confidence, and skill-tree activity are hidden |
| **no_evidence** | Cohort has no activity yet | Zero counts only; metrics are null, not zero |

Additional rules:

- Apply complementary suppression: if one small cell could be derived from a
  total and another cell, suppress the related total or second cell.
- Do not publish a percentage with fewer than 5 observations, a median with
  fewer than 3, or a cohort trend with fewer than 10.
- Never rank learners, instructors, or courses. Report distributions and
  evidence labels.
- Do not join optional survey or research data to security or disciplinary data.
- Exports must preserve the same suppression state as the screen. A CSV or PDF
  must not contain a value the UI hides.
- Suppression is not a substitute for access control: instructors see only
  their assigned courses; researchers see only approved de-identified extracts.

## 5. Retention

| Data class | Default | Action at end |
|---|---|---|
| Core account and learning records | Institution schedule | Delete or de-identify per schedule |
| Activity and audit events | 90 days review window | Anonymise or delete |
| Lab sessions and timing inputs | Institution schedule; 90-day operational review | Delete |
| Pulse and course feedback | Until consent withdrawn or study close | Delete optional rows; retain aggregates |
| Survey and research responses | Approved study period | Destroy or de-identify |
| Research extracts | Approved study period | Destroy; record destruction |
| Backups | 30 days default | Rotate; re-apply erasure ledger on restore |
| Downloaded exports | Not stored by the platform | Recipient deletes per agreement |

The operator's retention schedule overrides these defaults where the institution
or law requires a longer or shorter period. The privacy notice and data
dictionary must be updated in the same release.

## 6. Research governance

Research use requires all of the following:

1. **Question and purpose** — a written question, expected benefit, and why
   de-identified aggregate data is sufficient.
2. **Ethics review** — institutional research ethics board approval or a
   documented exemption before any extract is created.
3. **Privacy review** — the privacy officer confirms the lawful basis, consent
   scope, retention, and re-identification risk.
4. **Data minimisation** — request only the fields needed; prefer aggregates and
   pseudonymous IDs; never request passwords, MFA material, VPN private keys, or
   raw IP addresses.
5. **De-identification** — remove direct identifiers; replace user IDs with a
   study-specific keyed hash; suppress small cells; assess linkage risk.
6. **Access control** — named researchers only, least privilege, time-boxed
   access, audit-logged downloads.
7. **Publication review** — no cell below the minimum; no learner-level quotes
   without separate consent; no re-identification through combination.
8. **Destruction** — delete the extract and keys at the end of the approved
   period; record the destruction.

Prohibited research uses: re-identification attempts, advertising, sale,
employment or admission decisions, immigration or law-enforcement matching, and
any use beyond the approved protocol. Suspected misuse is handled as a privacy
incident.

## 7. Export schemas

Exports are versioned. Adding, removing, or renaming a field requires a version
bump and a migration note.

### `analytics-export-v1` (cross-course CSV/PDF)

| Field | Classification | Notes |
|---|---|---|
| `course_code`, `course_name` | Confidential | Course identity |
| `cohort_state` | Internal | available / suppressed / no_evidence |
| `enrolled_learners`, `started_learners`, `completed_learners` | Confidential | Counts; suppressed rows show blanks |
| `completion_rate`, `abandonment_rate`, `started_completion_rate` | Confidential | Null when suppressed |
| `median_learning_minutes`, `learning_minutes_iqr` | Confidential | Median and IQR |
| `first_attempt_rate`, `median_attempts`, `hint_use_rate` | Confidential | Suppressed when small |
| `learning_reported`, `difficulty_reported` | Confidential | Self-reported; response count |
| `positive_rate`, `likes`, `dislikes` | Confidential | Suppressed when small |
| `confidence_gain` | Confidential | Performance-growth proxy, not a psychological score |
| `skill_tree_assigned_pct`, `skill_tree_completed_pct` | Confidential | Suppressed when small |
| `minimum_cohort_size`, `suppression_reason` | Internal | Why a row is blank |

### `activity-export-v1` (admin CSV/JSON)

| Field | Classification | Notes |
|---|---|---|
| `id`, `created_at`, `event_type` | Internal | Event envelope |
| `label`, `detail` | Confidential | May contain learner text; formula-neutralised in CSV |
| `actor_id`, `actor_name`, `actor_role` | Confidential | Removed for erased accounts |
| `target_type`, `target_id`, `target_label` | Confidential | Context |
| `ip_address` | Restricted | Security review only |

### `self-service-export-v1` (JSON)

Contains the account record, VPN metadata, courses, completions, flag attempts,
quiz attempts, achievements, lab sessions, competition entries, and activity
history. Excludes password hashes, TOTP secrets, recovery codes, trusted-device
tokens, and the WireGuard private key.

### `course-report-v1` (PDF)

Contains course identity, enrolled learners, completion and attempt summaries,
quiz results, achievements, and the report reason. Suppressed aggregates stay
suppressed. Downloaded PDFs are not stored by the platform.

### Spreadsheet safety

CSV and Excel-compatible exports neutralise values beginning with `=`, `+`, `-`,
`@`, tab, CR, LF, or their full-width forms by prefixing an apostrophe, except
for plain numbers and lone punctuation markers. The original text follows the
marker. Tests cover `=HYPERLINK(...)`, `@SUM(1+1)`, `+cmd|' /C calc'!A0`, and
full-width variants. JSON and PDF exports do not interpret formulas.

## 8. Roles and access

| Role | Access |
|---|---|
| Learner | Own records, own exports, optional consent controls |
| Instructor | Assigned courses; aggregate above the minimum cohort; no cross-course learner ranking |
| Programme lead / dean | Aggregate programme reporting; no unnecessary learner-level detail |
| Administrator | Platform operations and support; audited; privacy mode available |
| Privacy officer / auditor | Consent, erasure, audit, and export-reason evidence |
| Approved researcher | De-identified extract under an approved protocol |

## 9. Change control

- Update this page, the data dictionary, and the event schema together.
- Bump the export schema version when a field changes.
- Add a suppression test for every new report surface.
- Add a consent-boundary test for every new optional data collection.
- Record the review date in the release notes.
