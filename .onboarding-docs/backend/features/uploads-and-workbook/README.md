# Uploads and workbook

## Purpose

Import lab packages, upload workbook chapters, serve workbook answers, and build
the static wiki. Uploads are a high-risk surface; every path validates type,
size, archive structure, and authorization before writing.

## Code map

| Concern | Location |
|---|---|
| Workbook router | `platform/backend/app/routers/workbook.py` |
| Workbook answers | `platform/backend/app/routers/workbook_answers.py` |
| Instructor upload | `platform/backend/app/routers/instructor.py` (`/labs/upload`) |
| Admin lab import | `platform/backend/app/routers/admin.py` (`/labs/import`) |
| System restore upload | `platform/backend/app/routers/admin.py` (`/system/restore/upload`) |
| Workbook builder | `platform/backend/app/services/workbook_builder.py` |
| Lab upload | `platform/backend/app/services/lab_upload.py` |
| Exercise transfer | `platform/backend/app/services/exercise_transfer.py` |
| Model | `platform/backend/app/models/workbook.py` |

## API surface

| Method | Path | Notes |
|---|---|---|
| GET | `/api/admin/workbook/chapters` | list chapters |
| POST | `/api/admin/workbook/upload` | ZIP of Markdown, `chapter_dir` form field |
| POST | `/api/admin/workbook/build`, `/build-all-course-wikis` | rebuild |
| DELETE | `/api/admin/workbook/chapter/{dir}` | remove a chapter |
| GET/PUT | `/api/workbook-answers/{lab_slug}` | answer content |
| POST | `/api/admin/labs/import` | import a lab ZIP as a draft |
| POST | `/api/admin/system/restore/upload` | restore archive |
| POST | `/api/reports/verify` | public report verification upload |

## Behaviour that matters

- **Authorization first.** Student uploads return `403`; anonymous uploads
  return `401`. Admin/instructor dependencies are server-side.
- **Extension and size.** The workbook upload requires a `.zip` filename and
  caps the archive at 50 MB. Lab import has its own cap.
- **Archive safety.** `extract_upload` rejects traversal in `chapter_dir`, caps
  entries, caps per-file size, caps total uncompressed size, and sanitizes file
  names. Lab import validates the package schema.
- **No auto-publish.** Imported labs are drafts; a human approves them.
- **No execution on upload.** The upload path does not run the lab; the tester
  or a later spawn does.
- **Restore is administrative.** Restore upload is admin-only and should be
  audited and tested in a drill.

## Persistent state

| Store | Data |
|---|---|
| `workbook_data` | chapter files, studio state, erasure ledger |
| `wiki_data` | built site |
| `labs` / lab directories | imported lab definition and compose |
| `workbook_answers` | answer content per lab |
| `backups_data` | restored snapshots |
| `activity_events` | upload and build actions |

## Fixtures and tests

- Create a ZIP fixture and upload it in a test.
- Focused tests:

```bash
cd platform/backend
python -m pytest tests/test_zip_upload_hardening.py tests/test_workbook_api.py \
  tests/test_workbook_start.py tests/test_workbook_answers.py \
  tests/test_exercise_transfer.py tests/test_spreadsheet_safety.py -q
```

- Blackbox upload checks: `security-tests/karate/features/04-upload-security.feature`.

## Extension checklist

- Validate extension, content type, and magic bytes separately.
- Enforce a size cap before reading the whole body.
- Reject traversal and absolute paths.
- Cap archive entries and uncompressed size.
- Keep the write inside the intended directory.
- Add a test for each rejection path.
- Never trust the client filename.

## Related

- [Exercise export/import](../../../../docs/EXERCISE-EXPORT-IMPORT.md)
- [Workbook builder](../../../wiki/subsystem-overview.md)
- [Lab creation engine](../../../../docs/LAB-CREATION-ENGINE.md)
- [Malware lab governance](../../../../docs/MALWARE-LAB-GOVERNANCE.md)
