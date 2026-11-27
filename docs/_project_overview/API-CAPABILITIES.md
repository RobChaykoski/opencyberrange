# API capabilities

Generated from the live FastAPI application on 2026-11-27T01:25:41+00:00.

| Item | Value |
|---|---|
| Product | SWOCTS Cyber Range Release 5.56.2 (Powered by OpenCyberRange) |
| Platform version | `5.56.2` |
| OpenAPI version | `3.1.0` |
| API title | SWOCTS Cyber Range |
| API version | `5.56.2` |
| Paths | 490 |
| Operations | 548 |
| Methods | DELETE 36, GET 288, PATCH 6, POST 187, PUT 31 |

The machine-readable contract is [`openapi.json`](openapi.json). It follows the
OpenAPI specification and can be imported into Swagger UI, Redoc, Postman,
Insomnia, or an API gateway. The application serves the same schema at
`/openapi.json` when the API is running.

## Authentication and exposure

The API is same-origin behind nginx at `/api`. Browser calls use the SPA's
Bearer token; the wiki subrequests use the HttpOnly `wiki_session` cookie
validated by nginx against `/api/auth/me`. Do not publish a live token or a
real hostname in an exported schema.

| Scheme | Type | Details |
|---|---|---|
| `OAuth2PasswordBearer` | oauth2 | - |

## Serving and exposure

The API is private by default. The machine-readable schema in this folder is the
reviewed offline export; it does not make the live documentation public.

| Surface | Default | Control |
|---|---|---|
| REST API `/api/*` | Available to authenticated callers through nginx | JWT / role and consent checks |
| `/openapi.json` | Hidden | `enable_api_docs` setting; `ENABLE_API_DOCS=true` is an emergency override |
| `/docs` (Swagger UI) | Hidden | Same setting |
| `/redoc` | Hidden | Same setting |
| `/api/health`, `/health`, `/api/version` | Available | Health and release probes |

When enabling the live docs for a review, restrict them at the edge and turn
them off again afterwards. The exported `openapi.json` is the safer artifact to
share with an integrator.

## Capability summary

| Capability | Endpoint families |
|---|---|
| Identity and session | `/api/auth/*`, `/api/identity/*`, `/api/sso/*`, `/api/profile/security/*` |
| Learning catalogue | `/api/exercises/*`, `/api/labs/*`, `/api/curriculum/*`, `/api/courses/*` |
| Lab runtime | `/api/labs/*`, `/api/rangebox/*`, `/api/workbook/*` |
| Assessment and evidence | `/api/quiz/*`, `/api/evidence/*`, `/api/reviews/*`, `/api/competency-reviews/*`, `/api/capstones/*` |
| Learner portfolio | `/api/profile/*`, `/api/portfolio/*`, `/api/journeys/*`, `/api/impact/*`, `/api/recognition/*` |
| Analytics and reporting | `/api/analytics/*`, `/api/reports/*`, `/api/usage/*`, `/api/dashboard/*` |
| Administration | `/api/admin/*`, `/api/settings/*`, `/api/modules/*`, `/api/security-admin/*`, `/api/governance/*` |
| Integrations | `/api/lti/*`, `/api/open-badges/*`, `/api/nice/*` |
| Public/health | `/api/setup/*`, `/api/config/public`, `/api/version`, `/health` |

## Operations by tag

### About

| Method | Path | Summary | Security |
|---|---|---|---|
| GET | `/api/about` | Get About | OAuth2PasswordBearer |
| GET | `/api/about/licences/{name}` | Get Licence | OAuth2PasswordBearer |
| GET | `/api/about/sbom/{name}` | Get Sbom | OAuth2PasswordBearer |

### Accommodations

| Method | Path | Summary | Security |
|---|---|---|---|
| GET | `/api/accommodations/me` | Get My Accommodation | OAuth2PasswordBearer |
| DELETE | `/api/courses/{course_id}/students/{student_id}/accommodation` | Clear Student Accommodation | OAuth2PasswordBearer |
| GET | `/api/courses/{course_id}/students/{student_id}/accommodation` | Get Student Accommodation | OAuth2PasswordBearer |
| PUT | `/api/courses/{course_id}/students/{student_id}/accommodation` | Set Student Accommodation | OAuth2PasswordBearer |

### Admin

| Method | Path | Summary | Security |
|---|---|---|---|
| GET | `/api/admin/activity` | Get Activity Log | OAuth2PasswordBearer |
| POST | `/api/admin/activity/clear` | Clear Activity Log | OAuth2PasswordBearer |
| GET | `/api/admin/activity/export` | Export Activity Log | OAuth2PasswordBearer |
| GET | `/api/admin/competency-coverage` | Competency Coverage | OAuth2PasswordBearer |
| POST | `/api/admin/containers/cleanup-orphaned` | Cleanup Orphaned Containers | OAuth2PasswordBearer |
| GET | `/api/admin/courses/{course_id}/retention` | Get Retention Policy | OAuth2PasswordBearer |
| PUT | `/api/admin/courses/{course_id}/retention` | Set Retention Policy | OAuth2PasswordBearer |
| POST | `/api/admin/courses/{course_id}/retention/complete` | Complete Retention | OAuth2PasswordBearer |
| POST | `/api/admin/courses/{course_id}/retention/preview` | Preview Retention | OAuth2PasswordBearer |
| GET | `/api/admin/courses/{course_id}/retention/runs` | List Retention Runs | OAuth2PasswordBearer |
| GET | `/api/admin/data-labels/policy` | Get Data Label Policy | OAuth2PasswordBearer |
| GET | `/api/admin/docker/disk-usage` | Get Docker Disk Usage | OAuth2PasswordBearer |
| POST | `/api/admin/docker/prune-build-cache` | Prune Build Cache | OAuth2PasswordBearer |
| POST | `/api/admin/docker/prune-images` | Prune All Images | OAuth2PasswordBearer |
| POST | `/api/admin/impersonate/disconnect` | Disconnect Impersonation | OAuth2PasswordBearer |
| POST | `/api/admin/impersonate/launch` | Impersonate Launch Lab | OAuth2PasswordBearer |
| GET | `/api/admin/impersonate/status` | Impersonation Status | OAuth2PasswordBearer |
| POST | `/api/admin/impersonate/{session_id}` | Impersonate Session | OAuth2PasswordBearer |
| GET | `/api/admin/labs` | List Labs | OAuth2PasswordBearer |
| POST | `/api/admin/labs` | Create Lab | OAuth2PasswordBearer |
| POST | `/api/admin/labs/bulk-toggle` | Bulk Toggle Labs | OAuth2PasswordBearer |
| POST | `/api/admin/labs/discover` | Discover Labs | OAuth2PasswordBearer |
| POST | `/api/admin/labs/import` | Import Exercise | OAuth2PasswordBearer |
| PUT | `/api/admin/labs/{lab_id}` | Update Lab | OAuth2PasswordBearer |
| POST | `/api/admin/labs/{lab_id}/approve` | Approve Lab | OAuth2PasswordBearer |
| PUT | `/api/admin/labs/{lab_id}/compose` | Update Lab Compose | OAuth2PasswordBearer |
| GET | `/api/admin/labs/{lab_id}/details` | Get Lab Details Admin | OAuth2PasswordBearer |
| GET | `/api/admin/labs/{lab_id}/export` | Export Exercise | OAuth2PasswordBearer |
| DELETE | `/api/admin/labs/{lab_id}/images` | Delete Lab Images | OAuth2PasswordBearer |
| GET | `/api/admin/labs/{lab_id}/images` | Get Lab Images | OAuth2PasswordBearer |
| POST | `/api/admin/labs/{lab_id}/reject` | Reject Lab | OAuth2PasswordBearer |
| POST | `/api/admin/labs/{lab_id}/toggle` | Toggle Lab | OAuth2PasswordBearer |
| GET | `/api/admin/rangebox-capacity` | Get Rangebox Capacity | OAuth2PasswordBearer |
| POST | `/api/admin/rangebox-capacity/test` | Run Rangebox Capacity Test | OAuth2PasswordBearer |
| GET | `/api/admin/retention/due` | List Retention Due | OAuth2PasswordBearer |
| GET | `/api/admin/sessions/active` | List Active Sessions | OAuth2PasswordBearer |
| GET | `/api/admin/sessions/health` | Get Sessions Health | OAuth2PasswordBearer |
| DELETE | `/api/admin/sessions/history` | Clear Session History | OAuth2PasswordBearer |
| GET | `/api/admin/sessions/history` | Session History | OAuth2PasswordBearer |
| POST | `/api/admin/sessions/terminate-all` | Terminate All Sessions | OAuth2PasswordBearer |
| POST | `/api/admin/sessions/terminate/{session_id}` | Terminate Session | OAuth2PasswordBearer |
| GET | `/api/admin/sessions/{session_id}/logs` | Get Session Logs | OAuth2PasswordBearer |
| POST | `/api/admin/sessions/{session_id}/reset-stale` | Reset Stale Session | OAuth2PasswordBearer |
| POST | `/api/admin/sessions/{session_id}/resync-vpn` | Resync Session Vpn | OAuth2PasswordBearer |
| GET | `/api/admin/stats` | Get Stats | OAuth2PasswordBearer |
| POST | `/api/admin/stress-test` | Start Stress Test | OAuth2PasswordBearer |
| GET | `/api/admin/stress-test/active` | Get Active Stress Test | OAuth2PasswordBearer |
| POST | `/api/admin/stress-test/cancel` | Cancel Stress Test | OAuth2PasswordBearer |
| POST | `/api/admin/stress-test/cleanup` | Stress Test Cleanup | OAuth2PasswordBearer |
| GET | `/api/admin/stress-test/events/{run_id}` | Get Stress Test Events | OAuth2PasswordBearer |
| GET | `/api/admin/stress-test/last-result` | Get Last Stress Result | OAuth2PasswordBearer |
| POST | `/api/admin/stress-test/report` | Generate Stress Report Pdf | OAuth2PasswordBearer |
| GET | `/api/admin/system/activity-calendar` | Activity Calendar | OAuth2PasswordBearer |
| POST | `/api/admin/system/backup` | Create Backup | OAuth2PasswordBearer |
| GET | `/api/admin/system/backups` | List Backups | OAuth2PasswordBearer |
| DELETE | `/api/admin/system/backups/{filename}` | Delete Backup | OAuth2PasswordBearer |
| GET | `/api/admin/system/backups/{filename}` | Download Backup | OAuth2PasswordBearer |
| GET | `/api/admin/system/data-integrity` | Get Data Integrity Status | OAuth2PasswordBearer |
| POST | `/api/admin/system/data-integrity/review` | Review Data Integrity Write | OAuth2PasswordBearer |
| GET | `/api/admin/system/ha` | Read-only HA status snapshot | OAuth2PasswordBearer |
| GET | `/api/admin/system/metrics` | Get System Metrics | OAuth2PasswordBearer |
| POST | `/api/admin/system/metrics/sample` | Sample System Metrics | OAuth2PasswordBearer |
| GET | `/api/admin/system/release` | Compare this installation with the latest GitHub release | OAuth2PasswordBearer |
| POST | `/api/admin/system/restore` | Restore Backup | OAuth2PasswordBearer |
| POST | `/api/admin/system/restore/upload` | Restore Uploaded Backup | OAuth2PasswordBearer |
| GET | `/api/admin/system/software-integrity` | Verify deployed lab content against the release manifest | OAuth2PasswordBearer |
| GET | `/api/admin/system/status` | System Status | OAuth2PasswordBearer |
| GET | `/api/admin/users` | List Users | OAuth2PasswordBearer |
| POST | `/api/admin/users/approve` | Approve User | OAuth2PasswordBearer |
| POST | `/api/admin/users/create` | Create User | OAuth2PasswordBearer |
| GET | `/api/admin/users/export` | Export Users | OAuth2PasswordBearer |
| POST | `/api/admin/users/import` | Import Users | OAuth2PasswordBearer |
| GET | `/api/admin/users/locked` | List Locked Users | OAuth2PasswordBearer |
| GET | `/api/admin/users/pending` | List Pending Users | OAuth2PasswordBearer |
| DELETE | `/api/admin/users/{user_id}` | Delete User | OAuth2PasswordBearer |
| GET | `/api/admin/users/{user_id}` | Get User | OAuth2PasswordBearer |
| PUT | `/api/admin/users/{user_id}` | Update User | OAuth2PasswordBearer |
| GET | `/api/admin/users/{user_id}/details` | Get User Details | OAuth2PasswordBearer |
| POST | `/api/admin/users/{user_id}/force-logout` | Force Logout User | OAuth2PasswordBearer |
| POST | `/api/admin/users/{user_id}/labs/{lab_id}/reset` | Reset User Lab | OAuth2PasswordBearer |
| POST | `/api/admin/users/{user_id}/mfa/reset` | Reset another account's MFA | OAuth2PasswordBearer |
| POST | `/api/admin/users/{user_id}/reset-password` | Reset Password | OAuth2PasswordBearer |
| POST | `/api/admin/users/{user_id}/unlock` | Unlock User | OAuth2PasswordBearer |
| DELETE | `/api/admin/vpn/peer-by-key/{public_key}` | Remove Vpn Peer By Key | OAuth2PasswordBearer |
| DELETE | `/api/admin/vpn/peer/{user_id}` | Remove Vpn Peer | OAuth2PasswordBearer |
| GET | `/api/admin/vpn/peers` | List Vpn Peers | OAuth2PasswordBearer |
| POST | `/api/admin/vpn/peers/{user_id}/repair` | Repair Vpn Peer | OAuth2PasswordBearer |
| POST | `/api/admin/vpn/reconcile-peers` | Reconcile Vpn Peers | OAuth2PasswordBearer |
| POST | `/api/admin/vpn/register/{user_id}` | Register Vpn Peer | OAuth2PasswordBearer |
| GET | `/api/admin/vpn/status` | Vpn Sync Status | OAuth2PasswordBearer |
| POST | `/api/admin/vpn/sync` | Sync Vpn Peers | OAuth2PasswordBearer |

### Analytics

| Method | Path | Summary | Security |
|---|---|---|---|
| GET | `/api/analytics/courses/{course_id}/competency` | Course Competency | OAuth2PasswordBearer |
| GET | `/api/analytics/courses/{course_id}/exercises` | Course Exercises | OAuth2PasswordBearer |
| POST | `/api/analytics/courses/{course_id}/labs/{lab_id}/reviews` | Add Lab Health Review | OAuth2PasswordBearer |
| GET | `/api/analytics/courses/{course_id}/overview` | Course Overview | OAuth2PasswordBearer |
| GET | `/api/analytics/courses/{course_id}/pulse-comments` | Course Pulse Comments | OAuth2PasswordBearer |
| GET | `/api/analytics/courses/{course_id}/readiness` | Course Readiness | OAuth2PasswordBearer |
| GET | `/api/analytics/courses/{course_id}/readiness/calibration` | Readiness Calibration | OAuth2PasswordBearer |
| GET | `/api/analytics/courses/{course_id}/students/{user_id}/capabilities` | Student Capabilities | OAuth2PasswordBearer |
| POST | `/api/analytics/courses/{course_id}/students/{user_id}/notes` | Add Readiness Note | OAuth2PasswordBearer |
| POST | `/api/analytics/events/workbook-open` | Workbook Opened | OAuth2PasswordBearer |
| GET | `/api/analytics/metrics` | Metric Dictionary | OAuth2PasswordBearer |
| GET | `/api/analytics/pulse/{lab_id}` | Get Pulse | OAuth2PasswordBearer |
| POST | `/api/analytics/pulse/{lab_id}` | Submit Pulse | OAuth2PasswordBearer |
| GET | `/api/analytics/reaction/{lab_id}` | Get Exercise Reaction | OAuth2PasswordBearer |
| POST | `/api/analytics/reaction/{lab_id}` | Set Exercise Reaction | OAuth2PasswordBearer |
| GET | `/api/analytics/reports/activity` | Reports Activity | OAuth2PasswordBearer |
| GET | `/api/analytics/reports/curriculum-demand` | Curriculum Demand | OAuth2PasswordBearer |
| POST | `/api/analytics/reports/export-audit` | Audit Report Export | OAuth2PasswordBearer |
| GET | `/api/analytics/reports/export.pdf` | Reports Export Pdf | OAuth2PasswordBearer |
| GET | `/api/analytics/reports/overview` | Reports Overview | OAuth2PasswordBearer |
| GET | `/api/analytics/student/me` | Student Analytics | OAuth2PasswordBearer |
| GET | `/api/analytics/surveys` | List Surveys | OAuth2PasswordBearer |
| POST | `/api/analytics/surveys` | Create Survey | OAuth2PasswordBearer |
| GET | `/api/analytics/surveys/available` | Available Surveys | OAuth2PasswordBearer |
| DELETE | `/api/analytics/surveys/{survey_id}` | Delete Survey | OAuth2PasswordBearer |
| GET | `/api/analytics/surveys/{survey_id}/responses` | Survey Responses | OAuth2PasswordBearer |
| POST | `/api/analytics/surveys/{survey_id}/responses` | Submit Survey Response | OAuth2PasswordBearer |

### Archive

| Method | Path | Summary | Security |
|---|---|---|---|
| GET | `/api/archive/me` | My Archive | OAuth2PasswordBearer |

### Audit

| Method | Path | Summary | Security |
|---|---|---|---|
| GET | `/api/admin/audit/impersonations` | Admin Impersonation Sessions | OAuth2PasswordBearer |
| GET | `/api/admin/audit/users/by-username/{username}/history` | Admin User History By Username | OAuth2PasswordBearer |
| GET | `/api/admin/audit/users/{user_id}/history` | Admin User History | OAuth2PasswordBearer |
| GET | `/api/courses/{course_id}/students/{user_id}/history` | Course Student History | OAuth2PasswordBearer |

### Authentication

| Method | Path | Summary | Security |
|---|---|---|---|
| POST | `/api/auth/change-password` | Change Password | OAuth2PasswordBearer |
| POST | `/api/auth/delete-account` | Delete My Account | OAuth2PasswordBearer |
| POST | `/api/auth/delete-request` | Request Account Deletion | OAuth2PasswordBearer |
| GET | `/api/auth/export` | Export User Data | OAuth2PasswordBearer |
| GET | `/api/auth/export-status` | Export Status | OAuth2PasswordBearer |
| POST | `/api/auth/forgot-password` | Forgot Password | public / none |
| POST | `/api/auth/forgot-username` | Forgot Username | public / none |
| POST | `/api/auth/impersonate` | Start Impersonation | OAuth2PasswordBearer |
| POST | `/api/auth/impersonate/exit` | Exit Impersonation | OAuth2PasswordBearer |
| POST | `/api/auth/login` | Login | public / none |
| POST | `/api/auth/logout` | Logout | OAuth2PasswordBearer |
| GET | `/api/auth/me` | Get Current User Info | OAuth2PasswordBearer |
| GET | `/api/auth/me/impersonation` | Get Impersonation Status | OAuth2PasswordBearer |
| POST | `/api/auth/mfa/disable` | Disable Mfa | OAuth2PasswordBearer |
| POST | `/api/auth/mfa/enroll` | Enroll Mfa | OAuth2PasswordBearer |
| POST | `/api/auth/mfa/recovery-codes` | Generate Recovery Codes | OAuth2PasswordBearer |
| POST | `/api/auth/mfa/recovery-codes/verify` | Verify Recovery Code | OAuth2PasswordBearer |
| POST | `/api/auth/mfa/verify` | Verify Mfa | OAuth2PasswordBearer |
| POST | `/api/auth/reauth` | Reauthenticate | OAuth2PasswordBearer |
| POST | `/api/auth/refresh` | Refresh Access Token | public / none |
| POST | `/api/auth/register` | Register | public / none |
| POST | `/api/auth/reset-password` | Reset Password | public / none |
| GET | `/api/auth/sessions` | List Sessions | OAuth2PasswordBearer |
| POST | `/api/auth/sessions/revoke-all` | Revoke All Sessions | OAuth2PasswordBearer |
| DELETE | `/api/auth/sessions/{session_id}` | Revoke One Session | OAuth2PasswordBearer |
| GET | `/api/auth/settings` | Get User Settings | OAuth2PasswordBearer |
| PUT | `/api/auth/settings` | Update User Settings | OAuth2PasswordBearer |
| GET | `/api/auth/survey-consent` | Get Survey Consent | OAuth2PasswordBearer |
| POST | `/api/auth/survey-consent` | Update Survey Consent | OAuth2PasswordBearer |
| GET | `/api/auth/wiki-access` | Check Wiki Access | OAuth2PasswordBearer |
| GET | `/api/auth/wiki-admin-access` | Check Wiki Admin Access | OAuth2PasswordBearer |
| DELETE | `/api/auth/wiki-cookie` | Clear Wiki Cookie | public / none |
| POST | `/api/auth/wiki-cookie` | Issue Wiki Cookie | OAuth2PasswordBearer |
| GET | `/api/auth/wiki-released` | Wiki Released Chapters | public / none |

### Capstones

| Method | Path | Summary | Security |
|---|---|---|---|
| POST | `/api/capstones/plan` | Capstone Plan | OAuth2PasswordBearer |
| GET | `/api/capstones/plans` | List Capstone Plans | OAuth2PasswordBearer |
| POST | `/api/capstones/plans` | Save Capstone Plan | OAuth2PasswordBearer |
| GET | `/api/capstones/plans/{plan_id}` | Get Capstone Plan | OAuth2PasswordBearer |
| PUT | `/api/capstones/plans/{plan_id}` | Update Capstone Plan | OAuth2PasswordBearer |
| POST | `/api/capstones/plans/{plan_id}/approve` | Approve Capstone Plan | OAuth2PasswordBearer |
| POST | `/api/capstones/plans/{plan_id}/archive` | Archive Capstone Plan | OAuth2PasswordBearer |
| GET | `/api/capstones/profiles` | Capstone Profiles | OAuth2PasswordBearer |

### Competencies

| Method | Path | Summary | Security |
|---|---|---|---|
| GET | `/api/competencies/{competency_id}/evidence` | Competency Evidence | OAuth2PasswordBearer |

### Competency reviews

| Method | Path | Summary | Security |
|---|---|---|---|
| GET | `/api/competency-reviews/catalogue` | Review Catalogue | OAuth2PasswordBearer |
| GET | `/api/competency-reviews/export-ready` | Export Ready | OAuth2PasswordBearer |
| GET | `/api/competency-reviews/queue` | Review Queue | OAuth2PasswordBearer |
| GET | `/api/competency-reviews/{lab_slug}` | Review Detail | OAuth2PasswordBearer |
| POST | `/api/competency-reviews/{lab_slug}/draft` | Save Review Draft | OAuth2PasswordBearer |
| POST | `/api/competency-reviews/{lab_slug}/sign` | Sign Review | OAuth2PasswordBearer |
| POST | `/api/competency-reviews/{review_id}/exported` | Mark Review Exported | OAuth2PasswordBearer |

### Competitions

| Method | Path | Summary | Security |
|---|---|---|---|
| GET | `/api/competitions` | List Competitions | OAuth2PasswordBearer |
| POST | `/api/competitions` | Create Competition | OAuth2PasswordBearer |
| GET | `/api/competitions/public/{competition_id}` | Public Competition | public / none |
| DELETE | `/api/competitions/{competition_id}` | Delete Competition | OAuth2PasswordBearer |
| GET | `/api/competitions/{competition_id}` | Get Competition | OAuth2PasswordBearer |
| PATCH | `/api/competitions/{competition_id}` | Update Competition | OAuth2PasswordBearer |
| POST | `/api/competitions/{competition_id}/archive` | Archive Competition | OAuth2PasswordBearer |
| GET | `/api/competitions/{competition_id}/certificate/{award}` | Get Event Certificate | OAuth2PasswordBearer |
| GET | `/api/competitions/{competition_id}/certificates` | List Event Certificates | OAuth2PasswordBearer |
| GET | `/api/competitions/{competition_id}/discovery` | Get Event Discovery | OAuth2PasswordBearer |
| GET | `/api/competitions/{competition_id}/discovery/overview` | Get Event Discovery Overview | OAuth2PasswordBearer |
| POST | `/api/competitions/{competition_id}/join` | Join Competition | OAuth2PasswordBearer |
| POST | `/api/competitions/{competition_id}/leave` | Leave Competition | OAuth2PasswordBearer |
| POST | `/api/competitions/{competition_id}/unarchive` | Unarchive Competition | OAuth2PasswordBearer |

### Consent

| Method | Path | Summary | Security |
|---|---|---|---|
| GET | `/api/consent/` | Learner consent and revocation status | OAuth2PasswordBearer |
| POST | `/api/consent/admin/enforce-suppressions` | Apply the suppression ledger | OAuth2PasswordBearer |
| GET | `/api/consent/admin/metrics` | Revocation verification metrics | OAuth2PasswordBearer |
| GET | `/api/consent/admin/revocations` | All revocation workflows | OAuth2PasswordBearer |
| POST | `/api/consent/admin/run-jobs` | Run due purge and verification jobs | OAuth2PasswordBearer |
| GET | `/api/consent/revocations` | The learner's own revocation history | OAuth2PasswordBearer |
| GET | `/api/consent/types` | Available consent types | OAuth2PasswordBearer |
| POST | `/api/consent/{consent_type}/grant` | Grant Consent | OAuth2PasswordBearer |
| POST | `/api/consent/{consent_type}/revoke` | Revoke Consent | OAuth2PasswordBearer |

### Course planning

| Method | Path | Summary | Security |
|---|---|---|---|
| PUT | `/api/courses/{course_id}/cohort-settings` | Update Cohort Settings | OAuth2PasswordBearer |
| POST | `/api/courses/{course_id}/cohorts` | Create Cohort | OAuth2PasswordBearer |
| POST | `/api/courses/{course_id}/cohorts/sync-default` | Sync Default Cohort Members | OAuth2PasswordBearer |
| DELETE | `/api/courses/{course_id}/cohorts/{cohort_id}` | Delete Cohort | OAuth2PasswordBearer |
| PATCH | `/api/courses/{course_id}/cohorts/{cohort_id}` | Update Cohort | OAuth2PasswordBearer |
| PUT | `/api/courses/{course_id}/cohorts/{cohort_id}/members` | Set Cohort Members | OAuth2PasswordBearer |
| POST | `/api/courses/{course_id}/exercise-sets` | Create Set | OAuth2PasswordBearer |
| DELETE | `/api/courses/{course_id}/exercise-sets/{set_id}` | Delete Set | OAuth2PasswordBearer |
| PATCH | `/api/courses/{course_id}/exercise-sets/{set_id}` | Update Set | OAuth2PasswordBearer |
| PUT | `/api/courses/{course_id}/exercise-sets/{set_id}/items` | Set Items | OAuth2PasswordBearer |
| GET | `/api/courses/{course_id}/planning` | Get Planning | OAuth2PasswordBearer |
| GET | `/api/courses/{course_id}/planning/coverage` | Get Coverage | OAuth2PasswordBearer |
| POST | `/api/courses/{course_id}/requirements` | Create Requirement | OAuth2PasswordBearer |
| DELETE | `/api/courses/{course_id}/requirements/{requirement_id}` | Delete Requirement | OAuth2PasswordBearer |
| PATCH | `/api/courses/{course_id}/requirements/{requirement_id}` | Update Requirement | OAuth2PasswordBearer |

### Courses

| Method | Path | Summary | Security |
|---|---|---|---|
| GET | `/api/courses/` | List Courses | OAuth2PasswordBearer |
| POST | `/api/courses/` | Create Course | OAuth2PasswordBearer |
| POST | `/api/courses/join` | Join Course | OAuth2PasswordBearer |
| DELETE | `/api/courses/{course_id}` | Delete Course | OAuth2PasswordBearer |
| GET | `/api/courses/{course_id}` | Get Course | OAuth2PasswordBearer |
| PUT | `/api/courses/{course_id}` | Update Course | OAuth2PasswordBearer |
| GET | `/api/courses/{course_id}/achievements` | List Achievements | OAuth2PasswordBearer |
| POST | `/api/courses/{course_id}/archive` | Archive Course | OAuth2PasswordBearer |
| GET | `/api/courses/{course_id}/assignments` | List Assignments | OAuth2PasswordBearer |
| POST | `/api/courses/{course_id}/assignments` | Create Assignment | OAuth2PasswordBearer |
| PUT | `/api/courses/{course_id}/assignments/reorder` | Reorder Assignments | OAuth2PasswordBearer |
| DELETE | `/api/courses/{course_id}/assignments/{assignment_id}` | Delete Assignment | OAuth2PasswordBearer |
| PUT | `/api/courses/{course_id}/assignments/{assignment_id}` | Update Assignment | OAuth2PasswordBearer |
| POST | `/api/courses/{course_id}/assignments/{assignment_id}/labs` | Add Labs To Assignment | OAuth2PasswordBearer |
| DELETE | `/api/courses/{course_id}/assignments/{assignment_id}/labs/{lab_id}` | Remove Lab From Assignment | OAuth2PasswordBearer |
| GET | `/api/courses/{course_id}/assignments/{assignment_id}/report` | Assignment Class Report | OAuth2PasswordBearer |
| GET | `/api/courses/{course_id}/assignments/{assignment_id}/report/{user_id}` | Assignment Student Report | OAuth2PasswordBearer |
| POST | `/api/courses/{course_id}/enroll-bulk` | Enroll Students Bulk | OAuth2PasswordBearer |
| DELETE | `/api/courses/{course_id}/enroll/{user_id}` | Remove Student | OAuth2PasswordBearer |
| POST | `/api/courses/{course_id}/feedback` | Submit Course Feedback | OAuth2PasswordBearer |
| GET | `/api/courses/{course_id}/feedback/me` | My Course Feedback | OAuth2PasswordBearer |
| GET | `/api/courses/{course_id}/feedback/summary` | Course Feedback Summary | OAuth2PasswordBearer |
| POST | `/api/courses/{course_id}/labs` | Assign Labs | OAuth2PasswordBearer |
| POST | `/api/courses/{course_id}/labs/bulk-remove` | Remove several exercises from a course | OAuth2PasswordBearer |
| PUT | `/api/courses/{course_id}/labs/reorder` | Reorder Labs | OAuth2PasswordBearer |
| DELETE | `/api/courses/{course_id}/labs/{lab_id}` | Remove Lab | OAuth2PasswordBearer |
| PUT | `/api/courses/{course_id}/labs/{lab_id}` | Update Course Lab | OAuth2PasswordBearer |
| POST | `/api/courses/{course_id}/labs/{lab_id}/reset/{user_id}` | Reset Student Lab | OAuth2PasswordBearer |
| POST | `/api/courses/{course_id}/regenerate-invite` | Regenerate Invite | OAuth2PasswordBearer |
| GET | `/api/courses/{course_id}/report` | Class Report | OAuth2PasswordBearer |
| GET | `/api/courses/{course_id}/report/{user_id}` | Student Report | OAuth2PasswordBearer |
| GET | `/api/courses/{course_id}/scoreboard` | Get Scoreboard | OAuth2PasswordBearer |
| GET | `/api/courses/{course_id}/staff` | List Course Staff | OAuth2PasswordBearer |
| POST | `/api/courses/{course_id}/staff` | Add Course Staff | OAuth2PasswordBearer |
| GET | `/api/courses/{course_id}/staff/candidates` | List Course Staff Candidates | OAuth2PasswordBearer |
| DELETE | `/api/courses/{course_id}/staff/{staff_id}` | Remove Course Staff | OAuth2PasswordBearer |
| GET | `/api/courses/{course_id}/students` | List Students | OAuth2PasswordBearer |
| PUT | `/api/courses/{course_id}/students/{user_id}/consent` | Record Minor Consent | OAuth2PasswordBearer |
| GET | `/api/courses/{course_id}/students/{user_id}/labs/{lab_id}/attempts` | Get Student Lab Attempts | OAuth2PasswordBearer |
| POST | `/api/courses/{course_id}/toggle-active` | Toggle Course Active | OAuth2PasswordBearer |
| POST | `/api/courses/{course_id}/unarchive` | Unarchive Course | OAuth2PasswordBearer |

### Curriculum Admin

| Method | Path | Summary | Security |
|---|---|---|---|
| DELETE | `/api/admin/curriculum/levels/{level_id}` | Delete Level | OAuth2PasswordBearer |
| PUT | `/api/admin/curriculum/levels/{level_id}` | Update Level | OAuth2PasswordBearer |
| GET | `/api/admin/curriculum/tracks` | List Tracks | OAuth2PasswordBearer |
| POST | `/api/admin/curriculum/tracks` | Create Track | OAuth2PasswordBearer |
| PUT | `/api/admin/curriculum/tracks/reorder` | Reorder Tracks | OAuth2PasswordBearer |
| DELETE | `/api/admin/curriculum/tracks/{track_id}` | Delete Track | OAuth2PasswordBearer |
| PUT | `/api/admin/curriculum/tracks/{track_id}` | Update Track | OAuth2PasswordBearer |
| POST | `/api/admin/curriculum/tracks/{track_id}/levels` | Create Level | OAuth2PasswordBearer |
| PUT | `/api/admin/curriculum/tracks/{track_id}/levels/reorder` | Reorder Levels | OAuth2PasswordBearer |

### Cyber DNA

| Method | Path | Summary | Security |
|---|---|---|---|
| GET | `/api/dna/v3/affinity` | Cyber DNA career affinity | OAuth2PasswordBearer |
| GET | `/api/dna/v3/behavior` | Cyber DNA behavior profile | OAuth2PasswordBearer |
| GET | `/api/dna/v3/competencies` | Cyber DNA competency scores | OAuth2PasswordBearer |
| GET | `/api/dna/v3/dna` | Cyber DNA learner payload | OAuth2PasswordBearer |
| GET | `/api/dna/v3/evidence` | Cyber DNA evidence ledger | OAuth2PasswordBearer |
| GET | `/api/dna/v3/interest` | Cyber DNA interest vector | OAuth2PasswordBearer |
| GET | `/api/dna/v3/snapshots` | List Cyber DNA snapshots | OAuth2PasswordBearer |
| POST | `/api/dna/v3/snapshots` | Record a Cyber DNA snapshot | OAuth2PasswordBearer |
| GET | `/api/dna/v3/snapshots/{snapshot_id}` | Cyber DNA snapshot | OAuth2PasswordBearer |

### Dashboard

| Method | Path | Summary | Security |
|---|---|---|---|
| GET | `/api/dashboard/celebrations` | Celebration Wall | OAuth2PasswordBearer |
| POST | `/api/dashboard/celebrations/{achievement_id}/celebrate` | Toggle Celebration | OAuth2PasswordBearer |
| GET | `/api/dashboard/instructor/feed` | Instructor Feed | OAuth2PasswordBearer |
| GET | `/api/dashboard/instructor/filter-options` | Instructor Filter Options | OAuth2PasswordBearer |
| GET | `/api/dashboard/instructor/ics-coverage` | Ics Attack Coverage | OAuth2PasswordBearer |
| GET | `/api/dashboard/instructor/learning` | Instructor Learning | OAuth2PasswordBearer |
| GET | `/api/dashboard/instructor/pulse` | Instructor Pulse | OAuth2PasswordBearer |
| GET | `/api/dashboard/instructor/report` | Instructor Report | OAuth2PasswordBearer |
| GET | `/api/dashboard/instructor/stats` | Instructor Stats | OAuth2PasswordBearer |
| GET | `/api/dashboard/student` | Student Dashboard | OAuth2PasswordBearer |

### Evidence

| Method | Path | Summary | Security |
|---|---|---|---|
| GET | `/api/evidence` | List Evidence | OAuth2PasswordBearer |
| POST | `/api/evidence` | Create Evidence | OAuth2PasswordBearer |
| GET | `/api/evidence/analytics` | Evidence Analytics Overview | OAuth2PasswordBearer |
| GET | `/api/evidence/appeals/queue` | Appeal Queue | OAuth2PasswordBearer |
| POST | `/api/evidence/appeals/{appeal_id}/decision` | Decide Appeal | OAuth2PasswordBearer |
| GET | `/api/evidence/queue` | Review Queue | OAuth2PasswordBearer |
| GET | `/api/evidence/rubrics` | List Evidence Rubrics | OAuth2PasswordBearer |
| GET | `/api/evidence/{evidence_id}` | Get Evidence | OAuth2PasswordBearer |
| POST | `/api/evidence/{evidence_id}/appeal` | Appeal Evidence | OAuth2PasswordBearer |
| POST | `/api/evidence/{evidence_id}/review` | Review Evidence | OAuth2PasswordBearer |

### Exercise Quizzes

| Method | Path | Summary | Security |
|---|---|---|---|
| GET | `/api/exercises/labs/{lab_slug}/quiz` | Get Exercise Quiz | OAuth2PasswordBearer |
| GET | `/api/exercises/labs/{lab_slug}/quiz/attempts` | List Exercise Quiz Attempts | OAuth2PasswordBearer |
| POST | `/api/exercises/labs/{lab_slug}/quiz/attempts` | Start Exercise Quiz | OAuth2PasswordBearer |
| POST | `/api/exercises/labs/{lab_slug}/quiz/attempts/{attempt_id}/submit` | Submit Exercise Quiz | OAuth2PasswordBearer |
| POST | `/api/exercises/labs/{lab_slug}/quiz/feedback` | Submit Exercise Quiz Feedback | OAuth2PasswordBearer |

### Exercise Tester

| Method | Path | Summary | Security |
|---|---|---|---|
| POST | `/api/admin/exercise-test` | Run Exercise Test | OAuth2PasswordBearer |
| GET | `/api/admin/exercise-test/active` | Get Active Test Run | OAuth2PasswordBearer |
| POST | `/api/admin/exercise-test/cancel` | Cancel Exercise Test | OAuth2PasswordBearer |
| GET | `/api/admin/exercise-test/events/{run_id}` | Get Test Events | OAuth2PasswordBearer |
| GET | `/api/admin/exercise-test/labs` | List Testable Labs | OAuth2PasswordBearer |
| POST | `/api/admin/exercise-test/report` | Generate Exercise Test Report | OAuth2PasswordBearer |
| DELETE | `/api/admin/exercise-test/results` | Clear All Exercise Test Results | OAuth2PasswordBearer |
| GET | `/api/admin/exercise-test/results` | Get Exercise Test Results | OAuth2PasswordBearer |
| DELETE | `/api/admin/exercise-test/results/{lab_slug}` | Delete Exercise Test Result | OAuth2PasswordBearer |

### Exercise Tester (Instructor)

| Method | Path | Summary | Security |
|---|---|---|---|
| POST | `/api/instructor/exercise-test` | Run Exercise Test | OAuth2PasswordBearer |
| GET | `/api/instructor/exercise-test/active` | Get Active Test Run | OAuth2PasswordBearer |
| POST | `/api/instructor/exercise-test/cancel` | Cancel Exercise Test | OAuth2PasswordBearer |
| GET | `/api/instructor/exercise-test/events/{run_id}` | Get Test Events | OAuth2PasswordBearer |
| GET | `/api/instructor/exercise-test/labs` | List Testable Labs | OAuth2PasswordBearer |
| POST | `/api/instructor/exercise-test/report` | Generate Exercise Test Report | OAuth2PasswordBearer |
| DELETE | `/api/instructor/exercise-test/results` | Clear All Exercise Test Results | OAuth2PasswordBearer |
| GET | `/api/instructor/exercise-test/results` | Get Exercise Test Results | OAuth2PasswordBearer |
| DELETE | `/api/instructor/exercise-test/results/{lab_slug}` | Delete Exercise Test Result | OAuth2PasswordBearer |

### Exercises

| Method | Path | Summary | Security |
|---|---|---|---|
| GET | `/api/exercises/labs/{lab_id}` | Get Lab Details | OAuth2PasswordBearer |
| GET | `/api/exercises/labs/{lab_id}/hint` | Get Hint | OAuth2PasswordBearer |
| POST | `/api/exercises/labs/{lab_id}/submit-flag` | Submit Flag | OAuth2PasswordBearer |
| GET | `/api/exercises/progress` | Get Progress | OAuth2PasswordBearer |
| GET | `/api/exercises/tracks` | List Tracks | OAuth2PasswordBearer |
| GET | `/api/exercises/tracks/{track_slug}` | Get Track | OAuth2PasswordBearer |
| GET | `/api/exercises/tracks/{track_slug}/levels/{level_id}/certificate` | Get a printable level-completion certificate | OAuth2PasswordBearer |
| GET | `/api/exercises/tracks/{track_slug}/levels/{level_id}/certificate.pdf` | Download the certificate as a PDF | OAuth2PasswordBearer |
| GET | `/api/exercises/verify/certificate/{certificate_id}` | Verify Certificate | public / none |
| GET | `/api/exercises/workbooks` | List Workbooks | OAuth2PasswordBearer |

### General

| Method | Path | Summary | Security |
|---|---|---|---|
| GET | `/` | Root | public / none |
| GET | `/api/version` | Api Version | public / none |
| GET | `/health` | Health | public / none |

### Governance

| Method | Path | Summary | Security |
|---|---|---|---|
| GET | `/api/governance/audit/dashboard` | Audit Dashboard | OAuth2PasswordBearer |
| GET | `/api/governance/privacy/dashboard` | Privacy Dashboard | OAuth2PasswordBearer |

### Human review

| Method | Path | Summary | Security |
|---|---|---|---|
| GET | `/api/courses/{course_id}/reviews` | List Course Reviews | OAuth2PasswordBearer |
| POST | `/api/reviews` | Request Review | OAuth2PasswordBearer |
| GET | `/api/reviews/mine` | List My Reviews | OAuth2PasswordBearer |
| PUT | `/api/reviews/{review_id}/decision` | Decide Review | OAuth2PasswordBearer |

### Identity Providers

| Method | Path | Summary | Security |
|---|---|---|---|
| GET | `/api/identity/providers` | List Identity Providers | OAuth2PasswordBearer |
| POST | `/api/identity/providers` | Create Identity Provider | OAuth2PasswordBearer |
| GET | `/api/identity/providers/export` | Export Identity Providers | OAuth2PasswordBearer |
| POST | `/api/identity/providers/import` | Import Identity Providers | OAuth2PasswordBearer |
| DELETE | `/api/identity/providers/{provider_id}` | Delete Identity Provider | OAuth2PasswordBearer |
| PATCH | `/api/identity/providers/{provider_id}` | Update Identity Provider | OAuth2PasswordBearer |
| POST | `/api/identity/providers/{provider_id}/default` | Make Default Identity Provider | OAuth2PasswordBearer |
| POST | `/api/identity/providers/{provider_id}/test` | Test Identity Provider | OAuth2PasswordBearer |

### Impact

| Method | Path | Summary | Security |
|---|---|---|---|
| GET | `/api/impact/catalogue` | Impact Catalogue | OAuth2PasswordBearer |
| GET | `/api/impact/cohort` | Cohort Impact | OAuth2PasswordBearer |
| POST | `/api/impact/contributions` | Submit Contribution | OAuth2PasswordBearer |
| POST | `/api/impact/contributions/{contribution_id}/reject` | Reject Contribution | OAuth2PasswordBearer |
| POST | `/api/impact/contributions/{contribution_id}/verify` | Verify Contribution | OAuth2PasswordBearer |
| GET | `/api/impact/me` | My Impact | OAuth2PasswordBearer |
| GET | `/api/impact/pending` | Pending Contributions | OAuth2PasswordBearer |
| POST | `/api/impact/stewardship/{learner_id}` | Record Stewardship | OAuth2PasswordBearer |

### Instructor

| Method | Path | Summary | Security |
|---|---|---|---|
| GET | `/api/instructor/courses` | List My Courses | OAuth2PasswordBearer |
| GET | `/api/instructor/courses/{course_id}` | Get My Course | OAuth2PasswordBearer |
| GET | `/api/instructor/courses/{course_id}/enrollable-users` | List Enrollable Users | OAuth2PasswordBearer |
| GET | `/api/instructor/labs` | List Available Labs | OAuth2PasswordBearer |
| GET | `/api/instructor/labs/assignments` | Lab Course Assignments | OAuth2PasswordBearer |
| POST | `/api/instructor/labs/upload` | Upload Lab Zip | OAuth2PasswordBearer |
| DELETE | `/api/instructor/labs/{lab_id}` | Delete Own Lab | OAuth2PasswordBearer |
| PUT | `/api/instructor/labs/{lab_id}` | Update Own Lab | OAuth2PasswordBearer |
| GET | `/api/instructor/labs/{lab_id}/export` | Export Own Lab | OAuth2PasswordBearer |
| GET | `/api/instructor/labs/{lab_id}/flag` | Reveal Lab Flag | OAuth2PasswordBearer |
| PUT | `/api/instructor/labs/{lab_id}/visibility` | Update Lab Visibility | OAuth2PasswordBearer |
| GET | `/api/instructor/overview` | Instructor Overview | OAuth2PasswordBearer |
| GET | `/api/instructor/stats` | Instructor Stats | OAuth2PasswordBearer |
| GET | `/api/instructor/tracks-and-levels` | List Tracks And Levels | OAuth2PasswordBearer |

### Journeys

| Method | Path | Summary | Security |
|---|---|---|---|
| GET | `/api/journeys` | List Journeys | OAuth2PasswordBearer |
| GET | `/api/journeys/mine` | My Journey | OAuth2PasswordBearer |
| PUT | `/api/journeys/mine` | Choose Journey | OAuth2PasswordBearer |

### LTI 1.3

| Method | Path | Summary | Security |
|---|---|---|---|
| GET | `/api/lti/admin/links` | List Links | OAuth2PasswordBearer |
| POST | `/api/lti/admin/links/{link_id}/lineitem` | Create Link Lineitem | OAuth2PasswordBearer |
| GET | `/api/lti/admin/links/{link_id}/results` | Get Link Results | OAuth2PasswordBearer |
| GET | `/api/lti/admin/links/{link_id}/roster` | Get Link Roster | OAuth2PasswordBearer |
| GET | `/api/lti/admin/links/{link_id}/roster/saved` | Get Saved Roster | OAuth2PasswordBearer |
| POST | `/api/lti/admin/links/{link_id}/score` | Post Link Score | OAuth2PasswordBearer |
| GET | `/api/lti/admin/links/{link_id}/scores` | List Link Scores | OAuth2PasswordBearer |
| POST | `/api/lti/admin/links/{link_id}/sync-roster` | Sync Link Roster | OAuth2PasswordBearer |
| GET | `/api/lti/admin/platforms` | List Platforms | OAuth2PasswordBearer |
| POST | `/api/lti/admin/platforms` | Create Platform | OAuth2PasswordBearer |
| DELETE | `/api/lti/admin/platforms/{platform_id}` | Delete Platform | OAuth2PasswordBearer |
| PATCH | `/api/lti/admin/platforms/{platform_id}` | Update Platform | OAuth2PasswordBearer |
| POST | `/api/lti/admin/platforms/{platform_id}/test` | Test Platform | OAuth2PasswordBearer |
| GET | `/api/lti/deep-link/{session_token}` | Deep Link Info | OAuth2PasswordBearer |
| POST | `/api/lti/deep-link/{session_token}/response` | Deep Link Response | OAuth2PasswordBearer |
| GET | `/api/lti/jwks` | Tool Jwks | public / none |
| POST | `/api/lti/launch` | Lti Launch | public / none |
| GET | `/api/lti/login` | Lti Login Get | public / none |
| POST | `/api/lti/login` | Lti Login Post | public / none |

### Labs

| Method | Path | Summary | Security |
|---|---|---|---|
| GET | `/api/labs/` | Get Labs | OAuth2PasswordBearer |
| GET | `/api/labs/active` | Get Active Lab | OAuth2PasswordBearer |
| POST | `/api/labs/extend` | Extend Lab Session | OAuth2PasswordBearer |
| POST | `/api/labs/pause` | Pause Lab Session | OAuth2PasswordBearer |
| GET | `/api/labs/prebuild-status` | Prebuild Status | OAuth2PasswordBearer |
| POST | `/api/labs/resume` | Resume Lab Session | OAuth2PasswordBearer |
| GET | `/api/labs/spawn-status/{session_id}` | Get Spawn Status | OAuth2PasswordBearer |
| POST | `/api/labs/spawn/{lab_slug}` | Spawn Lab | OAuth2PasswordBearer |
| POST | `/api/labs/stop` | Stop Lab | OAuth2PasswordBearer |
| GET | `/api/labs/vpn-config` | Get Vpn Config | OAuth2PasswordBearer |
| GET | `/api/labs/vpn-config/qr` | Get Vpn Config Qr | OAuth2PasswordBearer |
| GET | `/api/labs/vpn-status` | Get Vpn Status | OAuth2PasswordBearer |

### Modules

| Method | Path | Summary | Security |
|---|---|---|---|
| GET | `/api/modules/` | Get Modules Status | OAuth2PasswordBearer |

### NICE Framework

| Method | Path | Summary | Security |
|---|---|---|---|
| GET | `/api/nice/components` | Nice Components | OAuth2PasswordBearer |
| GET | `/api/nice/coverage` | Nice Coverage | OAuth2PasswordBearer |
| POST | `/api/nice/labs/seed` | Seed Nice Lab Mappings | OAuth2PasswordBearer |
| GET | `/api/nice/labs/{lab_id}` | Get Lab Nice Mappings | OAuth2PasswordBearer |
| PUT | `/api/nice/labs/{lab_id}` | Set Lab Nice Mappings | OAuth2PasswordBearer |
| POST | `/api/nice/labs/{lab_id}/review` | Review Lab Nice Mappings | OAuth2PasswordBearer |
| POST | `/api/nice/refresh` | Refresh Nice Framework | OAuth2PasswordBearer |
| GET | `/api/nice/status` | Nice Status | OAuth2PasswordBearer |

### Open Badges

| Method | Path | Summary | Security |
|---|---|---|---|
| GET | `/api/admin/badges` | List Badges | OAuth2PasswordBearer |
| POST | `/api/admin/badges/rotate-key` | Rotate Badge Key | OAuth2PasswordBearer |
| GET | `/api/admin/badges/settings` | Badge Settings | OAuth2PasswordBearer |
| PUT | `/api/admin/badges/settings` | Update Badge Settings | OAuth2PasswordBearer |
| POST | `/api/admin/badges/{badge_id}/revoke` | Revoke Badge | OAuth2PasswordBearer |
| GET | `/api/badges/achievements/{certificate_id}` | Achievement Definition | public / none |
| GET | `/api/badges/achievements/{certificate_id}/image` | Achievement Image | public / none |
| GET | `/api/badges/credentials/{jti}` | Hosted Credential | public / none |
| GET | `/api/badges/credentials/{jti}/jwt` | Hosted Credential Jwt | public / none |
| GET | `/api/badges/credentials/{jti}/status` | Credential Status | public / none |
| POST | `/api/badges/events/issue` | Issue Event Badge | OAuth2PasswordBearer |
| POST | `/api/badges/issue` | Issue Badge | OAuth2PasswordBearer |
| GET | `/api/badges/issuer` | Issuer Profile | public / none |
| GET | `/api/badges/issuer/jwks` | Issuer Jwks | public / none |
| GET | `/api/badges/mine` | My Badges | OAuth2PasswordBearer |
| POST | `/api/badges/{badge_id}/consent` | Badge Consent | OAuth2PasswordBearer |

### Portfolio shares

| Method | Path | Summary | Security |
|---|---|---|---|
| GET | `/api/profile/shares` | List portfolio share links | OAuth2PasswordBearer |
| POST | `/api/profile/shares` | Create a portfolio share link | OAuth2PasswordBearer |
| DELETE | `/api/profile/shares/{share_id}` | Revoke a portfolio share link | OAuth2PasswordBearer |
| GET | `/api/public/portfolio/{token}` | Read a shared portfolio | OAuth2PasswordBearer |

### Practice

| Method | Path | Summary | Security |
|---|---|---|---|
| GET | `/api/practice/pathways` | Practice Pathways | OAuth2PasswordBearer |
| GET | `/api/practice/progress` | Practice Progress | OAuth2PasswordBearer |
| GET | `/api/practice/sessions` | Practice History | OAuth2PasswordBearer |
| POST | `/api/practice/sessions` | Start Session | OAuth2PasswordBearer |
| GET | `/api/practice/sessions/{session_id}` | Get Session | OAuth2PasswordBearer |
| POST | `/api/practice/sessions/{session_id}/submit` | Submit Session | OAuth2PasswordBearer |

### Profile

| Method | Path | Summary | Security |
|---|---|---|---|
| GET | `/api/profile/career-assessment` | Short career-direction questions | OAuth2PasswordBearer |
| POST | `/api/profile/career-assessment` | Score a short career-direction check | OAuth2PasswordBearer |
| GET | `/api/profile/career-dossier` | Career-profile dossier (JSON) | OAuth2PasswordBearer |
| GET | `/api/profile/career-dossier.html` | Career-profile dossier (HTML) | OAuth2PasswordBearer |
| GET | `/api/profile/career-dossier.md` | Career-profile dossier (Markdown) | OAuth2PasswordBearer |
| GET | `/api/profile/competencies` | Learner competency assessment profile | OAuth2PasswordBearer |
| POST | `/api/profile/gps` | Optional cybersecurity GPS direction finder | OAuth2PasswordBearer |
| GET | `/api/profile/portfolio` | Professional portfolio (JSON) | OAuth2PasswordBearer |
| GET | `/api/profile/portfolio.html` | Professional portfolio (printable HTML) | OAuth2PasswordBearer |
| GET | `/api/profile/portfolio.md` | Professional portfolio (Markdown) | OAuth2PasswordBearer |
| GET | `/api/profile/role-readiness` | Role readiness answer | OAuth2PasswordBearer |
| GET | `/api/profile/roles` | Career pathway catalogue | OAuth2PasswordBearer |
| GET | `/api/profile/skill-dna` | Learner Skill DNA character sheet | OAuth2PasswordBearer |
| GET | `/api/profile/snapshots` | Stored report snapshots | OAuth2PasswordBearer |
| GET | `/api/profile/snapshots/{snapshot_id}` | Stored report snapshot | OAuth2PasswordBearer |
| GET | `/api/profile/snapshots/{snapshot_id}/html` | Stored report (HTML) | OAuth2PasswordBearer |
| GET | `/api/profile/snapshots/{snapshot_id}/markdown` | Stored report (Markdown) | OAuth2PasswordBearer |
| GET | `/api/profile/summary` | Profile snapshot with certificates and completions | OAuth2PasswordBearer |
| PUT | `/api/profile/title` | Equip an unlocked achievement title | OAuth2PasswordBearer |
| GET | `/api/profile/transcript.pdf` | Download a printable completion transcript | OAuth2PasswordBearer |

### Public config

| Method | Path | Summary | Security |
|---|---|---|---|
| GET | `/api/config/public` | Public Config | public / none |
| GET | `/api/public/community-events` | Community Events | public / none |

### Public usage

| Method | Path | Summary | Security |
|---|---|---|---|
| GET | `/api/public/qr/{source}` | Qr Landing | public / none |

### Question Banks

| Method | Path | Summary | Security |
|---|---|---|---|
| GET | `/api/admin/question-banks` | List certification question banks | OAuth2PasswordBearer |
| POST | `/api/admin/question-banks/validate` | Validate the question banks | OAuth2PasswordBearer |
| GET | `/api/admin/question-banks/{pathway_id}` | Read one certification question bank | OAuth2PasswordBearer |

### Quizzes

| Method | Path | Summary | Security |
|---|---|---|---|
| GET | `/api/exercises/tracks/{track_slug}/levels/{level_id}/quiz` | Get Level Quiz | OAuth2PasswordBearer |
| GET | `/api/exercises/tracks/{track_slug}/levels/{level_id}/quiz/attempts` | List Quiz Attempts | OAuth2PasswordBearer |
| POST | `/api/exercises/tracks/{track_slug}/levels/{level_id}/quiz/submit` | Submit Level Quiz | OAuth2PasswordBearer |

### RangeBox

| Method | Path | Summary | Security |
|---|---|---|---|
| GET | `/api/rangebox/capacity` | Rangebox Capacity | OAuth2PasswordBearer |
| DELETE | `/api/rangebox/standalone/destroy` | Standalone Rangebox Destroy | OAuth2PasswordBearer |
| POST | `/api/rangebox/standalone/launch` | Standalone Rangebox Launch | OAuth2PasswordBearer |
| GET | `/api/rangebox/standalone/status` | Standalone Rangebox Status | OAuth2PasswordBearer |
| GET | `/api/rangebox/transport` | Rangebox Transport | OAuth2PasswordBearer |
| POST | `/api/rangebox/ws-ticket` | Get Ws Ticket | OAuth2PasswordBearer |
| GET | `/api/rangebox/{session_id}/lab` | Rangebox Lab | OAuth2PasswordBearer |
| GET | `/api/rangebox/{session_id}/status` | Rangebox Status | OAuth2PasswordBearer |

### Recognition

| Method | Path | Summary | Security |
|---|---|---|---|
| POST | `/api/recognition/evaluate` | Evaluate Recognition | OAuth2PasswordBearer |
| GET | `/api/recognition/me` | My Recognition | OAuth2PasswordBearer |
| POST | `/api/recognition/seen` | Mark Seen | OAuth2PasswordBearer |
| POST | `/api/recognition/{learner_id}/award` | Manual Award | OAuth2PasswordBearer |

### Reports

| Method | Path | Summary | Security |
|---|---|---|---|
| GET | `/api/courses/{course_id}/reports` | List Reports | OAuth2PasswordBearer |
| GET | `/api/courses/{course_id}/reports/coaching-queue.csv` | Coaching Queue Csv | OAuth2PasswordBearer |
| GET | `/api/courses/{course_id}/reports/coaching-queue.pdf` | Coaching Queue Pdf | OAuth2PasswordBearer |
| GET | `/api/courses/{course_id}/reports/course-health.pdf` | Course Health Report | OAuth2PasswordBearer |
| GET | `/api/courses/{course_id}/reports/exercise-diagnostics.csv` | Exercise Diagnostics Csv | OAuth2PasswordBearer |
| GET | `/api/courses/{course_id}/reports/exercise-diagnostics.pdf` | Exercise Diagnostics Report | OAuth2PasswordBearer |
| POST | `/api/reports/verify` | Verify Report File | public / none |

### Security administration

| Method | Path | Summary | Security |
|---|---|---|---|
| GET | `/api/admin/security/access-rules` | List sign-in and registration allow/deny rules | OAuth2PasswordBearer |
| POST | `/api/admin/security/access-rules` | Add a sign-in or registration allow/deny rule | OAuth2PasswordBearer |
| POST | `/api/admin/security/access-rules/test` | Explain how the current rules evaluate one request | OAuth2PasswordBearer |
| DELETE | `/api/admin/security/access-rules/{rule_id}` | Remove a sign-in or registration allow/deny rule | OAuth2PasswordBearer |
| GET | `/api/admin/security/break-glass` | Break-glass grants and review state | OAuth2PasswordBearer |
| POST | `/api/admin/security/break-glass` | Request time-bound emergency access | OAuth2PasswordBearer |
| POST | `/api/admin/security/break-glass/{grant_id}/approve` | Approve a pending grant | OAuth2PasswordBearer |
| POST | `/api/admin/security/break-glass/{grant_id}/review` | Close the post-use review | OAuth2PasswordBearer |
| POST | `/api/admin/security/break-glass/{grant_id}/revoke` | Revoke a grant | OAuth2PasswordBearer |
| GET | `/api/admin/security/events` | Query security, audit, and privacy events | OAuth2PasswordBearer |
| GET | `/api/admin/security/events/summary` | Security event counts and top event types | OAuth2PasswordBearer |
| GET | `/api/admin/security/events/{event_id}` | One security event | OAuth2PasswordBearer |
| POST | `/api/admin/security/rbac/check` | Explain one authorization decision | OAuth2PasswordBearer |
| GET | `/api/admin/security/rbac/matrix` | Role and policy access matrix | OAuth2PasswordBearer |
| GET | `/api/admin/security/rbac/permissions` | Reviewed permission catalog | OAuth2PasswordBearer |
| GET | `/api/admin/security/rbac/roles` | Roles, grants, and effective permission counts | OAuth2PasswordBearer |
| PUT | `/api/admin/security/rbac/roles/{role_key}/permissions` | Replace one role's permission grants | OAuth2PasswordBearer |
| GET | `/api/admin/security/rbac/users/{user_id}` | Effective roles and permissions | OAuth2PasswordBearer |
| POST | `/api/admin/security/rbac/users/{user_id}/roles` | Grant an expiring extra role | OAuth2PasswordBearer |
| DELETE | `/api/admin/security/rbac/users/{user_id}/roles/{role_key}` | Revoke an extra role | OAuth2PasswordBearer |
| GET | `/api/admin/security/service-identities` | List non-human service credentials | OAuth2PasswordBearer |
| POST | `/api/admin/security/service-identities` | Create a scoped service credential | OAuth2PasswordBearer |
| DELETE | `/api/admin/security/service-identities/{credential_id}` | Revoke a service credential | OAuth2PasswordBearer |

### Settings

| Method | Path | Summary | Security |
|---|---|---|---|
| GET | `/api/settings/` | Get All Settings | OAuth2PasswordBearer |
| PUT | `/api/settings/` | Update Settings | OAuth2PasswordBearer |
| GET | `/api/settings/achievement-catalogue` | Grouped achievement catalogue for the studio | OAuth2PasswordBearer |
| GET | `/api/settings/change-requests` | List Change Requests | OAuth2PasswordBearer |
| POST | `/api/settings/change-requests/{change_id}/revert` | Revert Change Request | OAuth2PasswordBearer |
| GET | `/api/settings/custom-achievements` | List custom achievements | OAuth2PasswordBearer |
| POST | `/api/settings/custom-achievements` | Create a custom achievement | OAuth2PasswordBearer |
| DELETE | `/api/settings/custom-achievements/{achievement_id}` | Delete a custom achievement | OAuth2PasswordBearer |
| PUT | `/api/settings/custom-achievements/{achievement_id}` | Update a custom achievement | OAuth2PasswordBearer |
| POST | `/api/settings/mail/test` | Send Mail Test | OAuth2PasswordBearer |
| POST | `/api/settings/production/cutover` | Production Cutover | OAuth2PasswordBearer |
| GET | `/api/settings/production/preview` | Production Preview | OAuth2PasswordBearer |
| GET | `/api/settings/{category}` | Get Settings By Category | OAuth2PasswordBearer |

### Setup

| Method | Path | Summary | Security |
|---|---|---|---|
| POST | `/api/setup/complete` | Complete Setup | public / none |
| GET | `/api/setup/config` | Public Config | public / none |
| GET | `/api/setup/status` | Setup Status | public / none |

### Single Sign-On

| Method | Path | Summary | Security |
|---|---|---|---|
| POST | `/api/auth/sso/exchange` | Exchange Ticket | public / none |
| POST | `/api/auth/sso/ldap/{provider_id}/login` | Ldap Login | public / none |
| GET | `/api/auth/sso/oidc/{provider_id}/callback` | Oidc Callback | public / none |
| GET | `/api/auth/sso/oidc/{provider_id}/login` | Oidc Login | public / none |
| GET | `/api/auth/sso/providers` | List Sso Providers | public / none |
| POST | `/api/auth/sso/saml/{provider_id}/acs` | Saml Acs | public / none |
| GET | `/api/auth/sso/saml/{provider_id}/login` | Saml Login | public / none |

### Threat awareness

| Method | Path | Summary | Security |
|---|---|---|---|
| GET | `/api/ransomware-activity` | Get Ransomware Activity | OAuth2PasswordBearer |
| GET | `/api/threat-awareness` | Get Threat Awareness | OAuth2PasswordBearer |

### Usage

| Method | Path | Summary | Security |
|---|---|---|---|
| GET | `/api/usage/admin` | Admin Usage | OAuth2PasswordBearer |
| GET | `/api/usage/admin.csv` | Admin Usage Csv | OAuth2PasswordBearer |
| GET | `/api/usage/admin/qr` | Admin Qr Png | OAuth2PasswordBearer |
| GET | `/api/usage/public` | Public Usage | public / none |
| GET | `/api/usage/public.csv` | Public Usage Csv | public / none |

### Workbook

| Method | Path | Summary | Security |
|---|---|---|---|
| POST | `/api/admin/workbook/build` | Trigger Build | OAuth2PasswordBearer |
| POST | `/api/admin/workbook/build-all-course-wikis` | Build All Course Wikis | OAuth2PasswordBearer |
| DELETE | `/api/admin/workbook/chapter/{chapter_dir}` | Delete Chapter | OAuth2PasswordBearer |
| GET | `/api/admin/workbook/chapters` | List Chapters | OAuth2PasswordBearer |
| POST | `/api/admin/workbook/upload` | Upload Chapter | OAuth2PasswordBearer |

### Workbook answers

| Method | Path | Summary | Security |
|---|---|---|---|
| GET | `/api/workbook-answers` | List My Answers | OAuth2PasswordBearer |
| GET | `/api/workbook-answers/options` | Answer Options | OAuth2PasswordBearer |
| GET | `/api/workbook-answers/{lab_slug}` | Get My Answer | OAuth2PasswordBearer |
| PUT | `/api/workbook-answers/{lab_slug}` | Save My Answer | OAuth2PasswordBearer |


## WebSocket and streaming surfaces

OpenAPI does not describe WebSocket handshakes. These surfaces are exposed by
the application and are documented here for completeness.

| Method | Path | Purpose |
|---|---|---|
| WS | `/api/rangebox/{session_id}/vnc` | Student RangeBox VNC proxy; short-lived WebSocket ticket in the query string. |
| WS | `/api/rangebox/standalone/vnc` | Standalone RangeBox VNC proxy; short-lived WebSocket ticket in the query string. |
| WS | `/api/rangebox/admin/{user_id}/{session_id}/vnc` | Admin View-As RangeBox VNC proxy; read-only. |

## Full operation index

| Method | Path | Summary | Security |
|---|---|---|---|
| GET | / | Root | public / none |
| GET | /api/about | Get About | OAuth2PasswordBearer |
| GET | /api/about/licences/{name} | Get Licence | OAuth2PasswordBearer |
| GET | /api/about/sbom/{name} | Get Sbom | OAuth2PasswordBearer |
| GET | /api/accommodations/me | Get My Accommodation | OAuth2PasswordBearer |
| GET | /api/admin/activity | Get Activity Log | OAuth2PasswordBearer |
| POST | /api/admin/activity/clear | Clear Activity Log | OAuth2PasswordBearer |
| GET | /api/admin/activity/export | Export Activity Log | OAuth2PasswordBearer |
| GET | /api/admin/audit/impersonations | Admin Impersonation Sessions | OAuth2PasswordBearer |
| GET | /api/admin/audit/users/by-username/{username}/history | Admin User History By Username | OAuth2PasswordBearer |
| GET | /api/admin/audit/users/{user_id}/history | Admin User History | OAuth2PasswordBearer |
| GET | /api/admin/badges | List Badges | OAuth2PasswordBearer |
| POST | /api/admin/badges/rotate-key | Rotate Badge Key | OAuth2PasswordBearer |
| GET | /api/admin/badges/settings | Badge Settings | OAuth2PasswordBearer |
| PUT | /api/admin/badges/settings | Update Badge Settings | OAuth2PasswordBearer |
| POST | /api/admin/badges/{badge_id}/revoke | Revoke Badge | OAuth2PasswordBearer |
| GET | /api/admin/competency-coverage | Competency Coverage | OAuth2PasswordBearer |
| POST | /api/admin/containers/cleanup-orphaned | Cleanup Orphaned Containers | OAuth2PasswordBearer |
| GET | /api/admin/courses/{course_id}/retention | Get Retention Policy | OAuth2PasswordBearer |
| PUT | /api/admin/courses/{course_id}/retention | Set Retention Policy | OAuth2PasswordBearer |
| POST | /api/admin/courses/{course_id}/retention/complete | Complete Retention | OAuth2PasswordBearer |
| POST | /api/admin/courses/{course_id}/retention/preview | Preview Retention | OAuth2PasswordBearer |
| GET | /api/admin/courses/{course_id}/retention/runs | List Retention Runs | OAuth2PasswordBearer |
| DELETE | /api/admin/curriculum/levels/{level_id} | Delete Level | OAuth2PasswordBearer |
| PUT | /api/admin/curriculum/levels/{level_id} | Update Level | OAuth2PasswordBearer |
| GET | /api/admin/curriculum/tracks | List Tracks | OAuth2PasswordBearer |
| POST | /api/admin/curriculum/tracks | Create Track | OAuth2PasswordBearer |
| PUT | /api/admin/curriculum/tracks/reorder | Reorder Tracks | OAuth2PasswordBearer |
| DELETE | /api/admin/curriculum/tracks/{track_id} | Delete Track | OAuth2PasswordBearer |
| PUT | /api/admin/curriculum/tracks/{track_id} | Update Track | OAuth2PasswordBearer |
| POST | /api/admin/curriculum/tracks/{track_id}/levels | Create Level | OAuth2PasswordBearer |
| PUT | /api/admin/curriculum/tracks/{track_id}/levels/reorder | Reorder Levels | OAuth2PasswordBearer |
| GET | /api/admin/data-labels/policy | Get Data Label Policy | OAuth2PasswordBearer |
| GET | /api/admin/docker/disk-usage | Get Docker Disk Usage | OAuth2PasswordBearer |
| POST | /api/admin/docker/prune-build-cache | Prune Build Cache | OAuth2PasswordBearer |
| POST | /api/admin/docker/prune-images | Prune All Images | OAuth2PasswordBearer |
| POST | /api/admin/exercise-test | Run Exercise Test | OAuth2PasswordBearer |
| GET | /api/admin/exercise-test/active | Get Active Test Run | OAuth2PasswordBearer |
| POST | /api/admin/exercise-test/cancel | Cancel Exercise Test | OAuth2PasswordBearer |
| GET | /api/admin/exercise-test/events/{run_id} | Get Test Events | OAuth2PasswordBearer |
| GET | /api/admin/exercise-test/labs | List Testable Labs | OAuth2PasswordBearer |
| POST | /api/admin/exercise-test/report | Generate Exercise Test Report | OAuth2PasswordBearer |
| DELETE | /api/admin/exercise-test/results | Clear All Exercise Test Results | OAuth2PasswordBearer |
| GET | /api/admin/exercise-test/results | Get Exercise Test Results | OAuth2PasswordBearer |
| DELETE | /api/admin/exercise-test/results/{lab_slug} | Delete Exercise Test Result | OAuth2PasswordBearer |
| POST | /api/admin/impersonate/disconnect | Disconnect Impersonation | OAuth2PasswordBearer |
| POST | /api/admin/impersonate/launch | Impersonate Launch Lab | OAuth2PasswordBearer |
| GET | /api/admin/impersonate/status | Impersonation Status | OAuth2PasswordBearer |
| POST | /api/admin/impersonate/{session_id} | Impersonate Session | OAuth2PasswordBearer |
| GET | /api/admin/labs | List Labs | OAuth2PasswordBearer |
| POST | /api/admin/labs | Create Lab | OAuth2PasswordBearer |
| POST | /api/admin/labs/bulk-toggle | Bulk Toggle Labs | OAuth2PasswordBearer |
| POST | /api/admin/labs/discover | Discover Labs | OAuth2PasswordBearer |
| POST | /api/admin/labs/import | Import Exercise | OAuth2PasswordBearer |
| PUT | /api/admin/labs/{lab_id} | Update Lab | OAuth2PasswordBearer |
| POST | /api/admin/labs/{lab_id}/approve | Approve Lab | OAuth2PasswordBearer |
| PUT | /api/admin/labs/{lab_id}/compose | Update Lab Compose | OAuth2PasswordBearer |
| GET | /api/admin/labs/{lab_id}/details | Get Lab Details Admin | OAuth2PasswordBearer |
| GET | /api/admin/labs/{lab_id}/export | Export Exercise | OAuth2PasswordBearer |
| DELETE | /api/admin/labs/{lab_id}/images | Delete Lab Images | OAuth2PasswordBearer |
| GET | /api/admin/labs/{lab_id}/images | Get Lab Images | OAuth2PasswordBearer |
| POST | /api/admin/labs/{lab_id}/reject | Reject Lab | OAuth2PasswordBearer |
| POST | /api/admin/labs/{lab_id}/toggle | Toggle Lab | OAuth2PasswordBearer |
| GET | /api/admin/question-banks | List certification question banks | OAuth2PasswordBearer |
| POST | /api/admin/question-banks/validate | Validate the question banks | OAuth2PasswordBearer |
| GET | /api/admin/question-banks/{pathway_id} | Read one certification question bank | OAuth2PasswordBearer |
| GET | /api/admin/rangebox-capacity | Get Rangebox Capacity | OAuth2PasswordBearer |
| POST | /api/admin/rangebox-capacity/test | Run Rangebox Capacity Test | OAuth2PasswordBearer |
| GET | /api/admin/retention/due | List Retention Due | OAuth2PasswordBearer |
| GET | /api/admin/security/access-rules | List sign-in and registration allow/deny rules | OAuth2PasswordBearer |
| POST | /api/admin/security/access-rules | Add a sign-in or registration allow/deny rule | OAuth2PasswordBearer |
| POST | /api/admin/security/access-rules/test | Explain how the current rules evaluate one request | OAuth2PasswordBearer |
| DELETE | /api/admin/security/access-rules/{rule_id} | Remove a sign-in or registration allow/deny rule | OAuth2PasswordBearer |
| GET | /api/admin/security/break-glass | Break-glass grants and review state | OAuth2PasswordBearer |
| POST | /api/admin/security/break-glass | Request time-bound emergency access | OAuth2PasswordBearer |
| POST | /api/admin/security/break-glass/{grant_id}/approve | Approve a pending grant | OAuth2PasswordBearer |
| POST | /api/admin/security/break-glass/{grant_id}/review | Close the post-use review | OAuth2PasswordBearer |
| POST | /api/admin/security/break-glass/{grant_id}/revoke | Revoke a grant | OAuth2PasswordBearer |
| GET | /api/admin/security/events | Query security, audit, and privacy events | OAuth2PasswordBearer |
| GET | /api/admin/security/events/summary | Security event counts and top event types | OAuth2PasswordBearer |
| GET | /api/admin/security/events/{event_id} | One security event | OAuth2PasswordBearer |
| POST | /api/admin/security/rbac/check | Explain one authorization decision | OAuth2PasswordBearer |
| GET | /api/admin/security/rbac/matrix | Role and policy access matrix | OAuth2PasswordBearer |
| GET | /api/admin/security/rbac/permissions | Reviewed permission catalog | OAuth2PasswordBearer |
| GET | /api/admin/security/rbac/roles | Roles, grants, and effective permission counts | OAuth2PasswordBearer |
| PUT | /api/admin/security/rbac/roles/{role_key}/permissions | Replace one role's permission grants | OAuth2PasswordBearer |
| GET | /api/admin/security/rbac/users/{user_id} | Effective roles and permissions | OAuth2PasswordBearer |
| POST | /api/admin/security/rbac/users/{user_id}/roles | Grant an expiring extra role | OAuth2PasswordBearer |
| DELETE | /api/admin/security/rbac/users/{user_id}/roles/{role_key} | Revoke an extra role | OAuth2PasswordBearer |
| GET | /api/admin/security/service-identities | List non-human service credentials | OAuth2PasswordBearer |
| POST | /api/admin/security/service-identities | Create a scoped service credential | OAuth2PasswordBearer |
| DELETE | /api/admin/security/service-identities/{credential_id} | Revoke a service credential | OAuth2PasswordBearer |
| GET | /api/admin/sessions/active | List Active Sessions | OAuth2PasswordBearer |
| GET | /api/admin/sessions/health | Get Sessions Health | OAuth2PasswordBearer |
| DELETE | /api/admin/sessions/history | Clear Session History | OAuth2PasswordBearer |
| GET | /api/admin/sessions/history | Session History | OAuth2PasswordBearer |
| POST | /api/admin/sessions/terminate-all | Terminate All Sessions | OAuth2PasswordBearer |
| POST | /api/admin/sessions/terminate/{session_id} | Terminate Session | OAuth2PasswordBearer |
| GET | /api/admin/sessions/{session_id}/logs | Get Session Logs | OAuth2PasswordBearer |
| POST | /api/admin/sessions/{session_id}/reset-stale | Reset Stale Session | OAuth2PasswordBearer |
| POST | /api/admin/sessions/{session_id}/resync-vpn | Resync Session Vpn | OAuth2PasswordBearer |
| GET | /api/admin/stats | Get Stats | OAuth2PasswordBearer |
| POST | /api/admin/stress-test | Start Stress Test | OAuth2PasswordBearer |
| GET | /api/admin/stress-test/active | Get Active Stress Test | OAuth2PasswordBearer |
| POST | /api/admin/stress-test/cancel | Cancel Stress Test | OAuth2PasswordBearer |
| POST | /api/admin/stress-test/cleanup | Stress Test Cleanup | OAuth2PasswordBearer |
| GET | /api/admin/stress-test/events/{run_id} | Get Stress Test Events | OAuth2PasswordBearer |
| GET | /api/admin/stress-test/last-result | Get Last Stress Result | OAuth2PasswordBearer |
| POST | /api/admin/stress-test/report | Generate Stress Report Pdf | OAuth2PasswordBearer |
| GET | /api/admin/system/activity-calendar | Activity Calendar | OAuth2PasswordBearer |
| POST | /api/admin/system/backup | Create Backup | OAuth2PasswordBearer |
| GET | /api/admin/system/backups | List Backups | OAuth2PasswordBearer |
| DELETE | /api/admin/system/backups/{filename} | Delete Backup | OAuth2PasswordBearer |
| GET | /api/admin/system/backups/{filename} | Download Backup | OAuth2PasswordBearer |
| GET | /api/admin/system/data-integrity | Get Data Integrity Status | OAuth2PasswordBearer |
| POST | /api/admin/system/data-integrity/review | Review Data Integrity Write | OAuth2PasswordBearer |
| GET | /api/admin/system/ha | Read-only HA status snapshot | OAuth2PasswordBearer |
| GET | /api/admin/system/metrics | Get System Metrics | OAuth2PasswordBearer |
| POST | /api/admin/system/metrics/sample | Sample System Metrics | OAuth2PasswordBearer |
| GET | /api/admin/system/release | Compare this installation with the latest GitHub release | OAuth2PasswordBearer |
| POST | /api/admin/system/restore | Restore Backup | OAuth2PasswordBearer |
| POST | /api/admin/system/restore/upload | Restore Uploaded Backup | OAuth2PasswordBearer |
| GET | /api/admin/system/software-integrity | Verify deployed lab content against the release manifest | OAuth2PasswordBearer |
| GET | /api/admin/system/status | System Status | OAuth2PasswordBearer |
| GET | /api/admin/users | List Users | OAuth2PasswordBearer |
| POST | /api/admin/users/approve | Approve User | OAuth2PasswordBearer |
| POST | /api/admin/users/create | Create User | OAuth2PasswordBearer |
| GET | /api/admin/users/export | Export Users | OAuth2PasswordBearer |
| POST | /api/admin/users/import | Import Users | OAuth2PasswordBearer |
| GET | /api/admin/users/locked | List Locked Users | OAuth2PasswordBearer |
| GET | /api/admin/users/pending | List Pending Users | OAuth2PasswordBearer |
| DELETE | /api/admin/users/{user_id} | Delete User | OAuth2PasswordBearer |
| GET | /api/admin/users/{user_id} | Get User | OAuth2PasswordBearer |
| PUT | /api/admin/users/{user_id} | Update User | OAuth2PasswordBearer |
| GET | /api/admin/users/{user_id}/details | Get User Details | OAuth2PasswordBearer |
| POST | /api/admin/users/{user_id}/force-logout | Force Logout User | OAuth2PasswordBearer |
| POST | /api/admin/users/{user_id}/labs/{lab_id}/reset | Reset User Lab | OAuth2PasswordBearer |
| POST | /api/admin/users/{user_id}/mfa/reset | Reset another account's MFA | OAuth2PasswordBearer |
| POST | /api/admin/users/{user_id}/reset-password | Reset Password | OAuth2PasswordBearer |
| POST | /api/admin/users/{user_id}/unlock | Unlock User | OAuth2PasswordBearer |
| DELETE | /api/admin/vpn/peer-by-key/{public_key} | Remove Vpn Peer By Key | OAuth2PasswordBearer |
| DELETE | /api/admin/vpn/peer/{user_id} | Remove Vpn Peer | OAuth2PasswordBearer |
| GET | /api/admin/vpn/peers | List Vpn Peers | OAuth2PasswordBearer |
| POST | /api/admin/vpn/peers/{user_id}/repair | Repair Vpn Peer | OAuth2PasswordBearer |
| POST | /api/admin/vpn/reconcile-peers | Reconcile Vpn Peers | OAuth2PasswordBearer |
| POST | /api/admin/vpn/register/{user_id} | Register Vpn Peer | OAuth2PasswordBearer |
| GET | /api/admin/vpn/status | Vpn Sync Status | OAuth2PasswordBearer |
| POST | /api/admin/vpn/sync | Sync Vpn Peers | OAuth2PasswordBearer |
| POST | /api/admin/workbook/build | Trigger Build | OAuth2PasswordBearer |
| POST | /api/admin/workbook/build-all-course-wikis | Build All Course Wikis | OAuth2PasswordBearer |
| DELETE | /api/admin/workbook/chapter/{chapter_dir} | Delete Chapter | OAuth2PasswordBearer |
| GET | /api/admin/workbook/chapters | List Chapters | OAuth2PasswordBearer |
| POST | /api/admin/workbook/upload | Upload Chapter | OAuth2PasswordBearer |
| GET | /api/analytics/courses/{course_id}/competency | Course Competency | OAuth2PasswordBearer |
| GET | /api/analytics/courses/{course_id}/exercises | Course Exercises | OAuth2PasswordBearer |
| POST | /api/analytics/courses/{course_id}/labs/{lab_id}/reviews | Add Lab Health Review | OAuth2PasswordBearer |
| GET | /api/analytics/courses/{course_id}/overview | Course Overview | OAuth2PasswordBearer |
| GET | /api/analytics/courses/{course_id}/pulse-comments | Course Pulse Comments | OAuth2PasswordBearer |
| GET | /api/analytics/courses/{course_id}/readiness | Course Readiness | OAuth2PasswordBearer |
| GET | /api/analytics/courses/{course_id}/readiness/calibration | Readiness Calibration | OAuth2PasswordBearer |
| GET | /api/analytics/courses/{course_id}/students/{user_id}/capabilities | Student Capabilities | OAuth2PasswordBearer |
| POST | /api/analytics/courses/{course_id}/students/{user_id}/notes | Add Readiness Note | OAuth2PasswordBearer |
| POST | /api/analytics/events/workbook-open | Workbook Opened | OAuth2PasswordBearer |
| GET | /api/analytics/metrics | Metric Dictionary | OAuth2PasswordBearer |
| GET | /api/analytics/pulse/{lab_id} | Get Pulse | OAuth2PasswordBearer |
| POST | /api/analytics/pulse/{lab_id} | Submit Pulse | OAuth2PasswordBearer |
| GET | /api/analytics/reaction/{lab_id} | Get Exercise Reaction | OAuth2PasswordBearer |
| POST | /api/analytics/reaction/{lab_id} | Set Exercise Reaction | OAuth2PasswordBearer |
| GET | /api/analytics/reports/activity | Reports Activity | OAuth2PasswordBearer |
| GET | /api/analytics/reports/curriculum-demand | Curriculum Demand | OAuth2PasswordBearer |
| POST | /api/analytics/reports/export-audit | Audit Report Export | OAuth2PasswordBearer |
| GET | /api/analytics/reports/export.pdf | Reports Export Pdf | OAuth2PasswordBearer |
| GET | /api/analytics/reports/overview | Reports Overview | OAuth2PasswordBearer |
| GET | /api/analytics/student/me | Student Analytics | OAuth2PasswordBearer |
| GET | /api/analytics/surveys | List Surveys | OAuth2PasswordBearer |
| POST | /api/analytics/surveys | Create Survey | OAuth2PasswordBearer |
| GET | /api/analytics/surveys/available | Available Surveys | OAuth2PasswordBearer |
| DELETE | /api/analytics/surveys/{survey_id} | Delete Survey | OAuth2PasswordBearer |
| GET | /api/analytics/surveys/{survey_id}/responses | Survey Responses | OAuth2PasswordBearer |
| POST | /api/analytics/surveys/{survey_id}/responses | Submit Survey Response | OAuth2PasswordBearer |
| GET | /api/archive/me | My Archive | OAuth2PasswordBearer |
| POST | /api/auth/change-password | Change Password | OAuth2PasswordBearer |
| POST | /api/auth/delete-account | Delete My Account | OAuth2PasswordBearer |
| POST | /api/auth/delete-request | Request Account Deletion | OAuth2PasswordBearer |
| GET | /api/auth/export | Export User Data | OAuth2PasswordBearer |
| GET | /api/auth/export-status | Export Status | OAuth2PasswordBearer |
| POST | /api/auth/forgot-password | Forgot Password | public / none |
| POST | /api/auth/forgot-username | Forgot Username | public / none |
| POST | /api/auth/impersonate | Start Impersonation | OAuth2PasswordBearer |
| POST | /api/auth/impersonate/exit | Exit Impersonation | OAuth2PasswordBearer |
| POST | /api/auth/login | Login | public / none |
| POST | /api/auth/logout | Logout | OAuth2PasswordBearer |
| GET | /api/auth/me | Get Current User Info | OAuth2PasswordBearer |
| GET | /api/auth/me/impersonation | Get Impersonation Status | OAuth2PasswordBearer |
| POST | /api/auth/mfa/disable | Disable Mfa | OAuth2PasswordBearer |
| POST | /api/auth/mfa/enroll | Enroll Mfa | OAuth2PasswordBearer |
| POST | /api/auth/mfa/recovery-codes | Generate Recovery Codes | OAuth2PasswordBearer |
| POST | /api/auth/mfa/recovery-codes/verify | Verify Recovery Code | OAuth2PasswordBearer |
| POST | /api/auth/mfa/verify | Verify Mfa | OAuth2PasswordBearer |
| POST | /api/auth/reauth | Reauthenticate | OAuth2PasswordBearer |
| POST | /api/auth/refresh | Refresh Access Token | public / none |
| POST | /api/auth/register | Register | public / none |
| POST | /api/auth/reset-password | Reset Password | public / none |
| GET | /api/auth/sessions | List Sessions | OAuth2PasswordBearer |
| POST | /api/auth/sessions/revoke-all | Revoke All Sessions | OAuth2PasswordBearer |
| DELETE | /api/auth/sessions/{session_id} | Revoke One Session | OAuth2PasswordBearer |
| GET | /api/auth/settings | Get User Settings | OAuth2PasswordBearer |
| PUT | /api/auth/settings | Update User Settings | OAuth2PasswordBearer |
| POST | /api/auth/sso/exchange | Exchange Ticket | public / none |
| POST | /api/auth/sso/ldap/{provider_id}/login | Ldap Login | public / none |
| GET | /api/auth/sso/oidc/{provider_id}/callback | Oidc Callback | public / none |
| GET | /api/auth/sso/oidc/{provider_id}/login | Oidc Login | public / none |
| GET | /api/auth/sso/providers | List Sso Providers | public / none |
| POST | /api/auth/sso/saml/{provider_id}/acs | Saml Acs | public / none |
| GET | /api/auth/sso/saml/{provider_id}/login | Saml Login | public / none |
| GET | /api/auth/survey-consent | Get Survey Consent | OAuth2PasswordBearer |
| POST | /api/auth/survey-consent | Update Survey Consent | OAuth2PasswordBearer |
| GET | /api/auth/wiki-access | Check Wiki Access | OAuth2PasswordBearer |
| GET | /api/auth/wiki-admin-access | Check Wiki Admin Access | OAuth2PasswordBearer |
| DELETE | /api/auth/wiki-cookie | Clear Wiki Cookie | public / none |
| POST | /api/auth/wiki-cookie | Issue Wiki Cookie | OAuth2PasswordBearer |
| GET | /api/auth/wiki-released | Wiki Released Chapters | public / none |
| GET | /api/badges/achievements/{certificate_id} | Achievement Definition | public / none |
| GET | /api/badges/achievements/{certificate_id}/image | Achievement Image | public / none |
| GET | /api/badges/credentials/{jti} | Hosted Credential | public / none |
| GET | /api/badges/credentials/{jti}/jwt | Hosted Credential Jwt | public / none |
| GET | /api/badges/credentials/{jti}/status | Credential Status | public / none |
| POST | /api/badges/events/issue | Issue Event Badge | OAuth2PasswordBearer |
| POST | /api/badges/issue | Issue Badge | OAuth2PasswordBearer |
| GET | /api/badges/issuer | Issuer Profile | public / none |
| GET | /api/badges/issuer/jwks | Issuer Jwks | public / none |
| GET | /api/badges/mine | My Badges | OAuth2PasswordBearer |
| POST | /api/badges/{badge_id}/consent | Badge Consent | OAuth2PasswordBearer |
| POST | /api/capstones/plan | Capstone Plan | OAuth2PasswordBearer |
| GET | /api/capstones/plans | List Capstone Plans | OAuth2PasswordBearer |
| POST | /api/capstones/plans | Save Capstone Plan | OAuth2PasswordBearer |
| GET | /api/capstones/plans/{plan_id} | Get Capstone Plan | OAuth2PasswordBearer |
| PUT | /api/capstones/plans/{plan_id} | Update Capstone Plan | OAuth2PasswordBearer |
| POST | /api/capstones/plans/{plan_id}/approve | Approve Capstone Plan | OAuth2PasswordBearer |
| POST | /api/capstones/plans/{plan_id}/archive | Archive Capstone Plan | OAuth2PasswordBearer |
| GET | /api/capstones/profiles | Capstone Profiles | OAuth2PasswordBearer |
| GET | /api/competencies/{competency_id}/evidence | Competency Evidence | OAuth2PasswordBearer |
| GET | /api/competency-reviews/catalogue | Review Catalogue | OAuth2PasswordBearer |
| GET | /api/competency-reviews/export-ready | Export Ready | OAuth2PasswordBearer |
| GET | /api/competency-reviews/queue | Review Queue | OAuth2PasswordBearer |
| GET | /api/competency-reviews/{lab_slug} | Review Detail | OAuth2PasswordBearer |
| POST | /api/competency-reviews/{lab_slug}/draft | Save Review Draft | OAuth2PasswordBearer |
| POST | /api/competency-reviews/{lab_slug}/sign | Sign Review | OAuth2PasswordBearer |
| POST | /api/competency-reviews/{review_id}/exported | Mark Review Exported | OAuth2PasswordBearer |
| GET | /api/competitions | List Competitions | OAuth2PasswordBearer |
| POST | /api/competitions | Create Competition | OAuth2PasswordBearer |
| GET | /api/competitions/public/{competition_id} | Public Competition | public / none |
| DELETE | /api/competitions/{competition_id} | Delete Competition | OAuth2PasswordBearer |
| GET | /api/competitions/{competition_id} | Get Competition | OAuth2PasswordBearer |
| PATCH | /api/competitions/{competition_id} | Update Competition | OAuth2PasswordBearer |
| POST | /api/competitions/{competition_id}/archive | Archive Competition | OAuth2PasswordBearer |
| GET | /api/competitions/{competition_id}/certificate/{award} | Get Event Certificate | OAuth2PasswordBearer |
| GET | /api/competitions/{competition_id}/certificates | List Event Certificates | OAuth2PasswordBearer |
| GET | /api/competitions/{competition_id}/discovery | Get Event Discovery | OAuth2PasswordBearer |
| GET | /api/competitions/{competition_id}/discovery/overview | Get Event Discovery Overview | OAuth2PasswordBearer |
| POST | /api/competitions/{competition_id}/join | Join Competition | OAuth2PasswordBearer |
| POST | /api/competitions/{competition_id}/leave | Leave Competition | OAuth2PasswordBearer |
| POST | /api/competitions/{competition_id}/unarchive | Unarchive Competition | OAuth2PasswordBearer |
| GET | /api/config/public | Public Config | public / none |
| GET | /api/consent/ | Learner consent and revocation status | OAuth2PasswordBearer |
| POST | /api/consent/admin/enforce-suppressions | Apply the suppression ledger | OAuth2PasswordBearer |
| GET | /api/consent/admin/metrics | Revocation verification metrics | OAuth2PasswordBearer |
| GET | /api/consent/admin/revocations | All revocation workflows | OAuth2PasswordBearer |
| POST | /api/consent/admin/run-jobs | Run due purge and verification jobs | OAuth2PasswordBearer |
| GET | /api/consent/revocations | The learner's own revocation history | OAuth2PasswordBearer |
| GET | /api/consent/types | Available consent types | OAuth2PasswordBearer |
| POST | /api/consent/{consent_type}/grant | Grant Consent | OAuth2PasswordBearer |
| POST | /api/consent/{consent_type}/revoke | Revoke Consent | OAuth2PasswordBearer |
| GET | /api/courses/ | List Courses | OAuth2PasswordBearer |
| POST | /api/courses/ | Create Course | OAuth2PasswordBearer |
| POST | /api/courses/join | Join Course | OAuth2PasswordBearer |
| DELETE | /api/courses/{course_id} | Delete Course | OAuth2PasswordBearer |
| GET | /api/courses/{course_id} | Get Course | OAuth2PasswordBearer |
| PUT | /api/courses/{course_id} | Update Course | OAuth2PasswordBearer |
| GET | /api/courses/{course_id}/achievements | List Achievements | OAuth2PasswordBearer |
| POST | /api/courses/{course_id}/archive | Archive Course | OAuth2PasswordBearer |
| GET | /api/courses/{course_id}/assignments | List Assignments | OAuth2PasswordBearer |
| POST | /api/courses/{course_id}/assignments | Create Assignment | OAuth2PasswordBearer |
| PUT | /api/courses/{course_id}/assignments/reorder | Reorder Assignments | OAuth2PasswordBearer |
| DELETE | /api/courses/{course_id}/assignments/{assignment_id} | Delete Assignment | OAuth2PasswordBearer |
| PUT | /api/courses/{course_id}/assignments/{assignment_id} | Update Assignment | OAuth2PasswordBearer |
| POST | /api/courses/{course_id}/assignments/{assignment_id}/labs | Add Labs To Assignment | OAuth2PasswordBearer |
| DELETE | /api/courses/{course_id}/assignments/{assignment_id}/labs/{lab_id} | Remove Lab From Assignment | OAuth2PasswordBearer |
| GET | /api/courses/{course_id}/assignments/{assignment_id}/report | Assignment Class Report | OAuth2PasswordBearer |
| GET | /api/courses/{course_id}/assignments/{assignment_id}/report/{user_id} | Assignment Student Report | OAuth2PasswordBearer |
| PUT | /api/courses/{course_id}/cohort-settings | Update Cohort Settings | OAuth2PasswordBearer |
| POST | /api/courses/{course_id}/cohorts | Create Cohort | OAuth2PasswordBearer |
| POST | /api/courses/{course_id}/cohorts/sync-default | Sync Default Cohort Members | OAuth2PasswordBearer |
| DELETE | /api/courses/{course_id}/cohorts/{cohort_id} | Delete Cohort | OAuth2PasswordBearer |
| PATCH | /api/courses/{course_id}/cohorts/{cohort_id} | Update Cohort | OAuth2PasswordBearer |
| PUT | /api/courses/{course_id}/cohorts/{cohort_id}/members | Set Cohort Members | OAuth2PasswordBearer |
| POST | /api/courses/{course_id}/enroll-bulk | Enroll Students Bulk | OAuth2PasswordBearer |
| DELETE | /api/courses/{course_id}/enroll/{user_id} | Remove Student | OAuth2PasswordBearer |
| POST | /api/courses/{course_id}/exercise-sets | Create Set | OAuth2PasswordBearer |
| DELETE | /api/courses/{course_id}/exercise-sets/{set_id} | Delete Set | OAuth2PasswordBearer |
| PATCH | /api/courses/{course_id}/exercise-sets/{set_id} | Update Set | OAuth2PasswordBearer |
| PUT | /api/courses/{course_id}/exercise-sets/{set_id}/items | Set Items | OAuth2PasswordBearer |
| POST | /api/courses/{course_id}/feedback | Submit Course Feedback | OAuth2PasswordBearer |
| GET | /api/courses/{course_id}/feedback/me | My Course Feedback | OAuth2PasswordBearer |
| GET | /api/courses/{course_id}/feedback/summary | Course Feedback Summary | OAuth2PasswordBearer |
| POST | /api/courses/{course_id}/labs | Assign Labs | OAuth2PasswordBearer |
| POST | /api/courses/{course_id}/labs/bulk-remove | Remove several exercises from a course | OAuth2PasswordBearer |
| PUT | /api/courses/{course_id}/labs/reorder | Reorder Labs | OAuth2PasswordBearer |
| DELETE | /api/courses/{course_id}/labs/{lab_id} | Remove Lab | OAuth2PasswordBearer |
| PUT | /api/courses/{course_id}/labs/{lab_id} | Update Course Lab | OAuth2PasswordBearer |
| POST | /api/courses/{course_id}/labs/{lab_id}/reset/{user_id} | Reset Student Lab | OAuth2PasswordBearer |
| GET | /api/courses/{course_id}/planning | Get Planning | OAuth2PasswordBearer |
| GET | /api/courses/{course_id}/planning/coverage | Get Coverage | OAuth2PasswordBearer |
| POST | /api/courses/{course_id}/regenerate-invite | Regenerate Invite | OAuth2PasswordBearer |
| GET | /api/courses/{course_id}/report | Class Report | OAuth2PasswordBearer |
| GET | /api/courses/{course_id}/report/{user_id} | Student Report | OAuth2PasswordBearer |
| GET | /api/courses/{course_id}/reports | List Reports | OAuth2PasswordBearer |
| GET | /api/courses/{course_id}/reports/coaching-queue.csv | Coaching Queue Csv | OAuth2PasswordBearer |
| GET | /api/courses/{course_id}/reports/coaching-queue.pdf | Coaching Queue Pdf | OAuth2PasswordBearer |
| GET | /api/courses/{course_id}/reports/course-health.pdf | Course Health Report | OAuth2PasswordBearer |
| GET | /api/courses/{course_id}/reports/exercise-diagnostics.csv | Exercise Diagnostics Csv | OAuth2PasswordBearer |
| GET | /api/courses/{course_id}/reports/exercise-diagnostics.pdf | Exercise Diagnostics Report | OAuth2PasswordBearer |
| POST | /api/courses/{course_id}/requirements | Create Requirement | OAuth2PasswordBearer |
| DELETE | /api/courses/{course_id}/requirements/{requirement_id} | Delete Requirement | OAuth2PasswordBearer |
| PATCH | /api/courses/{course_id}/requirements/{requirement_id} | Update Requirement | OAuth2PasswordBearer |
| GET | /api/courses/{course_id}/reviews | List Course Reviews | OAuth2PasswordBearer |
| GET | /api/courses/{course_id}/scoreboard | Get Scoreboard | OAuth2PasswordBearer |
| GET | /api/courses/{course_id}/staff | List Course Staff | OAuth2PasswordBearer |
| POST | /api/courses/{course_id}/staff | Add Course Staff | OAuth2PasswordBearer |
| GET | /api/courses/{course_id}/staff/candidates | List Course Staff Candidates | OAuth2PasswordBearer |
| DELETE | /api/courses/{course_id}/staff/{staff_id} | Remove Course Staff | OAuth2PasswordBearer |
| GET | /api/courses/{course_id}/students | List Students | OAuth2PasswordBearer |
| DELETE | /api/courses/{course_id}/students/{student_id}/accommodation | Clear Student Accommodation | OAuth2PasswordBearer |
| GET | /api/courses/{course_id}/students/{student_id}/accommodation | Get Student Accommodation | OAuth2PasswordBearer |
| PUT | /api/courses/{course_id}/students/{student_id}/accommodation | Set Student Accommodation | OAuth2PasswordBearer |
| PUT | /api/courses/{course_id}/students/{user_id}/consent | Record Minor Consent | OAuth2PasswordBearer |
| GET | /api/courses/{course_id}/students/{user_id}/history | Course Student History | OAuth2PasswordBearer |
| GET | /api/courses/{course_id}/students/{user_id}/labs/{lab_id}/attempts | Get Student Lab Attempts | OAuth2PasswordBearer |
| POST | /api/courses/{course_id}/toggle-active | Toggle Course Active | OAuth2PasswordBearer |
| POST | /api/courses/{course_id}/unarchive | Unarchive Course | OAuth2PasswordBearer |
| GET | /api/dashboard/celebrations | Celebration Wall | OAuth2PasswordBearer |
| POST | /api/dashboard/celebrations/{achievement_id}/celebrate | Toggle Celebration | OAuth2PasswordBearer |
| GET | /api/dashboard/instructor/feed | Instructor Feed | OAuth2PasswordBearer |
| GET | /api/dashboard/instructor/filter-options | Instructor Filter Options | OAuth2PasswordBearer |
| GET | /api/dashboard/instructor/ics-coverage | Ics Attack Coverage | OAuth2PasswordBearer |
| GET | /api/dashboard/instructor/learning | Instructor Learning | OAuth2PasswordBearer |
| GET | /api/dashboard/instructor/pulse | Instructor Pulse | OAuth2PasswordBearer |
| GET | /api/dashboard/instructor/report | Instructor Report | OAuth2PasswordBearer |
| GET | /api/dashboard/instructor/stats | Instructor Stats | OAuth2PasswordBearer |
| GET | /api/dashboard/student | Student Dashboard | OAuth2PasswordBearer |
| GET | /api/dna/v3/affinity | Cyber DNA career affinity | OAuth2PasswordBearer |
| GET | /api/dna/v3/behavior | Cyber DNA behavior profile | OAuth2PasswordBearer |
| GET | /api/dna/v3/competencies | Cyber DNA competency scores | OAuth2PasswordBearer |
| GET | /api/dna/v3/dna | Cyber DNA learner payload | OAuth2PasswordBearer |
| GET | /api/dna/v3/evidence | Cyber DNA evidence ledger | OAuth2PasswordBearer |
| GET | /api/dna/v3/interest | Cyber DNA interest vector | OAuth2PasswordBearer |
| GET | /api/dna/v3/snapshots | List Cyber DNA snapshots | OAuth2PasswordBearer |
| POST | /api/dna/v3/snapshots | Record a Cyber DNA snapshot | OAuth2PasswordBearer |
| GET | /api/dna/v3/snapshots/{snapshot_id} | Cyber DNA snapshot | OAuth2PasswordBearer |
| GET | /api/evidence | List Evidence | OAuth2PasswordBearer |
| POST | /api/evidence | Create Evidence | OAuth2PasswordBearer |
| GET | /api/evidence/analytics | Evidence Analytics Overview | OAuth2PasswordBearer |
| GET | /api/evidence/appeals/queue | Appeal Queue | OAuth2PasswordBearer |
| POST | /api/evidence/appeals/{appeal_id}/decision | Decide Appeal | OAuth2PasswordBearer |
| GET | /api/evidence/queue | Review Queue | OAuth2PasswordBearer |
| GET | /api/evidence/rubrics | List Evidence Rubrics | OAuth2PasswordBearer |
| GET | /api/evidence/{evidence_id} | Get Evidence | OAuth2PasswordBearer |
| POST | /api/evidence/{evidence_id}/appeal | Appeal Evidence | OAuth2PasswordBearer |
| POST | /api/evidence/{evidence_id}/review | Review Evidence | OAuth2PasswordBearer |
| GET | /api/exercises/labs/{lab_id} | Get Lab Details | OAuth2PasswordBearer |
| GET | /api/exercises/labs/{lab_id}/hint | Get Hint | OAuth2PasswordBearer |
| POST | /api/exercises/labs/{lab_id}/submit-flag | Submit Flag | OAuth2PasswordBearer |
| GET | /api/exercises/labs/{lab_slug}/quiz | Get Exercise Quiz | OAuth2PasswordBearer |
| GET | /api/exercises/labs/{lab_slug}/quiz/attempts | List Exercise Quiz Attempts | OAuth2PasswordBearer |
| POST | /api/exercises/labs/{lab_slug}/quiz/attempts | Start Exercise Quiz | OAuth2PasswordBearer |
| POST | /api/exercises/labs/{lab_slug}/quiz/attempts/{attempt_id}/submit | Submit Exercise Quiz | OAuth2PasswordBearer |
| POST | /api/exercises/labs/{lab_slug}/quiz/feedback | Submit Exercise Quiz Feedback | OAuth2PasswordBearer |
| GET | /api/exercises/progress | Get Progress | OAuth2PasswordBearer |
| GET | /api/exercises/tracks | List Tracks | OAuth2PasswordBearer |
| GET | /api/exercises/tracks/{track_slug} | Get Track | OAuth2PasswordBearer |
| GET | /api/exercises/tracks/{track_slug}/levels/{level_id}/certificate | Get a printable level-completion certificate | OAuth2PasswordBearer |
| GET | /api/exercises/tracks/{track_slug}/levels/{level_id}/certificate.pdf | Download the certificate as a PDF | OAuth2PasswordBearer |
| GET | /api/exercises/tracks/{track_slug}/levels/{level_id}/quiz | Get Level Quiz | OAuth2PasswordBearer |
| GET | /api/exercises/tracks/{track_slug}/levels/{level_id}/quiz/attempts | List Quiz Attempts | OAuth2PasswordBearer |
| POST | /api/exercises/tracks/{track_slug}/levels/{level_id}/quiz/submit | Submit Level Quiz | OAuth2PasswordBearer |
| GET | /api/exercises/verify/certificate/{certificate_id} | Verify Certificate | public / none |
| GET | /api/exercises/workbooks | List Workbooks | OAuth2PasswordBearer |
| GET | /api/governance/audit/dashboard | Audit Dashboard | OAuth2PasswordBearer |
| GET | /api/governance/privacy/dashboard | Privacy Dashboard | OAuth2PasswordBearer |
| GET | /api/identity/providers | List Identity Providers | OAuth2PasswordBearer |
| POST | /api/identity/providers | Create Identity Provider | OAuth2PasswordBearer |
| GET | /api/identity/providers/export | Export Identity Providers | OAuth2PasswordBearer |
| POST | /api/identity/providers/import | Import Identity Providers | OAuth2PasswordBearer |
| DELETE | /api/identity/providers/{provider_id} | Delete Identity Provider | OAuth2PasswordBearer |
| PATCH | /api/identity/providers/{provider_id} | Update Identity Provider | OAuth2PasswordBearer |
| POST | /api/identity/providers/{provider_id}/default | Make Default Identity Provider | OAuth2PasswordBearer |
| POST | /api/identity/providers/{provider_id}/test | Test Identity Provider | OAuth2PasswordBearer |
| GET | /api/impact/catalogue | Impact Catalogue | OAuth2PasswordBearer |
| GET | /api/impact/cohort | Cohort Impact | OAuth2PasswordBearer |
| POST | /api/impact/contributions | Submit Contribution | OAuth2PasswordBearer |
| POST | /api/impact/contributions/{contribution_id}/reject | Reject Contribution | OAuth2PasswordBearer |
| POST | /api/impact/contributions/{contribution_id}/verify | Verify Contribution | OAuth2PasswordBearer |
| GET | /api/impact/me | My Impact | OAuth2PasswordBearer |
| GET | /api/impact/pending | Pending Contributions | OAuth2PasswordBearer |
| POST | /api/impact/stewardship/{learner_id} | Record Stewardship | OAuth2PasswordBearer |
| GET | /api/instructor/courses | List My Courses | OAuth2PasswordBearer |
| GET | /api/instructor/courses/{course_id} | Get My Course | OAuth2PasswordBearer |
| GET | /api/instructor/courses/{course_id}/enrollable-users | List Enrollable Users | OAuth2PasswordBearer |
| POST | /api/instructor/exercise-test | Run Exercise Test | OAuth2PasswordBearer |
| GET | /api/instructor/exercise-test/active | Get Active Test Run | OAuth2PasswordBearer |
| POST | /api/instructor/exercise-test/cancel | Cancel Exercise Test | OAuth2PasswordBearer |
| GET | /api/instructor/exercise-test/events/{run_id} | Get Test Events | OAuth2PasswordBearer |
| GET | /api/instructor/exercise-test/labs | List Testable Labs | OAuth2PasswordBearer |
| POST | /api/instructor/exercise-test/report | Generate Exercise Test Report | OAuth2PasswordBearer |
| DELETE | /api/instructor/exercise-test/results | Clear All Exercise Test Results | OAuth2PasswordBearer |
| GET | /api/instructor/exercise-test/results | Get Exercise Test Results | OAuth2PasswordBearer |
| DELETE | /api/instructor/exercise-test/results/{lab_slug} | Delete Exercise Test Result | OAuth2PasswordBearer |
| GET | /api/instructor/labs | List Available Labs | OAuth2PasswordBearer |
| GET | /api/instructor/labs/assignments | Lab Course Assignments | OAuth2PasswordBearer |
| POST | /api/instructor/labs/upload | Upload Lab Zip | OAuth2PasswordBearer |
| DELETE | /api/instructor/labs/{lab_id} | Delete Own Lab | OAuth2PasswordBearer |
| PUT | /api/instructor/labs/{lab_id} | Update Own Lab | OAuth2PasswordBearer |
| GET | /api/instructor/labs/{lab_id}/export | Export Own Lab | OAuth2PasswordBearer |
| GET | /api/instructor/labs/{lab_id}/flag | Reveal Lab Flag | OAuth2PasswordBearer |
| PUT | /api/instructor/labs/{lab_id}/visibility | Update Lab Visibility | OAuth2PasswordBearer |
| GET | /api/instructor/overview | Instructor Overview | OAuth2PasswordBearer |
| GET | /api/instructor/stats | Instructor Stats | OAuth2PasswordBearer |
| GET | /api/instructor/tracks-and-levels | List Tracks And Levels | OAuth2PasswordBearer |
| GET | /api/journeys | List Journeys | OAuth2PasswordBearer |
| GET | /api/journeys/mine | My Journey | OAuth2PasswordBearer |
| PUT | /api/journeys/mine | Choose Journey | OAuth2PasswordBearer |
| GET | /api/labs/ | Get Labs | OAuth2PasswordBearer |
| GET | /api/labs/active | Get Active Lab | OAuth2PasswordBearer |
| POST | /api/labs/extend | Extend Lab Session | OAuth2PasswordBearer |
| POST | /api/labs/pause | Pause Lab Session | OAuth2PasswordBearer |
| GET | /api/labs/prebuild-status | Prebuild Status | OAuth2PasswordBearer |
| POST | /api/labs/resume | Resume Lab Session | OAuth2PasswordBearer |
| GET | /api/labs/spawn-status/{session_id} | Get Spawn Status | OAuth2PasswordBearer |
| POST | /api/labs/spawn/{lab_slug} | Spawn Lab | OAuth2PasswordBearer |
| POST | /api/labs/stop | Stop Lab | OAuth2PasswordBearer |
| GET | /api/labs/vpn-config | Get Vpn Config | OAuth2PasswordBearer |
| GET | /api/labs/vpn-config/qr | Get Vpn Config Qr | OAuth2PasswordBearer |
| GET | /api/labs/vpn-status | Get Vpn Status | OAuth2PasswordBearer |
| GET | /api/lti/admin/links | List Links | OAuth2PasswordBearer |
| POST | /api/lti/admin/links/{link_id}/lineitem | Create Link Lineitem | OAuth2PasswordBearer |
| GET | /api/lti/admin/links/{link_id}/results | Get Link Results | OAuth2PasswordBearer |
| GET | /api/lti/admin/links/{link_id}/roster | Get Link Roster | OAuth2PasswordBearer |
| GET | /api/lti/admin/links/{link_id}/roster/saved | Get Saved Roster | OAuth2PasswordBearer |
| POST | /api/lti/admin/links/{link_id}/score | Post Link Score | OAuth2PasswordBearer |
| GET | /api/lti/admin/links/{link_id}/scores | List Link Scores | OAuth2PasswordBearer |
| POST | /api/lti/admin/links/{link_id}/sync-roster | Sync Link Roster | OAuth2PasswordBearer |
| GET | /api/lti/admin/platforms | List Platforms | OAuth2PasswordBearer |
| POST | /api/lti/admin/platforms | Create Platform | OAuth2PasswordBearer |
| DELETE | /api/lti/admin/platforms/{platform_id} | Delete Platform | OAuth2PasswordBearer |
| PATCH | /api/lti/admin/platforms/{platform_id} | Update Platform | OAuth2PasswordBearer |
| POST | /api/lti/admin/platforms/{platform_id}/test | Test Platform | OAuth2PasswordBearer |
| GET | /api/lti/deep-link/{session_token} | Deep Link Info | OAuth2PasswordBearer |
| POST | /api/lti/deep-link/{session_token}/response | Deep Link Response | OAuth2PasswordBearer |
| GET | /api/lti/jwks | Tool Jwks | public / none |
| POST | /api/lti/launch | Lti Launch | public / none |
| GET | /api/lti/login | Lti Login Get | public / none |
| POST | /api/lti/login | Lti Login Post | public / none |
| GET | /api/modules/ | Get Modules Status | OAuth2PasswordBearer |
| GET | /api/nice/components | Nice Components | OAuth2PasswordBearer |
| GET | /api/nice/coverage | Nice Coverage | OAuth2PasswordBearer |
| POST | /api/nice/labs/seed | Seed Nice Lab Mappings | OAuth2PasswordBearer |
| GET | /api/nice/labs/{lab_id} | Get Lab Nice Mappings | OAuth2PasswordBearer |
| PUT | /api/nice/labs/{lab_id} | Set Lab Nice Mappings | OAuth2PasswordBearer |
| POST | /api/nice/labs/{lab_id}/review | Review Lab Nice Mappings | OAuth2PasswordBearer |
| POST | /api/nice/refresh | Refresh Nice Framework | OAuth2PasswordBearer |
| GET | /api/nice/status | Nice Status | OAuth2PasswordBearer |
| GET | /api/practice/pathways | Practice Pathways | OAuth2PasswordBearer |
| GET | /api/practice/progress | Practice Progress | OAuth2PasswordBearer |
| GET | /api/practice/sessions | Practice History | OAuth2PasswordBearer |
| POST | /api/practice/sessions | Start Session | OAuth2PasswordBearer |
| GET | /api/practice/sessions/{session_id} | Get Session | OAuth2PasswordBearer |
| POST | /api/practice/sessions/{session_id}/submit | Submit Session | OAuth2PasswordBearer |
| GET | /api/profile/career-assessment | Short career-direction questions | OAuth2PasswordBearer |
| POST | /api/profile/career-assessment | Score a short career-direction check | OAuth2PasswordBearer |
| GET | /api/profile/career-dossier | Career-profile dossier (JSON) | OAuth2PasswordBearer |
| GET | /api/profile/career-dossier.html | Career-profile dossier (HTML) | OAuth2PasswordBearer |
| GET | /api/profile/career-dossier.md | Career-profile dossier (Markdown) | OAuth2PasswordBearer |
| GET | /api/profile/competencies | Learner competency assessment profile | OAuth2PasswordBearer |
| POST | /api/profile/gps | Optional cybersecurity GPS direction finder | OAuth2PasswordBearer |
| GET | /api/profile/portfolio | Professional portfolio (JSON) | OAuth2PasswordBearer |
| GET | /api/profile/portfolio.html | Professional portfolio (printable HTML) | OAuth2PasswordBearer |
| GET | /api/profile/portfolio.md | Professional portfolio (Markdown) | OAuth2PasswordBearer |
| GET | /api/profile/role-readiness | Role readiness answer | OAuth2PasswordBearer |
| GET | /api/profile/roles | Career pathway catalogue | OAuth2PasswordBearer |
| GET | /api/profile/shares | List portfolio share links | OAuth2PasswordBearer |
| POST | /api/profile/shares | Create a portfolio share link | OAuth2PasswordBearer |
| DELETE | /api/profile/shares/{share_id} | Revoke a portfolio share link | OAuth2PasswordBearer |
| GET | /api/profile/skill-dna | Learner Skill DNA character sheet | OAuth2PasswordBearer |
| GET | /api/profile/snapshots | Stored report snapshots | OAuth2PasswordBearer |
| GET | /api/profile/snapshots/{snapshot_id} | Stored report snapshot | OAuth2PasswordBearer |
| GET | /api/profile/snapshots/{snapshot_id}/html | Stored report (HTML) | OAuth2PasswordBearer |
| GET | /api/profile/snapshots/{snapshot_id}/markdown | Stored report (Markdown) | OAuth2PasswordBearer |
| GET | /api/profile/summary | Profile snapshot with certificates and completions | OAuth2PasswordBearer |
| PUT | /api/profile/title | Equip an unlocked achievement title | OAuth2PasswordBearer |
| GET | /api/profile/transcript.pdf | Download a printable completion transcript | OAuth2PasswordBearer |
| GET | /api/public/community-events | Community Events | public / none |
| GET | /api/public/portfolio/{token} | Read a shared portfolio | OAuth2PasswordBearer |
| GET | /api/public/qr/{source} | Qr Landing | public / none |
| GET | /api/rangebox/capacity | Rangebox Capacity | OAuth2PasswordBearer |
| DELETE | /api/rangebox/standalone/destroy | Standalone Rangebox Destroy | OAuth2PasswordBearer |
| POST | /api/rangebox/standalone/launch | Standalone Rangebox Launch | OAuth2PasswordBearer |
| GET | /api/rangebox/standalone/status | Standalone Rangebox Status | OAuth2PasswordBearer |
| GET | /api/rangebox/transport | Rangebox Transport | OAuth2PasswordBearer |
| POST | /api/rangebox/ws-ticket | Get Ws Ticket | OAuth2PasswordBearer |
| GET | /api/rangebox/{session_id}/lab | Rangebox Lab | OAuth2PasswordBearer |
| GET | /api/rangebox/{session_id}/status | Rangebox Status | OAuth2PasswordBearer |
| GET | /api/ransomware-activity | Get Ransomware Activity | OAuth2PasswordBearer |
| POST | /api/recognition/evaluate | Evaluate Recognition | OAuth2PasswordBearer |
| GET | /api/recognition/me | My Recognition | OAuth2PasswordBearer |
| POST | /api/recognition/seen | Mark Seen | OAuth2PasswordBearer |
| POST | /api/recognition/{learner_id}/award | Manual Award | OAuth2PasswordBearer |
| POST | /api/reports/verify | Verify Report File | public / none |
| POST | /api/reviews | Request Review | OAuth2PasswordBearer |
| GET | /api/reviews/mine | List My Reviews | OAuth2PasswordBearer |
| PUT | /api/reviews/{review_id}/decision | Decide Review | OAuth2PasswordBearer |
| GET | /api/settings/ | Get All Settings | OAuth2PasswordBearer |
| PUT | /api/settings/ | Update Settings | OAuth2PasswordBearer |
| GET | /api/settings/achievement-catalogue | Grouped achievement catalogue for the studio | OAuth2PasswordBearer |
| GET | /api/settings/change-requests | List Change Requests | OAuth2PasswordBearer |
| POST | /api/settings/change-requests/{change_id}/revert | Revert Change Request | OAuth2PasswordBearer |
| GET | /api/settings/custom-achievements | List custom achievements | OAuth2PasswordBearer |
| POST | /api/settings/custom-achievements | Create a custom achievement | OAuth2PasswordBearer |
| DELETE | /api/settings/custom-achievements/{achievement_id} | Delete a custom achievement | OAuth2PasswordBearer |
| PUT | /api/settings/custom-achievements/{achievement_id} | Update a custom achievement | OAuth2PasswordBearer |
| POST | /api/settings/mail/test | Send Mail Test | OAuth2PasswordBearer |
| POST | /api/settings/production/cutover | Production Cutover | OAuth2PasswordBearer |
| GET | /api/settings/production/preview | Production Preview | OAuth2PasswordBearer |
| GET | /api/settings/{category} | Get Settings By Category | OAuth2PasswordBearer |
| POST | /api/setup/complete | Complete Setup | public / none |
| GET | /api/setup/config | Public Config | public / none |
| GET | /api/setup/status | Setup Status | public / none |
| GET | /api/threat-awareness | Get Threat Awareness | OAuth2PasswordBearer |
| GET | /api/usage/admin | Admin Usage | OAuth2PasswordBearer |
| GET | /api/usage/admin.csv | Admin Usage Csv | OAuth2PasswordBearer |
| GET | /api/usage/admin/qr | Admin Qr Png | OAuth2PasswordBearer |
| GET | /api/usage/public | Public Usage | public / none |
| GET | /api/usage/public.csv | Public Usage Csv | public / none |
| GET | /api/version | Api Version | public / none |
| GET | /api/workbook-answers | List My Answers | OAuth2PasswordBearer |
| GET | /api/workbook-answers/options | Answer Options | OAuth2PasswordBearer |
| GET | /api/workbook-answers/{lab_slug} | Get My Answer | OAuth2PasswordBearer |
| PUT | /api/workbook-answers/{lab_slug} | Save My Answer | OAuth2PasswordBearer |
| GET | /health | Health | public / none |
