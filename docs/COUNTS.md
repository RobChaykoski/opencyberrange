# Lab and content counts

Different parts of the repository count different things. Use these definitions
when updating the README, release notes, or a deployment record.

| Count | Value | Source |
|---|---:|---|
| Lab definitions | **210** | every `platform/labs/**/lab.yaml` |
| Unique lab slugs | **210** | directory name of each `lab.yaml` |
| Tester manifests | **210** | `platform/tester/manifests/*.yaml` |
| Competency contracts | **210** | `platform/backend/app/data/competency-contracts.yaml` |
| Labs with a workbook link | **201** | non-empty `workbook:` in `lab.yaml` |
| Labs without a workbook link | **9** | remaining `lab.yaml` files |
| Registered labs in dev/prod | **210** | `labs` table after discovery |
| Public catalogue labs | **170** | `visibility = 'public'`; what a student sees before course enrolment |
| Course-scoped labs | **40** | `visibility = 'course'`; visible only inside an assigned course |
| Tracks | **13** | track folders under `platform/labs` |

The badge and headline should use **210 lab definitions** and, when referring
to workbook coverage, **201 workbook-mapped labs**. A deployment record should
say **210 registered labs** only after lab discovery has run.

The student dashboard and exercise catalogue show **170 public exercises**,
because 40 of the 210 are course-scoped. Do not treat the 170 total as a
missing-content bug; confirm the public/course split before changing the count.

The 5.17.2 wave added 19 pathway labs: 9 Active Directory exercises
(`windows-11-*`) and 10 modern application-security exercises (`web-11-*`).
They have competency contracts and tester manifests. Their review status is
`pathway_implementation`; the live harness walkthrough is the remaining review
step.

## Historical snapshots

Older records such as "191 labs" (5.17.1), "179 labs" (Release 4), or "160 labs"
are historical snapshots, not current counts. Do not copy them into a current
release claim without checking the tree.

## Regenerate the workbook coverage

```bash
python scripts/generate-workbook-coverage.py
```

This writes `Workbook/COVERAGE.md` with the per-track workbook count.
