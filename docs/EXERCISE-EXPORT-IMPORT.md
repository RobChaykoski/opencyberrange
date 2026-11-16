# Exercise export and import

Exercises can be exported as a reusable ZIP and imported on another
OpenCyberRange instance (or the same one under a new name). The format is the
same authoring layout an instructor upload already accepts:

```text
<slug>/
  lab.yaml
  docker-compose.yml
  containers/
    target/
      Dockerfile
      ...
  export-manifest.json
  EXPORT-README.md
```

`export-manifest.json` records the format version, source slug/track/level,
whether the flag was included, the file list, and non-fatal warnings.

## Export

- Admin: **Admin → Exercises → export icon** on a row.
- Instructor: **Instructor Panel → Exercises → export icon**.
- API:
  - `GET /api/admin/labs/{id}/export?include_flag=false`
  - `GET /api/instructor/labs/{id}/export`

The exporter reads the lab's source directory. If the directory is missing (for
example a database-only lab), it rebuilds `lab.yaml` and the compose file from
the database and warns that container files are not included.

### Flag handling

By default the flag in `lab.yaml` is replaced with:

```yaml
flag: "OCR{REPLACE_ME}"
```

This makes the archive safe to share for reuse. An administrator can request
`include_flag=true` for a trusted backup; that archive contains the original
flag and must be treated as a secret. Instructor exports never include the flag.

## Import

- Admin: **Admin → Exercises → Import Exercise**.
- API: `POST /api/admin/labs/import` (multipart ZIP, `track`, `level_id`,
  optional `name`, optional `flag`, optional `reuse_flag=true`).

The importer:

1. Runs the existing ZIP validator (path traversal, size, zip-bomb, required
   files, compose structure).
2. Generates a discovery-compatible slug under the selected track/level.
3. Extracts the source into the labs tree.
4. Generates a new flag unless one is supplied, and writes it into the imported
   `lab.yaml`.
5. Creates the `Lab` row with `visibility="draft"` and `created_by` set to the
   importer.

If no flag is supplied, the new flag is returned **once** in the import
response. Store it immediately. The imported exercise is never published
automatically; review and publish it from the exercise table.

## Metadata preserved

The importer keeps `title`, `category`, `difficulty`, `estimated_time`,
`prerequisites`, `learning_outcomes`, `mapped_skills`, `assessment_criteria`,
`mitre_attack`, `ics_techniques`, `content_version`, hints, tools, hostnames,
workbook/chapter metadata, competency/framework fields, topology/network flags,
and certificate-counting settings.

## Manual

- Admin: [Managing Labs](../Manual-Lite/04_Admin_Guide/08_Managing_Labs.md),
  including the import modal screenshot `admin-import-exercise.png`.
- Instructor: [Assigning Labs to a Course](../Manual-Lite/03_Instructor_Guide/07_Assigning_Labs_to_a_Course.md)
  for the read-only export action.

## Tests

`platform/backend/tests/test_exercise_transfer.py` covers:

- flag scrubbing and trusted-flag export;
- round-trip file inclusion and manifest contents;
- import as draft with a generated flag;
- provided and reused flags;
- missing `lab.yaml` rejection;
- admin/instructor export permissions;
- admin import through the HTTP API.
