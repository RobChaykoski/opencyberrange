# Release 5.52.10 deliverables

Status: **release prepared**. Deployment evidence is recorded in
[`PRODUCTION-DEPLOYMENT-STATEMENT.md`](PRODUCTION-DEPLOYMENT-STATEMENT.md) after
the signed tag is applied.

| Item | Value |
|---|---|
| Version | `5.52.10` |
| Signed tag | `v5.52.10` |
| Release date | 26 November 2026 |
| Alembic | `0067_course_content_rls` (no migration) |
| Lab definitions | `217` |
| Workbook-mapped labs | `206` |
| Supersedes | `5.52.9` |

## Fixed

| Area | Detail |
|---|---|
| RangeBox proxy lookup | `get_rangebox_ip()` returns `None` when the proxy network or its subnet is missing instead of guessing the base `.2` address. With the per-block allocator, the base `.2` can belong to another lab. The VNC, status, and impersonation paths already handle `None` by failing closed or falling back to the standalone RangeBox. |
| Tests | Added coverage for a missing network, a network without a subnet, the legacy `/30` layout, and a manager without a Docker client. |

## Verification

| Check | Result |
|---|---|
| Backend tests | `655 passed`, `559 skipped` (DB-backed tests need `TEST_DATABASE_URL`) |
| RangeBox tests | `15 passed` across the image and proxy-network suites |
| Publication audit | `0 findings` |
| API manual | Current |
| Link check | `1,230` Markdown files, no broken links |
| Supply-chain lock | Signed; `142` files and `217` lab hashes match |

## Deployment

| Environment | Version | Status |
|---|---|---|
| Development | `5.52.10` | Pending |
| Production | `5.52.10` | Pending |
