# OpenCyberRange editions

Status: **Active product model**

OpenCyberRange has three cumulative editions. The edition names describe scope
and operational shape, not three separate codebases. Each edition builds on the
previous one.

| Edition | Version line | Shape | Primary user |
|---|---|---|---|
| **Community / Academic** | 1.1.x | Single-host Docker Compose teaching platform | Instructor, classroom, self-hosted operator |
| **Professional** | 2.1.x | Community / Academic plus analytics, reporting, cohort analysis, accreditation support, and research exports | Programme lead, teaching team, analyst |
| **Enterprise** | 3.0.x | Professional plus HA, SSO, enterprise reporting, multi-tenant support, LMS integration, and regulatory reporting | Institution, IT operations, multi-cohort deployment |

## Edition boundaries

### Community / Academic â€” 1.1

Community / Academic is the supported, stable teaching platform:

- courses, exercises, tracks, labs, RangeBox, flags, hints, and achievements;
- lab improvements and workbook improvements;
- exercise authoring;
- profiles, certificates, transcripts, and competitions;
- single-host Docker Compose deployment on Ubuntu 22.04 or 24.04;
- WireGuard learner access, backups, privacy, erasure, and mail settings;
- bug fixes, maintenance, and security updates.

Community / Academic is the reference behaviour. Professional and Enterprise
must not regress it.

### Professional â€” 2.0

Professional adds the teaching intelligence and evidence layer on the same
single-host deployment. The Professional and Enterprise priority set is:

1. **Competency Framework Engine** â€” explicit competency definitions, mappings,
   evidence rules, and progression levels.
2. **Student Feedback Engine** â€” structured, consent-aware feedback tied to
   exercises, tracks, and competencies.
3. **Radar / Spider Web Reporting** â€” competency profiles for learners, cohorts,
   and programmes.
4. **Exercise Health Analytics** â€” which labs are failing, where learners
   abandon, and which exercises need authoring attention.
5. **Instructor Intervention Dashboard** â€” early, explainable support signals
   for instructors.

Professional also carries:

- educational analytics and cohort analysis;
- reporting, instructor dashboards, and teaching-review signals;
- accreditation support;
- research exports for approved, de-identified studies;
- the 24.04 single-host baseline;
- the OWASP Top 10 security baseline and release evidence.

The five priority capabilities are **Professional and Enterprise only**. They
are not Community / Academic features.

Professional is not a multi-host or identity-federation product. It remains a
single Docker host and does not add SSO, multi-tenancy, LMS integration, or
distributed scheduling.

### Enterprise â€” 3.0

Enterprise adds the deployment, identity, and institutional layer:

- multi-host lab pool with capacity-aware placement;
- central session `/24` allocation and VPN gateway route reconciliation;
- node agent, mTLS control channel, drain, node-loss recovery, and reconciliation;
- replicated frontend/API, PostgreSQL HA, Redis HA, shared object storage;
- WireGuard gateway failover;
- LDAP, OIDC, and SAML single sign-on;
- enterprise reporting and regulatory/compliance reporting;
- multi-tenant support;
- LMS integration;
- enterprise monitoring, alerting, and operational runbooks.

Enterprise depends on Professional. It does not replace the single-host path,
which remains the default and fallback.

## Feature matrix

| Capability | Community / Academic 1.1 | Professional 2.0 | Enterprise 3.0 |
|---|---:|---:|---:|
| Courses, labs, RangeBox, flags, hints | Yes | Yes | Yes |
| Lab and workbook improvements | Yes | Yes | Yes |
| Exercise authoring | Yes | Yes | Yes |
| Profiles, certificates, transcripts | Yes | Yes | Yes |
| Competitions and achievements | Yes | Yes | Yes |
| Single-host Docker Compose | Yes | Yes | Yes |
| Ubuntu 22.04 support | Yes | Maintenance reference | No |
| Ubuntu 24.04 support | Yes | Yes | Yes |
| Educational analytics | No | Yes | Yes |
| Reporting and instructor dashboards | No | Yes | Yes |
| Cohort analysis | No | Yes | Yes |
| Competency Framework Engine | No | Yes | Yes |
| Student Feedback Engine | No | Yes | Yes |
| Radar / Spider Web Reporting | No | Yes | Yes |
| Exercise Health Analytics | No | Yes | Yes |
| Instructor Intervention Dashboard | No | Yes | Yes |
| Accreditation support | No | Yes | Yes |
| Research exports | No | Yes | Yes |
| Multi-host lab pool and control-plane HA | No | No | Yes |
| Gateway failover | No | No | Yes |
| LDAP / OIDC / SAML single sign-on | No | No | Yes |
| Enterprise reporting | No | No | Yes |
| Multi-tenant support | No | No | Yes |
| LMS integration | No | No | Yes |
| Regulatory and compliance reporting | No | No | Yes |

## Delivery status

The matrix describes edition scope, not shipped capability. Current delivery:

| Item | State |
|---|---|
| Community / Academic 1.1 core platform | Delivered and supported |
| Professional 2.0 analytics and course reporting | Delivered on the 24.04 preview |
| Professional 2.0 Competency Framework Engine | Planned |
| Professional 2.0 Student Feedback Engine | Planned |
| Professional 2.0 Radar / Spider Web Reporting | Partially delivered: course and all-course skill-tree radar in Learning reports; learner/cohort competency radar planned |
| Professional 2.0 Exercise Health Analytics | Planned |
| Professional 2.0 Instructor Intervention Dashboard | Planned |
| Professional 2.0 cohort analysis | Planned |
| Professional 2.0 accreditation support | Planned |
| Professional 2.0 research exports | Partially delivered (cross-course CSV/PDF and survey package) |
| Enterprise 3.0 HA | Design complete in the private HA repository; not deployed |
| Enterprise 3.0 SSO | Settings-only on the `v3` branch; login flows not implemented |
| Enterprise 3.0 enterprise reporting, multi-tenancy, LMS, compliance reporting | Planned |

## Upgrade path

```text
Community / Academic 1.1  ->  Professional 2.0  ->  Enterprise 3.0
```

1. **Community / Academic to Professional:** back up, move to Ubuntu 24.04,
   deploy the 2.0 Professional line, run the Professional migration and
   acceptance checks. Data is preserved.
2. **Professional to Enterprise:** keep the Professional control plane and
   data, add the Enterprise topology: shared storage, replicated API/frontend,
   PostgreSQL HA, Redis HA, gateway pair, identity provider, and the lab-node
   pool.
3. **Enterprise to Professional / Community / Academic:** drain the pool, stop
   new placement, export data, and return to the single-host Professional path.
   There is no in-place downgrade of the database; restore from the
   pre-Enterprise backup if the schema is not backward compatible.

## Support policy

- **Community / Academic 1.1** is the maintenance line. Security and
  correctness fixes land here first and merge forward.
- **Professional 2.0** is the current feature line for teaching analytics,
  reporting, cohort analysis, accreditation support, and research exports.
- **Enterprise 3.0** is the HA, identity, multi-tenancy, LMS, and compliance
  line. It carries the Professional feature set plus enterprise deployment
  controls.
- A fix does not create a separate fork. It lands on the earliest affected
  edition and merges forward.

## Licensing

The edition names describe deployment scope. They do not change the repository
licence. OpenCyberRange remains under the PolyForm Noncommercial License 1.0.0;
commercial use, resale, and paid hosting require a separate commercial licence
from the copyright holder. "Community / Academic", "Professional", and
"Enterprise" are not commercial licence grants. Do not market an edition as a
commercial offering without that licence.

## Decision records

The edition model is recorded in
[`decisions/0002-edition-model.md`](decisions/0002-edition-model.md). The
naming and scope refinement is recorded in
[`decisions/0003-edition-scope-refinement.md`](decisions/0003-edition-scope-refinement.md).
Any change to the boundaries needs a written update to this page and the
affected charter.
