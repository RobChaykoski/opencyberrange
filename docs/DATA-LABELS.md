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
X-Data-Organisation: Example Institute
X-Data-Handling: Confidential. Share only with authorised recipients.
X-Data-Source: OpenCyberRange
X-Export-Generated-At: 2026-11-14T09:00:00+00:00
```

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

## CSV and Markdown

CSV downloads carry the label in response headers. The CSV body is unchanged so
spreadsheet imports and existing parsers keep working. Markdown and HTML
portfolio downloads carry the headers as well; adding a visible footer to those
formats is a content-design decision and is not implied by the metadata switch.

## Scope and limits

- Labels describe handling instructions; they do not encrypt or redact files.
  Access control and the audit trail remain the enforcement points.
- The label is only as good as the admin configuration. Review the
  classification when exporting learner records or incident evidence.
- Backup archives and Open Badges credentials are separate formats. Badges are
  public by design and are not stamped with the internal classification.
