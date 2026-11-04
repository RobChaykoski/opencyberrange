# Network and routing design

This reference is for the v3 lab pool. The goal is to keep the existing
per-session `/24` model while allowing sessions to run on more than one Docker
host.

## Network planes

Keep these planes separate and named:

| Plane | Example | Purpose | Trust |
|---|---|---|---|
| Client VPN | `10.0.0.0/24` peers, `10.100.0.0/16` lab CIDRs | Learner tunnel to lab sessions | Untrusted client, authenticated peer |
| Lab data plane | per-session `/24` | Containers inside one session | Isolated, untrusted |
| Node underlay | `192.168.50.0/24` or provider private network | Control plane ↔ node agent, gateway ↔ node | Private, authenticated |
| Control-plane service network | `172.20.0.0/24` | API, frontend, PostgreSQL, Redis, object storage | Private, no learner access |
| Management | operator VPN / bastion | SSH, maintenance | Highest privilege |

Do not put the node underlay on the same subnet as a lab session. Do not put
management on a lab-reachable bridge.

## Address plan

Example:

```text
Lab session pool:       10.100.0.0/16
Session allocations:    10.100.0.0/24 ... 10.100.255.0/24
Reserved/never allocate:10.100.0.0/24 (control examples), 10.100.255.0/24
Client VPN peers:       10.0.0.0/24
Node underlay:          192.168.50.0/24
Gateway underlay:       192.168.50.10
Control plane:          172.20.0.0/24
```

Rules:

- Allocate the whole `/24` centrally; never let a node pick one.
- Store the lease, owning node, session, creation time, and released time in
  `network_allocations`.
- Bind a CIDR to exactly one active session. A released lease can be reused only
  after the node confirms the old network is gone.
- Reserve a small prefix for diagnostics and gateway tests.
- If the pool is exhausted, return a capacity error; do not borrow a CIDR.

## Route lifecycle

1. Scheduler reserves a `/24` and a node.
2. Node agent creates the session network.
3. Agent reports the network ID, subnet, and underlay endpoint.
4. Gateway adds a route: `10.100.N.0/24 via <node-underlay>`.
5. Reconciliation confirms the route and the node both exist.
6. On stop, drain, or node failure: withdraw the route first, then clean the
   node resources.
7. A reconciler compares database leases, gateway routes, and node networks and
   repairs or reports drift.

The route table is a cache of the database, not the source of truth. A stale
route is a security bug; a missing route is a learner outage.

## VPN gateway HA

- Run two gateways with a floating address or provider load balancer.
- Both gateways must be able to reach every node underlay.
- Reconcile peers and routes from the database on startup and on a timer.
- Keep the active/passive state explicit in monitoring.
- Test client reconnect during a gateway failover.
- Do not run the gateway on a lab node that can be drained.

## Firewall and isolation matrix

| Source | Destination | Allow? | Notes |
|---|---|---|---|
| Learner VPN peer | Own session `/24` | Yes | Via gateway route |
| Learner VPN peer | Another session `/24` | No | Drop at gateway and node |
| Learner VPN peer | Node underlay | No | Management plane |
| Learner VPN peer | Control plane | No | Only public ingress |
| Lab container | Another lab container in same session | Yes | Session bridge |
| Lab container | Another session | No | Docker bridge + firewall |
| Lab container | Management LAN | No | Explicit drop |
| Lab container | Control-plane database/Redis | No | No route |
| Control plane | Node agent mTLS port | Yes | Private underlay only |
| Node agent | Control plane API | Yes | Outbound mTLS/heartbeat |
| Operator | SSH/management | Yes | Bastion/VPN only |

Apply the node firewall at boot and after Docker restarts. Docker can insert
rules ahead of naive rules; use `DOCKER-USER`, `FORWARD`, and raw PREROUTING
consistently and verify with real probes.

## DNS

- Lab DNS remains per-session and resolves only inside the session.
- Do not leak session hostnames into public DNS.
- The control plane needs stable names for node agents and the gateway.
- If a node has multiple interfaces, bind the agent to the underlay address
  explicitly; do not rely on the default route.
- Test DNS from a lab container, not just from the host.

## MTU, NAT, and overlays

- WireGuard, VXLAN, and provider overlays reduce usable MTU. Test a real
  multi-container lab, not just `ping`.
- Document whether lab egress is NATed. If it is, ensure return traffic is
  symmetric and logged.
- Hairpin NAT is a common failure when a learner reaches a published port on the
  same host. Test it explicitly if the lab model requires it.
- Avoid double NAT between the gateway and lab node.

## Cross-site or cross-cloud nodes

Use a private overlay (WireGuard mesh, Tailscale, provider VPC peering, or a
private interconnect). Do not expose Docker bridges or the node-agent port to
the internet. If a node cannot reach the control plane over a private path, it
is not eligible for the pool.

## Network acceptance probes

From a learner session:

```bash
ip route
ping -c 1 <own-target>
ping -c 1 <other-session-target>      # must fail
ping -c 1 <management-host>            # must fail
```

From the gateway:

```bash
ip route get <active-session-cidr>
# must point at the owning node, not the default route
```

From the control plane:

```bash
curl --cacert ca.pem https://<node-underlay>:<agent-port>/health
```

Record the exact commands, source, destination, and result in the release
evidence.
