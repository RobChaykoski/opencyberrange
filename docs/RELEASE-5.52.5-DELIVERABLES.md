# Release 5.52.5 deliverables

Status: **released and deployed** to development and production on 26 November
2026.

| Item | Value |
|---|---|
| Version | `5.52.5` |
| Signed tag | `v5.52.5` |
| Release date | 26 November 2026 |
| Alembic | `0067_course_content_rls` (no migration) |
| Lab definitions | `217` |
| Workbook-mapped labs | `206` |
| Supersedes | `5.52.4` |

## Fixed and changed

| Area | Detail |
|---|---|
| RangeBox proxy networks | The per-user `/29` was reused by every lab, so starting lab B while lab A's proxy network still existed produced `invalid pool request: Pool overlaps with other one on this address space` and the new desktop had no VNC path. The allocator now tries the base block and then every other `/29` in the user's `/24`. |
| VNC peer addresses | The RangeBox and backend addresses are derived from the network's real subnet (`network + 2/+3`), so a block such as `10.200.212.8/29` uses `.10` and `.11` instead of an out-of-subnet `.2`/`.3`. |
| Workbook origin | Production now sets `wiki_origin` to `https://ctfd.swocts.com:8443`. The workbook iframe is cross-origin, gets `allow-same-origin`, and MkDocs Material no longer throws `SecurityError` on `localStorage`. |
| Regression test | Five unit tests cover the allocator, peer-address derivation, reuse of an existing network, `get_rangebox_ip`, and exhaustion. |

## Verification

| Check | Result |
|---|---|
| Backend tests | `642 passed`, `559 skipped` (DB-backed tests need `TEST_DATABASE_URL`) |
| Allocator tests | `5 passed` |
| Workbook as `kokofan` | iframe on `https://ctfd.swocts.com:8443`, titles and 5.5k character bodies for L1.1 and L1.2, **0 console errors** |
| RangeBox start | `rangebox_212_…` healthy, VNC status **Connected**, workbook visible alongside the desktop |
| Race reproduction | Stop session 297, immediately spawn 298: cleanup ran in the background; the session rows settled to `stopped`/`running` without a failed spawn |
| Frontend tests | `56 passed` (21 files) |
| Frontend lint | `0 errors` |
| Frontend build | Passed |
| UI string budget | Passed (`5,412` budgeted strings) |
| Bundle budget | Passed |
| Link check | `1,225` Markdown files, no broken links |
| Supply-chain lock | Updated and signed |

## Deployment

| Environment | Version | Status |
|---|---|---|
| Development | `5.52.5` | Deployed and verified |
| Production | `5.52.5` | Deployed and verified |

Post-deploy checks: `/api/version` reports `5.52.5` on both hosts, backend and
frontend containers healthy, `nginx -t` passes, and the production wiki rebuilt
14 sites. Rollback images are tagged `pre-v5.52.5` on production; development
rolls back by rebuilding `v5.52.4`.

## Operational note

The stop endpoint marks the session `stopping` and runs Docker teardown in a
background task; a new spawn is allowed while that finishes. The workload is
safe now because the lab and proxy networks are allocated around whatever is
still present, but the session row can briefly show `stopping` after the UI
closes. Do not assume the desktop is gone until `stopped` and the `lab_*`
containers are removed.
