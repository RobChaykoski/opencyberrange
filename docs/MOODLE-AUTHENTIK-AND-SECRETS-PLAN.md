# Moodle pilot: Authentik and secrets plan

**Date:** 20 November 2026

This is the follow-on plan for the live Moodle pilot. The event uses local
Moodle accounts and the existing OpenCyberRange SMTP source. Authentik and
OpenBao are deliberate later phases, not last-minute event changes.

## Current event posture

- Production pilot Moodle on `172.16.16.41`, published at
  `https://moodle.swocts.com` through Nginx Proxy Manager.
- Local Moodle accounts with unique generated passwords, stored in a mode-600
  CSV on the production host.
- Self-registration, guest access, and debug output are disabled.
- SMTP is configured from the production OpenCyberRange settings. The Moodle
  SMTP password is a Compose secret, not a `mdl_config` row.
- OpenCyberRange platform settings marked secret are encrypted with the
  application Fernet key. The SMTP password row now uses the `v1:` envelope.
- Moodle database and data are backed up on a daily cron with 14-day retention.
- Production OpenCyberRange has a pre-change checkpoint backup.

Residual risks:

- No institutional SSO or MFA yet.
- No secrets manager on the host; `bao`/Vault is not installed.
- The production host root filesystem is not LUKS-encrypted.
- The event accounts are generic pilot accounts, not verified institutional
  identities.
- Privacy notice, consent, and retention decisions are still required.

## Phase 1: event controls (now)

- Keep the pilot account CSV root-only and distribute credentials out of band.
- Keep `secrets/moodle_smtp_pass` root/daemon-only.
- Keep `mdl_config.smtppass` empty; `config.php` reads the Compose secret.
- Do not put SMTP or admin secrets in shell history, chat, or tickets.
- Add HSTS and an access restriction at NPM.
- Back up before any configuration change and before the event.
- Record every account and LTI registration created for the pilot.
- Keep the public DNS records aligned with the firewall's WAN address using the
  scoped Cloudflare DDNS stack in
  [`deploy/cloudflare-ddns/`](../deploy/cloudflare-ddns/README.md), or the
  firewall's built-in Cloudflare DDNS client. Verify both public hostnames
  after a firewall reboot.

## Phase 2: Authentik

Authentik should be the identity provider for the real release, not the event
bootstrap.

### Build steps

1. Deploy Authentik on a production-grade host with its own PostgreSQL and
   Redis, TLS at `auth.swocts.com`, backups, and restricted admin access.
2. Configure MFA policy for staff and, if required, learners.
3. Create a Moodle OIDC or SAML application. Use OIDC if Moodle's OAuth2
   plugin covers the required claim mapping; use SAML if the institution needs
   SAML attribute release.
4. Map Authentik groups to Moodle cohorts/roles:
   - `swocts-learners` -> student
   - `swocts-instructors` -> editing teacher
   - `swocts-mentors` -> non-editing teacher
   - `swocts-tas` -> non-editing teacher
   - `swocts-moodle-admins` -> manager/admin, tightly controlled
5. Test with a small pilot group while local auth still exists.
6. Keep a break-glass local admin account, stored offline.
7. After validation, disable local password login for real users and make SSO
   the primary method.
8. Remove the generic `pilot.*` accounts or convert them to named identities.

### Acceptance criteria

- SSO login succeeds for learner, instructor, and mentor test identities.
- Group changes add/remove the correct Moodle role.
- MFA is enforced for privileged accounts.
- Local password login is disabled for non-break-glass users.
- Break-glass login is tested and documented.
- An IdP outage has a documented response.

## Phase 3: OpenBao

`bao` is not installed on the production host today. Do not install a new
secrets service during the event cutover. OpenBao makes sense once it has
auto-unseal and a real backup/HA design; without those, it only moves plaintext
from one local file to another.

### Build steps

1. Deploy OpenBao with TLS, audit devices, backups, and auto-unseal through a
   cloud KMS/HSM or another independent trust root.
2. Define paths:
   - `secret/moodle/smtp`
   - `secret/moodle/admin`
   - `secret/moodle/database`
   - `secret/opencyberrange/mail`
   - `secret/lti/moodle-pilot`
   - backup encryption keys
3. Use short-lived AppRole or workload identity for the Moodle and
   OpenCyberRange agents; no root tokens on application hosts.
4. Render the Moodle secret file from OpenBao with an agent/template, or inject
   it at container start. Keep `config.php` reading
   `/run/secrets/moodle_smtp_pass`.
5. Move the production OpenCyberRange Fernet key and mail password into
   OpenBao only after the key-rotation and break-glass procedures are tested.
6. Rotate secrets and record the change in the release evidence.

### Acceptance criteria

- No application secret is stored in a database row, Compose environment, or
  world-readable file.
- Secret retrieval is audited and scoped to the workload identity.
- Auto-unseal is tested; a host reboot does not require an operator to paste an
  unseal key.
- Backups of secret material are encrypted and restorable.
- Rotation of the Moodle SMTP credential and the OCR mail credential is
  rehearsed.

## Secret inventory

| Secret | Current location | Next location |
|---|---|---|
| Moodle SMTP password | `secrets/moodle_smtp_pass`, Compose secret | OpenBao -> rendered secret |
| Moodle admin password | `moodle-prod/.env`, mode 600 | OpenBao / break-glass vault |
| Moodle database password | `moodle-prod/.env` and Compose env | OpenBao |
| OpenCyberRange mail password | encrypted `platform_settings` | OpenBao |
| OpenCyberRange `WG_ENCRYPTION_KEY` | `platform/.env`, mode 600 | OpenBao |
| LTI tool private keys | encrypted `lti_platforms` rows | OpenBao |
| Backup GPG key | operator-controlled | OpenBao / offline escrow |

## Decision

For the event: local Moodle accounts, SMTP secret file, envelope encryption for
OpenCyberRange settings, backups, and NPM TLS.

After the event: Authentik first for identity, then OpenBao for secret
consolidation and rotation. A production release should not claim SSO or
centralized secret management until both acceptance criteria are met.
