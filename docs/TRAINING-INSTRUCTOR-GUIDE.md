# Training instructor guide

This guide is for running a single-student or cohort capstone in the dev-only
training lab. It uses synthetic data only.

## Before the cohort

On the development host:

```bash
cd ~/opencyberrange
git pull --ff-only origin main
bash scripts/ecosystem_seed/seed_all.sh
bash scripts/ecosystem_seed/seed_ocr.sh
bash scripts/ecosystem_seed/seed_lti.sh
bash scripts/validate-ecosystem-test.sh
```

The last command must report `VALIDATION PASSED`. It checks Moodle, Moodle TLS,
Authentik, NetBox, Ralph, and Fleet.

## Moodle

| Course | Use |
|---|---|
| `OCR-CAP-SINGLE` | Single-student capstone |
| `OCR-CAP-COHORT` | Cohort capstone with two teams |
| `OCR-FOUND` | Foundations and lab guide |

Each capstone course has a brief and a scenario pack. The scenario pack uses
only documentation IP ranges and fake assets from NetBox.

Staff accounts: `instructor01`, `mentor01`, `ta01`.
Learner accounts: `student01`..`student08`.
The lab password is set by `TRAINING_PASSWORD` in `deploy/ecosystem-test/.env`.

## OpenCyberRange dev

`seed_ocr.sh` creates:

- `OCR-CAP-COHORT` with all learners and the mentor/TA/co-instructor staff rows.
- `OCR-CAP-SINGLE` with only the first four learners and no mentor/TA rows, so
  cross-course scope denial can be demonstrated.

The role matrix and the seed results are recorded in
`docs/TRAINING-CAPSTONES.md` and `docs/TRAINING-VALIDATION.md`.

## Run a single-student capstone

1. Open `OCR-CAP-SINGLE` in Moodle and assign the brief.
2. The learner uses the scenario pack, NetBox, and Authentik.
3. Collect the timeline, evidence list, containment action, and hardening action.
4. Confirm the mentor report shows only the assigned learner.
5. Require a short verbal defence.

## Run a cohort capstone

1. Open `OCR-CAP-COHORT` and confirm `Cohort A` and `Cohort B`.
2. Assign `instructor01` (instructor), `mentor01` (mentor), `ta01` (TA).
3. Cohort A owns authentication/endpoint evidence; Cohort B owns asset and
   identity change evidence.
4. The cohort submits one joint timeline, three evidence-backed findings, and one
   joint defence.
5. Confirm the mentor sees only assigned learners and the TA sees only the
   assigned course.

## LTI launch

The `OpenCyberRange capstone lab` activity in `OCR-CAP-COHORT` launches the OCR
dev range as an LTI 1.3 tool. The launch flow is:

```text
Moodle activity -> OCR /api/lti/login -> Moodle auth -> id_token
  -> OCR /api/lti/launch -> /lti/callback?ticket=...
```

If the launch fails after recreating the OCR backend, re-run
`bash scripts/ecosystem_seed/seed_lti.sh` to restore the runtime CA trust.

## Between cohorts

```bash
bash scripts/ecosystem_seed/reset_training_lab.sh --yes
```

This deletes the training volumes and reseeds Moodle, Authentik, NetBox, Ralph,
Fleet, the OCR dev courses, and LTI. It does not touch production.

## Known limits

- Fleet 4.95.0 panics when writing enroll secrets, so a fake osquery host cannot
  be enrolled until a fixed image is pinned. Fleet itself is healthy.
- OpenIAM is fetched but not started; it needs a dedicated Docker Swarm lab host.
  See `docs/OPENIAM-TEST-STACK.md`.
- Run Moodle CLI commands as the `daemon` user, not root. A root cache purge
  creates root-owned lock files and Moodle then returns 500 or
  `Unable to acquire a lock for caching`. Fix ownership with
  `chown -R daemon:root /bitnami/moodledata /bitnami/moodle`, then purge caches
  as `daemon`.

## Safety

- Never connect the training stack to production, a real identity provider, real
  SMTP, or real learner/patient records.
- Keep the lab ports on the dev network.
- Treat every `.env` value as a lab credential and never reuse it.
