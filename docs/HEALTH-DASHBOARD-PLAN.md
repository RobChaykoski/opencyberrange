# Host health dashboard plan (`health.swocts.com`)

**Status:** the monitoring stack is now running on the independent OpenGRC
production host, not the development host. Grafana, Prometheus, Alertmanager,
Pushgateway, Blackbox, and the local node exporter are healthy, the provisioned
dashboard and Prometheus datasource are present, and all Prometheus targets are
up. The `health.swocts.com` DNS/NPM cutover to that host is the remaining step;
OIDC must be re-verified through the public hostname after the cutover.
**Hostname:** `health.swocts.com`.
**Owner:** platform operations.
**Release:** supports Release 6.2 (scale and availability). The dashboard is not a
Release 6.0 or 6.1 exit criterion.

This is the plan for a single health surface for every deployed system. It does
not replace the local monitor or the external dead-man switch; it consumes them.

## Why

The platform currently has a local sensor (`scripts/monitor-deployment.sh`) and
a generated public status page, but no central view. A host failure, a full
disk, a stopped backup, an expired certificate, or a dead lane in the lab pool
is found by a person. The dashboard should answer:

- Is each host up, and is it on the expected release?
- Are the containers, database, cache, reverse proxy, identity provider, and
  lab services healthy?
- Is the last backup recent, and did the last restore drill pass?
- Are certificates, DNS records, VPN peers, and lab capacity in policy?
- Which failures are already alerting, and who owns them?

## Scope

| Layer | Systems |
|---|---|
| Edge | `health.swocts.com`, Nginx Proxy Manager, Cloudflare DNS/DDNS, TLS certificates |
| Identity | Authentik, OIDC/SAML providers, break-glass path |
| Platform | Production and development OCR, backend, frontend, worker, scheduler |
| Data | PostgreSQL, Valkey, backup volume, offsite copy, restore-drill record |
| Curriculum | Workbook origin, MkDocs builds, lab catalogue freshness |
| Labs | Lab hosts, Docker capacity, RangeBox pool, image prebuild, orphan cleanup |
| Integrations | Moodle, CTFd, OpenGRC, OpenMetadata, DefectDojo, OpenSearch where deployed |
| Operations | Cron/systemd timers, disk, memory, NTP, certificate expiry, queue depth |

## Non-goals

- Not a GRC system of record. OpenGRC owns controls, evidence, risks, and
  approvals.
- Not a learner analytics product. No learner PII, names, emails, or session
  content.
- Not a replacement for the external dead-man switch. A dashboard on the same
  infrastructure cannot prove its own host is alive.
- Not a public status page by default. A read-only public page can be added
  later at a separate hostname if the institution wants one.

## Current scaffold

`deploy/monitoring/` contains a working Compose stack:

- Prometheus, Blackbox Exporter, Alertmanager, Pushgateway, and Grafana, pinned by digest.
- Provisioned Prometheus datasource and the `OCR health overview` dashboard.
- Example HTTP, node, and TCP target files.
- Alert rules for target down, scrape down, certificate expiry, disk, memory, backup age, and monitor heartbeat.
- Alertmanager route with a placeholder webhook.

It was brought up locally and verified: Prometheus ready, Grafana 12.1 healthy,
Alertmanager ready, dashboard provisioned, and the blackbox probe path returning
success against local test targets. The stack now runs on the independent OpenGRC
production host with Authentik OIDC, public probes, and production/development
API, wiki, and host targets. DNS and the reverse proxy still point
`health.swocts.com` at the previous host until the cutover is completed.

## Architecture

```text
hosts and services
  -> local agent / blackbox checks / pushed heartbeats
  -> monitoring host (not the platform host)
  -> health.swocts.com (Authentik OIDC, admin/viewer roles)
  -> alert routing (email, chat, on-call)
  -> external dead-man switch and uptime check for the dashboard itself
```

The monitoring host must be independent of the systems it observes. Running it
on the production platform recreates the blind spot the dashboard is meant to
remove.

### Stack decision, before build

| Option | Fit | Trade-off |
|---|---|---|
| Uptime Kuma + external heartbeat | Small, fast, HTTP/TCP/TLS checks | Limited host metrics and long-term history |
| Prometheus + Blackbox + node_exporter + Grafana | Host metrics, blackbox probes, alert rules, long retention | More moving parts and storage |
| Zabbix | Host and service monitoring with agents | Heavier operation and UI |

The recommended first build is **Prometheus + Blackbox Exporter +
node_exporter + Grafana**, with a separate external dead-man service. Uptime
Kuma is acceptable for a small single-campus deployment if host metrics are not
required.

## DNS and reverse proxy

- Create `health.swocts.com` as an `A`/`AAAA` record for the monitoring host.
- Default to **DNS only** and terminate TLS at Nginx Proxy Manager, matching
  the existing platform and wiki pattern.
- If Cloudflare proxy is enabled, configure an origin certificate and Full
  (strict); do not rely on the dashboard's own TLS for origin trust.
- Publish HSTS, `X-Content-Type-Options`, `Referrer-Policy`, and a restrictive
  `frame-ancestors` policy.
- Do not expose the metrics endpoints publicly. Only the authenticated
  dashboard and its health probe are public.
- Reserve `status.swocts.com` for an optional read-only public page; keep it
  separate from the administrative dashboard.

## Security

- Authentik OIDC only, with the platform-admin group for configuration. Add a
  dedicated read-only viewer group before sharing the dashboard.
- No local dashboard passwords. The break-glass path is the platform admin, not
  a shared monitoring account.
- Ingest uses a scoped token or mTLS; agents cannot read other agents' data.
- Do not put secrets, tokens, internal IPs, learner identifiers, or full
  hostnames in metric labels. Redact before storage.
- Rate-limit login and probe endpoints; log configuration changes.
- Retain raw metrics for a defined period (30 days is a reasonable default) and
  aggregate longer if needed. Backups of the monitoring data follow the same
  encryption rule as platform backups.
- The dashboard is a high-value target: it reveals topology and failure modes.
  Restrict it to staff, or to VPN/allowlisted networks if the institution
  prefers.

## Checks and acceptance criteria

| Check | Target | Alert |
|---|---|---|
| Public platform | `/api/version` and `/` on each environment | 2 failures |
| Workbook origin | `:8443/wiki/` | 2 failures |
| Identity provider | Authentik discovery and login page | 2 failures |
| TLS | Every public certificate | 14 days before expiry |
| Host | CPU, memory, disk, load, NTP | 5-minute threshold |
| Containers | Expected services running and healthy | 2 failures |
| Database | Connection, replication/lag where applicable, disk | 5 minutes |
| Backups | Local and offsite age, last restore drill | 26 hours / 35 days |
| Lab capacity | Running sessions, queue, orphaned containers | 10 minutes at cap |
| Dashboard itself | External uptime and dead-man switch | 2 failures / 10 minutes |

The build is not complete until a deliberately stopped host and a deliberately
stopped dashboard both page the on-call channel.

## Rollout

1. **Inventory and ownership.** List every system, its owner, its health signal,
   and the alert route. Exclude anything without an owner.
2. **External checks now.** Create the public uptime check and dead-man switch
   for the current production platform before the dashboard exists.
3. **Collectors.** Deploy node/blackbox checks on the monitoring host and
   read-only agents or push heartbeats on the observed hosts.
4. **Dashboard.** Publish `health.swocts.com` behind Authentik and NPM.
5. **Alerts and runbooks.** Route by severity; link each alert to the runbook
   section that resolves it.
6. **Failure tests.** Stop a host, stop the dashboard, expire a certificate in a
   test namespace, and age a backup. Verify the page.
7. **HA and retention.** Add a second monitoring node or an offsite replica only
   after the single-node version is trusted.

## Dependencies

- Integration work and Release 6 complete.
- DNS record and certificate for `health.swocts.com`.
- Authentik application and group mapping.
- A monitoring host independent of production.
- An alert channel with an owner and an escalation path.
- An external dead-man service account.

## Open decisions

- Prometheus/Grafana versus Uptime Kuma.
- Monitoring host location and whether it is also the NPM host.
- Retention period and backup encryption for monitoring data.
- Whether a public read-only status page is required.
- Which systems are in the first wave; not every integration needs a dashboard
  panel on day one.

## Related

- [Monitoring stack](../deploy/monitoring/README.md)
- [Operations monitoring and the external watchdog](OPERATIONS-MONITORING.md)
- [Deployment runbook](DEPLOYMENT-RUNBOOK.md)
- [Deployment status](status-dashboard.md)
- [Backup security](BACKUP-SECURITY.md)
- [Tenant isolation status](TENANT-ISOLATION-STATUS.md)
