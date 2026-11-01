---
name: OpenCyberRange Design
description: Design, review, or implement UI for the OpenCyberRange training platform. Use for Vue pages, dashboards, profiles, course/lab interfaces, admin screens, forms, tables, certificates/PDFs, dark and light themes, accessibility reviews, responsive layout, and workbook or course-content design. Enforces the platform's existing tokens, Vue conventions, and student/instructor safety rules.
---

# OpenCyberRange Design

Use this skill for any visual or interaction work in the OpenCyberRange platform: new pages, component changes, layout reviews, accessibility fixes, dashboards, profiles, course authoring, certificates, and workbook content.

This skill is the project-specific source of truth. It takes precedence over generic style recommendations from other UI skills.

## Start by reading

Read the reference that matches the task:

- `references/design-system.md` — tokens, typography, spacing, colour roles, elevation, breakpoints.
- `references/page-patterns.md` — dashboard, profile, catalogue, admin, lab, auth, certificate, and workbook patterns.
- `references/accessibility-and-qa.md` — WCAG checks, interaction rules, responsive and print verification.
- `references/frontend-conventions.md` — Vue, routing, axios, styling, security, and build conventions.
- `references/course-content.md` — instructional design, lab copy, workbook structure, and safe AI/cyber content.

Also inspect the actual code before proposing changes:

- `platform/frontend/src/App.vue` — global CSS variables and shared button/layout rules.
- The target view in `platform/frontend/src/views/` and shared components in `platform/frontend/src/components/`.
- `platform/frontend/src/components/icons/trackIcons.js` for track iconography.

## Core rules

1. **Preserve the product, not just the pixels.** Do not change routes, API contracts, permissions, lab lifecycle, or data semantics during a design task.
2. **Use the existing token system.** Reuse `--bg-primary`, `--bg-secondary`, `--text-primary`, `--accent`, `--success`, `--warning`, `--danger`, and the other variables in `App.vue`. Do not introduce a second palette or a parallel theme system.
3. **Both themes must work.** Every new surface, border, badge, chart, overlay, and state must be checked in dark (default) and `[data-theme="light"]`.
4. **Vue conventions.** Use Vue 3 `<script setup>`, Composition API, scoped styles, the shared `src/api/axios.js` client, and existing icon components. Do not add a framework or CSS library.
5. **Operational density beats marketing layout.** Dashboards, admin, and lab pages are for repeated work. Add hierarchy, not oversized heroes or decorative animations.
6. **No emoji-only icons.** Use inline SVG or the existing icon components. Status must not rely on colour alone.
7. **Every state is designed.** Include loading, empty, error, success, disabled, permission-denied, and long-content states where relevant.
8. **Safety is part of design.** Destructive actions need confirmation, clear consequences, and a safe default. Never expose secrets, flags, VPN keys, or student PII in UI copy, screenshots, or logs.
9. **Accessibility is a requirement.** Keyboard operation, visible focus, labels, contrast, reduced motion, and responsive text are not optional polish.
10. **Keep the brand mature.** Do not restyle the whole platform as neon cyberpunk, glassmorphism, or a marketing landing page. Restrained dark surfaces, clear status colour, and strong data legibility are the brand.

## Workflow

1. **Locate the task.** Identify the user, the primary job, and the page state being changed.
2. **Audit first.** Read the target view plus one comparable view. Note existing patterns instead of inventing a new one.
3. **Sketch in words.** For broad changes, state the intended layout, hierarchy, and responsive behaviour before editing.
4. **Implement in small batches.** Prefer editing existing components and scoped styles. Do not rewrite a view to change one component.
5. **Check both themes and viewport widths.** Use the breakpoints and checklist in `references/accessibility-and-qa.md`.
6. **Verify the build.** Run `npm run build` in `platform/frontend` and `npm run lint` where the touched code warrants it. If backend behaviour changed, run the relevant pytest suite.
7. **Report the design decisions.** Summarise what changed, states covered, and anything not verified in a real browser.

## Using other UI skills

Generic UI skills such as `ui-ux-pro-max` are useful for accessibility guidance, interaction states, chart selection, and layout critique. Use them as advisory inputs, then adapt the result to this skill.

Never let a generic skill override:

- the existing colour and theme tokens
- the OpenCyberRange information architecture
- Vue and scoped-CSS conventions
- the safety and course-design rules in this skill

For example, a generic "cybersecurity" recommendation to use a neon matrix-green palette is **not** applicable here. The platform already has an established slate-and-blue visual identity.
