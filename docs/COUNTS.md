# Lab and content counts

Different parts of the repository count different things. Use these definitions
when updating the README, release notes, or a deployment record.

| Count | Value | Source |
|---|---:|---|
| Lab definitions | **191** | every `platform/labs/**/lab.yaml` |
| Unique lab slugs | **191** | directory name of each `lab.yaml` |
| Tester manifests | **191** | `platform/tester/manifests/*.yaml` |
| Competency contracts | **191** | `platform/backend/app/data/competency-contracts.yaml` |
| Labs with a workbook link | **182** | non-empty `workbook:` in `lab.yaml` |
| Labs without a workbook link | **9** | remaining `lab.yaml` files |
| Registered labs in dev/prod | **191** | `labs` table after discovery |
| Tracks | **12** | track folders under `platform/labs` |

The badge and headline should use **191 lab definitions** and, when referring
to workbook coverage, **182 workbook-mapped labs**. A deployment record should
say **191 registered labs** only after lab discovery has run.

## Historical snapshots

Older records such as "179 labs" in the Release 4 evidence are historical
snapshots, not current counts. Do not copy them into a current release claim
without checking the tree.

## Regenerate the workbook coverage

```bash
python scripts/generate-workbook-coverage.py
```

This writes `Workbook/COVERAGE.md` with the per-track workbook count.
