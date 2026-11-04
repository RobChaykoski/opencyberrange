---
name: OpenCyberRange HA Architecture
description: Use when designing, reviewing, or implementing the v3 multi-host HA solution for OpenCyberRange. Covers control-plane HA, lab-node pools, session network and VPN routing, mTLS node communication, capacity and placement, overload prevention, monitoring, failure recovery, and acceptance tests.
---

# OpenCyberRange HA Architecture

Use this skill for **v3 high availability** work: moving from one Docker host to a
control plane plus a pool of lab nodes without losing the per-session isolation,
the single-host fallback, or the learner experience.

This is an architecture and operations skill, not a generic Kubernetes tutorial.
Keep the OpenCyberRange model: a session owns a `/24`, Docker Compose runs the
lab, WireGuard reaches the session, and the platform API remains the source of
truth.

Companion documents:

- [`docs/V3-HA-LAB-POOL.md`](../../../docs/V3-HA-LAB-POOL.md) — phased target
  architecture and the current single-host assumptions.
- [`docs/V3-PARKING-LOT.md`](../../../docs/V3-PARKING-LOT.md) — scope entry V3-8.
- [`docs/ARCHITECTURE.md`](../../../docs/ARCHITECTURE.md) — current platform
  architecture and trust boundaries.
- [`docs/V2-SECURITY-OWASP-TOP-10.md`](../../../docs/V2-SECURITY-OWASP-TOP-10.md)
  — security requirements that still apply.

## Core stance

1. **Single-host remains the default.** HA is an opt-in deployment profile. Do
   not make a classroom install depend on a scheduler, a registry, or a second
   host.
2. **A lab session is not migrated.** If a node dies, the session is marked
   lost, routes are withdrawn, and relaunch lands on a healthy node. Say this in
   the product and the runbook.
3. **The control plane is the source of truth.** Node-local state is a cache and
   a reconciliation target, never the only record of a session.
4. **Isolation is non-negotiable.** No lab can reach another lab, the
   management LAN, the Docker API, or the control-plane database.
5. **Admission control beats hope.** A node that cannot prove it has capacity
   must reject new sessions before pulling an image or creating a network.
6. **Every failure has a visible state.** The UI, API, logs, and alerts must
   agree on whether a node, session, route, or dependency is healthy.

## Required design inputs

Before drawing a topology, record:

| Input | Why it matters |
|---|---|
| Peak concurrent sessions and burst profile | Sizes the lab pool and headroom |
| Session RAM/CPU/disk distribution by lab | Prevents sizing from averages alone |
| KVM / shared-container / multi-container mix | Drives hard placement filters |
| Cohort and course affinity rules | Avoids spreading one class randomly |
| Failure domains (host, rack, network, cloud) | Sets realistic HA claims |
| RTO and RPO | Decides how much automation is required |
| VPN client scale and address plan | Drives gateway and route design |
| Image build and pull budget | Spawn latency is usually image-bound |
| Monitoring and on-call ownership | A dashboard without an owner is decoration |

If the answer is "one host is enough", stop. Do not build HA for a single-host
deployment.

## Target topology

```text
Client
  |
  | WireGuard
  v
+--------------------- control plane ---------------------+
| ingress / TLS -> frontend replicas -> API replicas      |
|                         |                               |
|          PostgreSQL HA  Redis HA  object storage        |
|                         |                               |
|                 scheduler leader (advisory lock)        |
+-------------------------+-------------------------------+
                          | mTLS control channel
        +-----------------+-----------------+
        v                 v                 v
   lab node A        lab node B        lab node C
   node agent        node agent        node agent
   Docker + compose  Docker + compose  Docker + compose
   session /24s      session /24s      session /24s
        \                 |                 /
         \______ VPN gateway route table __/
```

The VPN gateway is a **router**, not a trust boundary. The Docker bridge and the
node firewall still enforce isolation.

## Design workflow

1. **Pick the failure story.** Write down what survives and what does not:
   control-plane replica, API node, database primary, Redis, lab node, gateway,
   registry, and network partition.
2. **Draw three networks.** Management/underlay, lab data plane, and client VPN.
   Label every route, firewall rule, and trust boundary.
3. **Define the contracts.** `lab_nodes`, `network_allocations`,
   `LabSession.node_id`, node-agent commands, heartbeat, and route ownership.
4. **Size the pool.** Use measured per-lab memory/CPU/disk, not the lab
   estimate, and reserve headroom for the largest lab.
5. **Design admission and placement.** Hard filters, affinity, spread,
   least-allocated score, and a clear "no capacity" response.
6. **Design monitoring and the admin UI.** Node list, capacity, drain, session
   counts, route count, queue depth, and alerts.
7. **Write the acceptance tests before implementation.** If a test cannot be
   run, the design is not ready.
8. **Implement one phase at a time.** Keep the single-host runtime as the
   reference path and run its tests unchanged.

## Network design checklist

Read [`references/network-and-routing.md`](references/network-and-routing.md)
for the full checklist. Minimum requirements:

- [ ] Separate management, lab, and VPN address spaces. No overlap.
- [ ] One central `/24` allocator; every active CIDR has exactly one owner node.
- [ ] Gateway route add/remove is idempotent and reconciled against the database.
- [ ] Node underlay is reachable only from the control plane and gateway.
- [ ] Docker API and node-agent control port are never public.
- [ ] Per-session Docker bridge and firewall rules remain on the node.
- [ ] Lab-to-lab, lab-to-management, and lab-to-control-plane probes fail.
- [ ] IPv4 first; if IPv6 is added, allocate and test it explicitly.
- [ ] MTU, DNS, NAT, hairpin, and overlay encapsulation are tested with a real
  lab, not only ping.
- [ ] Cross-cloud or cross-site nodes use a private overlay, not exposed bridges.

## Node communication checklist

Read [`references/node-agent-contract.md`](references/node-agent-contract.md).

- [ ] Control plane → node agent uses mutually authenticated TLS.
- [ ] Node agent is the only component with the local Docker socket.
- [ ] Commands are idempotent, signed/authenticated, timeout-bounded, and
  retried with a command ID.
- [ ] Heartbeats report CPU, RAM, disk, KVM, image inventory, session count, and
  agent version.
- [ ] Agent reports desired vs actual state; the control plane reconciles.
- [ ] Certificate rotation and revocation are documented and tested.
- [ ] A node can be drained without killing running sessions.
- [ ] Orphan sessions and leaked networks are cleaned up after a partition.

## Capacity and overload checklist

Read [`references/capacity-and-placement.md`](references/capacity-and-placement.md).

- [ ] Hard reservation per session: memory, CPU, disk, PIDs, and optional KVM.
- [ ] Node admission uses measured free capacity and reserve headroom.
- [ ] Per-node, per-course, and per-cohort caps prevent one class from taking
  the pool.
- [ ] The scheduler rejects with a clear capacity error; it never starts a
  partial session.
- [ ] Shared containers and multi-container labs land on the same node.
- [ ] Image inventory is a placement input, not a surprise pull.
- [ ] Drain mode stops new placement while existing sessions finish.
- [ ] Load tests cover the advertised concurrent-session number plus a burst.

## Monitoring and UI checklist

Read [`references/monitoring-and-ui.md`](references/monitoring-and-ui.md).

The admin UI must show, per node:

- health and last heartbeat;
- CPU, RAM, and disk used/reserved/free;
- active, starting, stopping, and failed sessions;
- KVM availability and image readiness;
- drain/undrain control with confirmation;
- route count and recent agent errors.

The backend must expose:

- node list and detail;
- session placement and owning node;
- capacity summary and rejection reasons;
- queue depth and scheduler latency;
- route reconciliation status;
- dependency health for PostgreSQL, Redis, registry, and VPN gateway.

Alerts must cover:

- node heartbeat loss;
- repeated spawn failures;
- capacity below the safety reserve;
- route drift or duplicate CIDRs;
- PostgreSQL/Redis failover;
- certificate expiry;
- scheduler leader changes.

## Failure and acceptance tests

Read [`references/failure-and-acceptance.md`](references/failure-and-acceptance.md).
The release gate is not "the dashboard is green". It is:

1. Two control-plane API replicas and two lab nodes run 100 concurrent sessions.
2. No duplicate CIDRs; every active CIDR has exactly one route.
3. Cross-session and lab-to-management probes fail.
4. Kill one lab node: affected sessions are marked lost, routes withdrawn, and
   relaunch succeeds on the healthy node.
5. Kill one API replica: existing sessions continue and new requests succeed.
6. Fail over PostgreSQL: scheduler leadership moves; no duplicate cleanup.
7. Fail over Redis: rate limiting degrades safely, then recovers.
8. Drain a node: no new sessions arrive; existing sessions finish.
9. Rolling upgrade: no control-plane outage; running labs survive.
10. Prewarmed image: spawn on a node with the image does not build or pull.

Record the evidence in the release notes. A screenshot is not evidence of
failover.

## Design review output

A HA design is ready for review only when it includes:

- topology diagram with trust boundaries;
- address plan and route ownership;
- node-agent API contract and security model;
- capacity table and placement rules;
- failure matrix with RTO/RPO;
- monitoring dashboard and alert list;
- acceptance-test plan and rollback path;
- explicit statement of what is **not** HA.

## Anti-patterns

- Sharing one Docker socket across hosts.
- Exposing the Docker API or node-agent port to the internet.
- Allocating `/24`s on the node instead of centrally.
- Treating the VPN gateway as the only isolation control.
- Scheduling by CPU percentage alone while ignoring memory and disk.
- Pulling a large image after admitting a session.
- Using a public leaderboard-style "node health" that hides degraded states.
- Calling a design HA when a node loss still requires manual database surgery.
- Adding HA to the v2 branch or to a single-host classroom deployment.
