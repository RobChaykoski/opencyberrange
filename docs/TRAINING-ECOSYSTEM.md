# Training ecosystem (dev only)

This is a **simulated, multi-component training environment**. It exists so
learners can practise across realistic open-source systems without touching any
production service or real record.

It is not a production integration. It is not a data pipeline. It is a lab.

## Hard rules

- Run it on the **development host** (`<dev-host-ip>`) or a developer workstation.
  Never deploy it on the production host (`<prod-host-ip>`).
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
| `tls` | Caddy | 8443 | Dev-only HTTPS front for Moodle (LTI 1.3 testing) |
| `assets` | NetBox | 8083 | Sites, devices, prefixes, asset ownership |
| `assets` | Ralph | 8084 | Asset lifecycle and ownership records |
| `endpoint` | Fleet | 8082 | Device posture and endpoint compliance |
| external | OpenIAM | - | Identity governance, access review, certification |

OpenIAM publishes its own multi-service compose stack. Fetch it separately and
keep it on the dev host:

```bash
bash scripts/fetch-openiam-test-stack.sh
```

OpenIAM's official deployment is a Swarm-based multi-stack setup. See
`docs/OPENIAM-TEST-STACK.md` and run `scripts/run-openiam-test-stack.sh` on a
dedicated dev lab host only. Swarm is deliberately not initialised on the shared
dev host, so the training seed fetches OpenIAM but does not start it.

## Current dev deployment

The stack is deployed on the development host (`<dev-host-ip>`) with lab-only
credentials and synthetic data. Ports bind to the dev host IP so the dev range
and learner machines can reach them:

| Service | URL |
|---|---|
| Moodle | `http://<dev-host-ip>:8091/` |
| Moodle (dev TLS) | `https://<moodle-dev-host>:9443/` |
| Authentik | `http://<dev-host-ip>:9000/` |
| NetBox | `http://<dev-host-ip>:8083/` |
| Ralph | `http://<dev-host-ip>:8084/` |
| Fleet | `http://<dev-host-ip>:8082/` |

Validated on 19 November 2026 with Moodle 5.0.1, Authentik 2026.8.5,
NetBox, Ralph, and Fleet. The validator reported all checks passing on both the
workstation and the development host. Ralph's lab admin is seeded from
`RALPH_ADMIN_*`; OpenIAM's official compose stack is fetched on the dev host but
is not started by default.

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
docker compose --profile tls up -d
```

First-run notes:

- NetBox creates its superuser from `SUPERUSER_*` values derived from `.env`.
- Fleet needs a one-time database initialisation:
  `docker compose --profile endpoint run --rm -T --entrypoint /bin/sh fleet -c 'fleet prepare db' < /dev/null`.
  If that command is interrupted, remove the Fleet database volume and run it
  again; a half-migrated lab database will not serve. The seeder then creates
  the lab admin from `FLEET_ADMIN_*`. Fleet 4.95.0 currently panics when
  writing enroll secrets, so host enrollment is blocked until a fixed image is
  pinned; the UI and API share the same path.
- Ralph needs a one-time migration:
  `docker compose exec -T -w /opt/ralph/ralph-core ralph /opt/ralph/ralph-core/bin/ralph migrate --noinput`.
  The seeder then creates the lab admin from `RALPH_ADMIN_*`.
- Authentik needs its initial `akadmin` password set from the container logs.

## Dev-only TLS for Moodle

The `tls` profile adds Caddy on 9443 in front of Moodle. It uses Caddy's
internal CA, so browsers and services must trust that CA; the certificate is not
publicly trusted. Set `MOODLE_TLS_HOST` to the host learners and the dev range
use (for example `<dev-host-ip>`) and keep the port on the dev network.

Moodle is configured with `MOODLE_REVERSEPROXY=yes` and `MOODLE_SSLPROXY=yes`, so
its generated URLs use `https` when Caddy forwards `X-Forwarded-Proto: https`.
Use this endpoint for LTI 1.3 testing.

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

OpenCyberRange dev seed:

```bash
# run on the development host
bash scripts/ecosystem_seed/seed_ocr.sh
```

It creates the `OCR-CAP-COHORT` course, enrolls `student01`..`student08`,
assigns `mentor01`, `ta01`, and `instructor01`, and assigns three labs:
failed-login analysis, identity lifecycle, and firewall policy hardening. It
also creates `OCR-CAP-SINGLE` without mentor or TA staff so cross-course scope
denial can be tested. It refuses to run when the backend reports a production
environment.

## Capstone shapes

See `docs/TRAINING-CAPSTONES.md` for the single-student and cohort runbooks and
acceptance checks. See `docs/TRAINING-INSTRUCTOR-GUIDE.md` for the full
instructor workflow, scenario packs, and reset steps.

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

The development OpenCyberRange instance is at `<dev-host-ip>`. Integration is
**dev-to-dev only**:

1. Set `MOODLE_BIND=<dev-host-ip>` (or the dev host IP) in the training `.env` so
   the dev range can reach Moodle, or run the stack on the same host.
2. Register the OCR dev instance as an LTI/external tool in Moodle.
3. Register the training Moodle as an OIDC client in Authentik, then use that
   client for both Moodle and OCR dev.
4. Point OCR dev at the training Moodle with dev-only credentials.
5. Never copy the training `.env` to production and never register the training
   Moodle in a production identity provider.

The production range must keep zero configuration that references these hosts.

### LTI 1.3 launch

The training stack includes a dev-only Caddy TLS front for Moodle. For a
screenshot-backed walkthrough of the full flow (Deep Linking, learner launch,
reviewed grade passback, and NRPS roster), see
[`MOODLE-LTI-SHOWCASE.md`](MOODLE-LTI-SHOWCASE.md).

The whole local showcase is one command after both stacks are running:

```bash
python scripts/ecosystem_seed/seed_showcase.py
# or
bash scripts/ecosystem_seed/seed_showcase.sh
pwsh scripts/ecosystem_seed/seed_showcase.ps1
```

That command seeds Moodle and OpenCyberRange, creates the Moodle 5 course tool
and the pre-linked demo activity, registers the matching LTI platform, and
generates the tool RSA key on first use. It is idempotent.

To refresh only the LTI side:

```bash
# on the development host
bash scripts/ecosystem_seed/seed_lti.sh
```

It performs three steps:

1. Trusts the OCR dev certificate in Moodle and the Caddy root CA in OCR when
   the URLs use HTTPS. This is a runtime trust change, so re-run it after
   recreating either container.
2. Creates or updates a Moodle 5 course-level LTI 1.3 tool in `OCR-CAP-COHORT`
   and a demo activity linked to the selected exercise. The seed prints the
   actual client ID and deployment ID; it may not be `ocr-training-client` if
   that ID is already taken by another tool.
3. Registers or updates the matching platform in OCR and stores a tool RSA key
   so Deep Linking responses and AGS client assertions can be signed.

For a private Docker host, the seed also relaxes Moodle's cURL SSRF allow-list
(`MOODLE_ALLOW_PRIVATE_LTI_URLS=1`, the default) so Moodle can fetch the tool
JWKS and call AGS/NRPS. Set it to `0` when the tool uses a public HTTPS URL.

The verified launch flow is:

```text
Moodle activity
  -> OCR /api/lti/login
  -> Moodle /mod/lti/auth.php
  -> signed id_token
  -> OCR /api/lti/launch
  -> 302 /lti/callback?ticket=...
```

Field map:

| Side | Setting | Value |
|---|---|---|
| Moodle tool | Tool URL | `https://<<dev-host>-host>/api/lti/launch` |
| Moodle tool | Initiate login URL | `https://<<dev-host>-host>/api/lti/login` |
| Moodle tool | Public keyset URL | `https://<<dev-host>-host>/api/lti/jwks` |
| Moodle tool | Redirection URI | `https://<<dev-host>-host>/api/lti/launch` |
| OCR platform | Issuer | Moodle site URL |
| OCR platform | Auth login URL | `<moodle>/mod/lti/auth.php` |
| OCR platform | Token URL | `<moodle>/mod/lti/token.php` |
| OCR platform | JWKS URL | `<moodle>/mod/lti/certs.php` |
| OCR platform | Client ID | `ocr-training-client` |
| OCR platform | Deployment ID | Moodle tool type id |

LTI 1.3 expects HTTPS. The dev host uses
`https://<moodle-dev-host>:9443`; set `MOODLE_TLS_HOST` to a
hostname that resolves to the dev host. Do not expose it publicly.

## Validate

```bash
bash scripts/validate-ecosystem-test.sh
# or
pwsh scripts/validate-ecosystem-test.ps1
```

The validator checks Moodle, its database, the TLS front, and each enabled
profile: Authentik health, NetBox login and API, Ralph response, and Fleet
response. It refuses to run when `OCR_ENV` is `production` or `prod`.

See `docs/TRAINING-VALIDATION.md` for the recorded results.

## Reset

```bash
cd deploy/ecosystem-test
docker compose --profile sso --profile assets --profile endpoint --profile tls down -v
```

Then start and seed again. Re-run `scripts/ecosystem_seed/seed_lti.sh` after
recreating the Moodle or OCR containers so the runtime CA trust is restored.
The environment is designed to be disposable.

## What "working" means

- A learner can log into Moodle and see a capstone course.
- An instructor can see the cohort and its groups.
- A mentor sees only assigned learners in OCR dev.
- NetBox shows the synthetic site, devices, and prefixes.
- Fleet is reachable and ready for fake endpoint enrolment.
- No component holds a production credential or production data.
