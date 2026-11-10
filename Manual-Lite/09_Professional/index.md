# SWOCTS Cyber Range Professional profile - manual supplement

Professional is the **Community / Academic profile plus learning analytics,
reporting, cohort analysis, competency evidence, and research exports** on
platform release **2.5.5**. Read the [core manual](../index.md) first.
Everything in it still applies to Professional.

## What is different in Professional

| Area | What you get | Where |
|---|---|---|
| Learner analytics | Private learning analytics for each learner: completion, hints, first-attempt rate, time, growth indicators, domain evidence, Cyber DNA, and positive practice affinities | **Learning analytics** and **Cyber DNA** |
| Course analytics | Course overview, exercise drill-down, pulse feedback, learning hours, and aggregate reactions | **Course -> Analytics** |
| Cross-course reports | Red/amber/green teaching signals, completion and abandonment, learning hours, feedback, skill-tree coverage, and CSV/PDF exports | **Reports & analytics** |
| Competency evidence | Six-domain competency profile with evidence levels (`no evidence`, `early`, `growing`, `strong`) | Learner profile and course analytics |
| Feedback | Exercise like/dislike and opt-in pulse surveys with aggregate reporting | Active exercise and course analytics |
| Research exports | Cross-course CSV/PDF and the survey package for approved studies | Reports and the REB survey package in `docs/research/REB-SURVEY-PACKAGE.md` |

The five Professional priorities are defined in
`docs/PROFESSIONAL-PRIORITIES.md`. The programme reports are defined in
`docs/PROGRAMME-REPORTS.md`.

## What Professional is not

Professional is not the HA, SSO, multi-tenant, LMS, or compliance-reporting
profile. That is the Enterprise preview profile. Professional also keeps the Community /
Academic privacy stance: analytics are descriptive, aggregate views show totals
rather than learner names, and the platform does not rank or predict learners.

## Learner quick start

1. Open **Learning analytics** from the sidebar.
2. Review completion, hint-free rate, first-attempt rate, time, and growth.
3. Use the **AI study prompts** as reflection aids. They never reveal a flag.
4. Open a completed exercise to see its feedback and pulse controls.

## Instructor quick start

1. Open a course and choose **Analytics**.
2. Use **Overview** for the cohort signal and **Exercises** for lab-level
   friction.
3. Open **Reports & analytics** in the **Admin** section (administrators) or
   **Instructor** section (instructors) for the cross-course view. Export CSV or
   PDF from there. See [Reporting and Analytics](../04_Admin_Guide/28_Reporting_And_Analytics.md).
4. Treat red and amber signals as review prompts, never as learner labels.

## Administrator notes

- Reports and analytics are instructor- or administrator-only.
- Learner-level exports are logged. Aggregate views do not show learner names.
- Course access is scoped: administrators see every active course, and
  instructors see the courses they own.
- Survey participation is opt-in and separate from normal platform access.

!!! warning "Do not import Community / Academic data backwards"
    A Professional backup contains analytics and feedback tables that the
    1.1 schema does not have. Restore it only into a Professional or Enterprise
    deployment of the same or newer version.
