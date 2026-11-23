# Publication metadata policy

Status: **enforced by `scripts/audit-publication.py` and the Quality workflow.**

This repository is public. Treat every committed file as publishable. The
following are not publishable:

- real public or private IPv4 addresses;
- internal hostnames, SSH aliases, deployment usernames, and administrator
  email addresses;
- private subnets, port maps, backup paths, and topology diagrams that identify
  the live deployment;
- lab flags and expected answer keys outside the lab definition/runtime;
- credentials, API tokens, private keys, and connection strings.

## Placeholders

Public documentation uses placeholders instead of live values:

| Placeholder | Meaning |
|---|---|
| `<auth-host>` | Public identity-provider hostname |
| `<platform-host>` | Public OpenCyberRange hostname |
| `<moodle-host>` | Public Moodle hostname |
| `<public-ip>` | Public edge address |
| `<prod-host-ip>` | Production host private address |
| `<dev-host-ip>` | Development host private address |
| `<npm-host-ip>` | NPM private address |
| `<private-subnet>` | Deployment subnet |
| `<prod-host>` / `<dev-host>` | SSH aliases |
| `<deploy-user>` | Deployment account |
| `<flag>` | A lab answer key; never printed in documentation |

Examples use the RFC 5737 documentation ranges (`192.0.2.0/24`,
`198.51.100.0/24`, `203.0.113.0/24`) and `example.com` names. Real values live
in the private deployment inventory or the operations vault, never in git.

Configuration files use safe defaults (`127.0.0.1`, `*.example.com`) so a
missing `.env` fails closed instead of exposing a live host.

## Flags are answer keys

A flag is allowed only in:

- `platform/labs/**/lab.yaml` (the definition);
- `platform/labs/**/docker-compose.yml` and container code (the runtime);
- intentional lab assets such as `_shared/` evidence or the OSINT
  external-target registry.

A flag is **not** allowed in:

- workbooks, lab READMEs, or the manual;
- `platform/tester/manifests` (the manifest stores `{flag}`, resolved by the
  harness from `lab.yaml`);
- backend tests (use a synthetic test flag);
- CTF export packs (templates use `<flag_1>`/`<flag_2>` and read real values
  from the environment);
- release notes, changelogs, or documentation examples.

The platform can issue per-session seeded flags for cohorts where the static
lab flag must not be reusable. See `lab_sessions.seeded_flag_hash`.

## Audit and CI

```bash
python scripts/audit-publication.py --summary
python scripts/audit-publication.py --json
python scripts/audit-publication.py --index .local/publication-index.json
python scripts/audit-publication.py --report /tmp/publication-report.md
```

The index is local-only and contains real flag values for the operator. It is
ignored by git. The JSON and text output redact values.

The Quality workflow runs the audit on every push and pull request. A finding
fails the build.

## If a value is already published

Removing it from the working tree is not enough. Git history and GitHub caches
may retain it.

1. **Rotate first.** Revoke the token, rotate the credential, or change the
   exposed endpoint. Deleting the file does not revoke a secret.
2. **Assess the exposure.** Decide whether the address, hostname, or payload
   changes the attack surface. A public address is already discoverable; the
   association with a service, version, and credential is the risk.
3. **Rewrite history when required.** Use `git filter-repo` with a replacements
   file, coordinate a force-push with every clone, and ask GitHub Support to
   purge cached views and forks. This is destructive; get explicit approval.
4. **Re-run the audit.** Confirm zero findings on the rewritten tree.
5. **Record the decision.** Link the incident, the rotated credential, the
   history rewrite, and the review date in OpenGRC.

At the time this policy was added, the audit found the public IP in 5 commits,
the production private address in 37 commits, and a sample lab flag in 1 commit.
Treat those values as disclosed until the history is rewritten and the affected
credentials or flags are rotated.

## DLP mapping

The audit uses the same vocabulary as the production DLP scenario:

- OpenDiscoveryEngine: `private_ipv4`, `public_ipv4`, `internal_hostname`,
  `cloud_metadata_endpoint`, `assessment_flag`, `api_key_assignment`;
- OpenGRC: `PUB-001` through `PUB-004`;
- OpenCyberRange context service: `POST /scan`, `POST /scan-and-decide`.

A publication decision records the detector class, the redacted value, the
policy version, and the reviewer. It never stores the raw match.

## Review checklist

- [ ] No real address, hostname, username, or admin email in the diff.
- [ ] No lab flag outside the lab definition/runtime.
- [ ] No secret, token, or private key.
- [ ] Placeholders and `*.example.com` names are used.
- [ ] Configuration defaults bind to loopback or a documentation address.
- [ ] `python scripts/audit-publication.py --summary` returns zero findings.
- [ ] If a value was already public, rotation and history review are recorded.
