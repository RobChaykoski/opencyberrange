# Courses

## Purpose

Group learners into a cohort, assign exercises in a deliberate order, give the
instructor scoped access, and retain or archive the cohort according to policy.

## Code map

| Concern | Location |
|---|---|
| Router | `platform/backend/app/routers/courses.py` |
| Instructor surfaces | `platform/backend/app/routers/instructor.py` |
| Curriculum admin | `platform/backend/app/routers/curriculum_admin.py` |
| Planning | `platform/backend/app/services/course_planning.py` |
| Course wiki | `platform/backend/app/services/course_wiki.py` |
| Model | `platform/backend/app/models/course.py` |

## API surface

| Method | Path | Notes |
|---|---|---|
| POST | `/api/courses/` | create a course; instructor scope required |
| GET | `/api/courses/` | courses visible to the caller |
| GET | `/api/courses/{id}` | course detail, assignments, staff |
| PUT/DELETE | `/api/courses/{id}` | update or delete |
| POST | `/api/courses/join` | learner joins with an invite code |
| POST | `/api/courses/{id}/enroll-bulk` | instructor enrols a list |
| DELETE | `/api/courses/{id}/enroll/{user_id}` | remove an enrolment |
| GET | `/api/courses/{id}/students` | roster |
| POST | `/api/courses/{id}/labs` | assign an exercise |
| PUT | `/api/courses/{id}/labs/reorder` | change order |
| DELETE | `/api/courses/{id}/labs/{lab_id}` | remove an assignment |
| POST | `/api/courses/{id}/archive` | archive a cohort |
| POST | `/api/courses/{id}/toggle-active` | activate or pause |
| POST | `/api/courses/{id}/feedback` | course feedback |
| GET | `/api/courses/{id}/scoreboard` | course-scoped scoreboard |
| GET/PUT | `/api/admin/courses/{id}/retention` | retention policy |
| POST | `/api/admin/courses/{id}/retention/preview` | preview deletion |

## Behaviour that matters

- **Course scope.** An instructor sees only their courses or their institution,
  never another instructor's cohort.
- **Assignments are ordered.** The catalogue shows the course order, not just
  the global track order.
- **Visibility.** A course-scoped lab is hidden until the learner is enrolled
  and the lab is assigned.
- **Invite codes.** Joining is explicit; a code can be regenerated.
- **Retention.** Completion data follows the course retention workflow, not a
  manual SQL delete.
- **Archive, do not delete, by default.** Archiving preserves evidence.

## Persistent state

| Store | Data |
|---|---|
| `courses` | name, code, semester, instructor, invite code, dates, active/archived |
| `course_enrollments` | learner, course, consent, enrolled_at |
| `course_lab_assignments` | lab order and settings |
| `course_staff` | teaching assistants and co-instructors |
| `course_feedback` | learner check-ins and instructor notes |
| `course_completion_resets` | reset history |
| `lab_completions` | learner progress, scoped by course checks |

## Fixtures and tests

- `seed_example_course.py` creates the example course shell.
- `seed_demo_class.py` creates a demo course with students (development only).
- Focused tests:

```bash
cd platform/backend
python -m pytest tests/test_course_progress_focus.py tests/test_course_feedback.py \
  tests/test_tenant_rls.py tests/test_course_progress_focus.py -q
```

## Extension checklist

- Enforce course ownership in a dependency or a service helper.
- Add the field to the model and the response schema.
- Add a test for the owner, a non-owner instructor, and a learner in another
  tenant.
- Update the course wiki if the navigation changes.
- Do not widen catalogue visibility before the course check.

## Related

- [Labs and sessions](../labs-and-sessions/README.md)
- [Analytics and reports](../analytics-and-reports/README.md)
- [Tenant isolation status](../../../../docs/TENANT-ISOLATION-STATUS.md)
- [Retention policies](../../../../docs/RETENTION-POLICIES.md)
