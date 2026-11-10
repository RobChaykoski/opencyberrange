# Analytics event schema and Exercise Health

Status: **v2.5.4 contract; normalized event table still deferred**
Code contract: `platform/backend/app/services/analytics_schema.py`
Related: [Analytics governance](ANALYTICS-GOVERNANCE.md),
[Data dictionary](DATA-DICTIONARY.md),
[Learning analytics](V2-LEARNING-ANALYTICS.md)

## Why this exists

The current platform derives most metrics from `lab_sessions`, `lab_completions`,
`flag_attempts`, and survey tables. That is enough for a first dashboard, but it
cannot answer a revision question: did feedback and completion improve because
the lab changed, or because the cohort changed? The missing field is
**exercise version**.

This page defines the minimum event envelope for future analytics work and the
fields the Exercise Health panel must show. It deliberately does not introduce
one opaque health score.

## Minimum analytics event

Every event carries the following envelope. Fields marked **required** must be
present; `exercise_version` and `mapping_version` become required whenever
`exercise_id` is set.

| Field | Type | Required | Privacy | Definition |
|---|---|---|---|---|
| `event_id` | string (UUID) | Yes | pseudonymous | Stable event identifier; supports idempotency and audit. |
| `pseudonymous_user_id` | string | Yes | pseudonymous | Keyed hash of the learner ID. Raw user IDs stay in the operational database and are never exported to research. |
| `course_id` | integer / null | No | confidential | Course context, or null for standalone practice. |
| `cohort_id` | string / null | No | confidential | Stable cohort key such as `CS101-2026F`. |
| `exercise_id` | integer / null | No | internal | Lab/exercise identifier. |
| `exercise_version` | string / null | When exercise set | internal | Content version or content hash of the lab. |
| `mapping_version` | string / null | When exercise set | internal | Version of the track and competency mapping used at event time. |
| `occurred_at` | datetime (UTC) | Yes | confidential | When the learner action happened. |
| `attempt_id` | string / null | No | pseudonymous | Groups events from one exercise attempt. |
| `event_type` | enum | Yes | internal | See event types below. |
| `result` | enum / null | No | confidential | Outcome such as `completed`, `abandoned`, `correct`, `passed`. |
| `platform_version` | string | Yes | internal | Release that produced the event. |
| `source` | enum | Yes | internal | `learner`, `instructor`, or `system`. |
| `privacy_classification` | enum | Yes | internal | `pseudonymous`, `confidential`, `restricted`, `aggregate`, or `internal`. |

### Event types

- `exercise_started`
- `exercise_completed`
- `exercise_abandoned`
- `flag_attempted`
- `hint_requested`
- `workbook_opened`
- `quiz_attempted`
- `pulse_submitted`
- `feedback_submitted`
- `certificate_issued`
- `transcript_requested`

### Result values

`started`, `completed`, `abandoned`, `correct`, `incorrect`, `passed`,
`failed`, `opened`, `submitted`, `issued`, `requested`.

### Versioning rules

1. **Exercise version** changes whenever the lab's objectives, walkthrough,
   flag path, containers, or hints change materially. Add it to `lab.yaml` and
   persist it on the event.
2. **Mapping version** changes whenever a lab moves track, level, competency, or
   skill-tree mapping. Do not rewrite historical mapping silently.
3. **Platform version** identifies the release that produced the event.
4. Reports group by `exercise_version` before comparing revisions. Never mix
   versions in one completion or feedback rate without a visible label.
5. A missing version is **not** treated as the current version. It is
   `unversioned` and excluded from revision comparisons.

## Exercise Health panel

For each exercise, report every component below. The panel may show a summary
status, but the components remain visible.

| Field | Definition | Notes |
|---|---|---|
| Assigned learners | Learners enrolled and assigned the exercise | Roster denominator |
| Started learners | Distinct learners with a session | Activity denominator |
| Completed learners | Distinct learners with a valid completion | Reset completions excluded until re-completed |
| Median active time | Median bounded learning minutes | Include IQR |
| Active time IQR | Q3 − Q1 for active time | Shows spread, not just central tendency |
| First-attempt success | Completions with one attempt / completions | Attempts are flag submissions |
| Median attempts | Median flag attempts per completion | Also show share with 3+ attempts |
| Hint-use rate | Completions with at least one hint / completions | Hint pressure |
| Time to first hint | First hint time − session start | Null until hint events are timestamped |
| Reset rate | Instructor resets / learners with a session | Separates resets from failure |
| Technical failure rate | Sessions with `status = error` / sessions | Separates platform failure from learning difficulty |
| Abandonment point | Last completed step before stop | Null until step-level events are collected; show the reason |
| Difficulty rating | Mean pulse difficulty (1–5) | Show response count |
| Instruction clarity | Mean clarity rating (1–5) | Course-level until per-exercise clarity ships |
| Learning-value rating | Mean pulse learning (1–5) | Self-reported |
| Free-text themes | Coded themes and counts | Never raw comments across courses |
| Lab version | Content version or hash | Required for revision comparison |
| Sample size | Distinct learners with evidence | Always visible |
| Health status | green / amber / red / grey | Worst component, with reasons |
| Component status | One status per component | Prevents one strong metric hiding a weak one |

### Status model

| Status | Meaning |
|---|---|
| **Green** | Technically reliable, clear, appropriate difficulty, strong learning value. |
| **Amber** | Mixed evidence, strained experience, or a component near its threshold. |
| **Red** | Technical failures, unclear instructions, severe abandonment, or low learning value. |
| **Grey** | Insufficient evidence; no judgement is made. |

Use the components for triage:

- High difficulty + high learning value: keep, but add scaffolding or a hint.
- High completion + low learning value: likely too easy; add challenge.
- High technical failure + high abandonment: fix the environment before
  rewriting the content.
- Low sample: grey; do not label the lab or the instructor.

## Implementation status

| Capability | Status |
|---|---|
| Cohort suppression and available/suppressed/no_evidence states | Implemented |
| Exercise Health components from sessions, completions, attempts, hints, resets, technical failures | Implemented on the course exercise endpoint |
| Health status with component statuses | Implemented |
| `exercise_version` and `mapping_version` on every event | Planned; required before revision comparisons |
| Step-level abandonment point and hint timestamps | Planned; fields return null with a reason until collected |
| Per-exercise instruction clarity | Planned; course-level clarity is available |
| Versioned `analytics_events` table | Planned for v2.5.3 |
| CSV/Excel formula-injection protection | Implemented for activity, ops, and cross-course CSV |

Until the event table ships, reports must state which fields are unavailable and
must not substitute zero for missing evidence.
