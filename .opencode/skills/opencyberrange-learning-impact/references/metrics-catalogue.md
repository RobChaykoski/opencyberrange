# Metrics Catalogue

Use this reference with the `OpenCyberRange Learning Impact` skill.

Every entry separates the **construct** (what we care about) from the
**observable** (what the platform records). The observable is a proxy. Report it
with its limits, not as the construct itself.

## How to read an entry

| Field | Meaning |
|---|---|
| Construct | The capability or experience being estimated |
| Observable | The event or score the platform can actually record |
| Formula | A reproducible calculation |
| Minimum data | What must exist for the metric to be reportable |
| Report with | The measures that must appear beside it |
| Do not | The common misuse |

If a metric has no formula and no minimum data, it is a slogan, not a metric.

---

## 1. Retention and recall

### 1.1 Delayed checkpoint score

- **Construct:** durable retrieval and application after a delay.
- **Observable:** score on an equivalent task taken 7, 30, or 90 days after the
  learning event.
- **Formula:** `correct items / total items`, with the delay and aids recorded.
- **Minimum data:** one immediate checkpoint, one delayed checkpoint, a stated
  delay, and a note on whether hints or the workbook were available.
- **Report with:** n, median and interquartile range, the delay, and the task
  equivalence method.
- **Do not:** call a same-day retest "retention."

### 1.2 Retention index

- **Construct:** how much of the immediate performance survives the delay.
- **Observable:** the ratio of delayed to immediate checkpoint scores.
- **Formula:** `min(delayed_score / immediate_score, 1.0)` when the immediate
  score is greater than zero. Report the raw scores as well.
- **Minimum data:** both scores on equivalent forms.
- **Report with:** raw scores, delay, and the ceiling effect. A ratio above 1.0
  is possible and usually means the forms were not equivalent, not that memory
  improved.
- **Do not:** compare retention indices across programmes with different delays
  or different task difficulty.

### 1.3 Hint-free delayed success

- **Construct:** independent retrieval without scaffolding.
- **Observable:** percentage of learners who complete the delayed task with zero
  hints and no workbook.
- **Formula:** `learners with zero hints and a correct solve / learners
  attempted`.
- **Minimum data:** hint events and completion events on the delayed task.
- **Report with:** the hint policy and the definition of "solve."
- **Do not:** treat hint use as cheating. A hint can be good help-seeking.

### 1.4 Error recurrence rate

- **Construct:** whether feedback corrected a misconception or only a single
  attempt.
- **Observable:** the same error class appearing again in later sessions.
- **Formula:** `repeated error classes / error classes observed at least twice`
  across a defined window. Define error classes from the rubric, not from free
  text.
- **Minimum data:** at least two sessions and a stable error taxonomy.
- **Report with:** the taxonomy and the window.
- **Do not:** infer recurrence from a single repeated click or typo.

### 1.5 Spacing adherence (context measure)

- **Construct:** whether the reinforcement schedule was actually delivered.
- **Observable:** the gap between practice sessions.
- **Formula:** `median days between sessions`, plus the percentage of learners
  inside the intended spacing window.
- **Minimum data:** session timestamps.
- **Report with:** the intended schedule.
- **Do not:** treat adherence as a learner trait; it is usually a programme
  design and scheduling outcome.

---

## 2. Working-memory load

Working memory is a limited system for holding and manipulating information.
Hands-on labs load it through interface complexity, multi-step procedures,
interruptions, and time pressure. Measure **load**, not capacity.

### 2.1 NASA-TLX mental demand

- **Construct:** perceived mental demand of the task.
- **Observable:** the mental-demand subscale of NASA-TLX, 0–100, administered
  immediately after the task.
- **Formula:** the subscale score, reported as a median with interquartile
  range. If the full TLX is used, state the weighting method.
- **Minimum data:** one post-task response and the task identifier.
- **Report with:** the task, the time limit, and the accommodation status.
- **Do not:** call a high score "low intelligence" or "poor memory." It is a
  design signal first.

### 2.2 Interruption recovery time

- **Construct:** the cost of rebuilding task state after an interruption.
- **Observable:** time from the end of a scripted interruption to the next
  correct action on the interrupted task.
- **Formula:** `t(next correct action) - t(interruption end)`, reported as a
  median and p90.
- **Minimum data:** an explicit interruption event and an explicit correct
  action event.
- **Report with:** the interruption type and whether notes were allowed.
- **Do not:** compare labs with different interruption designs.

### 2.3 Aid use

- **Construct:** how much external support the task required.
- **Observable:** count of workbook opens, hint requests, and note lookups per
  task.
- **Formula:** `aid events / tasks`, reported as a distribution.
- **Minimum data:** task boundaries and aid events.
- **Report with:** the aid policy. Some aids are the point of the exercise.
- **Do not:** rank learners by "independence" without stating the aid policy.

### 2.4 Dual-task decrement (advanced)

- **Construct:** performance cost when attention is divided.
- **Observable:** accuracy or latency on a primary task with and without a
  secondary task.
- **Formula:** `(dual-task performance - single-task performance) /
  single-task performance`, with the direction stated.
- **Minimum data:** counterbalanced single- and dual-task conditions.
- **Report with:** the secondary task and the practice order.
- **Do not:** run this in a live cohort without a pilot and an ethics review.

---

## 3. Rapid decision quality

Speed is only meaningful with correctness and a stated time limit.

### 3.1 Decision latency

- **Construct:** how long the learner takes to commit to a decision.
- **Observable:** time from the decision prompt to the submitted choice.
- **Formula:** median and p90 latency, in seconds. Report the distribution, not
  only the mean.
- **Minimum data:** a prompt timestamp and a submission timestamp.
- **Report with:** accuracy, task difficulty, and the time limit.
- **Do not:** publish latency alone or use it as a proxy for expertise.

### 3.2 Decision accuracy

- **Construct:** correctness of the chosen action under the scenario's rules.
- **Observable:** the rubric score for the decision.
- **Formula:** `correct decisions / decisions made`.
- **Minimum data:** a pre-defined correctness rule and a task id.
- **Report with:** latency and the number of decisions.
- **Do not:** score a defensible alternative as wrong because it was not the
  instructor's preferred click path.

### 3.3 Correct decisions per active minute

- **Construct:** useful decision throughput.
- **Observable:** correct decisions divided by time spent actively deciding.
- **Formula:** `correct decisions / (sum of decision latencies / 60)`.
- **Minimum data:** decision latencies and correctness.
- **Report with:** accuracy and the active-time definition. Idle time and
  reading time should be excluded deliberately, not by accident.
- **Do not:** use this to compare learners who received different amounts of
  reading material or accommodation time.

### 3.4 Timeout rate

- **Construct:** whether the time limit, not the task, drove the outcome.
- **Observable:** decisions that expired without a submission.
- **Formula:** `timeouts / decision opportunities`.
- **Minimum data:** the time limit and the timeout event.
- **Report with:** accuracy and the time limit.
- **Do not:** treat a timeout as a wrong answer without saying so; they are
  different failure modes.

### 3.5 Time to first correct decision

- **Construct:** how quickly the learner finds a workable path.
- **Observable:** time from scenario start to the first correct decision.
- **Formula:** the elapsed time, reported as a median with a range.
- **Minimum data:** scenario start and decision events.
- **Report with:** the number of prior incorrect decisions.
- **Do not:** use this as a selection test.

---

## 4. Reprioritisation and triage

Reprioritisation cannot be measured in a static checklist. The scenario must
inject a change: a new alert, a changed constraint, a new stakeholder, or a
resource loss.

### 4.1 Top-3 priority alignment

- **Construct:** whether the learner reordered work toward the highest-value
  items after the change.
- **Observable:** the learner's top three priorities and an expert reference
  ranking.
- **Formula:** `|learner_top3 ∩ expert_top3| / 3`. Report the item sets.
- **Minimum data:** a post-change ranking and a published expert ranking.
- **Report with:** the scenario change and the rationale for the expert ranking.
- **Do not:** treat one expert's ranking as objective truth. Publish the rubric
  and allow defensible alternatives.

### 4.2 Time to re-plan

- **Construct:** how quickly the learner acts on the new information.
- **Observable:** time from the change event to the first action consistent with
  the revised priority.
- **Formula:** `t(first revised action) - t(change event)`, median and p90.
- **Minimum data:** a change event and an action consistent with the new order.
- **Report with:** the action definition and the time limit.
- **Do not:** count a reflexive click as a re-plan.

### 4.3 Priority inversion rate

- **Construct:** whether low-value work displaced high-value work.
- **Observable:** high-priority tasks left incomplete while low-priority tasks
  were completed.
- **Formula:** `sessions with at least one inversion / sessions`, plus the list
  of inversions.
- **Minimum data:** task priorities and completion events.
- **Report with:** the priority source and the time limit.
- **Do not:** call every unfinished task an inversion; some are correct
  deprioritisation.

### 4.4 Recovery after interruption

- **Construct:** the ability to resume the right task after a disruption.
- **Observable:** whether the learner returns to the interrupted task and
  completes the correct next step.
- **Formula:** `correct resumptions / interruptions`.
- **Minimum data:** interruption and resumption events.
- **Report with:** the interruption type and the recovery window.
- **Do not:** penalise a learner who correctly abandons a task because the
  scenario changed.

---

## 5. Transfer and calibration

### 5.1 Novel-context score

- **Construct:** application of a procedure in an unfamiliar but equivalent
  context.
- **Observable:** checkpoint score on a new system, artefact, or scenario.
- **Formula:** `correct items / total items`, with the novelty stated.
- **Minimum data:** a transfer task that is not a reskin of the practice task.
- **Report with:** the mapping between the practice and transfer tasks.
- **Do not:** reuse the same hostnames, flags, or walkthrough steps.

### 5.2 Hint-free transfer success

- **Construct:** independent transfer.
- **Observable:** percentage of learners who solve the transfer task with no
  hints and no workbook.
- **Formula:** `hint-free correct transfer solves / attempts`.
- **Minimum data:** hint events and transfer completion.
- **Report with:** the hint policy.
- **Do not:** compare across different transfer tasks without saying so.

### 5.3 Confidence–accuracy gap

- **Construct:** calibration — knowing when you are unsure.
- **Observable:** confidence rating (0–1) and correctness for each decision.
- **Formula:** `mean(confidence) - accuracy`. Positive means overconfidence.
  Report with the Brier score.
- **Minimum data:** at least five confidence-rated decisions per learner for a
  learner-level view; more for a cohort.
- **Report with:** the Brier score, n, and the decision mix.
- **Do not:** interpret a single decision as a calibration trait.

### 5.4 Brier score

- **Construct:** probabilistic accuracy of confidence judgments.
- **Observable:** confidence and binary outcome per decision.
- **Formula:** `mean((confidence - outcome)^2)`, where `outcome` is 1 for correct
  and 0 for incorrect. Lower is better.
- **Minimum data:** confidence and correctness.
- **Report with:** the base rate of correct decisions.
- **Do not:** compare Brier scores across tasks with different difficulty
  without adjustment.

---

## 6. Supporting measures

These are context, not the headline.

| Measure | Formula | Use | Do not |
|---|---|---|---|
| Completion | `completed labs / started labs` | Programme delivery and drop-off | Treat as learning |
| Time-to-criterion | Sessions or active hours to reach a defined criterion | Pacing and support planning | Rank individuals by speed |
| Hint dependency | `hint requests / decisions` | Detect under-scaffolded or over-scaffolded tasks | Call hints cheating |
| Help-seeking quality | Rubric score for timing and specificity of help | Coach better help-seeking | Penalise appropriate help |
| Collaboration / handoff quality | Rubric score for completeness, accuracy, and escalation | Team and incident-response training | Score personality |
| Return practice rate | `learners with a second practice session / starters` | Reinforcement design | Shame low returners |

---

## 7. Metrics to avoid

Do not add these unless a specific, reviewed question requires them:

- raw click counts, mouse distance, or keystroke logs as "engagement";
- a single composite "cyber score";
- time-on-page as attention;
- completion rate as competence;
- leaderboards of speed or hints;
- inferred personality, motivation, or mental-health labels;
- "working-memory capacity" estimated from lab performance alone;
- any metric that cannot be explained to the learner in one sentence.

---

## 8. Minimum reporting checklist

For every metric in a report, include:

- [ ] construct and observable;
- [ ] formula or scoring rule;
- [ ] n and missing data;
- [ ] median or mean with spread, as appropriate;
- [ ] the comparison or baseline;
- [ ] the task, time limit, and aids allowed;
- [ ] the accommodation policy;
- [ ] one limitation;
- [ ] the decision the metric informs.
