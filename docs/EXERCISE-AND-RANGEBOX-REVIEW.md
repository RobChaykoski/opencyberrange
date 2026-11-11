# Exercise and RangeBox design review

Status: **Review complete; combined workspace implemented and verified for 2.6.0**
Scope: Community / Academic profile and Professional 2.6.0
Owner: Design and Product

This review checks the exercise page, the active-lab panel, and the RangeBox
workspace for layout, hierarchy, and functionality. It records what changed now
and what is deliberately deferred.

## 2.6.0 combined workspace

The active exercise now has a desktop workspace for RangeBox-enabled labs:

- RangeBox occupies the top-left pane.
- The scenario, targets, hints, and flag form occupy the right column.
- The workbook is framed along the bottom, with **Expand/Restore** and
  **Open in new tab**.
- The session timer and **Stop Exercise** remain in the panel header.
- Phones (768 px and below) and VPN-only labs keep the stacked panel, so a
  learner on a narrow screen still gets the section jump bar.

The workspace is gated on `session.rangebox_enabled` and a desktop-width
viewport. A lab whose `tools` list includes `rangebox` launches a Kali desktop;
an empty tools list stays VPN-only.

Verification on **11 November 2026** used dedicated test student and instructor
accounts and `scripts/ui-workspace-regression.mjs`:

- The workspace, RangeBox pane, flag input, timer, and workbook frame rendered
  for both roles.
- The workbook iframe resolved to the correct wiki chapter.
- **Expand/Restore**, **Open in new tab** for RangeBox, **Open in new tab** for
  the workbook, **Request Hint**, invalid-flag error handling, and
  **Stop Exercise** were exercised.
- The mobile viewport kept the stacked panel and the section jump bar.
- The walkthrough found and fixed one button bug: **Open in new tab** used
  in-page routing instead of opening a tab. It now uses `window.open` with the
  resolved `/rangebox?...` URL.
- The workbook CSP now allows the Material for MkDocs Google Fonts stylesheet
  and font files; the SPA policy remains strict.

Screenshots: `docs/img/exercise-workspace.png` (desktop) and
`docs/img/exercise-workspace-mobile.png` (phone fallback). The regression
evidence is written to `ui-workspace-artifacts/workspace-regression.json`.

## Method

1. Read the exercise page (`TrackDetail.vue`), the RangeBox workspace
   (`RangeBox.vue`), and the active-lab layout.
2. Check the primary learner sequence: open track -> choose exercise -> start ->
   read brief -> work in RangeBox -> submit flag -> review feedback.
3. Check loading, empty, error, completed, and mobile states against the
   accessibility and responsive checklist.
4. Classify every finding against the programme scope.

## What changed now

| Change | Why |
|---|---|
| Exercise like/dislike moved to the top of the active exercise | It was below the scenario and flag form, so learners did not find it. It is now visible before the long brief, with a disabled state until the exercise starts. |
| Certification pathway panel added to each track | Learners can see entry, core, and advanced vendor certifications, role direction, and links to the Security Certification Roadmap, the CISO MindMap 2026, and SWOCTS resources. |
| Admin user record and edit redesign | The old record was a flat list of fields and tables. It now has an account hero, summary stats, searchable evidence, active-session cards, and a separate audited password reset. |
| Password reset hardened | Admin re-authentication, token revocation, forced password change, audit logging, and rejection of password changes on the general update endpoint. |

## Findings

### 1. The active-lab panel is one long scroll — addressed in 2.6.0

The old panel rendered, in order: scenario, objectives, ICS techniques, exercise
network, target hostnames, workbook, flag submission, and hints. On a laptop this
put the flag and hints several screens below the top.

**Decision:** the combined workspace moves the flag, targets, hints, and scenario
into the right column and frames the workbook below. VPN-only labs keep the
stacked panel, where the mobile jump bar and section anchors provide the same
navigation. The full tab refactor is no longer required for RangeBox labs.

### 2. RangeBox has no exercise context — addressed in 2.6.0

The standalone RangeBox view is a full-screen VNC surface with a toolbar for
status, clipboard, minimize, and fullscreen. The combined exercise workspace now
puts that desktop beside the scenario, targets, hints, and flag form, so the
learner does not have to switch windows to read the brief. The **Open in new
tab** fallback remains for a second monitor.

**Decision:** delivered for RangeBox-enabled labs. A dedicated in-desktop
briefing tab is not required while the exercise workspace is available.

### 3. Flag submission auto-stops the lab — working as intended

The flag form warns that a correct flag shuts down the environment. The warning
is present and specific. Keep it. Do not move the flag action without the
warning.

### 4. Hints are below the flag — medium

Hints are useful while working, but they sit after the flag form. In a tabbed
brief, Hints should be its own tab so learners can reach it without scrolling.

### 5. Workbook link is buried — addressed in 2.6.0

The workbook is now a framed pane in the workspace with **Expand/Restore** and
**Open in new tab**, instead of one card among many.

### 6. Mobile RangeBox is cramped — medium

The RangeBox is a fixed full-screen VNC surface. On a narrow screen the toolbar
and desktop are hard to use. Show an orientation hint for lab work and keep the
toolbar controls at 44 px targets. Do not try to reflow the remote desktop.

### 7. Good states already present

- Connection status is labelled, not colour-only.
- Reconnect, clipboard, minimize, and fullscreen are available.
- Session timer and expiry warning exist.
- Empty, loading, and error states exist on the exercise page.
- The certification panel is keyboard reachable and collapses.

## Prioritized follow-up

| Priority | Item | Status |
|---|---|---|
| 1 | Active-lab tabs / sticky section nav | Resolved by the combined workspace for RangeBox labs; VPN-only labs keep the mobile jump bar |
| 2 | RangeBox Briefing and Hints beside the desktop | Resolved by the combined workspace |
| 3 | Back to exercise action in RangeBox | Resolved by the combined workspace; the standalone tab keeps Close |
| 4 | Move workbook and hints into the working flow | Resolved: workbook pane, Expand/Restore, and right-column hints |
| 5 | Mobile orientation hint and 44 px toolbar targets | Mobile fallback retained; toolbar targets remain a design check |

## Project management record

- **In scope now:** the combined RangeBox workspace, the new-tab fix, the
  workbook CSP correction, and the regression walkthrough.
- **Deferred:** a fully tabbed panel for VPN-only labs; the stacked panel and
  jump bar are sufficient at current content depth.
- **Not Enterprise:** these are not HA, SSO, multi-tenancy, LMS, or compliance
  features.
- **Evidence:** frontend build and lint pass; the browser walkthrough passed for
  a test student and test instructor; screenshots and the JSON evidence file are
  attached.
