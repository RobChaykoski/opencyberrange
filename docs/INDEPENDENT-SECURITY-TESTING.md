# Independent security testing

## Status

**Not yet commissioned.** No independent penetration test or third-party
security assessment has been completed for Release 5.17.2. This page must not
be cited as evidence that one exists.

## Why it matters

Internal tests, CodeQL, Trivy, dependency audits, and a lab harness are useful
engineering controls. They are not an independent assessment of the production
deployment, multi-tenant isolation, authentication flows, or operational
recovery.

## Required scope

Commission a tester with web application, API, identity, and container
experience. The scope should include:

- authentication, MFA, session, refresh, and re-authentication flows;
- object, function, and tenant authorization, including two-institution tests;
- API and GraphQL surfaces, including rate limits and error handling;
- RBAC/PBAC administration and break-glass controls;
- file upload, export, badge, certificate, and LTI surfaces;
- container and Kubernetes-adjacent configuration where deployed;
- backup/restore and cutover procedures;
- social engineering and physical testing only if separately authorised.

Out of scope unless separately authorised: denial of service against the
production host, testing another institution's data, destructive database
tests, and attacks on third-party providers.

## Procurement requirements

- signed statement of work and rules of engagement;
- named testers, dates, source IPs, and emergency contact;
- written authorisation for the production host and any test accounts;
- data-handling and confidentiality terms;
- evidence handling and secure deletion;
- a remediation window and retest option.

## Published summary template

When a test is complete, replace this section with a dated summary:

| Field | Value |
|---|---|
| Tester | |
| Dates | |
| Scope | |
| Critical findings | |
| High findings | |
| Medium / low findings | |
| Retest status | |
| Report location | |

Do not publish exploit details, credentials, or another institution's data.
Publish the dated summary and remediation status, not a raw report.
