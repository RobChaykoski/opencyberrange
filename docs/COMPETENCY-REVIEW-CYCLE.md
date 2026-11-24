# Competency review cycle

Status: **backend review cycle implemented; dashboard form is the next slice**.
The current instructor workflow is the packet plus the YAML overrides file. The
API now records a signed review with a period and a next-review date.

Release 6.0 requires every lab contract to be reviewed. A one-time review is not
enough: the exercise changes, the taxonomy changes, the evidence mix changes, and
the instructor who signed it may leave. The review needs a cycle.

## Cycle states

| State | Meaning |
|---|---|
| `pending` | No signed review exists |
| `draft` | A reviewer started a review but has not signed |
| `changes_requested` | The reviewer signed a request for changes; the contract is not approved |
| `current` | A signed approval exists and the lab and taxonomy hashes still match |
| `due_soon` | The next review date is within 60 days |
| `overdue` | The next review date has passed |
| `stale` | The lab content or the taxonomy changed after the signature |

A stale contract is not silently trusted. The queue ranks `overdue`, `stale`,
`changes_requested`, `pending`, `due_soon`, `draft`, and `current` in that order.

## Cycle length

The reviewer selects **6, 12, or 24 months**. The default is 12.

- **6 months** for advanced, high-use, or low-reliability contracts.
- **12 months** for most contracts.
- **24 months** for stable, low-change contracts with strong evidence.

The next review date is calculated from the signature date. A cycle is a policy
choice, not a prediction.

## Sign-off

The instructor signs one review with:

- the competency list and weights;
- the evidence types and weights;
- the reliability level and rationale;
- an explicit attestation: they inspected the exercise, workbook, and evidence;
- a decision: **approved** or **changes requested**;
- the cycle length and the next review date.

The signature stores the contract hash, the lab content hash, and the taxonomy
hash. A later change to the lab or the taxonomy makes the review `stale`.

The instructor does not edit the generated contract file. An administrator or
release operator exports the approved reviews, regenerates the contracts, runs
the validator, and signs the supply-chain lock.

## API

| Method | Path | Purpose |
|---|---|---|
| GET | `/api/competency-reviews/queue` | Cycle queue with status counts |
| GET | `/api/competency-reviews/{lab_slug}` | Contract, latest review, history, hashes |
| POST | `/api/competency-reviews/{lab_slug}/draft` | Save an unsigned draft |
| POST | `/api/competency-reviews/{lab_slug}/sign` | Sign an approval or a change request |
| GET | `/api/competency-reviews/export-ready` | Approved, signed, not exported |
| POST | `/api/competency-reviews/{id}/exported` | Administrator marks an export |

The queue and detail are available to instructors, administrators, mentors, and
teaching assistants in the tenant. Only an administrator can mark an export.

## Data model

```text
competency_contract_reviews
  id, institution_id, lab_slug
  status, decision
  contract_snapshot, contract_hash, lab_hash, taxonomy_hash
  rationale, attestation
  reviewer_id, reviewer_role
  review_cycle_months, next_review_at, signed_at
  exported_at, exported_by_id
  created_at, updated_at
```

The table is append-only for signed decisions. A newer signed approval supersedes
the older signed row; the history remains.

## Export rule

Only an approved, signed review with no export timestamp is exportable. The
export writes the reviewed values into
`platform/backend/app/data/competency-contract-overrides.yaml`, then the operator
runs:

```bash
python scripts/generate-competency-contracts.py
python scripts/generate-competency-review-queue.py
python scripts/validate-competency-contracts.py
python scripts/audit-release6-coverage.py --fail-on-gaps
```

Then the operator signs the supply-chain lock. The review record and the
generated contract must agree before the release tag.

## Dean and administrator view

The dean needs cycle coverage, not learner rows:

- contracts current, due soon, overdue, stale, pending;
- coverage by track and by reviewer;
- reviews signed this term and reviews waiting for export;
- contracts whose lab content changed after signature.

No learner record is part of the cycle view.

## Acceptance criteria

- A reviewer can draft, sign, and request changes.
- A signature requires an attestation and a rationale.
- The queue shows current, due soon, overdue, stale, and pending.
- A lab or taxonomy change makes a signature stale.
- Only an approved signed review can be exported.
- Only an administrator can mark an export.
- A signed review stores the hashes it reviewed.
- Another instructor can see the queue, but the review is attributed to its
  signer.
- No export mutates the running application contract.

## Next slice

- Dashboard form with taxonomy picker, weights, reliability, rationale,
  attestation, and cycle selection.
- Queue status chips and a due/overdue summary for the dean.
- Export script and an export status panel.


## Controls in the reviewed slice

- **Tenant scope.** Reads, drafts, signatures, export-ready rows, and export
  marking are filtered by the caller's institution unless the caller is a
  platform administrator.
- **Signer roles.** Instructors, institution administrators, and platform
  administrators can sign. Mentors and teaching assistants can view the queue
  but cannot sign.
- **Draft ownership.** Another reviewer cannot overwrite a draft. An
  administrator must reassign it.
- **Immutable signatures.** A database guard preserves the tenant and the signed
  integrity fields after sign-off. A partial unique index allows one active
  signed review per institution and lab.
- **Precise staleness.** The lab hash covers the contract-bearing Markdown and
  YAML files plus the test manifest. The taxonomy hash covers only the
  competency ids in the review, so an unrelated taxonomy addition does not stale
  every contract.
- **Audit events.** Sign, supersede, and export actions are written to the audit
  log with the review, actor, decision, and hashes.
- **Export gate.** Export-ready returns only current or due-soon reviews. Stale,
  overdue, and changes-requested rows are returned as blocked. A second export
  is rejected.

## Deferred before the 6.0 release gate

1. An export manifest and a CI check that every `review_status: reviewed`
   contract has a signed review with the same contract hash. Today the review
   record and the YAML gate are still separate.
2. Track ownership, assignment, reassignment, due/overdue notification, and
   escalation to a track lead or dean.
3. A learner-visible gate that marks evidence and competency statements
   provisional when the underlying contract is stale, overdue, or
   changes-requested.
4. A dean aggregate view: current, due soon, overdue, stale, and pending by
   track and reviewer; signed this term; awaiting export.
5. Recent reauthentication and MFA before sign-off; PBAC permissions for
   `competency.review.sign` and `competency.review.export`.
6. A sample audit and calibration report.
