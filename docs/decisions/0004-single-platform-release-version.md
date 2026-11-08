# ADR 0004: One platform release number, edition names as profiles

Status: **Accepted**
Date: 2026-11-07
Supersedes: the separate edition version lines in ADR 0002 and ADR 0003

## Amendment (2026-11-08)

The one-platform-release-number decision is unchanged. The current release is
**2.5.0**, a minor release adding organizational course health, two-way course
feedback, and optional exercise knowledge checks. The previous **2.4.1** patch
release contained the security and UX remediation for the 2.4.0 feature release
(mobile student shell, RangeBox workspace, Events, and Live activity). The
`2.1.4` references below describe the release that established this decision;
edition names remain profiles, not separate version lines.

The legacy history already contains published `v2.2.0` through `v2.3.2` tags,
so this release uses `v2.4.1` rather than moving an existing tag. The earlier
`v2.4.0` tag remains the feature-release snapshot.

## Context

The platform is one cumulative codebase with edition names that describe scope
and entitlement, not separate products. In practice, the separate `1.1`, `2.1`,
and `3.0` version lines have created drift:

- the backend and frontend report `2.1.4`;
- `versions.yaml` still said Professional `2.1.0`;
- the supported-versions page claimed Enterprise `3.1.2`, while the README and
  edition page described Enterprise `3.0.x`;
- documentation and support conversations now spend time reconciling version
  numbers that do not correspond to separate deployables.

The Enterprise HA control plane is a genuinely separate repository and is not
shipped as part of this tree. It should be versioned independently and described
by compatibility, not by pretending it is a third version of this application.

## Decision

1. **One platform release number covers this tree.** The current release is
   `2.1.4`, reported by the backend, frontend, footer, API, images, and release
   notes.
2. **Community / Academic, Professional, and Enterprise are edition profiles,
   not version lines.** They select scope, entitlement, documentation, and
   support expectations.
3. **Community / Academic 1.1.x remains a maintenance line.** Existing installs
   stay supported, but new installs use the `2.1.4` tree with the Community /
   Academic profile. The 1.1 line is not a competing current release number.
4. **Enterprise is a preview profile on `2.1.4` until the HA workstream ships.**
   Do not label it `3.1.2` or any other independent platform version in this
   tree.
5. **The HA control-plane repository has its own version** and a compatibility
   matrix against platform releases. A compatibility statement is not a platform
   version.

## Consequences

- `docs/EDITIONS.md`, `README.md`, `docs/SUPPORTED-VERSIONS.md`, and
  `versions.yaml` use `2.1.4` as the platform release and edition names as
  profiles.
- Release tags identify the platform release, not an edition.
- Documentation may say "Professional profile on 2.1.4" but not "Professional
  2.1.4" as if it were a separate product.
- Enterprise claims must say "preview" until HA, SSO, multi-tenancy, LMS, and
  compliance reporting are shipped and verified.
- A future split into separately versioned deployables would need a new ADR.

## Review

Review this decision when the HA workstream becomes a supported deployment or
when a genuinely separate product is split from this repository.
