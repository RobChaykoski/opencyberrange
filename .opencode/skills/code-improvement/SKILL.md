---
name: code-improvement
description: Use when planning or executing a backend refactor, schema-contract change, or test-coverage completion in OpenCyberRange. Covers zero-drift model and schema package splits, strict lab metadata validation, and router-to-test coverage with DB-backed behavioural tests.
argument-hint: "[task or brief name]"
---

# Code Improvement

A repeatable workflow for structural backend work where the risk is not the new
code but the silent drift it can introduce. The briefs in this directory are
worked examples; read the one that matches the task before touching code.

## When to Use

- Splitting a large backend module into a package without changing its wire or
  database contract.
- Changing a schema or metadata contract that many files depend on.
- Auditing routers against the test suite and filling missing endpoint coverage.
- Any refactor where "it imports and the tests pass" is not enough evidence.

## Briefs

| Brief | Use for |
|---|---|
| [Split models package](01-split-models-package.md) | Moving ORM classes into domain modules with zero Alembic/schema drift |
| [Split schemas package](02-split-schemas-package.md) | Moving Pydantic models while preserving every import and JSON schema |
| [Lab metadata schema](03-lab-metadata-json-schema.md) | Enforcing `lab.yaml` with a JSON Schema and CI validator |
| [Test coverage completion](04-test-coverage-completion.md) | Router coverage audit and DB-backed tests for write/auth paths |

Treat a brief as a contract, not a suggestion. If the codebase has changed since
the brief was written, update the plan to preserve the brief's invariants rather
than copying its assumptions.

## Workflow

1. **Inventory before editing.** Use AST/regex scans to list classes, routes,
   imports, tables, and test files. Record the baseline before any change.
2. **Capture a fingerprint.** For a refactor, compute the before state that must
   not change: SQLAlchemy metadata (tables, columns, types, defaults, FKs,
   indexes, constraints), Pydantic `model_json_schema()`, OpenAPI, or a route
   table. Save it outside the tree.
3. **Move, don't rewrite.** Prefer mechanical extraction that preserves code,
   comments, and docstrings. Re-export every public name from the package
   `__init__.py`; do not edit call sites unless a name truly collides.
4. **Prove equivalence.** Recompute the fingerprint after the change and compare
   byte-for-byte where possible. Differences are regressions until explained.
5. **Test behaviour through the API.** For endpoint work, assert status, response
   shape, persisted effects, and authorization negatives. Use the existing
   `db` marker/fixtures and keep tests hermetic.
6. **Run the real suite.** `ruff check app tests`, the full backend suite with
   `TEST_DATABASE_URL`, and the frontend build when UI changes. Do not treat a
   skipped DB test as a pass.
7. **Commit in reviewable batches.** One concern per commit, with the evidence
   (fingerprint match, test count, CI status) in the message. Push and confirm
   CI before calling it done.

## Hard Rules

- No API, schema, or database contract change during a pure refactor.
- No import breakage: re-export the old surface from the new package.
- No hidden dual-key support in a loader unless it logs a deprecation warning.
- Tests must not depend on execution order or data from another test.
- Do not weaken authorization or privacy controls to make a test pass.
- If a task exposes a real bug, add a regression test first, then fix the
  smallest surface that explains it.

## Definition of Done

- [ ] Baseline fingerprint captured and post-change fingerprint matches, or every
      difference is intentional and documented.
- [ ] Existing public imports still work.
- [ ] New/changed behaviour has a focused test, including the negative/auth path.
- [ ] `ruff check app tests` clean; full suite green with a real database.
- [ ] Frontend lint/build green when UI changed.
- [ ] Docs and manual pages updated when the user-visible contract changed.
- [ ] Pushed and CI green.
