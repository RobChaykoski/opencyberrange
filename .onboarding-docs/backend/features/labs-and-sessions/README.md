# Labs and sessions

## Purpose

Discover lab definitions, expose them through the catalogue, start an isolated
lab for one learner, provide a desktop when the exercise needs one, and clean
everything up on expiry.

## Code map

| Concern | Location |
|---|---|
| Lab router | `platform/backend/app/routers/labs.py` |
| RangeBox router | `platform/backend/app/routers/rangebox.py` |
| Exercise tester | `platform/backend/app/routers/exercise_tester.py` |
| Orchestration | `platform/backend/app/services/docker_manager.py` |
| Preflight | `platform/backend/app/services/lab_preflight.py` |
| Capacity | `platform/backend/app/services/rangebox_capacity.py` |
| Network/topology | `platform/backend/app/services/topology_engine.py` |
| Lab text/naming | `platform/backend/app/services/lab_text.py`, `lab_naming.py` |
| Model | `platform/backend/app/models/lab.py` |
| Definitions | `platform/labs/<Track>/<slug>/lab.yaml` and `docker-compose.yml` |

## API surface

| Method | Path | Notes |
|---|---|---|
| GET | `/api/labs/` | catalogue after visibility and course checks |
| POST | `/api/labs/spawn/{lab_slug}` | start a session |
| GET | `/api/labs/spawn-status/{session_id}` | poll readiness |
| POST | `/api/labs/stop` | stop and clean up |
| POST | `/api/labs/extend` | extend a session |
| POST | `/api/labs/pause`, `/resume` | pause/resume where supported |
| GET | `/api/labs/active` | current sessions |
| GET | `/api/labs/vpn-config` | WireGuard config text |
| GET | `/api/labs/vpn-config/qr` | QR code |
| GET | `/api/labs/vpn-status` | peer status |
| GET | `/api/labs/prebuild-status` | image readiness |

## Session lifecycle

1. **Authorize.** Check visibility, course assignment, enrolment, and consent.
2. **Preflight.** Check session quota, image presence, host capacity, and
   RangeBox capacity.
3. **Allocate.** Choose a per-session `/24` from `10.100.0.0/16`.
4. **Create.** Compose project plus bridge network; start target containers.
5. **Desktop.** If requested, start RangeBox and wait for VNC 6080.
6. **Connect.** Peer Manager creates the WireGuard peer and firewall rule for
   only this `/24`.
7. **Expire.** Scheduler stops the project, removes the network, revokes the
   peer, and records the closure.

## Persistent state

| Store | Data |
|---|---|
| `labs` | catalogue record, flag hash, metadata, visibility, chapter |
| `lab_sessions` | user, lab, status, network, containers, timestamps |
| `flag_attempts` | attempts and hints used |
| `lab_completions` | completion and evidence |
| Docker | per-session containers and networks (ephemeral) |
| Images | prebuilt `ocr-lab/*` images (persistent on host) |

The platform does **not** store learner filesystem data or lab container disks
in PostgreSQL.

## Fixtures and tests

- Register the catalogue: `python /app/app/scripts/init_platform.py` or
  `discover_labs.py`.
- Add a lab: create `platform/labs/<Track>/<slug>/lab.yaml` and a compose file,
  then run `python scripts/validate-lab.py <dir>` and `discover_labs.py`.
- Focused tests:

```bash
cd platform/backend
python -m pytest tests/test_lab_visibility.py tests/test_lab_dns.py \
  tests/test_lab_network_cleanup.py tests/test_rangebox_capacity.py \
  tests/test_rangebox_transport.py tests/test_lab_preflight.py -q
```

## Rules

- Never build an image during a production spawn. Prebuild and verify.
- Never expose a lab container on a host port.
- Never let one learner reach another learner's `/24`.
- Clean up containers, networks, and peers on every failure path.
- Keep intentionally vulnerable lab software pinned; do not "fix" it.

## Related

- [Lab runtime subsystem](../../../lab-runtime/subsystem-overview.md)
- [Flags and scoring](../flags-and-scoring/README.md)
- [Network sandbox](../../../../docs/NETWORK-SANDBOX.md)
- [RangeBox capacity](../../../../docs/RANGEBOX-CAPACITY.md)
- [Lab metadata schema](../../../../docs/LAB-METADATA-SCHEMA.md)
