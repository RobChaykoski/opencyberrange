# Learner-visible scores

Status: **implemented for DNA, portfolio, readiness, and competency views; regression-tested**.
The transcript PDF and exported reports still need the same audit.

Release 6.0 requires that a learner never sees a low score where the honest
answer is **no evidence**.

## The rule

| State | What the learner sees |
|---|---|
| No evidence | **Unmeasured** or **No practice evidence yet**, never `0` |
| Evidence below the threshold | A score marked **provisional**, with the evidence count |
| Evidence at or above the threshold | A score, with the evidence count and coverage |

A zero is a measurement. Absence is not a zero.

## Where it applies

- Cyber DNA and the competency radar.
- The portfolio hero and skill bars.
- Role readiness dimensions.
- The competency taxonomy details.
- The instructor readiness panel, which uses **No evidence** for an empty axis.

The API keeps the score `null`; the client must not coerce it to `0`. Sorting may
use `score || 0` internally, but display may not.

## What changed

- `CareerAtlas.vue` shows **No practice evidence yet** when `overall` is null.
- `CyberDiscoveryPanel.vue` says **No practice score yet. This is unmeasured,
  not a zero.**
- `PortfolioPanel.vue` shows **practice score unmeasured** and omits the skill
  bar fill when a skill has no score.
- `InstructorReadinessPanel.vue` omits the bar fill and exposes
  `aria-valuetext="No evidence"`.
- `CompetencyTaxonomy.vue` omits a dimension bar when the dimension is null.

## Regression test

`platform/frontend/src/components/__tests__/CareerAtlas.test.js` mounts the
component with `overall: null` and asserts that `0/99` is absent and the
unmeasured text is present. It also asserts a real score still renders.

## Remaining audit

- Transcript PDF and profile report.
- Exported CSV/PDF competency rows.
- Admin and instructor aggregate exports.
- Any new component that formats a competency score.

A new score surface should add the same test before it ships.
