---
name: OpenCyberRange Design Tester
description: Review UI changes made with the OpenCyberRange Design skill. Use after a design change to verify the view, light and dark themes, layout, filters, table density, responsive behaviour, accessibility, and build/lint status against the project's design system and the design skill's rules.
---

# OpenCyberRange Design Tester

Use this skill **after** a change made with the OpenCyberRange Design skill, or
when reviewing an existing screen for design quality. The design skill is the
source of truth for what to build. This skill is the independent review that
asks whether the result actually works as a view, in both themes, at real
widths, and with real filter states.

Do not use this skill to restyle a page or add a feature. Use it to find gaps,
record evidence, and send the change back to the design skill if it fails.

## Inputs

Collect these before reviewing:

- the route and the target view (`platform/frontend/src/views/...`);
- the changed files (`git diff --stat` and `git diff`);
- the design skill and its references:
  - `.opencode/skills/opencyberrange-design/SKILL.md`
  - `references/design-system.md`
  - `references/page-patterns.md`
  - `references/accessibility-and-qa.md`
  - `references/frontend-conventions.md`
- `platform/frontend/src/App.vue` (tokens and shared rules);
- build and lint output;
- screenshots or a running preview when available.

If there is no running preview, say so. Do not claim a visual check you did not
perform.

## Review order

Work in this order so a structural problem is not hidden by a colour nit.

### 1. Scope and product safety

- The route, API contract, permissions, lab lifecycle, and data semantics are
  unchanged unless the task explicitly changed them.
- No secret, flag, VPN key, or student PII is added to UI copy, screenshots, or
  logs.
- Destructive actions still have a confirmation, a clear consequence, and a safe
  default.
- The change does not add a new framework, CSS library, or parallel theme.

### 2. View and task fit

- The page still serves its primary job. Admin and instructor screens are
  operational: density and scanability beat a marketing layout.
- The hierarchy is obvious at a glance: page title, primary action, filters,
  data, secondary actions.
- New columns or controls earn their width. If a column is rarely useful, move
  it into a detail view rather than taking space from the table.
- Long content has a defined behaviour (wrap, truncate with a title, or scroll).
- Loading, empty, error, disabled, permission-denied, and long-content states
  exist where the view can reach them.

### 3. Light and dark mode

- Every new surface, border, badge, overlay, table row, chart, and focus ring is
  checked in both the default dark theme and `[data-theme="light"]`.
- Colours come from the existing tokens (`--bg-primary`, `--bg-secondary`,
  `--text-primary`, `--text-secondary`, `--text-muted`, `--border-color`,
  `--accent`, `--success`, `--warning`, `--danger`). No new palette.
- Status is not communicated by colour alone; pair it with text, an icon, or a
  shape.
- Contrast is readable for body text, muted text, badges, and disabled states.
- Hardcoded hex values are acceptable only when they already exist in the
  design system for that component; new ones are a finding.

### 4. Layout and responsive behaviour

- Check at roughly 320 px, 768 px, 1024 px, and 1440 px.
- Filter bars wrap instead of overflowing.
- Tables either scroll horizontally with a clear affordance or switch to a
  stacked/card layout on narrow screens.
- Action buttons remain reachable and do not wrap into an unreadable column.
- The page does not introduce horizontal page scroll; only the table container
  may scroll.
- Sticky headers, pagination, and summaries do not overlap content.
- Text zoom and long usernames/emails do not break the row.

### 5. Filters and data controls

- Search covers every field the placeholder promises (for example name,
  username, email, and student ID).
- Filters compose correctly. Test at least one combination, not one filter at a
  time.
- The active filter state is visible; a clear/reset action exists and clears all
  filters, not just one.
- The result count matches the filtered list and says whether results are
  filtered.
- Pagination resets to page 1 when filters change and clamps when the result set
  shrinks (including after a delete).
- An empty result has a useful empty state with a way back, not a blank table.
- Filter controls have visible labels or accessible names; placeholder text is
  not the only label.
- Keyboard users can reach and operate every filter and the clear action.
- A filter does not silently hide a row that the user just acted on without
  explanation.

### 6. Table and column quality

- The table has a clear primary column (the thing an operator scans first).
- Role and status are separate concepts. Do not encode both in one badge.
- Dates show a human label (relative or short) and expose the exact timestamp in
  a `title` or detail view.
- Empty values say `Never`, `Not set`, or `-` consistently; do not leave a blank
  cell.
- Actions have accessible names, not icon-only mystery buttons without a title.
- Column order matches the operator's task: identity, state, last activity,
  secondary metadata, actions.

### 7. Accessibility

- Every input has a label or `aria-label`.
- Every icon-only button has a title or visually hidden text.
- Focus is visible and in a logical order.
- The table uses `scope="col"` on headers where appropriate.
- Status is not colour-only.
- Motion respects reduced-motion expectations; no decorative animation on an
  operational screen.
- Screen-reader-only text exists for visual-only status marks.

### 8. Verification

Run the checks that match the change:

```sh
cd platform/frontend
npm run build
npx eslint src/views/<ChangedView>.vue
```

If the change touched an API contract or a serializer, also run the relevant
backend tests:

```sh
cd platform/backend
TEST_DATABASE_URL=sqlite:///./tmp-design-test.db python -m pytest tests/test_<relevant>.py -q
```

Record the exact commands and the pass/fail result. A build is not a visual
check, and lint is not a design review.

## Severity

| Severity | Meaning | Action |
|---|---|---|
| Blocker | Broken view, unreadable theme, inaccessible control, data loss, or scope break | Send back to the design skill |
| Major | A state or filter is missing, table unusable at a supported width, or a misleading status | Fix before merge |
| Minor | Inconsistent spacing, weak hierarchy, missing title, avoidable truncation | Fix if cheap; otherwise record |
| Nit | Taste-level polish with no usability impact | Optional |

## Report format

Return this report, even when everything passes:

```text
## Design test report

View / route:
Changed files:
Scope check:
Theme check (dark / light):
Layout check (320 / 768 / 1024 / 1440):
Filter and data check:
Accessibility check:
Build / lint:
Findings:
- [Blocker|Major|Minor|Nit] <file:line> — <what> — <why it matters>
Verdict: PASS | PASS WITH FIXES | FAIL
Not verified:
```

## Do not approve when

- A new colour bypasses the token system.
- Only the dark theme was checked.
- The filter bar overflows at a supported width.
- A filter combination produces an empty table with no explanation.
- Pagination can point past the last page.
- A status is colour-only or an icon-only action has no accessible name.
- The change silently alters an API contract, permission, or route.
- The report claims a browser check that was not performed.

## Relationship to the design skill

The design skill decides what to build and owns the tokens and conventions. This
skill checks the result. If the two disagree, the design skill wins on intent
and tokens; this skill wins on evidence and release readiness. Record the
disagreement instead of quietly restyling the page.
