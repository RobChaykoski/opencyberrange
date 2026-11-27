# Wiki and workbook (frontend)

## Purpose

Serve the learner-facing workbook and course wiki. The wiki is a build artifact,
not part of the SPA bundle. The frontend shows it in a framed pane or a
dedicated origin and keeps access scoped with an HttpOnly cookie.

## Routes and views

| Route | View | Notes |
|---|---|---|
| `/workbooks` | `WorkbooksLanding.vue` | workbook landing |
| `/workbook-answers` | `WorkbookAnswers.vue` | answer workspace |
| `/exercises/:trackSlug/briefing` | `ExerciseBriefing.vue` | embeds the chapter |
| `/admin` (Workbook tab) | `Admin.vue` | upload, build, delete |

The wiki itself is served at `/wiki` by nginx from the `wiki_data` volume. A
separate 8443 origin can be configured with `WIKI_BASE_URL`.

## Build and publish

```bash
cd platform
docker compose --env-file .env -f docker-compose.dev.yml --profile tools \
  run --rm wiki-builder
```

The builder runs MkDocs with the pinned toolchain and writes the namespaced tree
to `wiki_data`. The frontend mounts it read-only.

Manual-Lite has its own config:

```bash
python -m mkdocs build -f mkdocs-manual-lite.yml --strict
```

## API calls

| Action | Endpoint |
|---|---|
| List chapters | `GET /api/admin/workbook/chapters` |
| Upload ZIP | `POST /api/admin/workbook/upload` |
| Build | `POST /api/admin/workbook/build`, `/build-all-course-wikis` |
| Delete chapter | `DELETE /api/admin/workbook/chapter/{dir}` |
| Answers | `GET/PUT /api/workbook-answers/{lab_slug}` |
| Wiki cookie | `POST /api/auth/wiki-cookie`, `DELETE /api/auth/wiki-cookie` |

## Behaviour that matters

- **Separate origin.** The workbook may run on 8443 with its own CSP and cookie
  scope. Do not widen the SPA frame policy more than needed.
- **HttpOnly cookie.** `wiki_session` is not readable by JavaScript.
- **Read-only mount.** nginx serves the volume read-only; the builder writes it.
- **No live learner rows in the wiki.** The workbook is public or course-scoped
  content, not a report.
- **Broken links fail CI.** `check-links.py --mkdocs` must pass.
- **Minor-safe.** The high-school config excludes content outside its scope.

## Storage

| Store | Data |
|---|---|
| `wiki_data` | built MkDocs tree |
| `workbook_data` | builder inputs and Exercise Studio state |
| HttpOnly cookie | wiki session |

## Run and test

```bash
python scripts/check-links.py --mkdocs
python scripts/check-doc-assets.py
python scripts/check-minor-safe.py
bash scripts/build-wiki.sh
```

## Extension checklist

- Add the page to the correct MkDocs nav.
- Run the link check and the minor-safe check.
- Keep the manual and workbook origins separate.
- Do not hand-edit a generated page.
- Do not put a learner row, secret, or live address in a wiki page.

## Related

- [Wiki subsystem](../../../wiki/subsystem-overview.md)
- [MkDocs governance](../../../../docs/MKDOCS-GOVERNANCE.md)
- [Manual publishing](../../../../docs/MANUAL-PUBLISHING.md)
- [Backend uploads and workbook](../../../backend/features/uploads-and-workbook/README.md)
