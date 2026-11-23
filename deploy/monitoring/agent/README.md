# Monitoring agent for one host

This is the per-host half of the `health.swocts.com` stack. It runs
`node_exporter`, which the central Prometheus instance scrapes over a private
management network.

Do not run this on Windows hosts. Use `windows_exporter` there and add a
separate scrape job; do not expose it publicly.

## Install

On each Linux host:

```bash
cd deploy/monitoring/agent
cp .env.example .env
chmod 600 .env
# set NODE_EXPORTER_BIND to a private management address on this host
docker compose up -d
```

The container needs `pid: host` and a read-only `/` mount to report host
metrics. The `rslave` propagation requires a Linux host; Docker Desktop on
Windows or macOS does not provide a real host root and is not supported for this
agent.

## Firewall

Allow the monitoring host to reach port `9100` on the private address. Deny
everyone else. Do not expose `9100` through Nginx Proxy Manager, Cloudflare, or a
public firewall rule.

Example with nftables:

```bash
nft add rule inet filter input ip saddr <monitoring-host> tcp dport 9100 accept
nft add rule inet filter input tcp dport 9100 drop
```

Use the institution's own firewall management, not ad-hoc rules that disappear
after a reboot.

## Register the host centrally

On the monitoring host, add the address to
`prometheus/targets/nodes.yml`:

```yaml
- targets:
    - <host-private-address>:9100
  labels:
    environment: production
    host: <short-host-label>
    owner: <team>
```

Reload Prometheus:

```bash
curl -X POST http://127.0.0.1:9090/-/reload
```

## Verify

From the monitoring host:

```bash
curl -fsS http://<host-private-address>:9100/metrics | head
```

Then check the target in Prometheus:

```bash
curl -fsS 'http://127.0.0.1:9090/api/v1/targets?state=active' \
  | grep -o '<host-private-address>:9100'
```

## Upgrade

The image is pinned by digest. To rotate it, update the compose file in a
reviewed change, then:

```bash
docker compose pull
docker compose up -d
```

Do not use `latest`.
