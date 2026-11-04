# OpenCyberRange 2.x Program Charter

Status: **Active scope guard**
Owner: Robert Chaykoski
Last reviewed: 2026-11-04

This charter is the source of truth for what 2.x is allowed to become. If a
request, branch, or release note disagrees with this page, the page wins until a
written scope change is accepted.

## Program objective

Ship a 2.0 release that makes OpenCyberRange better at **understanding learning**
and **reporting on it**, while running reliably on the validated 24.04 baseline,
without turning the release into a general platform expansion.

## The 2.x feature set

Only these two workstreams may add product capability in 2.x:

| Workstream | Commitment | Evidence of success |
|---|---|---|
| **Analytics** | Learner growth, course insight, exercise signals, and a shared metric dictionary | A learner can see their own progress; an instructor can see where a cohort is struggling without ranking individuals |
| **Reporting** | Cross-course reports, teaching-review signals, pulse feedback, and exports | An instructor or administrator can review a course and export the evidence |

Nothing else is a 2.x feature commitment. High availability and multi-host lab
pools were moved to v3; see [`V3-HA-LAB-POOL.md`](V3-HA-LAB-POOL.md).

## Allowed outside the feature set

These are allowed because they protect correctness, security, or the release
itself. They do not become feature marketing.

- Bug fixes with a regression test.
- Security fixes and dependency updates.
- Compatibility updates for the host OS, runtime, database, and build toolchain.
- Documentation corrections, release notes, and operational runbooks.
- Small accessibility or usability fixes on an existing in-scope surface.
- Carrying forward a 1.x maintenance feature so 2.x is not a functional
  regression.

A carry-forward is **not** counted as a 2.x feature. The SMTP/registration email
work shipped on 1.1 and is inherited by 2.x for that reason.

## Out of scope for 2.x

These are v3 candidates unless the charter is amended:

- A new scoring or ranking model.
- SSO, SAML, LDAP, or external identity providers.
- LMS, SIS, or calendar integrations.
- New product domains or tracks (beyond curriculum maintenance).
- Multi-host lab pools, distributed scheduling, HA failover, or a new
  architectural target. These are v3 candidates.
- A public leaderboard, predictive model, or automated high-stakes decision.
- A new notification framework, chat system, or support-desk product.

## Current scope register

| ID | Item | Classification | State | Owner |
|---|---|---|---|---|
| A1 | Student learning analytics view | In scope — Analytics | Delivered; deployed on the 24.04 preview | Product |
| A2 | Course analytics overview and exercise drill-down | In scope — Analytics | Delivered; deployed on the 24.04 preview | Product |
| A3 | Metric dictionary and shared definitions | In scope — Analytics | Delivered; deployed on the 24.04 preview | Product |
| R1 | Cross-course Reports page with RAG signals | In scope — Reporting | Delivered; deployed on the 24.04 preview | Product |
| R2 | Pulse surveys and course survey reporting | In scope — Reporting | Delivered; deployed on the 24.04 preview | Product |
| R3 | CSV/PDF export for teaching review | In scope — Reporting | Shipped — CSV and PDF | Product |
| H1 | Ubuntu 24.04 target for 2.0 | Update — required platform path | Partial — host/platform pass; network/lab/recovery gates pending | Platform |
| M1 | 1.1 registration email / SMTP settings | Carry-forward from 1.1 | Inherited | Maintenance |
| M2 | Certificate input hardening | Bug fix | Shipped | Security |
| M3 | Version identity endpoint and footer | Update — operational | Shipped | Platform |
| S1 | OWASP Top 10 security baseline for interface, data, and delivery | Update — required process | Active | Security |
| V3-1 | Configurable scoring model | v3 candidate | Parking lot | Product |
| V3-2 | SSO / external identity | v3 candidate | Parking lot | Platform |
| V3-3 | LMS/SIS integration | v3 candidate | Parking lot | Product |

## Change control

### Adding a feature to 2.x

A new 2.x feature needs a written change request with:

1. The user and the behaviour it changes.
2. The workstream: analytics or reporting.
3. The evidence that proves it worked.
4. The data, privacy, and failure impact.
5. The work it displaces from the current release.
6. A rollback or disable path.

No request, no schedule. A verbal "yes" is not a change.

### Accepting a bug fix or update

A bug fix or update only needs:

- the observed defect or compatibility gap;
- the smallest fix;
- a regression test or validation step;
- a note in the maintenance log.

It still must not grow product surface. If the fix needs a new setting, panel, or
workflow, it is a feature and returns to change control.

### Moving an item to v3

Add it to `docs/V3-PARKING-LOT.md` with:

- the problem it solves;
- why it is not needed for 2.x;
- what would have to be true to schedule it;
- the risk of waiting.

## Cadence

| Moment | Question | Output |
|---|---|---|
| Start of work block | Which register row are we advancing? | One row selected |
| End of work block | Did we finish that row or create a new one? | Register updated |
| Weekly | Does the README still match this charter? | Drift corrected |
| Release gate | Is every shipped feature in the register? | Signed release note |

## Release gate

A 2.x release is ready only when:

- every shipped feature maps to A, R, or H;
- no unregistered feature shipped;
- bug fixes and updates are recorded separately from features;
- the v3 parking lot contains every deferred idea;
- the README, release notes, and register agree;
- H1 (24.04) is frozen and recorded in the support matrix.

**Current status:** analytics and reporting are delivered and running on the
24.04 preview host. 2.0 GA is blocked only by H1 (network/lab/recovery gates).
HA is a v3 workstream and is not a 2.0 release gate.
