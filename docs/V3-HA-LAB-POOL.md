# Enterprise 3.0 Multi-Host Lab Pool and HA Deployment Plan

Status: **Enterprise 3.0 — control-plane HA reference implemented and locally
drilled; lab-pool and full multi-host validation not implemented**
Program link: [`docs/V3-PARKING-LOT.md`](V3-PARKING-LOT.md)
Design skill: `.opencode/skills/opencyberrange-ha-architecture/SKILL.md`

> Enterprise 3.0 adds high availability and multi-host lab pools on top of
> Professional 2.0. The Professional analytics and reporting workstreams do not
> depend on this plan.

## Purpose

This plan defines how v3 can move from a single Docker host to a pool of lab
hosts for capacity and high availability. It also explains where Docker Swarm
and Kubernetes fit, and why the first target is a controller plus node-agent
pool rather than Swarm scheduling of lab sessions.

Terminology:

- **Docker pod** in this document means a registered Docker Engine host (or a
  logical group of hosts) that runs learner lab sessions. It is not a
  Kubernetes Pod.
- **Lab pool** means the set of Docker pods managed by one control plane.
- **Control plane** means the frontend, API, scheduler, database, Redis, and
  VPN gateway services.

## What the current code assumes

The current implementation is deliberately single-host:

| Assumption | Location |
|---|---|
| One local Docker socket | `DockerManager` uses `docker.from_env()` |
| Local Compose CLI | `docker compose` is run as a subprocess for lab up/down |
| Labs read from a local mount | `/labs` inside the backend container |
| Session subnet is derived only from the user | `get_subnet_id()` in `docker_manager.py` |
| Session has no host ownership | `LabSession` has `network_id` and `network_subnet`, but no `node_id` |
| Only one WireGuard endpoint | Peer Manager and `wg0` run on the installation host |
| Images are built and tagged locally | `scripts/prebuild-labs.sh` tags `ocr-lab/*` on one host |
| Backups are local files | `/app/backups` named volume |
| Per-worker state can be local | Some locks/state live under `/tmp` |
| Scheduler leader election exists | PostgreSQL advisory lock in `main.py`; this part is already HA-friendly |

Any one of these breaks naive multi-host deployment. The plan removes them in
phases so the single-host path keeps working.

## Target architecture

```mermaid
flowchart TB
    LB[Load balancer / ingress]
    subgraph CP[Control plane]
        FE1[frontend 1]
        FE2[frontend 2]
        API1[backend 1]
        API2[backend 2]
        PG[(PostgreSQL HA)]
        RD[(Redis HA)]
        OS[(Object storage / shared wiki + backups)]
        WG[WireGuard gateway(s)]
    end
    subgraph LP[Lab host pool]
        A1[node agent<br/>Docker pod A]
        A2[node agent<br/>Docker pod B]
        A3[node agent<br/>Docker pod C]
        L1[session containers<br/>10.100.x/24]
        L2[session containers<br/>10.101.x/24]
        L3[session containers<br/>10.102.x/24]
    end
    REG[(Private image registry)]
    LB --> FE1 & FE2
    FE1 & FE2 --> API1 & API2
    API1 & API2 --> PG
    API1 & API2 --> RD
    API1 & API2 --> OS
    API1 & API2 --> A1 & A2 & A3
    A1 --> L1
    A2 --> L2
    A3 --> L3
    REG --> A1 & A2 & A3
    WG --> L1 & L2 & L3
```

### Control plane HA

- Two or more backend replicas behind a load balancer. JWT auth is shared, so
  no session affinity is required.
- PostgreSQL with a primary and standby (Patroni, managed PostgreSQL, or the
  platform's chosen HA service).
- Redis with replication/Sentinel or a managed Redis service for shared rate
  limits and short-lived coordination.
- Shared object storage for generated wiki content, backups, and exports.
  `/tmp` state must move to Redis or PostgreSQL before more than one backend
  host is allowed.
- The existing PostgreSQL advisory lock already elects one scheduler leader
  across replicas. Keep that pattern.
- WireGuard gateways run as an active/passive or active/active pair and
  reconcile peers from the database.

### Lab host pool

Each Docker pod runs a small **node agent** beside Docker. The agent:

- owns the local Docker socket and `docker compose` execution;
- receives commands over mTLS from the control plane;
- reports CPU, RAM, disk, KVM availability, image inventory, and session
  counts;
- prepares images ahead of a spawn;
- applies local firewall and isolation rules;
- creates and destroys session networks and containers;
- streams container status and logs;
- supports drain mode so no new sessions land on it.

The control plane keeps a `lab_nodes` table (name, endpoint, certificate
fingerprint, region, labels, capacity, status, last heartbeat, drain flag) and
a `network_allocations` table (CIDR, node, session, released_at). `LabSession`
gains `node_id` and `project_name` so cleanup and status checks target the
correct host.

### Placement

The scheduler selects a node by:

1. hard filters: active, not draining, enough free memory/CPU, required KVM,
   required image, allowed region;
2. lab affinity: shared containers and dependent services must land on the
   same node;
3. spread/anti-affinity: avoid concentrating one course or one student cohort;
4. least allocated score, then a stable tie-break.

If no node fits, return a clear capacity error rather than starting a partial
session.

### Networking

Clients already route all lab CIDRs through the VPN. In a pool, the VPN gateway
must know which Docker pod owns each session CIDR.

Recommended path:

- Allocate each session `/24` from a central allocator and record the owning
  node.
- Keep the gateway on a private network that can reach every lab pod.
- Install a route on the gateway for each active session CIDR to the owning
  node's underlay address.
- Withdraw the route when the session stops or the node is drained/fails.
- Keep the existing per-session Docker bridge and firewall isolation on the
  node; the gateway is only a route, not a trust boundary.

If lab pods live in different clouds or networks, use a private overlay
(WireGuard mesh, Tailscale, or provider VPC peering) rather than exposing
Docker APIs or lab bridges publicly.

### Images

`prebuild-labs.sh` currently builds and tags locally. For a pool:

- push immutable `ocr-lab/<slug>-<service>:<hash>` images to a private
  registry;
- keep the stable `:latest` tag for the fast spawn path;
- have the node agent pull and verify the image before admitting a session;
- track per-node image inventory so placement does not send a session to a
  node that will need a long pull;
- pin and sign images where the deployment requires it.

### Storage and state

- Database snapshots go to object storage, not just a local volume.
- The erasure suppression ledger and workbook state need a shared durable
  location understood by every backend replica.
- The admin impersonation store and other `/tmp`-backed coordination move to
  Redis or PostgreSQL.
- Exercise tester scratch state remains node-local and ephemeral.

## What HA means for a lab session

A running lab is stateful. It cannot be live-migrated between Docker pods
without checkpoint/restore support that is out of scope.

Define the contract:

- **Control plane failure:** API/frontend fail over; students keep their
  browser session and their lab keeps running on its node.
- **Lab node failure:** the session is marked `error`/`lost`, its network
  allocation is released, the VPN route is withdrawn, and the student is told
  to relaunch. A fresh session is placed on a healthy node.
- **Gateway failure:** peers reconnect to the standby gateway; routes are
  reconciled from the database.
- **Database failover:** short write outage; API retries; scheduler leadership
  moves to another replica.

Do not promise live migration. Promise fast recovery and clear user messaging.

## Option comparison

| Option | Fit | Notes |
|---|---|---|
| Single host (current) | Baseline | No HA; simple and fully validated |
| Replicated Compose control plane | Partial | Helps API/DB failover but labs still fail with the host |
| Controller + Docker pod agents | **Recommended first HA target** | Fits per-session networks, Compose, KVM, and existing firewall model |
| Docker Swarm for the platform stack | Optional | Useful for stateless control-plane services; not suitable as the lab scheduler |
| Docker Swarm for labs | Not recommended | Per-session Compose projects, static IPs, custom `/24` bridges, KVM devices, host-local shared containers, and WireGuard routing do not map cleanly to Swarm overlay services |
| Kubernetes | Later adapter | Strong scheduling/HA, but needs Multus/Whereabouts or Cilium for per-session IPs, device plugins for KVM, privileged-lab policy, and a Compose-to-manifest path |

### Why not start with Swarm

Swarm is good at scheduling stateless replica services. A lab session is the
opposite: one stateful Compose project per learner, a dedicated bridge and
`/24`, static container IP offsets, host-local shared containers, and firewall
rules on the node. Swarm overlay networking and service VIPs obscure the exact
address layout the exercises depend on. Swarm could host the platform services
in Phase 4, but the lab pool still needs an agent and a scheduler.

## Phased implementation

### Phase 1 — Runtime abstraction

- Introduce a `LabRuntime` interface with `LocalDockerRuntime` as the only
  implementation.
- Route `DockerManager` operations through the interface without changing
  behaviour.
- Add contract tests so local mode remains byte-for-byte compatible with the
  existing spawn/teardown path.

Exit criteria: single-host tests and lab smoke tests unchanged.

### Phase 2 — Node registry and agent

- Add `lab_nodes`, `network_allocations`, and `LabSession.node_id`.
- Build the node agent with mTLS, health, inventory, image pull, and
  create/destroy/status endpoints.
- Add an admin node list and drain action.
- Keep one node in the pool; all traffic still goes to it.

Exit criteria: a session can be created and destroyed through the agent with
the same visible behaviour as local mode.

### Phase 3 — Scheduler and routing

- Add placement filters and least-allocated scoring.
- Bind each session to a node and allocate its `/24` centrally.
- Add gateway route add/remove and reconciliation.
- Add node-failure detection, session loss handling, and orphan cleanup.
- Add per-node capacity display to Admin.

Exit criteria: two lab nodes run sessions concurrently with no overlapping
CIDRs, correct VPN routes, and no cross-session reachability.

### Phase 4 — Control-plane HA

Reference implementation status: **implemented in `opencyberrange-ha`, locally
drilled on one Docker host in November 2026.**

- Run two frontend and two backend replicas behind a load balancer. **Done in
  the reference compose and HAProxy config.**
- Move PostgreSQL and Redis to HA services. **Reference primary/standby
  PostgreSQL and Redis primary/replica/three-Sentinel composes added; managed
  services are still the production recommendation.**
- Move backups, wiki, and ledger state to shared storage. **Shared volumes are
  wired into the reference compose, with a filesystem adapter and verification
  probe; the production object-store adapter is still required.**
- Move `/tmp` coordination to Redis/PostgreSQL. **The exercise-tester run
  directory is on a shared volume as an interim step; it is not yet moved to a
  shared service.**
- Add active/standby WireGuard gateways with peer and route reconciliation.
  **Route and peer reconcilers are implemented and unit-tested; the live
  keepalived/WireGuard drill is still required.**
- Test failover of each component. **Local pass: API loss, frontend loss, Redis
  degradation, PostgreSQL promotion, and Redis Sentinel failover. Pending:
  multi-host failure domains, gateway failover, and the 24-hour soak.**

Exit criteria: killing any control-plane replica does not stop a running lab,
and a new login/launch succeeds during the failover window. **Local single-host
replica-loss drill passes; the multi-host exit gate is still open.**

### Phase 5 — Operations and optional orchestrators

- Add drain, rolling upgrade, image prewarm, and capacity alerts.
- Add failure drills to the upgrade runbook.
- Evaluate Swarm or Kubernetes only after the agent-based pool is stable.
- If Kubernetes is adopted, implement it as another `LabRuntime` backend, not a
  rewrite of the control plane.

## Acceptance tests

1. Two app nodes, two lab nodes, and one gateway: 100 concurrent sessions.
2. No duplicate session CIDRs; every active CIDR has exactly one route.
3. Cross-session and lab-to-management-LAN probes fail.
4. Kill one lab node: affected sessions are marked lost, routes withdrawn, and
   relaunch succeeds on the healthy node.
5. Kill one API node: existing sessions continue and new requests succeed.
6. Fail over PostgreSQL: scheduler leadership moves; no duplicate cleanup.
7. Fail over Redis: rate limiting degrades safely, then recovers.
8. Drain a lab node: no new sessions arrive; existing sessions finish.
9. Rolling upgrade: no control-plane outage; running labs survive.
10. Image prewarm: a spawn on a node with the image does not build or pull.

## Risks

| Risk | Mitigation |
|---|---|
| Sessions cannot be migrated | Document lost-session recovery and make relaunch fast |
| Central `/24` allocation leaks on crashes | Lease expiry + reconciler against node state |
| Gateway routing becomes the bottleneck | Route reconciliation, health checks, standby gateway |
| Image sprawl across nodes | Registry + inventory + prewarm + eviction policy |
| KVM labs land on non-KVM nodes | Hard node label/taint requirement |
| Shared containers and Dockur VMs need co-location | Lab affinity key enforced by scheduler |
| More moving parts than a classroom needs | Keep single-host mode as the default; pool is opt-in |

## Recommendation

1. Finish the **24.04 single-host migration first**. Do not combine an OS
   migration with a distributed scheduler.
2. Build the **controller + node-agent lab pool** as the first HA step.
3. Treat Docker Swarm as an optional control-plane convenience, not the lab
   scheduler.
4. Keep Kubernetes as a later `LabRuntime` adapter once the pool is proven.
