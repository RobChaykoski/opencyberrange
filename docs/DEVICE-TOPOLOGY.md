# Network device topology engine

Status: **Release 4.** The engine runs routers, hosts, and flag services as
reviewed containers. Switches are represented by the Docker L2 bridge that backs
each link; a dedicated switch container is not shipped yet.

## What it does

A lab declares a small topology in its Compose file. At spawn, the backend:

1. validates the topology against a strict schema;
2. allocates a private `/29` for each point-to-point link from the protected
   `10.128.0.0/9` range, unique per session;
3. assigns `.2` and `.3` to the two endpoints (`.1` is the bridge gateway);
4. attaches the services to their links and injects a JSON description of the
   node role, links, peer addresses, gateway, and routes;
5. enables IPv4 forwarding on a router, installs a default route on a host or
   service, and starts `sshd` plus a status endpoint on every node.

The engine never creates a privileged container, a host-network container, a
bind mount, or a container from an arbitrary image. A bad topology fails the
spawn before any container starts.

## Authoring

```yaml
x-ocr-topology:
  training_user: analyst
  training_password: "Topology2026"
  nodes:
    h1:
      service: h1
      role: host
    r1:
      service: r1
      role: router
    svc:
      service: svc
      role: service
      flag: "OCR{example}"
      http_port: 80
  links:
    - from: h1
      to: r1
    - from: r1
      to: svc
```

Each referenced service must:

- use `ocr-lab/topology-node:*`;
- set `labels.ip_offset`;
- keep `security_opt: [no-new-privileges:true]`;
- add only `NET_ADMIN` and `NET_RAW`;
- avoid `build`, `privileged`, `network_mode`, `pid`, `ipc`, `devices`, and
  `volumes`;
- keep `ocr_lab_net` enabled (the default);
- leave `OCR_*` environment variables to the engine.

## Node roles

| Role | Behaviour |
|---|---|
| `host` | Optional default route via a directly connected router; SSH and status |
| `router` | IPv4 forwarding, connected routes from its links, optional static routes |
| `service` | Host behaviour plus `GET /flag` on the HTTP port |

Every role exposes:

- `sshd` on port 22 for the training user;
- `GET /status` on port 8080 with `node`, `role`, `links`, `routes`, and
  `gateway`.

The status endpoint is the supported way for a learner or the test runner to
discover link addresses without guessing.

## Static routes

A router can add routes to a direct peer by node id:

```yaml
nodes:
  r1:
    service: r1
    role: router
    routes:
      - to: 10.20.20.0/24
        via: svc
```

The engine resolves `via` to the peer's link address. It does not accept an
arbitrary next hop that is not directly connected.

## Limits and safety

- Maximum 12 nodes and 24 links.
- Link subnets are `/29`, allocated from `10.128.0.0/9`, never `10.200.0.0/16`.
- The node image is reviewed and built by `scripts/prebuild-labs.sh`; it is not
  built at spawn time in production. Its Dockerfile and entrypoint are covered by
  the signed supply-chain lock, and a CycloneDX SBOM is committed at
  `platform/backend/app/data/about/sbom/topology-node.cdx.json`.
- Nodes run as root inside their container because `sshd`, `chpasswd`, and
  interface changes require it. They have no host mounts, no Docker socket, no
  host network, and only `NET_ADMIN`/`NET_RAW`.
- The management IP stays on the per-session `/24`; topology links are additional
  networks. The learner reaches the management IP; the link path is the exercise.
- A switch is a Docker bridge, not a device. The topology is routed (L3), not a
  vendor NOS.

## Demo labs

`platform/labs/Network/`:

- `network-12-2-device-topology-engine` — host → router → service; routed path.
- `network-12-3-two-router-transit` — two routers, transit and return routes.
- `network-12-4-firewall-service-path` — nftables forward policy on the router.
- `network-12-5-multi-service-router` — three-link mapping and documentation.

The workbook at `Workbook/CH_NET12_Device_Topology/` covers all four exercises,
from the status endpoint and default route through transit routes, forward
policy, and topology documentation.

## Tests

- Unit: `platform/backend/tests/test_topology_engine.py` (18 cases) — allocation,
  gateway, role mapping, route resolution, subnet bounds, and every rejected
  unsafe service shape.
- Static: `scripts/validate-lab.py` accepts image-only topology labs while still
  checking metadata, flags, and test steps.
- Live dev: the lab spawned as `h1`, `r1`, and `svc`; `h1` had a default route
  via `r1`, `r1` reported forwarding `1`, and `h1` fetched
  `OCR{t0p0l0gy_r0ut3d}` from the service link address.

## Not shipped

- A switch container with a multi-port bridge and one broadcast domain.
- FRRouting/OSPF/BGP configuration.
- Firewall (nftables) policy as a first-class node role.
- Deep Linking or LTI integration for topology labs.

Those are Release 5 candidates; the current engine is a routed L3 topology with
Docker bridges as L2 segments.
