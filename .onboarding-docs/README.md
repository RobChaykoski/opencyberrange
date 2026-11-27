# Developer onboarding

This guide is for a software engineer joining the SWOCTS Cyber Range project
(powered by OpenCyberRange). It explains what the platform does, how it is
deployed, which frameworks and services are involved, and how to work on each
subsystem safely.

Start here, then open the subsystem that matches your task.

| If you need to... | Read |
|---|---|
| Understand the product, users, and constraints | [Platform overview](platform-overview.md) |
| See the whole system at a glance | [Platform technical architecture](platform-technical-architecture-diagram.md) |
| Run the platform on your machine | [Local development](local-development.md) |
| Run tests and the quality gates | [Testing and quality gates](testing-and-quality-gates.md) |
| Work on the API | [Backend](backend/subsystem-overview.md) |
| Work on the web app | [Frontend](frontend/subsystem-overview.md) |
| Change schema or data | [Database](database/subsystem-overview.md) |
| Change deployment, ports, or volumes | [Deployment](deployment/subsystem-overview.md) |
| Work on labs, sessions, or RangeBox | [Lab runtime](lab-runtime/subsystem-overview.md) |
| Work on SSO, LTI, or OpenGRC | [Integrations](integrations/subsystem-overview.md) |
| Work on HA or standby services | [HA](ha/subsystem-overview.md) |
| Work on metrics or alerting | [Monitoring](monitoring/subsystem-overview.md) |
| Run the blackbox security suite | [Security tests](security-tests/README.md) |

## Source of truth

| Question | Authoritative source |
|---|---|
| Release and stack versions | [`versions.yaml`](../versions.yaml) |
| Runtime shape | [`platform/docker-compose.prod.yml`](../platform/docker-compose.prod.yml) |
| Environment variables | [`platform/.env.example`](../platform/.env.example) |
| Architecture decisions | [`docs/decisions/`](../docs/decisions/) |
| Lab catalogue and counts | [`platform/labs/`](../platform/labs/) and [`docs/COUNTS.md`](../docs/COUNTS.md) |
| Curriculum order | [`curriculum-manifest.yaml`](../curriculum-manifest.yaml) |
| Competency mapping | [`curriculum-frameworks.yaml`](../curriculum-frameworks.yaml) and [`platform/backend/app/data/`](../platform/backend/app/data/) |
| Security and privacy rules | [`SECURITY.md`](../SECURITY.md), [`PRIVACY.md`](../PRIVACY.md), [`docs/DATA-CLASSIFICATION.md`](../docs/DATA-CLASSIFICATION.md) |

## What this guide is not

- It is not a replacement for the deployment runbook or the release procedure.
- It does not grant production access. Development and test fixtures are
  clearly labelled and must never be copied to production.
- It does not repeat every API endpoint. Each feature page names the router and
  service where the contract lives.

## Repository map

```text
opencyberrange-next/
├── platform/
│   ├── backend/            FastAPI application, models, services, seed scripts
│   ├── frontend/           Vue 3 + Vite single-page app and nginx edge config
│   ├── labs/               Lab definitions, compose files, shared targets
│   ├── tester/             Lab solver manifests and tester image
│   ├── templates/          Exercise Studio templates
│   ├── wiki-builder/       MkDocs build container
│   ├── docker-compose.*.yml
│   └── .env.example
├── Workbook/               Learner-facing Markdown and generated curriculum pages
├── deploy/                 SSO, monitoring, Moodle, ecosystem test stacks
├── docs/                   Design, operations, security, compliance, and reviews
├── scripts/                Validation, generation, deployment, and test tooling
├── security-tests/karate/  Blackbox security and privacy suite
└── versions.yaml
```

## First-day checklist

1. Read [Platform overview](platform-overview.md) and the
   [architecture diagram](platform-technical-architecture-diagram.md).
2. Get the stack running with [Local development](local-development.md).
3. Run the backend and frontend tests in
   [Testing and quality gates](testing-and-quality-gates.md).
4. Open your subsystem page and the feature pages you will touch.
5. Read the non-negotiables in the workspace bootstrap
   (`.opencode/bootstrap.md`, outside this repository) before changing
   deployment, security, consent, or learner data.
