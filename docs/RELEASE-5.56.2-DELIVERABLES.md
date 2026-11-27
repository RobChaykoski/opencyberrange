# Release 5.56.2 deliverables

Release date: **2026-11-26**  
Tag: `v5.56.2`  
Base: `v5.56.1`

## Delivered

| Item | Evidence |
|---|---|
| Karate API-testing chapter (`SWSEC02`) | Four labs, one shared target, workbook pages, tester manifests, competency contracts |
| Documentation governance | `docs/documentation/DOCUMENTATION-STANDARDS.md`, review form, register, generated group indexes, `scripts/documentation_map.py --check` |
| Developer onboarding guide | `.onboarding-docs/` with platform, subsystem, feature, storage, fixture, and deployment pages |
| Blackbox security suite | `security-tests/karate/`, 44 scenarios, runtime fixture creation and cleanup |
| Curriculum framework map | `validate-framework-map.py` passes for all 222 labs |
| Generated records | 222 contracts, 222 manifests, 211 workbook links, 197 pending reviews |

## Verification

- `python scripts/validate-lab.py --all --summary` — 222 clean.
- `python scripts/validate-framework-map.py` — PASS.
- `python scripts/validate-competency-contracts.py` — PASS.
- `python scripts/audit-publication.py --summary` — 0 findings.
- `python scripts/documentation_map.py --check` — PASS.
- `python scripts/check-links.py --mkdocs` — 0 broken links.
- `python scripts/check-links.py .onboarding-docs` — 0 broken links.
- Backend pytest — 671 passed, 562 skipped.
- Karate blackbox suite — 44/44 scenarios passed; cleanup `remaining=0`.
- Supply-chain lock — signed and verified.
- Integrity manifest — stable across two runs.

## Known follow-ups

- The 197 competency contracts still need subject-matter review.
- The Karate labs are provisional until a live student-tester walkthrough is
  recorded.
- Production deployment must be recorded in
  `PRODUCTION-DEPLOYMENT-STATEMENT.md` after it is performed.
