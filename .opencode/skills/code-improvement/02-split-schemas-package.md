# Task: Split `app/schemas.py` into an `app/schemas/` package

## Why
`platform/backend/app/schemas.py` is ~1,010 lines of Pydantic models in one module. Routers and services import from it by name; the file has grown past the point where finding a model or spotting a duplicated field is easy.

## Hard rules (do not violate)
1. **Wire compatibility.** Every request/response body must serialize exactly as before: same field names, types, defaults, aliases, `Field(...)` constraints, and validators. This is a reorganization only — no API change. If you notice an actual bug in a schema, do NOT fix it here; note it for a follow-up.
2. **Same import surface.** Routers/services use both `from app.schemas import X` and module-style access. The new `app/schemas/__init__.py` MUST re-export every public model (explicit `__all__`) so no importing file needs to change.
3. **Pydantic v2 idioms only.** Keep existing `model_config`, `field_validator`/`model_validator` exactly as written. Do not introduce v1-style `class Config` or `@validator`.
4. **No logic in schemas.** Schemas stay declarative: no DB access, no service calls, no I/O in validators beyond pure value transforms (the existing pattern).
5. **Style.** `ruff check app` clean. Keep docstrings on non-obvious models.

## Procedure
1. Read all of `app/schemas.py`. Group models by the domain they serve — mirror the model domains used in task 01 where names align (auth, lab, course, lti, survey, plus `common.py` for shared bits like pagination envelopes or generic ID/response wrappers if present).
2. Create `app/schemas/` package with one module per domain (~5–9 modules). Move classes verbatim; add each module's own imports (`pydantic`, `datetime`, `enum`, etc.).
3. Write `app/schemas/__init__.py` re-exporting every public model with an explicit `__all__`.
4. Delete old `app/schemas.py` only once the package resolves all existing imports.
5. Run the verification suite below.

## Definition of done (all must pass)
- [ ] `python -c "import app.schemas as s; print(len(s.__all__))"` equals the number of public classes in the old module (record that count first).
- [ ] Every router module still imports cleanly: `python -c "from app.main import app"` (or whatever the FastAPI entrypoint is) succeeds.
- [ ] `ruff check app` clean.
- [ ] Full backend test suite green (`pytest -q` with `TEST_DATABASE_URL` pointed at a local Postgres 17; CI does this automatically against its postgres service — push and confirm CI passes).
- [ ] Spot-check one GET and one POST endpoint response shape against a pre-split sample (e.g. hit `/api/v1/courses` locally or via an existing test) to confirm identical JSON keys.

## Commit shape
One commit: "refactor(backend): split schemas.py into app/schemas package" with the class-per-module map in the body.
