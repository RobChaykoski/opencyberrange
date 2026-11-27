# Architecture

How the platform is put together and where its trust boundaries are.

| Document | Use it for |
|---|---|
| [Architecture](../ARCHITECTURE.md) | Services, data flow, and STRIDE/DREAD review |
| [Authorization service](../AUTHORIZATION-SERVICE.md) | The single authorization decision point |
| [RBAC and PBAC](../RBAC-PBAC.md) | Roles, permissions, and policy checks |
| [Tenant isolation status](../TENANT-ISOLATION-STATUS.md) | Enforced RLS tables and the classified remainder |
| [Auth lifecycle](../AUTH-LIFECYCLE.md) | Sessions, refresh tokens, MFA, and re-authentication |
| [Database integrity](../DATABASE-INTEGRITY.md) | Checksums, the change ledger, and quality audits |
| [Database migrations](../DATABASE-MIGRATIONS.md) | Revision policy and the migration chain |
| [Data dictionary](../DATA-DICTIONARY.md) | Every table and its owner |
| [Supply chain](../SUPPLY-CHAIN.md) | Lock, signatures, and release inputs |
| [Deployment topology and sizing](../DEPLOYMENT-TOPOLOGY-AND-SIZING.md) | Supported shape and capacity |
| [Scaling and hardening roadmap](SCALING-ROADMAP.md) | Single-host hardening, worker nodes, microVMs, registry, and telemetry |
| [Network sandbox](../NETWORK-SANDBOX.md) | Lab isolation and firewall model |
| [Device topology](../DEVICE-TOPOLOGY.md) | Host, container, and lab network layout |
| [KasmVNC](../KASMVNC.md) | The browser desktop transport |
| [Reverse proxy](../REVERSE-PROXY.md) | TLS, headers, and origin layout |
| [Wiki origin split](../WIKI-ORIGIN-SPLIT.md) | The separate 8443 workbook origin |
