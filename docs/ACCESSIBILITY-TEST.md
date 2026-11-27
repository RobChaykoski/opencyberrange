# Accessibility test plan

Target: **WCAG 2.2 Level AA** for the learner-facing application, with WCAG 2.1
AA as the procurement baseline. This is a test plan, not a conformance claim.
A VPAT/ACR requires an independent audit.

Scope: login, registration, catalogue, course, lab briefing, flag submission,
RangeBox, achievements, certificate/transcript, charts, profile, and privacy
settings. The workbook/wiki is generated HTML and needs the same checks on its
tables and diagrams.

## 1. Test matrix

| Environment | Combination | Why |
|---|---|---|
| NVDA + Chrome/Edge | NVDA current stable, Windows 11 | most common Windows screen reader |
| JAWS + Chrome | JAWS current, Windows 11 | enterprise procurement baseline |
| Windows Narrator + Edge | Windows 11 | no third-party install |
| Keyboard only | Chrome and Firefox, no mouse/trackpad | WCAG 2.1.1 |
| Zoom | 200% and 400%, 1280px and 390px widths | WCAG 1.4.4, 1.4.10 |
| High contrast | Windows contrast theme, forced colors | WCAG 1.4.3, 1.4.11 |
| Reduced motion | `prefers-reduced-motion: reduce` | WCAG 2.3.3 |
| Color blindness | protanopia, deuteranopia, tritanopia, achromatopsia | WCAG 1.4.1 |
| Mobile | iOS Safari and Android Chrome, 390x844 | orientation/reflow |

Use a staging deployment and a disposable learner account. Do not record a
minor. Do not put names, emails, or tokens in the report.

## 2. WCAG 2.2 AA checklist

Mark each `Pass`, `Fail`, `Partial`, or `N/A`. A `Partial` needs an issue id.

### Perceivable

| Criterion | Test focus | Result |
|---|---|---|
| 1.1.1 Non-text content | every image/icon has a text alternative; decorative icons are hidden | |
| 1.2.1–1.2.5 Media | N/A unless learner-facing audio/video; captions and description if present | |
| 1.3.1 Info and relationships | headings, lists, tables, form labels, landmarks | |
| 1.3.2 Meaningful sequence | DOM order matches visual order in the shell, lab panel, and tables | |
| 1.3.3 Sensory characteristics | instructions do not rely on "the green button" alone | |
| 1.3.4 Orientation | portrait and landscape both work | |
| 1.3.5 Identify input purpose | login, registration, profile fields use correct `autocomplete` | |
| 1.4.1 Use of color | status, errors, charts, and links are not color-only | |
| 1.4.2 Audio control | no autoplay audio | |
| 1.4.3 Contrast (minimum) | body text 4.5:1; large text 3:1 | |
| 1.4.4 Resize text | 200% zoom without loss | |
| 1.4.5 Images of text | avoid; use real text | |
| 1.4.10 Reflow | 320 CSS px width, no two-dimensional scroll | |
| 1.4.11 Non-text contrast | controls, focus rings, chart lines 3:1 | |
| 1.4.12 Text spacing | line/letter/word spacing overrides do not clip | |
| 1.4.13 Content on hover/focus | tooltips dismissible, hoverable, persistent | |

### Operable

| Criterion | Test focus | Result |
|---|---|---|
| 2.1.1 Keyboard | every function works with Tab/Shift+Tab/Enter/Space/arrows | |
| 2.1.2 No keyboard trap | focus can leave every dialog, menu, and VNC panel | |
| 2.1.4 Character key shortcuts | single-character shortcuts can be turned off or remapped | |
| 2.2.1 Timing adjustable | session timeout warns and can be extended; accommodations work | |
| 2.2.2 Pause, stop, hide | animations and auto-updating panels can be paused | |
| 2.3.1 Three flashes | no flashing content | |
| 2.4.1 Bypass blocks | skip link reaches `#main-content` | |
| 2.4.2 Page titled | every route has a unique, meaningful title | |
| 2.4.3 Focus order | focus order follows the task | |
| 2.4.4 Link purpose | link text is meaningful out of context | |
| 2.4.5 Multiple ways | nav, search, and catalogue paths exist | |
| 2.4.6 Headings and labels | one H1; labels describe the input | |
| 2.4.7 Focus visible | visible focus on every interactive element | |
| 2.4.11 Focus not obscured (minimum) | sticky header/tabbar does not cover the focused control | |
| 2.5.1 Pointer gestures | no path/ multipoint-only action | |
| 2.5.2 Pointer cancellation | activation on up-event; can cancel | |
| 2.5.3 Label in name | visible label is in the accessible name | |
| 2.5.4 Motion actuation | device motion is not the only input | |
| 2.5.7 Dragging movements | drag-and-drop has a button/keyboard alternative | |
| 2.5.8 Target size (minimum) | 24x24 CSS px, or spacing exception | |

### Understandable

| Criterion | Test focus | Result |
|---|---|---|
| 3.1.1 Language of page | `<html lang="en">` | |
| 3.1.2 Language of parts | non-English terms marked | |
| 3.2.1 On focus | focus does not change context | |
| 3.2.2 On input | input does not submit/change context unexpectedly | |
| 3.2.3 Consistent navigation | same nav order across routes | |
| 3.2.4 Consistent identification | same icon/label means the same thing | |
| 3.2.6 Consistent help | help is in the same place | |
| 3.3.1 Error identification | errors are text, not color alone | |
| 3.3.2 Labels or instructions | required fields and format are explained | |
| 3.3.3 Error suggestion | a fix is suggested where possible | |
| 3.3.4 Error prevention | destructive actions confirm and can be reversed | |
| 3.3.7 Redundant entry | do not ask for the same data twice | |
| 3.3.8 Accessible authentication | no cognitive test; paste and password managers work | |

### Robust

| Criterion | Test focus | Result |
|---|---|---|
| 4.1.2 Name, role, value | custom controls expose role/state; buttons are buttons | |
| 4.1.3 Status messages | flag accepted, lab starting, save success announced via `aria-live` | |

## 3. Keyboard-only lab task

Do this with the mouse physically disconnected or ignored.

1. Load the login page. Press Tab once: the skip link appears. Enter.
2. Tab through the form. Confirm every field has a visible label and focus ring.
3. Log in with Enter. Confirm focus moves to the main heading or a status.
4. Open the course with Enter. Reach the lab card with Tab.
5. Activate "Start lab" with Enter or Space. Confirm the status is announced and
   focus is not lost.
6. If the lab needs VPN, download the config with the keyboard, import it in the
   WireGuard client, and connect. Record the time.
7. Open the briefing. Read the objectives and hints with the keyboard.
8. If RangeBox opens, Tab into the VNC canvas and type. Confirm Tab can leave
   the canvas (no keyboard trap) and that the browser's keyboard shortcuts are
   not stolen without a documented escape.
9. Reach the flag input, type the flag, submit with Enter. Confirm the success
   message is announced and focus moves to it.
10. Open the achievement wall. Confirm each achievement is reachable and its
    name, date, and description are announced.

Pass: every step is possible without a pointer. A failure gets an issue id and
the step number. Record the time to first flag as a secondary signal.

## 4. Screen-reader scripts

### 4.1 Login and registration (NVDA, JAWS, Narrator)

1. Read the page from the top. Expected: page title, "Skip to main content",
   banner, navigation, main heading, form.
2. Tab to username. Expected: "Username, edit text". Type.
3. Tab to password. Expected: "Password, password edit". Type.
4. Submit. Expected: an alert announces success or the exact error; focus moves
   to the alert or the first invalid field.
5. On registration, confirm the age band and privacy acknowledgment are
   announced with their labels, not "radio button 1 of 4".

Fail signs: "unlabeled", "button" with no name, focus disappears, error is only
visual, password value read aloud.

### 4.2 Catalogue and course

1. Navigate by headings and landmarks. Expected: one H1, a list/grid with a
   name, and a count.
2. Tab to a lab card. Expected: the card's accessible name includes the title
   and state; the action button has a name.
3. Enter the course. Confirm the roster/assignment table has headers and the
   reading order matches the visual order.

### 4.3 Lab briefing and flag

1. Read the briefing with the screen reader. Confirm the objectives are a list,
   hints are buttons/disclosures with expanded state, and the flag input has a
   label and instructions.
2. Submit a wrong flag. Expected: `role="alert"` message, no page reload, focus
   retained.
3. Submit the correct flag. Expected: success announced, achievement
   announcement (if any) does not interrupt the success message.

### 4.4 Achievements

The medallion exposes the label and date as text; the icon is decorative. Test:

1. Navigate the achievement wall by headings/list.
2. For each medallion, confirm the screen reader announces the **label** and
   **date**, and the **description** (or an accessible description) — not just
   the icon.
3. Confirm a hidden achievement is not announced before it is earned.
4. Confirm the celebration animation is not the only signal; a live-region text
   message exists.

If the only description is a `title` attribute, record a partial finding: title
tooltips are not reliable for keyboard or touch and are inconsistently exposed.

### 4.5 Charts

`EChart.vue` renders a canvas with `role="img"` and an `aria-label`. That is a
start, not a complete answer. Test:

1. Tab to the chart. Expected: "image" or "figure" with a meaningful name.
2. Ask the screen reader for the chart's summary. Can it answer:
   - What is the highest/lowest value?
   - What is the trend?
   - What is the unit and period?
3. If the answer requires sight, the chart fails. A text summary or an
   accessible data table is required. The summary must include the values, not
   only "bar chart".
4. Confirm the chart is not the only place a value appears; any decision the
   chart supports has a text equivalent in the page.

Recommended pattern: a visible or visually hidden table with the same data, a
short `aria-describedby` summary, and a link "View data table".

## 5. Color blindness

Use Chrome DevTools → Rendering → Emulate vision deficiencies, or a simulator.
Check:

- success/error/warning states have text or icons, not color alone;
- charts use labels, patterns, or direct labels, not only hue;
- focus ring is visible against the background;
- links are distinguishable from text without color (underline or weight);
- competency/readiness bands are labelled, not just colored.

Record a screenshot per deficiency only for a failing case, and never with
learner data.

## 6. Issue log

Use [`accessibility-test/issue-log.csv`](accessibility-test/issue-log.csv).
Columns:

```text
id,date,tester,environment,route,criterion,severity,summary,steps,expected,actual,assistive_tech,evidence,owner,status
```

Severity:

- **blocker**: a learner cannot complete a core task.
- **high**: a core task is possible only with help or workaround.
- **medium**: friction or missing announcement, task still possible.
- **low**: polish, documentation, or a minor contrast issue.

## 7. Report template

Use [`accessibility-test/report-template.md`](accessibility-test/report-template.md).
A complete report has:

- environments and versions;
- per-criterion result table;
- keyboard-only lab result and time;
- screen-reader result for login, lab, achievements, charts;
- color-blindness result;
- issue list with owners and target release;
- a clear statement: "This is not a VPAT/ACR."

## 8. Exit criteria

- No blocker or high issue on login, registration, lab launch, flag submission,
  achievements, or certificate/transcript.
- Every core task is possible keyboard-only.
- Login, lab status, flag result, and save status are announced.
- Every chart has a text or table equivalent.
- Every achievement has an accessible name, date, and description.
- Color is never the only carrier of meaning.
- The report and issue log are attached to the release evidence.

## Related

- [Accessibility statement](ACCESSIBILITY.md)
- [Browser matrix](BROWSER-MATRIX.md)
- [Release test plan](RELEASE-TEST-PLAN.md)
- [First-time user test](research/FIRST-TIME-USER-TEST.md)
