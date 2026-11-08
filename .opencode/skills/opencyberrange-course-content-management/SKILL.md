---
name: OpenCyberRange Course Content Management
description: Use when designing, building, or reviewing the Academy course workspace, course content authoring, programme/course/module organisation, cohorts, publishing workflows, or the student-instructor feedback loop. Defines the organisational content model, roles, lifecycle, feedback metrics, and the no-scoreboard rule for OpenCyberRange.
---

# OpenCyberRange Course Content Management

Use this skill for the **Academy → Courses** area and anything that organises
teaching content: programmes, courses, modules, assignments, cohorts, authoring,
review, publishing, and the two-way feedback loop.

Read `opencyberrange-design` first. It owns the visual system and Vue
conventions. This skill owns the **content organisation and feedback model**.
Use `opencyberrange-program-management` before adding a new product surface.

## The content model

Use one hierarchy everywhere. Do not invent a second vocabulary in a page.

```
Programme (optional grouping)
  └── Course (code, term, instructor, cohort)
        ├── Module / Unit (ordered teaching block)
        │     └── Item (lab assignment, reading, quiz, survey, resource)
        └── People (instructor, teaching assistant, students)
```

Rules:

- A **Course** is the unit of enrolment, permissions, and feedback. A course can
  exist without a programme.
- A **Module** groups items into a teachable sequence. Modules have an order,
  a short outcome statement, and an optional unlock rule.
- An **Item** is one assignable object. Supported types: `lab`, `reading`,
  `quiz`, `survey`, `resource`, `live_session`. A lab item points at an existing
  lab; do not duplicate lab content into the course.
- A course may also have ungrouped items. Show them under an "Unassigned"
  module rather than hiding them.
- Keep `Track → Level → Lab` as the exercise catalogue. The course layer
  references labs; it does not replace the catalogue.

## Roles

| Role | Can |
|---|---|
| Admin / programme lead | Create courses, assign instructors, share content across courses, export reports |
| Instructor | Author modules/items, publish, manage roster, give student feedback, read course feedback |
| Teaching assistant | Read roster and feedback; grade/coach if granted; cannot change ownership |
| Student | Read published content, submit work, give course feedback, read own feedback |

Never expose another student's identity, comments, or coaching to a student.
Student feedback is anonymous to instructors by default; store the author only
for duplicate prevention and the student's own record.

## Content lifecycle

Every course item is in one state:

`draft → in_review → published → archived`

- **Draft** is visible only to authors.
- **In review** is visible to reviewers; students do not see it.
- **Published** is visible to the enrolled cohort.
- **Archived** is read-only and hidden from the active catalogue; completion
  records remain.

Requirements:

- Show the state in the authoring UI and explain what students can see.
- Publishing is an explicit action with a confirmation and a summary of what
  changes for students.
- Use versioning or a clone-on-edit rule for published content. Never silently
  rewrite a module students are working through.
- A course can be cloned for a new term. Cloning copies structure and settings,
  not student data or completions.
- Reuse content by reference where possible; a copied module must record its
  source so updates can be reviewed.

## Course workspace information architecture

The course page is a workspace, not a landing page. Use a stable left rail (or
tabs on narrow screens) with these sections:

1. **Overview** — course identity, instructor, term, cohort size, progress,
   next action, feedback pulse, and recent activity.
2. **Content** — modules and items, with authoring controls for instructors and
   a read-only sequence for students.
3. **People** — roster, enrolment, groups/cohorts, and per-student record.
4. **Feedback** — the two-way loop described below. Replaces the scoreboard.
5. **Achievements** — course-scoped badges and evidence.
6. **Settings** — course details, invite code, visibility, archive, and
   destructive actions.

Do not use a public leaderboard, rank, or projected scoreboard. If a numeric
view is needed, use private, descriptive metrics with a clear label.

## The two-way feedback loop

Feedback is a loop, not a survey graveyard.

### Student → course/instructor

Collect:

- a short pulse after an exercise: difficulty, learning value, and what was
  unclear (reuse `exercise_pulse_surveys`);
- a lightweight reaction (like/dislike) while working (reuse
  `exercise_reactions`);
- a course-level check-in: clarity, challenge fit, engagement, confidence, and
  an optional comment;
- optional instructor-created surveys for deeper review.

### Instructor → student

Collect:

- a coaching note with a rating or observation and a next step;
- a response to a student's unclear point;
- acknowledgement of progress or a risk flag.

### Metrics

Compute private, descriptive metrics for the course:

- **Response rate** — unique respondents / enrolled students.
- **Clarity** — average of course-level clarity and pulse learning scores.
- **Challenge fit** — how close the reported difficulty is to the target band.
- **Engagement** — reaction like ratio plus participation.
- **Instructor responsiveness** — students with a coaching response / students
  who asked for help.
- **Overall feedback score** — a weighted 0–100 summary of the above, with the
  weights shown in the UI.

Rules:

- Label every metric with its source and sample size.
- Show a confidence/empty state when the sample is small; do not imply precision.
- Never rank students or instructors publicly.
- Aggregate student comments before showing them to instructors; strip identity.
- A student sees the aggregate and their own record, not other students' data.
- **Initial feedback must count immediately.** Aggregate existing pulse surveys,
  reactions, and completions on first load so the dashboard is useful before a
  new survey is submitted. Show the data source.

## Authoring and review workflow

1. **Scope** — course outcome, cohort, and assessment plan.
2. **Structure** — create modules, then add items by reference.
3. **Draft** — write the module outcome, instructions, and success criteria.
4. **Review** — check accuracy, safety, accessibility, and the workbook link.
5. **Publish** — confirm the student-visible change and notify the cohort if
   needed.
6. **Teach** — monitor feedback, answer unclear points, and adjust the next
   module.
7. **Close** — archive the course, preserve completions, and export evidence.

## Content quality checklist

- Every module states what the learner can do afterwards.
- Every lab item matches a real lab slug and workbook.
- Time estimates, difficulty, and prerequisites are visible.
- Instructions work on the supported screen sizes.
- No real secrets, personal data, or live malware.
- Defence is taught alongside attack.
- The workbook and lab test steps agree.

## Optional knowledge checks

Knowledge checks are benchmark practice, never exam items or gates.

- Attach a small bank to an exercise (`quiz.yaml`), with a track fallback when
  no specific bank exists.
- Show 2–3 randomised questions per attempt; allow unlimited re-attempts.
- Reveal the correct answer, an explanation, and a primary reference after
  submission.
- Frame the result as a benchmark, not a grade. It must not affect lab access,
  completion, certificates, or course ranking.
- Feed quiz participation and accuracy into Cyber DNA as evidence, not as a
  prediction.
- Collect optional post-quiz ratings for satisfaction, relevance, usefulness,
  and ease of use; aggregate them into the course experience report.
- Do not copy real exam questions, braindumps, or NDA-protected material.
- Keep the bank expandable: content lives beside the lab and is validated by
  `scripts/check-quiz-banks.py`.

## Safety and privacy

- Do not expose student PII in aggregate views, exports, or URLs.
- Store feedback author IDs only for duplicate prevention and the student's own
  view.
- Destructive actions (delete course, remove student, reset completions) need
  confirmation and an explanation of what is preserved.
- Keep feedback out of public pages and certificates.
- Never publish an instructor's private coaching note.

## Definition of done

- The page uses the `opencyberrange-design` tokens and Vue conventions.
- Every state is designed: loading, empty, error, permission denied, small
  sample, and long content.
- The feedback summary works with zero new submissions by aggregating existing
  pulse/reaction data.
- Students cannot see other students' feedback or identity.
- The scoreboard is not presented as a public ranking.
- The backend has a test for the summary calculation and the permission rules.
- The documentation and changelog describe the new workspace.
