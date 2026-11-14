# Release tags

This page maps the tags in the repository to the release they actually
represent. It exists because the history contains several naming eras.

## Current supported release

| Tag | Release | Status |
|---|---|---|
| `v4.0.1` | SWOCTS Cyber Range Release 4 hotfix | Current production hotfix (signed annotated tag): login reload loop |
| `v4` | SWOCTS Cyber Range Release 4 | Release 4 baseline (signed annotated tag) |
| `v3` | SWOCTS Cyber Range Release 3 | Previous supported release (signed annotated tag) |
| `v2.7.0` | SWOCTS Cyber Range 2.7.0 | Previous release; upgrade to Release 4 (unsigned tag; documented exception) |
| `v2.6.0` | SWOCTS Cyber Range 2.6.0 | Previous release; upgrade to Release 3 |
| `v2.5.5` | SWOCTS Cyber Range 2.5.5 | Previous release; upgrade to Release 3 |
| `v2.5.4` | SWOCTS Cyber Range 2.5.4 | Previous release; upgrade to Release 3 |
| `v2.5.3` | SWOCTS Cyber Range 2.5.3 | Previous release; upgrade to Release 3 |
| `v2.5.2` | SWOCTS Cyber Range 2.5.2 | Previous release; upgrade to Release 3 |
| `v2.5.1` | SWOCTS Cyber Range 2.5.1 | Previous release; upgrade to Release 3 |
| `v2.4.1` | SWOCTS Cyber Range 2.4.1 | Previous release; upgrade to Release 3 |
| `v2.4.0` | SWOCTS Cyber Range 2.4.0 | Feature release before the 2.4.1 remediation; upgrade to Release 3 |
| `v2.1.4-professional`, `v2.1.4` | Professional 2.1.4 | Previous current line; upgrade to Release 3 |
| `v1.1.x` | Community / Academic 1.1.3 | Maintenance line for existing single-host installs |

`v4` and `v4.0.1` are signed with the release key
`8E81B5F3FDC5F5A62B0C258791FD6FBC4ADAFDA2`. The public key is
`docs/release-signing-key.asc`. `v2.7.0` is the last unsigned annotated tag,
points at `ce7c25bb`, and remains a documented exception from before the
signing gate.

## Release tag checklist

1. Confirm `versions.yaml`, `README.md`, and `/api/version` agree on the release.
2. Confirm CI, Quality checks, CodeQL, Trivy, and the supply-chain lock are green.
3. Create a signed annotated tag on the release commit:
   `git tag -s vX.Y.Z -m "SWOCTS Cyber Range X.Y.Z"`.
4. Verify the signature locally: `git tag -v vX.Y.Z`.
5. Push the tag: `git push origin vX.Y.Z`.
6. Record the tag, commit, and signature status in this file and in the release
   notes.

## Legacy wave tags

Tags `v2.1.5` through `v2.3.2` are historical wave/build tags from before the
current single-platform release model. They are not newer than `2.7.0` and
should not be used to choose a deployment. The current release number is
recorded in `versions.yaml` and returned by `/api/version`.

## Enterprise branch tags

Tags `v3.0.0` through `v3.1.2` belong to the experimental Enterprise/HA branch
and are historical. They are **not** the supported single-host platform
release. The platform release `v4` is the signed tag on the current tree.
Release 4 ships OIDC, SAML, and LDAP SSO. Multi-tenancy, LMS/LTI, the
per-student accommodation engine, and weekly Jeopardy-style challenge quizzes
that feed Cyber DNA are Release 5.

## Choosing a version

1. Use `main` or the latest `v4` tag for new installs.
2. Keep `1.1.x` only for an existing Community / Academic maintenance install.
3. Do not deploy a `v2.2.x`, `v2.3.x`, or `v3.x` tag as the current platform.
4. Check `docs/SUPPORTED-VERSIONS.md` before changing a dependency or host OS.
