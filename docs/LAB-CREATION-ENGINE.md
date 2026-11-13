# Lab creation engine

`scripts/create-lab.py` turns a small node/link specification into a complete
routed-topology lab: `lab.yaml`, `docker-compose.yml` with `x-ocr-topology`, a
README, and a workbook scaffold. It runs the static validator before returning.

## Quick start

```bash
python3 scripts/create-lab.py \
  --track network --level 13 \
  --name "BGP Route Leak" \
  --node h1:host --node r1:router --node r2:router \
  --node svc:service:flag \
  --link h1-r1 --link r1-r2 --link r2-svc \
  --pace guided \
  --flag 'OCR{bgp_route_leak}'
```

Without `--node` / `--link` it creates the standard three-node guided topology
(`h1` host → `r1` router → `svc` service).

## Node and link syntax

- `--node id:host`
- `--node id:router`
- `--node id:service:flag` — the node that serves the flag
- `--link from-to` — a point-to-point `/29`

One service is always selected for the flag. If no node has the `:flag` marker,
the first service is used.

## What is generated

| File | Contents |
|---|---|
| `platform/labs/<Track>/<slug>/lab.yaml` | Metadata, outcomes, scenario, credentials, hints, topology, generated test steps |
| `platform/labs/<Track>/<slug>/docker-compose.yml` | `x-ocr-topology` plus reviewed node services with resource caps |
| `platform/labs/<Track>/<slug>/README.md` | Node table and publishing checklist |
| `Workbook/<slug>/00_Introduction.md` | Learner scaffold with topology and steps |

Every node gets:

- `ocr-lab/topology-node:latest` (reviewed image only);
- `NET_ADMIN` and `no-new-privileges`;
- `mem_limit` 192–256m, `cpus` 0.20–0.25, `pids_limit` 96;
- `ip_offset` starting at 21.

The generator refuses duplicate node ids, unknown links, a missing service, and
passwords shorter than 10 characters.

## Pace

- `--pace guided` writes four structured hints and the full guided flow.
- `--pace independent` writes one general hint so the learner chooses the method.

Use `--node ...` / `--link ...` to add a decoy or a second router for the
independent variant.

## Options

| Option | Purpose |
|---|---|
| `--track` | Track slug (default `network`) |
| `--level` | Level number used in the slug and `week` |
| `--lab-num` | Override the next free lab number |
| `--difficulty` | `beginner`, `intermediate`, `advanced`, `expert` |
| `--duration` | Estimated minutes |
| `--visibility` | `draft` (default), `course`, `public` |
| `--prereq` | Prerequisite slug, repeatable |
| `--flag` | Flag value; generated if omitted |
| `--training-password` | SSH password for the nodes |
| `--dry-run` | Show files without writing |
| `--no-validate` | Skip the static validator |
| `--list-tracks` | List track slugs |

## After generation

1. Replace the scaffold flag and scenario text; never keep a generated flag in a
   published lab.
2. Add the workbook page to the track's MkDocs navigation.
3. `python scripts/validate-lab.py <lab directory>`
4. Build the node image if needed:
   `docker build -t ocr-lab/topology-node:latest platform/topology-node`
5. Discover the lab:
   `docker compose exec -T backend python /app/app/scripts/discover_labs.py`
6. Spawn it, complete it once, and check the generated test steps.

## Safety and performance

The generator only emits the reviewed topology image and the same caps the
engine enforces. It does not accept a `build:` context, `privileged`, host
networking, devices, or volumes. The static validator rejects a lab that exceeds
512m / 0.5 CPU / 256 PIDs per node or 2048m total.

The supply-chain lock covers `scripts/create-lab.py`, the node image build
context, and every generated lab.
