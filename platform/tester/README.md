# Lab test harness

`platform/tester` is the independent, manifest-driven acceptance layer for the
production labs. The `Dockerfile` here builds the solver sidecar image; the
contract and runner live in the repository root so they can be reviewed without
starting a lab.

## Contract

Every production lab has a generated contract at
`platform/tester/manifests/<lab-id>.yaml`. Example:

```yaml
lab_id: linux-1-1-ssh-service-detection
track: Linux
difficulty: beginner
source: platform/labs/Linux/linux-1-1-ssh-service-detection/lab.yaml
expected_services:
  - {port: 22, protocol: tcp}
health_timeout_seconds: 60
solver:
  image: ocr-tester:latest
  command: /tests/linux-1-1-ssh-service-detection.sh
  steps:
    - name: Verify SSH port is open
      command: nc -z -w 5 {target.target} 22 && echo 'port_open'
      expect: port_open
expected_flag_count: 1
# The answer key stays in lab.yaml; the harness resolves {flag} at run time.
expected_flag: "{flag}"
forbidden_networks: [control-plane, database, other-learners]
max_memory_mb: 768
max_cpu: 0.75
```

The manifests are generated from `lab.yaml` and `docker-compose.yml`:

```bash
python scripts/generate-lab-manifests.py          # write
python scripts/generate-lab-manifests.py --check  # CI/review
```

Do not edit a manifest by hand. Change the lab definition or the generator.

## What the harness proves

For every run:

1. **Build** — `docker compose build` succeeds (or `--no-build` uses the
   already-built images).
2. **Start** — every compose service starts.
3. **Health** — every declared TCP/UDP service is reachable within
   `health_timeout_seconds`.
4. **Network isolation** — no `network_mode: host`, no forbidden network, no
   non-project network, and no published `0.0.0.0`/`::` ports.
5. **Expected ports** — the declared services answer from the solver sidecar.
6. **Flag existence** — the expected flag is present in the lab source tree.
7. **Flag validation** — the solver steps produce the expected flag and the
   declared distinct-flag count.
8. **Repeat solve** — the same solve steps run a second time in the same
   environment.
9. **Resource usage** — container memory and CPU stay under the manifest
   ceiling.
10. **Teardown** — `docker compose down -v --remove-orphans` always runs.

A **run** starts with `down -v`, so each of the three runs starts from a clean
container and volume state. Add `--rebuild` to rebuild the images for every run
when validating a Dockerfile change.

## Commands

```bash
# Static contract validation; runs anywhere and is in CI.
python scripts/lab_harness.py --validate-all

# One lab, three clean runs.
python scripts/lab_harness.py --lab linux-1-1-ssh-service-detection --runs 3

# Lightweight local smoke when the full tester image is not built yet.
python scripts/lab_harness.py --lab linux-1-1-ssh-service-detection --runs 1 \
  --no-build --no-solver-build --solver-image nicolaka/netshoot:latest

# A release gate on the lab runner.
python scripts/lab_harness.py --all --runs 3 --rebuild --json lab-harness.json
```

Useful options: `--no-build`, `--no-solver-build`, `--keep`, `--fail-fast`.

The live mode needs Docker, the lab images, and `/dev/kvm` for KVM labs. Build
the solver image once if it is not present:

```bash
docker build -t ocr-tester:latest platform/tester
```

The solver runs commands from the tester sidecar on the lab's project network.
`{target.NAME}`, `{cred.ROLE.user}`, `{cred.ROLE.pass}`, and `{flag}` are
resolved before execution. `{target.NAME}` resolves from the compose service
name and hostname, and also from the `topology.nodes[].id` in `lab.yaml` via its
`ip_offset` (so a diagram id such as `webserver` reaches the `web-server`
service).

### Topology labs

Labs whose compose file declares `x-ocr-topology` get an extra compose override
built by `app/services/topology_engine.py` before the project starts. The
harness allocates a free `/29` per link inside `10.128.0.0/9`, assigns the node
addresses, and injects `OCR_ROLE`, `OCR_LINKS`, `OCR_GATEWAY`, `OCR_ROUTES`,
`OCR_FLAG`, and the training credentials. Without that step the nodes start
with no role and no SSH password, so every probe fails. The override lives in a
temporary file and is deleted after teardown.

## Release gate

A production release is not accepted until:

- `python scripts/generate-lab-manifests.py --check` passes.
- `python scripts/lab_harness.py --validate-all` passes.
- `python scripts/lab_harness.py --all --runs 3 --rebuild` passes on the lab
  runner. The JSON result is the release evidence.

The full 191-lab, three-run gate is intentionally a self-hosted job because it
needs Docker, lab images, and KVM. The `.github/workflows/lab-harness.yml`
workflow is the runner entry point.

## Adding a lab

1. Add the lab under `platform/labs/<Track>/<lab-id>/`.
2. Add `test.steps` with commands and `expect` assertions. Use the existing
   `{target.*}`, `{cred.*}`, and `{flag}` placeholders.
3. Run `python scripts/generate-lab-manifests.py`.
4. Run `python scripts/lab_harness.py --lab <lab-id> --runs 3`.
5. Commit the lab, the manifest, and the refreshed supply-chain lock.

Optional `test:` overrides:

```yaml
test:
  health_timeout_seconds: 90
  expected_services:
    - {port: 22, protocol: tcp}
    - {port: 161, protocol: udp}
  forbidden_networks: [control-plane, database, other-learners]
```
