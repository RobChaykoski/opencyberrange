# SWOCTS Cyber Range Professional 2.x Program Charter

Status: **Active scope guard**
Edition: **Professional** â€” Community / Academic 1.1 plus analytics, reporting,
cohort analysis, competency evidence, and research exports
Owner: Robert Chaykoski
Last reviewed: 2026-11-04

See [Editions](EDITIONS.md) for the Community / Academic, Professional, and
Enterprise boundary, and [ADR 0003](decisions/0003-edition-scope-refinement.md)
for the naming and scope decision.

The five Professional priorities are:

1. Competency Framework Engine.
2. Student Feedback Engine.
3. Radar / Spider Web Reporting.
4. Exercise Health Analytics.
5. Instructor Intervention Dashboard.

They are described in
[Professional and Enterprise priorities](PROFESSIONAL-PRIORITIES.md) and are
**Professional and Enterprise only**. They are not Community / Academic work.

This charter is the source of truth for what 2.x is allowed to become. If a
request, branch, or release note disagrees with this page, the page wins until a
written scope change is accepted.

## Program objective

Ship the **Professional 2.0** edition: the Community / Academic 1.1 teaching
platform plus the capability to **understand learning**, **evidence
competency**, and **report on it**, while running reliably on the validated
24.04 baseline, without turning the release into a general platform expansion.

Professional is not the HA, SSO, multi-tenant, LMS, or compliance-reporting
edition. Those are **Enterprise 3.0**.

## The 2.x feature set

Only these two workstreams may add product capability in 2.x:

| Workstream | Commitment | Evidence of success |
|---|---|---|
| **Analytics** | Educational analytics, cohort analysis, instructor dashboards, the Competency Framework Engine, the Student Feedback Engine, radar reporting, exercise health, and intervention signals | A learner can see their own growth; an instructor can see where a cohort is struggling and which competency is weak without ranking individuals |
| **Reporting and evidence** | Cross-course reports, accreditation support, teaching-review signals, and research exports | An instructor, programme lead, or approved researcher can review a course or cohort and export the evidence |

The five priority capabilities sit inside these two workstreams. Nothing else is
a Professional 2.x feature commitment. High availability, SSO, enterprise
reporting, multi-tenant support, LMS integration, and regulatory/compliance
reporting are **Enterprise 3.0**; see
[`V3-PARKING-LOT.md`](V3-PARKING-LOT.md) and [`EDITIONS.md`](EDITIONS.md).

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

These are Enterprise 3.0 candidates unless the charter is amended:

- A new scoring or ranking model.
- SSO, SAML, LDAP, or external identity providers.
- LMS, SIS, or calendar integrations.
- Multi-tenant support and tenant isolation.
- Enterprise reporting and regulatory/compliance reporting.
- New product domains or tracks (beyond curriculum maintenance).
- Multi-host lab pools, distributed scheduling, HA failover, or a new
  architectural target.
- A public leaderboard, predictive model, or automated high-stakes decision.
- A new notification framework, chat system, or support-desk product.

## Current scope register

| ID | Item | Classification | State | Owner |
|---|---|---|---|---|
| A1 | Student learning analytics view | In scope â€” Analytics | Delivered; deployed on the 24.04 preview | Product |
| A2 | Course analytics overview and exercise drill-down | In scope â€” Analytics | Delivered; deployed on the 24.04 preview | Product |
| A3 | Metric dictionary and shared definitions | In scope â€” Analytics | Delivered; deployed on the 24.04 preview | Product |
| C1 | Competency Framework Engine | In scope â€” Analytics | Planned | Product |
| C2 | Student Feedback Engine | In scope â€” Analytics | Planned | Product |
| C3 | Radar / Spider Web Reporting | In scope â€” Analytics | Planned | Product |
| C4 | Exercise Health Analytics | In scope â€” Analytics | Planned | Product |
| C5 | Instructor Intervention Dashboard | In scope â€” Analytics | Planned | Product |
| R1 | Cross-course Reports page with RAG signals | In scope â€” Reporting | Delivered; deployed on the 24.04 preview | Product |
| R2 | Pulse surveys and course survey reporting | In scope â€” Reporting | Delivered; deployed on the 24.04 preview | Product |
| R3 | CSV/PDF export for teaching review | In scope â€” Reporting | Shipped â€” CSV and PDF | Product |
| R4 | Cohort analysis and accreditation support | In scope â€” Reporting | Planned | Product |
| R5 | Research exports for approved studies | In scope â€” Reporting | Partial â€” cross-course CSV/PDF and survey package | Research |
| H1 | Ubuntu 24.04 target for 2.0 | Update â€” required platform path | Partial â€” host/platform pass; network/lab/recovery gates pending | Platform |
| M1 | 1.1 registration email / SMTP settings | Carry-forward from 1.1 | Inherited | Maintenance |
| M2 | Certificate input hardening | Bug fix | Shipped | Security |
| M3 | Version identity endpoint and footer | Update - operational | Shipped | Platform |
| M4 | Admin user record preview and edit usability | Update - usability fix on an existing admin surface | Delivered in this change | Design |
| M5 | Admin password reset re-authentication and dedicated action | Bug fix - security | Delivered in this change | Security |
| S1 | OWASP Top 10 security baseline for interface, data, and delivery | Update - required process | Active | Security |
| V3-1 | Configurable scoring model | Enterprise candidate | Parking lot | Product |
| V3-2 | SSO / external identity | Enterprise candidate | Settings only | Platform |
| V3-3 | LMS/SIS integration | Enterprise candidate | Parking lot | Product |
| V3-4 | Multi-tenant support | Enterprise candidate | Parking lot | Platform |
| V3-5 | Enterprise and compliance reporting | Enterprise candidate | Parking lot | Product |

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
