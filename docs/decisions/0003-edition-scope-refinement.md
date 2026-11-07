# ADR 0003: Edition naming and Professional/Enterprise scope

Status: **Accepted; separate edition version lines superseded by
[ADR 0004](0004-single-platform-release-version.md)**
Date: 2026-11-04
Supersedes: naming and scope in ADR 0002

## Context

ADR 0002 introduced Base, Pro, and Enterprise as three cumulative deployment
editions. The product strategy has since sharpened both the names and the
scope:

- 1.1 is the Community / Academic edition, focused on teaching fundamentals and
  maintenance.
- 2.0 is the Professional edition, focused on educational analytics, reporting,
  competency evidence, and instructor intervention.
- 3.0 is the Enterprise edition, focused on HA, SSO, enterprise reporting,
  multi-tenancy, LMS integration, and regulatory reporting.

The five Professional priorities are explicitly **not** Community / Academic
work:

1. Competency Framework Engine.
2. Student Feedback Engine.
3. Radar / Spider Web Reporting.
4. Exercise Health Analytics.
5. Instructor Intervention Dashboard.

## Decision

Adopt the following edition names and scopes:

| Edition | Version | Scope |
|---|---|---|
| **Community / Academic** | 1.1.x | Teaching platform, lab and workbook improvements, exercise authoring, bug fixes, maintenance and security |
| **Professional** | 2.0.x | Community / Academic plus educational analytics, reporting, cohort analysis, competency framework, feedback engine, radar reporting, exercise health, intervention dashboard, accreditation support, and research exports |
| **Enterprise** | 3.0.x | Professional plus HA, SSO, enterprise reporting, multi-tenant support, LMS integration, and regulatory/compliance reporting |

The editions remain cumulative, share one codebase, and do not change the
repository licence.

The five Professional priorities are inherited by Enterprise. They are not
delivered on the Community / Academic line.

## Consequences

- Documentation, charters, the support matrix, versions, and skills use
  Community / Academic, Professional, and Enterprise consistently.
- Community / Academic remains the reference behaviour and fallback.
- Professional scope is guarded by the priority list; new work needs a written
  scope change.
- Enterprise work must not leak into Professional.
- Commercial licensing is unchanged. The edition names are deployment profiles,
  not commercial licence grants.

## Review

Review at each major release. A boundary change needs an ADR update, a charter
update, and a support-matrix update.
