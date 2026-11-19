# Training ecosystem (dev only)

This is a **simulated, multi-component training environment**. It exists so
learners can practise across realistic open-source systems without touching any
production service or real record.

It is not a production integration. It is not a data pipeline. It is a lab.

## Hard rules

- Run it on the **development host** (`172.16.16.44`) or a developer workstation.
  Never deploy it on the production host (`172.16.16.41`).
- Load **fake users, fake courses, fake assets, and fake endpoint data** only.
- No production SMTP, no production SSO, no production API tokens, no production
  database dumps, no patient, learner, or employee records.
- Keep ports bound to loopback by default. Expose to the dev network only when a
  learner machine must reach it.
- Treat every `.env` value as a lab credential. Never reuse one.
- `docker compose down -v` is the reset button. Losing lab data is expected.

## Components

| Profile | Service | Port | Training job |
|---|---|---|---|
| default | Moodle | 8091 | Courses, cohorts, capstone briefs, submissions |
| default | MariaDB | internal | Disposable Moodle database |
| `sso` | Authentik | 9000 | OIDC/SAML login, groups, MFA, application access |
| `assets` | NetBox | 8083 | Sites, devices, prefixes, asset ownership |
| `assets` | Ralph | 8084 | Asset lifecycle and ownership records |
| `endpoint` | Fleet | 8082 | Device posture and endpoint compliance |
| external | OpenIAM | - | Identity governance, access review, certification |

OpenIAM publishes its own multi-service compose stack. Fetch it separately and
keep it on the dev host:

```bash
bash scripts/fetch-openiam-test-stack.sh
```

## Current dev deployment

The stack is deployed on the development host (`172.16.16.44`) with lab-only
credentials and synthetic data. Ports bind to the dev host IP so the dev range
and learner machines can reach them:

| Service | URL |
|---|---|
| Moodle | `http://172.16.16.44:8091/` |
| Authentik | `http://172.16.16.44:9000/` |
| NetBox | `http://172.16.16.44:8083/` |
| Ralph | `http://172.16.16.44:8084/` |
| Fleet | `http://172.16.16.44:8082/` |

Validated on 19 November 2026 with Moodle 5.0.1, Authentik 2026.8.5,
NetBox, Ralph, and Fleet. The validator reported all checks passing on both the
workstation and the development host.

Do not treat these URLs as production. They are lab endpoints on the dev network
and must stay off the production host.

## Start

```bash
cd deploy/ecosystem-test
cp .env.example .env
# replace every password in .env with a lab-only value
docker compose up -d
docker compose --profile sso up -d
docker compose --profile assets up -d
docker compose --profile endpoint up -d
```

First-run notes:

- NetBox creates its superuser from `SUPERUSER_*` values derived from `.env`.
- Fleet needs a one-time database initialisation:
  `docker compose --profile endpoint run --rm -T --entrypoint /bin/sh fleet -c 'fleet prepare db' < /dev/null`.
  If that command is interrupted, remove the Fleet database volume and run it
  again; a half-migrated lab database will not serve.
- Ralph needs its first admin created in the web UI.
- Authentik needs its initial `akadmin` password set from the container logs.

## Seed fake data

```bash
# Linux/macOS
bash scripts/ecosystem_seed/seed_all.sh

# Windows
pwsh scripts/ecosystem_seed/seed_all.ps1
```

Moodle seed creates:

- Category `OpenCyberRange Training`.
- Courses `OCR-CAP-SINGLE`, `OCR-CAP-COHORT`, `OCR-FOUND`.
- Staff `instructor01`, `mentor01`, `ta01`.
- Students `student01` .. `student08`.
- Groups `Cohort A` and `Cohort B`, plus cohort `OCR-TRAINING-COHORT`.
- Capstone brief pages in `OCR-CAP-SINGLE` and `OCR-CAP-COHORT`, and a training
  lab guide in `OCR-FOUND`.

Authentik seed creates:

- Groups `ocr-learners`, `ocr-mentors`, `ocr-teaching-assistants`,
  `ocr-instructors`, `ocr-privacy-office`, and `ocr-auditors`.
- Users `student01`..`student08`, `mentor01`, `ta01`, `instructor01`,
  `privacy01`, and `auditor01` in the matching groups.

Default fake password is `TrainLab!2026#Student`; override with
`TRAINING_PASSWORD`. These accounts are not real people.

NetBox seed creates a synthetic tenant, site, manufacturers, device types, roles,
five devices, and three training prefixes.

## Capstone shapes

See `docs/TRAINING-CAPSTONES.md` for the single-student and cohort runbooks and
acceptance checks.

- **Single student:** one Moodle course, one OCR lab, one evidence submission.
  Report scope is the learner and the assigned mentor.
- **Multi-student cohort:** Moodle groups map to OCR course staff assignments and
  to Authentik groups. Each team owns a slice (detection, identity, assets) and
  one joint brief.
- **Defensive:** Moodle brief plus Wazuh/Fleet endpoint evidence and OpenGRC
  control evidence, all synthetic.
- **Identity:** Moodle plus Authentik plus Keycloak/OpenIAM lab systems. No real
  identity provider is connected.
- **Data protection:** OpenDetectionEngine/OpenDLP classification of synthetic
  data, plus OpenGRC privacy controls.

## Linking to the development cyber range

The development OpenCyberRange instance is at `172.16.16.44`. Integration is
**dev-to-dev only**:

1. Set `MOODLE_BIND=172.16.16.44` (or the dev host IP) in the training `.env` so
   the dev range can reach Moodle, or run the stack on the same host.
2. Register the OCR dev instance as an LTI/external tool in Moodle.
3. Register the training Moodle as an OIDC client in Authentik, then use that
   client for both Moodle and OCR dev.
4. Point OCR dev at the training Moodle with dev-only credentials.
5. Never copy the training `.env` to production and never register the training
   Moodle in a production identity provider.

The production range must keep zero configuration that references these hosts.

### LTI 1.3 fields (next step)

OpenCyberRange already exposes LTI 1.3 endpoints. To wire the training Moodle:

| Side | Setting | Value |
|---|---|---|
| Moodle tool | Tool URL | `https://<ocr-dev-host>/api/lti/launch` |
| Moodle tool | Initiate login URL | `https://<ocr-dev-host>/api/lti/login` |
| Moodle tool | Public keyset URL | `https://<ocr-dev-host>/api/lti/jwks` |
| Moodle tool | Redirection URI | `https://<ocr-dev-host>/api/lti/launch` |
| OCR platform | Issuer | Moodle site URL |
| OCR platform | Auth login URL | `<moodle>/mod/lti/auth.php` |
| OCR platform | Token URL | `<moodle>/mod/lti/token.php` |
| OCR platform | JWKS URL | `<moodle>/mod/lti/certs.php` |
| OCR platform | Client ID / deployment ID | Values generated by Moodle |

LTI 1.3 expects HTTPS. Put Moodle behind a dev-only TLS reverse proxy before
testing launches; do not expose it publicly. Register the platform in
**Admin > Settings > LTI platforms** and add an External Tool activity in
`OCR-CAP-SINGLE` or `OCR-CAP-COHORT`.

## Validate

```bash
bash scripts/validate-ecosystem-test.sh
# or
pwsh scripts/validate-ecosystem-test.ps1
```

The validator checks Moodle, its database, and each enabled profile: Authentik
health, NetBox login and API, Ralph response, and Fleet response. It refuses to
run when `OCR_ENV` is `production` or `prod`.

## Reset

```bash
cd deploy/ecosystem-test
docker compose --profile sso --profile assets --profile endpoint down -v
```

Then start and seed again. The environment is designed to be disposable.

## What "working" means

- A learner can log into Moodle and see a capstone course.
- An instructor can see the cohort and its groups.
- A mentor sees only assigned learners in OCR dev.
- NetBox shows the synthetic site, devices, and prefixes.
- Fleet is reachable and ready for fake endpoint enrolment.
- No component holds a production credential or production data.
