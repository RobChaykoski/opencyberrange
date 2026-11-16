# DFIR analyst report template

Use this structure for every report-based module. Keep it short enough for a
peer to review, but complete enough for another analyst to reproduce the work.

## 0. Short finding

- What happened:
- Evidence used:
- Confidence and alternative explanation:
- Next step or recommendation:

## 1. Case and question

- Case ID:
- Question or hypothesis:
- Scope (hosts, users, time range, evidence sources):
- What is explicitly out of scope:

## 2. Evidence and custody

| Evidence | Source path or system | Acquired at (UTC) | SHA-256 | Custodian |
|---|---|---|---|---|
| | | | | |

State whether you worked on the original or a verified copy. Record the tool
and command used for acquisition.

## 3. Method

- Commands or queries:
- Timezone and clock assumptions:
- Normalisation or parsing steps:
- Known gaps or missing sources:

## 4. Findings

| # | Time (UTC) | Source | Finding | Confidence | Alternative explanation |
|---|---|---|---|---|---|
| 1 | | | | | |

Use exact timestamps, hostnames, users, paths, hashes, and ports. Separate
observation from interpretation.

## 5. Timeline

Provide a short ordered timeline. Mark uncertain ordering and clock skew.

## 6. Impact and scope

- Confirmed affected accounts or hosts:
- Suspected but unconfirmed:
- Data or service impact:
- What the evidence cannot prove:

## 7. Response recommendations

- Immediate containment:
- Eradication and recovery:
- Notification or escalation:
- Evidence to preserve:

## 8. Lessons learned

- Detection or logging gap:
- Process or control improvement:
- Follow-up owner and date:

## 9. Reviewer sign-off

- Reviewer:
- Review date:
- Decision: accepted / needs revision
- Open questions:
