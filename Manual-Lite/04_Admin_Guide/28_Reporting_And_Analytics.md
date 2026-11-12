# Reporting and Analytics

The **Reports & analytics** page is the cross-course teaching view for
instructors and administrators. Use it to compare course health, spot exercises
that are causing friction, review learner feedback, and export evidence for a
teaching review or accreditation file.

## Prerequisites

- You are signed in as an administrator or an instructor.
- At least one active course exists and has learners or activity. An empty
  installation shows the page with zero counts and an empty-state message.
- You own the course, or you are an administrator. Administrators see every
  active course; instructors see only the courses assigned to them.

## Where it lives

Open **Reports & analytics** in the left sidebar:

- An administrator finds it in the **Admin** section, between **Live activity** and
  **System**.
- An instructor finds it in the **Instructor** section, below **Exercises**.

The page uses the `/reports` route. It is separate from the Admin Panel tabs, so
opening it does not change the tab you last used in `/admin`.

!!! note "Surveys are nearby"
    The **Surveys** link in the Instructor section opens the survey builder and
    response history. Reporting and survey results are separate pages but share
    the same consent and privacy rules. See
    [Survey privacy](https://github.com/RobChaykoski/opencyberrange/blob/main/docs/SURVEY-PRIVACY.md) if you distribute surveys.

## Read the summary cards

The cards across the top summarise every course in scope:

| Card | What it counts |
| --- | --- |
| Courses | Active courses visible to you. |
| Learners | Enrolled learner seats across those courses. A learner in two courses counts twice. |
| Learning hours | Tracked learning time on completed exercises plus bounded session time for started exercises. |
| Pulse responses | Quick pulse surveys submitted by learners. |
| Exercise feedback | Positive share of optional exercise likes and dislikes. |
| Signals | Courses currently marked green, amber, or red. |

These are descriptive teaching signals. They are not grades, predictions, or a
learner ranking.

## Read a course row

The course table shows one row per active course:

| Column | What it means |
| --- | --- |
| Course | Course code and name. The link opens the course Analytics tab. |
| Signal | Green, amber, or red, with the first reason for that signal. |
| Learners | Number of enrolled learners. |
| Completion | Completed learner-exercise pairs divided by all assigned pairs, plus the count of learners with at least one completion. |
| Abandonment | Share of started learner-exercise pairs that were not completed. |
| Learning | Average self-reported learning from the pulse survey, on a 1-5 scale. |
| Feedback | Positive share of exercise likes and dislikes, with totals. |
| Confidence | Performance-growth proxy from hint, attempt, and time trends. |
| Pulse | Number of pulse responses for the course. |
| Open | Opens the course Analytics tab. |

### What the colours mean

- **Green:** strong completion and high learning reported.
- **Amber:** learners are succeeding but the experience looks strained, for
  example high completion with low reported learning or high reported
  difficulty.
- **Red:** abandonment of 50% or more, completion below 50%, a median of five or
  more flag attempts, or learning reported at 2 or below.

Always read the reason beside the colour. A colour without its reason is not
enough to change a course.

## Review exercise coverage

The **Exercise coverage by skill branch** radar maps assigned and completed
exercises across the five Skill DNA branches: Explorer, Builder, Defender,
Investigator, and Leader.

1. Choose **All courses** or one course in the **Scope** selector.
2. Compare the outer shape (assigned curriculum) with the inner shape (completed
   exercises).
3. Use the table beside the chart for exact counts and shares.

The radar describes the mix of exercises, not learner scores. Completed
exercises are distinct exercises with at least one completion.

## Review trending topics

**Trending topics** aggregates the optional "what should we cover next?" answers
from pulse surveys. Use it to plan the next module or guest session. The chart
shows counts only; it does not show which learner requested a topic.

## Review curriculum demand

Below the trending topics, **Curriculum demand** turns the same telemetry into a
short list of where to build or rework exercises. It combines three signals:

| Signal | What it uses | How to use it |
|---|---|---|
| **Topic demand** | Pulse topic requests compared with the exercises already assigned in that area. | Build one guided and one independent exercise in a high-demand area. |
| **Exercise friction** | Completion, abandonment, hint pressure, median attempts, and technical failures. | Check the brief and starting state, add a warm-up, or split the exercise. |
| **Competency gap** | Cohort coverage below 40% for a taxonomy competency. | Add practice for the lowest-coverage competency first. |

Each card shows its sample size, its evidence source, and a suggested action.
Cards are sorted by priority. The panel uses the same small-cohort suppression as
the rest of the page: a course below the minimum learner count contributes no
recommendations. Recommendations are planning prompts, not an evaluation of
teaching or learners.

## Drill into a course

1. Select a course name, or choose **Open** in its row.
2. The course opens on the **Analytics** tab.
3. Review the summary cards, overall signal, learning impact, trending topics,
   and the per-exercise signals table.
4. Use **Exercise signals** to find exercises with high hint pressure, high
   attempt burden, or low completion.

The course tab is the evidence behind the cross-course report. It does not
change the course or any learner record.

## Export a report

1. Enter a **Reason for export** of at least five characters, for example
   `end-of-term teaching review`.
2. Choose **Export CSV** for a spreadsheet, or **Export PDF** for a printable
   report.
3. Open the downloaded file and store it according to your institution's data
   policy.

Every export writes the reason, exporter, format, and scope to the audit log.
The course scope follows your role: administrators export every active course
and instructors export the courses they own. The PDF entry also records the
number of courses, and the PDF endpoint sends `Cache-Control: no-store`. Do not
reuse another person's reason; the audit entry is tied to the signed-in account.

!!! tip "Exports are point-in-time"
    The CSV and PDF are built from the data visible when you start the export.
    Re-export after a course changes if you need the latest figures.

## Privacy and responsible use

- Reports show aggregates. They do not list learner names in the cross-course
  table, trending topics, or exercise feedback totals.
- Learner-level evidence stays in the course roster, profile, and transcript,
  where access is already scoped.
- Do not turn a red course signal into a learner label. Investigate the exercise
  and the teaching design first.
- Confidence gain is a transparent performance-growth proxy, not a validated
  psychological measure.
- If you enable Privacy Mode in the sidebar, names in rosters and activity views
  are masked; report exports still follow the reason and audit rules above.

## Related pages

- [Admin Panel Overview](01_Admin_Panel_Overview.md)
- [Monitoring Active Sessions](13_Monitoring_Active_Sessions.md)
- [Generating PDF Reports](../03_Instructor_Guide/12_Generating_PDF_Reports.md)
- [Learning analytics design](https://github.com/RobChaykoski/opencyberrange/blob/main/docs/V2-LEARNING-ANALYTICS.md)
- [Programme reports](https://github.com/RobChaykoski/opencyberrange/blob/main/docs/PROGRAMME-REPORTS.md)
