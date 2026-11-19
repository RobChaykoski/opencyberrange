# Capstone runbook (training lab)

This runbook uses the dev-only training stack in `deploy/ecosystem-test`. It is
for synthetic exercises only. Read `docs/TRAINING-ECOSYSTEM.md` first.

## One-time setup

On the development host:

```bash
bash scripts/ecosystem_seed/seed_all.sh
bash scripts/ecosystem_seed/seed_ocr.sh
```

The first command seeds Moodle, Authentik, and NetBox. The second creates the
matching `OCR-CAP-COHORT` course in the dev range, enrols the fake students, and
assigns the mentor, teaching assistant, and co-instructor.

## Single-student capstone

**Goal:** one learner completes an investigation and defends it.

1. In Moodle, open `Capstone: Single-Student Security Operations`
   (`OCR-CAP-SINGLE`).
2. Confirm the learner is enrolled as `student` and the mentor is enrolled as
   `teacher`.
3. Open the `Capstone brief` page and assign the scenario.
4. The learner uses the training stack only:
   - Moodle for the brief and submission.
   - Authentik for group and application access.
   - NetBox for the synthetic asset map.
5. Evidence to collect:
   - ordered timeline;
   - system and time for each evidence item;
   - one containment action and one hardening action;
   - a short verbal defence.
6. In the dev OpenCyberRange instance, confirm the mentor report shows only the
   assigned learner and the small-cell suppression still applies.

**Pass condition:** the learner can explain what happened, cite evidence, and
separate observation from inference.

## Multi-student cohort capstone

**Goal:** two teams produce one joint defence.

1. In Moodle, open `Capstone: Multi-Student Cohort Defence`
   (`OCR-CAP-COHORT`).
2. Confirm `Cohort A` and `Cohort B` each contain the intended learners.
3. Assign `instructor01` as the instructor, `mentor01` as mentor, and `ta01` as
   teaching assistant.
4. Split the work:
   - **Cohort A:** detection, endpoint, and network evidence.
   - **Cohort B:** identity, asset ownership, and access review.
5. Each team records findings in Moodle; the cohort produces one joint timeline
   and one joint defence.
6. In the dev OpenCyberRange instance, confirm:
   - the mentor sees only assigned learners;
   - the teaching assistant sees only assigned-course lab health;
   - the auditor and privacy office views remain aggregate;
   - exports carry purpose, owner, audience, retention, and classification.

**Pass condition:** the joint brief has one timeline, named owners, three
evidence-backed findings, and one coherent defence.

## Verified access matrix (dev)

Checked against the seeded `OCR-CAP-COHORT` course on 19 November 2026:

| Account | Course reports | Privacy dashboard | Audit dashboard |
|---|---:|---:|---:|
| `student01` | 403 | 403 | 403 |
| `mentor01` | 200 | — | — |
| `ta01` | 200 | — | — |
| `instructor01` | 200 | — | — |
| `privacy01` | — | 200 | 403 |
| `auditor01` | — | 403 | 200 |

This confirms the role boundaries without exposing real data. Re-run the same
checks after a seed or policy change.

Cross-course scope is checked with a second course that is not assigned to the
mentor or teaching assistant:

| Course | `student01` | `mentor01` | `ta01` | `instructor01` |
|---|---:|---:|---:|---:|
| `OCR-CAP-COHORT` | 403 | 200 | 200 | 200 |
| `OCR-CAP-SINGLE` | 403 | 403 | 403 | 200 |

## Acceptance checks

- Moodle login page responds and shows the three training courses.
- The `OpenCyberRange capstone lab` LTI activity launches through the OIDC flow
  and returns the OCR ticket callback.
- Capstone brief pages are present in both capstone courses.
- Authentik shows the `ocr-*` groups and the fake users.
- NetBox shows the `Training (synthetic)` tenant, five devices, and three
  prefixes.
- Ralph and Fleet are reachable; any data added there is fake.
- The training stack is not referenced by production configuration.
- No production credentials or records exist anywhere in the stack.

## Reset between cohorts

```bash
cd deploy/ecosystem-test
docker compose --profile sso --profile assets --profile endpoint down -v
docker compose up -d
docker compose --profile sso --profile assets --profile endpoint up -d
# initialise Fleet once
docker compose --profile endpoint run --rm -T --entrypoint /bin/sh fleet -c 'fleet prepare db' < /dev/null
bash ../../scripts/ecosystem_seed/seed_all.sh
```

The reset is destructive by design. It removes only lab volumes.
