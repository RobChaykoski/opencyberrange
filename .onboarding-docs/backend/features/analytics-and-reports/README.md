# Analytics and reports

## Purpose

Give instructors and administrators useful, privacy-safe signals about a cohort
and produce exports that an institution can defend. Small cohorts are
suppressed; a missing measurement is shown as unmeasured, never zero.

## Code map

| Concern | Location |
|---|---|
| Analytics router | `platform/backend/app/routers/analytics.py` |
| Dashboards | `platform/backend/app/routers/dashboard.py`, `instructor.py` |
| Reports | `platform/backend/app/routers/reports.py` |
| Report services | `platform/backend/app/services/analytics_report.py`, `pdf_report.py`, `report_pdf.py`, `report_integrity.py`, `report_access.py` |
| Gradebook adapters | `platform/backend/app/services/gradebook.py` (Canvas, Brightspace, Moodle, generic) |
| Export labels | `platform/backend/app/services/export_labels.py`, `data_labels.py` |
| Readiness | `platform/backend/app/services/readiness_dashboard.py`, `role_readiness.py` |
| Model | `platform/backend/app/models/` (completions, sessions, achievements) |

## API surface

| Method | Path | Notes |
|---|---|---|
| GET | `/api/analytics/*` | cohort metrics, growth, readiness, skill signals |
| GET | `/api/dashboard/*` | learner and instructor dashboards |
| GET | `/api/reports/*` | report list, download, verify |
| POST | `/api/reports/verify` | public report-integrity check (report id + file) |
| GET | `/api/admin/stats` | platform stats |
| GET | `/api/admin/competency-coverage` | coverage view |

## Behaviour that matters

- **Suppression.** Small cohorts are suppressed rather than reported as zero.
- **Unmeasured, not zero.** A missing measurement is labelled unmeasured.
- **No learner ranking.** Analytics are cohort and outcome oriented.
- **Aggregate exports.** Reports carry labels (`X-Data-Classification`,
  organisation, handling, source) and a signed manifest.
- **Scope checks.** An instructor sees only their course or institution; a
  learner sees only their own data.
- **Report integrity.** The PDF hash and signature let a recipient verify the
  file; a failed check is visible.
- **Lab friction.** The friction CSV separates wrong-flag attempts from hint
  requests and ranks labs by starts without completion.
- **Gradebook.** The LMS export reuses scoreboard scoring and offers Canvas,
  Brightspace, Moodle, and generic layouts. It omits visible `#` label lines so
  an importer reads the header, while response headers and the manifest retain
  the classification.
- **Under-18 exclusion.** Individual reports and the gradebook exclude learners
  who identify as under 18; aggregate reports count only the remaining cohort.

## Persistent state

| Store | Data |
|---|---|
| PostgreSQL | completions, sessions, attempts, achievements, evidence |
| `backups_data` | snapshots used for restore, not analytics |
| Report files | stored per deployment policy, with manifest |
| `activity_events` | source events |

Analytics does **not** copy learner rows to a warehouse.

## Fixtures and tests

- `seed_analytics_demo.py` creates a reporting baseline.
- `simulate_student.py` creates synthetic activity.
- Focused tests:

```bash
cd platform/backend
python -m pytest tests/test_analytics.py tests/test_analytics_schema.py \
  tests/test_instructor_learning_metrics.py tests/test_reports.py \
  tests/test_report_access.py tests/test_report_integrity.py -q
```

## Extension checklist

- Add the metric to the schema and a test with a small cohort.
- Confirm the suppression threshold and the unmeasured label.
- Confirm the tenant and course scope.
- Add export labels if the data leaves the platform.
- Update the reporting roadmap and the data dictionary.

## Related

- [Analytics governance](../../../../docs/ANALYTICS-GOVERNANCE.md)
- [Instructor analytics](../../../../docs/INSTRUCTOR-ANALYTICS.md)
- [Reporting roadmap](../../../../docs/REPORTING-ROADMAP.md)
- [Data labels](../../../../docs/DATA-LABELS.md)
- [OpenGRC integration](../../../integrations/opengrc/README.md)
