# Learner catalogue (frontend)

## Purpose

Show a learner what they can do next: their dashboard, the public catalogue,
track pages, course pages, and competitions. Visibility and ordering are decided
by the backend; the SPA renders the response.

## Routes and views

| Route | View | Notes |
|---|---|---|
| `/dashboard` | `DashboardRouter.vue` → `StudentDashboard.vue` | role-aware landing |
| `/discover` | `Discover.vue` | catalogue discovery |
| `/exercises` | `Exercises.vue` | exercise catalogue and focus filter |
| `/exercises/:trackSlug` | `TrackDetail.vue` | track chapters and labs |
| `/courses` | `CourseList.vue` | learner courses |
| `/courses/:id` | `Course.vue` | course detail and assignments |
| `/competitions` | `Competitions.vue` | event catalogue |
| `/competitions/:id` | `CompetitionDetail.vue` | event detail |

## API calls

| Data | Endpoint |
|---|---|
| Tracks and labs | `GET /api/exercises/tracks`, `GET /api/exercises/tracks/{slug}` |
| Progress | `GET /api/exercises/progress` |
| Courses | `GET /api/courses/`, `GET /api/courses/{id}` |
| Dashboard | `GET /api/dashboard/*` |
| Competitions | `GET /api/competitions/*` |
| Focus filter | server-side query parameter, URL-backed |

## Behaviour that matters

- **Server-side visibility.** The client never filters a hidden lab into view.
- **Focus is URL-backed.** `?focus=...` is shareable and reload-safe.
- **Course scope.** A course lab appears only when assigned and enrolled.
- **No global ranking.** Course scoreboards are scoped and opt-in.
- **Empty states.** A learner with no course sees the public catalogue, not an
  error.
- **Mobile shell.** The same routes render in the compact layout.

## Storage

No catalogue data is persisted in the browser. Filters and focus live in the URL
or component state. `useCareerGoal` stores a career goal in `localStorage` for
the profile and catalogue focus.

## Run and test

```bash
cd platform/frontend
npm run dev
npm test
npm run lint
```

Backend coverage: `tests/test_lab_visibility.py`,
`tests/test_course_progress_focus.py`, `tests/test_public_config_api.py`.

## Extension checklist

- Add the route and the navigation entry.
- Fetch through `src/api/axios.js`.
- Add a loading, empty, and error state.
- Keep the focus filter server-side and after visibility checks.
- Add a mobile layout check.
- Do not compute a permission or a score in the component.

## Related

- [Backend courses](../../../backend/features/courses/README.md)
- [Backend labs](../../../backend/features/labs-and-sessions/README.md)
- [Frontend overview](../../subsystem-overview.md)
