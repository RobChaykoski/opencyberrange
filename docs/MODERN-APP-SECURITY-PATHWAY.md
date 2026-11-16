# Modern application security pathway

This pathway extends the Web and Software Security tracks into API, GraphQL,
JWT, OAuth/OIDC, DevSecOps, containers, Kubernetes, and software-supply-chain
security. The source of truth is
`platform/backend/app/data/modern-appsec-pathway.yaml`.

## Why this pathway

The Web track covers reconnaissance and classic web exploitation. Modern
applications add API contracts, GraphQL schemas, token flows, CI/CD pipelines,
containers, Kubernetes RBAC, and artifact provenance. Each of those is a
different trust boundary, and each needs its own evidence and remediation.

## Progression

| Module | Title | Level | Minutes | Focus |
|---|---|---|---|---|
| MAS-01 | API Security Foundations and Inventory | beginner | 60 | routes, methods, auth, object IDs |
| MAS-02 | API Authorization: BOLA and BFLA | intermediate | 90 | object and function authorization |
| MAS-03 | GraphQL Security | intermediate | 100 | schema, introspection, depth, field auth |
| MAS-04 | JWT Security | intermediate | 90 | signature, claims, expiry, revocation |
| MAS-05 | OAuth and OIDC Abuse | advanced | 120 | redirect URI, PKCE, state, consent |
| MAS-06 | DevSecOps and CI/CD Security | intermediate | 100 | workflow permissions, secrets, provenance |
| MAS-07 | Container Security | intermediate | 100 | image, user, capabilities, runtime |
| MAS-08 | Kubernetes Security | advanced | 140 | RBAC, service accounts, network policy |
| MAS-09 | Supply Chain and Artifact Integrity | intermediate | 90 | SBOM, signing, dependency risk |
| MAS-10 | Capstone: Modern Application Security Assessment | advanced | 180 | evidence pack and remediation |

## Lab targets

- The pinned OWASP Juice Shop image for API, token, and application behaviour.
- The platform API for inventory, authorization, rate-limit, and misconfiguration review.
- Local mocks for GraphQL, OAuth, CI/CD, containers, Kubernetes, and supply-chain exercises.
- No real tenant, registry, cloud account, or public target is used.

See [`JUICE-SHOP-LABS.md`](JUICE-SHOP-LABS.md) for the image digest and isolation
rules, [`API-SECURITY-LABS.md`](API-SECURITY-LABS.md) for the API sequence, and
[`OWASP-SECURITY-BASELINE.md`](OWASP-SECURITY-BASELINE.md) for the control
matrix.

## Evidence contract

Every module requires:

- the request, schema, manifest, image, or pipeline that supports the finding;
- the authorization or design decision and its reason;
- the blast radius in the lab context;
- a preventive or detective control;
- a verification step or regression test.

A solved challenge or a tool screenshot alone is not evidence.

## Safety

- No denial-of-service or resource-exhaustion testing against a shared service.
- No real tokens, secrets, tenant IDs, or personal data.
- No public registry pushes, cloud account changes, or shared-cluster tests.
- Use a disposable namespace or local cluster for Kubernetes.
- Use only the pinned lab image and local mocks.

## Existing and planned labs

Existing:

- `web-2-2-insecure-api-endpoints`
- `web-2-4-api-enumeration-gauntlet`
- `identity-1-2-oauth-oidc-sso`
- `software-security-1-1-hidden-export-route`

Planned:

- `web-11-1-api-inventory`
- `web-11-2-api-bola-bfla`
- `web-11-3-graphql-security`
- `web-11-4-jwt-security`
- `web-11-5-oauth-abuse`
- `web-11-6-devsecops-pipeline`
- `web-11-7-container-security`
- `web-11-8-kubernetes-security`
- `web-11-9-supply-chain-integrity`
- `web-11-10-modern-appsec-capstone`

## Validation

`platform/backend/tests/test_modern_appsec_pathway.py` checks ordering,
weighting, prerequisites, taxonomy references, existing-lab existence, planned
slug uniqueness, ATT&CK mappings, evidence and fix requirements, and coverage of
API, GraphQL, JWT, OAuth, DevSecOps, container, Kubernetes, and supply-chain
topics.

## Related documents

- [API reference](../Manual-Lite/11_API_Reference/index.md)
- [API security labs](API-SECURITY-LABS.md)
- [OWASP Top 10 2025 labs](OWASP-TOP10-LABS.md)
- [OWASP security validation baseline](OWASP-SECURITY-BASELINE.md)
- [External datasets and references](SECURITY-DATASETS.md)
