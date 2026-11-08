# OpenCyberRange Design System

Source of truth for global tokens: `platform/frontend/src/App.vue`.
Page-level styles are scoped in each `views/*.vue` file.

## Colour roles

Use semantic variables. Do not hard-code the dark values into components.

| Role | Dark (default) | Light | Use |
|---|---|---|---|
| `--bg-primary` | `#0f172a` | `#ffffff` | Page background |
| `--bg-secondary` | `#1e293b` | `#f1f5f9` | Cards, panels, sidebars |
| `--bg-tertiary` | `#334155` | `#e2e8f0` | Secondary buttons, tracks, inert fills |
| `--text-primary` | `#f8fafc` | `#0f172a` | Headings and primary content |
| `--text-secondary` | `#94a3b8` | `#475569` | Supporting copy, labels |
| `--text-muted` | `#64748b` | `#94a3b8` | Metadata, placeholders |
| `--border-color` | `#334155` | `#cbd5e1` | Borders, dividers |
| `--accent` | `#2563eb` | `#1d4ed8` | Primary actions, fills, focus, borders |
| `--accent-text` | `#60a5fa` | `#1d4ed8` | Accent-coloured text and links on the page background |
| `--success` | `#22c55e` | `#16a34a` | Completed, healthy, approved |
| `--warning` | `#f59e0b` | `#d97706` | Pending, caution, time pressure |
| `--danger` | `#ef4444` | `#dc2626` | Destructive actions, errors |
| `--purple` | `#8b5cf6` | `#7c3aed` | Secondary categories, achievements |
| `--nav-label` | `#475569` | `#94a3b8` | Disabled/inactive navigation |
| `--panel-bg` | `#1e293b` | `#ffffff` | Modal/panel surfaces |
| `--accent-bg` | `rgba(59,130,246,.10)` | same | Accent tint |
| `--danger-bg` | `rgba(239,68,68,.10)` | same | Danger tint |
| `--success-bg` | `rgba(34,197,94,.15)` | `rgba(22,163,74,.12)` | Success tint |
| `--warning-bg` | `rgba(245,158,11,.15)` | `rgba(217,119,6,.12)` | Warning tint |

### Rules

- Text on `--bg-primary` or `--bg-secondary` should normally use `--text-primary` or `--text-secondary`. Do not use `--text-muted` for essential body copy.
- Status colour must be paired with a label, icon, or shape.
- Prefer translucent tints for badges and progress fills; keep the base token for the strong accent.
- If a new semantic colour is truly required, define it in `:root` **and** `[data-theme="light"]` in `App.vue`, and document it here.
- Avoid embedding brand colours in page-specific styles. The one existing exception is track colour returned from the database (`track.color`), which may be used as an accent for that track.

## Typography

- Body: `Inter, -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif`.
- Mono: `"JetBrains Mono", ui-monospace, monospace` for certificate IDs, IPs, commands, and technical metadata.
- Serif: `Georgia, "Times New Roman", serif` is reserved for certificate/transcript display type.
- Base line-height: `1.6`.
- Page title: about `2rem`, weight `700–800`, `--text-primary`.
- Section title: `1.125–1.25rem`, weight `600–700`, usually with a bottom divider.
- Card title: `0.875–1rem`, weight `600–700`.
- Labels: `0.75–0.875rem`, weight `500–600`, `--text-secondary`.
- Metadata: `0.68–0.8rem`, `--text-muted`.
- Eyebrow/section labels: uppercase, `0.68–0.75rem`, letter-spacing `0.08–0.18em`.
- Avoid viewport-width font sizing except occasional certificate display type.

## Spacing and layout

Observed scale (use these before inventing new values):

`0.25 · 0.35 · 0.5 · 0.65 · 0.75 · 1 · 1.25 · 1.5 · 1.75 · 2 · 3rem`

Common patterns:

- Page padding: `1rem` mobile, `2rem` desktop.
- Card/panel padding: `1rem–1.6rem`.
- Grid gap: `0.75rem–1.5rem`.
- Section vertical rhythm: `1.5rem–2rem`.
- Content width: `900px` for forms/settings, `1080px` for profile and multi-column operational pages.
- Full-width admin tables may exceed the reading column; wrap them in `overflow-x: auto`.
- Use `minmax(0, 1fr)` in grids to prevent long IDs and emails from overflowing.

## Radii and elevation

Observed radii:

- `6px` — buttons, inputs, compact controls
- `8px` — small panels, nav items
- `10px` — table wrappers, notices
- `12px` — cards, section panels
- `14px` — feature cards, certificate cards
- `18px` — profile hero
- `999px` — progress bars, pills, chips, avatar frames

Shadows are restrained. Dark theme surfaces separate primarily through borders and background contrast.

- Small elevation: `0 10px 28px rgba(...)`
- Hero/panel: `0 18px 45px rgba(2, 6, 23, 0.18)`
- Certificate: `0 24px 70px rgba(15, 23, 42, 0.22)`

Do not add glow or blur to functional controls unless it communicates a live/active state.

## Buttons and controls

Prefer the shared classes from `App.vue`:

- `.btn`
- `.btn--primary`
- `.btn--secondary`
- `.btn--success`
- `.btn--danger` (outline danger)
- `.btn--outline`
- `.btn--sm`
- `.btn--xs`

Page-local `.btn` definitions may override the shared system; preserve the local convention when editing an existing view.

Rules:

- One primary action per region.
- Secondary actions use `.btn--secondary` or `.btn--outline`.
- Destructive actions use danger styling and require confirmation.
- Disabled actions must remain readable and explain why when the reason is not obvious.
- Icon-only controls require an accessible label and a visible focus ring.
- Minimum interactive target: `24×24px` (WCAG 2.2); `40–44px` preferred for primary touch controls.

## Forms

- Always pair an input with a `<label>` (or an explicit `aria-label` when visually hidden).
- Help text sits below the input in `--text-muted`; errors appear below and are associated with the field.
- Use `aria-describedby` for help and error text on non-trivial fields.
- Validate on blur/submit and preserve user input after errors.
- Never disable submit silently; if it is disabled, make the missing requirement visible.

## Tables

- Use `<th scope="col">` for column headers; add a caption or visually hidden caption for complex tables.
- Keep row height compact but not cramped (`0.5–0.7rem` vertical padding).
- Use `--bg-primary` or alternating `rgba` fills for rows.
- Keep identifiers in mono and allow wrapping.
- Put horizontal scrolling on the wrapper, not the page.
- On mobile, prioritise the identifying column and hide/stack secondary metadata rather than shrinking text below `0.75rem`.

## Status and badges

Existing badge vocabulary:

- Approved / active / complete: green tint, success text.
- Pending / warning: amber tint.
- Inactive / disabled: neutral/red tint depending on meaning.
- Admin: purple tint.
- Instructor: blue tint.
- Student: neutral tint.
- VPN registered: green; no VPN: neutral.

Add text or an icon for meaning; never rely on the tint alone.

## Motion

- Default interaction transition: `120–180ms ease`.
- Larger state transitions (progress bar, card lift): `180–350ms`.
- Respect `prefers-reduced-motion: reduce`; remove transforms and non-essential animation.
- Do not animate content that conveys live status without providing a static final state.

## Breakpoints

Use the established breakpoints:

- `900px` — multi-column operational layouts collapse
- `768px` — app shell/sidebar behaviour
- `640px` — single-column forms and cards, centred hero content

Verify at approximately `375`, `768`, `1024`, and `1440` px.
