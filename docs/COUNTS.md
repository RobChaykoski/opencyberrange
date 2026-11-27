# Lab and content counts

Different parts of the repository count different things. Use these definitions
when updating the README, release notes, or a deployment record.

| Count | Value | Source |
|---|---:|---|
| Lab definitions | **222** | every `platform/labs/**/lab.yaml` |
| Unique lab slugs | **222** | directory name of each `lab.yaml` |
| Tester manifests | **222** | `platform/tester/manifests/*.yaml` |
| Competency contracts | **222** | `platform/backend/app/data/competency-contracts.yaml` |
| Labs with a workbook link | **211** | non-empty `workbook:` in `lab.yaml` |
| Labs without a workbook link | **11** | remaining `lab.yaml` files |
| Registered labs in dev/prod | **218** | `labs` table after discovery; the four Karate labs register on the next discovery run |
| Public catalogue labs | **175** | `visibility = 'public'`; what a student sees before course enrolment |
| Course-scoped labs | **47** | `visibility = 'course'`; visible only inside an assigned course |
| Tracks | **13** | track folders under `platform/labs` |

The badge and headline should use **222 lab definitions** and, when referring
to workbook coverage, **211 workbook-mapped labs**. A deployment record should
say **222 registered labs** only after lab discovery has run.

The student dashboard and exercise catalogue show **175 public exercises**,
because 47 of the 222 are course-scoped. Do not treat the 175 total as a
missing-content bug; confirm the public/course split before changing the count.

The 5.17.2 wave added 19 pathway labs: 9 Active Directory exercises
(`windows-11-*`) and 10 modern application-security exercises (`web-11-*`).
The November 2026 wave added the course-visible Arkime and ZAP labs. The
Software Security track now includes the four `software-security-3-*` Karate
API-testing labs. The Cloud IAM lab is deferred to 5.37.0 and is not counted
here.

## Curriculum-manifest state

`curriculum-manifest.yaml` is the source for the generated README inventory and
`Workbook/CURRICULUM.md`. The four Karate labs are declared under `SWSEC02`,
which follows `SWSEC01` and recommends `MAL01` next. The manifest still names
planned chapters; those are intentional and are not counted as lab definitions.
`python scripts/generate-curriculum-docs.py --check` must pass before a release.
The lab counts above come from `lab.yaml`, not the manifest.

## Historical snapshots

Older records such as "191 labs" (5.17.1), "179 labs" (Release 4), or "160 labs"
are historical snapshots, not current counts. Do not copy them into a current
release claim without checking the tree.

## Regenerate the workbook coverage

```bash
python scripts/generate-workbook-coverage.py
```

This writes `Workbook/COVERAGE.md` with the per-track workbook count.
