# Release 5.59.0 deliverables

Release date: **2026-11-27**  
Tag: `v5.59.0`  
Base: `v5.58.1`

## Delivered

| Item | Evidence |
|---|---|
| Capstone Builder editor | `/capstone-builder`; validation gate, waivers, objectives, labs, assessments, deliverables, evidence map |
| Capstone plan exports | `GET /api/capstones/plans/{id}/export.md` and `.pdf`; editor download actions |
| Per-session flags for 149 labs | `flag_path`/`flag_service`/`flag_command`; `flag_mode: write\|replace`; launcher creates the parent directory |
| Replace mode | Swaps the flag inside a report, log, history file, page, or configuration without destroying it |
| Runtime verifier | `scripts/verify-flag-render.sh`; 22 labs verified on the development host |
| Flag-exposure audit | `scripts/audit_flag_exposure.py --fail-on-leaks` in the Quality workflow |
| Tooling and governance docs | `docs/OSINT-RESOURCES.md`, `docs/LEGAL-READINESS.md`, `docs/UPSTREAM-LICENSE-PERMISSION-REQUEST.md`, `docs/FLAG-EXPOSURE.md` |

## Verification

- Backend pytest: 679 passed, 578 skipped locally.
- Frontend: 81 tests; lint, i18n budget, and build pass.
- Labs: 222 definitions; schema, lint, manifests, and outcomes current.
- Flag audit: 73 static labs, 0 leaked answers; publication audit clean.
- CI and Quality checks: pass at `9ac8a755`.

## Residual risks

- 73 labs still publish a static flag; the audit and rotation plan are in `docs/FLAG-EXPOSURE.md`.
- Capstone publication to a course and LMS packaging remain.
- The licence stays PolyForm Noncommercial until the upstream author gives written permission.
