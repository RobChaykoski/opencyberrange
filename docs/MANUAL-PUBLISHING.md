# Manual publishing

Status: **the publishing gap is closed with a checked, versioned artifact.**
CI already builds every MkDocs site on every change; this page records where the
built manual goes and how to publish it without exposing authenticated content.

## Decision: manual-only static artifact

The publish target is a **checksummed build artifact**, not a public web host.

- The **user manual** (`mkdocs-manual-lite.yml`) is the only site published by
  default. It is the documentation that had no delivery step.
- **Workbook and course sites are not published.** They are served by the
  platform behind `auth_request` and the workbook release gate. A static mirror
  would bypass that gate and expose every chapter, including future course
  material.
- **GitHub Pages is intentionally not used.** Pages cannot enforce the workbook
  auth model, cannot set the platform CSP or `X-Robots-Tag` headers, and would
  publish an unauthenticated mirror of instructor and deployment guidance.

The artifact is suitable for a release download, an internal web root, or a
documentation host that already has its own access control.

## Running the workflow

`.github/workflows/docs-publish.yml` runs:

- automatically on any `v*` tag, publishing the manual;
- manually with **Actions → Publish documentation → Run workflow**.

The `scope` input is either:

| Scope | Builds | Use |
|---|---|---|
| `manual` (default) | `mkdocs-manual-lite.yml` into `reference/manual/` | Release or internal publishing |
| `all` | every `mkdocs-*.yml` into one directory per config | Inspection only; not for public hosting |

Each run produces:

- `docs-<scope>-<commit>.tar.gz` — the built tree;
- `SHA256SUMS` — one line per built file;
- `manifest.json` — commit, ref, tool versions, site list, file/byte counts, and
  the SHA-256 of the tarball.

Verify before publishing:

```bash
sha256sum -c SHA256SUMS
sha256sum docs-manual-<commit>.tar.gz   # compare with manifest.json
tar -tzf docs-manual-<commit>.tar.gz | head
```

## Publishing to an internal web root

The manual is self-contained: `font: false`, vendored JavaScript/CSS, relative
links, and no canonical URL. It works under any directory prefix.

```bash
tar -xzf docs-manual-<commit>.tar.gz -C /tmp/manual
sudo rsync -a --delete /tmp/manual/ /srv/ocr-manual/
```

Serve it from a static host or an nginx location that keeps the platform
controls:

```nginx
location /manual/ {
    alias /srv/ocr-manual/;
    add_header X-Content-Type-Options nosniff always;
    add_header X-Robots-Tag "noindex, nofollow, noarchive, nosnippet" always;
    # Keep the manual behind the same session gate as the wiki if it is not
    # intended for the public internet.
    auth_request /_wiki_auth;
}
```

Do not place the manual inside `/usr/share/nginx/wiki/` or the `wiki_data`
volume: the wiki builder replaces that tree on every publish.

## Built-output gate

`scripts/check-built-docs.py` runs before packaging and fails on:

- a missing `index.html` or `search/search_index.json`;
- root-absolute `href="/..."` or `src="/..."` references outside the optional
  `404.html` (which the host normally supplies);
- a non-empty `course/` directory, which would be runtime learner content.

## Regenerating screenshots

The manual screenshots are generated with a demo account, not live learner
data. See [`MANUAL-SCREENSHOTS.md`](MANUAL-SCREENSHOTS.md). Run the screenshot
script before a manual release so the published pages match the current UI.
