# Integrations and ecosystem

The platform is one part of a wider teaching and governance ecosystem. The
integration boundary is deliberately narrow: the platform owns its learner and
lab data; other systems own their domains.

## Systems

| System | Owns | Integration |
|---|---|---|
| OpenGRC | Governance, risk, control catalogue, audits, evidence requests | Aggregate evidence, stable IDs and hashes |
| OpenDetectionEngine / OpenDLP | Data sources, classifiers, DLP policy | Discovery and classification evidence |
| DefectDojo | Findings, deduplication, remediation | Finding references |
| Authentik | Operational SSO for the ecosystem | OIDC/SAML provider (ADR 0006) |
| OpenIAM | Identity governance and access certification | Identity lifecycle evidence |
| Moodle | Course delivery and LTI consumer | LTI 1.3 launch and deep linking |
| Monitoring | Prometheus/Grafana on a separate host | Metrics scrape |

## Rules

- One connector at a time; start with one framework and a small control set.
- Export stable identifiers and hashes, not a copy of the other system's tables.
- Send aggregate evidence only. No learner rows, PCAP, or payloads cross the
  boundary.
- Read-only and aggregate by default.
- Publication controls `PUB-001` through `PUB-004` live in OpenGRC; the platform
  consumes them, it does not duplicate them.
- `deploy/ecosystem-test/` is a dev-only synthetic stack. Never point it at
  production or give it production credentials.

## Pages

- [Integration diagram](subsystem-technical-architecture-diagram.md)
- [SSO](sso/README.md)
- [LTI](lti/README.md)
- [OpenGRC](opengrc/README.md)

## Related

- [Ecosystem tooling map](../../docs/ECOSYSTEM-TOOLING-MAP.md)
- [Reporting roadmap](../../docs/REPORTING-ROADMAP.md)
- [ADR 0006 identity platform roles](../../docs/decisions/0006-identity-platform-roles.md)
- [Backend SSO and LTI](../backend/features/sso-and-lti/README.md)
