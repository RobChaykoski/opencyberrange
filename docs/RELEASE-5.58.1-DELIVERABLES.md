# Release 5.58.1 deliverables

Release date: **2026-11-27**  
Tag: `v5.58.1`  
Base: `v5.58.0`

## Delivered

| Item | Evidence |
|---|---|
| Landing-page README | `README.md` (215 lines): pitch, hero screenshot, audience, workflow, quick start, editions, generated track table, attribution at the bottom |
| Aligned current claims | `COUNTS.md`, `SUPPORTED-VERSIONS.md`, `SECURITY.md`, `RELEASE-6-SCOPE.md`, `COMPETENCY-FRAMEWORK.md`, `OPEN-SOURCE-READINESS.md`, `NEXT-STEPS.md`, `docs/README.md` |
| Historical labels | `RELEASE-5-PRODUCTION-READINESS.md`, `RELEASE-5-SCOPE.md`, `HANDOFF-2026-11-26.md`, `RELEASE_NOTES.md` |
| Documentation navigation | Browse-by-intent table in `docs/README.md`; platform badge points at `RELEASES.md` |
| Punctuation repair | Four double-encoded sequences fixed in `SECURITY.md`, `SUPPORTED-VERSIONS.md`, the overview data dictionary, and the platform-settings page |

## Verification

- CI and Quality checks: pass at `117cfb36`.
- Backend pytest: 677 passed, 576 skipped locally.
- Links (809 files), doc assets (103), API manual, lab outcomes, manifests (222),
  lab metadata, curriculum docs, documentation map, publication audit (0
  findings), and MkDocs strict build: pass.
- Tenant isolation probe on development: `PASSED`.

## Residual risks

- Runtime behaviour is unchanged; the version string is the only code change.
- The structural documentation work (Diátaxis folders, markdownlint/UTF-8 CI,
  mkdocs config move) remains for a later change.
