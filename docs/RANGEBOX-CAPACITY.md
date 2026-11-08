# RangeBox capacity and stress results

Last run: **2026-11-08** on the development host, using the built-in
**Level 4 RangeBox VNC load test** from the Admin > System > Tester panel.

This run is the sizing evidence cited by
[Sizing and settings](architecture/SIZING-AND-SETTINGS.md). Keep the run output
with the release record; the deployment smoke test is separate evidence and does
not measure capacity.

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

## Operational cap

The platform does not run at the computed maximum by default. The live cap is
**`rangebox_capacity_percent`** of the capacity ceiling, defaulting to **75%**.
The ceiling is the measured Level 4 stress-test maximum when one has been
recorded; until then it is the computed maximum. The remaining quarter is
headroom for the backend, database, SIEM, and interactive VNC. On the 27-box
development host that gives a live cap of 20; on the 11-box production-class
host it gives 8.

Change the percentage in **Admin → Settings → Exercises → RangeBox capacity**.
The card shows the computed maximum, the measured ceiling, the saved live cap,
and the running count. Use **Run ceiling test** to start a Level 4 test at the
computed maximum. A run that attempts at least 90% of the computed maximum is
recorded as the measured ceiling. The test spawns real RangeBoxes, so run it on
an idle host and follow progress in **System → Stress Tester**.

An explicit `MAX_CONCURRENT_RANGEBOXES` environment variable still pins an exact
cap and bypasses the percentage. Clear the variable to return control to the
setting.

## Recommended limits

| Host | Computed hard maximum | Live cap at 75% | Short burst | Enforce with |
|---|---:|---:|---:|---|
| 12 vCPU / 62 GiB (development) | 27 | **20** | 25 | `rangebox_capacity_percent=75` |
| 8 vCPU / 30 GiB (production) | 11 | **8** | 10 | `rangebox_capacity_percent=75` |

The computed maximum is the tighter of memory, CPU, and disk headroom. The live
cap leaves room for the backend, database, SIEM, browser workloads, and real
keyboard and mouse interaction rather than idle desktops.

To pin a fixed operational limit instead, set the environment variable for the
host class:

```bash
# 12 vCPU / 62 GiB development host
MAX_CONCURRENT_RANGEBOXES=20

# 8 vCPU / 30 GiB production-class host
MAX_CONCURRENT_RANGEBOXES=8
```

| Setting | Value | Evidence |
|---|---|---|
| `RANGEBOX_MEM_LIMIT` | 2 GiB | Hard cap per desktop; idle use measured at 160-180 MiB |
| `RANGEBOX_CPU_QUOTA` | 50000 (0.5 vCPU) | Keeps a burst desktop from starving the host |
| `RANGEBOX_MEM_RESERVE_GB` | 8 | Leaves room for the platform and SIEM |
| `RANGEBOX_CPU_RESERVE_CORES` | 2 | Prevents CPU oversubscription before VNC latency fails |
| `RANGEBOX_MIN_FREE_DISK_GB` | 10 | Keeps disk headroom for images and logs |

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
