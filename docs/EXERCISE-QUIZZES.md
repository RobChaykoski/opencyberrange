# Exercise Knowledge Checks

Status: **Optional benchmark feature, 2.4.1**

Exercise knowledge checks are short, optional quizzes attached to an exercise.
They are **benchmark practice, not exam items**. They do not affect lab access,
course completion, certificates, or grades. Their purpose is to help a learner
check understanding, guide the next study step, and add evidence to Cyber DNA.

## Student experience

- The check is launched from the exercise row or the Active Lab panel.
- Each attempt draws **2–3 questions** from the exercise's bank.
- Re-attempts are unlimited. A new attempt draws a different set where possible.
- After submission the learner sees the score, the correct answer, an
  explanation, and a reference link for every question.
- The learner can then send optional ratings for satisfaction, relevance,
  usefulness, and ease of use. Those ratings feed the course experience report.
- A 70% score is the benchmark line. The UI calls it a benchmark, never a grade.

## Data and progression

- Quiz attempts add `quiz_attempts`, `quiz_labs`, and `quiz_accuracy` to the
  Cyber DNA signals. They contribute to **Builder** and **Explorer** evidence.
- Four optional achievements are available:
  - **Quiz Ace** — 100% on an exercise check.
  - **Quiz Explorer** — checks across five exercises.
  - **Quiz Scholar** — 80% or better on ten exercise checks.
  - **Quiz Comeback** — improve a score by 30 points or more.
- Course feedback summaries include quiz participation, accuracy, and the four
  experience ratings. No ranking is shown.

## Coverage

The current tree has:

- **10 lab-specific certification banks** for high-value exercises across
  Windows, Linux, Web, Network, Forensics, OSINT, Malware, and AI.
- **11 track fallback banks**, so every exercise in every track has a check even
  when no lab-specific certification bank exists yet.

Run the checker to see the current numbers:

```bash
python scripts/check-quiz-banks.py
```

The checker validates unique question ids, option counts, correct-answer
indices, explanations, references, and the minimum bank size. CI runs it with
`--check`.

## Adding a bank

Create `quiz.yaml` beside the lab's `lab.yaml`:

```yaml
certification:
  name: "CompTIA Security+"
  code: "SY0-701"
  url: "https://www.comptia.org/certifications/security"
  scope: "Benchmark practice inspired by Security+ objectives. Not an actual exam item."

questions:
  - id: "unique-question-id"
    prompt: "Clear, single-answer question?"
    options:
      - "Option A"
      - "Option B"
      - "Option C"
      - "Option D"
    correct: 1
    explanation: "Why B is correct and why the distractors are not."
    reference:
      label: "Official reference label"
      url: "https://example.org/official-reference"
```

Rules:

- Lab-specific certification banks should have **5–6 questions**.
- General or fallback banks should have **at least 2–3** relevant questions.
- Every question needs one correct option, an explanation, and a reference.
- Do not copy an actual exam item, a braindump, or material covered by an NDA.
- Prefer the certification authority or a primary standard body (CompTIA,
  Microsoft, NIST, OWASP, IETF, CISA, ExifTool, Volatility, and similar).
- Verify the reference URL resolves before publishing.
- Keep the language calm and instructional; explain why the distractors are
  wrong where useful.

A track fallback lives at `platform/labs/<Track>/_track_quiz.yaml`. It is used
only when the exercise has no `quiz.yaml` of its own.

## Scoring and privacy

- Correct answers are never returned by the start-attempt endpoint.
- The bank is read from the lab directory at request time, so expanding it is a
  content change.
- Attempts store the selected question ids and answers so old results remain
  reproducible when the bank grows.
- Student feedback is aggregated for instructors. Students never see another
  student's answers or ratings.
- Quiz data is optional; a learner can ignore every check and still complete the
  course.

## Current certification banks

| Track | Exercise | Certification |
|---|---|---|
| Windows | Basic Windows Port Scan | CompTIA Network+ |
| Windows | SMB Null Session Connection | CompTIA Security+ |
| Windows | MS-SQL Version and Instance Enumeration | CompTIA PenTest+ |
| Linux | SSH Basic Login | CompTIA Linux+ |
| Web | Basic SQL Injection (Login) | CompTIA Security+ |
| Network | Packet Capture Analysis | CompTIA CySA+ |
| Forensics | Windows Memory Analysis with Volatility | CompTIA CySA+ |
| OSINT | EXIF Metadata Investigation | CompTIA Security+ |
| Malware | EICAR Triage | CompTIA CySA+ |
| AI | Prompt Injection Basics | OWASP LLM Top 10 |
