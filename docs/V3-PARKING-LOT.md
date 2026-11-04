# OpenCyberRange v3 Parking Lot

This file holds real ideas that are deliberately **not** in the 2.x programme.
Keeping them here prevents scope drift without losing them.

## Rules

- Every deferred feature gets an entry.
- An entry is not a commitment.
- Moving an entry into v3 requires its own plan, measures, and release gate.
- Moving an entry into 2.x requires a written charter amendment and a displaced
  item.

## Candidates

| ID | Candidate | Problem it solves | Why not 2.x | What would make it schedulable |
|---|---|---|---|---|
| V3-1 | Configurable scoring model | Instructors want course-specific weighting and clearer score explanations | Scoring is a major product model change; 2.x is analytics, reporting, and HA only | A validated scoring design, instructor review, migration plan, and a release gate |
| V3-2 | SSO / SAML / LDAP | Institutions want central identity | New identity surface and security boundary | Requirements from at least one institution and a security review |
| V3-3 | LMS / SIS integration | Course rosters and grades need to sync | New integration and data-sharing contract | A named LMS, data-sharing agreement, and privacy review |
| V3-4 | Public leaderboard | Some cohorts want public competition ranking | Conflicts with the current privacy and non-ranking stance | A deliberate policy change with opt-in and safeguarding review |
| V3-5 | Predictive learner risk model | Early support for struggling learners | High-stakes prediction risk; current analytics are descriptive only | Validation evidence, human-in-the-loop design, and an ethics review |
| V3-6 | Notification framework | More than registration email, with preferences | New product surface | A notification inventory and consent model |
| V3-7 | Additional runtime target beyond the Docker lab pool | Kubernetes or other orchestrators | 2.x HA focuses on the controller/agent lab pool first | A proven 2.x pool and a separate runtime adapter plan |

## Not a candidate

Do not park work here to avoid saying no. A request that conflicts with privacy,
safety, or licensing is rejected, not deferred.
