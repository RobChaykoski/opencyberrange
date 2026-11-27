# Competency and evidence

## Purpose

Turn learner activity into defensible evidence of competency. A lab has a
contract that names the evidence types and weights. Evidence is append-only and
can be reviewed, appealed, exported, and used for readiness.

## Code map

| Concern | Location |
|---|---|
| Evidence router | `platform/backend/app/routers/evidence.py` |
| Competency reviews | `platform/backend/app/routers/competency_reviews.py` |
| Evidence service | `platform/backend/app/services/evidence.py`, `evidence_adapters.py`, `evidence_analytics.py` |
| Competency services | `platform/backend/app/services/competency_contract.py`, `competency_model.py`, `competency_coverage.py`, `competency_radar.py` |
| Rubrics | `platform/backend/app/data/rubrics/`, `services/rubrics.py` |
| Contracts | `platform/backend/app/data/competency-contracts.yaml` (generated) |
| Taxonomy | `platform/backend/app/data/competency-taxonomy.yaml` |
| Model | `platform/backend/app/models/evidence.py`, `competency_review.py` |

## API surface

| Method | Path | Notes |
|---|---|---|
| POST | `/api/evidence` | record evidence |
| GET | `/api/evidence` | list the caller's evidence |
| GET | `/api/evidence/{id}` | evidence detail |
| POST | `/api/evidence/{id}/review` | instructor review |
| POST | `/api/evidence/{id}/appeal` | learner appeal |
| GET | `/api/evidence/appeals/queue` | reviewer queue |
| GET | `/api/evidence/rubrics` | rubric registry |
| GET | `/api/reviews/queue` | competency contract review queue |
| POST | `/api/reviews/{lab_slug}/draft`, `/sign` | contract review workflow |

## Behaviour that matters

- **Append-only evidence.** A correction is a new record or a review, not a
  destructive overwrite.
- **Contract first.** Evidence types and weights come from the lab contract.
- **Human authority.** The instructor decides; the model or rubric recommends.
  There is no LLM-only pass/fail.
- **Unmeasured is not zero.** A missing evidence type is shown as unmeasured.
- **Review queue.** 25 contracts reviewed, 197 pending at the time of writing;
  the generated queue is the source of truth.
- **Appeals.** A learner can appeal; the reviewer decision is recorded.
- **Readiness.** Aggregates are cohort-safe and suppress small groups.

## Persistent state

| Store | Data |
|---|---|
| `evidence_records` | append-only evidence, learner, contract, payload |
| `evidence_reviews` | reviewer decision and rubric |
| `evidence_appeals` | appeal and decision |
| `competency_contract_reviews` | review state and sign-off |
| `lab_outcomes` | generated outcomes data |
| Rubrics YAML | source definitions |

## Fixtures and tests

- Generate contracts and outcomes:

```bash
python scripts/generate-competency-contracts.py
python scripts/generate-lab-outcomes.py
python scripts/validate-competency-contracts.py
```

- Focused tests:

```bash
cd platform/backend
python -m pytest tests/test_evidence_engine.py tests/test_evidence_adapters.py \
  tests/test_evidence_reviews.py tests/test_evidence_appeals.py \
  tests/test_evidence_analytics.py tests/test_competency_contracts.py \
  tests/test_competency_coverage.py -q
```

## Extension checklist

- Add the evidence type to the contract generator, not to a single lab by hand.
- Add a rubric and validate it.
- Add a test for the reviewer and appeal paths.
- Update the competency review guide and queue.
- Do not put learner rows in an exported evidence bundle.

## Related

- [Evidence engine](../../../../docs/EVIDENCE-ENGINE.md)
- [Competency framework](../../../../docs/COMPETENCY-FRAMEWORK.md)
- [Competency review guide](../../../../docs/COMPETENCY-REVIEW-GUIDE.md)
- [Digital cyber transcript](../../../../docs/DIGITAL-CYBER-TRANSCRIPT.md)
- [Capstone builder](../../../../docs/CAPSTONE-BUILDER.md)
