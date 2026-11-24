# Competency contract review guide

Status: **human review workflow**. The generator produces a baseline; a person
decides whether it is true.

Release 6.0 needs a reviewed contract for every lab. The review is not a code
change and it is not an approval by the model. It is a subject-matter decision
recorded in one place.

## Where a decision goes

Record the decision in:

`platform/backend/app/data/competency-contract-overrides.yaml`

Do **not** edit `competency-contracts.yaml` by hand. It is generated from the
labs, the mapping, and the overrides file.

## Workflow

```bash
# 1. See the backlog and the smallest tracks first
python scripts/competency-review-packet.py --summary

# 2. Generate one packet, or a track of packets
python scripts/competency-review-packet.py --track AI --limit 1
python scripts/competency-review-packet.py --track AI --out /tmp/ocr-review

# 3. Review the lab and its workbook against the packet
#    platform/labs/<track>/<lab>/lab.yaml

# 4. Add the reviewed entry to competency-contract-overrides.yaml

# 5. Regenerate and validate
python scripts/generate-competency-contracts.py
python scripts/generate-competency-review-queue.py
python scripts/validate-competency-contracts.py
python scripts/audit-release6-coverage.py --require-reviewed
```

`--require-reviewed` fails until every contract is reviewed. That is expected.

## Override template

```yaml
labs:
  ai-1-1-prompt-injection-basics:
    competency_ids:
    - id: AI-001
      weight: 0.4
    - id: AI-002
      weight: 0.3
    - id: AI-003
      weight: 0.2
    - id: AI-004
      weight: 0.1
    evidence_weights:
      flag: 0.35
      validation_step: 0.35
      analyst_answer: 0.2
      artifact: 0.1
    assessment_reliability:
      level: high
      score: 0.85
      evidence_completeness: high
      determinism: deterministic
      independent_validation: pending
      rationale: "Subject-matter review on 2026-11-24. The lab teaches
        prompt injection and mitigation; the flag, validation step, analyst
        answer, and artifact contract is explicit. Harness result recorded
        separately."
    review_status: reviewed
    reviewed_at: '2026-11-24'
```

Do not invent `usage_rank` or `usage_completions`. Leave them out unless you
have the measured values.

## Decision rules

- **Competencies.** The ids describe what the learner actually practises. Do not
  add a competency because the workbook mentions the word once.
- **Weights.** Competency weights sum to 1.0. Evidence weights sum to 1.0.
- **Evidence.** Every listed evidence type can be collected. A human-reviewed
  artifact or analyst answer is present where the lab needs judgement.
- **Criteria.** The assessment criteria are observable and specific.
- **Collection.** No keystrokes, mouse movement, or exhaustive terminal history.
- **Workbook.** The path resolves to the authored chapter.
- **Reliability.** Replace the baseline rationale with what you actually
  verified. If the lab has an executable test manifest, record the harness
  result; if not, say why.

## What not to do

- Do not mark a contract reviewed to improve the percentage.
- Do not copy a rationale from another lab.
- Do not review a lab you cannot inspect.
- Do not edit the generated contract file; the next regeneration will overwrite
  it.

## Related

- [Competency review queue](COMPETENCY-REVIEW-QUEUE.md) (generated)
- [Competency contracts](COMPETENCY-CONTRACTS.md) (generated)
- [Release 6 scope](RELEASE-6-SCOPE.md)
