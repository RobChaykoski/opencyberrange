# OpenIAM test stack (dedicated dev lab host)

OpenIAM is the identity-governance layer in the ecosystem. This page explains
why it is fetched but not auto-started by the training stack, and how to run it
on a host set aside for the identity lab.

## Why it is separate

OpenIAM's official deployment is a set of **Docker Swarm stacks**:

- infrastructure: MariaDB/PostgreSQL, Redis, RabbitMQ, OpenSearch, Vault, Consul
- core services: ESB, workflow, IDM, groovy manager, audit log, synchronization,
  reconciliation, email manager
- UI: Tomcat with webconsole, IdP, and self-service
- reverse proxy

It also generates a Vault CA/key pair and expects a dedicated resource budget.
Initialising Swarm on the shared OpenCyberRange dev host would change that host's
Docker mode for every other workload, so the training seed does not do it.

## Prerequisites

- A dedicated Linux dev lab host with Docker.
- Enough CPU, RAM, and disk for the full stack; check the official OpenIAM
  README for the current minimums.
- No production network, identity provider, or data.

## Start

```bash
# on the dedicated lab host only
bash scripts/fetch-openiam-test-stack.sh
bash scripts/run-openiam-test-stack.sh
```

`run-openiam-test-stack.sh` refuses to continue unless Swarm is already active.
If it is not, the script prints the exact commands:

```bash
docker swarm init
cd deploy/ecosystem-test/openiam
export OPENIAM_RPROXY_HTTP=1
./generate.cert.sh
./setup.sh
./startup.sh
```

Use the OpenIAM web console to create fake users, roles, and one fake
access-review campaign. Do not connect it to production LDAP, Active Directory,
HR, or any real identity source.

## Teardown

```bash
cd deploy/ecosystem-test/openiam
./shutdown.sh
./teardown.sh
docker swarm leave --force   # only on the dedicated lab host
```

## Integration boundary

- Authentik remains the operational SSO platform.
- OpenIAM owns lifecycle, provisioning, access review, certification, and
  segregation of duties.
- Keycloak remains an advanced IAM lab.
- OpenCyberRange, OpenGRC, OpenDetectionEngine, and OpenEMR consume aggregate
  governance evidence, never raw identity records.
