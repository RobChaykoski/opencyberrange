# Northwind Freight - WebSocket C2 Tunnel

Intermediate traffic-analysis lab. A synthetic workstation beacons through a
`wstunnel` WebSocket relay to a tasking server that has no address on the lab
network. The student captures the relay half of the session from the network tap
and recovers the task key from the tunneled payload.

## Layout

```
network-2-6-wstunnel-c2-tunneling/
├── docker-compose.yml
├── lab.yaml
├── README.md
└── containers/
    ├── relay/
    │   ├── Dockerfile
    │   └── entrypoint.sh
    ├── victim/
    │   ├── Dockerfile
    │   ├── entrypoint.sh
    │   └── beacon.sh
    └── beacon/
        └── tasking.json
```

## How it works

`c2-relay` runs `wstunnel server --restrict-to beacon:80` on TCP 8080. It is
the only service on the student lab network that participates in the tunnel.

`victim` runs `wstunnel client -L tcp://127.0.0.1:9000:beacon:80` and a beacon
loop that requests `http://127.0.0.1:9000/tasking.json` every four seconds. The
client forwards that local port through the WebSocket to the relay, and the
relay opens the real connection to `beacon`.

`beacon` serves `tasking.json` from nginx. It is labelled `ocr_lab_net: "false"`
and joins only the `internal` network, so the platform never attaches it to the
student lab bridge and students cannot reach it directly.

`x-ocr-network-tap: true` makes the platform spawn `ocr-network-tap` at `.253`.
The tap mirrors every lab container's traffic and streams PCAP on TCP 9999. The
student connects with:

```bash
timeout 30 nc network-tap 9999 > /tmp/tunnel.pcap
```

The relay-to-beacon leg is on the internal network and is not mirrored, so the
capture contains the WebSocket session, not the plain HTTP to the tasking
server.

Both custom images download the pinned `wstunnel` release and verify the
tarball SHA256 (the same version and checksums as `scripts/setup-wstunnel.sh`)
before extracting the binary.

## Flag

`OCR{w3bs0ck3t_c2_tunn3l_d3t3ct3d}` appears in the tasking JSON response and is
visible inside the WebSocket frames in the capture.

## Validation

```bash
python scripts/validate-lab.py platform/labs/Network/network-2-6-wstunnel-c2-tunneling
```

Manual smoke test (without the platform, so no tap):

```bash
cd platform/labs/Network/network-2-6-wstunnel-c2-tunneling
docker compose up -d --build
docker compose exec victim curl -s http://127.0.0.1:9000/tasking.json
docker compose down -v
```

The expected response contains the `task_key` above.
