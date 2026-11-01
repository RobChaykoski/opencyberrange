# Accessibility, Responsive, and QA Checklist

Target: **WCAG 2.2 AA** for student-facing and instructor-facing UI.

## Contrast

- Body text: at least `4.5:1` against its background.
- Large text (≥ `24px`, or ≥ `18.66px` bold): at least `3:1`.
- UI component boundaries and meaningful icons: at least `3:1`.
- Do not use `--text-muted` for essential instructions, error messages, or small metadata that the user must read.
- Check both themes. A token that passes in dark mode may fail in light mode.

## Keyboard and focus

- Every interactive element is reachable by keyboard.
- Use native `<button>`, `<a>`, `<input>`, `<select>`, and `<textarea>` before ARIA substitutes.
- Visible focus is mandatory. Prefer a `2px` accent ring with a `2px` offset; do not remove the outline without a replacement.
- Focus must not be obscured by sticky headers, sidebars, banners, or overlays.
- Provide a skip link on pages with repeated navigation when it is missing at the shell level.
- Dialogs trap focus, close on `Escape`, and restore focus to the trigger.
- Do not use hover as the only way to discover an action.

## Semantics and labels

- One `<h1>` per page; preserve heading order.
- Icon-only controls need `aria-label` or visually hidden text.
- Decorative SVGs use `aria-hidden="true"`; meaningful SVGs expose a title or adjacent text.
- Inputs have a visible or programmatically associated label.
- Errors are announced and associated with `aria-describedby`; invalid fields use `aria-invalid`.
- Status changes use a live region only when they are asynchronous and important. Avoid noisy live regions for every poll update.
- Tables use `<th scope="col">` / `scope="row"` and a caption for complex data.
- Do not put interactive controls inside another interactive element.

## Colour and status

- Never use colour as the only signal.
- Badges must include text. Add an icon or shape where scanability matters.
- Progress bars include a text value and `role="progressbar"` with `aria-valuenow`, `aria-valuemin`, and `aria-valuemax`.
- Error, warning, and success states include a readable sentence.

## Motion

- Respect `prefers-reduced-motion: reduce`.
- Remove non-essential transforms, parallax, glow pulses, and auto-playing animation.
- Keep the final semantic state visible when animation is disabled.
- Avoid motion that flashes more than three times per second.

## Targets and touch

- Minimum `24×24px` target; prefer `40–44px` for primary touch actions.
- Space adjacent targets so users do not hit the wrong one.
- Do not rely on tiny close icons or text-only links for high-risk actions.

## Responsive text and layout

Test at approximately `375`, `768`, `1024`, and `1440` px wide.

- No page-level horizontal scrolling. Table/card wrappers may scroll internally.
- Long emails, usernames, certificate IDs, track names, and file paths wrap with `overflow-wrap: anywhere` where needed.
- Buttons may become full-width on small screens, but labels must stay intact.
- Do not truncate essential values without an accessible full-value path.
- Grids use `minmax(0, 1fr)` to prevent overflow.
- At `640px`, stacked layouts should preserve reading order and action priority.

## Forms

- Required fields are marked visually and programmatically.
- Help text and errors are associated with the field.
- Validation messages explain the fix, not just "Invalid".
- Submit state shows progress and prevents duplicate submission.
- Preserve values after a server error.
- Password fields include visibility toggles with accessible labels.

## Loading and async states

- Show a loading state within the affected region, not a global blank screen.
- If data refreshes in the background, do not move focus or announce every poll.
- Failed sections can show an inline retry without discarding successful sections.
- Disable destructive or duplicate actions while their request is in flight.

## Print and PDF

- Hide sidebar, theme toggle, banners, buttons, forms, and interactive controls.
- Use a white/paper background for certificates and transcripts.
- Verify page breaks do not split a certificate frame.
- Keep certificate IDs and award dates legible in mono/serif at print size.
- Test at A4 and US Letter if the platform supports both.

## Verification commands

Frontend:

```bash
cd platform/frontend
npm run lint
npm run build
```

Backend when touched:

```bash
cd platform/backend
python -m pytest -q
```

Labs when touched:

```bash
python scripts/validate-lab.py platform/labs/<Track>/<lab-directory>
```

## Manual review

If a browser is available:

1. Check dark and light themes.
2. Check the four widths listed above.
3. Tab through the page and confirm focus order and visible focus.
4. Zoom to `200%` and confirm no essential content is clipped.
5. Check loading, empty, error, and success states.
6. Check the print preview for certificate/transcript pages.

If no browser is available, say so explicitly in the summary and list what was verified only by build/lint.
