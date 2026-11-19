# Training lab validation evidence

**Date:** 19 November 2026

**Environment:** development host `172.16.16.44`

**Release line:** 5.27.3

**Scope:** the dev-only training stack, the dev OpenCyberRange instance, and the
LTI launch path. Production was not involved.

## Results

| Check | Result | Evidence |
|---|---|---|
| Training validator | **PASS** | `failures: 0`; Moodle, Moodle DB, Moodle TLS, Authentik, NetBox, Ralph, Fleet |
| Moodle courses and pages | **PASS** | `mdl_page = 3`; `OCR-CAP-SINGLE`, `OCR-CAP-COHORT`, `OCR-FOUND` |
| Authentik population | **PASS** | 6 `ocr-*` groups, 13 synthetic users |
| NetBox inventory | **PASS** | Synthetic tenant, site, 5 devices, 3 prefixes |
| Ralph admin | **PASS** | Migrations applied; admin seeded from `RALPH_ADMIN_*` |
| Fleet admin | **PASS** | Setup endpoint completed; login and API token verified |
| Fleet fake host | **BLOCKED** | Fleet 4.95.0 panics with a nil pointer in `ApplyEnrollSecretSpec` when writing an enroll secret; the UI uses the same API path |
| LTI 1.3 launch | **PASS** | Moodle activity -> OCR `/api/lti/login` -> Moodle `/mod/lti/auth.php` -> signed `id_token` -> OCR `/api/lti/launch` -> `302 /lti/callback?ticket=...` |
| Course report scope | **PASS** | `student01` 403; `mentor01`, `ta01`, `instructor01` 200 on the assigned cohort course |
| Privacy/audit scope | **PASS** | `privacy01` privacy 200 / audit 403; `auditor01` privacy 403 / audit 200; `student01` both 403 |
| Cross-course scope | **PASS** | Mentor and TA 403 on `OCR-CAP-SINGLE`; the instructor 200 |
| NICE review | **PASS** | 6 DB-backed NICE tests; `POST /api/nice/labs/{lab_id}/review` present on dev |
| Full backend suite | **PASS** | 967 passed against a scratch PostgreSQL |
| Frontend build | **PASS** | `npm test` and `npm run build` |
| OpenIAM | **NOT STARTED** | Official Swarm-based multi-stack fetched; starting it requires `docker swarm init` and a dedicated lab host |
| Production impact | **NONE** | No training host, credential, SSO client, or LTI platform exists in production |

## Notes

- The LTI launch was repeated after recreating the OCR backend and re-running
  `scripts/ecosystem_seed/seed_lti.sh`.
- The certificate trust used for LTI is runtime-only. Re-run `seed_lti.sh` after
  recreating the Moodle or OCR containers.
- Fleet 4.95.0 has an upstream nil-pointer panic in `ApplyEnrollSecretSpec`.
  Until a fixed image is pinned, host enrollment is blocked; keep Fleet as a
  running UI and do not treat the missing host as a configuration error.
- All accounts, courses, devices, and alerts in this environment are synthetic.
