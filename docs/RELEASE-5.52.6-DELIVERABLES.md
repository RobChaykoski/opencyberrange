# Release 5.52.6 deliverables

Status: **released and deployed** to development and production on 26 November
2026.

| Item | Value |
|---|---|
| Version | `5.52.6` |
| Signed tag | `v5.52.6` |
| Release date | 26 November 2026 |
| Alembic | `0067_course_content_rls` (no migration) |
| Lab definitions | `217` |
| Workbook-mapped labs | `206` |
| Supersedes | `5.52.5` |

## Fixed and changed

| Area | Detail |
|---|---|
| RangeBox reattach | A backend restart reattached only the base `/29` correctly. Sessions allocated to a later block were given an out-of-subnet `.3` address, so their VNC path stayed down. The reattach address is now derived from the network's real subnet. |
| Workbook origin default | A TLS deployment derives `https://<host>:8443` when `wiki_origin` is empty, so a fresh install no longer starts in the opaque same-origin sandbox that makes MkDocs Material throw `SecurityError` on `localStorage`. The saved setting still overrides the derived origin. |
| Course wiki framing | The dynamic `X-Wiki-Frame-Ancestor` value is now emitted for `/api/auth/wiki-access` and `/api/auth/wiki-admin-access` as well as `/api/auth/me`, so enrolled and admin course wikis frame on the same terms as the open range tracks. |
| Publication hygiene | Release notes use `https://<platform-host>:8443` instead of the live hostname, and the Arkime lab README no longer prints the flag. The publication audit reports no findings. |
| API manual | `Manual-Lite/11_API_Reference/index.md` is regenerated for the current OpenAPI schema. |

## Verification

| Check | Result |
|---|---|
| Backend tests | `651 passed`, `559 skipped` (DB-backed tests need `TEST_DATABASE_URL`) |
| New regression tests | `9` across the proxy reattach and workbook-origin paths |
| Publication audit | `0 findings` |
| API manual | Current (`generate-api-manual.py --check` passes) |
| Tenant isolation (development) | `PASSED`; 47 tables, 0 tables leaked |
| Frontend tests | `56 passed` (21 files) |
| Frontend lint | `0 errors` |
| Frontend build | Passed |
| UI string budget | Passed (`5,412` budgeted strings) |
| Bundle budget | Passed |
| Link check | `1,226` Markdown files, no broken links |
| Supply-chain lock | Signed; `142` files and `217` lab hashes match |

## Deployment

| Environment | Version | Status |
|---|---|---|
| Development | `5.52.6` | Deployed and verified |
| Production | `5.52.6` | Deployed and verified |

After deployment, record the `/api/version` result, container health, wiki
rebuild, backup path, and rollback image tags for both environments.
