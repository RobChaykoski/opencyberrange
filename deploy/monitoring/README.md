# Monitoring instance for `health.swocts.com`

A separate Docker Compose stack for the central health dashboard. It runs on an
independent monitoring host, not on the production platform host.

The stack is Prometheus, Blackbox Exporter, Alertmanager, Pushgateway, Grafana,
and a local `node_exporter`. It is intentionally separate from the platform
Compose project so a platform outage does not take the dashboard with it.

## What it monitors

- Public HTTPS endpoints and redirects.
- TLS certificate expiry.
- TCP services on a private management network.
- Host CPU, memory, disk, and uptime through `node_exporter`.
- Push-based backup and local-monitor heartbeats.
- Prometheus scrape targets.

The target files contain placeholder hosts only. Replace them with the
institution's public service URLs, host addresses, and private management
addresses. Do not use a wildcard.

## Before DNS

The stack is ready to run on localhost. To test it under `health.swocts.com`,
create DNS pointing at the monitoring host, then create an NPM proxy host:

| NPM field | Value |
|---|---|
| Domain | `health.swocts.com` |
| Scheme | `http` |
| Forward hostname | monitoring host address |
| Forward port | `3000` |
| Websockets | on |
| Block common exploits | on |
| Access list | staff only or VPN/allowlist |

Use DNS-only at Cloudflare and terminate TLS at NPM, matching the platform and
wiki pattern. If you enable the Cloudflare proxy, use an origin certificate and
Full (strict).

Only Grafana is published. Prometheus, Alertmanager, Pushgateway, and
`node_exporter` bind to `127.0.0.1` on the monitoring host.

## Authentik OIDC

Create an Authentik OIDC application:

- Redirect URI: `https://health.swocts.com/login/generic_oauth`
- Scopes: `openid profile email`
- Groups: `ops-admin` for configuration, `ops-viewer` for read-only

Put the client ID and secret in `.env`. Keep the local Grafana admin enabled
until OIDC works, then set `GRAFANA_DISABLE_LOGIN_FORM=true`. Keep the bootstrap
password in the institutional password manager.

Grafana does not map Authentik groups to Grafana roles automatically unless the
role attribute path matches. Verify one admin and one viewer account before the
dashboard is trusted.

## Start

```bash
cd deploy/monitoring
cp .env.example .env
chmod 600 .env
# set the Grafana admin password and Authentik OIDC values
docker compose up -d
docker compose ps
```

Validate locally:

```bash
curl -fsS http://127.0.0.1:9090/-/ready
curl -fsS http://127.0.0.1:3000/api/health
curl -fsS http://127.0.0.1:9093/-/ready
```

Grafana is at `http://127.0.0.1:3000` until NPM publishes it.

The Prometheus and Grafana containers run as non-root users. On hosts with a
shared umask, make the read-only config trees world-readable:

```bash
chmod -R a+rX prometheus alertmanager blackbox grafana
```

Do not make `.env` world-readable.

If NPM runs on another host, set `GRAFANA_BIND` to the monitoring host's private
address (or `0.0.0.0` behind a firewall that allows only NPM). Keep
`127.0.0.1` when NPM is on the same host.

## Add hosts

On each Linux host, run the agent in [`agent/`](agent/README.md). It exposes
`node_exporter` on a private management address. Allow only the monitoring host
to reach port 9100, then add the address to `prometheus/targets/nodes.yml` and
reload:

```bash
curl -X POST http://127.0.0.1:9090/-/reload
```

For a Windows host, use `windows_exporter` and add a dedicated scrape job; do
not expose it publicly.

## Add HTTP and TCP checks

- `prometheus/targets/http.yml`: public HTTPS URLs.
- `prometheus/targets/http-insecure.yml`: self-signed or lab endpoints.
- `prometheus/targets/tcp.yml`: database, cache, VPN, and other private ports.

Every target needs `environment`, `service`, and `owner` labels. Do not put
secrets, learner identifiers, or internal IPs in labels.

## Backup and heartbeat metrics

Push these after the corresponding job succeeds:

```text
ocr_backup_last_success_timestamp_seconds
ocr_monitor_heartbeat_timestamp_seconds
```

Use Pushgateway on `127.0.0.1:9091`. The alert rules treat a missing or stale
metric as a failure. Do not push a success from a script that did not actually
verify the work.

## Alerts

Edit `alertmanager/alertmanager.yml` with the institutional webhook or relay.
The repository contains a placeholder, not a live URL. Alert routing:

- Critical: public endpoint down, TLS within 14 days, backup older than 26 hours,
  monitor heartbeat missing.
- Warning: disk below 15%, memory above 90%.

Test the path by stopping one target and confirming a page. A dashboard that
has never alerted is an assumption.

## External watchdog

The dashboard cannot detect its own host failure. Configure an external uptime
check for `https://health.swocts.com/api/health` and a dead-man switch that pages
when Prometheus or Alertmanager stops reporting. Keep that provider outside this
stack.

## Security

- No public metrics endpoints. Only Grafana is published.
- No secrets in the repository; `.env` is mode 600 and gitignored.
- No learner data. Health checks read status endpoints and host metrics only.
- Retain raw metrics for 30 days; back up the Prometheus and Grafana volumes
  with the same encryption rule as platform backups.
- Review the target list quarterly. A stale target produces noise, not coverage.

## Relation to Release 6

This stack supports the Release 6 scale and availability workstream: it is the
single pane for the platform, identity, edge, data, and lab hosts during the HA
and disaster-recovery drills. It does not replace OpenGRC, which remains the
system of record for controls and evidence.

See [Host health dashboard plan](../../docs/HEALTH-DASHBOARD-PLAN.md) and
[Operations monitoring](../../docs/OPERATIONS-MONITORING.md).
