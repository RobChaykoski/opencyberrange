# Cyber DNA

## Purpose

Cyber DNA is a bounded context that turns versioned activity events into
evidence, competency scores, behaviour and interest signals, gated career
affinity, and immutable snapshots. It must not read the catalogue tables and has
no foreign keys into them.

## Code map

| Concern | Location |
|---|---|
| Package | `platform/backend/app/cyber_dna/` |
| Router | `platform/backend/app/cyber_dna/router.py` (mounted at `/api/dna`) |
| Event contract | `platform/backend/app/services/dna_events.py` |
| Skill DNA | `platform/backend/app/services/skill_dna.py` |
| GPS | `platform/backend/app/services/cyber_gps.py` |
| Registry | `platform/backend/app/cyber_dna/models.py` |
| Docs | `docs/CYBER-DNA-V3.md` |

## API surface

| Method | Path | Notes |
|---|---|---|
| GET | `/api/dna/v3/dna` | DNA summary |
| GET | `/api/dna/v3/evidence` | evidence |
| GET | `/api/dna/v3/competencies` | competency scores |
| GET | `/api/dna/v3/behaviour` | behaviour signals |
| GET | `/api/dna/v3/interest` | interest signals |
| GET | `/api/dna/v3/affinity` | career affinity, gated |
| GET/POST | `/api/dna/v3/snapshots` | immutable snapshots |

## Behaviour that matters

- **Versioned events.** `2026.1` v3 event contract; formula version `2026.14`.
- **Append-only, idempotent evidence.** A replayed event does not duplicate.
- **Saturating scores.** Competency scores cap at 99.
- **Affinity gate.** Below 30 labs, 3 domains, and 100 observations the API
  returns `available: false` with a gate payload, never a zero.
- **Formula.** `100 x (0.50 coverage + 0.20 depth + 0.15 behaviour + 0.15
  interest)`; missing components renormalise. Confidence is a band, not a
  probability.
- **Consent.** `/api/dna/*` is consent-gated. Revocation returns `403` with
  `X-Consent-Status` and purges DNA evidence.
- **No catalogue reads.** The context owns its own identifiers. It must not join
  to `labs`, `lab_completions`, `courses`, or enrolments.
- **Snapshots are immutable.** A correction is a new snapshot.

## Persistent state

| Store | Data |
|---|---|
| `dna_evidence_records` | append-only evidence |
| `dna_snapshots` | immutable JSON snapshot |
| DNA tables | competency, behaviour, interest, affinity |
| Consent tables | gate state |
| No FK to catalogue tables | deliberate boundary |

## Fixtures and tests

- `seed_dna_fixtures.py` creates a synthetic learner and consent state
  (development only).
- Focused tests:

```bash
cd platform/backend
python -m pytest tests/test_cyber_dna_v3.py tests/test_skill_dna.py \
  tests/test_skill_momentum.py tests/test_career_readiness.py \
  tests/test_career_explorer.py tests/test_dna_onboarding.py -q
```

## Extension checklist

- Version the event contract before changing event shape.
- Keep the adapter server-side; never trust a client-computed score.
- Add an idempotency test.
- Add a consent-revocation test.
- Do not add a foreign key into the catalogue.
- Do not retune weights on a small, non-consenting cohort.

## Related

- [Cyber DNA v3](../../../../docs/CYBER-DNA-V3.md)
- [Career Atlas and momentum](../../../../docs/CAREER-ATLAS-AND-MOMENTUM.md)
- [Privacy and consent](../privacy-and-consent/README.md)
- [Competency and evidence](../competency-and-evidence/README.md)
