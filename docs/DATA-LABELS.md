# Export data labels

Administrators can add a data-classification label to anything the platform
exports. The controls live in **Admin → Settings → Data labels**.

## Settings

| Setting | Purpose |
|---|---|
| Export data labels | Master switch. Off removes new labels without changing stored data. |
| Default classification | Public, Internal, Confidential, or Restricted. |
| Export owner | Organisation written as the PDF author and `X-Data-Organisation`. Empty uses SWOCTS Cyber Range. |
| Handling note | Free-text instruction in the metadata. Empty uses a default sentence for the chosen classification. |
| Include generation time | Adds the UTC generation time to headers and JSON metadata. |

The settings panel shows a preview of the classification, owner, and handling
note before saving.

## Where the label appears

### HTTP responses

A response middleware detects attachments, `application/pdf`, and `text/csv`
responses and adds:

```
X-Data-Classification: Confidential
X-Data-Classification-Key: confidential
X-Data-Organisation: Example Institute
X-Data-Region: EU
X-Data-Handling: Confidential. Share only with authorised recipients.
X-Data-Source: OpenCyberRange
X-Data-Policy: enforced
X-Data-Enforcement: enabled
X-Export-Generated-At: 2026-11-14T09:00:00+00:00
```

`X-Data-Policy` is `advisory`, `enforced`, `denied`, or `unauthenticated`.
`X-Data-Enforcement` appears only when enforcement is active.

The values come from the current settings at the time of the download, so a
label change applies without rebuilding or restarting.

### PDF documents

PDF exports set document properties:

- **Title**: the report or certificate title.
- **Author**: the export owner.
- **Subject**: the original subject plus the classification.
- **Creator**: OpenCyberRange.
- **Keywords**: classification, subject, handling note, and generation time.

This covers learner transcripts, completion certificates, event certificates,
learning/analytics reports, course and coaching reports, and exercise-test
reports.

### JSON exports

The account data export, career dossier, professional portfolio, and identity
provider export include an `export_metadata` object:

```json
{
  "classification": "Internal",
  "classification_key": "internal",
  "organisation": "Example Institute",
  "handling": "Internal use. Share only within the institution.",
  "source": "OpenCyberRange",
  "generated_at": "2026-11-14T09:00:00+00:00"
}
```

### CSV, Markdown, and HTML

CSV downloads prepend `#` comment rows with the classification, organisation,
handling note, and generation time, followed by the normal header row. The
response headers remain the machine-readable copy. Markdown dossiers and
portfolios start with a blockquote label block; HTML exports insert a styled
label banner immediately after `<body>`.

## Enforceable policy

Labelling is advisory by default. Set
`data_label_enforcement_enabled=true` to make the label a decision point for
downloads. The effective label is the higher-ranked of:

1. the classification implied by the export path (for example
   `/api/admin/system/backups` is Restricted, `/api/auth/export` is
   Confidential, and public certificate verification is Public); and
2. the institution's configured default.

The download is allowed only when **all** of these hold:

- the role has `export.data`;
- the role has the permission for the effective rank (`export.public`,
  `export.internal`, `export.confidential`, or `export.restricted`);
- the rank is at or below the institution ceiling
  (`data_label_max_export_rank`), the role ceiling
  (`data_label_role_max_rank`), and the region ceiling
  (`data_label_region_rules`);
- the level is marked `exportable`; and
- Restricted exports are not blocked (`data_label_block_restricted_exports`).
  Restricted is blocked by default; a break-glass grant for
  `export.restricted` is the reviewed exception when enforcement is on.

Denied downloads return `403` with `error=DataLabelExportDenied`,
`X-Data-Policy: denied`, and the classification that caused the denial. The
decision and the actor are written to the security event store as
`export.denied`; allowed exports are `export.allowed`.

### Organisational schemes

`data_label_custom_levels` accepts a JSON list. Each level needs a unique
`key`, a `label`, and an integer `rank`; `handling` and `exportable` are
optional. Invalid JSON falls back to the built-in four-level scheme with a
warning on `GET /api/admin/data-labels/policy`.

```json
[
  {"key": "public", "label": "Public", "rank": 0},
  {"key": "official", "label": "Official", "rank": 1},
  {"key": "protected", "label": "Protected", "rank": 2},
  {"key": "sealed", "label": "Sealed", "rank": 3, "exportable": false}
]
```

Use `data_label_region` plus `data_label_region_rules` to apply a regional
ceiling, for example:

```json
{"EU": {"max_export_rank": 2, "block_restricted": true}}
```

`data_label_role_max_rank` adds a per-role institution ceiling after RBAC:
`{"student": 2, "instructor": 2, "admin": 3}`. RBAC is always checked first;
the ceiling can only lower what a role may export.

Admins can preview a decision before enabling enforcement:

```bash
GET /api/admin/data-labels/policy?role=student&path=/api/auth/export
```

## Scope and limits

- Labels describe handling instructions; they do not encrypt or redact files.
  Enforcement prevents a download through the API, but a user who already has
  an allowed file can still copy it. Access control and the audit trail remain
  the wider enforcement points.
- The label is only as good as the admin configuration. Review the
  classification when exporting learner records or incident evidence.
- Backup archives and Open Badges credentials are separate formats. Badges are
  public by design and are not stamped with the internal classification.
- Enforcement currently applies to response downloads detected as attachments,
  PDFs, or CSV. JSON export metadata is stamped separately; per-route JSON
  export authorization is still being migrated.
