# Frontend subsystem

The frontend is a Vue 3 single-page application built by Vite and served by
nginx. It owns the learner, instructor, and admin experience; it does not own
authorization or business rules. Every decision that matters is enforced by the
backend.

## Folder map

```text
platform/frontend/
├── src/
│   ├── main.js              app bootstrap
│   ├── App.vue              root shell
│   ├── router/index.js      routes and guards
│   ├── api/axios.js         Axios instance, token refresh, 401 handling
│   ├── views/               route-level pages
│   ├── components/          reusable UI, charts, panels, dialogs
│   ├── composables/         shared state and browser APIs
│   ├── directives/          UI directives
│   ├── utils/               formatting and helpers
│   ├── data/                static client data
│   └── test/                Vitest setup
├── public/
├── nginx-ssl.conf           nginx edge configuration
├── vite.config.js           dev server proxy and build output
├── package.json
└── Dockerfile               Node build + nginx runtime
```

## Frameworks and purpose

| Library | Used for |
|---|---|
| Vue 3 | component model and reactivity |
| Vue Router 5 | route table, guards, deep links |
| Vite 8 | dev server, HMR, production build |
| Axios | API client, interceptors, refresh |
| ECharts 6 | analytics and dashboard charts |
| marked + DOMPurify | Markdown rendering, sanitised |
| noVNC | RangeBox desktop in the browser |
| SortableJS | drag-and-drop ordering |
| Vitest + jsdom | unit tests |

## Runtime shape

- nginx serves the built SPA and proxies `/api` to the backend.
- `/wiki` is served from `wiki_data`, read-only.
- The app uses history-mode routing; nginx must fall back to `index.html`.
- A separate 8443 origin can serve the workbook with its own CSP and cookie
  scope.
- The mobile shell switches layout at phone widths; the same routes are used.

## Browser storage

| Store | Key | Purpose |
|---|---|---|
| `localStorage` | `token` | access token for the Axios interceptor |
| `localStorage` | `refresh_token` | rotating refresh token |
| `localStorage` | `user` | cached display identity |
| `sessionStorage` | `ocr_impersonating` | impersonation mode flag |
| `sessionStorage` | `ocr_original_session` | token to restore on exit |
| `sessionStorage` | `ocr_imp_meta` | impersonation metadata |
| `localStorage` | career goal / celebration effect | UI preferences |
| HttpOnly cookie | `wiki_session` | scoped wiki access |
| `localStorage`/`sessionStorage` | feature-specific keys | see the feature page |

Tokens in `localStorage` are readable by JavaScript. The backend mitigates this
with short access-token lifetimes, refresh rotation, revocation, CSP, and strict
output encoding. Do not add a new place to persist a token.

## Run

```bash
cd platform/frontend
npm ci
npm run dev
```

Vite proxies `/api` to `http://backend:8000`, which resolves inside Compose. For
host-only development, change the proxy target to `http://127.0.0.1:8000` or use
the Compose dev service. The supported path is Compose.

Production build:

```bash
npm run build
```

The frontend image builds with Node 22 and serves with the pinned nginx image.

## Test

```bash
cd platform/frontend
npm run lint
npm test
npm run build
```

## Feature pages

Start at [frontend features](features/README.md).

## Rules

- Never trust a role, tenant, score, or visibility value from the client.
- Sanitize Markdown with DOMPurify before rendering.
- Never put a learner row or token in a URL query string.
- Keep the mobile shell and the desktop layout on the same data contracts.
- Add a Vitest test for a new composable or a non-trivial component.
- Update the route table and the guards together.
- Respect the CSP; no inline script without the hash process.

## Related

- [Frontend architecture diagram](subsystem-technical-architecture-diagram.md)
- [Backend](../backend/subsystem-overview.md)
- [Wiki](../wiki/subsystem-overview.md)
- [MkDocs governance](../../docs/MKDOCS-GOVERNANCE.md)
- [Accessibility](../../docs/ACCESSIBILITY.md)
