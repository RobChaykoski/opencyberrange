# Profile and catalogue experience review

Date: **12 November 2026**
Routes reviewed: `/profile`, `/dashboard`, `/courses`, `/courses/:id`,
`/exercises`, `/exercises/:track`, `/events`, `/workbooks`
Personas: a **new student** (0 completions, 0 certificates, 0 badges) and an
**experienced student** (17 completions, 6 certificates, 12 badges, Cyber DNA
67/99, one course). Both were seeded on development `.44`; screenshots are in
`ui-verify-artifacts/profile-review/` and `ui-verify-artifacts/page-review/`.

## Implementation status (12 November 2026)

**Implemented:** P0 data truth (one visible-lab denominator, one course-completion
rule, honest zero-state copy), P1 progressive disclosure (career tabs and the
optional GPS card only appear after evidence; the learning record defaults to
progress-bearing tracks; name prompt in the hero), P2 advanced-learner focus
(course/track/certification/career selector, course/track/certificate progress
lenses, career target promoted to the top of the portfolio, mobile tab scroll
cue), and the token-colour fixes for workbook actions and profile status
badges. Course-card percentages now round half-up to match the course page.

**Remaining:** a filter/compact mode for the title collection and replacing
emoji achievement badges with the SVG icon system.

## Design test report

- **Scope:** profile and learner catalogue only; no routes, permissions, or
  lab lifecycle changed.
- **Theme check:** light and dark checked on the profile; light checked on the
  cross-page crawl.
- **Layout check:** 1440 px desktop and 390 px mobile; no horizontal page
  overflow on the checked views.
- **Accessibility check:** tab roles, labels, progress bars, and empty states
  present. Mobile tab bar overflows without an explicit scroll cue.
- **Build/lint:** existing build and lint pass. No console errors on the eight
  crawled pages.
- **Verdict:** **PASS WITH FIXES.** The visual system is coherent; the main
  problems are data truth, progressive disclosure, and career relevance.

## What already works

- The slate/blue token system, card radii, borders, and light/dark surfaces are
  consistent across Dashboard, Courses, Exercises, and the track page.
- The profile tab structure is clear and keyboard-operable. The Overview,
  Skill tree, Learning record, Account, and Security separation is sound.
- The new-student Skill tree empty state is excellent: it explains the model,
  gives three concrete steps, and offers **Find your first exercise**.
- The experienced profile has genuinely useful evidence: certificates,
  completion detail, Cyber DNA branches, titles, momentum, and a career
  target selector.
- The track page is information-rich without losing the next action.

## New student: what I would like and not like

### I would like

1. **One obvious start.** A compact "Start here" card with one recommended
   beginner exercise, the expected time, and a single **Start exercise**
   action. The current first recommendation is a career affinity with zero
   evidence, which is not a starting point.
2. **Plain-language definitions.** Explain "branch", "99", "clean solve", and
   "certificate" on first use, with a **How this works** link. The current
   "branch above 60" language assumes the model has already been learned.
3. **A reason to add a name.** The hero falls back to the username and the
   avatar initials are derived from it. Offer **Add your name for
   certificates** in the hero, not only in Account.
4. **Small, honest progress.** "0 of 139" is accurate but intimidating. Show
   "0 exercises completed" and "Your first certificate needs 5 exercises"
   instead of a range-wide percentage.
5. **A shorter Learning record.** Show enrolled courses and started tracks
   first, then a collapsed **Browse all tracks** list. A new learner does not
   need every level of every track on day one.

### I would not like

1. **Career judgments before evidence.** Cyber GPS shows **SIGNAL FADING**,
   "0 evidence points", and "0 recent completions"; Portfolio opens on
   **"I want to become a SOC Analyst"** and **"Not Ready"**. These read as
   negative judgments about a learner who has not started.
2. **Seven tabs before the first lab.** Cyber GPS and Portfolio are fully
   present for a zero-evidence learner. They should be locked, previewed, or
   introduced after the first completed exercise.
3. **A wall of zeros.** The Learning record renders every track and every
   level as "Not started" (139 exercises). It is demotivating and hides the
   one action that matters.
4. **Duplicate class labels.** The Overview shows "Recruit / Recruit" and says
   "Your highest branch is Recruit." Recruit is a class, not a branch. With no
   evidence the copy should say the first branch appears after one exercise.
5. **The optional GPS prompt before the profile content.** On mobile it takes
   most of the first screen before the learner sees their own profile.

## Experienced student: what I would like and not like

### I would like

1. **A focus selector that drives the page.** Let me choose:
   - my enrolled course,
   - a target track,
   - a certification path,
   - or a career goal.
   Then show progress and the next action for that focus, with range-wide
   progress as a secondary line.
2. **Separate progress lenses.** Today the hero says **12% complete** while I
   hold **6 certificates**. Show:
   - course progress (for example 8/8 assigned),
   - track progress (8/53),
   - certificate progress,
   - range-wide progress (17/139 or 17/179, explicitly labelled).
3. **Career goal selection at the top.** The target-role select exists in
   `RoleReadinessPanel.vue`, but it is buried inside the collapsed **Career
   readiness** section on the Portfolio tab. Put the target role and career
   family at the top of the career area.
4. **Filters on the Learning record.** Show "in progress", "complete", and
   "not started" tracks; default to progress-bearing tracks and collapse the
   rest. The certificate cards themselves are good and should stay prominent.
5. **A compact title collection.** The Skill tree title grid is long. Keep the
   equipped title and recently earned titles visible; put the full collection
   behind a filter or "Show all".

### I would not like

1. **A low global percentage that contradicts my certificates.** 12% across
   the whole range does not reflect 6 completed levels. It makes the
   certificates feel disconnected from progress.
2. **Career direction split across two tabs.** Cyber GPS and Portfolio overlap:
   GPS shows direction and evidence; Portfolio shows readiness, evidence, and
   taxonomy. I have to remember which tab holds the control I need. One
   **Career** hub with three clear sections would be easier.
3. **Five equal 80.6 competency scores.** Several "strongest competencies"
   showed exactly 80.6. That looks like a normalisation artefact and weakens
   trust in the ranking. Either show the underlying evidence or label the
   score as relative.
4. **A 40-hour target with no explanation.** "15.5 of 40 hours" needs a short
   explanation that 40 hours is the continuing-education practice target, not a
   grade or a deadline.
5. **Workbook buttons in legacy orange.** The track page uses `#e67e22` for
   every **Workbook** button. Orange reads as warning and bypasses the token
   system; the same page uses blue for the primary launch action.

## Cross-page consistency findings

### Major: two different exercise totals for the same learner

- Dashboard hero: **17 / 179 exercises, 9%**.
- Profile hero: **17 / 139 exercises, 12%**.

The dashboard counts all active labs; the profile counts the labs visible to
that learner. Both are labelled "exercises" with no scope. Pick one
denominator, or label the scopes explicitly.

References:
`platform/backend/app/routers/dashboard.py` (totals around lines 1323–1349)
and `platform/backend/app/routers/profile.py` (totals around lines 318–326).

### Major: course progress uses two different rules

For the same experienced learner and the same course:

- Dashboard completion matrix: **8 / 8 complete**.
- Course detail page and Courses card: **0 / 8, 0%**.

The dashboard matrix counts any global completion
(`dashboard.py` around line 1466), while the course page uses the
enrolment/reset-aware helper in `courses.py` around lines 224–278. A
completion before enrolment counts on one page and not the other. Use one rule
everywhere, and show "completed before enrolment" explicitly if that is the
intended behaviour.

### Major: zero-evidence career surfaces are presented as findings

`Profile.vue` (around lines 326–333 and 460–498) renders the first affinity and
the full career panels even when every branch is zero. `topAffinity` selects the
first affinity when none is recommended. A new learner sees a career direction,
"signal fading", and "Not Ready" before completing one exercise.

### Minor: legacy colours bypass the token system

`Profile.vue` contains hardcoded status colours (`#10b981`, `#dc2626`,
`#2563eb`, `#e2e8f0`, and others). `TrackDetail.vue` uses `#e67e22` and
`#d35400` for workbook buttons (around lines 3005–3035). These do not follow
`--success`, `--danger`, `--accent`, `--text-primary`, or the shared button
system, and they can drift in light/high-contrast themes.

### Minor: mobile tab bar has no overflow affordance

At 390 px the profile tab bar is horizontally scrollable but looks cut off
after "Learning". Add a fade/arrow cue or allow the tabs to wrap.

### Minor: badge icons use emoji while the rest of the UI uses SVG

Profile recognition badges render emoji. They are labelled, so this is not an
accessibility failure, but the icon style is inconsistent with the SVG icon
system used elsewhere.

## Recommended changes, in order

### P0 — make the numbers true

1. Unify the exercise denominator across Dashboard, Profile, Courses, and
   Exercises. Use the visible catalogue as the default and label range-wide
   counts separately.
2. Use the same enrolment/reset-aware completion rule for the dashboard matrix,
   course detail, course card, and profile course progress.
3. Fix zero-state copy: remove "Your highest branch is Recruit", remove the
   duplicate Recruit label, and do not show a career affinity when there is no
   evidence.

### P1 — progressive disclosure

4. New learner mode: hide or lock Cyber GPS and Portfolio until the first
   completion (or until the learner chooses a career goal). Replace them with a
   single **Build your first evidence** card.
5. New learner Learning record: show enrolled/started tracks first and collapse
   the full catalogue behind **Browse all tracks**.
6. Add an **Add your name for certificates** action in the hero when the
   display name is still the username.

### P2 — give experienced learners control

7. Add a focus selector at the top of the profile: course, track, certification,
   or career goal. Drive the hero and next-step cards from that focus.
8. Split progress into course / track / certificate / range-wide lenses.
9. Surface the target-role selector at the top of the career area, not inside a
   collapsed panel.
10. Add filters and a compact default to the Learning record and title
    collection.

### P3 — visual consistency

11. Replace `#e67e22`/`#d35400` workbook buttons with a token-based secondary
    action; reserve warning amber for actual warnings.
12. Replace hardcoded status colours in `Profile.vue` with `--success`,
    `--danger`, `--accent`, and `--text-primary`.
13. Add a visible scroll cue to the mobile profile tabs, or wrap them.

## What I would not change

- Keep the certificate cards, completion detail, and PDF download prominent.
- Keep the Skill tree and career atlas; they are a real differentiator for
  experienced learners.
- Keep the tab structure, but make the tabs earned rather than all visible on
  day one.
- Keep the current brand gradient and card system; the problem is hierarchy and
  data truth, not the palette.
