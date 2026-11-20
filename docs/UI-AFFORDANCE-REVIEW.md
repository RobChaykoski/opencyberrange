# UI affordance and signifier review

Status: **findings recorded; P1–P4 fixed in 5.28.6, P5–P7 open.**
Scope: `platform/frontend/src` (90+ SFCs).
Companion: `opencyberrange-ha/docs/13-ha-status-panel.md` (read-only HA panel).

## The lens

An **affordance** is an action possibility. A **signifier** is the cue that
makes it perceivable: a label, an icon, a raised edge, an underline.

Software has almost no inherent affordances — a `<div>` does not look pressable
the way a physical button does. Everything is convention, so the cue *is* the
contract. That produces two failure modes worth reviewing for:

- **False affordance** — something looks actionable and is not, or looks
  harmless and is destructive.
- **Hidden affordance** — something is actionable with no cue at all.

A third, quieter failure: a status that communicates by colour alone.

## Method

1. Automated scan of every SFC template for click handlers on non-interactive
   elements without `role`/`tabindex`/key handlers, anchors without a real
   `href`, buttons without a `type`, icon-only buttons without a label, and
   `cursor: pointer` on selectors that are not controls.
2. Manual read of every high-severity hit in context — the scan cannot tell a
   modal backdrop from a false affordance.
3. Fixed the four patterns that carried real user impact; recorded the rest.

Result at 5.28.5: **518 flags, 41 high-signal**. After triage, 12 were modal
overlays, 2 were copy-on-click text, 1 was a badge used as a button, 1 was a
misleading dismiss header; the rest repeated those shapes in
`InstructorPanel.vue` and `InstructorDashboard.vue`.

After 5.28.6 the same scan reports **466 flags, 23 high**. The scanner now
recognises `v-modal-dialog` and a backdrop that closes on Escape, so the fixed
overlays no longer appear; the 23 that remain are the backlog below, not
regressions.

Re-run:

```bash
python scripts/audit-ui-affordances.py            # human summary
python scripts/audit-ui-affordances.py --json     # machine output
```

## What was already correct

| Pattern | Where | Why |
|---|---|---|
| `cursor`/hover/focus scoped to `role="button"` | `Admin.vue`, `.stat-card[role="button"]` | The cue exists only when the action does |
| Full dialog contract | `components/ConfirmDialog.vue` | `role`, `aria-modal`, labelledby/describedby, focus to Cancel, `danger` styling, busy label |
| Keyboard-operable card | `Admin.vue`, System health card | `role`, `tabindex`, Enter **and** Space, `aria-label` |
| Status is never colour-only | `Admin.vue`, `health-dot` + `health-card-status` | The word is always present |
| Effect-explaining titles | `TrackDetail.vue`, pause/resume | "credit the paused time" is a consequence, not a label |

These are the templates to copy, not exceptions to tolerate.

## Findings

| ID | Severity | Location (5.28.5) | Problem | Status |
|---|---|---|---|---|
| P1 | High | `Admin.vue`, 12 `modal-overlay` blocks | Backdrop click dismissed; **no** Escape handler, only 2 of 12 declared `role="dialog"`/`aria-modal`; focus never moved into the dialog and could tab behind it | **Fixed 5.28.6** |
| P2 | High | `Admin.vue` invite code (table cell, course header) | `<code @click>` copied to clipboard with no label, no keyboard path; one site papered over it with inline `cursor: pointer` | **Fixed 5.28.6** |
| P3 | High | `Admin.vue`, exercise-tester `Report` badge | `<span @click>` inside a `<label>`; looked like part of the row control, unreachable by keyboard | **Fixed 5.28.6** |
| P4 | Medium | `Admin.vue`, scan-warnings header | The whole header cleared the list; only the `×` glyph hinted at it | **Fixed 5.28.6** |
| P5 | Medium | `ConsentPanel`, `CoursePlanningPanel` (×3), `IdentityProvidersPanel` (×2), 43 total | Destructive actions use `window.confirm()`: browser chrome, no object name, no danger styling, blocking | Open |
| P6 | Low | 376 `<button>` elements | No explicit `type`; the default is `submit`. Harmless until a `<form>` wrapper appears | Open |
| P7 | Low | tester status dots, `T`/`F` badges | Explain themselves only through `title`, which touch and keyboard users never see | Open |
| P8 | Medium | `InstructorPanel.vue` (10 flags) | Repeats P1–P4: clickable rows without roles, overlays without Escape, badges as buttons | Open |
| P9 | High | `ChangePassword.vue:52`, `Dashboard.vue:68` | Icon-only buttons with no accessible name | Open |
| P10 | High | `Course.vue:78` | Clickable `<tr>`: a mouse-only row action with no keyboard equivalent | Open |
| P11 | Medium | `InstructorDashboard.vue:401` | Clickable `<h2>` (sort/expand) with no role or keyboard path | Open |
| P12 | Medium | `FlagCelebration.vue:4`, `PulseSurveyModal.vue:3`, `ReauthDialog.vue:2` | Modal-shaped components without the full dialog contract (Escape, trap, labelledby) | Open |
| P13 | Low | `TrackDetail.vue:134,1067`, `WorkbooksLanding.vue:15,29`, `App.vue:48` | Clickable containers with no role, no tabindex, no key handler | Open |

### Remaining high findings at 5.28.6

```
App.vue:48                              click on <div> without role/tabindex/key
components/FlagCelebration.vue:4        click on <div> without tabindex/key
components/PulseSurveyModal.vue:3       click on <div> without role/tabindex/key
components/ReauthDialog.vue:2           click on <div> without tabindex/key
views/ChangePassword.vue:52             icon-only <button> without aria-label/title
views/Course.vue:78                     click on <tr> without role/tabindex/key
views/Dashboard.vue:68                  icon-only <button> without aria-label/title
views/InstructorDashboard.vue:29        click on <div> without role/tabindex/key
views/InstructorDashboard.vue:401       click on <h2> without role/tabindex/key
views/InstructorPanel.vue:228           click on <code> without role/tabindex/key
views/InstructorPanel.vue:231,688,755   click on <div> without role/tabindex/key
views/InstructorPanel.vue:766,1163      click on <div> without role/tabindex/key
views/InstructorPanel.vue:1202          click on <span> without role/tabindex/key
views/InstructorPanel.vue:1281,1352,1407 click on <div> without role/tabindex/key
views/TrackDetail.vue:134,1067          click on <div> without role/tabindex/key
views/WorkbooksLanding.vue:15,29        click on <div>/<span> without role/tabindex/key
```

## What shipped in 5.28.6

### `v-modal-dialog` directive

`platform/frontend/src/directives/modalDialog.js`, registered globally in
`main.js`, applied to all 12 admin overlays. It adds:

- `role="dialog"`, `aria-modal="true"`, `tabindex="-1"`;
- `aria-labelledby` wired to the first `.modal-title`, `h2`, or `h3` inside,
  generating an id when needed;
- Escape closes via the same handler the backdrop click uses;
- focus moves to the first control on open, Tab and Shift+Tab wrap inside, and
  focus returns to the trigger on close.

A directive rather than a component: the overlays carry their own scoped styles,
so a rewrite would have been a large diff with no behaviour gained.

### `CopyCode.vue`

A real `<button>` with a copy icon, `aria-label="Copy invite code"`, and an
inline "Copied" confirmation in an `aria-live` region. Falls back to
`document.execCommand('copy')` when the Clipboard API is unavailable (plain HTTP
lab installs).

### Smaller fixes

- `Report` badge is now `<button type="button">` with an `aria-label` naming the
  lab and status.
- The scan-warnings `×` is a labelled button; the header is inert.
- `ConfirmDialog` closes on Escape.
- `.tester-badge` and `.scan-warnings__dismiss` were adjusted for native button
  rendering.

### Tests

`src/directives/__tests__/modalDialog.test.js` and
`src/components/__tests__/CopyCode.test.js`: dialog semantics, Escape, focus
entry, Tab wrap, clipboard write, and the inline confirmation.

## Backlog

**P5 — replace native confirmations.** Build the pattern once: a
`useConfirm()` composable that renders `ConfirmDialog` with `danger`, the object
name in the message, and a typed confirmation for irreversible actions. Then
migrate the 43 call sites component by component. Acceptance: no
`window.confirm(` in `src`, and each destructive action names what it destroys.

**P6 — explicit button types.** Mechanical sweep adding `type="button"` where the
attribute is absent, holding back any button that intentionally submits a form.
Acceptance: no `<button>` without a type, and the auth/registration forms still
submit on Enter.

**P7 — hover-only labels.** Give the tester dots and `T`/`F` badges visible text
or `aria-label`; keep `title` as a bonus, not the only channel.

**P8 — InstructorPanel parity.** Apply the same four fixes. Acceptance:
`audit-ui-affordances.py` reports no high-severity hits in the file.

## Rules for new UI

1. **If it is not actionable, it must not look actionable** — no pointer, no
   hover lift, no chevron. The HA panel is deliberately plain text for this
   reason.
2. **If it is actionable, say what it does** — a verb in the label, a title for
   consequences, an icon only alongside an `aria-label`.
3. **If it destroys, it must look destructive** — danger styling, the object
   named, and confirmation proportional to the loss.
4. **Never colour alone** — pair every state dot with a word.
5. **Feedback follows the action** — a copy confirms inline; a save reports
   where the result went.
6. **Keyboard is a first-class path** — if a mouse can reach it, Tab can too,
   and Escape closes what a backdrop click closes.

## Limits of this review

The scan is heuristic. It cannot judge whether a label is honest, whether a
warning is proportionate, or whether a flow makes sense. It also cannot see
runtime-composed markup inside render functions. Treat the count as a starting
point, and read the high-severity hits in context before changing anything.
