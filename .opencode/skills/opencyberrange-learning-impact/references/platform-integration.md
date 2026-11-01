# Platform Integration and Future Timing

Use this reference with the `OpenCyberRange Learning Impact` skill.

This is a forward-looking data contract. It describes the minimum event model
needed for the reports in this skill and for future features: paced delivery,
timed exercises, coordinated support, and cohort dashboards.

Treat the schema as a versioned contract. Add fields; do not silently change the
meaning of an existing one.

## 1. Principles

- **Server-side time.** Record timestamps on the server, not the browser. Keep a
  monotonic elapsed value so clock changes do not corrupt latencies.
- **Explicit events.** Do not infer a decision from a click. Record the decision
  and its correctness.
- **Pseudonymous.** The analytics record stores a learner ID, not a name or email.
- **Purpose-bound.** Every event maps to a metric in the catalogue.
- **Minimum data.** No keystrokes, mouse paths, screen recordings, webcam, or
  microphone by default.
- **Replayable.** A session record plus the task version should reproduce the
  metric.
- **Exportable.** The learner can request their record; the instructor can export
  a cohort without learner-level identifiers.

## 2. Event model

### Session envelope

```json
{
  "schema_version": "0.1",
  "session_id": "s-2026-11-01-0007",
  "learner_id": "anon-7f3a",
  "lab_slug": "network-0-1-ping-basics",
  "track": "network",
  "level": 0,
  "task_version": "2026.10",
  "started_at": "2026-11-01T14:00:00Z",
  "ended_at": "2026-11-01T14:22:00Z",
  "mode": "standard",
  "accommodations": ["extra_time"],
  "checkpoints": [],
  "events": []
}
```

`mode` values: `standard`, `low_bandwidth`, `no_device`, `instructor_led`.

`accommodations` is a controlled list. It is used for equity analysis, never to
lower a score.

### Event types

| Type | Required fields | Purpose | Metric family |
|---|---|---|---|
| `session_start` | `t` | Session boundary | All |
| `task_start` | `t`, `task_id` | Task boundary | Load, speed, reprioritisation |
| `decision` | `t`, `task_id`, `correct`, `latency_s`, optional `confidence`, `choice` | Decision quality and calibration | Speed, calibration |
| `hint_request` | `t`, `hint_id`, optional `task_id` | Support use and dependency | Load, support |
| `workbook_open` | `t`, optional `section` | Aid use | Load |
| `interruption` | `t`, `interruption_id`, `kind`, optional `ends_t` | Load and recovery | Load |
| `resume` | `t`, `interruption_id`, `task_id`, `correct_next_step` | Recovery | Load, reprioritisation |
| `change_event` | `t`, `change_id`, `kind`, `summary` | Scenario change that forces re-planning | Reprioritisation |
| `reprioritize` | `t`, `ranked`, `expert_ranked`, optional `latency_s` | Priority alignment | Reprioritisation |
| `checkpoint` | `t`, `checkpoint_id`, `kind`, `score`, `max`, optional `aids_allowed` | Retention and transfer | Retention, transfer |
| `flag_attempt` | `t`, `correct` | Completion context | Supporting |
| `session_end` | `t`, optional `reason` | Session boundary | All |

`decision.latency_s` should come from the prompt timestamp, not from the time
between two arbitrary events. If the platform cannot provide it, omit it rather
than estimating.

`correct` is a rubric decision. Define it in the lab or task manifest. Do not
derive it from a keyword match on free text.

### Checkpoint kinds

| Kind | Meaning |
|---|---|
| `pre` | Baseline before the learning event |
| `immediate` | Within 15 minutes of the event |
| `delayed` | At a stated delay (7, 30, or 90 days) |
| `transfer` | Novel context after practice |

Include `delay_days` for delayed checkpoints and `equivalent_form_id` when
equivalent forms are used.

## 3. Derived metrics

The reference calculator in `scripts/compute_session_metrics.py` implements these
from the event model:

| Metric | Inputs | Formula |
|---|---|---|
| `retention_index` | `immediate` and `delayed` checkpoints | `min(delayed / immediate, 1.0)` |
| `decision_accuracy` | `decision.correct` | `correct / decisions` |
| `decision_latency_median_s` | `decision.latency_s` | Median |
| `decision_latency_p90_s` | `decision.latency_s` | 90th percentile |
| `throughput_correct_per_min` | `decision.correct`, `latency_s` | `correct / (sum(latency_s) / 60)` |
| `time_to_first_correct_decision_s` | `decision` events | First correct latency or elapsed time |
| `hint_rate_per_decision` | `hint_request`, `decision` | `hints / decisions` |
| `interruption_recovery_median_s` | `interruption`, `resume` | Median of `resume.t - interruption.ends_t` |
| `reprioritization_alignment` | `reprioritize.ranked`, `expert_ranked` | Mean top-3 overlap / 3 |
| `calibration_gap` | `decision.confidence`, `correct` | `mean(confidence) - accuracy` |
| `brier_score` | `decision.confidence`, `correct` | `mean((confidence - outcome)^2)` |
| `time_on_task_s` | envelope timestamps or last event | Elapsed time |

Report the raw inputs and the n. A derived metric without its inputs is not
auditable.

## 4. Coordinated support

The future platform should use the same events to coordinate support, not to
surveil.

### Support triggers

Use a combination of signals, never a single metric:

| Signal pattern | Possible support | Guardrail |
|---|---|---|
| High load + repeated same error | Offer a worked example or a 10-minute check-in | Do not auto-label the learner |
| Long latency + low accuracy on a timed task | Offer extra time or a low-pressure mode | Do not reveal the answer |
| Many hints in a short window | Offer a short break or a different scaffold | Do not block the lab |
| Repeated interruption with poor recovery | Suggest a quieter session or a shorter task | Do not require disclosure |
| Correct but overconfident decisions | Add a calibration prompt | Do not shame |
| No return practice after 14 days | Send a practice invitation | Allow opt-out |

### Coordination rules

- Support is **offered**, not imposed.
- The learner can dismiss a support prompt without explanation.
- A human decides anything that affects access, grading, or eligibility.
- Do not send a learner's individual data to an external partner.
- Aggregate only when the group is large enough to prevent re-identification
  (default: 10 or more).
- Record the support action so its effect can be evaluated.

### Timing features

Pacing and timed exercises are part of the learning design, not a race.

- State the time limit before the task.
- Offer extra time by default, or report timed and untimed conditions separately.
- Use server-side elapsed time; display a calm timer, not a countdown that
  creates panic.
- Pause the timer for approved breaks and accommodations.
- Do not use time pressure in the first exposure to a new procedure.
- Record the time limit and the accommodation in the session envelope.

## 5. Suggested storage model

This is a sketch, not a migration.

```text
learning_sessions
  id, schema_version, learner_id (pseudonymous), lab_slug, task_version,
  started_at, ended_at, mode, accommodations_json

learning_events
  id, session_id, event_type, occurred_at, elapsed_s, task_id,
  payload_json

learning_checkpoints
  id, session_id, checkpoint_id, kind, delay_days, score, max,
  aids_allowed, equivalent_form_id

learning_support_actions
  id, session_id, trigger_code, action_code, offered_at, accepted_at,
  dismissed_at, notes
```

Indexes: `(learner_id, started_at)`, `(lab_slug, task_version)`,
`(session_id, event_type)`.

Retention: define per deployment. A default of 24 months for aggregate planning
data and 12 months for learner-level records is a reasonable starting point; the
deployment owner must confirm it.

## 6. API sketch

```text
POST /api/learning/sessions
POST /api/learning/sessions/{id}/events
POST /api/learning/sessions/{id}/checkpoints
GET  /api/learning/learners/{id}/report
GET  /api/learning/cohorts/{id}/report
GET  /api/learning/export?from=...&to=...&format=json|csv
```

Rules:

- Authorise by role and cohort membership.
- Return aggregate data for organisation reports.
- Return learner-level data only to the learner and to the instructor responsible
  for that cohort.
- Never return another learner's identifier in a learner report.
- Log access to learner-level reports.

## 7. Rollout phases

### Phase 1 — Instrument

- Add session, decision, hint, checkpoint, and flag events.
- Add server-side timestamps and a task version.
- Export JSON/CSV for offline analysis.
- Do not build dashboards yet.

### Phase 2 — Report

- Add the three report templates.
- Add the reference calculator.
- Add cohort aggregates with `n` and missing data.
- Add the learner correction route.

### Phase 3 — Pace and coordinate

- Add scheduled checkpoints and practice invitations.
- Add support prompts with the guardrails above.
- Add a support-action log.
- Evaluate whether the support improved retention or reduced load.

### Phase 4 — Partner delivery

- Add organisation-level capability briefs.
- Add cohort scheduling and facilitator coordination.
- Add aggregate retention benchmarks by role and track.
- Publish the limitations and the data-sharing terms.

## 8. Acceptance tests

Before a metric ships:

- [ ] The event is emitted once per action, with a server timestamp.
- [ ] The metric can be recomputed from the exported record.
- [ ] The task version is stored.
- [ ] The report shows `n` and missing data.
- [ ] The learner report contains no other learner's data.
- [ ] The organisation report contains no learner-level data.
- [ ] Accommodations are recorded and do not lower the score.
- [ ] A learner can request and correct their record.
- [ ] A support prompt can be dismissed without explanation.
- [ ] A human reviews any action that affects access or grading.

## 9. What not to build

- A live leaderboard of speed, hints, or errors.
- A "risk score" for individual learners.
- A psychological profile generated from logs.
- A keystroke or screen-recording pipeline.
- A partner dashboard with learner names.
- An automated intervention that changes access or grading.
- A single composite "cyber capability" score.
