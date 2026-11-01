# Course and Lab Content Design

OpenCyberRange is a training platform. Visual design must serve learning progression, not just look good in a screenshot.

## Course hierarchy

`Track → Level → Lab`

- A **track** is a subject stream (Windows, Linux, Web, Network, Malware, OT, AI Hacking).
- A **level** is a stage with an ordered set of labs.
- A **lab** is one exercise with a scenario, objectives, hints, a target, a flag, and a workbook.
- Levels unlock sequentially by default. Copy and visuals must make the prerequisite obvious.
- Future levels may exist in the seed without labs; do not present them as available content.

## Lab content contract

Every lab should include:

1. **Name** that states the skill, not just the theme.
2. **Difficulty** (`beginner`, `intermediate`, `advanced`, `expert`).
3. **Category** that matches the track.
4. **Duration** estimate in minutes.
5. **Scenario** that explains who the target is and why the assessment matters.
6. **Objectives** written as observable actions ("decode the register", "capture the flag").
7. **Hints** that scaffold from concept to tool to command.
8. **Automated test steps** that follow the real solve path.
9. **Workbook** with the full walkthrough.
10. **Defensive takeaways** that explain how to prevent the issue.

Do not hide the flag in the scenario, hint, or README in a way that gives away the solution without teaching the method.

## Workbook structure

Use the established chapter pattern:

- `00_Introduction.md` — why the topic matters, what the learner will do, connection details.
- One page per exercise:
  - Before You Begin
  - Scenario
  - Your Objectives
  - Background
  - Walkthrough
  - What Just Happened?
  - Analysis Questions
  - Defensive Takeaways
  - If You Get Stuck
  - Further Reading
- `Chapter Review` — self-assessment, answer key, command cheat sheet, what comes next.

Use Material admonitions intentionally:

- `!!! note` for clarification
- `!!! warning` for safety or destructive actions
- `!!! tip` for a better workflow
- `!!! danger` for a real hazard

## Writing style

- Direct, calm, technical. No hype.
- Explain the "why" before the command.
- Use exact target names, ports, paths, and flags as they appear in the lab.
- Prefer short paragraphs and tables over walls of text.
- Use code fences for commands and expected output.
- Define acronyms on first use.
- Avoid "simply", "just", and "obviously"; they make learners feel behind.
- Use second person for instructions ("Open the target", "Submit the flag").
- Use "we" sparingly; the platform voice is neutral and instructional.

## AI hacking content

AI labs should teach the failure mode, not depend on a specific model version.

- Use deterministic mock targets for core exercises.
- Keep real model APIs optional, never required for a beginner lab.
- State that the target is simulated and safe to attack.
- Cover both attack and defence in every exercise.
- Distinguish direct prompt injection, jailbreak/policy bypass, and indirect injection.
- Warn against testing systems without authorisation.

Never ship a lab that:

- calls a real model with a live secret in the prompt
- depends on external network access for the core solve path
- includes real personal data, real credentials, or real malware
- asks learners to attack infrastructure outside the isolated lab network
- treats a model's self-reported safety as an access-control mechanism

## Certificates and progression UI

- Certificate wording must match the completion rule exactly: every visible exercise in the level is complete.
- Show the level, track, completion count, award date, and deterministic certificate ID.
- A certificate card is a record, not a decorative badge; it must link to the printable certificate.
- Track progress should show both a bar and per-level completion.
- Achievements are course-scoped; do not imply a platform-wide competitive ranking unless the backend supports it.

## Copy for destructive or risky actions

- Name the object and the consequence: "Stop this lab session" not "Stop".
- Explain what is preserved and what is lost.
- Use a confirmation step for irreversible actions.
- Do not use scare styling for normal but important actions.
- For student data, never display more PII than the task requires.

## Design review questions

Before shipping course-facing UI, ask:

1. Can a new student tell what to do next in under ten seconds?
2. Is the prerequisite or lock reason explicit?
3. Does the page explain the difference between "not started", "in progress", "complete", and "certified"?
4. Can an instructor scan a roster and find an exception without opening every row?
5. Does the lab workbook match the actual target, flag, and test steps?
6. Does the content teach defence, not only attack?
