# Simulated training ecosystem (dev only)

This stack exists to run **training capstones** with open-source tools. It is
not a production integration and must never receive production data.

## Isolation rules

- Run it on the **dev host only**. Do not deploy this compose file on
  production.
- Ports bind to `127.0.0.1`; there is no public exposure.
- Use fake users, fake courses, fake assets, and fake endpoint data only.
- No production SMTP, no production SSO, no production API tokens, no
  production database dumps.
- Volumes are disposable: `docker compose down -v` resets the whole lab.
- Do not connect this stack to OpenCyberRange production, OpenGRC production,
  OpenEMR production, or any real identity provider.
- Treat every credential in `.env` as a lab credential, not a secret to reuse.

## Services and profiles

| Profile | Services | Training use |
|---|---|---|
| default | Moodle + MariaDB | Course shell, learners, instructors, capstone submissions |
| `sso` | Authentik + PostgreSQL + Redis | OIDC/SAML login, groups, MFA, application access |
| `assets` | NetBox + PostgreSQL + Redis, Ralph + PostgreSQL | Asset inventory, ownership, network source of truth |
| `endpoint` | Fleet + MySQL + Redis | Endpoint posture, device compliance, patch state |
| OpenIAM | Official OpenIAM compose (not embedded) | Identity governance, access review, certification |

## Start

```bash
cd deploy/ecosystem-test
cp .env.example .env
# replace every password in .env with a lab-only value
docker compose up -d
bash ../../scripts/validate-ecosystem-test.sh
```

Add profiles as needed:

```bash
docker compose --profile sso up -d
docker compose --profile assets up -d
docker compose --profile endpoint up -d
```

## Capstone shapes

- **Single student:** Moodle course + Authentik SSO + one OpenCyberRange lab.
- **Multi-student cohort:** Moodle groups + Authentik groups + OpenCyberRange
  enrolments + NetBox/Ralph asset ownership.
- **Defensive capstone:** Moodle brief + Wazuh/Fleet endpoint evidence +
  OpenGRC control evidence (fake records).
- **Identity capstone:** Moodle + Authentik + Keycloak/OpenIAM lab systems, with
  no production identity provider.
- **Data-protection capstone:** OpenDetectionEngine/OpenDLP classification
  results plus OpenGRC privacy controls, using synthetic data only.

## OpenIAM

OpenIAM's official deployment is a multi-service compose stack. It is not
embedded here because it has its own database, message bus, and versioned
configuration. Fetch it separately:

```bash
bash ../../scripts/fetch-openiam-test-stack.sh
```

Follow the official OpenIAM Docker guide, keep it on the dev host, and load only
fake identities and fake access-review campaigns.

## Validation

`scripts/validate-ecosystem-test.sh` checks:

- Moodle login page and database.
- Authentik liveness/readiness when the `sso` profile is running.
- NetBox and Ralph login pages when `assets` is running.
- Fleet health when `endpoint` is running.

A failed optional profile is a lab setup issue, not a production incident.
