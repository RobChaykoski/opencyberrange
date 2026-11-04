# ADR 0002: Base, Pro, and Enterprise editions

Status: **Accepted; naming and scope refined by
[ADR 0003](0003-edition-scope-refinement.md)**
Date: 2026-11-04

## Context

The project has three release lines but the documentation described them only as
version numbers. Users and maintainers need a stable way to reason about scope,
support, and deployment shape:

- 1.1 is the supported base teaching platform.
- 2.0 adds analytics and reporting on a single host.
- 3.0 adds multi-host HA and identity federation.

Without named editions, the scope guard, support matrix, and sales/operations
conversation drift.

## Decision

Adopt three deployment editions:

| Edition | Version | Scope |
|---|---|---|
| Base | 1.1.x | Single-host teaching platform, maintenance line |
| Pro | 2.0.x | Base plus analytics, reporting, and exports |
| Enterprise | 3.0.x | Pro plus multi-host HA, identity federation, enterprise operations |

The editions are cumulative. Each builds on the previous one. They are not
separate codebases and do not change the repository licence.

## Consequences

- The main README, support matrix, charters, release notes, and HA docs must use
  the edition names consistently.
- The scope guard becomes: Base is maintenance, Pro is analytics/reporting,
  Enterprise is HA/identity/operations.
- Enterprise work must not leak into the Pro line.
- Base remains the reference behaviour and fallback.
- Commercial licensing is unchanged; the edition names are deployment profiles,
  not a commercial licence grant.

## Review

Review the edition boundaries at each major release. A boundary change needs an
ADR update, a charter update, and a support-matrix update.
