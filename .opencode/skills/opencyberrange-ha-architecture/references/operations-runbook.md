# Operations runbook

Short, actionable procedures. Every step should be possible from the admin UI
or a documented command; no step should require reading the source code.

## Daily checks

- All nodes online and heartbeating.
- Capacity above the safety reserve.
- No route drift or duplicate CIDRs.
- No orphan sessions or leaked networks.
- PostgreSQL replication healthy.
- Redis healthy.
- Certificates not expiring within 30 days.
- Last backup completed and readable.

## Drain a node

1. Confirm the node is healthy enough to finish existing sessions.
2. Set `drain=true` in Admin → Lab nodes.
3. Confirm new sessions stop landing there.
4. Wait for active sessions to finish, or stop them with learner notice.
5. Upgrade/reboot only when `active=0`.
6. Health-check, undrain, and watch the next few placements.

Do not drain every node at once.

## Node heartbeat lost

1. Check whether the node host is reachable on the underlay.
2. Check the agent container and certificate.
3. If the agent is down but Docker is healthy, restart the agent; existing
   sessions may continue.
4. If the host is down, mark the node offline and withdraw routes.
5. Mark its sessions lost, notify affected learners, and offer relaunch.
6. After recovery, reconcile and remove orphans.

## Node failure

1. Remove the node from placement.
2. Withdraw all routes owned by the node.
3. Mark sessions lost; preserve the audit record.
4. Relaunch on healthy capacity.
5. Check for leaked networks and containers after the node returns.
6. Record the failure and the learner impact.

## Route drift

1. Stop new admission if duplicate CIDRs are active.
2. Compare `network_allocations` with gateway routes.
3. Withdraw stale routes.
4. Re-add missing routes for active sessions.
5. Investigate why reconciliation missed the change.
6. Do not restart the gateway until you know whether routes are missing or
   duplicated.

## Database failover

1. Confirm the standby is healthy and caught up.
2. Promote through the chosen HA tool, not by hand-editing containers.
3. Confirm one scheduler leader.
4. Confirm API health and login.
5. Check session cleanup did not run twice.
6. Record RTO/RPO and any lost transaction.

## Redis failover

1. Confirm the replica is promoted.
2. Confirm rate limiting is degrading safely, not blocking all traffic.
3. Restart API workers only if they hold stale connections.
4. Watch for a thundering herd after recovery.

## Capacity exhaustion

1. Reject new sessions with a clear capacity message.
2. Check for orphan sessions and released-but-not-cleaned networks.
3. Drain or add a node if available.
4. Do not lower reservations to admit more sessions.
5. Record the peak and update the capacity plan.

## Emergency stop

1. Stop new placement.
2. Keep existing sessions running if safe.
3. Preserve logs and route tables.
4. Use the single-host fallback only if the control plane is unrecoverable.
5. Restore and re-apply the erasure ledger after any database restore.

## Post-incident

- Write the timeline.
- Record which alert fired and which did not.
- Add or fix one test.
- Update the capacity model if the incident was load-related.
- Do not close the incident without a follow-up owner.
