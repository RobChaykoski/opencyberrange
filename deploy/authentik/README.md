# Production Authentik

Authentik is the production identity provider for the SWOCTS Cyber Range. It
runs on the production host with its own PostgreSQL and Redis, behind Nginx
Proxy Manager at `https://<auth-host>`.

The development `deploy/ecosystem-test` stack keeps its own disposable
Authentik. Do not point the production platform at the test IdP and do not copy
production data into the test stack.

> **Placeholders.** `<auth-host>`, `<public-ip>`, `<npm-host-ip>`, and
> `<prod-host-ip>` are intentionally generic. Take the real values from the
> private deployment inventory and never commit them.

## Network path

```text
Browser
  -> https://<auth-host> (public DNS, <public-ip>)
  -> Nginx Proxy Manager <npm-host-ip>:443
  -> production host <prod-host-ip>:9000
  -> authentik-server
  -> postgresql / redis (private Compose network)
```

Required before the first browser login:

1. Public DNS `A <auth-host> -> <public-ip>` (DNS only, not proxied).
2. NPM proxy host `<auth-host>`:
   - Scheme `http`
   - Forward host `<prod-host-ip>`
   - Forward port `9000`
   - Websockets enabled
   - Preserve Host header enabled
   - SSL: Let's Encrypt, Force SSL, HSTS
3. Firewall rule allowing `<npm-host-ip>` to `<prod-host-ip>:9000` only. Do not
   publish port 9000 to the internet.

## Install on the production host

```bash
mkdir -p ~/authentik
cd ~/authentik
# Copy docker-compose.yml and create .env with mode 600.
cp deploy/authentik/docker-compose.yml .
cp deploy/authentik/.env.example .env
chmod 600 .env
# Fill every value in .env with a generated secret. Do not commit it.
docker compose up -d
docker compose ps
```

The bootstrap environment creates the initial `akadmin` account and an API
token. Keep `.env` mode 600 and do not paste its contents into chat, tickets, or
logs.

## First login and hardening

1. Sign in at `https://<auth-host>/if/admin/` as the bootstrap
   administrator.
2. Change the bootstrap password.
3. Enable MFA for the administrator and every staff account.
4. Create groups:
   - `swocts-learners`
   - `swocts-instructors`
   - `swocts-mentors`
   - `swocts-platform-admins`
5. Create the OpenCyberRange OIDC provider and application. Use a confidential
   client, the redirect URI
   `https://<platform-host>/api/auth/sso/oidc/<provider_id>/callback`, and the
   `openid email profile` scopes. Ensure the `groups` claim is included.
6. Record the client ID and client secret in the platform identity-provider
   settings. Set `instructor_group` to `swocts-instructors`.
7. Test with learner, instructor, and administrator identities while local
   password login still works.
8. Keep a break-glass local administrator. Do not lock every local account out
   before SSO is verified.

## Backups

Run a daily database dump from the production host:

```bash
mkdir -p ~/authentik/backups
docker exec authentik-postgresql-1 pg_dump -U authentik authentik \
  > ~/authentik/backups/authentik-$(date -u +%Y%m%d-%H%M%S).sql
chmod 600 ~/authentik/backups/authentik-*.sql
```

Keep the last 14 daily dumps and copy them off-host with the same off-site
process used for the platform. The media volume is configuration data; back it
up with the database if custom branding or flow assets are added.

## Verification

```bash
docker compose ps
curl -sk https://<auth-host>/-/health/live/
curl -sk https://<auth-host>/-/health/ready/
curl -sk https://<auth-host>/application/o/opencyberrange/.well-known/openid-configuration
```

Then complete one browser OIDC login through the platform and confirm the
platform `/api/version`, provider discovery, and role mapping.

## Rollback

- Keep the platform `sso_enabled=false` until the first successful login.
- The platform identity provider can be disabled without deleting it.
- Keep the break-glass local administrator active.
- The Authentik stack can be stopped without affecting the platform's local
  login. Do not remove its volumes until a verified backup exists.
