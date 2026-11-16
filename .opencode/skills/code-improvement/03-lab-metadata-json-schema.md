# Task: Lab metadata JSON Schema + CI validator

## Why
There are 191 `lab.yaml` metadata files across the lab tree, hand-edited with no shared contract. `platform/backend/scripts/discover_labs.py` reads keys from them (`name`, `description`, `scenario`, `difficulty`, `category`, `duration_minutes`, `objectives`, `hints`, `tools`, `hostnames`, `workbook`, `visibility`, `flag`), but real files use different names in places (e.g. `title` instead of `name`, `estimated_time` instead of `duration_minutes`). Typos and key drift are currently silent: a lab simply fails to load or loads with missing fields.

## Hard rules (do not violate)
1. **The schema describes what the loader actually consumes.** Before writing the schema, audit both sides: (a) every key `discover_labs.py` reads, and (b) the union of keys used across all 191 `lab.yaml` files. The JSON Schema's `required`/`properties` must match the loader's contract.
2. **Reconcile the drift deliberately.** For each mismatched pair (`title` vs `name`, `estimated_time` vs `duration_minutes`), pick ONE canonical key — prefer what the majority of lab files already use — and make the other side conform: either update `discover_labs.py` to read the canonical key, or rewrite the minority of lab files. Do not leave dual-key support in the loader unless you add an explicit, logged deprecation warning.
3. **Fail CI on errors, warn on unknown keys.** Unknown/typo'd keys are the whole point of this task: they must surface. Missing required fields = hard error. Also validate value types (e.g. `difficulty` is one of the allowed enum values — read the actual set from `discover_labs.py` or the codebase, do not invent one; `objectives` is a non-empty list of strings where required).
4. **Do not change lab content.** Fixing a key name in a `lab.yaml` is allowed; changing descriptions, objectives text, hints, or flags is NOT part of this task.
5. **No new heavy dependencies.** Use `jsonschema` + `PyYAML` (add to `requirements.txt` only if missing — check first).

## Deliverables
1. `platform/backend/lab_metadata.schema.json` — JSON Schema draft 2020-12 for a single `lab.yaml`. Include `$schema`, `title`, per-property `description`, `additionalProperties: false` (so typos become errors), and an enum for any constrained string field.
2. `platform/backend/scripts/validate_lab_metadata.py` — CLI script that:
   - walks the repo for all `lab.yaml` files,
   - parses each with PyYAML (clear error on YAML syntax failure, file + line),
   - validates against the schema,
   - prints a per-file report; exits non-zero if any file fails.
3. CI step in `.github/workflows/ci.yml` inside the existing `backend` job (after Lint, before/after Test — your choice): run the validator on the whole repo and fail the build on errors.

## Procedure
1. Audit: list every key used across all 191 files (`grep -rhoP '^[A-Za-z_]+:' */**/lab.yaml | sort | uniq -c` or a quick Python one-liner) and every key `discover_labs.py` reads. Write the mismatch table into your working notes.
2. Decide canonical keys (majority wins); apply the minimal conforming change on the minority side.
3. Write the schema, then the validator, then iterate until all 191 files pass.
4. Add the CI step; run `python scripts/validate_lab_metadata.py` locally to confirm it passes and that a deliberately broken temp file makes it fail (delete the temp file after).

## Definition of done
- [ ] All 191 `lab.yaml` files validate clean.
- [ ] A typo'd key in any `lab.yaml` fails local validation AND would fail CI.
- [ ] `discover_labs.py` loads every lab successfully after the key reconciliation (run it or its test if one exists).
- [ ] `ruff check app scripts` clean; CI green on a pushed branch.

## Commit shape
Up to 3 commits: (1) key-name reconciliation, (2) schema + validator script, (3) CI wiring.
