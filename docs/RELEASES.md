# Release tags

This page maps the tags in the repository to the release they actually
represent. It exists because the history contains several naming eras.

## Current supported release

| Tag | Release | Status |
|---|---|---|
| `v2.7.0` | SWOCTS Cyber Range 2.7.0 | Current supported platform release (unsigned annotated tag) |
| `v2.6.0` | SWOCTS Cyber Range 2.6.0 | Previous release; upgrade to 2.7.0 |
| `v2.5.5` | SWOCTS Cyber Range 2.5.5 | Previous release; upgrade to 2.7.0 |
| `v2.5.4` | SWOCTS Cyber Range 2.5.4 | Previous release; upgrade to 2.7.0 |
| `v2.5.3` | SWOCTS Cyber Range 2.5.3 | Previous release; upgrade to 2.7.0 |
| `v2.5.2` | SWOCTS Cyber Range 2.5.2 | Previous release; upgrade to 2.7.0 |
| `v2.5.1` | SWOCTS Cyber Range 2.5.1 | Previous release; upgrade to 2.7.0 |
| `v2.4.1` | SWOCTS Cyber Range 2.4.1 | Previous release; upgrade to 2.7.0 |
| `v2.4.0` | SWOCTS Cyber Range 2.4.0 | Feature release before the 2.4.1 remediation; upgrade to 2.7.0 |
| `v2.1.4-professional`, `v2.1.4` | Professional 2.1.4 | Previous current line; upgrade to 2.7.0 |
| `v1.1.x` | Community / Academic 1.1.3 | Maintenance line for existing single-host installs |

`v2.7.0` is an annotated tag without a GPG signature. It points at `ce7c25bb`,
the commit deployed on 11 November 2026. `v2.6.0` points at `2835303b`, the
commit deployed to production (`172.16.16.41` / `https://ctfd.swocts.com`) and
development (`172.16.16.44`) on 11 November 2026.
The release key documented in `docs/SUPPLY-CHAIN.md` still signs the
supply-chain lock and can sign the tag on the release workstation if a signed
tag is required.

## Legacy wave tags

Tags `v2.1.5` through `v2.3.2` are historical wave/build tags from before the
current single-platform release model. They are not newer than `2.7.0` and
should not be used to choose a deployment. The current release number is
recorded in `versions.yaml` and returned by `/api/version`.

## Enterprise branch tags

Tags `v3.0.0` through `v3.1.2` belong to the experimental Enterprise/HA branch.
They are **not** part of the supported single-host release in this tree. The
Enterprise profile on 2.6.0 is a preview; HA, SSO, multi-tenancy, LMS, and
compliance reporting are not shipped in the supported deployment.

## Choosing a version

1. Use `main` or the latest `v2.7.x` tag for new installs.
2. Keep `1.1.x` only for an existing Community / Academic maintenance install.
3. Do not deploy a `v2.2.x`, `v2.3.x`, or `v3.x` tag as the current platform.
4. Check `docs/SUPPORTED-VERSIONS.md` before changing a dependency or host OS.
