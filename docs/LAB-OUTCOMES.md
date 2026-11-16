# Lab outcomes contract

Every lab must expose a measurable outcome, not only a flag. The generated
contract is `platform/backend/app/data/lab-outcomes.yaml`.

## Fields

| Field | Meaning |
|---|---|
| `skills_earned` | The named skills a learner practises, with the competency ID and weight |
| `competencies_proven` | The same evidence with taxonomy category context and weight |
| `knowledge_domains` | The taxonomy domains the lab touches |
| `practice_axes` | The broad practice axes from `lab.yaml` `mapped_skills` |
| `evidence_artifacts` | The accepted evidence: flag, automated validation, analyst finding, submitted artifact |
| `confidence` | Assessment reliability score, level, and basis — not a learner score |
| `review_status` | Whether the contract is baseline-derived or reviewed |

## Source of truth

The generator combines:

1. `platform/backend/app/data/competency-taxonomy.yaml` — the reviewed competency
   catalogue;
2. `platform/backend/app/data/competency-contracts.yaml` — per-lab competency
   weights, evidence, and reliability;
3. `platform/labs/**/lab.yaml` — track, difficulty, workbook, and mapped skills.

```bash
python scripts/generate-lab-outcomes.py
python scripts/generate-lab-outcomes.py --check
```

CI runs `--check` so a lab or taxonomy change cannot silently leave the outcome
contract stale.

## How Cyber DNA and the workbook use it

- The workbook can render **Skills earned**, **Competencies proven**,
  **Knowledge domains**, **Evidence**, and **Confidence** for each lab.
- Cyber DNA can attach evidence to the same competency IDs instead of inventing
  a second mapping.
- Reports and transcripts can show which evidence was required and how reliable
  the assessment is.
- A learner sees what the lab proves and what it does not prove.

## Confidence semantics

Confidence is the **assessment reliability**, derived from the competency
contract. It is not a psychological score, a grade, or a prediction about the
learner. A `0.65` medium-confidence contract means the evidence types and
weights are explicit but independent validation may still be pending.

## Review rule

A lab is not “reviewed” merely because the generator produced an entry. Review
requires the harness/evidence check and a human decision recorded in the
competency contract.
