# OCR Sizing & Settings — Single Source of Truth

All memory in MiB (binary; the config's "GB"/"g"/"G" values are GiB, so
1 GiB = 1024 MiB). Defaults are verified against the 2.5.0 code and the
**2026-11-08 RangeBox capacity run**; the measured evidence is in
[RangeBox capacity and stress results](../RANGEBOX-CAPACITY.md).

## 1. Host sizing per edition

Proxmox vCPU = sockets x cores. Use 1 socket and put the count in cores
(multiple sockets only help NUMA on very large hosts, not here).

| Edition | Profile | Sockets | Cores | vCPU | RAM (MiB) | RAM (GiB) | Computed RangeBox limit |
|---|---|---|---|---|---|---|---|
| Lite | Minimum (boots, Docker labs, no RangeBox) | 1 | 2 | 2 | 4096 | 4 | 1 (effectively none) |
| Lite | Kick the tires (stack + a little headroom) | 1 | 2-4 | 2-4 | 8192 | 8 | 1 |
| Lite | Recommended (a class) | 1 | 4 | 4 | 16384 | 16 | 4 |
| Lite | Comfortable | 1 | 6-8 | 6-8 | 24576-32768 | 24-32 | 8-12 |
| Enterprise | Minimum (1 AD lab set, 1 user) | 1 | 4 | 4 | 16384 | 16 | 4 |
| Enterprise | Recommended (a class, AD/OT) | 1 | 8 | 8 | 32768 | 32 | 12 |
| Enterprise | Comfortable | 1 | 16 | 16 | 65536 | 64 | 24 |

The computed limit is the tighter of memory, CPU, and the 64-box ceiling. It is
an upper bound, not a class recommendation. The measured run below shows why:
VNC responsiveness and CPU contention fail before the memory limit.

Backend workers stop scaling past 4 cores (worker count = `(2 x cores) + 1`,
cap 9). Beyond that, cores and RAM go to labs, RangeBoxes, and (Enterprise)
Windows VMs. Enterprise nested virt also needs the VM CPU type set to `host`.

## 2. Per-component footprint

| Component | Count | RAM each (MiB) | CPU each | Cap source |
|---|---|---|---|---|
| PostgreSQL 15 | 1 | ~150-200 | light | none |
| Backend (uvicorn) | `(2 x vCPU) + 1`, cap 9 workers | ~150-250 / worker | shares cores | Dockerfile |
| nginx frontend | 1 | ~50 | light | none |
| RangeBox (per student) | 0..N | 2048 (hard cap) | 0.5 vCPU | `RANGEBOX_MEM_LIMIT` / `RANGEBOX_CPU_QUOTA` |
| Docker lab containers | per active lab | unbounded (no limit) | bursty | none set |
| Shared Windows/AD VM (Enterprise) | per definition | 4096 | 2 cores | shared VM `ram` / `cpu_cores` |

Measured idle RangeBox footprint on 2026-11-08 was **160-180 MiB per box** and
**1-2% CPU per box**, with short spikes while the desktop initialised. The 2 GiB
hard cap is therefore a ceiling for bursts and browser workloads, not the idle
working set. Memory is not the first constraint at idle; VNC responsiveness and
CPU contention arrive first.

## 3. Measured evidence (2026-11-08)

Test source: the built-in **Level 4 RangeBox VNC load test** (Admin > System >
Tester), run on the development host. Full method and reproduction steps are in
[RangeBox capacity and stress results](../RANGEBOX-CAPACITY.md).

| Item | Development host | Production-class host |
|---|---|---|
| vCPU | 12 | 8 |
| RAM | 62 GiB | 30 GiB |
| RangeBox memory limit | 2 GiB | 2 GiB |
| Platform reserve | 8 GiB | 8 GiB |
| Computed hard maximum | 27 | 11 |
| Recommended class limit | **20** | **8** |
| Short burst | 25 | 10 |

| Concurrent users | Spawned | Rejected | Host CPU | Host memory | Error rate | All latency thresholds |
|---:|---:|---:|---:|---:|---:|---|
| 5 | 5 | 0 | 6.6% | 5.4% | 0.0% | Pass |
| 10 | 10 | 0 | 11.9% | 6.7% | 0.0% | Pass |
| 20 | 20 | 0 | 12.2% | 9.1% | 0.0% | Pass |
| 25 | 25 | 0 | 15.8% | 10.2% | 0.0% | Pass |
| 30 | 27 | 3 | 14.6% | 10.6% | 0.0% | Fail: first VNC frame p95 4.56 s |

At 27 boxes the first VNC frame p95 crossed the 2 s threshold. The hard maximum
was enforced correctly: the three requests beyond 27 were rejected rather than
creating a 28th box. Use the recommended class limit, not the computed maximum,
for a real class.

## 4. Tunable env knobs (set in `.env` or compose)

| Knob | Default | Meaning |
|---|---|---|
| `RANGEBOX_MEM_LIMIT` | `2g` (2048 MiB) | Hard RAM cap per browser desktop |
| `RANGEBOX_CPU_QUOTA` | `50000` (0.5 vCPU) | CPU cap per browser desktop |
| `RANGEBOX_MEM_RESERVE_GB` | `8` (8192 MiB) | Free RAM kept before a new RangeBox is allowed |
| `RANGEBOX_CPU_RESERVE_CORES` | `2` | CPU cores kept free before a new RangeBox is allowed |
| `RANGEBOX_MIN_FREE_DISK_GB` | `10` | Free disk required before a new RangeBox is allowed |
| `RANGEBOX_MAX_CEILING` | `64` | Absolute max concurrent RangeBoxes |
| `MAX_CONCURRENT_RANGEBOXES` | (dynamic) | Pin a fixed cap; unset = computed from memory, CPU, and disk |
| `RANGEBOX_SPAWN_LOCK_FILE` | `/tmp/ocr-rangebox-spawn.lock` | Cross-worker spawn lock |
| uvicorn workers | `(2 x cores) + 1`, cap 9 | Backend processes (auto) |
| shared VM `ram` | `4G` (4096 MiB) | Per Windows/AD VM (per definition or DB row) |
| shared VM `cpu_cores` | `2` | Per Windows/AD VM |

To enforce the measured recommendation on each host:

```bash
# 12 vCPU / 62 GiB development host
MAX_CONCURRENT_RANGEBOXES=20

# 8 vCPU / 30 GiB production-class host
MAX_CONCURRENT_RANGEBOXES=8
```

The capacity check takes the minimum of memory, CPU, and disk headroom, so a
pinned cap cannot override a host that is already full. A container is counted
from the moment Docker creates it, so a desktop that is still starting is
included rather than briefly showing as zero.

## 5. Platform settings (DB-backed, admin-editable at runtime)

| Key | Default | Meaning |
|---|---|---|
| `default_session_hours` | 2 | Lab session length before expiry |
| `max_session_hours` | 8 | Ceiling for extensions |
| `container_cpu_limit` | 0.5 | Default CPU limit per lab container (Docker CPUs) |
| `container_memory_limit` | 512M | Default memory limit per lab container |
| `shared_vm_session_hours` | 2 | Shared-VM session length |
| `shared_vm_max_extensions` | 4 | Max shared-VM extensions |
| `shared_vm_max_uptime_hours` | 8 | Shared-VM hard uptime cap |
| `shared_vm_idle_timeout_minutes` | 30 | Idle shutdown for shared VMs |
| `jwt_expiration_hours` | 24 | JWT lifetime |
| `max_failed_attempts` | 5 | Failed logins before lockout |
| `lockout_duration_minutes` | 30 | Lockout duration |
| `require_approval` | true | Admin approval for new registrations |
| `enable_api_docs` | false | Serve Swagger UI / ReDoc |

## 6. Entitlement / caps

| Setting | Lite | Enterprise |
|---|---|---|
| max_privileged_accounts | 1 | unlimited (null) |
| max_active_courses | 5 | unlimited (null) |
| students | unlimited | unlimited |

Set by `backend/data/entitlement.json`; no file = Lite defaults.

## 7. Ports & networks

| Item | Value | Env |
|---|---|---|
| HTTP | 80 | `OCR_HTTP_PORT` |
| HTTPS | 443 | `OCR_HTTPS_PORT` |
| Backend API | 127.0.0.1:8000 (localhost only) | `OCR_BACKEND_PORT` |
| WireGuard | 51820/udp | `WG_SERVER_ENDPOINT` |
| Lab subnets | 10.100.0.0/14 | `WG_NETWORK_BASE` (10.100) |
| VPN client base | 10.0.0.0 | `WG_CLIENT_BASE` |

Documentation examples use `192.168.120.0/24` as a placeholder management
subnet. Replace it with your own; never copy the example addresses into a live
deployment.

## 8. Virtualization requirement

| Edition | KVM | Host type |
|---|---|---|
| Lite | Not needed (Docker-only) | Plain Linux VM (or, with plumbing, LXC) |
| Enterprise | `/dev/kvm` required for shared VMs; VM CPU type = host (nested virt) | Linux VM, NOT LXC |

## 9. Validation evidence

Two artefacts back the sizing and settings in this document:

1. **RangeBox capacity test** — the Level 4 VNC load test. The run records
   concurrent users, spawns, rejections, host CPU, host memory, error rate, and
   latency thresholds. The latest run is in
   [RangeBox capacity and stress results](../RANGEBOX-CAPACITY.md). Re-run it on
   any new host class and update the recommended limit from the first failing
   step.
2. **Deployment smoke run** — `scripts/ui-smoke.mjs` writes
   `ui-smoke-artifacts/evidence.json` with the deployment URL, expected and
   actual version, role, every check, failures, screenshots, and the run
   timestamps. The CI workflow uploads the directory as `ui-smoke-evidence`.
   This is the release evidence that the sized host is serving the expected
   build, not a capacity measurement.

Keep both artefacts with the release record. A green smoke run proves the
deployment is reachable and on the expected version; it does not prove the host
is correctly sized. The capacity run is the sizing evidence.

## 10. Worked examples

- Lite, 4 vCPU / 16384 MiB: core stack ~2 GiB, computed limit 4 RangeBoxes.
  Use 4 concurrent boxes, not 5; the CPU reserve and 0.5 vCPU quota bind first.
- Lite, 8 vCPU / 32768 MiB: computed limit 12; the measured pattern suggests a
  class limit of 8-10 for interactive use, with 12 as a short burst.
- Enterprise, one student on an AD lab: core ~2 GiB + DC 4096 MiB + workstation
  4096 MiB + their RangeBox wants 8192 MiB free = ~18 GiB, ~5-6 vCPU. Shared VMs
  are shared class-wide (one DC); per-student workstations and RangeBoxes stack.
