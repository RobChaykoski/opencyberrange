# Task: Split `app/models.py` into an `app/models/` package

## Why
`platform/backend/app/models.py` is ~2,178 lines with 72 ORM classes in one module. It is the single biggest maintenance hazard in the backend: every domain change touches one giant file, and Alembic autogenerate depends on all models being importable from one place.

## Hard rules (do not violate)
1. **Zero schema drift.** Table names, column types, nullability, defaults (`server_default=text(...)`), `CheckConstraint`, `UniqueConstraint`, `Index`, and `deferred` columns must remain byte-identical in what Alembic sees. This is a pure code reorganization — no DDL changes.
2. **Same `Base`.** Every model keeps inheriting from the same `Base` imported from `app.database`. Do not create a second declarative base.
3. **No import breakage.** ~89 files do `from app.models import X`. The new `app/models/__init__.py` MUST re-export every public class name so all existing imports keep working unchanged. Do not edit importing files unless a name genuinely collides between domain modules (if two domains define the same class name, rename in the domain module and add an alias in `__init__.py`).
4. **No circular imports.** Domain modules may import from `app.database` and sibling model modules only for type hints; all `ForeignKey("table.col")` references stay as string literals; all `relationship(...)` targets stay as strings. If a cycle appears, break it with `TYPE_CHECKING` guards.
5. **Alembic safety.** `alembic/env.py` must end up importing the `app.models` package (its `__init__`) so `Base.metadata` is fully populated before `upgrade()` and any autogenerate. Verify after the split.
6. **Style.** `ruff check app` must pass clean. Preserve existing docstrings/comments on classes and non-obvious columns — they encode intent (e.g. why `avatar_data` is stored inline).

## Procedure
1. Read all of `app/models.py`. Group the 72 classes into domain modules by their existing internal section comments / naming:
   - `app/models/auth.py` — User, sessions, MFA, SSO/identity, API keys, audit rows
   - `app/models/lab.py` — Lab, LabRun/attempt, progress, flags, hints, workbook state
   - `app/models/course.py` — Course, module, enrollment, curriculum, competitions, planning
   - `app/models/lti.py` — LTI deployment/context/resource models
   - `app/models/survey.py` — surveys, questions, responses, reviews, accommodations
   - `app/models/common.py` (optional) — shared mixins / timestamp columns if any exist
   Adjust boundaries to match what the file actually contains; the point is 6–10 modules of ~200–400 lines each, not a fixed list.
2. Create `app/models/` as a package. Move classes into the domain modules, keeping their imports (`Column`, `relationship`, `deferred`, `text`, etc.) at the top of each module.
3. Write `app/models/__init__.py`: import every public class from each domain module and re-export it (explicit `__all__` list). Add a docstring: "Package re-exports all ORM models; import models from `app.models` as before."
4. Delete the old `app/models.py` only after the package exists and imports resolve.
5. Run the full verification suite below and fix anything that fails before declaring done.

## Definition of done (all must pass)
- [ ] `python -c "import app.models; print(len(app.models.Base.metadata.tables))"` prints the same table count as before the split (record it first).
- [ ] `ruff check app` clean.
- [ ] Full backend test suite passes: from `platform/backend`, set `TEST_DATABASE_URL=postgresql://ocr_test:ocr_test@127.0.0.1:5432/ocr_test` (start a local postgres:17 or use the CI service) and run `pytest -q`. All ~97 test files green.
- [ ] Alembic check: `alembic upgrade head` succeeds on a fresh DB, and if you can run `alembic check` (or autogenerate into a throwaway migration), it produces **no** new operations. Delete any throwaway migration afterwards.
- [ ] No file outside `app/models/` needed modification (except `alembic/env.py` import path if it pointed at the old module).

## Commit shape
One commit: "refactor(backend): split models.py into app/models package" — include in the body the class-per-module map and the unchanged table count.
