# About area

The in-app About page is the audit-friendly view of what this installation is
made of. It is deliberately split from the public version endpoint:

| Surface | Audience | Contents |
|---|---|---|
| `GET /api/version` | Public | Release name and version only |
| `/about` (signed-in) | All authenticated users | Release, platform summary, branding, project licence, component inventory, licence documents, SBOM downloads |
| `/api/about` (signed-in) | All authenticated users | The same inventory as JSON |

The page is linked from the global footer. It does not expose secrets, student
data, or database contents. It does expose exact dependency versions and SBOMs;
those are already part of the source release, and access requires a signed-in
account.

## What it shows

- **Platform summary** — release, edition, Python, Node, PostgreSQL, Redis.
- **Branding** — the SWOCTS name/logo are owned by SWOCTS and were created and
  designed by Avery Chaykoski. The OpenCyberRange attribution remains.
- **Project licence** — PolyForm Noncommercial 1.0.0.
- **Components** — direct backend and frontend dependencies, container images,
  and lab toolchains with their licence families.
- **Licence documents** — `LICENSE`, `NOTICE`, `LICENSING.md`, `BRANDING.md`,
  `BUILD_NOTICE.md`, `THIRD_PARTY_NOTICES.md`, and every text in
  `THIRD_PARTY_LICENSES/`.
- **SBOMs** — CycloneDX files with size and SHA-256 checksums.

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

The generator copies the licence documents into `app/data/about/licenses/` and
writes `sbom/manifest.json` with the SBOM sizes and hashes. It does not create
the SBOM JSON files; those are generated with the commands in
`platform/backend/app/data/about/README.md`.

## Access and safety

- `/api/about` and its file endpoints require a signed-in user.
- File names are allowlisted by exact basename; path traversal is rejected.
- No database writes and no student data are involved.
- The page uses the existing theme tokens and responsive layout, so it works in
  dark/light mode and on mobile.

## Update checklist

1. Change the dependency, image, or licence inventory.
2. Regenerate the frontend SBOM if frontend dependencies changed.
3. Regenerate the backend SBOM if backend dependencies changed.
4. Run `python scripts/generate-about.py`.
5. Run `python scripts/check-licences.py`.
6. Build the frontend and review `/about` in both themes and at ~390 px.
