# OpenCyberRange editions

Status: **Active product model**

OpenCyberRange has three deployment editions. The editions describe scope and
operational shape, not three separate codebases. Each edition builds on the
previous one.

| Edition | Version line | Shape | Primary user |
|---|---|---|---|
| **Base** | 1.1.x | Single-host Docker Compose teaching platform | Instructor, small classroom, self-hosted operator |
| **Pro** | 2.0.x | Base plus learning analytics, reporting, and exports | Instructor, programme lead, teaching team |
| **Enterprise** | 3.0.x | Pro plus multi-host HA, identity federation, and enterprise operations | Institution, IT operations, multi-cohort deployment |

## Edition boundaries

### Base — 1.1

Base is the supported, stable teaching platform:

- courses, exercises, tracks, labs, RangeBox, flags, hints, and achievements;
- profiles, certificates, transcripts, and competitions;
- single-host Docker Compose deployment on Ubuntu 22.04 or 24.04;
- WireGuard learner access, backups, privacy, erasure, and mail settings;
- maintenance and security fixes.

Base is the reference behaviour. Pro and Enterprise must not regress it.

### Pro — 2.0

Pro adds the teaching intelligence layer on the same single-host deployment:

- student learning analytics and course analytics;
- cross-course reports, RAG signals, pulse surveys, CSV/PDF export;
- learning hours, exercise reactions, and engagement badges;
- the 24.04 single-host baseline;
- OWASP Top 10 security baseline and release evidence.

Pro is not a multi-host product. It remains a single Docker host and does not
add identity federation or distributed scheduling.

### Enterprise — 3.0

Enterprise adds the deployment and identity layer:

- multi-host lab pool with capacity-aware placement;
- central session `/24` allocation and VPN gateway route reconciliation;
- node agent, mTLS control channel, drain, node-loss recovery, and reconciliation;
- replicated frontend/API, PostgreSQL HA, Redis HA, shared object storage;
- WireGuard gateway failover;
- LDAP, OIDC, and SAML identity-provider settings and federation adapters;
- enterprise monitoring, alerting, and operational runbooks.

Enterprise depends on Pro. It does not replace the single-host path, which
remains the default and fallback.

## Feature matrix

| Capability | Base 1.1 | Pro 2.0 | Enterprise 3.0 |
|---|---:|---:|---:|
| Courses, labs, RangeBox, flags, hints | Yes | Yes | Yes |
| Profiles, certificates, transcripts | Yes | Yes | Yes |
| Competitions and achievements | Yes | Yes | Yes |
| Single-host Docker Compose | Yes | Yes | Yes |
| Ubuntu 22.04 support | Yes | Maintenance reference | No |
| Ubuntu 24.04 support | Yes | Yes | Yes |
| Learning analytics | No | Yes | Yes |
| Cross-course reporting, CSV/PDF | No | Yes | Yes |
| Pulse surveys and feedback | No | Yes | Yes |
| Multi-host lab pool | No | No | Yes |
| Control-plane HA | No | No | Yes |
| Gateway failover | No | No | Yes |
| LDAP/OIDC/SAML settings | No | No | Yes |
| Enterprise monitoring/alerts | No | No | Yes |

## Upgrade path

```text
Base 1.1  ->  Pro 2.0  ->  Enterprise 3.0
```

1. **Base to Pro:** back up, move to Ubuntu 24.04, deploy the 2.0 Pro line, run
   the Pro migration and acceptance checks. Data is preserved.
2. **Pro to Enterprise:** keep the Pro control plane and data, add the
   Enterprise topology: shared storage, replicated API/frontend, PostgreSQL HA,
   Redis HA, gateway pair, and the lab-node pool.
3. **Enterprise to Base/Pro:** drain the pool, stop new placement, export data,
   and return to the single-host Pro path. There is no in-place downgrade of the
   database; restore from the pre-Enterprise backup if the schema is not
   backward compatible.

## Support policy

- **Base 1.1** is the maintenance line. Security and correctness fixes land
  here first and merge forward.
- **Pro 2.0** is the current feature line for teaching analytics and reporting.
- **Enterprise 3.0** is the HA/identity line. It carries the Pro feature set plus
  enterprise deployment controls.
- A fix does not create a separate fork. It lands on the earliest affected
  edition and merges forward.

## Licensing

The edition names describe deployment scope. They do not change the repository
licence. OpenCyberRange remains under the PolyForm Noncommercial License 1.0.0;
commercial use, resale, and paid hosting require a separate commercial licence
from the copyright holder. Do not market an edition as a commercial offering
without that licence.

## Decision record

The edition model is recorded in
[`decisions/0002-edition-model.md`](decisions/0002-edition-model.md). Any change
to the boundaries needs a written update to this page and the affected charter.
