# RangeBox capacity and stress results

Last run: **2026-11-08** on the development host (`172.16.16.44`), using the
built-in **Level 4 RangeBox VNC load test** from the Admin > System > Tester
panel.

## Test host

| Item | Value |
|---|---|
| vCPU | 12 |
| RAM | 62 GiB |
| RangeBox memory limit | 2 GiB per container |
| Platform reserve | 8 GiB |
| Computed hard maximum | 27 RangeBoxes |
| Container image | `opencyberrange/rangebox:lite` (Kali) |

## Results

| Concurrent users | Spawned | Rejected | Host CPU | Host memory | Error rate | All latency thresholds |
|---:|---:|---:|---:|---:|---:|---|
| 5 | 5 | 0 | 6.6% | 5.4% | 0.0% | Pass |
| 10 | 10 | 0 | 11.9% | 6.7% | 0.0% | Pass |
| 20 | 20 | 0 | 12.2% | 9.1% | 0.0% | Pass |
| 25 | 25 | 0 | 15.8% | 10.2% | 0.0% | Pass |
| 30 | 27 | 3 | 14.6% | 10.6% | 0.0% | Fail: first VNC frame p95 4.56 s |

At 27 boxes the VNC first-frame p95 crossed the test's 2 s threshold. The hard
maximum was then enforced correctly: the three requests beyond 27 were rejected
rather than creating a 28th box.

Idle containers used about `160–180 MiB` each and roughly `1–2%` CPU per box,
with short spikes while the desktop initialised. Memory is not the first
constraint at idle; VNC responsiveness and CPU contention arrive first.

## Recommended limits

| Host | Computed hard maximum | Recommended class limit | Short burst |
|---|---:|---:|---:|
| 12 vCPU / 62 GiB (development) | 27 | **20** | 25 |
| 8 vCPU / 30 GiB (production) | 11 | **8** | 10 |

The computed maximum is based on RAM only. The recommended class limit leaves
headroom for the backend, database, SIEM, browser workloads, and real keyboard
and mouse interaction rather than idle desktops.

To enforce a fixed operational limit, set the environment variable:

```bash
MAX_CONCURRENT_RANGEBOXES=20
```

The capacity check now uses a cross-worker lock, so concurrent launches cannot
overshoot the configured maximum. It also takes the minimum of memory, CPU, and
disk headroom: `RANGEBOX_CPU_RESERVE_CORES` (default `2`) and
`RANGEBOX_MIN_FREE_DISK_GB` (default `10`) prevent a host from being filled by
desktops alone. Use the RangeBox tab's **Deployed** count to confirm the live
number. A container is counted from the moment Docker creates it, so a desktop
that is still starting is already included rather than briefly showing as zero.

## Reproducing

1. Open **Admin > System > Tester**.
2. Choose **Level 4 — RangeBox VNC load test**.
3. Start with 5 users, then increase in steps of 5.
4. Watch host CPU, host memory, first-frame latency, and rejected launches.
5. Stop at the first run where a latency threshold fails; that is the practical
   ceiling for that host, not the memory-derived maximum.
