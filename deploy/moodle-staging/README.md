# Staging Moodle for `<moodle-host>`

This is a separate, internet-facing **staging** Moodle for demonstrating the
OpenCyberRange LTI 1.3 integration. It is not the disposable training lab and
must never be connected to OpenCyberRange production
(`https://<platform-host>`) or a production identity provider.

Use fake courses, fake learners, and fake evidence only.

> **Placeholders.** `<moodle-host>`, `<prod-host-ip>`, and `<npm-host-ip>` are
> intentionally generic. Take the real values from the private deployment
> inventory and never commit them.

## Shape

```text
Internet
  -> Caddy :443 (automatic TLS, security headers)
  -> Moodle :8080 (loopback debug port only)
  -> MariaDB (private compose network)
```

The stack has its own project name and volumes. It does not share the training
stack's database, volumes, or `.env`.

## Prerequisites

- DNS `A`/`AAAA` record for `<moodle-host>` pointing at the staging host.
- Inbound TCP 80 and 443 to that host, so Caddy can obtain and renew the
  certificate. If another proxy terminates TLS, put this stack behind it and
  adjust the Caddy/port mapping.
- Docker Engine with Compose v2.
- Strong unique passwords. Do not reuse training-lab or production secrets.

## Start

```bash
cd deploy/moodle-staging
cp .env.example .env
# edit every placeholder, including MOODLE_ADMIN_PASSWORD and database secrets
# optionally add a demo-only TRAINING_PASSWORD
docker compose up -d
docker compose logs -f caddy
docker compose exec -T -u daemon moodle php /harden.php
```

Open `https://<moodle-host>/login/index.php`.

The hardening step disables self-registration, guest access, and debug output,
sets a strong password policy, makes session cookies HTTPS-only, and keeps
profiles minimal.

Moodle runs with `sslproxy=yes` and `reverseproxy=no` because Caddy preserves the
public Host header. Do not switch `reverseproxy` back on unless the proxy is
changed to forward the internal host name instead.

## Validate

```bash
curl -sSI https://<moodle-host>/login/index.php
# expect HTTP/2 200, HSTS, X-Content-Type-Options, Referrer-Policy

curl -s https://<moodle-host>/login/index.php | grep -i 'create new account'
# expect no match

docker compose exec -T moodle php /admin/cli/cfg.php --name=registerauth
# expect an empty value
```

Log in once as the administrator and once as `student01` using the passwords in
`.env`. Then remove or rotate the staging credentials you no longer need.

## Seed fake demo data

```bash
cd deploy/moodle-staging
bash seed_staging.sh
```

The script refuses the training default password and the production
OpenCyberRange hostname. It creates the same synthetic Moodle courses and users
as the training lab, using the `TRAINING_PASSWORD` from `.env`.

Do not add real learner records, production SSO, production SMTP, or production
API tokens.

## LTI integration

Register this Moodle only against a **staging** OpenCyberRange instance. Do not
register it in `<platform-host>`.

Use the seed from the repository root with the staging containers and URLs, for
example:

```bash
MOODLE_CONTAINER=moodle-staging-moodle-1 \
OCR_CONTAINER=<staging-ocr-backend-container> \
MOODLE_ISSUER=https://<moodle-host> \
MOODLE_INTERNAL_URL=https://<moodle-host> \
OCR_PUBLIC_URL=https://<staging-ocr-host> \
OCR_INTERNAL_URL=https://<staging-ocr-host> \
bash scripts/ecosystem_seed/seed_lti.sh
```

The seed creates the Moodle 5 course tool, the demo activity, the platform
registration, and a tool RSA key. It prints the `client_id` and
`deployment_id` it used.

If the staging OpenCyberRange is behind a private address, set
`OCR_INTERNAL_URL` so the Moodle container can reach its JWKS endpoint while the
browser uses `OCR_PUBLIC_URL`.

## Behind Nginx Proxy Manager

The current staging deployment terminates TLS at Nginx Proxy Manager and
forwards plain HTTP to the staging Moodle:

| NPM setting | Value |
|---|---|
| Domain | `<moodle-host>` |
| Scheme | `http` |
| Forward host | `<staging-host-ip>` |
| Forward port | `8092` |
| Preserve Host header | enabled |
| Websockets | not required |
| SSL | Let's Encrypt, Force SSL |

Do not use an `https` upstream and do not point the proxy back at
`<moodle-host>`; both cause timeouts or a loop.

Restrict direct access to the upstream port to the NPM host if the network
allows it. On a Windows staging host:

```powershell
New-NetFirewallRule -DisplayName "Moodle staging from NPM" `
  -Direction Inbound -Protocol TCP -LocalPort 8092 `
  -RemoteAddress <npm-host-ip> -Action Allow
```

Add HSTS in the NPM proxy host's advanced configuration:

```nginx
add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;
```

## Local preview

Use the local override on a workstation only:

```bash
docker compose -f docker-compose.yml -f docker-compose.local.yml up -d
```

Then open `https://localhost:9444`. Caddy uses its internal CA, so the browser
will warn until you trust it. The direct Moodle debug port stays on
`127.0.0.1:8092`.

Tear the preview down with:

```bash
docker compose -f docker-compose.yml -f docker-compose.local.yml down -v
```

## Operations

- Back up the MariaDB volume and the Moodle data volumes before changes.
- Pin `STAGING_MOODLE_IMAGE` and `STAGING_MARIADB_IMAGE` to tested tags.
- Keep the admin UI behind the institution's access control (VPN, IP allowlist,
  or an identity-aware proxy) if the event does not need public access.
- Review Moodle and Caddy logs after the event.
- Remove test accounts, courses, and LTI platform registrations when finished.
- Keep `/etc/nginx`-style security headers and TLS termination at Caddy or the
  upstream proxy.

## Explicitly out of scope

- Production OpenCyberRange at `<platform-host>`.
- Production SSO, SMTP, API tokens, or database dumps.
- Real learner, staff, or institutional data.
- Using the training-lab default password on the public hostname.
