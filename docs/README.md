# Documentation index

Start with the source of truth, then choose the section that matches your role.
The signed tag and [`versions.yaml`](../versions.yaml) win over any page.

## Start here

| Document | Use it for |
|---|---|
| [Production deployment statement](PRODUCTION-DEPLOYMENT-STATEMENT.md) | The deployed release, cutover state, and evidence |
| [Deployment runbook](DEPLOYMENT-RUNBOOK.md) | Operating the development and production hosts |
| [Validation report](VALIDATION-REPORT.md) | Reproducible test, build, lab, and smoke evidence |
| [Lab and content counts](COUNTS.md) | The canonical 210-lab definitions and counts |
| [Deployment topology and sizing](DEPLOYMENT-TOPOLOGY-AND-SIZING.md) | Supported shape, ports, and database budget |

## Browse by area

- [Architecture](architecture/index.md)
- [Operations](operations/index.md)
- [Curriculum and assessment](curriculum/index.md)
- [Security](security/index.md)
- [Integrations](integrations/index.md)
- [Compliance and procurement](compliance/index.md)
- [Archive](archive/README.md)

## Release and governance

- [Release tags](RELEASES.md)
- [Changelog](../CHANGELOG.md)
- [Contributors and branches](CONTRIBUTORS-AND-BRANCHES.md)
- [Editions](EDITIONS.md) and [supported versions](SUPPORTED-VERSIONS.md)
- [Security policy](../SECURITY.md), [privacy summary](../PRIVACY.md), and
  [code of conduct](../CODE_OF_CONDUCT.md)
- [Contributing](../CONTRIBUTING.md), [support](../SUPPORT.md), and
  [licensing](../LICENSING.md)
- [Repository hygiene](REPOSITORY-HYGIENE.md) and
  [MkDocs governance](MKDOCS-GOVERNANCE.md)
- [Open-source readiness](OPEN-SOURCE-READINESS.md)

## Architecture and security

- [Architecture](ARCHITECTURE.md)
- [Authorization service](AUTHORIZATION-SERVICE.md) and [RBAC/PBAC](RBAC-PBAC.md)
- [Tenant isolation status](TENANT-ISOLATION-STATUS.md)
- [Security events](SECURITY-EVENTS.md) and [auth lifecycle](AUTH-LIFECYCLE.md)
- [Database integrity](DATABASE-INTEGRITY.md) and [migrations](DATABASE-MIGRATIONS.md)
- [Supply chain](SUPPLY-CHAIN.md)
- [Backup and restore testing](BACKUP-RESTORE-TEST.md)
- [Independent security testing](INDEPENDENT-SECURITY-TESTING.md)

## Curriculum and assessment

- [Learning framework](LEARNING-FRAMEWORK.md)
- [Lab metadata schema](LAB-METADATA-SCHEMA.md) and [lab outcomes](LAB-OUTCOMES.md)
- [Competency contracts](COMPETENCY-CONTRACTS.md)
- [Active Directory pathway](ACTIVE-DIRECTORY-PATHWAY.md)
- [Modern application-security pathway](MODERN-APP-SECURITY-PATHWAY.md)
- [DFIR pathway](DFIR-PATHWAY.md) and [detection engineering](DETECTION-ENGINEERING-PATHWAY.md)
- [Content gap analysis](CONTENT-GAP-ANALYSIS.md)
- [Curriculum drift report](CURRICULUM-DRIFT-REPORT.md)

## Privacy and data protection

- [Privacy notice](PRIVACY-NOTICE.md)
- [Privacy and data deletion](PRIVACY-AND-DATA-DELETION.md)
- [Data classification](DATA-CLASSIFICATION.md) and [data labels](DATA-LABELS.md)
- [Consent revocation](CONSENT-REVOCATION.md) and [retention policies](RETENTION-POLICIES.md)
- [Survey privacy](SURVEY-PRIVACY.md)
- [Data processing agreement template](DPA-TEMPLATE.md)

## Operations and procurement

- [OS support](OS-SUPPORT.md) and [browser matrix](BROWSER-MATRIX.md)
- [Deployment status](status-dashboard.md)
- [Procurement requirements](PROCUREMENT-REQUIREMENTS.md) and [compliance](COMPLIANCE.md)
- [HECVAT](HECVAT.md)
- [Manual screenshots](MANUAL-SCREENSHOTS.md)

## Historical records

These are retained for provenance. They are not current operating guidance.

- [Release 4 close-out](archive/RELEASE-4-CLOSE-OUT.md)
- [Repository cutover](archive/CUTOVER-TO-CANONICAL-REPO.md)
- [Upgrade to latest GA plan](archive/UPGRADE-TO-LATEST-GA-PLAN.md)
- [2.7.0 plan](archive/2.7.0-PLAN.md)
- The `docs/reviews/` directory (dated review and demo-data records)

For a full list, browse the directory or the MkDocs navigation in
[`mkdocs-manual-lite.yml`](../mkdocs-manual-lite.yml).
