# Project overview pack

Status: **current for release 5.56.1** (26 November 2026).

This folder is the single place for the platform's infrastructure, network,
software inventory, data dictionary, and API contract. It is written for
operators, reviewers, and integrators who need the current picture without
reading the whole repository.

| File | What it answers |
|---|---|
| [INFRASTRUCTURE.md](INFRASTRUCTURE.md) | What the runtime components are, how a request flows, and which component talks to which |
| [NETWORK-MAP.md](NETWORK-MAP.md) | The internal network map: Docker networks, published ports, lab/VPN ranges, and trust boundaries |
| [SOFTWARE-METADATA.md](SOFTWARE-METADATA.md) | Name, pinned version, latest available version, source, and notes for the stack |
| [software-metadata.json](software-metadata.json) | The same inventory in machine-readable form |
| [DATA-DICTIONARY.md](DATA-DICTIONARY.md) | The data dictionary copy for this pack |
| [API-CAPABILITIES.md](API-CAPABILITIES.md) | Human-readable OpenAPI capability inventory grouped by tag |
| [openapi.json](openapi.json) | The live OpenAPI 3.1 contract exported from FastAPI |

## Source of truth

- Runtime topology and threat boundaries: [`../ARCHITECTURE.md`](../ARCHITECTURE.md)
- Deployment commands and layout: [`../DEPLOYMENT-RUNBOOK.md`](../DEPLOYMENT-RUNBOOK.md)
- Sizing and exposure rules: [`../DEPLOYMENT-TOPOLOGY-AND-SIZING.md`](../DEPLOYMENT-TOPOLOGY-AND-SIZING.md)
- Privacy fields: [`../DATA-DICTIONARY.md`](../DATA-DICTIONARY.md)
- Release record: [`../PRODUCTION-DEPLOYMENT-STATEMENT.md`](../PRODUCTION-DEPLOYMENT-STATEMENT.md)
- API reference: [`../../Manual-Lite/11_API_Reference/index.md`](../../Manual-Lite/11_API_Reference/index.md)

## Regenerating the API export

The API files are generated from the live FastAPI app so they cannot drift:

```bash
python scripts/export-openapi.py
python scripts/export-openapi.py --check
```

`DATA-DICTIONARY.md` is a copy of the reviewed data dictionary. When the source
dictionary changes, copy it into this folder and review the diff.

## Publication rule

Use placeholders for real addresses, hostnames, accounts, and secrets. The
network map uses generic Docker subnets and address ranges; it does not publish
the production host's management address.
