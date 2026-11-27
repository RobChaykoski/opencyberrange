# Network and ports

## Public ports

| Port | Protocol | Service | Required |
|---|---|---|---|
| 80 | TCP | nginx HTTP bootstrap / redirect | yes |
| 443 | TCP | nginx HTTPS, SPA, `/api`, `/wiki` | yes |
| 8443 | TCP | separate workbook origin | only if the split origin is enabled |
| 51820 | UDP | WireGuard | only if the built-in VPN is used |
| 5555 | TCP | optional wstunnel browser terminal | only when deliberately enabled |

## Private services

| Port | Service | Reachable from |
|---|---|---|
| 8000 | FastAPI | host loopback only (`127.0.0.1:8000`) |
| 5432 | PostgreSQL | Compose network only |
| 6379 | Valkey | Compose network only |
| 2375 | Docker socket proxy | `docker_control` network only |
| 6080 | RangeBox VNC | proxied by the backend; not published |
| 5556 | Dex (optional SSO test stack) | Compose network only |
| 389 | OpenLDAP (optional SSO test stack) | Compose network only |

Never publish 5432, 6379, or 2375. A learner must not reach the management
network, another learner's lab, or the Docker socket.

## Trusted proxy headers

The backend runs Uvicorn with:

```text
--proxy-headers --forwarded-allow-ips "${FORWARDED_ALLOW_IPS:-127.0.0.1,172.16.0.0/12}"
```

Only nginx (and the loopback tunnel used by tests) may set
`X-Forwarded-For`. Do not add lab ranges to `FORWARDED_ALLOW_IPS`; a lab
container must not be able to spoof a client address. This is why the blackbox
Karate suite can use `X-Forwarded-For` only when it reaches the backend through
an SSH tunnel to loopback.

## TLS

The frontend entrypoint uses:

```text
platform/certs/selfsigned.crt
platform/certs/selfsigned.key
```

If both exist, nginx serves HTTPS on 443. Without them it serves HTTP on 80.
For a public deployment, use a trusted certificate or terminate TLS at a
reverse proxy. The certificate SAN must include the exact hostname or IP
learners use.

## DNS and public origin

| Variable | Meaning |
|---|---|
| `SERVER_PUBLIC_HOST` | Address learners type in the browser |
| `PUBLIC_BASE_URL` | Stable external origin for SSO callback and ACS URLs |
| `FRONTEND_BASE_URL` | Optional frontend origin override |
| `CORS_ORIGINS` | Comma-separated browser origins allowed to call the API |
| `WIKI_BASE_URL` | Optional separate wiki origin |
| `WIKI_COOKIE_DOMAIN` | Parent-domain scope for the HttpOnly wiki cookie |

Set `PUBLIC_BASE_URL` before configuring an identity provider. Changing it
later invalidates callback URLs registered at the IdP.

## Compose networks

| Network | Members | Purpose |
|---|---|---|
| default | frontend, backend, db, valkey | private application traffic |
| `docker_control` | backend, docker-socket-proxy | Docker API; internal only |
| per-session lab bridge | lab targets, RangeBox | `10.100.x.0/24`, isolated per learner |
| standalone RangeBox bridge | RangeBox tab | `10.50.x.0/24` |

## VPN

- The learner gets a `/32` in `10.255.x.y`.
- The peer routes only the learner's lab `/24` from `10.100.0.0/16`.
- The Peer Manager applies and persists firewall rules.
- Use `WG_NETWORK_BASE` and `WG_CLIENT_BASE` to avoid collisions with common
  home networks.
- Verify with `scripts/verify_vpn_routes.py` and the admin VPN page.

## Firewall rules of thumb

- Allow inbound 80/443 from learners.
- Allow 8443 only when the split wiki origin is enabled.
- Allow 51820/UDP only when VPN is enabled.
- Allow SSH only from the management network.
- Deny inbound to 8000, 5432, 6379, and 2375.
- Allow outbound only to what the deployment needs: image registries, package
  mirrors, the identity provider, and the monitoring endpoint.

## Related

- [Reverse proxy](../../docs/REVERSE-PROXY.md)
- [Network sandbox](../../docs/NETWORK-SANDBOX.md)
- [Device topology](../../docs/DEVICE-TOPOLOGY.md)
- [Security events](../../docs/SECURITY-EVENTS.md)
