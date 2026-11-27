# Tester

The tester is an independent acceptance layer. It does not trust the learner's
UI and it does not reuse the lab's own scripts for proof. It executes the
generated manifest steps from a sidecar container.

## Files

| Item | Location |
|---|---|
| Image | `platform/tester/Dockerfile` |
| Contracts | `platform/tester/manifests/<slug>.yaml` (generated) |
| Runner | `scripts/lab_harness.py` |
| Generator | `scripts/generate-lab-manifests.py` |
| Docs | `platform/tester/README.md` |

## What it proves

For each clean run: build, start, health, network isolation, expected ports,
flag existence, flag validation, repeat solve, resource ceiling, and teardown.

## Commands

```bash
# Static contract validation (CI)
python scripts/lab_harness.py --validate-all

# One lab, three clean runs
python scripts/lab_harness.py --lab linux-1-1-ssh-service-detection --runs 3

# All labs, three runs, JSON evidence
python scripts/lab_harness.py --all --runs 3 --json harness.json
```

Live mode needs Docker, the lab images, and `/dev/kvm` for KVM labs. Static mode
runs anywhere.

## Contract rules

- The manifest is generated; do not hand-edit it.
- The flag stays in `lab.yaml`; the manifest uses `{flag}`.
- Solver steps use `{target.<service>}` and must be deterministic.
- A lab must survive three clean runs.
- The last step should retrieve the flag so the validator sees the evidence.
- Resource ceilings must match the compose file.

## Adding a solver step

1. Add the step to `lab.yaml` under `test.steps`.
2. Keep the command portable to the Alpine tester image (`curl`, `jq`, `nc`,
   `python3`, `grep`, `sed`).
3. Avoid network access outside the lab.
4. Regenerate the manifest.
5. Run the lab three times.

## Security

- The tester sidecar is attached only to the session network.
- It must not reach the control plane, database, or another learner.
- It runs with the lab's resource ceiling.
- `EXEC` on the Docker proxy is needed for the tester; keep it scoped.

## Related

- [Lab runtime](../subsystem-overview.md)
- [Lab harness README](../../../platform/tester/README.md)
- [Lab metadata schema](../../../docs/LAB-METADATA-SCHEMA.md)
