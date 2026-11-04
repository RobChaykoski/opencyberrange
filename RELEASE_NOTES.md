# OpenCyberRange 1.1.0

Released: 4 November 2026

OpenCyberRange 1.1 is a maintenance-line feature release on Ubuntu 22.04 LTS.
It keeps the 1.0 deployment and upgrade path and adds account email plus the
recent validation fixes.

## Highlights

- **Registration email:** new accounts receive a registration-success message.
  Accounts that need approval are told they are pending; auto-approved accounts
  receive a sign-in link.
- **SMTP settings:** admins configure the relay, from address, public URL, and
  credentials under Admin → Settings → Email, then send a test message.
- **Version identity:** the backend exposes `GET /api/version`, and the app
  footer shows the running release.
- **Certificate verification hardening:** malformed IDs, including emoji,
  kanji, non-ASCII digits, and whitespace, are rejected before lookup.

## Upgrade notes

1. Take a database snapshot.
2. Pull the `v1.1.0` tag or the matching `main` commit.
3. Rebuild the backend and frontend images.
4. Start the stack and verify `GET /api/version` reports `1.1.0`.
5. Open Admin → Settings → Email, save the relay settings, and send a test
   message.

## Supported scope

- Ubuntu 22.04 LTS for the 1.x maintenance line.
- Self-hosted Docker Compose deployments.
- WireGuard learner access, with optional WSTunnel deployments.

## Known limitations

- SMTP delivery is best effort. A failed relay never blocks account creation.
- The SMTP password is stored in `platform_settings` and masked in the admin API,
  not encrypted separately. Protect database backups.
- The footer version is informational and does not gate access.

## Previous release

See the `v1.0.0` tag for the 1.0.0 release notes.
