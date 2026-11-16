# OWASP security validation baseline

This page is the review and validation guide for the platform's application,
API, and AI-skill security. The machine-readable source of truth is
`platform/backend/app/data/owasp-security-baseline.yaml`.

It covers three standards:

| Standard | Edition | Used for | Licence |
|---|---|---|---|
| **OWASP API Security Top 10 2023** | 2023 | API routes, object/function authorization, API labs | CC BY-SA 4.0 |
| **OWASP Top 10 2025** | 2025 | Web application, platform, supply chain, web labs | CC BY 3.0 |
| **OWASP Agentic Skills Top 10** | 1.0-2026 | AI skill governance, agent isolation, AI labs | CC BY-SA 4.0 |

The categories are awareness and review aids, not a certification. A status of
`covered` means the platform has a control and regression evidence. `partial`
means a control exists but a feature-level review or lab is still needed. `gap`
means the work is not done.

## How to validate

```bash
cd platform/backend
pytest -q tests/test_owasp_security_baseline.py
pytest -q tests/test_route_authorization.py tests/test_object_route_manifest.py
pytest -q tests/test_idor_matrix.py tests/test_horizontal_privilege.py
pytest -q tests/test_ratelimit.py tests/test_auth.py tests/test_jwt_validation.py
python ../../scripts/check-nginx-security-headers.py
python ../../scripts/check-external-datasets.py
```

The baseline test also loads the compiled FastAPI route table, checks that every
protected route has an authorization dependency, and checks that no CORS
configuration allows `*` with credentials.

## API Security Top 10 2023

| ID | Risk | Status | Primary evidence |
|---|---|---|---|
| API1 | Broken Object Level Authorization | covered | `test_idor_matrix.py`, `test_horizontal_privilege.py`, `test_object_route_manifest.py` |
| API2 | Broken Authentication | covered | `test_auth.py`, `test_jwt_validation.py`, `test_token_revocation.py`, `test_mfa.py` |
| API3 | Broken Object Property Level Authorization | partial | `test_input_safety.py`, `test_admin_users.py`, schema review |
| API4 | Unrestricted Resource Consumption | covered | `test_ratelimit.py`, `test_concurrency.py`, `test_stress_state.py` |
| API5 | Broken Function Level Authorization | covered | `test_route_authorization.py`, `test_access_matrix.py`, `test_authorization_matrix.py` |
| API6 | Unrestricted Access to Sensitive Business Flows | partial | auth, flag, competition, and certificate tests |
| API7 | Server Side Request Forgery | partial | `test_scripts_hardening.py`, `test_image_validation.py`, `test_rangebox_transport.py` |
| API8 | Security Misconfiguration | covered | header check, compose security, config secrets |
| API9 | Improper Inventory Management | partial | route audit, object manifest, about inventory |
| API10 | Unsafe Consumption of APIs | partial | SSO hardening, script hardening, config secrets |

### API gaps to close

1. **API3**: add a schema-level mass-assignment test for every new writable
   user, lab, and course field.
2. **API6**: require a flow-abuse review before a new checkout, coupon,
   competition-join, or bulk-export flow ships.
3. **API7**: require an allow-list and a negative test for any future URL
   import, webhook, or image fetch.
4. **API9**: add a generated deprecation ledger before a second API version.
5. **API10**: add a contract and timeout test for every new third-party API.

The API lab sequence is in [`API-SECURITY-LABS.md`](API-SECURITY-LABS.md).

## OWASP Top 10 2025

| ID | Risk | Status | Primary evidence |
|---|---|---|---|
| A01 | Broken Access Control | covered | IDOR matrix, tenant RLS, access matrix |
| A02 | Security Misconfiguration | covered | header check, compose security, config secrets |
| A03 | Software Supply Chain Failures | covered | supply-chain lock, integrity test, SBOM, Trivy |
| A04 | Cryptographic Failures | covered | crypto rotation, JWT validation, password policy |
| A05 | Injection | covered | input safety, SQL safety lint, script hardening |
| A06 | Insecure Design | partial | production control, architecture threat model, RBAC/PBAC |
| A07 | Authentication Failures | covered | auth lifecycle, MFA, breach check, token revocation |
| A08 | Software or Data Integrity Failures | covered | signed lock, integrity status, export labels |
| A09 | Security Logging and Alerting Failures | covered | security events, audit history, event coverage |
| A10 | Mishandling of Exceptional Conditions | partial | cleanup, health, input safety |

### Web gaps to close

1. **A06**: add a short design review to the lab and feature template so a new
   flow states its abuse cases before implementation.
2. **A10**: add a shared error taxonomy so a new route cannot leak a stack
   trace or turn a validation failure into a 500.

The web lab sequence is in [`OWASP-TOP10-LABS.md`](OWASP-TOP10-LABS.md).

## Agentic Skills Top 10

| ID | Risk | Status | Primary evidence |
|---|---|---|---|
| AST01 | Malicious Skills | partial | prompt-injection labs, synthetic manifests |
| AST02 | Supply Chain Compromise | covered | supply-chain lock, no skill registry |
| AST03 | Over-Privileged Skills | covered | RBAC/PBAC, owner-scoped AI keys |
| AST04 | Insecure Metadata | partial | input safety, lab text, asset checks |
| AST05 | Untrusted External Instructions | partial | offline indirect-injection lab, minor-safe defaults |
| AST06 | Weak Isolation | covered | compose security, isolation audit, network sandbox |
| AST07 | Update Drift | covered | immutable pins, dataset hashes, integrity test |
| AST08 | Poor Scanning | partial | static review, link checks, dataset validation |
| AST09 | No Governance | partial | security events, audit history, change control |
| AST10 | Cross-Platform Reuse | partial | platform-neutral lab text, provenance |

The AI lab sequence is in
[`AI-SECURITY-AGENTIC-LABS.md`](AI-SECURITY-AGENTIC-LABS.md).

## OpenCRE cross-mapping

Use [OpenCRE Explorer](https://www.opencre.org/explorer) to cross-map a
category or a platform control to related standards. Record:

- the CRE identifier;
- the linked standard and section;
- the access date;
- the decision or gap it supports.

OpenCRE is CC0-1.0. The mapping note does not copy the index; it records the
reference and the review decision. This is especially useful for API6, API9,
A06, A10, and the AST categories marked `partial`.

## Attribution

OWASP API Security Top 10 2023 is CC BY-SA 4.0, OWASP API Security Project team.
OWASP Top 10 2025 is CC BY 3.0, OWASP Top 10 Team. OWASP Agentic Skills Top 10
is CC BY-SA 4.0, OWASP Agentic Skills Top 10 project team. OpenCRE is CC0-1.0,
OWASP OpenCRE project.

See [`THIRD_PARTY_NOTICES.md`](../THIRD_PARTY_NOTICES.md) and
`THIRD_PARTY_LICENSES/` for the notices. Keep the attribution and share-alike
terms with any copied category text.
