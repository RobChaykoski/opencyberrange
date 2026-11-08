# SWOCTS Cyber Range 2.5.2

SWOCTS Cyber Range is powered by OpenCyberRange.

Edition: **Professional** — Community / Academic plus analytics, reporting,
cohort analysis, competency evidence, accreditation support, and research
exports.
Status: **patch release**. 2.5.2 moves the administrator privacy default into
the Settings screen and corrects the analytics report test for the six-dimension
Skill DNA model.

## Privacy settings

- Added **Admin > Settings > Security > Default Privacy Mode**. Administrators
  can now choose whether new admin browsers start with privacy mode enabled.
- Added **Privacy Mode (this browser)** to the same screen for an immediate
  local toggle. The sidebar toggle remains available.
- An explicit per-browser choice always wins. Legacy auto-written `"on"` values
  are treated as unset so a changed platform default reaches browsers that never
  made a choice.
- Privacy mode masks usernames, emails, display names, and student IDs in admin
  and instructor views. It is a visual control for screen sharing and
  shoulder-surfing, not an authorization boundary.

## Fixes and verification

- Updated the analytics report test to expect the current six Skill DNA
  dimensions. The `leader` branch was added in 2.5.0 but the report assertion
  still expected five.
- Backend test suite, frontend lint and production build, documentation links,
  licence checks, compose image builds, and Trivy all pass.
- Browser verification against the development stack passed 13/13 privacy
  checks, including a fresh admin browser, the current-browser toggle, the
  platform default, legacy preference migration, and explicit preference
  precedence.

## Upgrade notes

1. Take a database snapshot before upgrading.
2. Pull the current `main` commit or the `v2.5.2` tag.
3. Rebuild the backend and frontend images.
4. Restart the backend once so `privacy_default_on` is seeded into
   `platform_settings`.
5. Start the stack and confirm `/health` and `/api/version` report `2.5.2`.
6. Open **Admin > Settings > Security** and confirm both privacy controls are
   present.
7. If the host uses the prebuild workflow, run `scripts/prebuild-labs.sh` to
   refresh stable `ocr-lab/*:latest` images.
8. Rebuild the workbook wiki and user manual after pulling the documentation.

The backend startup migration is idempotent and additive. Existing users,
courses, sessions, completions, achievements, certificates, and backups are
preserved.

## Previous releases

2.5.1 added the licence-compliance, About/build-info, privacy-control, and
course-workspace cleanup changes. 2.5.0 added organizational course health,
two-way feedback, optional knowledge checks, certificates, the Cyber DNA tester
trait, the celebration wall, database integrity, and deleted-user resilience.
See `CHANGELOG.md` for the complete history.
