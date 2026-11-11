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
