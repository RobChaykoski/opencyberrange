# Failure model and acceptance tests

HA is a set of tested recovery paths, not a topology diagram.

## Failure matrix

| Failure | Expected behaviour | RTO target | Data risk |
|---|---|---|---|
| API replica dies | Load balancer routes to survivor; new requests succeed | < 30 s | None |
| Frontend replica dies | Survivor serves the UI | < 30 s | None |
| PostgreSQL primary fails | Standby promotes; scheduler leader re-elected | < 2 min | Last committed transaction only |
| Redis fails over | Rate limiting degrades safely; sessions continue | < 1 min | Ephemeral counters |
| Lab node dies | Sessions on it marked lost; routes withdrawn; relaunch works elsewhere | < 2 min to new session | In-session work lost |
| Node agent dies | Node marked degraded/offline; no new placement | < 60 s detection | Existing sessions keep running until node loss |
| VPN gateway dies | Standby takes over; peers reconnect | < 2 min | Tunnel interruption |
| Registry unavailable | Prewarmed nodes still spawn; cold nodes reject clearly | No new cold spawn | None |
| Network partition | Node stops accepting work; control plane marks it degraded | < 60 s | Possible orphan cleanup |
| CIDR allocator bug | Duplicate CIDRs detected and blocked | Immediate admission stop | None if caught before bind |
| Image pull failure | Session fails before learner sees "running" | < 1 attempt | None |
| Control-plane total loss | Existing node sessions may continue; platform unavailable | Rebuild from backup | Last backup |

State explicitly which rows are **not** HA. A lab session is not migrated.

## RTO/RPO worksheet

Before implementation, record:

- maximum acceptable platform outage;
- maximum acceptable new-session delay;
- whether in-session learner work may be lost;
- backup frequency and restore time;
- who can declare a failover;
- who can drain or remove a node.

If the product cannot meet the stated RTO, reduce the claim rather than hide it.

## Acceptance tests

### A. Normal operation

- Two API replicas, two lab nodes, one gateway, one registry.
- 100 concurrent sessions (or the advertised number).
- No duplicate CIDRs.
- Every active CIDR has exactly one gateway route.
- Session start p95 within the published target.
- Admin dashboard shows accurate counts.

### B. Isolation

From a learner session:

- own targets reachable;
- another session's targets unreachable;
- management LAN unreachable;
- control-plane database and Redis unreachable;
- Docker API unreachable.

From the host:

- Docker API not public;
- node-agent port not public;
- no lab bridge reachable from management.

### C. Lab node failure

1. Start sessions on node A and node B.
2. Kill node A's Docker/agent or power it off.
3. Confirm:
   - node A becomes `offline`;
   - node A's sessions become `lost`;
   - gateway routes are withdrawn;
   - new sessions land on node B;
   - relaunch works;
   - no orphaned containers remain after recovery.

### D. API replica failure

1. Kill one backend replica.
2. Confirm existing sessions continue.
3. Confirm login and new launch succeed through the survivor.
4. Confirm scheduler leadership remains single-owner.

### E. PostgreSQL failover

1. Promote the standby or stop the primary.
2. Confirm the scheduler leader moves.
3. Confirm no duplicate cleanup jobs.
4. Confirm audit and session state are consistent after recovery.

### F. Redis failover

1. Stop the Redis primary.
2. Confirm rate limiting degrades without blocking lab traffic.
3. Confirm counters recover and no auth outage occurs.

### G. Drain

1. Drain node A.
2. Confirm no new sessions land there.
3. Confirm existing sessions continue.
4. Undrain and confirm admission resumes after health checks pass.

### H. Rolling upgrade

1. Upgrade one API replica at a time.
2. Upgrade one lab node at a time with drain.
3. Confirm no control-plane outage and running labs survive.

### I. Image prewarm

1. Prewarm a large lab image on node B.
2. Request that lab.
3. Confirm it lands on node B and does not pull/build.
4. Confirm an unprewarmed node is not selected when the image is missing and the
   spawn budget would be exceeded.

### J. Capacity rejection

1. Fill the pool to the advertised limit.
2. Request one more session.
3. Confirm a clear `capacity_unavailable` response, no partial containers, and
   no leaked CIDR.
4. Release one session and confirm admission resumes.

## Evidence format

For each test record:

- commit and image digests;
- node/gateway/API versions;
- exact command or action;
- timestamps;
- before/after screenshots or API output;
- route table before/after;
- session IDs and node IDs;
- what failed and what was cleaned up;
- operator sign-off.

A green dashboard screenshot is not evidence of failover.

## Rollback

- Keep the single-host path runnable.
- Keep the previous control-plane image tag.
- Keep node drain and remove procedures.
- If the scheduler or agent is faulty, stop new placements first; do not delete
  running sessions.
- Restore PostgreSQL from the last verified backup if a failover corrupts state.
- Re-apply the erasure ledger after any restore.
