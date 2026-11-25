# Lab and content counts

Different parts of the repository count different things. Use these definitions
when updating the README, release notes, or a deployment record.

| Count | Value | Source |
|---|---:|---|
| Lab definitions | **217** | every `platform/labs/**/lab.yaml` |
| Unique lab slugs | **217** | directory name of each `lab.yaml` |
| Tester manifests | **217** | `platform/tester/manifests/*.yaml` |
| Competency contracts | **217** | `platform/backend/app/data/competency-contracts.yaml` |
| Labs with a workbook link | **206** | non-empty `workbook:` in `lab.yaml` |
| Labs without a workbook link | **11** | remaining `lab.yaml` files |
| Registered labs in dev/prod | **217** | `labs` table after discovery |
| Public catalogue labs | **170** | `visibility = 'public'`; what a student sees before course enrolment |
| Course-scoped labs | **47** | `visibility = 'course'`; visible only inside an assigned course |
| Tracks | **13** | track folders under `platform/labs` |

The badge and headline should use **217 lab definitions** and, when referring
to workbook coverage, **206 workbook-mapped labs**. A deployment record should
say **217 registered labs** only after lab discovery has run.

The student dashboard and exercise catalogue show **170 public exercises**,
because 47 of the 217 are course-scoped. Do not treat the 170 total as a
missing-content bug; confirm the public/course split before changing the count.

The 5.17.2 wave added 19 pathway labs: 9 Active Directory exercises
(`windows-11-*`) and 10 modern application-security exercises (`web-11-*`).
The November 2026 wave added the course-visible Arkime and ZAP labs. The Cloud
IAM lab is deferred to 5.37.0 and is not counted here.

## Curriculum-manifest caveat

`curriculum-manifest.yaml` is the source for the generated README inventory and
`Workbook/CURRICULUM.md`. It is behind the tree: it still names planned
chapters, it does not declare the Metasploit track, and some chapter
directories (for example `CH_FOR03_Live_Memory`) do not match the manifest.
`python scripts/generate-curriculum-docs.py --check` therefore fails. Do not
hand-edit the generated README inventory to paper over this; fix the manifest
and regenerate. The lab counts above come from `lab.yaml`, not the manifest.

## Historical snapshots

Older records such as "191 labs" (5.17.1), "179 labs" (Release 4), or "160 labs"
are historical snapshots, not current counts. Do not copy them into a current
release claim without checking the tree.

## Regenerate the workbook coverage

```bash
python scripts/generate-workbook-coverage.py
```

This writes `Workbook/COVERAGE.md` with the per-track workbook count.
