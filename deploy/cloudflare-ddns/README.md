# Cloudflare dynamic DNS

The public SWOCTS hostnames depend on a firewall WAN address that can change
after a firewall reboot. This stack keeps the Cloudflare `A` records pointed at
the current public IPv4 address.

## Three supported approaches

### A. Firewall built-in DDNS (preferred)

If the firewall is OPNsense, pfSense, or another platform with a Cloudflare
DDNS client, configure it there first. It reacts directly to the WAN address
change and starts before the application containers.

Use the same scoped Cloudflare token and the same record list described below.

### B. Platform settings (single-host fallback)

When the OpenCyberRange host is the always-on machine behind the firewall, the
platform can run the update itself. In **Admin -> Settings -> Network**:

1. Create a dedicated Cloudflare token with `Zone:DNS:Edit` for one zone.
2. Set the zone, the explicit A records, the TTL, and the check interval.
3. Save the token and enable **Cloudflare Dynamic DNS**.
4. Use **Test without writing** to validate the token and current records, then
   **Check and update now** to apply the address.

The scheduler checks the public IPv4 through Cloudflare's trace endpoint and
refuses private or non-public addresses. It updates only records inside the
configured zone, refuses wildcards, and refuses a name with more than one A
record. The token is stored with the same encrypted secret handling as the SMTP
password and is never returned to the browser. Errors and the last address are
shown in the same panel.

This updater manages `A` records only. It does not replace a firewall DDNS
client, does not handle IPv6, and does not change NPM upstreams or certificates.

### C. This container (separate host)

Run this stack on an always-on host behind the firewall, preferably the Nginx
Proxy Manager host. It checks the public address every five minutes and after
every container restart, and only updates Cloudflare when the value changes.

Do not run this container and the platform updater against the same records.
Two writers produce confusing flap and make the last-change audit meaningless.

## Cloudflare token

Create a dedicated token, not a global API key:

1. Cloudflare dashboard -> My Profile -> API Tokens -> Create Token.
2. Use the **Edit zone DNS** template.
3. Zone Resources: include **only** `example.com`.
4. Permissions: `Zone -> DNS -> Edit`.
5. Copy the token once into `.env`. Do not paste it into chat, tickets, or the
   repository.

Recommended token name: `swocts-ddns-npm`.

Rotate the token after the event and record the change.

## Configure the container (approach C)

```bash
cd deploy/cloudflare-ddns
cp .env.example .env
chmod 600 .env
# set CLOUDFLARE_API_TOKEN and the exact DDNS_DOMAINS list
docker compose up -d
docker compose logs -f cloudflare-ddns
```

The default record list is:

```text
<moodle-host>,<platform-host>
```

Keep it explicit. Do not use `*.example.com` unless every record should follow
the firewall address.

## Proxied or DNS-only

- **DNS only (grey cloud), default:** `DDNS_PROXIED=false`. Nginx Proxy Manager
  terminates TLS and can keep using its Let's Encrypt certificate. This is the
  current deployment shape.
- **Cloudflare proxy (orange cloud):** `DDNS_PROXIED=true`. Cloudflare terminates
  public TLS; configure an origin certificate or Full (strict) to NPM. Do not
  enable the proxy without validating the origin certificate and the NPM proxy
  host.

For a DNS-only record, a TTL of 120-300 seconds keeps failover/refresh quick.
For a proxied record, Cloudflare manages the edge TTL.

## Verify

From an external resolver:

```bash
dig +short <moodle-host> @1.1.1.1
dig +short <platform-host> @1.1.1.1
```

Both should return the current public IPv4 address. Then check:

```bash
curl -sSI https://<moodle-host>/login/index.php
curl -sS https://<platform-host>/api/version
```

If the firewall IP changed and DNS is stale, check the updater logs first:

```bash
docker compose logs --tail=100 cloudflare-ddns
```

## Firewall reboot behaviour

- The container starts with the host and retries on its cron interval.
- If the WAN is not up yet, the first checks fail and later checks succeed.
- The firewall's built-in DDNS is still preferable because it runs on the
  device that owns the WAN address.
- After a reboot, verify both public hostnames and the NPM proxy hosts. A stale
  DNS record is the most likely cause of a sudden TLS or connection failure.

## Deployment status

Deployed on `<prod-host>` on 2026-11-20 and verified:

- `.env` is mode `600`, owned by the deploy user.
- The container is `running` with restart policy `unless-stopped`; Docker is
  enabled at boot.
- It detected WAN IPv4 `<public-ip>` and reported both records already current.
- A no-op DNS write returned `200`, confirming the token can edit records.
- Public resolvers return `<public-ip>` for both names.

```bash
cd ~/cloudflare-ddns
docker compose ps
docker compose logs --tail 30 --no-log-prefix
```

## Security

- Use a token scoped to `Zone:DNS:Edit` for `example.com` only. The current pilot
  token was supplied interactively and should be rotated after the event.
- `.env` is mode 600 and gitignored.
- The container drops capabilities and enables `no-new-privileges`.
- Do not run multiple updaters for the same records.
- After rotating the token, replace `CLOUDFLARE_API_TOKEN` in `.env` and run
  `docker compose up -d`; the records do not change.
- OpenBao should hold the token after the event; see
  [`docs/MOODLE-AUTHENTIK-AND-SECRETS-PLAN.md`](../../docs/MOODLE-AUTHENTIK-AND-SECRETS-PLAN.md).

## Current integration

The production pilot uses:

- NPM host: `<npm-host-ip>`
- NPM upstream for `<moodle-host>`: `<prod-host-ip>:8092`
- Production OCR: `https://<platform-host>`

The DDNS updater only changes public DNS. It does not change NPM upstreams,
Moodle, OpenCyberRange, or TLS certificates.
