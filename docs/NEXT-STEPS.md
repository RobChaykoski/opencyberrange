# Next steps after 2.7.0

Status: **paused** on 11 November 2026. Everything below is queued; nothing is
in progress.

## Baseline

- `v2.7.0` is live on development (`172.16.16.44`) and production
  (`172.16.16.41` / `https://ctfd.swocts.com`), both healthy.
- Tag `v2.7.0` -> `ce7c25bb`; release evidence is in `599d78c1`.
- CI, Quality checks, CodeQL, and Trivy are green on the public repository.
- Actions stay disabled on the private `opencyberrange-v2` mirror.
- Production: 34 GB free disk, computed RangeBox maximum 20, live cap 15.
- Development: 189 GB free disk, same computed maximum and live cap.
- The Beginner quiz banks are live; the other 11 tracks have no quiz banks.

## Queue

### 1. Post-release watch

- Watch backend logs, health, and disk for 24-48 hours.
  - `docker logs --since 24h ocr-backend | grep -Ei 'traceback|error|exception'`
  - `curl -sS http://127.0.0.1:8000/health`
  - `df -h /var/lib/docker`
- Sign `v2.7.0` with the release key if it is available; otherwise keep the
  documented unsigned-tag exception in `docs/RELEASES.md`.
- Run the scheduled external-links workflow once:
  `gh workflow run external-links.yml --repo RobChaykoski/opencyberrange`.

### 2. Quiz banks for the remaining tracks

The runtime, scoring, and UI gating are live. This is content work only.

Levels by track on the current deployment:

| Track | Levels |
|---|---:|
| ai | 6 |
| forensics | 2 |
| identity | 2 |
| linux | 6 |
| malware | 2 |
| network | 7 |
| osint | 2 |
| ot | 1 |
| software-security | 5 |
| web | 6 |
| windows | 10 |

That is **49 level banks** if every level gets a quiz. Start with the tracks
that have the most learners, and skip levels where a quiz adds no value.

Work items:

1. Extend `QUIZZES` in
   `platform/backend/app/scripts/seed_level_quizzes.py` by track slug and level
   number, using the existing 4-6 question shape and passing score 70.
2. Keep option order stable after learners have attempted a bank; stored
   attempts reference option indices.
3. Run the seed script in each backend container.
4. Verify: `has_quiz=true` for seeded levels, the Quiz button appears only on
   completed levels, and a full-mark submission returns 100%.

### 3. Production capacity test

- Run the Level 4 RangeBox stress test on development first, then production in
  an idle window.
- The test spawns up to the computed maximum (20). Watch host CPU, memory,
  first-frame latency, and rejected launches.
- Record the result in `docs/RANGEBOX-CAPACITY.md` and confirm the measured
  ceiling and live cap in **Admin -> Settings -> Exercises -> RangeBox
  capacity**.
- Do not run it while learners are active; a failed threshold is the practical
  ceiling, not a target to exceed.

### 4. Disk and prebuild plan

- Production is at 34 GB free against the 60 GB prebuild recommendation.
- Remove stale `ocr-lab` hash tags against `scripts/.lab-build-manifest.json`,
  then check `docker system df` and `df -h /var/lib/docker`.
- Never run `docker image prune -a`; it removes the prebuilt lab images.
- Prebuild `web-1-1-basic-directory-enumeration` on development if development
  is meant to be fully prebuilt. Production already has it.
- Plan expansion before the next lab-image wave if cleanup cannot recover
  enough headroom.

### 5. Lab metadata and learning analytics

Continue the development focus recorded in `versions.yaml`: lab metadata and
learning analytics. Break this into a written scope before implementation.

### 6. Advanced DNA insights: manual, screenshots, and review

The development preview adds **Momentum**, the **Career Atlas**, and the extended
career dossier. It is gated by **Admin -> Settings -> Features -> Advanced DNA
Insights** and is off by default in production. The design and review checklist
are in `docs/CAREER-ATLAS-AND-MOMENTUM.md`.

Work items:

1. **Deploy the preview to development.** Pull the reviewed tree on
   `172.16.16.44` as `ocrv2`, build and restart the backend and frontend with the
   root Compose files, then enable **Advanced DNA Insights** in
   **Admin -> Settings -> Features** or with `bash scripts/dev-insights.sh on`.
2. **Run the backend tests** for Momentum, the Career Atlas, and the feature gate:
   `python -m pytest tests/test_skill_momentum.py tests/test_career_explorer.py -q`.
3. **Run the frontend gates:** `npm run lint` and `npm run build` in
   `platform/frontend`.
4. **Capture the manual screenshots from development** with a real learner and an
   administrator:
   ```bash
   UI_BASE_URL=https://172.16.16.44 \
   UI_SMOKE_USERNAME='<learner>' UI_SMOKE_PASSWORD='<password>' \
   node scripts/ui-manual-screenshots.mjs
   ```
   The script writes:
   - `Manual-Lite/02_Student_Guide/img/profile-dna.png`
   - `Manual-Lite/02_Student_Guide/img/profile-momentum.png`
   - `Manual-Lite/02_Student_Guide/img/profile-careers.png`
   - `Manual-Lite/04_Admin_Guide/img/admin-settings-features.png`
   The committed preview images are design illustrations, not live captures. A
   real capture must replace them before the preview is announced.
5. **Review the manual pages** after the capture:
   - `Manual-Lite/02_Student_Guide/21_Career_Atlas_And_Momentum.md`
   - `Manual-Lite/02_Student_Guide/16_Viewing_Your_Profile.md`
   - `Manual-Lite/02_Student_Guide/11_Tracking_Your_Progress.md`
   - `Manual-Lite/04_Admin_Guide/20_Platform_Settings.md`
   - `Manual-Lite/04_Admin_Guide/28_Reporting_And_Analytics.md`
   - `Manual-Lite/08_Glossary/01_Glossary.md`
6. **Run the documentation gates:**
   `python scripts/check-doc-assets.py` and
   `mkdocs build -f mkdocs-manual-lite.yml`.
7. **Run the security delta review** with the project software-security skill
   before release:
   - permissions: only the signed-in learner's data; no staff-wide atlas
     endpoint;
   - inputs: no new user-controlled input reaches SQL, a shell, a template, or a
     file path;
   - databases: only existing completion and session records, filtered by
     `user_id`;
   - output: every learner- or API-controlled value is HTML-escaped in the
     dossier; the Vue components use interpolation, not `v-html`;
   - gate: the feature is off by default and read fresh on every request;
   - secrets: no new secret, token, key, or PII in code, screenshots, or docs.
8. **Record the review** in `docs/UI-VERIFICATION.md` with the date, widths
   (375, 768, 1024, 1440), themes, and the name of the reviewer.
9. **Decide the production release.** Keep the feature off until the
   institutional review of career framing and salary data is signed off.

### 7. Phone OSINT exercises

The first phone exercise is implemented as
`platform/labs/OSINT/osint-2-3-responsive-leak` with the workbook chapter
`Workbook/CH_OSINT02_Mobile_OSINT/01_The_Mobile_Build.md`. The desktop response
omits the flag; the mobile response includes a contact card with the flag. This
demonstrates that a client-specific template is not an access control.

Next:

1. Publish and validate the lab on development. Run
   `python scripts/validate-lab.py platform/labs/OSINT/osint-2-3-responsive-leak`
   and a live walkthrough on a phone.
2. Finish the public-profile exercise (`osint-2-4-public-profile`). It is
   implemented with a training mirror and the uppercase
   `OCR{linkedIn_0s1nt_m4st3r_2026}` flag. Set the real `PROFILE_URL` in the lab
   Compose file, regenerate `Workbook/CH_OSINT02_Mobile_OSINT/img/profile-qr.png`
   with `scripts/generate-osint-qr.py`, and confirm the public LinkedIn About
   uses the uppercase form. Do not scrape, collect PII, or search another
   person's profile.
3. Validate the synthetic Shodan exercise (`osint-2-5-public-banner`). It is
   implemented with a local mirror in `_shared/app.py`; do not query real Shodan
   for third-party hosts.
4. Update the workbook, `mkdocs-osint.yml`, and the manifest after each lab is
   validated.
5. Run `python scripts/generate-curriculum-docs.py`,
   `python scripts/generate-workbook-coverage.py`, and the security delta review.

See [Phone OSINT exercises](PHONE-OSINT-EXERCISES.md) for the design, ATT&CK
mapping, and safety rules.

### 8. Career readiness, GPS, and curriculum demand

The development tree adds the learner **Portfolio** tab (role readiness,
Cybersecurity GPS, professional portfolio, competency taxonomy), the per-course
exercise heatmap, and the instructor **Curriculum demand** panel. They are behind
the same **Advanced DNA Insights** gate and are documented in
[CAREER-READINESS-AND-GPS.md](CAREER-READINESS-AND-GPS.md).

Next:

1. Deploy the reviewed tree to development, keep the gate on there, and confirm
   `/api/profile/competencies`, `/api/profile/roles`,
   `/api/profile/role-readiness`, `/api/profile/gps`, and
   `/api/analytics/reports/curriculum-demand` respond for a learner and an
   instructor.
2. Run `python -m pytest tests/test_curriculum_demand.py
   tests/test_career_readiness.py -q` and the DB-backed profile tests with
   `TEST_DATABASE_URL`.
3. Capture the Portfolio tab, GPS, taxonomy, exercise heatmap, and Curriculum
   demand at 375/768/1024/1440 in both themes. Replace the preview images and
   record the pass in `docs/UI-VERIFICATION.md`.
4. Have an instructor review the curriculum-demand prompts against a real course
   and confirm the wording reads as a planning prompt, not a teacher evaluation.
5. Keep the gate off in production until the career-framing review is signed off.

### 9. Achievement studio and certification question banks

The development tree adds a grouped, filterable **Achievement studio** and an
admin-only **Question banks** view. Tier and difficulty set the point value, and
a perfect three-question sampled check earns the SWOCTS-specific **Platinum
Check**. The full bank, answers, explanations, and references are never sent to
learners. See [Certification question banks](CERTIFICATION-QUESTION-BANKS.md).

Next:

1. Deploy to development and open **Admin -> Settings -> Achievements** and
   **Question banks**. Confirm the studio groups, filters, create/edit, and
   two-step delete work, and that a non-admin receives 403 from the bank API.
2. Run `python scripts/check-question-banks.py` and
   `python -m pytest tests/test_achievement_catalogue.py
   tests/test_certification_quiz.py -q`.
3. Have a subject-matter reviewer read each pathway against the current public
   objectives. Record the review date and update `reviewed_at`.
4. Capture the studio and question-bank views at 375/768/1024/1440 in both
   themes and record the pass in `docs/UI-VERIFICATION.md`.
5. Keep the question bank admin-only. Do not expose answers through a learner
   route, an export, or a workbook asset.

### 10. DevFest 2027 Cyber Discovery Experience

The event plan is captured in
[DEVFEST-2027-CYBER-DISCOVERY.md](DEVFEST-2027-CYBER-DISCOVERY.md) and
`platform/backend/app/data/devfest-2027.yaml`. The experience now uses the
existing event engine: a normal event with `experience_key = "devfest-2027"`
gets the Cyber Discovery panel and the `discovery` certificate. Seed it with
`python -m app.scripts.seed_devfest_event --preview` on development.

Next:

1. Build the four **Career Stories** briefs in [CAREER-STORIES.md](CAREER-STORIES.md).
   Start with the SOC and DFIR stories.
2. Add the event labs or workbook chapters for the stories and map them to the
   competencies in the plan.
3. Rehearse the full six hours on development with a mixed cohort.
4. Capture the event detail, discovery panel, and certificate at 375/768/1024/1440
   in both themes and record the pass in `docs/UI-VERIFICATION.md`.
5. Run `python scripts/check-devfest-plan.py` after any plan edit.

### 11. Hardening and refactor follow-ups

The November 2026 hardening pass is deployed to development. See
[HARDENING-2026-11.md](HARDENING-2026-11.md). Remaining work:

1. Drain the inline `ALTER TABLE` blocks in `main.py` into Alembic revisions, then
   add the no-inline-migration guard.
2. Rehearse a PostgreSQL major-version upgrade.
3. Run a real backup and restore drill from the `backups_data` volume.
4. Audit the frontend nginx configuration and `ui-*.mjs` smoke suites.
5. Add the remaining eager-load fixes in `analytics.py`, `dashboard.py`, and
   `admin.py`, gated by `stress_test.py` query-count diffs.
6. Decide whether to enable the socket-proxy `BUILD` category; it must stay off
   unless on-demand lab builds are enabled.

## Known warnings to ignore

- `RangeBox ... not available after retries - skipping bridge` appeared while
  temporary QA sessions were being torn down. The sessions still reached
  `running` and the RangeBox IP-hiding check passed.
- Development logged an on-demand build for
  `web-1-1-basic-directory-enumeration` because that image is not prebuilt
  there. Production had no missing images.

## Resume checklist

1. `git status` is clean and both hosts are on `main`.
2. `python scripts/status-dashboard.py --config docs/status-hosts.json`
   reports `healthy`.
3. CI on `main` is green.
4. Pick the first item from the queue and record the result in
   `docs/UI-VERIFICATION.md` or `docs/2.7.0-PLAN.md`.
