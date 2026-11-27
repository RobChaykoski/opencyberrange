# Lab runtime subsystem

The lab runtime turns a lab definition into one isolated learner environment,
gives the learner a way to reach it, runs the acceptance harness, and cleans it
up. It is the most operationally sensitive part of the platform after auth.

## Folder map

```text
platform/labs/
├── <Track>/<slug>/
│   ├── lab.yaml             contract, flag, hints, test steps
│   └── docker-compose.yml   services, resources, networks
├── _shared/                 shared target images
├── _swsec_shared/           software-security target
├── _karate_shared/          Karate lab target
└── <Track>/_track_quiz.yaml quiz bank

platform/tester/
├── Dockerfile               solver sidecar image
├── manifests/<slug>.yaml    generated acceptance contract
└── README.md
```

## Lifecycle

1. **Discover** — `discover_labs.py` reads every `lab.yaml` and registers the
   exercise.
2. **Validate** — `validate-lab.py`, the metadata schema, and the harness
   contract.
3. **Prebuild** — `prebuild-labs.sh` builds stable `ocr-lab/<slug>-<service>`
   images. Production never builds during a spawn.
4. **Spawn** — the backend creates a Compose project and a per-session bridge.
5. **Connect** — VPN peer and firewall rules, or RangeBox VNC through the
   backend.
6. **Solve** — the learner uses the tools; the flag proves completion.
7. **Expire** — the scheduler stops the project, removes networks, and revokes
   the peer.
8. **Accept** — the harness proves build, start, health, isolation, flag,
   repeat solve, resource ceiling, and teardown.

## Authoring a lab

```bash
mkdir -p "platform/labs/<Track>/<slug>"
# add lab.yaml and docker-compose.yml
python scripts/validate-lab.py "platform/labs/<Track>/<slug>"
python scripts/generate-lab-manifests.py
python scripts/lab_harness.py --validate-all
python scripts/generate-workbook-coverage.py
```

Required lab fields include title, category, difficulty, estimated time,
prerequisites, learning outcomes, mapped skills, assessment criteria, MITRE
mapping, description, flag, hints, test steps, workbook, hostnames, and topology.
See [LAB-METADATA-SCHEMA](../../docs/LAB-METADATA-SCHEMA.md).

## Isolation rules

- One Compose project and one bridge per session.
- Lab containers never publish a host port.
- No `network_mode: host`.
- No control-plane, database, or other-learner network.
- Per-session `/24` from `10.100.0.0/16`.
- Topology links use the protected `10.128.0.0/9` range.
- Resource ceilings come from the manifest.

## Persistent state

| Store | Data |
|---|---|
| `labs` | catalogue row |
| `lab_sessions` | session and network |
| Docker | containers, networks, images (ephemeral except images) |
| `/labs` | definitions, read-only |
| `workbook_data` | workbook and course wiki inputs |

Lab containers do not persist learner filesystem data in PostgreSQL.

## Pages

- [Runtime diagram](subsystem-technical-architecture-diagram.md)
- [Tester](tester/README.md)
- [RangeBox](rangebox/README.md)

## Related

- [Lab creation engine](../../docs/LAB-CREATION-ENGINE.md)
- [Lab definitions repository](../../docs/LAB-DEFINITIONS-REPOSITORY.md)
- [Network sandbox](../../docs/NETWORK-SANDBOX.md)
- [RangeBox capacity](../../docs/RANGEBOX-CAPACITY.md)
- [Backend labs and sessions](../backend/features/labs-and-sessions/README.md)
