# Attack simulation dashboard

Status: **proposal** (18 November 2026). Extends the existing event and
competition model; it is not a replacement for the course labs or the team
scenario design.

Presentation follows [progressive disclosure](INFORMATION-DESIGN-PROGRESSIVE-DISCLOSURE.md): summary first, detail on request, and the learner controls what stays visible.

This is the live event view for a blue-team/red-team exercise, in the spirit of a
Collegiate Cyber Defense Competition (CCDC). The dashboard must show the state of
the exercise, not only a scoreboard.

## 1. Event model

| Role | Responsibility |
|---|---|
| **White team** | Runs the event, controls injects, scores, resolves disputes, can pause or stop |
| **Red team** | Executes authorised attacks inside the rules of engagement |
| **Blue team** | Defends services, investigates incidents, submits reports |
| **Green team** | Optional observers, judges, or support |
| **Safety lead** | Owns the stop control, isolation, and escalation |

An event has:

- a scenario and rules of engagement;
- teams, participants, and roles;
- a service catalogue and availability checks;
- a set of injects;
- a scoring policy;
- a start and end time;
- a pause/stop control;
- an audit record.

## 2. Live dashboard

Organizer view:

```text
Live Exercise — Healthcare Cloud Defence
  Participants        197
  Teams                28
  Compromises          42
  Active incidents     17
  Reports submitted    89
  Services up          94.2%
  MTTR                 37 min
  MTTD                 11 min
  Elapsed              02:14:36
```

Below the summary:

- **Service health** — each service, owner team, uptime, last check.
- **Incident queue** — severity, team, service, age, owner, status.
- **Inject timeline** — released, scheduled, cancelled.
- **Scoreboard** — team score with a breakdown, not only a total.
- **Report queue** — submitted, reviewed, returned.
- **Alerts** — platform incident, rule violation, unsafe action.

Participant view:

- team score and rank (if the event publishes a leaderboard);
- service health for their team;
- active incidents and assigned owner;
- injects and deadlines;
- submitted reports and feedback;
- rules of engagement and stop/help path.

## 3. Scoring

A transparent, multi-dimensional score:

| Component | Example weight | Evidence |
|---|---:|---|
| Service availability | 35% | Uptime checks and restore time |
| Incident response | 25% | Detection, containment, recovery, MTTR |
| Reports | 20% | Technical and executive reports, reviewed |
| Injects | 10% | Completed inject tasks |
| Flags and objectives | 10% | Authorised challenge flags |
| Penalties | variable | Unsafe action, rule violation, false report |

Rules:

- Publish the score policy before the event.
- Show the breakdown beside the total.
- Use a score freeze window for disputes.
- Separate **availability** from **security** so a team cannot win by disabling
  a service.
- Penalise unsafe or out-of-scope action, not a failed defence.
- Do not reward a team for attacking another team outside the rules.
- Keep a white-team override with an audit reason.

Example leaderboard:

| Team | Availability | IR | Reports | Injects | Total |
|---|---:|---:|---:|---:|---:|
| Blue Team 4 | 330 | 245 | 210 | 90 | 925 |
| Blue Team 7 | 310 | 230 | 205 | 86 | 881 |
| Blue Team 2 | 300 | 225 | 200 | 90 | 865 |

The total is not meaningful without the breakdown.

## 4. Metrics

| Metric | Definition |
|---|---|
| **MTTD** | Time from the first observable event to the first correct detection |
| **MTTR** | Time from detection to verified restoration |
| **Compromises** | Confirmed loss of a service, host, or credential |
| **Active incidents** | Open incidents not yet contained |
| **Reports submitted** | Reports in the queue, including returned reports |
| **Service uptime** | Successful checks divided by total checks |
| **False positives** | Alerts closed as benign after investigation |
| **Containment rate** | Incidents contained within the scenario target |
| **Recovery rate** | Services restored to a verified baseline |

MTTR is calculated per incident and aggregated as a median, not a mean, so one
long incident does not hide the rest. Show the sample size.

## 5. Real-time architecture

```text
Lab events -> event bus (Valkey/Redis) -> score engine -> dashboard (SSE/WebSocket)
                                      -> audit store
                                      -> snapshot store
```

- The score engine is deterministic and versioned.
- Every score change has an audit entry: input, rule, before, after, actor.
- The dashboard reads a materialized snapshot, not the raw event stream.
- If the event bus is unavailable, the dashboard shows **stale** and the last
  update time; it does not show a blank score.
- The white team can pause scoring without pausing the lab.
- A recalculated score keeps the old value and the reason.

## 6. Data model

Reuse the existing competition and participant tables where possible.

| Table | Purpose |
|---|---|
| `simulation_events` | Event, scenario, rules, start/end, state |
| `simulation_teams` | Team, name, captain, members |
| `simulation_services` | Service, owner, check, target uptime |
| `simulation_incidents` | Incident, team, service, severity, state, detected_at, contained_at, restored_at |
| `simulation_injects` | Inject, release time, target, content, state |
| `simulation_reports` | Report, team, type, reviewer, score, feedback |
| `simulation_scores` | Event, team, component, value, rule version, created_at |
| `simulation_audit` | Actor, action, object, before, after, reason, created_at |

## 7. Fairness and integrity

- Isolate each team's network and services.
- Use unique flags and credentials per team.
- Rate-limit submissions and report uploads.
- Log every score change and every white-team override.
- Freeze the scoreboard during a dispute window.
- Do not publish another team's incident details.
- Publish the rubric and the penalty policy before the event.
- Review a sample of scores after the event.
- Provide a correction path and a public changelog for score changes.

## 8. Safety and legal

- Use synthetic data and isolated infrastructure. No real patient, learner, or
  institutional data.
- Publish rules of engagement and a stop control.
- Prohibit destructive attacks, real malware, and attacks on the platform or
  other teams outside the scenario.
- Provide a safety lead and an escalation path.
- Stop the event if a participant is unsafe or a service affects production.
- Keep an incident log for the event itself.
- Do not stream sensitive learner data to a public leaderboard.

## 9. CCDC-style scenario

Example: a hospital cloud defence event.

- Services: patient portal, identity provider, object store, reporting API.
- Injects: a new compliance requirement, a backup failure, a press inquiry.
- Red team: authorised credential access, storage exposure, consent abuse.
- Blue team: detect, contain, restore, report.
- White team: score availability, IR quality, report quality, inject handling.
- Green team: observe and review.

The scenario is not a free-for-all. The red team stays inside the rules; the
blue team is scored on defence and communication, not only on flags.

## 10. Implementation phases

1. **Phase 1 — event summary.** Extend the existing competition view with
   participants, services, incidents, reports, and MTTR. No new live transport.
2. **Phase 2 — live updates.** Add SSE or WebSocket snapshots and stale-state
   handling.
3. **Phase 3 — score engine.** Component scores, rule version, audit, freeze,
   and override.
4. **Phase 4 — participant view.** Team-scoped dashboard and report queue.
5. **Phase 5 — CCDC pilot.** One event with a white/red/blue/green team and a
   post-event review.

## 11. Acceptance criteria

- The organizer sees participants, teams, services, incidents, reports, uptime,
  MTTD, and MTTR.
- Every score has a breakdown and an audit entry.
- A stale dashboard says it is stale.
- A team cannot see another team's private incident data.
- The white team can pause, freeze, correct, and stop.
- The event runs without real data, real malware, or production impact.
- A post-event report shows the score changes and the review.

## 12. Anti-patterns

- A scoreboard with no breakdown.
- Rewarding a team for taking a service offline.
- Hiding a score change.
- Letting the red team attack outside the rules.
- Publishing one team's incident details to another team.
- Treating MTTR as a single mean with no sample size.
- Running the event without a stop control.
