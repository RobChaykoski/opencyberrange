# Information design: progressive disclosure

Status: **design rule** (18 November 2026). Applies to every dashboard, matrix,
transcript, and readiness view proposed in this repository.

The platform has a lot of evidence. Showing all of it at once is not
transparency; it is noise. The rule is:

> **Summary first. Detail on request. The learner decides what to keep, pin,
> hide, or ignore.**

Information should accumulate as the learner uses the platform, not arrive in
one overwhelming page. The default view is the smallest useful view.

## 1. Why this rule exists

- A learner opens the profile to answer one question, not to read a data dump.
- An instructor opens the risk dashboard to find the next check-in, not to audit
  every learner.
- An employer opens a transcript to decide whether to read further, not to
  inspect every quiz attempt.
- A lab-health view should surface the one degraded lab, not a wall of green.

Density is available. It is not the default.

## 2. The four layers

Every feature uses the same four layers.

| Layer | What the user sees | Example |
|---|---|---|
| **1. Signal** | One sentence, one number, one status | "SOC Analyst 92% — high confidence" |
| **2. Summary** | Three to five rows or one chart | Capability summary, top five risks |
| **3. Detail** | Expandable sections, tables, evidence | Per-requirement breakdown, artifact list |
| **4. Raw evidence** | Links, hashes, logs, source records | The policy diff, query, timeline, report |

Do not skip from layer 1 to layer 4. Do not put layer 4 on the landing view.

## 3. Default budgets

Use these as hard defaults unless the page has a documented reason:

- **One** primary action per region.
- **One** primary metric or status at the top.
- **Three to five** primary rows or cards.
- **One** chart on the first screen.
- **Two or three** filter controls visible; the rest behind "Filters".
- **No more than two** levels of navigation before content.
- **No full table** above the fold unless the table is the job.

If a page needs more, split it into tabs or sections. Do not solve density by
making the text smaller.

## 4. Cumulative, not exhaustive

Information accumulates over the learner's journey:

- show the current readiness and the **change since last visit**;
- show new artifacts since the last review;
- show the next action, not every completed action;
- show historical evidence only when the learner opens the history;
- keep the record complete but not the first screen.

A learner should be able to say "I know what to do next" after ten seconds.

## 5. User control

Give the user explicit controls, and persist them:

| Control | Behaviour |
|---|---|
| **Pin** | Keep a card or metric at the top |
| **Hide** | Remove from the default view; still available in "Show all" |
| **Snooze** | Hide a flag or suggestion for a chosen period |
| **Dismiss** | Close a one-time notice with a reason |
| **Choose target** | Select one role or job profile as the primary view |
| **Compare** | Add a second role or cohort only on request |
| **Show all** | Reveal the full table or history |
| **Reset view** | Restore the default without losing data |

Do not treat "hidden" as "deleted". Do not treat "dismissed" as "resolved" unless
the feature says so.

## 6. Per-feature defaults

### Learner profile

- Default: current target role, top three capabilities, next action.
- Expand: full capability matrix, all roles, all artifacts.
- Hide: unmeasured capabilities behind "Show unmeasured".
- The learner chooses the target role and which artifacts are shareable.

### Competency matrix

- Default: eight capability rows with score, confidence, and evidence count.
- Expand: sub-skills and evidence links.
- Collapse: domains with no evidence under a single "Not measured yet" row.
- Never show a 212-row competency table on the first screen.

### Role readiness

- Default: one selected role with score, confidence, gates, and top gap.
- Expand: component breakdown, evidence packet, other roles.
- Compare roles only when the learner asks.
- Do not show every role at full detail.

### Workforce readiness and job matching

- Default: one selected job profile.
- Expand: requirement breakdown, packet, employer view.
- Instructor: filter first, then show a short list; expand a learner for detail.
- Do not show every profile for every learner in one table.

### Student risk engine

- Default: top five learners by need, with the primary flag and last action.
- Expand: full breakdown, evidence, suggested actions, history.
- Hide dismissed and snoozed flags from the default queue.
- Show "no action needed" as a count, not as empty rows.
- Never show a full cohort table with every metric.

### Lab health

- Default: counts by status and the degraded/warning labs.
- Expand: one lab with infrastructure, learning signals, errors, and feedback.
- Hide healthy labs behind "Show healthy".
- Do not show every metric for every lab at once.

### Attack simulation dashboard

- Default: event summary, active incidents, service health, and the team's own
  score.
- Expand: full scoreboard, score breakdown, report queue, audit.
- Put the leaderboard behind a tab or "Show leaderboard".
- Keep the stop/pause control visible at all times.

### Digital Cyber Transcript

- Default: identity, capability summary, target-role readiness, verification.
- Expand: completed learning, artifacts, framework coverage, full role list.
- Collapse artifact types; expand to artifact titles; open the evidence last.
- The learner selects which artifacts are shareable.
- The PDF is complete but sectioned; the web view is summary-first.

### Simulated cloud range

- Default: the learner's current lab, role, and next task.
- Expand: the service map, credentials, evidence, reset.
- Collapse the full component catalogue and architecture diagram.
- Do not show all ten lab briefs on one page.

## 7. Visual hierarchy

- Use the existing tokens and components. Do not add a second card system.
- Use `ExpandableSection` for detail that is not needed on first paint.
- Use `<details>` only for secondary detail, never for the primary action.
- Use tabs for parallel views (Overview, Evidence, History), not for sequential
  steps.
- Use one strong number per card. Secondary numbers are smaller and labelled.
- Use colour with a text label and sample size.
- Keep the reading column at a comfortable width; do not stretch tables to the
  viewport.
- On mobile, collapse to the signal and the next action first.

## 8. State and personalisation

Persist per user and per surface:

- pinned cards;
- hidden sections;
- dismissed notices;
- selected target role or job profile;
- selected filters;
- last-seen timestamp for "new since your last visit".

Provide a visible **Reset view** action. A hidden item must remain discoverable
through "Show all" or a settings control.

## 9. Accessibility

- `ExpandableSection` must be keyboard operable and announce expanded state.
- Do not hide essential information only in a tooltip.
- Charts need a table fallback.
- Do not rely on colour alone.
- Respect `prefers-reduced-motion`.
- Keep focus order stable when a section expands.
- Preserve scroll position when a filter changes, unless the user expects a new
  page.

## 10. Anti-patterns

- A dashboard with twelve metrics and no next action.
- A profile that opens with every competency and every artifact.
- A transcript that is a 60-page PDF before the learner has chosen what to share.
- A risk table that ranks the whole cohort by default.
- A lab-health page that shows every healthy lab before the degraded one.
- A leaderboard that hides the score breakdown.
- Hiding information so the learner cannot find it at all.
- Treating "show all" as the default because the data exists.

## 11. Acceptance checklist

- [ ] The first screen answers one question and offers one next action.
- [ ] No more than five primary rows or cards by default.
- [ ] Detail is available within one interaction.
- [ ] The user can pin, hide, snooze, dismiss, and reset.
- [ ] Hidden data is still discoverable.
- [ ] The view remembers the user's choices.
- [ ] A table fallback exists for every chart.
- [ ] The layout works at 375, 768, 1024, and 1440 px.
- [ ] Both themes are checked.
- [ ] Keyboard and screen-reader paths are checked.
- [ ] The PDF transcript remains complete but sectioned.
- [ ] No essential information exists only in colour or a tooltip.
