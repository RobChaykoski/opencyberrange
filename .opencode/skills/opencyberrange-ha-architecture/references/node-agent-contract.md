# Node agent contract

The node agent is the only process on a lab node that talks to Docker. The
control plane never mounts or proxies the Docker socket.

## Responsibilities

- register the node and prove its identity;
- heartbeats with capacity and inventory;
- pull and verify prebuilt images;
- create and destroy session networks and containers;
- report status, logs, and resource usage;
- apply local firewall and isolation rules;
- reconcile desired state after a restart or partition;
- drain so no new sessions are placed on the node.

## Trust model

- Control plane → agent: mutually authenticated TLS on the private underlay.
- Agent → control plane: outbound mTLS heartbeat/result channel.
- No public listener for the agent or Docker API.
- Each node has its own certificate and a stable node ID.
- Certificate rotation and revocation are mandatory, not a later task.
- The agent should run with the minimum host privileges it needs; Docker socket
  access is already root-equivalent, so isolate the host from learners and
  protect the agent container itself.

## Data model

### `lab_nodes`

| Field | Notes |
|---|---|
| `id` | Stable UUID/string |
| `name` | Operator label |
| `endpoint` | Underlay URL, never public |
| `cert_fingerprint` | Pinned identity |
| `region` / `zone` | Placement and failure domain |
| `labels` | `kvm=true`, `gpu=none`, `classroom=a` |
| `cpu_total`, `cpu_reserved` | Millicores |
| `mem_total_mb`, `mem_reserved_mb` | Hard reservations |
| `disk_total_gb`, `disk_reserved_gb` | Image and session storage |
| `max_sessions` | Operator cap |
| `status` | `online`, `degraded`, `draining`, `offline` |
| `last_heartbeat` | Failure detection |
| `agent_version` | Compatibility check |
| `drain` | Boolean |

### `network_allocations`

| Field | Notes |
|---|---|
| `cidr` | Unique while active |
| `node_id` | Owner |
| `session_id` | Nullable until bound |
| `state` | `reserved`, `active`, `releasing`, `released` |
| `created_at`, `released_at` | Lease audit |
| `route_state` | `pending`, `installed`, `withdrawn`, `drift` |

### `LabSession`

Add `node_id` and `project_name`. `network_subnet` remains, but it must match the
allocation record.

## Command envelope

Every control-plane command has:

```json
{
  "command_id": "uuid",
  "session_id": 123,
  "type": "create_session",
  "deadline": "2026-11-04T20:00:00Z",
  "payload": {},
  "desired_state_version": 7
}
```

Rules:

- The agent deduplicates by `command_id`.
- Commands are idempotent; retrying `create_session` must not create a second
  network.
- The agent returns accepted, progress, success, or a structured failure.
- The control plane retries with backoff until the deadline, then marks the
  command failed.
- The control plane never assumes success without an agent result or a
  reconciliation match.

## Suggested endpoints

Use the exact paths your implementation chooses, but keep the semantics:

| Method | Path | Purpose |
|---|---|---|
| `POST` | `/v1/register` | Register node identity and inventory |
| `POST` | `/v1/heartbeat` | Capacity, health, image inventory, session counts |
| `GET` | `/v1/capacity` | Current admission view |
| `POST` | `/v1/images/prepare` | Pull/verify an image before placement |
| `POST` | `/v1/sessions` | Create a session network and containers |
| `DELETE` | `/v1/sessions/{id}` | Stop and clean a session |
| `GET` | `/v1/sessions/{id}` | Status and resource usage |
| `GET` | `/v1/sessions/{id}/logs` | Bounded log stream |
| `POST` | `/v1/drain` | Enter/leave drain mode |
| `POST` | `/v1/reconcile` | Compare desired and actual state |

## Session state machine

```text
requested -> admitted -> preparing -> starting -> running
                                              -> stopping -> stopped
                                              -> failed
running/starting -> lost        (heartbeat or node loss)
```

- `lost` is terminal for that session. Do not try to migrate containers.
- The control plane withdraws the route and marks the session lost.
- Relaunch creates a new session on a healthy node.
- Orphan cleanup removes containers/networks with no active lease.

## Heartbeat and failure detection

- Heartbeat every 5–10 seconds; jitter to avoid a thundering herd.
- Mark `degraded` after 3 missed heartbeats.
- Mark `offline` after 6 missed heartbeats or a hard connection failure.
- Do not immediately delete session rows; mark them lost and keep the audit.
- A recovered agent reconciles and reports orphans; it does not silently
  re-adopt sessions the control plane has already marked lost.

## Agent restart and partition behavior

- Persist the node ID and certificate outside the container.
- On restart, report actual Docker networks/containers and compare with desired
  state.
- If the control plane is unreachable, keep running existing sessions but stop
  accepting new work.
- If the agent was offline long enough for the control plane to mark sessions
  lost, clean up only after the lease expiry and audit record.
- Never delete a network that another active lease still references.

## Security requirements

- mTLS with per-node certificates and a private CA.
- No shared bearer token as the only node authentication.
- Rate-limit and size-limit command payloads.
- Validate image names against a registry allowlist.
- Do not accept arbitrary Docker Compose YAML from the control plane; send a
  signed lab reference and let the agent resolve a known artifact.
- Redact secrets from agent logs.
- Record every destructive command in the control-plane audit log.

## Observability

The agent should expose or ship:

- command latency and failure counts;
- Docker API errors;
- image pull duration and failures;
- session create/stop duration;
- network create/remove failures;
- disk pressure and orphan counts;
- agent version and certificate expiry.

## Contract tests

- duplicate `create_session` returns the same result;
- stop is idempotent;
- agent restart reconciles without duplicating networks;
- control-plane timeout does not leak a session;
- certificate rotation does not require re-registration;
- drain blocks new sessions but not stop/status;
- an invalid image reference is rejected before Docker runs.
