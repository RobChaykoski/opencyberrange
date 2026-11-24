# Competency contract review guide

Status: **human review workflow**. The generator produces a baseline; a person
decides whether it is true.

Release 6.0 needs a reviewed contract for every lab. The review is not a code
change and it is not an approval by the model. It is a subject-matter decision
recorded in one place.

## Where a decision goes

The preferred route is the contract-review API and dashboard form described in
[Competency review cycle](COMPETENCY-REVIEW-CYCLE.md). The YAML override is the
export artifact, not the sign-off record.

For the current file-based workflow, record the decision in:

`platform/backend/app/data/competency-contract-overrides.yaml`

Do **not** edit `competency-contracts.yaml` by hand. It is generated from the
labs, the mapping, and the overrides file.

## Dashboard and export workflow

1. Open **Contract review** in the instructor navigation.
2. Inspect the competencies, evidence, reliability, and criteria. Choose a
   review cycle and sign an approval or a change request.
3. An administrator exports the approved reviews:

   ```bash
   python scripts/export-contract-reviews.py --export \
     --database-url "$DATABASE_URL" \
     --admin-export /secure/ocr-contract-reviews.json
   python scripts/export-contract-reviews.py --write-overrides \
     --database-url "$DATABASE_URL"
   ```

4. Regenerate and validate:

   ```bash
   python scripts/generate-competency-contracts.py
   python scripts/generate-competency-review-queue.py
   python scripts/validate-competency-contracts.py
   ```

5. Run the signed-review gate:

   ```bash
   python scripts/export-contract-reviews.py --check
   ```

The manifest at `docs/competency-reviews.lock.json` is pseudonymous and
committable. The administrator export contains reviewer names and rationales;
store it outside the repository.

## File-based workflow

Use this only when the dashboard is unavailable. A signed review is still the
preferred record.

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

A dashboard export writes the full `evidence` list (type, weight, source, and
validation), `assessment_criteria`, `review_id`, `review_hash`, `reviewer_ref`,
and `reviewer_role`. Both the `evidence` and `evidence_weights` forms are
supported; do not include both. The export script removes `evidence_weights` when
it writes an entry.

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

## Review cycle

A review is not permanent. The signed record carries a 6, 12, or 24 month
cycle and a next-review date. A lab or taxonomy change makes the review stale.
See [Competency review cycle](COMPETENCY-REVIEW-CYCLE.md).

## Related

- [Competency review queue](COMPETENCY-REVIEW-QUEUE.md) (generated)
- [Competency contracts](COMPETENCY-CONTRACTS.md) (generated)
- [Release 6 scope](RELEASE-6-SCOPE.md)
