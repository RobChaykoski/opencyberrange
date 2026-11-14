# Open Badges 3.0 — scope and build plan

Status: **planned, not shipped.** Release 5.0.1 exposes certificates and
verification, but no portable credential exists yet. This document defines the
implementation so it can be built and reviewed as a dedicated change; do not
describe badges as available until it ships.

## Goal

Issue IMS Open Badges 3.0 credentials from the results the platform already
produces, with a hosted, verifiable credential URL and an opt-in download. The
credential should open in an Open Badges viewer and be usable in a course
portfolio or LMS profile.

## Existing foundation

- Level and event certificates are generated from completion data
  (`curriculum.py`, `event_certificates.py`) and verified at
  `/verify/certificate/<id>`.
- Reports are already integrity-signed, and `REPORT_SIGNING_KEY` establishes the
  pattern for deployment-held signing material.
- Achievements and completions are audited and exposed on the learner profile.

Reuse the certificate eligibility rules rather than inventing a second
completion model.

## Credential design

- **Encoding:** hosted JWT-VC, signed with Ed25519 (`EdDSA`), carrying the
  standard `vc` claim. JSON-LD encoding is not required for phase 1.
- **Issuer:** `open_badge_issuer_url` (defaults to `PUBLIC_BASE_URL`), plus an
  issuer profile endpoint exposing name, URL, and public JWKS.
- **Subject:** a pseudonymous HTTPS identifier
  (`/api/badges/subjects/<opaque-id>`), not the username or email. The learner
  may opt in to including their display name.
- **Achievement:** derived from a level certificate or event award. The
  definition carries name, description, criteria URL, and evidence URL
  (the certificate verification page).
- **Status:** a hosted status endpoint plus a `credentialStatus` entry; a
  revoked credential must fail verification even if the signed JWT still parses.
- **Keys:** one active Ed25519 key, stored encrypted in `platform_settings`
  (`open_badge_signing_key`) with a `kid`; the public key is published at
  `/api/badges/issuer/jwks`. A rotation path retires the old public key but
  keeps it in the JWKS so old credentials verify.

## Data model (migration 0026)

`open_badge_credentials`

| Column | Purpose |
|---|---|
| `id` | local identifier |
| `user_id` | owner; deleted with the learner |
| `source_type`, `source_key` | `level_certificate` or `event_award` plus its identifier |
| `achievement_key` | stable slug used in the achievement URL |
| `achievement_name`, `achievement_description` | snapshot at issuance |
| `criteria_url`, `evidence_url` | public links |
| `credential_jti` | unique credential ID used in the URL and JWT |
| `issued_at`, `expires_at` | validity window (expiry optional) |
| `recipient_name_opt_in` | whether the display name is included |
| `revoked_at`, `revoked_by_id`, `revocation_reason` | revocation audit |

Plaintext secrets never enter this table; the signing key lives only in the
encrypted settings row.

## Endpoints

Public:

- `GET /api/badges/issuer` — issuer profile.
- `GET /api/badges/issuer/jwks` — public signing keys.
- `GET /api/badges/achievements/{key}` — achievement definition.
- `GET /api/badges/credentials/{jti}` — signed JWT-VC (JSON).
- `GET /api/badges/credentials/{jti}/status` — active/revoked status.

Authenticated learner:

- `GET /api/badges/mine` — issued credentials and status.
- `POST /api/badges/issue` — issue for an eligible certificate; idempotent per
  source.
- `POST /api/badges/{id}/consent` — include or omit the display name.

Admin:

- `POST /api/badges/{id}/revoke` — reason required, audited.
- Settings for enablement, issuer name/URL, key rotation.

## Privacy and erasure

- Issuance is opt-in per credential; no public URL exists until the learner
  requests it.
- Public credentials contain a pseudonymous subject and the achievement only.
- Account deletion revokes credentials, removes the subject mapping, and keeps
  only an audit reference.
- Retention purge includes badge rows for the course/cohort.

## Frontend

- Profile: **Credentials** card listing issued badges, copy-link, download JSON,
  and consent toggle.
- Public verification page: issuer, achievement, recipient (as shared), status,
  and a link to verify the certificate.
- Admin: enable/disable, issuer profile, key rotation, revocation list.

## Tests

- JWT signature verification with the published JWKS; tampered payload fails.
- Eligibility: no badge before completion; idempotent re-issue.
- Revocation makes the public status and verifier fail.
- Erasure removes the subject and revokes credentials.
- Public endpoints expose no email/username unless consent was given.
- Migration and settings key generation/rotation.

## Phases

1. **Foundation (2–3 days):** migration, key settings/generation, issuer profile
   and JWKS, signing service, tests.
2. **Issuance (3–4 days):** eligibility from level certificates, issue/list/
   status endpoints, revocation, audit.
3. **Experience (3–4 days):** profile card, public verification page, consent,
   admin settings/revocation.
4. **Assurance (2–3 days):** privacy/erasure tests, viewer compatibility check,
   docs and procurement note.

Phase 1 and 2 are the security-sensitive core; phase 3 should not start until
signing and revocation tests are green.
