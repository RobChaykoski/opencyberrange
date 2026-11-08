# SWOCTS Cyber Range Enterprise preview parking lot

> **Version note:** This document keeps its historical V2/V3 filename. The current platform release is **2.4.0**; Community / Academic, Professional, and Enterprise are edition profiles on that release.

This file holds real ideas that are deliberately **not** in the Professional
2.1.4 programme. Keeping them here prevents scope drift without losing them.

Enterprise preview is the HA, SSO, enterprise reporting, multi-tenant, LMS, and
regulatory/compliance profile. It builds on Professional 2.1.4 and the
Community / Academic profile, and inherits the five Professional priorities. See
[Editions](EDITIONS.md) and
[Professional and Enterprise priorities](PROFESSIONAL-PRIORITIES.md).

## Rules

- Every deferred feature gets an entry.
- An entry is not a commitment.
- Moving an entry into the Enterprise preview profile requires its own plan,
  measures, and release gate.
- Moving an entry into Professional requires a written charter amendment and a
  displaced item.

## Candidates

| ID | Candidate | Problem it solves | Why not Professional | What would make it schedulable |
|---|---|---|---|---|
| V3-1 | Configurable scoring model | Instructors want course-specific weighting and clearer score explanations | Scoring is a major product model change; 2.1.4 is analytics, reporting, and competency evidence | A validated scoring design, instructor review, migration plan, and a release gate |
| V3-2 | SSO / SAML / LDAP | Institutions want central identity | New identity surface and security boundary | Settings UI exists on `v3`; login flows, provider tests, and a security review remain |
| V3-3 | LMS / SIS integration | Course rosters and grades need to sync | New integration and data-sharing contract | A named LMS, data-sharing agreement, and privacy review |
| V3-4 | Multi-tenant support | One deployment serves several institutions or faculties | Tenant isolation changes the data model and operations | A tenancy model, isolation tests, migration plan, and security review |
| V3-5 | Enterprise reporting | Institution-wide reporting across tenants and cohorts | Professional reports stop at the programme/course boundary | A reporting model, role model, and export contract |
| V3-6 | Regulatory and compliance reporting | Accreditors and regulators need evidence in a defined format | Compliance regimes vary by jurisdiction and institution | A named regime, evidence map, retention rules, and legal review |
| V3-7 | Public leaderboard | Some cohorts want public competition ranking | Conflicts with the current privacy and non-ranking stance | A deliberate policy change with opt-in and safeguarding review |
| V3-8 | Predictive learner risk model | Early support for struggling learners | High-stakes prediction risk; current analytics are descriptive only | Validation evidence, human-in-the-loop design, and an ethics review |
| V3-9 | Notification framework | More than registration email, with preferences | New product surface | A notification inventory and consent model |
| V3-10 | Additional runtime target beyond the Docker lab pool | Kubernetes or other orchestrators | HA is an Enterprise workstream; the controller/agent pool comes first | A proven controller/agent pool and a separate runtime adapter plan |
| V3-11 | Multi-host HA lab pool | Capacity and availability across multiple Docker lab hosts; sessions must survive control-plane failure and recover after node loss | Moved out of 2.1.4 to keep the release focused on analytics and reporting | The phased plan in [V3-HA-LAB-POOL.md](V3-HA-LAB-POOL.md), capacity targets, and a failover release gate |

## Not a candidate

Do not park work here to avoid saying no. A request that conflicts with privacy,
safety, or licensing is rejected, not deferred.
