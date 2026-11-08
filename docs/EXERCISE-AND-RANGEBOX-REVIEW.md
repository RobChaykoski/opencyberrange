# Exercise and RangeBox design review

Status: **Review complete; selected fixes implemented**
Scope: Community / Academic profile and Professional 2.4.1
Owner: Design and Product

This review checks the exercise page, the active-lab panel, and the RangeBox
workspace for layout, hierarchy, and functionality. It records what changed now
and what is deliberately deferred.

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

### 1. The active-lab panel is one long scroll — high

The panel currently renders, in order: scenario, objectives, ICS techniques,
exercise network, target hostnames, workbook, flag submission, and hints. On a
laptop this puts the flag and hints several screens below the top.

**Recommendation:** split the panel into tabs or a sticky section nav:
**Briefing** (scenario, objectives, workbook), **Targets** (network, hostnames),
**Hints**, and **Flag**. Keep the reaction bar above the tabs. This is recorded
as CA-L1 (in-workspace brief) and a follow-up layout item.

**Decision:** defer the full tab refactor to the Community / Academic lab
improvement line. Do not mix it into a reporting release.

### 2. RangeBox has no exercise context — high

RangeBox is a full-screen VNC view with a toolbar for status, clipboard,
minimize, and fullscreen. It does not show the exercise brief, objectives, or
hints, and it has no explicit "Back to exercise" action when opened from a lab.

**Recommendation:** add **Briefing** and **Hints** tabs inside the RangeBox
workspace and a **Pop out** action for a read-only briefing window. Add a
visible **Back to exercise** action when the workspace was opened from a lab.
This is CA-L1.

**Decision:** design is recorded; implementation is deferred and scoped as a
Community / Academic lab improvement.

### 3. Flag submission auto-stops the lab — working as intended

The flag form warns that a correct flag shuts down the environment. The warning
is present and specific. Keep it. Do not move the flag action without the
warning.

### 4. Hints are below the flag — medium

Hints are useful while working, but they sit after the flag form. In a tabbed
brief, Hints should be its own tab so learners can reach it without scrolling.

### 5. Workbook link is buried — medium

The workbook button is one card among many. In the tabbed brief it belongs in
the Briefing tab next to the scenario and objectives.

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

| Priority | Item | Classification |
|---|---|---|
| 1 | Active-lab tabs / sticky section nav | Community / Academic lab improvement |
| 2 | RangeBox Briefing and Hints tabs with pop-out | CA-L1 |
| 3 | Back to exercise action in RangeBox | Community / Academic usability fix |
| 4 | Move workbook and hints into the Briefing flow | Community / Academic lab improvement |
| 5 | Mobile orientation hint and 44 px toolbar targets | Community / Academic accessibility fix |

## Project management record

- **In scope now:** the like/dislike visibility fix (bug fix), certification
  guidance (CA-L3), admin record usability (M4), password reset hardening (M5).
- **Deferred:** the tabbed active-lab layout and RangeBox briefing tabs (CA-L1).
- **Not Enterprise:** these are not HA, SSO, multi-tenancy, LMS, or compliance
  features.
- **Evidence:** build and lint pass; manual browser verification was not
  available in this environment, so theme and viewport checks remain a release
  QA task.
