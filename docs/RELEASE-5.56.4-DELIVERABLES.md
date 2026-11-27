# Release 5.56.4 deliverables

Release date: **2026-11-26**  
Tag: `v5.56.4`  
Base: `v5.56.3`

## Delivered

| Item | Evidence |
|---|---|
| Security test alignment | 4 failing tests updated for break-glass approval, 222 contracts, MFA recovery setup |
| API manual | `Manual-Lite/11_API_Reference/index.md` regenerated for `/api/admin/security/rbac/drift` |
| i18n baseline | `platform/frontend/scripts/ui-string-baseline.json` updated by one reviewed label |

## Verification

- CI: backend, frontend, compose, images — pass.
- Backend pytest: 671 passed, 569 skipped.
- Supply-chain lock: signed and verified.
- Runtime code is unchanged from 5.56.3.

## Follow-ups

- Production deployment of the 5.56.3 security fixes is performed with this tag.
- Passkeys and mandatory privileged MFA remain Release 6 scope.
