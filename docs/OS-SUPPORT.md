# Host OS Support and Ubuntu 24.04 Decision

Status: **1.1 supports Ubuntu 22.04 LTS and Ubuntu 24.04 LTS. 2.4.0 targets
Ubuntu 24.04 LTS. A 24.04 host is deployed and healthy, and KVM is available;
network/VPN, lab, and recovery gates remain before 2.4.0 is marked fully
supported.**

## Decision

The host OS follows the release line:

| Release line | Host OS | State |
|---|---|---|
| `1.1.x` maintenance | **Ubuntu 22.04 / 24.04 LTS** | Supported on both LTS baselines. 22.04 remains the documented baseline; 24.04 is validated in production. |
| `2.4.0` release | **Ubuntu 24.04 LTS target** | Migration in progress. 22.04 remains the supported source for upgrades during the 2.4.0 validation window. |

For new 2.4.0 installs, use:

| Host OS | State | Guidance |
|---|---|---|
| Ubuntu 24.04 LTS (Noble) | **Validation in progress** | Host, platform, and KVM readiness pass; network/VPN and lab-recovery gates remain |
| Ubuntu 22.04 LTS (Jammy) | **Compatibility path** | Allowed for existing 1.1.3-to-2.4.0 upgrades and the 2.4.0 validation window, not the long-term 2.4.0 target |
| Debian 12/13 | Best effort | Not part of the tested server matrix |
| Other Debian-based distributions | Unsupported | Package names, firewall backends, and systemd behaviour may differ |

Ubuntu 22.04 standard support ends in June 2027; Ubuntu 24.04 standard support
runs to June 2029. Keeping 1.1 on 22.04 avoids re-validating the maintenance
line. Moving 2.4.0 to 24.04 gives a new release a host OS that remains supported
for the life of the 2.4.0 line.

The full migration plan is in
[V2 Ubuntu 24.04 Migration Plan](V2-UBUNTU-24.04-MIGRATION.md).

This decision is about the **host OS only**. It does not change:

- the platform containers, which use `python:3.11-slim`, `node:22-alpine`,
  `nginx:alpine`, `postgres:15-alpine`, and `redis:7-alpine`;
- the exercise containers under `platform/labs/`, which stay on their pinned
  bases for reproducible labs;
- the Kali-based RangeBox, which follows `kalilinux/kali-rolling`;
- the UbuntuBox image, which stays on `ubuntu:22.04` for the 2.4.0 release.

## Why 24.04 for new installs

- Standard security support through June 2029 instead of June 2027.
- Current kernel, Docker, WireGuard, and nftables userspace.
- New deployments avoid an in-place host upgrade shortly after installation.
- The setup script already targets "Ubuntu 22.04 or newer" and uses generic
  apt package names, so most of the installation path is shared.
- CI builds already use GitHub's `ubuntu-latest` runner, which is the 24.04
  image. What remains untested is the host installer, firewall persistence, and
  the interactive lab runtime described in the validation gate.

## Why keep 1.1 on 22.04

- It is the validated baseline for the supported maintenance line.
- Bug fixes stay on the release they were tested against; an OS rebase would
  turn routine maintenance into a platform migration.
- Existing 1.x classrooms should not be forced into a host upgrade to keep
  receiving fixes.
- Lab images and UbuntuBox remain on 22.04, so existing exercise behaviour does
  not change.

The multi-host HA design is an Enterprise preview workstream, separate from the
host OS migration. See [the Enterprise preview HA lab pool plan](V3-HA-LAB-POOL.md).

## Ubuntu 24.04 validation gate

Before calling 24.04 fully supported, run this checklist on a clean 24.04 host:

1. **Installer** — `setup-range-server.sh --install` completes without manual
   package fixes.
2. **Docker and Compose** — host Docker Engine and Compose v2 start the four
   core containers; the backend can create and remove lab networks.
3. **WireGuard** — server keys, peer creation, client config download, and a
   working tunnel from a client.
4. **Firewall persistence** — `DOCKER-USER`, `FORWARD`, `raw PREROUTING`, and
   NAT rules are present before and after a reboot; the `ocr-vpn-firewall`
   service re-applies them after Docker starts.
5. **nftables backend** — confirm the iptables commands in the setup script
   resolve to the nft backend consistently and that
   `netfilter-persistent save` restores the expected rules.
6. **Lab spawn and isolation** — start at least one Docker-only lab, one
   multi-container lab, and one RangeBox session; confirm a learner cannot reach
   the host management LAN or another session's `/24`.
7. **AppArmor and user namespaces** — verify RangeBox browsers and any lab that
   uses sandboxing still start with Ubuntu's unprivileged-userns restriction
   enabled. Do not disable the restriction globally unless a specific lab
   requires it and the risk is documented.
8. **VPN and DNS** — confirm container DNS and lab name resolution behave with
   `systemd-resolved` on 24.04.
9. **Backup and restore** — collect a snapshot, restore it, and re-apply the
   erasure suppression ledger.
10. **Upgrade path** - upgrade an existing 22.04 deployment to 2.4.0, then perform
    a separate 22.04-to-24.04 host upgrade drill and repeat the checks above.

Record the result in the release notes before changing the support table. Until
then, treat 24.04 as the recommended target, not a fully certified host.

## Known 24.04 risks to watch

- **iptables persistence with Docker.** Docker manages its own firewall chains.
  Restoring stale iptables rules can restore old bridge references. The platform
  already re-applies its rules through a systemd unit; that path is the primary
  protection and needs a reboot test on 24.04.
- **nftables.** Ubuntu 24.04 presents iptables through the nft backend. Commands
  used by the installer are expected to work, but rule order and persistence must
  be checked rather than assumed.
- **AppArmor unprivileged user namespaces.** Ubuntu 24.04 restricts unprivileged
  user namespaces by default. Current labs do not appear to depend on them, but
  browser sandboxes and future container tools may. Test before relaxing the
  sysctl.
- **systemd-resolved.** Docker normally handles the loopback resolver, but lab
  DNS is central to several exercises and should be part of the smoke test.

## UbuntuBox is a separate decision

Moving the UbuntuBox desktop from `ubuntu:22.04` to `ubuntu:24.04` is not part
of the host OS migration. It changes the student-visible desktop, Python
version, Firefox packaging, and the available tool versions. Do that as its own
wave with per-lab and per-workbook validation, after the host migration is
stable.

The same rule applies to the ~148 lab images on `ubuntu:22.04`: keep the pinned
bases until each exercise has a solve test on the new base.
