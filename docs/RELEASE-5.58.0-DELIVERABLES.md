# Release 5.58.0 deliverables

Release date: **2026-11-27**  
Tag: `v5.58.0`  
Base: `v5.57.0`

## Delivered

| Item | Evidence |
|---|---|
| Per-session flags for baked labs | `lab_metadata.schema.json` (`flag_path`, `flag_service`, `flag_command`, `flag_owner`); session entrypoint wrapper; 112 of 222 labs rotate |
| Flag-render inference | `scripts/infer_flag_render.py`; 32 baked labs annotated |
| LAB_FLAG for runtime labs | Four OT PLC servers and the OSINT canary read `LAB_FLAG` with a static fallback |
| Digest-pinned lab base images | `scripts/pin_lab_base_images.py`; 225 references in 218 Dockerfiles; image-pin checker clean |
| Lab friction report | `scripts/lab_friction_report.py`; course-scoped CSV |
| LMS gradebook exports | Canvas, Brightspace, Moodle, generic layouts; scoreboard scoring model |

## Verification

- Backend pytest: 677 passed, 576 skipped.
- Lab metadata: 222/222 validated; `lint_labs.py --check`: 0 errors, 0 warnings.
- Frontend lint: 0 errors; i18n and bundle budgets pass.
- `generate-api-manual.py --check`, `generate-lab-outcomes.py --check`,
  `export-openapi.py --check`: pass.
- `check-links.py --mkdocs`, `documentation_map.py --check`: pass.
- CI and Quality checks: pass at `551bfead`.

## Residual risks

- 110 labs still use a baked/static flag; 112 of 222 rotate per session.
- Competency contracts still need subject-matter review.
- Release 6 scope counts remain to be refreshed in `RELEASE-6-SCOPE.md`.
