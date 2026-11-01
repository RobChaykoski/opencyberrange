# OpenCyberRange Next

This is the staging tree for the latest-supported-GA platform upgrade. The stable
production tree remains at `RobChaykoski/opencyberrange-backup`.

Start with:

- [Upgrade plan](docs/UPGRADE-TO-LATEST-GA-PLAN.md)
- [Supported versions](docs/SUPPORTED-VERSIONS.md)
- [Version inventory](scripts/report-versions.py)

Wave 0 establishes the baseline and CI before any application dependency is
changed. Lab and RangeBox images are intentionally out of scope.

```bash
python scripts/report-versions.py --platform-only
```

Do not push a lab or RangeBox image upgrade into this tree without a separate
programme and per-lab solve tests.
