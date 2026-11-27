# Profile and evidence (frontend)

## Purpose

Show a learner their own progress, evidence, certificates, achievements, and
career signals, and let them manage the privacy settings that control derived
features.

## Routes and views

| Route | View | Notes |
|---|---|---|
| `/profile` | `Profile.vue` | profile, consent, DNA, career panels |
| `/my-evidence` | `MyEvidence.vue` | evidence and review state |
| `/journey` | `Journey.vue` | learning journey |
| `/impact` | `Impact.vue` | impact and legacy |
| `/practice` | `Practice.vue` | practice exams |
| `/celebrations` | `Celebrations.vue` | achievements wall |
| `/certificate/:trackSlug/:levelId` | `Certificate.vue` | level certificate |
| `/certificate/event/:eventId/:award` | `Certificate.vue` | event certificate |
| `/verify` | `VerifyCertificate.vue` | public verification |
| `/verify/certificate/:id` | `VerifyCertificate.vue` | public result |

Supporting components include `CyberDnaV3Panel.vue`, `CareerAtlas.vue`,
`CareerGps.vue`, `CompetencyRadar.vue`, `ConsentPanel.vue`,
`AchievementMedallion.vue`, and `GradingReport.vue`.

## API calls

| Data | Endpoint |
|---|---|
| Profile | `GET /api/profile/summary`, `/api/auth/me` |
| Evidence | `GET /api/evidence`, `/api/evidence/{id}` |
| Competencies | `GET /api/profile/competencies` |
| DNA | `GET /api/dna/v3/*` |
| Consent | `GET /api/consent/`, `POST /api/consent/{type}/revoke|grant` |
| Export | `GET /api/auth/export` |
| Certificates | `GET /api/profile/transcript.pdf`, certificate routes |

## Behaviour that matters

- **Consent gate.** A revoked DNA/GPS/portfolio domain shows the gate, not a
  zero or a blank score.
- **Unmeasured is not zero.** A missing measure is labelled unmeasured.
- **Own data only.** The profile never fetches another learner's record.
- **Certificate verification is public by design.** It shows only the minimum
  needed to verify the credential.
- **Reauth for sensitive changes.** Consent revocation and deletion require a
  recent reauthentication.
- **Export is labelled.** The download carries classification and handling
  metadata.

## Storage

`localStorage` stores the career goal and celebration effect. The auth token is
handled by the Axios interceptor. Do not cache an export or evidence payload in
the browser.

## Run and test

```bash
cd platform/frontend
npm run dev
npm test
```

Backend coverage: `tests/test_profile.py`, `tests/test_evidence_engine.py`,
`tests/test_consent_revocation.py`, `tests/test_certificate_verify.py`,
`tests/test_career_profile.py`, `tests/test_skill_dna.py`.

## Extension checklist

- Add the panel and the route.
- Add a consent check if the data is derived.
- Show the gate payload when `available: false`.
- Never compute a score in the component.
- Add a test for the empty, measured, and revoked states.
- Update the privacy notice if you add a new data category.

## Related

- [Backend privacy and consent](../../../backend/features/privacy-and-consent/README.md)
- [Backend competency and evidence](../../../backend/features/competency-and-evidence/README.md)
- [Backend Cyber DNA](../../../backend/features/cyber-dna/README.md)
- [Career Atlas and momentum](../../../../docs/CAREER-ATLAS-AND-MOMENTUM.md)
