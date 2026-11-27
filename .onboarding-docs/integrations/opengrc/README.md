# OpenGRC

## Purpose

OpenGRC is the system of record for governance, risk, compliance, controls,
audits, exceptions, and evidence requests. OpenCyberRange produces aggregate
teaching and competency evidence and exports it; it does not duplicate the GRC
database.

## Evidence contract

Send:

- stable identifiers (control/framework reference, platform object id)
- a content hash
- the reporting period
- aggregate counts above the small-cohort threshold
- the platform release and signed tag

Never send:

- learner rows
- names, emails, or student IDs
- PCAP, payloads, or lab artifacts
- AI prompts or model memory

## First integration

1. Choose one framework and a small control set.
2. Map one track or capstone to those controls.
3. Define the export schema.
4. Add a boundary test proving zero learner rows leave the platform.
5. Publish the first Training-to-Control mapping, then widen.

## Deployment

`opengrc-prod` is a separate host. The Prometheus/Grafana stack in
`deploy/monitoring/` runs there, not on the OCR platform host. Do not point the
dev-only `deploy/ecosystem-test/` stack at production or give it production
credentials.

## Publication controls

`PUB-001` through `PUB-004` live in OpenGRC and are consumed by
OpenDiscoveryEngine. The OCR publication audit stays aligned; do not create a
second source of truth.

## Tests and evidence

- A boundary test that scans an export for learner identifiers.
- A hash and period check.
- A control/framework reference check.
- A release and signed-tag check.

## Related

- [Ecosystem tooling map](../../../docs/ECOSYSTEM-TOOLING-MAP.md)
- [Reporting roadmap](../../../docs/REPORTING-ROADMAP.md)
- [Compliance](../../../docs/COMPLIANCE.md)
- [Backend analytics and reports](../../backend/features/analytics-and-reports/README.md)
