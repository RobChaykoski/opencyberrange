# Capacity, admission, and placement

The goal is not to fill every node. The goal is to keep every admitted session
healthy and to reject work before it becomes a partial failure.

## Measure, do not guess

Collect per-lab measurements from real sessions:

- peak RSS and average RSS;
- CPU cores used at start, steady state, and flag submission;
- disk for images, writable layers, and captures;
- session duration and burst concurrency;
- container count and shared-container behavior;
- whether KVM is required;
- image pull time and image size.

Use a high percentile (p95 or max), not the average. A lab that uses 200 MB on
average but 3 GB at start needs the 3 GB reservation.

## Hard reservations

Each admitted session reserves:

```text
memory_mb = measured_peak_mb + safety_margin
cpu_millicores = measured_peak_millicores + safety_margin
disk_gb = image_gb + writable_gb + capture_gb
pids = measured_limit + headroom
```

Suggested starting safety margins:

| Resource | Margin |
|---|---|
| Memory | 15–25% or 256 MB, whichever is larger |
| CPU | 10–20% |
| Disk | 10 GB per node reserve, separate from session reservations |
| PIDs | 20% |

Never rely on Docker's default memory behavior. A container without a limit can
take the node down.

## Node admission

A node admits a session only if all are true:

1. `status` is `online` and not `draining`.
2. `free_memory - reserve >= session_memory`.
3. `free_cpu - reserve >= session_cpu`.
4. `free_disk >= session_disk + disk_reserve`.
5. The required image is present or can be pulled within the spawn budget.
6. KVM/shared-VM requirements are satisfied.
7. `active_sessions < max_sessions`.
8. The node is in the allowed region/classroom.

If any check fails, return a structured capacity error. Do not start a
half-provisioned session.

## Headroom

Keep headroom for:

- the largest lab's start burst;
- a node that goes offline and shifts load;
- image pulls and Docker housekeeping;
- the operator's emergency session.

A practical target is **20–30% free memory and CPU per node** at advertised
capacity. If you advertise 100 sessions, prove 100 + a burst.

## Placement order

1. **Hard filters:** health, drain, region, KVM, image, capacity.
2. **Affinity:** shared containers, dependent services, and multi-container labs
   must land together.
3. **Anti-affinity/spread:** avoid placing one course or cohort on one node when
   alternatives exist.
4. **Least allocated:** score by reserved memory and CPU, not raw usage.
5. **Stable tie-break:** node ID or hash, so placement is predictable.

Example score:

```text
score = 0.55 * memory_fill + 0.25 * cpu_fill + 0.10 * session_fill
      + 0.10 * image_pull_penalty
```

Lower is better. A node at 40% memory and 80% CPU should not beat a node at 55%
memory and 55% CPU if CPU is the actual bottleneck. Use the resource with the
least headroom as a hard constraint first.

## Per-cohort caps

Add optional placement limits:

- per course: no more than N sessions on one node;
- per learner: one active session;
- per classroom: spread across at least two nodes if available;
- per lab: avoid filling the pool with one exercise's image.

These are guardrails, not fairness guarantees.

## Queue and backpressure

When no node fits:

- reject with `capacity_unavailable`, a short reason, and a retry hint;
- do not silently queue for minutes;
- if a queue is added, cap it, show position, and expire stale requests;
- keep a reserved emergency slot for an operator or a lab recovery.

## Drain and maintenance

- `drain` stops new placements immediately.
- Existing sessions continue.
- The UI shows why the node is draining and who requested it.
- A drained node with no sessions can be upgraded or removed.
- Undrain requires capacity and health checks to pass again.

## Overcommit policy

Choose one and document it:

| Policy | Use |
|---|---|
| No CPU overcommit | Safest for bursty labs |
| CPU overcommit, memory hard-limited | Common for classroom labs |
| Memory overcommit | Not recommended; use only with swap and a proven test |

If you overcommit, the placement score must use **reserved** resources and the
node must still pass a live memory-pressure check.

## Load and soak tests

Run:

1. Advertised concurrency at steady state.
2. Advertised concurrency + 20% burst.
3. Largest lab image pull on a cold node.
4. Repeated create/stop cycles to detect leaks.
5. One node drained during a class.
6. One node killed during a class.
7. 24-hour soak with normal start/stop churn.

Record CPU, memory, disk, spawn latency, failure rate, and orphan count. A
capacity claim without a load test is a guess.
