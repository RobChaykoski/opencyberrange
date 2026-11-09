# ADR 0005: Lab network egress for v2.5.3

Status: **Accepted for v2.5.3**
Date: 2026-11-08
Owner: Platform / Security

## Context

Each learner lab runs on a per-user Docker bridge network. The host
`DOCKER-USER` rules block lab and RangeBox subnets from the management LAN and
block external interfaces from entering lab networks. The lab network still has
normal Docker outbound NAT, so a compromised lab container can attempt internet
egress.

This is not a host or control-plane boundary failure: lab containers do not
have the Docker socket, host networking, host credentials, or writable host
mounts. It is a data-exfiltration and external-command risk.

## Decision

For v2.5.3, keep the current bridge egress behaviour and rely on the existing
management-plane controls. Do not switch all lab networks to `internal=True`
without a per-lab egress review; several labs and RangeBox tool workflows depend
on package or tool access, and an unqualified change would break exercises.

Compensating controls:

- no Docker socket or host control-plane mount in any lab container;
- no lab uses `privileged`, host networking, host PID/IPC/UTS, or `SYS_ADMIN`;
- the host `DOCKER-USER` rules block lab-to-management and external-to-lab
  traffic;
- per-learner networks prevent cross-learner lab traffic;
- the isolation audit runs as a release gate and fails on any Critical finding.

## Follow-up

The next release should add an egress allowlist or a controlled proxy for labs
that need external access, then default the other labs to an internal network.
Until then, this ADR is the explicit risk acceptance, not a claim that egress is
restricted.

## Review

Review when the lab network policy changes, when a lab requires external
egress, or at the next release planning cycle.
