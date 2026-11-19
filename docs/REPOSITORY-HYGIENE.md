# Repository hygiene

A record of what was cleaned, what was archived, and what is deliberately kept.

## Root directory

Required GitHub community and policy files stay at the root because GitHub
surfaces them there and contributors expect them:

| File | Why it stays |
|---|---|
| `README.md`, `LICENSE`, `NOTICE` | Identity, licence, and attribution |
| `SECURITY.md` | Private vulnerability reporting and supported versions |
| `CONTRIBUTING.md` | Setup, tests, CLA, documentation checks |
| `CODE_OF_CONDUCT.md` | Community and event conduct |
| `PRIVACY.md`, `SUPPORT.md` | Plain-language privacy and support routes |
| `CHANGELOG.md` | Release history |
| `LICENSING.md`, `BUILD_NOTICE.md`, `THIRD_PARTY_NOTICES.md` | Licence and provenance |
| `README-UPGRADE.md` | Upgrade path for existing hosts |
| `versions.yaml`, `wikis.yaml` | Version and wiki configuration |

Temporary session notes, migration journals, and one-off plans do not belong at
the root. The completed ones are in [`docs/archive/`](archive/README.md).

## Archive

Fifteen completed documents were moved to `docs/archive/` with an index:
cutover, 2.7.0 plan, upgrade plan, UI verification, Release 4 close-out and
hotfix, V1 release, the Wave documents, the 5.0.1 security review, the 2026-11
hardening record, the local Release 5 stack, and the production validation
matrix. `MOVE-TO-OPENCYBER-NEXT.md` was merged into the cutover record and
deleted. Heavily referenced V2/V3 program history stays in place and is listed
in the archive index.

## Images and screenshots

- The manual images were audited. The sampled admin, activity, session, course,
  and profile screenshots use synthetic names (`alex_chen`, `jordan_lee`,
  `sso-student`) and `example.edu` addresses. No real learner data was found.
- `Manual-Lite/04_Admin_Guide/img/admin-diagnostics.png` had no reference and
  was removed.
- `Manual-Lite/assets/favicon.png` and
  `Manual-Lite/assets/opencyberrange-logo.png` are theme assets referenced by
  MkDocs, not orphans.
- `scripts/check-doc-assets.py` passes for every referenced image.
- The screenshots were captured on an older build (footer `v5`, 149 exercises),
  so a refresh is pending operator demo credentials. The procedure and the
  privacy rules are in [Manual screenshots](MANUAL-SCREENSHOTS.md).

## Scripts under review

These scripts are not named by CI, a workflow, or a document. They are **not**
deleted because several are manual maintenance tools. An owner should confirm
each before removal:

- `scripts/build-workbook-wikis.py` — used by the wiki builder image; keep.
- `scripts/check-mojibake.py`, `check-mojibake-diff.py`, `find-mojibake.py`,
  `fix-mojibake.py` — encoding maintenance; keep or retire together.
- `scripts/check-release-routes.py`, `scripts/lab_build_hash.py`,
  `scripts/lint_sql_safety.py` — focused review tools.
- `scripts/generate-framework-docs.py`, `generate-osint-qr.py`,
  `generate-review-html.py`, `generate-review-pdfs.py` — one-off generators.
- `platform/scripts/harden-firewall.sh`, `init_database.sh`, `manage-users.sh`
  — manual operations helpers; keep unless the runbook stops using them.

## Residual test accounts

- `smoke_tester` was removed from production with the erasure ledger, audit
  record, and security event (48 → 47 users). Real users and learner data were
  preserved.
- `tester` remains. Its personal-looking email is ambiguous, so it is not
  treated as test-only without a separate confirmation.

## Workbook coverage

The 19 new pathway labs now have workbook chapters
(`CH_WIN11_AD_Pathway`, `CH_WEB11_AppSec_Pathway`); coverage is **201 of 210**.
The remaining 9 labs have no workbook by design.

## Migrations and CI

- The Alembic revision graph is linear and ends at
  `0046_course_staff`; there is no abandoned migration head.
- All workflows in `.github/workflows/` have an active trigger. `lab-harness`
  and `ui-smoke` are on-demand/verification jobs, not dead files.
- The supply-chain lock and the runtime integrity manifest are regenerated for
  210 labs.

## Rule

Delete or move a file only after `rg` shows no remaining reference and the link,
asset, metadata, and strict-build checks pass. Record the removal here.
