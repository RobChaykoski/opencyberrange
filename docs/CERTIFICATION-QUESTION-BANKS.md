# Certification question banks

Status: **admin-curated; original exam-style practice** (reviewed 12 November
2026).

The exercise knowledge check draws three questions from a certification pathway
that matches the exercise's track. The goal is a short, realistic drill tied to
the work the learner just finished, not a second exam.

## What the learner sees

- A three-question sample, shuffled, with no answers in the response.
- The pathway name, code, domain, and a notice that the items are original
  practice written to public objectives.
- After submit: the selected answer, the correct answer, an explanation, and a
  public reference.
- The sampled-quiz achievements, including the Platinum Check for a perfect
  three-question sample.

## What only administrators see

The full bank is returned by admin-only endpoints:

| Method | Path | Purpose |
|---|---|---|
| GET | `/api/admin/question-banks` | Pathway summaries and validation counts |
| GET | `/api/admin/question-banks/{pathway_id}` | Full bank, answers, explanations, references |
| POST | `/api/admin/question-banks/validate` | Static reliability checks |

The learner endpoints never return `correct`, `explanation`, or `reference`
before submission. The answer key is revealed only in the submitted attempt.

## Source policy

- Items are **original** and written to published objectives. Do not paste
  copyrighted exam questions or braindumps.
- Every item names the objective it tests and a career pathway.
- Every pathway declares the career roles it supports.
- The shared bank currently carries **81 items across 9 pathways**; source and
  licence notes are in [QUESTION-BANK-SOURCES.md](QUESTION-BANK-SOURCES.md).
- Every item has a public `https://` reference that is not the platform itself,
  a local host, a private address, or a placeholder domain.
- Prefer vendor objectives, standards bodies (NIST, IETF, OWASP, MITRE), and
  vendor documentation over secondary blogs.
- Record a `reviewed_at` date and re-check the references when the certification
  or the source changes.

## Reliability checks

Run:

```bash
python scripts/check-question-banks.py
python scripts/check-question-banks.py --check-links
```

The check verifies:

- unique ids and prompts;
- at least two unique options and a valid correct index;
- a substantive explanation;
- a declared domain and objective;
- an external `https://` reference that is not self-referencing;
- a review date and a non-empty pathway definition.

`--check-links` performs a HEAD request for each unique reference. It is optional
because CI and air-gapped hosts may not have outbound access.

The same checks run in the admin **Question banks** tab through **Run
validation** and in `tests/test_certification_quiz.py`.

## Pathway mapping

The most specific pathway wins. A single-track pathway such as Network+ or Linux+
is preferred over a broad pathway such as Security+. If no pathway lists the
track, the exercise falls back to its own `quiz.yaml` bank, then to no check.

Current mappings:

| Track | Preferred pathway |
|---|---|
| network | CompTIA Network+ |
| linux | CompTIA Linux+ |
| web, software-security | OWASP Top 10 |
| ai | OWASP Top 10 for LLM Applications |
| identity, windows | Microsoft SC-900 |
| high-school | ISC2 Certified in Cybersecurity |
| forensics, malware, osint, ot | CompTIA CySA+ |

Broad Security+ items remain available to pathways that list the track when a
more specific pathway does not.

## Adding or changing a bank

1. Edit `platform/backend/app/data/certification-question-banks.yaml`.
2. Keep the `reviewed_at` date current.
3. Run `python scripts/check-question-banks.py`.
4. Run `python -m pytest tests/test_certification_quiz.py -q`.
5. Open **Admin -> Settings -> Question banks** and review the rendered item,
   correct answer, explanation, and reference.
6. Record the review in `docs/UI-VERIFICATION.md` if the change affects the UI.
