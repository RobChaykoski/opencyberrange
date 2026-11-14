# Automated scoring and AI: transparency statement

Status: **Release 4.** The product does not use an AI model to grade.

## How a result is produced

1. A lab defines a flag and a completion rule.
2. At spawn, the platform seeds a per-session flag hash for the learner.
3. On submission, the platform compares the submitted value with that hash.
4. A match records completion, attempts, hints used, and elapsed time.
5. A mismatch records the attempt and returns guidance.

There is no model, no confidence score, no free-text grading, and no learner
profiling in this path. Quiz and certification scores are deterministic
comparisons against authored answer keys.

## What the product does not do

- It does not send submissions, rubrics, or learner data to an LLM or AI API.
- It does not grade essays or writing style.
- It does not make a solely automated decision with legal or similarly
  significant effect. Final grades remain an institutional decision.

## Human oversight

- Instructors can see the completion evidence, attempts, hints, and time.
- An institution that treats a completion record as a final grade must provide
  the human-review and contest route required by GDPR Article 22 and Quebec
  Law 25.
- The instructor dashboard is the review surface. A formal override record and a
  student-initiated review workflow are Release 5.

## Audit evidence available today

- `flag_attempts` and `lab_completions` record the attempt and completion.
- Admin and activity audit rows record the actor, action, target, time, and IP.
- The flag itself is stored as a hash, not plaintext.

## Release 5 status

- The exercise flag panel states that the result is produced by deterministic
  flag matching and offers **Request human review**.
- A review request stores the learner's reason, source, attempts, completion
  state, and rule version. The learner sees pending/approved/rejected status and
  the instructor's note.
- Instructors see pending requests in **My Courses -> Reviews** and approve or
  reject with a note. Decisions are audited.
- The LTI AGS ledger records rule/score/reviewer data and is gated on instructor
  review before a score is posted.
- Remaining: a deeper per-question rubric breakdown for non-flag assessments.

## Bias and validation

Because there is no writing-style model, a model-bias study is not applicable.
The relevant fairness work is equal access: keyboard and screen-reader access,
time accommodations, language clarity, and identical scoring rules for every
learner. Any future AI feature must add a bias/validation study before release.
