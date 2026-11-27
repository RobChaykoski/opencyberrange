# Lab runtime technical architecture

```mermaid
flowchart TB
    subgraph API["ocr-backend"]
        Route["labs / rangebox routers"]
        Pre["lab_preflight<br/>capacity + image checks"]
        Orch["docker_manager<br/>compose project"]
        Sched["scheduler<br/>expiry + cleanup"]
        Peer["wireguard_manager"]
    end

    subgraph Control["Docker control"]
        Proxy["docker-socket-proxy"]
        Engine["Docker Engine"]
    end

    subgraph Session["Per-session network 10.100.x.0/24"]
        Target["lab target containers"]
        Topo["topology nodes"]
        Box["RangeBox desktop"]
        Solver["tester sidecar (acceptance only)"]
    end

    subgraph Access["Learner access"]
        VPN["WireGuard peer /32"]
        VNC["noVNC through backend"]
    end

    Route --> Pre --> Orch
    Orch --> Proxy --> Engine
    Engine --> Session
    Sched --> Orch
    Route --> Peer --> VPN
    VPN -->|only this /24| Session
    Route --> VNC --> Box
    Solver --> Target
```

## Start sequence

1. Authorize the learner and the lab.
2. Check image presence, session quota, host capacity, and RangeBox capacity.
3. Allocate the next `/24`.
4. Create the Compose project and network.
5. Start services; wait for declared TCP/UDP ports.
6. Start RangeBox and wait for 6080 if requested.
7. Create the VPN peer and firewall rule.
8. Mark the session ready.

## Stop sequence

1. Mark the session stopping.
2. `docker compose down -v --remove-orphans` for the project.
3. Remove the per-session network.
4. Revoke the peer and firewall rule.
5. Record the closure and free the address.

Every failure path runs the stop sequence. A leaked network or peer is a defect.

## Resource model

| Resource | Source |
|---|---|
| Memory / CPU | compose `mem_limit` and `cpus`, reflected in the manifest |
| Session count | backend quota and host capacity |
| RangeBox count | `MAX_CONCURRENT_RANGEBOXES`, CPU reserve, free disk |
| Disk | image store plus per-session writable layers |
| Network | one `/24` per session |

## Related

- [Lab runtime overview](subsystem-overview.md)
- [Tester](tester/README.md)
- [RangeBox](rangebox/README.md)
- [Docker proxy](../docker-proxy/subsystem-overview.md)
- [VPN network rules](../deployment/network-and-ports.md)
