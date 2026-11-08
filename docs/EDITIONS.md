# SWOCTS Cyber Range editions

SWOCTS Cyber Range is powered by OpenCyberRange.

Status: **Active product model**

OpenCyberRange has three cumulative editions. The edition names describe scope
and operational shape, not three separate codebases. Each edition builds on the
previous one.

One platform release number covers this tree. Edition names select scope and
entitlement; they are not separate version lines. See
[ADR 0004](decisions/0004-single-platform-release-version.md).

| Edition profile | Platform release | Status | Shape | Primary user |
|---|---|---|---|---|
| **Community / Academic** | 2.5.2 (1.1.3 maintenance line) | Supported profile | Single-host Docker Compose teaching platform | Instructor, classroom, self-hosted operator |
| **Professional** | 2.5.2 | Release profile � analytics preview | Community / Academic plus analytics, reporting, cohort analysis, accreditation support, and research exports | Programme lead, teaching team, analyst |
| **Enterprise** | 2.5.2 preview | Development profile | Professional plus HA, SSO, enterprise reporting, multi-tenant support, LMS integration, and regulatory reporting | Institution, IT operations, multi-cohort deployment |

## Edition boundaries

### Community / Academic profile

Community / Academic is the supported teaching platform profile. The 1.1.3
maintenance line remains available for existing installs; new installs use the
2.5.2 tree with this profile.

- courses, exercises, tracks, labs, RangeBox, flags, hints, and achievements;
- lab improvements and workbook improvements;
- exercise authoring;
- profiles, certificates, transcripts, and events;
- single-host Docker Compose deployment on Ubuntu 22.04 or 24.04;
- WireGuard learner access, backups, privacy, erasure, and mail settings;
- bug fixes, maintenance, and security updates.

Community / Academic is the reference behaviour. Professional and Enterprise
must not regress it.

### Professional profile

Professional adds the teaching intelligence and evidence layer on the same
single-host deployment and 2.5.2 platform release. The Professional and Enterprise priority set is:

1. **Competency Framework Engine** � explicit competency definitions, mappings,
   evidence rules, and progression levels.
2. **Student Feedback Engine** � structured, consent-aware feedback tied to
   exercises, tracks, and competencies.
3. **Radar / Spider Web Reporting** � competency profiles for learners, cohorts,
   and programmes.
4. **Exercise Health Analytics** � which labs are failing, where learners
   abandon, and which exercises need authoring attention.
5. **Instructor Intervention Dashboard** � early, explainable support signals
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

### Enterprise profile (preview)

Enterprise is a preview profile on 2.5.2 until the HA workstream ships. It adds
the deployment, identity, and institutional layer:

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

The matrix shows current delivery status by profile: **Delivered**, **Partial**, or **Planned**. Scope boundaries are described above.

| Capability | Community / Academic profile | Professional profile | Enterprise preview |
|---|---:|---:|---:|
| Courses, labs, RangeBox, flags, hints | Yes | Yes | Yes |
| Lab and workbook improvements | Yes | Yes | Yes |
| Exercise authoring | Yes | Yes | Yes |
| Profiles, certificates, transcripts | Yes | Yes | Yes |
| Events and achievements | Yes | Yes | Yes |
| Single-host Docker Compose | Yes | Yes | Yes |
| Ubuntu 22.04 support | Yes | Maintenance reference | No |
| Ubuntu 24.04 support | Yes | Yes | Yes |
| Educational analytics | No | Partial | Partial |
| Reporting and instructor dashboards | No | Delivered | Delivered |
| Cohort analysis | No | Planned | Planned |
| Competency Framework Engine | No | Planned | Planned |
| Student Feedback Engine | No | Planned | Planned |
| Radar / Spider Web Reporting | No | Partial | Partial |
| Exercise Health Analytics | No | Planned | Planned |
| Instructor Intervention Dashboard | No | Planned | Planned |
| Accreditation support | No | Planned | Planned |
| Research exports | No | Partial | Partial |
| Multi-host lab pool and control-plane HA | No | No | Planned |
| Gateway failover | No | No | Planned |
| LDAP / OIDC / SAML single sign-on | No | No | Partial |
| Enterprise reporting | No | No | Planned |
| Multi-tenant support | No | No | Planned |
| LMS integration | No | No | Planned |
| Regulatory and compliance reporting | No | No | Planned |

## Delivery status

The matrix describes edition scope, not shipped capability. Current delivery:

| Item | State |
|---|---|
| Community / Academic profile on 2.5.2 | Delivered and supported |
| Community / Academic 1.1.3 maintenance line | Supported for existing installs |
| Professional analytics and course reporting | Delivered |
| Professional Competency Framework Engine | Planned |
| Professional Student Feedback Engine | Delivered: opt-in course check-ins, exercise pulse, two-way coaching, and course health summary |
| Professional Radar / Spider Web Reporting | Partially delivered: course and all-course skill-tree radar in Learning reports; learner/cohort competency radar planned |
| Professional Exercise Health Analytics | Partially delivered: course exercise drill-down and prioritized course-health actions; programme report planned |
| Professional Instructor Intervention Dashboard | Partially delivered: private coaching notes and course-health actions; early support signals planned |
| Professional cohort analysis | Planned |
| Professional accreditation support | Planned |
| Professional research exports | Partially delivered (cross-course CSV/PDF and survey package) |
| Enterprise preview HA | Design complete in the private HA repository; not deployed |
| Enterprise preview SSO | Settings-only on the `v3` branch; login flows not implemented |
| Enterprise preview reporting, multi-tenancy, LMS, compliance reporting | Planned |

## Upgrade path

```text
Community / Academic profile  ->  Professional profile  ->  Enterprise preview
                 all on platform release 2.5.2
```

1. **Community / Academic to Professional:** back up, move to Ubuntu 24.04,
   deploy the 2.5.2 Professional profile, run the Professional migration and
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

- **Community / Academic 1.1.3** is the maintenance line for existing installs.
  Security and correctness fixes land here first and merge forward.
- **Community / Academic, Professional, and Enterprise** are profiles on platform
  release **2.5.2**. Release tags identify the platform release, not an edition.
- **Enterprise is a preview profile** until HA, SSO, multi-tenancy, LMS, and
  compliance reporting are shipped and verified. The separate HA repository has
  its own version and a compatibility statement, not a platform version.
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
[`decisions/0002-edition-model.md`](decisions/0002-edition-model.md), the
naming and scope refinement in
[`decisions/0003-edition-scope-refinement.md`](decisions/0003-edition-scope-refinement.md),
and the single-release-number decision in
[`decisions/0004-single-platform-release-version.md`](decisions/0004-single-platform-release-version.md).
Any change to the boundaries needs a written update to this page and the
affected charter.
