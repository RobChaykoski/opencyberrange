# Production pilot Moodle

This stack is the production-host Moodle for the live `<moodle-host>`
pilot. It is separate from `deploy/moodle-staging` and from the disposable
training lab.

Use it only for authorised participants and the agreed pilot course. Do not run
the synthetic training seed (`seed_moodle.php`) here.

> **Placeholders.** `<moodle-host>`, `<prod-host-ip>`, and `<npm-host-ip>` are
> intentionally generic. Take the real values from the private deployment
> inventory and never commit them.

## Shape

```text
Internet
  -> Nginx Proxy Manager :443, https://<moodle-host>
  -> production host <prod-host-ip>:8092
  -> Moodle + MariaDB (private compose network)
```

NPM terminates TLS. Moodle runs with `sslproxy=yes` and `reverseproxy=no`, so it
preserves the public Host while trusting the proxy's HTTPS scheme.

## Before real users

These are go/no-go items, not optional polish:

- [ ] Move to a production host and take a restore-tested backup.
- [ ] Configure institutional SSO and MFA; disable general local-password login.
- [ ] Configure SMTP for password reset and notifications.
- [ ] Publish the privacy notice, acceptable-use text, retention rule, and
      support contact.
- [ ] Restrict administrative access to staff/VPN or an identity-aware proxy.
- [ ] Capacity-test the expected concurrent cohort.
- [ ] Add uptime monitoring and alerting.
- [ ] Complete the LTI test against a staging OpenCyberRange first.
- [ ] Obtain approval for any production OpenCyberRange registration.
- [ ] Decide who may join the pilot and how their accounts are revoked.

Until SSO and SMTP are configured, the stack is technically live but not ready
for real students or instructors.

## Deploy on the production host

```bash
# on the production host
mkdir -p ~/moodle-prod
# copy this directory's files to ~/moodle-prod
cd ~/moodle-prod
cp .env.example .env
chmod 600 .env
# set strong unique MOODLE_DB_* and MOODLE_ADMIN_* values
docker compose up -d
docker compose exec -T -u daemon moodle php /harden.php
docker compose exec -T -u daemon moodle php /create_pilot_course.php
```

### SMTP secret

The SMTP password is not stored in `mdl_config`. It is a Compose secret at
`secrets/moodle_smtp_pass`, read by `config.php` at runtime. The file is
gitignored and must be owned by the container's web user, with no host-user
read access:

```bash
mkdir -p secrets
chmod 700 secrets
# write the password without a trailing newline if possible
printf '%s' "$SMTP_PASSWORD" > secrets/moodle_smtp_pass
chmod 600 secrets/moodle_smtp_pass
docker run --rm -v "$PWD/secrets:/secrets" alpine chown 1:1 /secrets/moodle_smtp_pass
```

The container mounts it read-only at `/run/secrets/moodle_smtp_pass`. Compose
outside Swarm mode ignores secret `uid`/`gid`/`mode`, so the host file must be
owned by uid/gid `1:1` (the Moodle web user) for the Apache process to read it.
Keep `mdl_config.smtppass` empty. Back up the secret separately or recover it
from the encrypted OpenCyberRange email settings.

Authentik and OpenBao are deliberately not rushed into this event stack. The
follow-on plan is in
[`../../docs/MOODLE-AUTHENTIK-AND-SECRETS-PLAN.md`](../../docs/MOODLE-AUTHENTIK-AND-SECRETS-PLAN.md).

Public DNS follows the firewall's WAN address. Use the scoped Cloudflare DDNS
stack in [`../cloudflare-ddns/`](../cloudflare-ddns/README.md) or the firewall's
built-in Cloudflare DDNS client. After a firewall reboot, verify both
`<moodle-host>` and `<platform-host>` before debugging NPM or Moodle.

The upstream is `<prod-host-ip>:8092`. Set the NPM proxy host to:

| NPM setting | Value |
|---|---|
| Scheme | `http` |
| Forward host | `<prod-host-ip>` |
| Forward port | `8092` |
| Preserve Host header | enabled |
| Websockets | not required |
| SSL | Let's Encrypt, Force SSL |

Add HSTS in the NPM advanced configuration:

```nginx
add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;
```

Restrict the direct upstream port to the NPM host:

```bash
sudo ufw allow from <npm-host-ip> to any port 8092 proto tcp
# or the equivalent firewall rule for the host
```

## Create the pilot course

`create_pilot_course.php` creates `PILOT-101` under a `SWOCTS Pilot` category.
No fake users or fake enrolments are created. Enrol real participants through
SSO or the Moodle administration UI.

## Pilot accounts

`create_pilot_accounts.php` creates:

- `pilot.instructor` — editing teacher
- `pilot.mentor` — non-editing teacher
- `pilot.ta` — non-editing teacher
- `pilot.student01` through `pilot.student08` — learners

All accounts are enrolled manually in `PILOT-101`. Passwords are generated
individually and written to `/tmp/pilot-accounts.csv` inside the container.
Copy it to the production host immediately:

```bash
docker exec moodle-prod-moodle-1 cat /tmp/pilot-accounts.csv \
  > ~/moodle-prod/pilot-accounts.csv
chmod 600 ~/moodle-prod/pilot-accounts.csv
docker exec moodle-prod-moodle-1 rm -f /tmp/pilot-accounts.csv
```

Retrieve the CSV only on the production host. Do not paste it into chat, tickets,
or the repository. Replace the generic identities with real participants or
Authentik identities before general use.

## LTI integration test

Only after the Moodle-side pilot is ready and a change window is agreed:

1. Take the production OpenCyberRange backup.
2. Use the production OpenCyberRange only for a dedicated pilot course and
   dedicated test account.
3. Create the Moodle 5 course tool and a pilot activity with
   `seed_moodle_lti.php`, pointing at `https://<platform-host>`.
4. Register the platform in the production OpenCyberRange.
5. Test launch, reviewed grade passback, and NRPS with the pilot course.
6. Record the result and remove the platform/links/scores/roster when the test
   ends, or leave them only with explicit approval.

Do not use the training-lab Moodle or the training-lab credentials for this.

To build the Moodle side:

```bash
docker compose exec -T -u daemon \
  -e OCR_PUBLIC_URL=https://<platform-host> \
  -e OCR_INTERNAL_URL=https://<platform-host> \
  -e MOODLE_LTI_CLIENT_ID=ocr-moodle-pilot \
  -e MOODLE_LTI_COURSE=PILOT-101 \
  -e MOODLE_LTI_COURSE_TOOL_NAME='OpenCyberRange Pilot' \
  -e MOODLE_LTI_ACTIVITY_NAME='OpenCyberRange Pilot Lab' \
  -e MOODLE_LTI_LAB_SLUG=network-0-1-ping-basics \
  -e MOODLE_ALLOW_PRIVATE_LTI_URLS=0 \
  moodle php /seed_moodle_lti.php
```

It prints the `client_id` and `deployment_id` to register in the production
OpenCyberRange. Do not relax Moodle's cURL security for the public HTTPS
endpoint.

## LTI networking

The production host resolves `<platform-host>` to the private NPM address
`<npm-host-ip>`.

OpenCyberRange 5.30.1 removed the ticket-exchange dependency on
`sso_enabled`, so a local-login deployment can leave SSO off and LTI launches
still work. No public SSO provider is configured.

Moodle's `curlsecurityblockedhosts` is narrowed to the default private ranges
plus a carve-out that admits only the NPM address `<npm-host-ip>`; every other
address in `172.16.0.0/12` is blocked. The LTI JWKS fetch was verified at `200`
through Moodle's own cURL wrapper, and private targets such as
`<prod-host-ip>` and `10.0.0.1` are rejected. The pre-change value is kept on the
production host at
`~/moodle-prod/curlsecurityblockedhosts.pre-narrow.txt`.

The dev-only seed path (`MOODLE_ALLOW_PRIVATE_LTI_URLS=1`) still relaxes the
list for `host.docker.internal`; do not use it in production.

## HSTS

NPM passes origin response headers through, so HSTS is set in Apache rather than
in the NPM admin UI:

```text
deploy/moodle-prod/apache-hsts.conf
  -> /opt/bitnami/apache/conf/vhosts/zz-hsts.conf
```

The Compose file mounts it, and `apachectl -t && apachectl -k graceful` applies
it to a running container. Verify with an external header check; do not rely on
the internal NPM response.

## Pilot readiness review

The 2026-11-20 review is in
[`docs/PILOT-READINESS-REVIEW.md`](../../docs/PILOT-READINESS-REVIEW.md). It
records the exact verification scope, the two pilot-only exceptions, and the
post-event cleanup list.

## Workbook embedding

The exercise workbook is an iframe served from the wiki origin. Its CSP uses the
OpenCyberRange `wiki_frame_ancestor` setting. Set it to include the LMS origin,
or the workbook pane will be blocked by `frame-ancestors`:

```text
https://<prod-host-ip> https://<platform-host> https://<public-ip> https://<moodle-host>
```

The backend caches this value for 30 seconds. After changing it, wait for the
cache window or restart the backend. This setting is separate from the SPA
`frame-ancestors` policy; it only allows the wiki/workbook pages to be framed by
the listed origins.

The generated frontend nginx configuration also serves a public, empty
`sitemap.xml` for workbook paths. MkDocs Material probes it from the sandboxed
workbook iframe; without the public empty response the probe fails with a
CORS/login console error. If the production frontend container is recreated
from an older image, rebuild the frontend or reapply the generated wiki block.

## Backups

```bash
cd ~/moodle-prod
bash backup.sh
```

Keep `backups/` private. The script dumps MariaDB and the Moodle data directory
and prunes its own files after 14 days. Add it to cron on the production host
and test a restore into a disposable copy before the event.

## Rollback

If the pilot fails:

1. Point NPM back to the staging upstream
   (`http://<staging-host-ip>:8092`) or take the site offline.
2. Stop `moodle-prod` with `docker compose down` (do not delete volumes until
   the feedback and retention decision are recorded).
3. Remove any production OpenCyberRange LTI platform, links, scores, roster
   rows, and test identities created for the pilot.
4. Record the failure and the data-retention decision.

## Do not

- Run the synthetic `seed_moodle.php` here.
- Expose the MariaDB port.
- Publish the direct 8092 upstream.
- Connect this instance to the training-lab Moodle or training credentials.
- Continue the pilot without SSO/MFA, SMTP, privacy notice, and backups.
