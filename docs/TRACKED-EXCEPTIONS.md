# Tracked exceptions and open findings

Status: **living register.** Every accepted risk or deferred fix has an owner, a
status, and the evidence needed to close it. An item closes only when the code or
document that removes it is linked here.

This page is the paper trail for an institutional security review. It does not
replace the detailed pages it references.

## How to use it

- Add a row when a review accepts a risk or defers a fix.
- Name the owner and the next action; do not leave "TBD".
- When an item closes, keep the row, set the status to **Closed**, and link the
  commit or test that proves it.
- Review the open rows at every release.

## Host scripts and runtime

| ID | Item | Severity | Status | Evidence / next action |
|---|---|---|---|---|
| HS-01 | `scripts/deploy-updates.sh` signature order | High | **Audited, fixed** | Fetch → verify tag → checkout verified commit → supply-chain check → apply. Signer fingerprint parsed from the GPG `using ... key` line, checkout bound to the verified tag object, backups mode 700 and pruned, prerelease tags excluded from auto-selection, and the state file records the verified ref/SHA. See [Host script security](HOST-SCRIPT-SECURITY.md#deploy-updates-audit). |
| HS-02 | `scripts/setup-range-server.sh` | High | Open | Read every branch that runs as root; verify it does not execute an unverified tree. |
| HS-03 | `scripts/install-platform.sh` | High | Open | Same audit as HS-02. |
| HS-04 | `scripts/harden-lab-egress.sh` | High | **Audited, hardened** | Added an IPv6 guard (fails when any Docker network has IPv6 enabled) and a digest-pin warning for the privileged image. Remaining: unknown-subnet discovery is point-in-time; re-run from the VPN firewall unit or fail on out-of-range subnets. |
| HS-08 | Privileged egress image uses a mutable tag | Medium | Open | Publish and pin `opencyberrange/rangebox:lite` by digest; `HARDEN_STRICT=1` now fails when it is not pinned. |
| HS-05 | systemd units (`ocr-platform.service`, timers) | Medium | Open | Confirm `WorkingDirectory`, `ExecStart`, and environment files point at the verified tree. |
| HS-06 | `docker_manager.py` (about 80% unread) | High | Open | Continue the security review; focus on container creation, mounts, and the Docker socket proxy. |
| HS-07 | 8443 / Kasm noVNC trust boundary | High | Open | Document the origin, certificate, and framing policy; add a test. |

## Release blockers from the code reviews

| ID | Item | Severity | Status | Evidence / next action |
|---|---|---|---|---|
| RB-01 | `admin.py` async endpoints block the event loop | High | Open | Move blocking work to `asyncio.to_thread`; add a latency test. |
| RB-02 | Middleware decodes the JWT 2–3 times and opens 2–4 DB sessions per request | High | Open | Decode once per request; share the session or close it deterministically. |
| RB-03 | `exercise_tester.py` cross-tenant flag disclosure | Critical | Open | Scope every lookup to the caller's tenant; add a denial test. |
| RB-04 | `exercise_tester.py` `timeout` command injection | Critical | Open | Pass arguments as a list; never interpolate into a shell. Add a regression test. |
| RB-05 | Analytics minor exclusion misses `course_pulse_comments` and `survey_responses` | High | Open | Apply the same under-18 exclusion used elsewhere; add a test. |
| RB-06 | Wiki served same-origin with `unsafe-inline` CSP on internet-facing installs | High | Open | Serve the wiki on its own origin or tighten the CSP; test both. |
| RB-07 | Manual TLS renewal | Medium | Open | Automate renewal or document a checked runbook. |
| RB-08 | Backups unencrypted at rest | High | Open | Confirm GPG/age encryption on every target; test a restore. |
| RB-09 | No external monitoring or dead-man switch | Medium | Open | Add an external ping and a host agent; blocked on host access. |

## Accepted recommendations

| ID | Item | Status | Next action |
|---|---|---|---|
| AR-01 | `Admin.vue` chunk splitting | Accepted | Split the largest route chunks; keep the bundle budget. |
| AR-02 | Shared-computer session controls (idle lock, autocomplete attrs) | Accepted | Add idle lock and form autocomplete hints. |
| AR-03 | TOTP replay guard | Accepted | Already implemented in `0068_mfa_replay_guard`? Verify and close. |
| AR-04 | Legacy-secret encryption migration | Accepted | Plan the re-encryption migration. |
| AR-05 | Passkeys on the Release 6 scope | Accepted | Add to the scope page. |
| AR-06 | TA/mentor course-scoping gap | Accepted | Scope course-staff queries; add a denial test. |
| AR-07 | Break-glass default approval | Accepted | Decide the default; test both paths. |
| AR-08 | YAML/DB drift reporting | Accepted | Add a drift report to CI. |
| AR-09 | First attack/detect pair (kerberoasting → Sysmon hunt) | Accepted | Author the pair with a shared scenario. |
| AR-10 | Cloud track growth | Accepted | Plan the next cloud labs. |
| AR-11 | Absorb review findings into `TENANT-ISOLATION-STATUS.md`, `SECURITY.md`, `BACKUP-RESTORE-TEST.md` | Open | Do it with the next security change. |
| AR-12 | Move the architecture backlog into `RELEASE-6-SCOPE.md` | Open | Fold the list into the scope page. |

## Licensing, legal, and repository

| ID | Item | Status | Next action |
|---|---|---|---|
| LG-01 | Relicence to AGPL-3.0-or-later + CC BY-SA 4.0 | **Blocked** | Written permission from Lewis Heuermann; draft in [UPSTREAM-LICENSE-PERMISSION-REQUEST.md](UPSTREAM-LICENSE-PERMISSION-REQUEST.md). |
| LG-02 | Flag injection before pilot announcements | **In progress** | 149 of 222 rotate; 73 static. See [FLAG-EXPOSURE.md](FLAG-EXPOSURE.md). |
| LG-03 | Entity, insurance, ToS/AUP, minors' privacy template | Open | See [LEGAL-READINESS.md](LEGAL-READINESS.md). |
| LG-04 | CLA grantee to the entity | Open | Incorporation first; then re-paper before external signatures. |
| LG-05 | CLA enforcement gate | Partial | PR checkbox added; CLA-assistant or a status check is the next step. |
| LG-06 | Release-chain CODEOWNERS | **Closed** | `#99`. |
| LG-07 | `GOVERNANCE.md` and `CITATION.cff` | **Closed** | `#99`. |
| LG-08 | Signing-key rotation and revocation procedure | **Closed** | `SECURITY.md#release-signing-key`. |

## Known bypass variables in the host updater

`deploy-updates.sh` has three explicit opt-outs. They are deliberate and logged,
but an operator must never set them on a production host:

| Variable | Effect | Rule |
|---|---|---|
| `ALLOW_UNSIGNED_MAIN=1` | Pulls `main` when no signed tag exists | Development only, with a written reason |
| `ALLOW_UNSIGNED_ZIP=1` | Accepts a ZIP without a signed tag | Controlled offline update only |
| `SUPPLY_CHAIN_STRICT=0` | Allows a missing lock to pass | Never in production |

Key rotation has a bootstrap caveat: the updater reads the public key from the
**current** tree, so a tag signed with a brand-new key cannot be verified until
the new public key is placed on the host. Rotate the key file first, then tag.
