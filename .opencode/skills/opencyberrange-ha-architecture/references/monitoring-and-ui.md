# Monitoring and admin UI

The HA UI must answer three questions in under ten seconds:

1. Is the platform healthy?
2. Where are the running sessions?
3. What should an operator do next?

Do not build a wall of raw metrics. Build an operational surface.

## Service health model

Track these independently:

| Component | Health signal |
|---|---|
| Frontend replicas | HTTP health, request latency, 5xx rate |
| API replicas | `/health`, DB/Redis connectivity, scheduler leadership, queue depth |
| PostgreSQL | primary/standby state, replication lag, connection saturation |
| Redis | primary/replica state, latency, evictions, rate-limit failures |
| Lab nodes | heartbeat, Docker API, disk, memory, KVM, image inventory |
| VPN gateway | tunnel health, peer count, route count, route drift |
| Registry | pull latency, image availability |
| Node agents | version, certificate expiry, command failures |

A component is not "healthy" just because its container is running.

## Node row in the admin UI

Each node should show:

- name, region/zone, agent version;
- status: `online`, `degraded`, `draining`, `offline`;
- last heartbeat age;
- CPU used/reserved/total;
- memory used/reserved/total;
- disk used/free;
- active/starting/stopping/failed sessions;
- KVM ready;
- image readiness for the current assignment;
- route count and last route drift;
- drain/undrain action with confirmation;
- a link to recent agent errors.

Use both a bar and a text ratio (`18 / 24 sessions`). Do not rely on colour
alone.

## Platform summary

Show:

- active sessions vs capacity;
- queued spawn requests and rejection count;
- spawn latency p50/p95;
- failed spawns in the last hour;
- orphaned sessions and leaked networks;
- route drift and duplicate CIDR count;
- PostgreSQL/Redis failover state;
- certificate expiries within 30 days.

## API shape

Keep the response boring and stable:

```json
{
  "generated_at": "2026-11-04T20:00:00Z",
  "nodes": [
    {
      "id": "node-a",
      "name": "Lab node A",
      "status": "online",
      "last_heartbeat": "2026-11-04T19:59:55Z",
      "capacity": {
        "cpu_millicores": { "total": 16000, "reserved": 9000, "used": 7000 },
        "memory_mb": { "total": 65536, "reserved": 42000, "used": 36000 },
        "disk_gb": { "total": 500, "free": 160 }
      },
      "sessions": {
        "active": 18,
        "starting": 1,
        "stopping": 0,
        "failed": 0,
        "max": 24
      },
      "kvm_ready": true,
      "images_ready": true,
      "route_count": 18,
      "drain": false
    }
  ],
  "summary": {
    "active_sessions": 42,
    "capacity_sessions": 72,
    "queued": 0,
    "route_drift": 0,
    "failed_spawns_1h": 1
  }
}
```

The UI may poll every 10–15 seconds. Pause polling when the tab is hidden;
refresh immediately on return. Do not announce every poll in a live region.

## Alerts

Alert on symptoms an operator can act on:

| Alert | Suggested trigger |
|---|---|
| Node heartbeat lost | 3 missed heartbeats |
| Node offline | 6 missed heartbeats or hard failure |
| Capacity critical | free memory or CPU below 10% on all nodes |
| Spawn failure spike | > 3 failures in 10 minutes |
| Route drift | any active CIDR missing or duplicated |
| Orphan sessions | session without a lease, or lease without a session |
| Database failover | primary change or replication lag above threshold |
| Redis failover | primary change or rate-limit errors |
| Certificate expiry | < 30 days |
| Scheduler leader change | unexpected change or no leader |

Every alert needs a runbook link. An alert without an action is noise.

## Logs and traces

- Correlate `session_id`, `node_id`, `command_id`, and `request_id`.
- Never log flags, passwords, tokens, VPN private keys, or full student PII.
- Keep control-plane logs and node-agent logs separately searchable.
- Log route changes and drain/undrain actions in the audit trail.
- Sample high-volume Docker status logs; keep lifecycle events complete.

## UI states

Design and test:

- loading: preserve the table/card layout;
- empty: "No lab nodes registered" with the registration step;
- degraded: a node is online but a dependency is failing;
- offline: heartbeat lost, with last-seen time;
- permission denied: instructor vs admin;
- action in progress: drain/undrain disabled with clear status;
- partial data: show the nodes that responded, mark the rest unknown.

Use the project design tokens and the `opencyberrange-design` skill. Do not add a
second theme or a marketing-style dashboard.

## SLOs to start with

| SLO | Target |
|---|---|
| Control-plane API availability | 99.9% monthly |
| New session admission latency | p95 < 2 s before image pull |
| Spawn success rate | > 99% excluding capacity rejection |
| Route reconciliation | < 30 s after change |
| Node failure detection | < 60 s |
| Admin dashboard freshness | < 15 s |

Adjust only with evidence.
