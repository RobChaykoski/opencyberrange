# Certification practice

Status: **v1 standalone practice** over the reviewed certification bank.
Inspired by the open-source CloudCertPrep model (MIT); no content or code was
copied into this repository.

The exercise check asks three questions after a lab. This page describes the
separate drill: a learner chooses a certification pathway and sits a timed mock
exam or a domain drill.

## Modes

| Mode | What it does |
|---|---|
| Mock exam | Samples the pathway across domains, up to the configured size, with a timer and pass mark |
| Domain drill | Samples only one domain, for focused repair |

Both modes return the same review: selected answer, correct answer, explanation,
public reference, and domain accuracy.

## What the learner sees before submission

- The prompt, the domain, and the objective.
- Options in a **per-question shuffled order**, labelled A–F.
- The timer and the number answered.
- A question navigator.

The response never contains `correct`, `explanation`, or `reference` while the
attempt is active. The correct answer is not in the browser.

## What the learner sees after submission

- Score, percentage, pass/fail against the practice pass mark, and timed-out
  state.
- Every question with the selected option, the correct option, the explanation,
  and the public reference.
- Domain accuracy for the pathway.

A pass here is a study signal. It is not a certification, a credential, or a
guarantee. The UI says so in the pathway notice.

## Spaced repetition

Selection is deterministic and explainable:

1. questions never seen come first;
2. then the highest error rate across submitted attempts;
3. then the least recently seen;
4. ties are ordered by question id, and the selected set is shuffled for
   presentation.

No model, no hidden weighting, no "AI difficulty". A learner can see the rule in
the documentation and predict the next attempt.

## Question bank

The bank is the reviewed certification bank in
`platform/backend/app/data/certification-question-banks.yaml`. Practice uses the
same questions as the exercise check, so there is one source of truth and one
validator.

The current bank is small (about 128 items across nine pathways). A mock exam is
therefore a short drill, not a full-length replica. The UI shows the available
count rather than pretending otherwise. Expanding the bank is content work with
its own review and provenance requirements.

## What we did not copy from CloudCertPrep

- Their Astro/Cloudflare/Supabase stack. This platform already owns auth,
  tenancy, evidence, and review; a second stack would fragment it.
- Their question content. It is MIT-licensed, but our policy requires original
  items, reviewed public references, and a recorded provenance note. A bulk
  import would need a separate content audit.
- Guest mode. A guest attempt cannot be tied to a learner or a tenant, and the
  answer key must remain server-side. Guest practice is deferred until it can be
  implemented without weakening answer-key protection or tenancy.

## API

| Method | Path | Purpose |
|---|---|---|
| GET | `/api/practice/pathways` | Pathways, domains, counts, exam config |
| POST | `/api/practice/sessions` | Start a mock or domain drill |
| GET | `/api/practice/sessions` | Recent attempts |
| GET | `/api/practice/sessions/{id}` | Active questions or a submitted review |
| POST | `/api/practice/sessions/{id}/submit` | Score the attempt |
| GET | `/api/practice/progress` | Per-pathway best and per-domain accuracy |

Every endpoint is authenticated and self-only. A session belongs to one learner;
another learner receives `404`.

## Data model (0058)

```text
practice_sessions
  id, institution_id, user_id, pathway_id, pathway_name
  mode, domain_id, question_count, duration_minutes, pass_mark
  status, started_at, expires_at, submitted_at
  score, total, percentage, passed, timed_out

practice_session_questions
  id, session_id, position, question_id, domain_id
  option_order (JSON), selected_index, is_correct, answered_at
```

Tenant RLS is forced on both tables. The session derives its tenant from the
learner; the question rows derive it from the session.

## Delivery

| Phase | Deliverable |
|---|---|
| 6.1 | Mock exam, domain drill, answer-key protection, optional shuffling, history, progress |
| 6.2 | Expand the reviewed bank and add an exam config per pathway |
| 6.3 | Guest practice with server-side grading and no persistence |
| 6.4 | Feed practice outcomes into the evidence ledger and readiness view |

## Acceptance criteria

- An active attempt never returns the correct answer, explanation, or reference.
- A submitted attempt cannot be submitted twice.
- Another learner cannot read the session.
- Spaced repetition prefers unseen, then wrong, then stale questions.
- A domain drill never returns a question from another domain.
- The UI states that a practice pass is not a certification.
- No practice result is published as a credential.
