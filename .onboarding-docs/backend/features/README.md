# Backend features

Each page describes one major area of backend functionality. Use this index to
find the router, services, models, endpoints, storage, fixtures, and extension
points for a task.

| Feature | What it covers |
|---|---|
| [Login](login/README.md) | Password login, JWT, refresh, sessions, MFA, reauth, lockout |
| [Registration](registration/README.md) | Self-registration, approval, invite codes, age and privacy gates |
| [Roles and admin](roles-and-admin/README.md) | RBAC/PBAC, admin users, security admin, break-glass |
| [Courses](courses/README.md) | Courses, enrolment, assignments, instructor scope, retention |
| [Labs and sessions](labs-and-sessions/README.md) | Catalogue, spawning, networks, RangeBox, expiry |
| [Flags and scoring](flags-and-scoring/README.md) | Flag submission, attempt limits, completions, achievements |
| [Quizzes](quizzes/README.md) | Exercise quizzes, question banks, practice exams, scoring |
| [Analytics and reports](analytics-and-reports/README.md) | Cohorts, dashboards, PDF/CSV reports, integrity manifests |
| [Competency and evidence](competency-and-evidence/README.md) | Contracts, evidence records, reviews, appeals, readiness |
| [Privacy and consent](privacy-and-consent/README.md) | Consent domains, revocation, erasure, suppression, export |
| [Cyber DNA](cyber-dna/README.md) | Events, evidence, affinity, snapshots, GPS boundaries |
| [SSO and LTI](sso-and-lti/README.md) | OIDC, SAML, LDAP, LTI 1.3, identity providers |
| [Uploads and workbook](uploads-and-workbook/README.md) | Lab import, workbook ZIP, workbook answers, wiki build |

## How to read a feature page

Every page has the same shape:

- **Purpose** — the user outcome.
- **Code map** — where the router, service, and model live.
- **API surface** — the main endpoints.
- **Persistent state** — tables and volumes.
- **Fixtures and tests** — how to create data and prove the change.
- **Extension checklist** — what to update when you change it.

## Adding a feature

1. Add a model and migration if new state is needed.
2. Add a Pydantic schema.
3. Add a router with an auth or permission dependency.
4. Put the logic in a service.
5. Add a test for the happy path, the denial path, and the tenant boundary.
6. Update the feature page and the data dictionary if the schema changed.
7. Regenerate the generated records.
