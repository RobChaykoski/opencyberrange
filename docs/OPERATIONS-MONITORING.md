# Operations monitoring and the external watchdog

The local monitor is a sensor. It cannot be the authority: if the host dies, the
disk fills, or Docker stops, the script that would notice is on the same host.
Production needs an external check that alerts when the platform or the local
monitor stops reporting.

## Architecture

```text
external uptime monitor  --->  https://<platform-host>/api/version
        |                              (public path, 443)
        |
external dead-man switch <---  scripts/monitor-deployment.sh (every 5 min)
                                       |
                                       +--> container, disk, backup, certificate,
                                            workbook 8443, offsite backup checks
                                       |
                                       +--> ALERT_WEBHOOK_URL on failure
```

- The **external uptime monitor** owns the "is the public site reachable?"
  question. It runs outside the host and survives a host failure.
- The **external dead-man switch** owns the "is the local monitor still
  running?" question. The local script pings it on success; a missed ping pages.
- The **local monitor** owns the deep checks that need host access: containers,
  disk, certificate expiry, backup age, offsite backup age.

## Central dashboard (`health.swocts.com`)

The central dashboard runs the separate stack in
[`deploy/monitoring/`](../deploy/monitoring/README.md) on the independent OpenGRC
production host. Grafana, Prometheus, Alertmanager, Pushgateway, Blackbox, and
node-exporter are healthy, the dashboard and datasource are provisioned, and all
Prometheus targets are up. Internal DNS and NPM forward `health.swocts.com` to
that host with Authentik OIDC; the previous development-host stack is stopped
with its volumes retained for rollback. The public Cloudflare A record still
points at the edge firewall; remove it for internal-only access or forward it
through NPM for public access.

It is a convenience and correlation layer, not a replacement for this page:

- The dashboard must run on a host independent of the systems it monitors.
- The external uptime check and dead-man switch still run outside that host.
- The dashboard must never be the only thing that notices a stopped monitor.

See [Host health dashboard plan](HEALTH-DASHBOARD-PLAN.md) for scope, security,
rollout, and acceptance criteria.

## External checks to create

| Check | Target | Interval | Alert after |
|---|---|---|---|
| Public platform | `https://<platform-host>/api/version` | 1 minute | 2 failures |
| Public TLS | Certificate on `https://<platform-host>` | 1 day | 14 days before expiry |
| Workbook origin (if public) | `https://<platform-host>:8443/wiki/` | 5 minutes | 2 failures |
| Local monitor heartbeat | Healthchecks.io or equivalent ping URL | 5 minutes | 10 minutes without a ping |
| Backup freshness | The dead-man payload, or the monitor's `backup-age` issue | 5 minutes | 26 hours |

Use a provider that supports a **dead-man switch** (Healthchecks.io, Better
Stack, or an equivalent). A simple uptime check cannot detect a host that is up
but whose monitor stopped.

## Install the local monitor

1. Create the root-only environment file:

   ```bash
   sudo install -d -m 700 /etc/opencyberrange
   sudo sh -c 'umask 077; cat > /etc/opencyberrange/monitor.env' <<'EOF'
   HEARTBEAT_URL=https://hc-ping.com/<uuid>
   HEARTBEAT_FAIL_URL=https://hc-ping.com/<uuid>/fail
   ALERT_WEBHOOK_URL=https://hooks.example.com/services/<redacted>
   DISK_MIN_GB=10
   BACKUP_MAX_HOURS=26
   EOF
   ```

   The heartbeat URL is a secret in practice: anyone with it can fake a healthy
   ping. Keep it root-only.

2. Adjust the checkout path in the systemd unit if it is not
   `/home/ocr/opencyberrange`.

3. Install and enable the timer:

   ```bash
   sudo cp deploy/systemd/ocr-monitor.service \
           deploy/systemd/ocr-monitor.timer \
           /etc/systemd/system/
   sudo systemctl daemon-reload
   sudo systemctl enable --now ocr-monitor.timer
   systemctl list-timers ocr-monitor.timer
   ```

4. Run once and read the status:

   ```bash
   sudo systemctl start ocr-monitor.service
   cat ~/.local/state/ocr-monitor/status.json
   ```

## Test the watchdog before release

1. **API failure.** Stop the backend (`docker stop ocr-backend`), run the monitor,
   confirm the webhook alert. Start the backend.
2. **Disk failure.** Temporarily set `DISK_MIN_GB` above the free space and run
   the monitor; confirm the alert. Restore the value.
3. **Dead-man switch.** Stop `ocr-monitor.timer` for longer than the grace
   period. Confirm the external service pages. Re-enable the timer.
4. **Host failure.** In a maintenance window, power off a lab host and confirm
   the external uptime check and the dead-man switch page independently.

Do not skip the third and fourth tests. A watchdog that has never failed is an
assumption.

## Failure routing

- **Page** the on-call operator for public 443, the dead-man switch, disk
  below threshold, or a backup older than 26 hours.
- **Ticket** a certificate expiring within 30 days.
- **Ticket** a workbook-origin failure unless the deployment has made it
  non-public.
- **Maintenance window:** pause the external checks or extend the grace period;
  do not disable the local monitor. Record the window and the owner.

## What not to do

- Do not rely on the admin dashboard or `monitor-deployment.sh` alone. Both run
  on the host they observe.
- Do not put the heartbeat URL in a public repository or a screenshot.
- Do not use the same alert channel for a failed login test and a production
  outage; route test alerts to a separate channel.
- Do not let a noisy check page every minute. Page on a sustained failure and
  use a ticket for a warning.

## Related

- `scripts/monitor-deployment.sh`
- `deploy/systemd/ocr-monitor.service` and `.timer`
- [Deployment runbook](DEPLOYMENT-RUNBOOK.md)
- [Backup security](BACKUP-SECURITY.md)
