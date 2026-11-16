# Release tags

This page maps the tags in the repository to the release they actually
represent. It exists because the history contains several naming eras.

## Current supported release

| Tag | Release | Status |
|---|---|---|
| `v5.17.0` | SWOCTS Cyber Range Release 5.17 | Current feature release (signed annotated tag): admin release/update indicator, RBAC/PBAC role editing and Moves/Adds/Changes, ATT&CK Navigator, report-based DFIR pathway, open dataset registry, and OWASP API/web/agentic validation and lab plans |
| `v5.16.0` | SWOCTS Cyber Range Release 5.16 | Previous feature release (signed annotated tag): OpenWrt appliance segmentation lab, persisted learner report snapshots, checked manual publishing |
| `v5.15.0` | SWOCTS Cyber Range Release 5.15 | Previous feature release (signed annotated tag): RangeBox launch choice and stop dialog, auth states, Cyber DNA discovery, OT scan assistant and gateway lab, Python 3.13, weekly built-image scan |
| `v5.14.0` | SWOCTS Cyber Range Release 5.14 | Previous feature release (signed annotated tag): strict cohorts, certificate design consistency, documentation click fix |
| `v5.13.1` | SWOCTS Cyber Range Release 5.13.1 | Previous patch (signed annotated tag): browser signature verification and public badge CORS |
| `v5.13.0` | SWOCTS Cyber Range Release 5.13 | Previous feature release (signed annotated tag): RemnuxBox KasmVNC, export label content, event badges and badge artwork |
| `v5.12.0` | SWOCTS Cyber Range Release 5.12 | Previous feature release (signed annotated tag): KasmVNC UbuntuBox |
| `v5.11.0` | SWOCTS Cyber Range Release 5.11 | Previous feature release (signed annotated tag): KasmVNC Kali, single-pane workspace, role-aware navigation, export data labels |
| `v5.10.0` | SWOCTS Cyber Range Release 5.10 | Previous feature release (signed annotated tag): profile badge list, name sharing, issuer URL guard |
| `v5.9.1` | SWOCTS Cyber Range Release 5.9.1 | Previous patch (signed annotated tag): badge revocation UI |
| `v5.9.0` | SWOCTS Cyber Range Release 5.9 | Previous feature release (signed annotated tag): badge admin, key rotation, public viewer |
| `v5.8.1` | SWOCTS Cyber Range Release 5.8.1 | Previous patch (signed annotated tag): badge eligibility fix |
| `v5.8.0` | SWOCTS Cyber Range Release 5.8 | Previous feature release (signed annotated tag): Open Badges 3.0 level credentials |
| `v5.7.0` | SWOCTS Cyber Range Release 5.7 | Previous feature release (signed annotated tag): real host package status in About |
| `v5.6.0` | SWOCTS Cyber Range Release 5.6 | Previous feature release (signed annotated tag): cohort enforcement, student filter, platform maintenance |
| `v5.5.0` | SWOCTS Cyber Range Release 5.5 | Previous feature release (signed annotated tag): course cohorts, exercise sets, and requirements |
| `v5.4.0` | SWOCTS Cyber Range Release 5.4 | Previous feature release (signed annotated tag): instructor cross-course overview and trends |
| `v5.3.1` | SWOCTS Cyber Range Release 5.3.1 | Previous UI patch (signed annotated tag): grouped admin navigation, Academy workbooks, IA proposal |
| `v5.3.0` | SWOCTS Cyber Range Release 5.3 | Previous feature release (signed annotated tag): System metrics and graphs |
| `v5.2.2` | SWOCTS Cyber Range Release 5.2.2 | Previous security patch (signed annotated tag): egress rule persistence |
| `v5.2.1` | SWOCTS Cyber Range Release 5.2.1 | Previous security patch (signed annotated tag): default-deny lab egress |
| `v5.2.0` | SWOCTS Cyber Range Release 5.2 | Previous production feature release (signed annotated tag): interaction audit, impersonation records, backup transports |
| `v5.1.2` | SWOCTS Cyber Range Release 5.1.2 | Previous operations patch (signed annotated tag): alert hook, SMB backup path |
| `v5.1.1` | SWOCTS Cyber Range Release 5.1.1 | Previous production patch (signed annotated tag): encrypted off-host backups, monitoring, LDAP dev fix |
| `v5.1.0` | SWOCTS Cyber Range Release 5.1 | Previous production feature release (signed annotated tag): IdP settings transfer |
| `v5.0.1` | SWOCTS Cyber Range Release 5 security patch | Previous production patch (signed annotated tag): SSO hardening and workbook framing |
| `v5.0.0` | SWOCTS Cyber Range Release 5 | Release 5 baseline (signed annotated tag) |
| `v4.0.2` | SWOCTS Cyber Range Release 4 production hotfix | Previous production hotfix (signed annotated tag): RangeBox workspace tabs |
| `v4.0.1` | SWOCTS Cyber Range Release 4 hotfix | Release 4 hotfix (signed annotated tag): login reload loop |
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

`v5.14.0` and later releases are signed with the current release key
`68A817762C831475F00DB54E775050A4C4921814`. The public key is
`docs/release-signing-key.asc`.

Key custody: the current release key has no passphrase. The private key exists
only on the offline signing workstation, and that host's disk must stay
encrypted and the machine powered off when not signing. Do not copy the private
key to a CI runner, a server, or a backup that is stored with the releases. If
the signing host is lost, retire the key and publish a replacement rather than
reusing it.

`v5.13.1`, `v5.13.0`, `v5.12.0`, `v5.11.0`, `v5.10.0`, `v5.9.1`, `v5.9.0`, `v5.8.1`, `v5.8.0`, `v5.7.0`, `v5.6.0`, `v5.5.0`, `v5.4.0`, `v5.3.1`, `v5.3.0`, `v5.2.2`, `v5.2.1`, `v5.2.0`, `v5.1.2`, `v5.1.1`, `v5.1.0`, `v5.0.1`, `v5.0.0`, `v4.0.2`, `v4` and `v4.0.1` are signed with the previous release key
`8E81B5F3FDC5F5A62B0C258791FD6FBC4ADAFDA2`, retained for historical
verification at `docs/release-signing-key-previous.asc`. The previous key's
passphrase was unavailable, so it was retired rather than revoked. `v2.7.0`
is the last unsigned annotated tag, points at `ce7c25bb`, and remains a
documented exception from before the signing gate.

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
release. The current platform releases are the `v5.x` tags on `main`; `v5.16.0`
is the newest.
Release 4 added OIDC, SAML, and LDAP SSO. Multi-tenancy, LMS/LTI,
the per-student accommodation engine, and weekly Jeopardy-style challenge quizzes
that feed Cyber DNA are Release 5.

## Choosing a version

1. Use `main` or the latest `v5.x` tag (currently `v5.16.0`) for new installs.
2. Keep `1.1.x` only for an existing Community / Academic maintenance install.
3. Do not deploy a `v2.2.x`, `v2.3.x`, or `v3.x` tag as the current platform.
4. Check `docs/SUPPORTED-VERSIONS.md` before changing a dependency or host OS.














