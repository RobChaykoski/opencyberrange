# Frontend features

| Feature | What it covers |
|---|---|
| [Auth and session](auth-and-session/README.md) | Login, registration, SSO callback, refresh, impersonation |
| [Learner catalogue](learner-catalogue/README.md) | Dashboard, discover, exercises, courses, tracks |
| [Lab workspace](lab-workspace/README.md) | Briefing, flag submission, RangeBox, noVNC |
| [Instructor and admin](instructor-and-admin/README.md) | Admin console, instructor dashboard, analytics, reports |
| [Profile and evidence](profile-and-evidence/README.md) | Profile, evidence, certificates, celebrations |
| [Wiki and workbook](wiki-and-workbook/README.md) | Workbook landing, answers, wiki origin, cookies |
| [Setup and onboarding](setup-and-onboarding/README.md) | First-run wizard, privacy pages, usage |

Each page lists the routes, views, API calls, storage, run/test steps, and
extension points.

## Adding a frontend feature

1. Add the view under `src/views/`.
2. Add the route and guard in `src/router/index.js`.
3. Put reusable UI in `src/components/`.
4. Put shared state or browser APIs in `src/composables/`.
5. Call the API through `src/api/axios.js`.
6. Add a Vitest test for the composable or the interaction.
7. Run `npm run lint && npm test && npm run build`.
