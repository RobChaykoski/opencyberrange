# Cloudflare dynamic DNS

The public SWOCTS hostnames depend on a firewall WAN address that can change
after a firewall reboot. This stack keeps the Cloudflare `A` records pointed at
the current public IPv4 address.

## Two supported approaches

### A. Firewall built-in DDNS (preferred)

If the firewall is OPNsense, pfSense, or another platform with a Cloudflare
DDNS client, configure it there first. It reacts directly to the WAN address
change and starts before the application containers.

Use the same scoped Cloudflare token and the same record list described below.

### B. This container (portable fallback)

Run this stack on an always-on host behind the firewall, preferably the Nginx
Proxy Manager host. It checks the public address every five minutes and after
every container restart, and only updates Cloudflare when the value changes.

## Cloudflare token

Create a dedicated token, not a global API key:

1. Cloudflare dashboard -> My Profile -> API Tokens -> Create Token.
2. Use the **Edit zone DNS** template.
3. Zone Resources: include **only** `swocts.com`.
4. Permissions: `Zone -> DNS -> Edit`.
5. Copy the token once into `.env`. Do not paste it into chat, tickets, or the
   repository.

Recommended token name: `swocts-ddns-npm`.

Rotate the token after the event and record the change.

## Configure

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
moodle.swocts.com,ctfd.swocts.com
```

Keep it explicit. Do not use `*.swocts.com` unless every record should follow
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
dig +short moodle.swocts.com @1.1.1.1
dig +short ctfd.swocts.com @1.1.1.1
```

Both should return the current public IPv4 address. Then check:

```bash
curl -sSI https://moodle.swocts.com/login/index.php
curl -sS https://ctfd.swocts.com/api/version
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

Deployed on `ocr-prod` on 2026-11-20 and verified:

- `.env` is mode `600`, owned by the deploy user.
- The container is `running` with restart policy `unless-stopped`; Docker is
  enabled at boot.
- It detected WAN IPv4 `70.54.16.7` and reported both records already current.
- A no-op DNS write returned `200`, confirming the token can edit records.
- Public resolvers return `70.54.16.7` for both names.

```bash
cd ~/cloudflare-ddns
docker compose ps
docker compose logs --tail 30 --no-log-prefix
```

## Security

- Use a token scoped to `Zone:DNS:Edit` for `swocts.com` only. The current pilot
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

- NPM host: `172.16.16.11`
- NPM upstream for `moodle.swocts.com`: `172.16.16.41:8092`
- Production OCR: `https://ctfd.swocts.com`

The DDNS updater only changes public DNS. It does not change NPM upstreams,
Moodle, OpenCyberRange, or TLS certificates.
