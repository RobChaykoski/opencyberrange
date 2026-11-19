---
name: ecosystem-tooling-and-reporting
description: Place shared security, identity, network, platform, privacy, and reporting tools across OpenCyberRange, OpenGRC, OpenDetectionEngine/OpenDLP, and OpenEMR/DRButler. Use when deciding which project owns a tool, how a report should be scoped by role, or how to keep evidence and visual language consistent across the ecosystem.
argument-hint: "[tool or report]"
license: MIT
metadata:
  author: OpenCyberRange
  version: "1.0.0"
---

# Ecosystem tooling and reporting

Use this skill when a tool, report, or design pattern could belong to more than
one project. Start with the project's primary job; do not duplicate a control or
a source of truth across projects.

## Project ownership

| Project | Primary job |
|---|---|
| OpenCyberRange | Teaching, labs, NICE mapping, readiness evidence |
| OpenGRC | Governance, risk, compliance, control evidence, audits |
| OpenDetectionEngine / OpenDLP | Data discovery, classification, DLP |
| OpenEMR / DRButler | Clinical operations, PHI protection, clinician workflow |
| Ralph | Asset inventory and ownership |
| Fleet | Endpoint posture and compliance |

## Tool routing

- **Authentik** is the operational SSO platform for all projects.
- **Keycloak** is the advanced federation/IAM lab and reference environment.
- **OpenIAM** owns identity governance: lifecycle, provisioning, access review,
  certification, and segregation of duties.
- **NetBox + Ralph** hold network and asset source-of-truth data.
- **LibreNMS, Oxidized, NAPALM, Open vSwitch, Mininet, OPNsense/pfSense,
  PacketFence** are network engineering tools. OCR teaches them; Ralph and
  OpenGRC consume their inventory and control evidence.
- **Wazuh, Suricata, Zeek, Sysmon, Security Onion, Fail2Ban, Lynis** are SOC and
  endpoint tools. OCR teaches them; Fleet and OpenGRC consume posture and
  control evidence.
- **OpenVAS, Nessus, Nikto, OWASP ZAP** are vulnerability-management tools. OCR
  teaches them; OpenGRC consumes remediation and control evidence; OpenEMR
  consumes clinical web-app exposure evidence.
- **Docker, Kubernetes, Cilium, Calico, Istio, GitHub Actions, GitLab CI,
  SonarQube, OWASP Dependency-Check, ScanCode** are platform and supply-chain
  tools. OCR teaches them; every project uses the CI gates.
- **OpenDLP** classifies data; OpenGRC consumes privacy controls; OCR uses the
  labels on exports; OpenEMR uses them for PHI.

## Report boundaries

Use the same five audiences everywhere:

- Privacy office: aggregate inventory, consent, retention, erasure, minors,
  processors, classification.
- Auditor: evidence-bound manifests, access review, change ledger, control
  coverage, exceptions.
- Mentor: assigned learners only.
- Teaching assistant: assigned course only.
- Administrator: platform health, backups, security events, tenant isolation,
  access inventory.

Never let a report make a grade, admission, employment, or disciplinary
decision. Suppress small cells, label exports, and audit access.

## Design rules

- Summary first, detail on request.
- Use the host project's component system. Share tokens and guidance, not a
  foreign CSS framework.
- Keep privacy and audit views quiet, dense, and evidence-led.
- Make every report accessible by keyboard, screen reader, colour, and small
  screen.
- Every export carries purpose, owner, audience, retention, and classification.

## Where to look

- `docs/ECOSYSTEM-TOOLING-MAP.md` — full tool/project matrix.
- `docs/ROLE-CAPABILITY-MODEL.md` — role skills and report access.
- `docs/REPORTING-ROADMAP.md` — report tiers and acceptance criteria.
- `docs/NICE-FRAMEWORK-INGESTION.md` — mapping and review queue.
- `docs/CURRICULUM-TRACKS-2027.md` — track scaffolds.
