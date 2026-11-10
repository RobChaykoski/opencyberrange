# About area

The in-app About page is the audit-friendly view of what this installation is
made of. It is deliberately split from the public version endpoint:

| Surface | Audience | Contents |
|---|---|---|
| `GET /api/version` | Public | Release name and version only |
| `/about` | Public | Simple first-visit About page: what the platform is, who it is for, access, privacy/security summary, links to register, sign in, and certificate verification |
| `/about/installation` | All authenticated users | Release, platform summary, branding, project licence, component inventory, licence documents, SBOM downloads |
| `/api/about` | All authenticated users | The installation inventory as JSON, with `Cache-Control: no-store` |

The public `/about` page is linked from the login and registration pages and is
safe to share before sign-in. The installation page is linked from the global
footer and does not expose secrets, student data, or database contents. It does
expose exact dependency versions and SBOMs; those are already part of the source
release, and access requires a signed-in account.

## What it shows

- **Build and runtime** — release, commit, build date, schema revision, backend
  and frontend image digests, Python, Node, PostgreSQL, Redis, edition, and the
  runtime check timestamp.
- **Platform summary** — release, edition, Python, Node, PostgreSQL, Redis.
- **Content and integrity** — lab, track, and level counts plus the append-only
  ledger summary.
- **Branding** — the SWOCTS name/logo are owned by SWOCTS and were created and
  designed by Avery Chaykoski. The OpenCyberRange attribution remains.
- **Project licence** — PolyForm Noncommercial 1.0.0.
- **Components** — direct backend and frontend dependencies, container images,
  and lab toolchains with their licence families.
- **Licence documents** — `LICENSE`, `NOTICE`, `LICENSING.md`, `BRANDING.md`,
  `BUILD_NOTICE.md`, `THIRD_PARTY_NOTICES.md`, and every text in
  `THIRD_PARTY_LICENSES/`.
- **SBOMs** — CycloneDX files with size and SHA-256 checksums.
- **Copy diagnostics** — a redacted JSON summary for support. It contains no
  secrets, usernames, hostnames, database DSNs, container IDs, or paths.

Privacy controls are documented in [`BUILD_NOTICE.md`](../BUILD_NOTICE.md) and
are managed from **Admin > Settings > Security**, not on the About page.

## Data sources and generation

The page reads `platform/backend/app/data/about/about.json`, which is generated
from the release manifests by `scripts/generate-about.py`:

- `versions.yaml` for platform and runtime versions;
- `platform/backend/requirements.txt` for backend components;
- `platform/frontend/package.json` and `package-lock.json` for frontend
  components and licence identifiers;
- `THIRD_PARTY_NOTICES.md` and `THIRD_PARTY_LICENSES/` for the notice inventory;
- `BRANDING.md` for the SWOCTS/OpenCyberRange attribution.

`GET /api/about` overlays live values on that inventory:

- `APP_VERSION` and the release name;
- the running Python version;
- PostgreSQL `server_version` and the Alembic schema revision;
- the live edition profile;
- lab, track, and level counts;
- the append-only ledger summary;
- backend and frontend image IDs when the Docker socket is available.

Build identity comes from `app/data/about/build.json`, which the generator writes
with the release, git revision, build timestamp, and pinned runtime versions.
`OCR_BUILD_REVISION` overrides the recorded git revision at container runtime.

The generator copies the licence documents into `app/data/about/licenses/` and
writes `sbom/manifest.json` with the SBOM sizes and hashes. It does not create
the SBOM JSON files; those are generated with the commands in
`platform/backend/app/data/about/README.md`.

## Access and safety

- `/api/about` and its file endpoints require a signed-in user.
- The public `/about` page is static and has no API dependency.
- `/api/about` sets `Cache-Control: no-store` so a browser or intermediary
  cannot keep an older release version after a deployment.
- File names are allowlisted by exact basename; path traversal is rejected.
- No database writes and no student data are involved.
- The pages use the existing theme tokens and responsive layout, so they work in
  dark/light mode and on mobile.

## Update checklist

1. Change the dependency, image, or licence inventory.
2. Regenerate the frontend SBOM if frontend dependencies changed.
3. Regenerate the backend SBOM if backend dependencies changed.
4. Run `python scripts/generate-about.py`.
5. Run `python scripts/check-licences.py`.
6. Build the frontend and review `/about` in both themes and at ~390 px.
