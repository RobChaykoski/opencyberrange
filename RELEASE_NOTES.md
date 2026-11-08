# SWOCTS Cyber Range 2.5.0

SWOCTS Cyber Range is powered by OpenCyberRange.

Edition: **Professional** — Community / Academic plus analytics, reporting,
cohort analysis, competency evidence, accreditation support, and research
exports.
Status: **minor release**. 2.5.0 adds organizational course health, the
two-way feedback engine, optional exercise knowledge checks, certificate
sharing, and the EXIF metadata lab.

Enterprise preview remains the separate HA, SSO, enterprise reporting,
multi-tenant, LMS, and compliance-reporting profile. See `docs/EDITIONS.md`.

## Organizational course health

- The Academy → Courses page is now an organizational course-health workspace:
  student satisfaction, instructor engagement, response rate, knowledge-check
  participation, and a prioritized action list.
- The course Overview is role-aware. Instructors and administrators see course
  health and next actions; students see their own progress, next exercise, and
  feedback status.
- The public scoreboard is removed from the course workspace. Detailed metrics
  remain private and descriptive, with sample sizes and data-source labels.
- A course-health status uses **Healthy / Watch / Needs attention** and explains
  the reason for the current status.

## Two-way feedback

- Students use the existing survey engine for a one-minute course check-in;
  participation is opt-in under **Privacy and data**.
- Instructors add private coaching notes and see aggregated student voice.
- Existing exercise pulse surveys and reactions feed the metrics immediately.
- The summary reports response rate, clarity, challenge fit, engagement,
  instructor coaching, and quiz experience.
- Student comments are anonymized. Students never see another student's answers
  or identity.

## Optional knowledge checks

- Each exercise can expose a short benchmark check: **2–3 randomized questions**
  per attempt, unlimited re-attempts, and explanations and references after
  submission.
- Ten lab-specific certification banks and eleven track fallback banks cover
  every exercise. The fallback is clearly labelled as a general track benchmark.
- Four achievements are available: **Quiz Ace**, **Quiz Explorer**,
  **Quiz Scholar**, and **Quiz Comeback**.
- Quiz participation and best scores add evidence to Cyber DNA (Builder and
  Explorer), and a Knowledge checks card appears on the profile.
- Post-quiz ratings for satisfaction, relevance, usefulness, and ease of use
  feed the course health report.
- Quizzes are optional and cannot affect lab access, completion, certificates, or
  grades.

## Certificates

- Added a server-rendered certificate PDF.
- Added **Download PDF**, **Copy verification link**, **Share on LinkedIn**, and
  native share actions, plus a share panel.
- Added Open Graph and Twitter metadata to the public verification page.
- Added a warning when the certificate still uses the login handle, with a link
  to set the printed name.
- Existing certificates remain valid when bonus labs are added: only
  certificate-required labs count toward the level.

## Labs and host validation

- Added the **EXIF Metadata Investigation** lab with a safe evidence image,
  camera, time, GPS, author, and free-text metadata, plus a beginner workbook.
- Certified Ubuntu 24.04 LTS for 2.4.1 on 8 November 2026. 2.5.0 inherits the
  certified baseline.
- Fixed VPN forwarding by placing the VPN accepts in `DOCKER-USER`, added the
  Docker bridge UFW rule, and added the `ocr-network-tap` image.
- Raised the MS-SQL lab `max_connect_errors` threshold, corrected the remote
  credentials, and removed the trailing newline from the flag file.

## Upgrade notes

1. Take a database snapshot before upgrading.
2. Pull the current `main` commit or the `v2.5.0` tag.
3. Rebuild the backend and frontend images.
4. Start the stack and confirm `/health` and `/api/version` report `2.5.0`.
5. Confirm the course Overview shows course health and that an existing lab still
   launches.
6. If the host uses the prebuild workflow, run `scripts/prebuild-labs.sh` to
   refresh stable `ocr-lab/*:latest` images.
7. Rebuild the workbook wiki and user manual after pulling the documentation.

The backend startup migration is idempotent and additive. Existing users,
courses, sessions, completions, achievements, certificates, and backups are
preserved.

## Verification

- Backend test suite passes, including the course-feedback and knowledge-check
  tests.
- Frontend production build and lint pass with 0 errors.
- Knowledge-check validator: 21 banks, 10 certification and 11 general, all
  valid.
- Documentation link check: 313 Markdown files, no broken links.
- CI on both repositories is green.
- Scheduled UI smoke against the public production URL passes.
- Both deployments report the same release after deployment.

## Previous release

2.4.1 contained the security and UX remediation on top of the 2.4.0 feature set.
The 2.5.0 review carries those fixes forward and records the full change set in
`CHANGELOG.md`.
