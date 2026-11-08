# Community / Academic backlog

Status: **Active**
Edition: **Community / Academic profile** (inherited by Professional 2.2.0 and
Enterprise preview)
Owner: Product

This backlog holds lab and workbook improvements that belong to the Community /
Academic line. They are not Professional analytics or reporting features, and
they are not Enterprise deployment features.

## Rules

- An entry is not a commitment.
- Moving an entry into a release needs a design note, acceptance checks, and a
  release gate.
- A fix that applies to 1.1 lands on 1.1 first and merges forward.
- Do not use this backlog to bypass the Professional or Enterprise scope guards.

## Items

| ID | Item | Problem | Classification | State |
|---|---|---|---|---|
| CA-L1 | Exercise brief tab inside the lab workspace, with pop-out | Learners must leave RangeBox and open the exercise in another window to reread the scenario, objectives, hints, or workbook link | Community / Academic lab improvement | Proposed |
| CA-L2 | Keep the exercise like/dislike control visible at the top of the active exercise | The control existed but sat below the scenario and flag form, so learners did not find it | Bug fix / usability fix | Implemented on the 2.2.0 line; merge to 1.1 |
| CA-L3 | Certification pathway panel on each track | Learners can see entry, core, and advanced vendor certifications and the roles a track can lead toward | Community / Academic curriculum guidance | Implemented on the 2.2.0 line; port to 1.1 |
| CA-L4 | CISO MindMap-informed career breadth | The curriculum should show the wider leadership and governance system around technical work, not only first-job skills | Community / Academic curriculum guidance | Proposed |

## CA-L1 design note

**Goal:** while a lab is running, the learner can read the exercise brief in a
tab inside the RangeBox workspace and optionally pop it out.

**Shape:**

- Add a **Briefing** tab to the RangeBox workspace alongside the existing
  terminal and files views.
- Reuse one `ExerciseBrief` component for the in-workspace tab and the pop-out
  route so the content cannot drift.
- Render scenario, objectives, target hostnames, workbook link, and hints with
  the existing sanitized markdown renderer. Never render raw HTML.
- Keep the selected tab in the URL (`?tab=briefing`) so refresh and deep links
  work.
- Add a **Pop out** action that opens a minimal, read-only briefing route in a
  new window. Use the router to build the URL and `noopener,noreferrer`.
- Do not put flags, VPN keys, credentials, or learner PII in the briefing.

**Accessibility and responsive behaviour:**

- Use `tablist` / `tab` / `tabpanel` semantics with arrow-key navigation.
- The pop-out control needs an accessible name and a visible label.
- The tab strip scrolls horizontally on narrow screens; the panel scrolls
  independently.
- The pop-out page works at 375 px wide and supports print.

**Acceptance checks:**

1. A running lab shows a Briefing tab.
2. The tab and the pop-out show identical content.
3. Refresh keeps the selected tab.
4. Pop-out opens without an opener reference and returns a readable page.
5. No secrets or learner PII appear in either view.
6. Keyboard and screen-reader navigation work.
7. The build and lint pass.

**Decision:** proposed for the Community / Academic profile lab improvement line.
Do not implement it as part of a Professional analytics or reporting change.

## CA-L3 design note

The track page shows a collapsible **Certification pathways** panel with three
steps (start here, build on it, go further), the roles the track can lead to,
and links to:

- the Security Certification Roadmap by Paul Jerimy;
- the CISO MindMap 2026 by Rafeeq Rehman;
- SWOCTS learning resources.

The mapping lives in `platform/frontend/src/data/certificationPaths.js`. It is
guidance, not an official mapping. Update it when a track is added or a vendor
changes a certification.

## CA-L4 design note

Use the CISO MindMap to identify curriculum breadth that is missing from the
technical tracks: IAM, GRC, cloud, AI, OT, data-centric security, third-party
risk, and team/business leadership. The goal is awareness and advanced context,
not turning every track into a CISO course. See
[Career and certification resources](CAREER-AND-CERTIFICATION-RESOURCES.md).
