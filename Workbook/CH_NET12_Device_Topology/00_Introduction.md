# Device Topology: Routed Path to a Protected Service

## Scenario

A small training network has three devices:

| Device | Role | Management address |
|---|---|---|
| `h1` | Learner workstation | shown in the exercise |
| `r1` | Linux router | shown in the exercise |
| `svc` | Protected HTTP service | shown in the exercise |

`h1` and `svc` are on different point-to-point links. Traffic between them has
to cross `r1`. Each link uses a private `/29` allocated when the lab starts, so
the addressing differs from session to session.

## Objectives

By the end of this chapter you can:

- map a routed topology from the node status endpoint;
- explain how a host default route selects a next hop;
- verify IPv4 forwarding on a Linux router;
- reach a protected service through the router rather than directly;
- explain why a routed segment is a control and monitoring point.

## Rules

- Use only the management addresses shown in the exercise.
- Do not change the router's forwarding setting or the link addressing.
- The flag is on the service node; reach it through the routed path.

## Labs in this chapter

| Lab | Focus | Time |
|---|---|---|
| 12.1 Routed Path | host → router → service; default route, forwarding, link evidence | 45 min |
| 12.2 Two-Router Transit | static routes and return paths across two routers | 60 min |
| 12.3 Firewall the Service Path | nftables forward policy on a routed segment | 50 min |
| 12.4 Multi-Service Router | three-link mapping and topology documentation | 70 min |

## The engine in one paragraph

The platform reads the lab's `x-ocr-topology` block, allocates a private `/29`
for each link, assigns the two endpoints, and starts a small reviewed node image
for each device. The image runs `sshd` for the training user, enables forwarding
on a router, installs a default route on a host, and serves `/flag` on a service.
The node status endpoint on port 8080 reports the role, links, peer addresses,
and gateway for that device.
