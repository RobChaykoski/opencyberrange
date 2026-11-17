# Open-source readiness

A fresh-contributor review for the Community / Academic edition.

## Fresh-clone path

1. `git clone https://github.com/RobChaykoski/opencyberrange.git`
2. Read `README.md` and `docs/README.md`.
3. Copy `platform/.env.example` to `platform/.env` and fill the required secrets.
4. Build the stack with the deployment runbook:
   `docker compose -f docker-compose.dev.yml up --build`.
5. Run the backend suite with `TEST_DATABASE_URL` pointing at a throwaway
   PostgreSQL database.
6. Build the frontend with `npm ci && npm run build`.
7. Build the manual with
   `python -m mkdocs build -f mkdocs-manual-lite.yml --strict`.
8. Scan and start a lab from **Admin → Exercises**.

## Friction points found

| Friction | Impact | Where it is recorded |
|---|---|---|
| DB tests skip without `TEST_DATABASE_URL` | A new contributor may see fewer tests than CI | `CONTRIBUTING.md` |
| `LABS_HOST_PATH` must be absolute | Lab spawn fails on a relative path | `docs/DEPLOYMENT-RUNBOOK.md` |
| Lab files must be world-readable (`a+rX`) | A non-root backend silently skips labs it cannot read | `docs/REPOSITORY-HYGIENE.md` |
| Lab images are large | First lab launch is slow | `docs/DEPLOYMENT-TOPOLOGY-AND-SIZING.md` |
| Screenshot refresh needs demo credentials | Manual images can lag the release | `docs/MANUAL-SCREENSHOTS.md` |
| The live harness is long | 210-lab verification is not a quick local check | `docs/CURRICULUM-DRIFT-REPORT.md` |

## Score

| Criterion | Status |
|---|---|
| Stale roadmap references | **Cleared** — plan documents carry a Status banner; current pages point at the source of truth |
| Completed migration artifacts in root | **Cleared** — moved to `docs/archive/` |
| Undocumented scripts | **Recorded** — candidates listed in `docs/REPOSITORY-HYGIENE.md`; none deleted without an owner decision |
| Orphaned documentation | **Cleared** — `docs/README.md` and the category hubs cover the tree; unreferenced screenshot removed |
| Consistent naming and formatting | **Standardised** — see `.opencode/skills/documentation/SKILL.md` |
| Single source of truth | **Yes** — signed tag, `versions.yaml`, production statement, and `COUNTS.md` |

## Evidence

- Backend: **908 passed** on a clean PostgreSQL database.
- Frontend: **6 passed**; build passed.
- Labs: **210 definitions, 210 manifests, 210 contracts, 201 workbook-mapped**.
- `validate-lab.py --all`: **210 labs, 0 failed checks**.
- Live harness: all **19 new pathway labs** passed one clean run; the full
  210-lab, three-run harness remains.
- Metadata, outcomes, manifests, API manual, licence, external-dataset, and
  documentation-link checks: passed.
- MkDocs manual strict build: passed.

## Go / no-go

**Ready for the Community / Academic release.** The remaining items are not
code-readiness blockers but must not be described as complete:

- Independent penetration testing is **not commissioned**.
- The full 210-lab live harness still needs three clean runs.
- The manual screenshots need a refresh on the current build once demo
  credentials are available.
