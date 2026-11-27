# Instructor and admin (frontend)

## Purpose

Give instructors a scoped view of their courses and give administrators the
platform controls: users, roles, catalogue, sessions, settings, reports,
backups, and security events.

## Routes and views

| Route | View | Guard |
|---|---|---|
| `/instructor` | `InstructorPanel.vue` | instructor or admin |
| `/instructor/courses/:id` | `InstructorDashboard.vue` | course owner or institution admin |
| `/admin` | `Admin.vue` | admin or institution admin |
| `/admin/usage` | `Admin.vue` (usage tab) | admin |
| `/reports` | `Reports.vue` | instructor/admin |
| `/governance` | `Governance.vue` | auditor/privacy/admin |
| `/curriculum` | `Curriculum.vue` | admin |
| `/contract-review` | `ContractReview.vue` | reviewer |
| `/evidence-review` | `EvidenceReview.vue` | reviewer |

Admin tabs are components such as `AdminPendingTab.vue`,
`CourseAnalytics.vue`, `CoursePlanningPanel.vue`, `CompetencyTaxonomy.vue`,
`IdentityProvidersPanel.vue`, `LtiPlatformsPanel.vue`, `AuditHistory.vue`, and
`HaStatusCard.vue`.

## API calls

| Area | Endpoints |
|---|---|
| Users | `/api/admin/users*`, `/api/admin/users/{id}/...` |
| Roles and security | `/api/admin/security/rbac/*`, `/api/admin/security/events*` |
| Catalogue | `/api/admin/labs*`, `/api/admin/curriculum/*` |
| Sessions | `/api/admin/sessions/*` |
| Reports | `/api/reports/*`, `/api/admin/stats` |
| Settings | `/api/admin/settings*`, `/api/admin/badges/*` |
| Backups | `/api/admin/system/backup*`, `/restore` |
| Governance | `/api/governance/*` |

## Behaviour that matters

- **Guards are convenience, not control.** The backend re-checks every role and
  tenant. A hidden tab is not a permission.
- **Course scope.** An instructor sees only their courses; an institution admin
  sees their institution.
- **Destructive actions confirm.** Delete, reset, terminate, and restore require
  an explicit confirmation and show the target.
- **Reauth.** Sensitive actions trigger the reauth dialog on `X-Reauth-Required`.
- **Impersonation banner.** When impersonating, a persistent banner and an exit
  action are shown.
- **Report downloads.** The UI shows the report id and integrity metadata, not
  raw learner rows.

## Storage

No admin state is persisted in the browser. Filters may live in the URL.
Impersonation state uses `sessionStorage`.

## Run and test

```bash
cd platform/frontend
npm run dev
npm test
```

Backend coverage: `tests/test_admin_users.py`,
`tests/test_institution_admin.py`, `tests/test_authorization_matrix.py`,
`tests/test_reports.py`, `tests/test_usage_dashboard.py`,
`tests/test_ha_status_api.py`.

## Extension checklist

- Add the route and the guard.
- Add the backend permission; never rely on the UI guard.
- Add a confirmation for a destructive action.
- Add a test for the denial path.
- Keep the instructor and admin surfaces separate.
- Update the RBAC matrix and the admin docs.

## Related

- [Backend roles and admin](../../../backend/features/roles-and-admin/README.md)
- [Backend analytics and reports](../../../backend/features/analytics-and-reports/README.md)
- [RBAC matrix](../../../../docs/RBAC-PBAC-MATRIX.md)
