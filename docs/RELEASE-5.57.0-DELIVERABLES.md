# Release 5.57.0 deliverables

Release date: **2026-11-27**  
Tag: `v5.57.0`  
Base: `v5.56.4`

## Delivered

| Item | Evidence |
|---|---|
| Shared metadata across 222 labs | `platform/backend/lab_metadata.schema.json`; `scripts/enrich_lab_metadata.py` |
| Lab quality gate | `scripts/lint_labs.py`; Quality CI |
| Workbook normalization | `scripts/normalize_workbook_sections.py`; 20 pages updated |
| Instructor friction report | `scripts/lab_friction_report.py` |
| Copyable workspace context | `TrackDetail.vue`; `CopyCode.vue` |
| Per-session flags | `labs.py` `_session_flag_env`; `docker_manager.create_lab_environment`; grader fallback |
| Skill DNA placeholder guard | `skill_dna._completion_rows`; `test_skill_dna.py` |
| Celebration Wall coverage | `test_celebrations.py` |

## Verification

- Backend pytest: 675 passed, 573 skipped.
- DB-backed session-flag and flag-submit tests: 15 passed.
- Lab schema: 222/222; `validate-lab`: 222 labs, 0 errors.
- `lab_qa --static`: 0 errors, 14 warnings.
- `lint_labs.py --check`: 0 errors, 1 warning (unpinned `nginx:alpine`).
- CI and Quality checks: pass.

## Residual risks

- 152 labs still use a baked/static flag; 70 of 222 rotate per session.
- 226 upstream image references remain tag-only.
- 197 competency contracts still need subject-matter review.
