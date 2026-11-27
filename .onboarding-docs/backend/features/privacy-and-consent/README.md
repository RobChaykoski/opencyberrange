# Privacy and consent

## Purpose

Make consent a precondition for derived features, make revocation immediate and
destructive for derived data, and keep educational records intact. Consent is
enforced centrally, not per feature.

## Code map

| Concern | Location |
|---|---|
| Consent middleware | `platform/backend/app/consent/middleware.py` |
| Consent service | `platform/backend/app/consent/service.py` |
| Consent router | `platform/backend/app/consent/router.py` |
| Registry | `platform/backend/app/consent/registry.py` |
| Erasure | `platform/backend/app/services/erasure.py`, `erasure_ledger.py` |
| Privacy | `platform/backend/app/services/privacy.py`, `survey_consent.py` |
| Account export/delete | `platform/backend/app/routers/auth.py` (`/export`, `/delete-account`) |
| Model | `platform/backend/app/models/` (consent and audit tables) |

## Consent domains

The middleware maps path prefixes to a consent type. The important ones:

| Domain | Gated paths |
|---|---|
| `cyber_dna` | `/api/dna`, `/api/profile/skill-dna`, `/api/profile/career-dossier`, `/api/profile/competencies` |
| `cyber_gps` | `/api/profile/gps`, `/api/profile/role-readiness` |
| `portfolio` | `/api/profile/portfolio`, `/api/profile/snapshots` |
| `portfolio_sharing` | `/api/portfolio` |
| `ai_coach` | `/api/coach`, `/api/ai` |
| `research` | `/api/research` |

## API surface

| Method | Path | Notes |
|---|---|---|
| GET | `/api/consent/` | dashboard and state |
| GET | `/api/consent/types` | registry |
| POST | `/api/consent/{type}/revoke` | requires recent reauth; returns `202` |
| POST | `/api/consent/{type}/grant` | requires recent reauth |
| GET | `/api/consent/revocations` | the learner's own history |
| GET | `/api/auth/export` | account export |
| POST | `/api/auth/delete-account` | immediate self-service deletion |
| GET | `/api/admin/security/events` | audit trail |

## Behaviour that matters

- **Consent is checked before the route.** A revoked or purging feature returns
  `403` with `X-Consent-Status` and a stable `ConsentRequired` payload.
- **Missing/invalid token passes through** so the normal auth dependency returns
  `401`.
- **Revocation purges derived data** transactionally and queues cleanup. A
  replay of a completion writes zero DNA evidence.
- **Suppression survives restore.** The append-only suppression ledger lives on
  `workbook_data`, outside PostgreSQL.
- **Educational records remain.** Revocation removes derived data, not the
  learner's course and completion record.
- **Erasure.** `erase_learner()` is the only supported path; no cross-boundary
  cascade.
- **Fail closed.** A consent-check failure returns `503`, not an allow.

## Persistent state

| Store | Data |
|---|---|
| `consent_states` | current state and version |
| `consent_events` / `consent_audits` | grant/revoke history |
| `consent_revocations` / `consent_jobs` | purge workflow |
| `consent_suppressions` | proof of deletion under a keyed subject hash |
| `workbook_data` | append-only suppression ledger |
| `security_events` | consent and export audit |

## Fixtures and tests

- `seed_dna_fixtures.py` creates consent states and evidence (development only).
- Focused tests:

```bash
cd platform/backend
python -m pytest tests/test_consent_middleware.py tests/test_consent_revocation.py \
  tests/test_erasure.py tests/test_privacy.py tests/test_survey_consent.py \
  tests/test_purge_erased_accounts.py -q
```

## Extension checklist

- Add the path prefix to `CONSENT_PATH_PREFIXES` if the feature is derived data.
- Keep a route-level check as defence in depth.
- Add a test for revoked, missing, and purging states.
- Add a security event.
- Do not put deleted payloads in the audit store.
- Verify suppression survives a restore.

## Related

- [Cyber DNA](../cyber-dna/README.md)
- [Data classification](../../../../docs/DATA-CLASSIFICATION.md)
- [Consent revocation](../../../../docs/CONSENT-REVOCATION.md)
- [Privacy and data deletion](../../../../docs/PRIVACY-AND-DATA-DELETION.md)
- [Retention policies](../../../../docs/RETENTION-POLICIES.md)
