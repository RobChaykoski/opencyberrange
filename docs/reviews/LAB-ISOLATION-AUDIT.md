# Lab container isolation audit

Status: **v2.5.3 release evidence**
Scope: all 149 lab definitions, lab compose files, Dockerfiles, and the running
development deployment
Gate script: `scripts/audit-lab-isolation.py`
Related: [Lab release proof](LAB-RELEASE-PROOF.md),
[Lab egress decision](../decisions/0005-lab-network-egress.md),
[RangeBox capacity](../RANGEBOX-CAPACITY.md),
[Security evidence](../V2-SECURITY-EVIDENCE.md)

## The boundary being tested

A learner controls a lab container and the browser-based RangeBox. The
container must not be able to reach:

- the Docker socket or Docker API;
- host-mounted credentials or writable host filesystem paths;
- management APIs and the platform backend;
- the platform database or Redis;
- another learner's lab network;
- the WireGuard administration plane;
- cloud metadata or host management endpoints.

Isolation is not proven by the existence of a container. It is proven by the
runtime configuration, the network rules, and a negative test.

## Method

1. **Static scan.** `scripts/audit-lab-isolation.py` reads every
   `platform/labs/**/docker-compose.yml`, `lab.yaml`, and `Dockerfile*`. It
   checks privileged mode, Docker socket mounts, host bind mounts, host
   namespaces, added capabilities, devices, unconfined security options, root
   users, management/metadata endpoints, and sensitive volume names.
2. **Runtime inspect.** `docker inspect` on the development host for every
   running container: privileged flag, network mode, capabilities, and binds.
3. **Network-rule audit.** The backend's
   `DockerManager.audit_lab_network_isolation()` checks the `DOCKER-USER`
   rules that block lab and RangeBox subnets from the host LAN and block
   external interfaces from entering Docker lab networks.
4. **Release gate.** The audit script exits non-zero when any **Critical**
   finding is present. Critical means a student-controlled container can reach
   the host or control plane.

## Static result

**149 lab compose files scanned. 0 Critical findings.**

| Check | Result |
|---|---|
| `privileged: true` | 0 |
| `/var/run/docker.sock` mount | 0 |
| Host network / PID / IPC / UTS namespace | 0 |
| `SYS_ADMIN`, `SYS_MODULE`, `SYS_PTRACE`, `DAC_READ_SEARCH` | 0 |
| Device passthrough | 0 |
| Unconfined security options | 0 |
| Cloud metadata or management endpoint in lab target | 0 |
| Writable host bind mount in a lab service | 0 |
| Sensitive volume name containing flags or credentials | 0 |

### High findings requiring justification

These capabilities are not host-control capabilities, but they are powerful and
must stay lab-scoped:

| Lab | Service | Capability | Why it is present |
|---|---|---|---|
| `linux-5-4-suricata-live-detection` | analyst | `NET_ADMIN`, `NET_RAW`, `SYS_NICE` | IDS sensor and traffic capture |
| `linux-5-6-brute-force-detection` | sensor | `NET_ADMIN`, `NET_RAW`, `SYS_NICE` | Detection sensor |
| `network-12-1-firewall-fundamentals` | firewall | `NET_ADMIN`, `NET_RAW` | Inline firewall lab |
| `network-12-2-firewall-policy-hardening` | firewall | `NET_ADMIN`, `NET_RAW` | Inline firewall lab |

The release gate accepts these because the containers are on the per-learner
lab network, not the host network, and the host `DOCKER-USER` rules block lab
traffic to the management LAN. Any new `cap_add` needs the same justification
in the lab review.

### Warnings

Most lab services do not set `user:`. They run as root inside the container
unless the image drops privileges. This is common for service labs that bind
low ports or manage their own users, but it is a warning, not a pass. Prefer a
non-root user where the service does not need root, and add
`security_opt: no-new-privileges:true` where it does not break the lab.

## Runtime result (development host)

- No lab or RangeBox containers were running during the audit, so there was no
  live student container to inspect. The static configurations are the
  evidence for the release gate.
- Platform containers inspected:
  - `ocr-frontend`: not privileged, no added capabilities, read-only wiki and
    certificate mounts.
  - `ocr-backend`: not privileged, no added capabilities, and it deliberately
    holds `/var/run/docker.sock` because it is the trusted orchestrator. The
    backend is **not** a learner-controlled container.
  - `ocr-db`, `ocr-redis`, `ocr-mailpit`: not privileged, no added
    capabilities.
- The development backend also has a writable bind mount of the repository
  backend directory (`/home/ocrv2/opencyberrange/backend:/app:rw`). That is a
  development convenience and must not be copied to production. It is inside
  the trusted backend container, not a lab container.
- `DockerManager.audit_lab_network_isolation()` reported **all checks OK**:
  - `10.100.0.0/14`, `10.104.0.0/13`, `10.112.0.0/12`, `10.128.0.0/9`, and
    `10.50.0.0/16` blocked from the host management LAN (`172.16.16.0/24`);
  - inbound DROP rules present for the external interface (`ens18`).

## Residual risk: egress

The per-learner lab network is a normal Docker bridge. The host firewall blocks
lab-to-management-LAN traffic, but it does not default-deny outbound internet
egress from lab containers. A compromised lab container could therefore attempt
outbound connections to the internet.

This is **not** a host or control-plane Critical finding under the stated gate.
For v2.5.3 the risk is **explicitly accepted** in
[ADR 0005](../decisions/0005-lab-network-egress.md), with the existing
management-plane controls as compensation. Per-lab allowlisting and default
internal networks are deferred to the next release:

- Prefer `internal=True` on the per-lab Docker network when the lab does not
  need internet access.
- If a lab needs egress, give it an explicit allowlist or a controlled proxy,
  not unrestricted NAT.
- Keep the RangeBox on its own proxy network for tool installation, separate
  from the lab target network.
- Add an egress test that attempts a connection from a student container to a
  known external address and to the host management address.

## Release gate

A release may ship only when:

- [ ] `python scripts/audit-lab-isolation.py` exits 0 (no Critical findings).
- [ ] Every `cap_add` has a written justification in the lab review.
- [ ] No lab compose file mounts the Docker socket, a host credential path, or
      a writable host directory.
- [ ] No lab uses host networking, host PID/IPC/UTS, `privileged`, or
      `SYS_ADMIN`.
- [ ] The runtime `DOCKER-USER` audit reports all rules present.
- [ ] The egress decision is recorded: default-deny, allowlist, or accepted
      risk with a reason. **v2.5.3: accepted risk, ADR 0005.**
- [ ] A negative test from a student container to the host management address,
      the backend, the database, and another learner's subnet is blocked.

## Reproduce

```bash
python scripts/audit-lab-isolation.py
```

On the host:

```bash
docker ps -q | xargs -r docker inspect \
  --format '{{.Name}} privileged={{.HostConfig.Privileged}} network={{.HostConfig.NetworkMode}} caps={{.HostConfig.CapAdd}} binds={{.HostConfig.Binds}}'
```

Inside the backend container:

```bash
docker exec -e PYTHONPATH=/app ocr-backend python -c \
  "from app.services.docker_manager import DockerManager; print(DockerManager().audit_lab_network_isolation())"
```
