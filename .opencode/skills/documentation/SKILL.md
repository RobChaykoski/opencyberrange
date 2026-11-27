---
name: Documentation
description: Use when writing, reviewing, or refreshing SWOCTS Cyber Range documentation, README/SECURITY/CONTRIBUTING/PRIVACY files, the Manual-Lite user manual, screenshots, release records, or GitHub community files. Enforces one source of truth, SWOCTS voice and formatting, valid links, privacy-safe screenshots, and a stale-reference sweep.
---

# Documentation

Keep SWOCTS Cyber Range documentation current, consistent, privacy-safe, and
valid. Apply this skill to every documentation change and whenever a release,
route, setting, lab count, or screenshot is touched.

## Source of truth (highest first)

1. **Signed release tag** and `versions.yaml`.
2. [`docs/PRODUCTION-DEPLOYMENT-STATEMENT.md`](../../docs/PRODUCTION-DEPLOYMENT-STATEMENT.md)
   for the deployed release, cutover state, and evidence.
3. [`docs/COUNTS.md`](../../docs/COUNTS.md) for lab, manifest, contract, and
   workbook counts.
4. [`docs/RELEASES.md`](../../docs/RELEASES.md) and
   [`CHANGELOG.md`](../../CHANGELOG.md) for history.
5. `README.md`, `SECURITY.md`, and `Manual-Lite/` for user-facing claims.

Never hard-code a version, count, or deployment state in a new page. Link to the
source or use the current value from it. When two documents disagree, fix the
lower one so it agrees with the source of truth.

## Voice and formatting

- Product name: **SWOCTS Cyber Range**. Attribution: **powered by
  OpenCyberRange** on first mention. Do not invent a second product name.
- Use sentence-case headings (`## Deploy the backend`), one H1 per page, and
  ATX headings.
- Prefer short paragraphs, tables for comparisons, and fenced code blocks with a
  language tag (`bash`, `yaml`, `json`, `text`).
- Use relative Markdown links inside the repository. Use absolute GitHub URLs
  only when the target is outside the MkDocs `docs_dir` (for example from
  `Manual-Lite/` into `docs/`).
- Reference versions as `` `5.17.4` `` and tags as `` `v5.17.4` ``. A historical
  record may keep its original version, but label it **Historical**.
- Dates are `16 November 2026` in prose and ISO `2026-11-16` in machine fields.
- Do not use emoji as headings. Use `!!! note`, `!!! warning`, and
  `!!! danger` admonitions in the manual.
- Prefer "learner" for a student, "instructor" for teaching staff, "operator"
  for the person running the deployment, and "administrator" for the platform
  admin role.
- Never include a real password, token, private key, learner name, email, IP, or
  screenshot of real data.

## GitHub community and policy files

Keep these present and current:

- `README.md` — what it is, edition, current release, quick start, links.
- `SECURITY.md` — supported versions, reporting channel, safe harbour, scope,
  lab-safety note, and the current tenant/authorization posture.
- `CONTRIBUTING.md` — local setup, tests, security delta review, CLA, and the
  documentation checks below.
- `CODE_OF_CONDUCT.md` — learner, instructor, contributor, and event conduct.
- `CHANGELOG.md` — human-readable release history.
- `LICENSE`, `LICENSING.md`, `BUILD_NOTICE.md`, `THIRD_PARTY_NOTICES.md`.
- `PRIVACY.md` — plain-language summary that links to the detailed notice.
- `SUPPORT.md` — where to ask, what not to post, and the security route.
- `.github/CODEOWNERS`, `PULL_REQUEST_TEMPLATE.md`, `ISSUE_TEMPLATE/*`,
  `CLA.md`, `dependabot.yml`, and the workflows.
- `docs/DPA-TEMPLATE.md`, `docs/PRIVACY-NOTICE.md`,
  `docs/DATA-CLASSIFICATION.md`, `docs/DATA-LABELS.md`, and
  `docs/PRIVACY-AND-DATA-DELETION.md` for institutional review.

## Privacy and security rules

- Screenshots, examples, and issue templates must use synthetic data. Never
  capture a real learner, instructor, email, token, or host.
- The manual screenshot script turns Privacy Mode off. Capture only against the
  development host with demo or test accounts, then review every diff for
  personal data before committing. If the served catalogue is not the current
  release, the capture is stale even when the data is safe.
- Do not publish operational malware, live credentials, another institution's
  data, or a real public target. Follow the lab-safety and external-target rules.
- A security problem goes to `SECURITY.md`, never a public issue.
- New personal data needs an export, erasure, and retention note. New
  authorization surfaces need an allowed/denied test.

## Screenshots

1. Capture on **development**, never production.
2. Use demo or test accounts with synthetic names (`alex_chen`,
   `jordan_lee`, `sso-student`) and example domains.
3. Confirm the footer/version and catalogue count match the current release.
4. Keep image paths stable; pages reference them directly.
5. Provide descriptive alt text and a `<figcaption>` in the manual.
6. Review the binary diff for PII, secrets, and outdated counts.
7. Record the capture date and release in the pull request.

If the current build or demo credentials are unavailable, do not fake a
screenshot. Leave the existing image, mark the page's refresh as pending, and
say so in the change summary.

## Required checks

Run from the repository root:

```bash
python scripts/check-links.py Manual-Lite docs Workbook --mkdocs
python scripts/check-doc-assets.py
python scripts/generate-api-manual.py --check
python scripts/generate-lab-outcomes.py --check
python scripts/generate-lab-manifests.py --check
python scripts/validate_lab_metadata.py --quiet
python -m mkdocs build -f mkdocs-manual-lite.yml --strict
```

The build must be warning-free. A broken link or missing image is a failure, not
a warning.

## Stale-reference sweep

Before finishing a documentation change, search the touched tree:

```bash
rg -n '5\.5[0-7]\.[0-9]\b|218 labs|\b218\b|193 pending|Release 4|not yet built|are planned|TODO|FIXME|TBD|ocr\.swocts\.com'
```

Triage every hit:

- **Current claim** → update to `5.58.0`, `222 labs`, `<platform-host>`, or the
  current state.
- **Historical record** → keep the value but add a `> **Historical.**` note with
  the date and what superseded it.
- **Dead file** → remove the link or point it at the merged document.

Also confirm that a document you delete or merge has no remaining inbound links
(`rg -n '<old-filename>' docs Manual-Lite README.md SECURITY.md`).

## Definition of done

- Source-of-truth values agree across README, SECURITY, the manual, the
  deployment statement, and COUNTS.
- Links, images, the API manual, lab outcomes, and manifests pass their checks.
- MkDocs builds in strict mode.
- No real data or secrets in text or screenshots.
- Stale and duplicate content is removed or merged, and inbound links are fixed.
- The change summary names the files touched and any screenshot refresh that
  still needs operator credentials.
