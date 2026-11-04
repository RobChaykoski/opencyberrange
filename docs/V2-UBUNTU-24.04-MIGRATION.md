# V2 Ubuntu 24.04 Migration Plan

Status: **In progress — host/platform deployed, network and lab gates pending**

Execution checklist: [`V2-24.04-BUILD-OUT.md`](V2-24.04-BUILD-OUT.md)

## Goal

Move the OpenCyberRange **2.0** line to Ubuntu 24.04 LTS as its supported host
OS, while keeping the **1.1 maintenance line on Ubuntu 22.04 LTS**.

The split is deliberate:

- 1.1 bug fixes and security patches stay on the 22.04 baseline. Do not
  backport 24.04-specific host changes into 1.1.
- Bug fixes that also affect 2.0 continue to land on 1.1 first and are merged
  forward into `main`.
- 2.0 targets 24.04 for new installs. 22.04 remains a supported upgrade source
  until the 2.0 validation window closes.

## Non-goals

This migration does **not** change:

- the platform container bases (`python:3.11-slim`, `node:22-alpine`,
  `nginx:alpine`, `postgres:15-alpine`, `redis:7-alpine`);
- the ~148 exercise images on `ubuntu:22.04`;
- the UbuntuBox desktop image, which stays on `ubuntu:22.04` for 2.0.0;
- the Kali-based RangeBox, which follows `kali-rolling`;
- the 1.1 release branch or its deployment documentation.

Changing any of those is a separate workstream with its own solve tests.

## Release-line and branch model

| Line | Branch / tag | Host OS | Change policy |
|---|---|---|---|
| 1.1 | `release/1.1` or `v1.1.x` tags | Ubuntu 22.04 | Bug and security fixes only |
| 2.0 | `main` and `v2.0.x` tags | Ubuntu 24.04 target | Features plus forward-merged 1.1 fixes |

Rules:

1. A host-level fix for 22.04 may land directly on the 1.1 line.
2. A host-level fix that applies to both lines lands on 1.1 first, then merges
   into `main`.
3. A 24.04-only change never lands on the 1.1 line.
4. CI keeps a 22.04 job for 1.1 and a 24.04 job for 2.0 once the validation
   phase starts.

## Migration phases

### Phase 0 — Policy and documentation

Status: **done**

- Publish the release-line split in `docs/OS-SUPPORT.md`.
- Record the target in `versions.yaml` under `runtime.host_os`.
- Update the README, prerequisites, Docker manual, and Lite quickstart.
- Make the installer print the detected OS and warn outside the 22.04/24.04
  matrix.

Exit criteria: documentation names 22.04 for 1.1 and 24.04 for 2.0 without
ambiguity.

### Phase 1 — Clean-host installer validation

Run `scripts/setup-range-server.sh --install` on a new 24.04 host.

Check:

- apt repositories and package names resolve;
- Docker Engine and Compose v2 install;
- Python 3.12 host venv builds the Peer Manager Flask app;
- WireGuard packages and kernel module are present;
- the platform directory, `.env`, and systemd units are created correctly.

Exit criteria: installation completes with no manual package workarounds.

### Phase 2 — Firewall and network validation

This is the highest-risk phase because 24.04 uses the nftables backend behind
the `iptables` command.

Validate:

- `DOCKER-USER` rules block external interfaces from lab subnets;
- `FORWARD`, `raw PREROUTING`, and NAT rules match the 22.04 baseline;
- `netfilter-persistent save` and the custom `ocr-vpn-firewall` service both
  restore rules after reboot;
- Docker recreates its own chains without breaking the platform rules;
- WireGuard peers can reach lab subnets and cannot reach the management LAN or
  another session's `/24`;
- `systemd-resolved` does not break container DNS or lab name resolution.

Decision point: if `iptables-persistent` proves unreliable with Docker on
24.04, replace it for platform rules with an explicit systemd unit or native
nftables ruleset. Do not silently leave firewall persistence untested.

### Phase 3 — Platform and lab smoke tests

Validate on 24.04:

- frontend, backend, PostgreSQL, Redis, and Wiki builder;
- login, MFA, VPN config download, and certificate verification;
- a single-container lab, a multi-container lab, a network-tap lab, and a
  shared-container lab;
- RangeBox, UbuntuBox, and REMnuxBox launch paths;
- KVM/VM labs on a KVM-capable host;
- backup collection, restore, and erasure-ledger re-application.

Exit criteria: the same representative lab matrix that passes on 22.04 passes
on 24.04.

### Phase 4 — Upgrade-path validation

Test both paths:

1. Existing 22.04 1.1 deployment upgraded to 2.0 on 22.04.
2. The same deployment moved to 24.04 using a documented host-upgrade or
   rebuild procedure.

A host OS upgrade is not a platform upgrade. Treat them as separate changes,
take a full snapshot first, and record the rollback path (restore the 22.04
host or rebuild it).

### Phase 5 — Make 24.04 the default

When Phases 1–4 pass:

- change the installer preflight from "recommended" to "supported";
- make 24.04 the default in the README and prerequisites;
- keep 22.04 documented as a compatibility source for 2.0 upgrades;
- add a 24.04 CI job for installer/config smoke tests.

### Phase 6 — Retire 22.04 for 2.0

At a 2.0 minor release after the compatibility window:

- stop testing 22.04 for 2.0;
- keep 22.04 in the 1.1 maintenance documentation until that line retires;
- update `versions.yaml` so 24.04 is the only supported 2.0 host.

## Test matrix

| Area | 22.04 (1.1) | 24.04 (2.0 target) |
|---|---|---|
| Installer | Required | Required |
| Docker/Compose | Required | Required |
| WireGuard | Required | Required |
| Firewall before/after reboot | Required | Required |
| Lab spawn and isolation | Required | Required |
| RangeBox / UbuntuBox / REMnuxBox | Required | Required |
| KVM lab | Required where hardware exists | Required where hardware exists |
| Backup and restore | Required | Required |
| 1.1 → 2.0 upgrade | Required | Required |
| Host upgrade 22.04 → 24.04 | n/a | Required drill |

## Rollback

- Platform rollback: restore the pre-upgrade database snapshot and previous
  image tags.
- Host rollback: rebuild on Ubuntu 22.04 and restore the snapshot. Ubuntu does
  not support an in-place downgrade.
- Keep the 1.1 line deployable on 22.04 throughout the migration.

## Risks

| Risk | Mitigation |
|---|---|
| Docker plus `iptables-persistent` restores stale rules | Reboot test; prefer a dedicated platform systemd rule unit if needed |
| nftables backend changes rule ordering | Compare full `iptables-save` output on both hosts |
| AppArmor unprivileged-userns restriction breaks a tool | Test browsers and sandboxed tooling; do not disable globally |
| Python 3.12 host differences in the Peer Manager | Pin Flask in the venv and run the health check |
| 22.04 and 24.04 behaviour drift during the window | Keep separate CI jobs and record the tested matrix |

## Definition of done

- 24.04 is the documented default for new 2.0 installs.
- 1.1 documentation still says 22.04 and the branch remains on 22.04.
- Full installer, firewall, lab, and upgrade drills pass on 24.04.
- `versions.yaml`, README, prerequisites, and deployment manuals agree.
