---
name: OpenCyberRange Program Management
description: Use when planning, scoping, reviewing, or accepting work for OpenCyberRange releases. Guards the 2.x scope to analytics, reporting, and high availability; classifies every request as in-scope, bug fix/update only, or v3; and requires a change decision before new feature work starts.
---

# OpenCyberRange Program Management

Use this skill to keep the release programme aligned to its charter. The job is
not to say yes to good ideas. The job is to keep the current release small
enough to finish and to send everything else to a decision, not to an accidental
commit.

## The one rule

**The current release ships only its declared feature set. Everything else is a
bug fix, a maintenance update, or a v3 candidate.**

For OpenCyberRange 2.x the declared feature set is:

1. **Analytics** — learner, course, and programme insight.
2. **Reporting** — reports, exports, and teaching-review surfaces.
3. **High availability** — multi-host Docker/lab pools, failover, and recovery.

No fourth workstream is added to 2.x without a written scope change.

## Classification workflow

Every request gets exactly one classification before work starts:

| Classification | Meaning | Action |
|---|---|---|
| **In scope** | Directly advances analytics, reporting, or HA | Add to the active workstream |
| **Bug fix** | Restores intended behaviour, security, correctness, or compatibility | Allowed; keep it small and add a regression test |
| **Update** | Dependency, version, OS, documentation, or operational correction with no new product surface | Allowed; record it in the maintenance log |
| **Carry-forward** | Already shipped on the 1.x maintenance line and inherited by 2.x | Do not count as a 2.x feature commitment |
| **v3 candidate** | New product capability, new workflow, new integration, or major model change | Write it in the v3 parking lot; do not implement |
| **Reject** | Conflicts with privacy, safety, or the charter | Record the reason |

If a request does not fit one row in under a minute, it is too vague to schedule.

## The one-sentence test

Before touching code, complete this sentence:

> For **<user>**, this changes **<behaviour>**, measured by **<evidence>**, and
> it belongs to **<analytics / reporting / HA>** because **<reason>**.

If the last blank says "it would be nice", "it is quick", or "we are already in
the file", stop. It is a v3 candidate or a separate maintenance item.

## Scope guardrails

1. **No drive-by features.** Fix the selected bug; do not add a panel, setting,
   integration, or workflow because the file is open.
2. **No new settings unless the feature is in scope.** A new setting is product
   surface, not a bug fix.
3. **No data-model expansion for a side idea.** A migration is a commitment.
4. **No public ranking, prediction, or high-stakes scoring.** Analytics remains
   descriptive and private by design.
5. **No release theme drift.** If the README, charter, and current work do not
   agree, stop and reconcile the documents first.
6. **Major means v3.** Scoring models, SSO/identity providers, LMS integrations,
   new runtime platforms, and new product domains are v3 unless the charter is
   explicitly amended.
7. **Fixes travel backward.** A fix that applies to 1.x lands on the 1.x line
   first, then merges forward. Do not fork behaviour to avoid the merge.

## Required records

Maintain these three living records:

1. `docs/V2-PROGRAM-CHARTER.md` — scope, success measures, guardrails, cadence.
2. The scope register inside that charter — every active item and its
   classification.
3. `docs/V3-PARKING-LOT.md` — ideas that are real but not for 2.x.

Every change request adds one row to the register and, if needed, one row to the
v3 parking lot. The register is the source of truth, not a chat message.

## Review cadence

Run a short review at the start and end of each work block:

- **Start:** What are we doing? Which scope row? What is the evidence?
- **End:** Did we finish the row, or did we start a new one? If the scope moved,
  why?

A weekly review is enough for a small programme. The rule is consistency, not
ceremony.

## Response pattern

When a request arrives, answer in this order:

1. **Classification:** in scope, bug fix, update, carry-forward, v3, or reject.
2. **Why:** one sentence tied to analytics, reporting, or HA.
3. **Decision:** proceed now, defer, or write it down.
4. **Record:** the file/row you updated.

If the request is out of scope, say so plainly and add it to the v3 parking lot.
Do not soften the no with an unplanned implementation.

## Red flags

Escalate to a written scope change if you hear:

- "While we are in here..."
- "It is only a small feature."
- "We can call it analytics."
- "The release is already open."
- "The customer asked for it" — without a charter amendment.
- A new dashboard, integration, role, scoring rule, or service appearing without
  a register row.

## Definition of done for a 2.x item

- It maps to one scope row.
- It has a test or a validation check.
- It has a documentation update.
- It has an explicit rollback or failure path.
- It did not add an unregistered feature.
- The register and the code agree.
