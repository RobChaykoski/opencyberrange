# About inventory

This directory is copied into the backend image and served by the authenticated
`/api/about` endpoints.

- `about.json` — generated component, licence, branding, and SBOM inventory.
- `build.json` — generated build identity: release, git revision, build time, and
  pinned runtime versions.
- `licenses/` — copies of the project and third-party licence documents.
- `sbom/` — CycloneDX SBOMs and their checksum manifest.

Do not edit these files by hand. Regenerate them with:

```bash
python scripts/generate-about.py
```

The SBOM JSON files are generated separately:

```bash
# Frontend (run from platform/frontend)
npm sbom --sbom-format cyclonedx --omit dev \
  > ../backend/app/data/about/sbom/frontend.cdx.json

# Backend (inside the backend image, or a clean venv built from
# platform/backend/requirements.txt)
pip install cyclonedx-bom
cyclonedx-py environment -o backend.cdx.json
```

Then run `python scripts/generate-about.py` again to refresh `about.json` and
`sbom/manifest.json`. See [`docs/ABOUT-AREA.md`](../../../../../docs/ABOUT-AREA.md)
for the page design and access rules.
