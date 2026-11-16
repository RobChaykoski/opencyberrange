# OWASP Top 10 2025 labs

These labs follow the OWASP Top 10 2025. The machine-readable plan is in
`platform/backend/app/data/owasp-security-baseline.yaml`; the validation matrix
is in [`OWASP-SECURITY-BASELINE.md`](OWASP-SECURITY-BASELINE.md).

The web labs reuse the pinned Juice Shop target for application behaviour and
the platform itself for supply-chain, logging, integrity, and error-handling
exercises. See [`JUICE-SHOP-LABS.md`](JUICE-SHOP-LABS.md) for the target setup.

## Sequence

| Lab | Risk | Title | Target | Level | Minutes |
|---|---|---|---|---|---|
| WEB-LAB-01 | A01 | Access control across two accounts | Juice Shop | beginner | 60 |
| WEB-LAB-02 | A02 | Browser and API misconfiguration | Platform | beginner | 45 |
| WEB-LAB-03 | A03 | Dependency and artifact provenance | Platform | intermediate | 75 |
| WEB-LAB-04 | A04 | Password and token cryptography | Platform | intermediate | 60 |
| WEB-LAB-05 | A05 | Injection from input to sink | Juice Shop | intermediate | 75 |
| WEB-LAB-06 | A06 | Design review of a checkout flow | Juice Shop | intermediate | 75 |
| WEB-LAB-07 | A07 | Authentication and session failures | Juice Shop | intermediate | 75 |
| WEB-LAB-08 | A08 | Integrity of a release artifact | Platform | intermediate | 60 |
| WEB-LAB-09 | A09 | From event to alert | Platform | beginner | 45 |
| WEB-LAB-10 | A10 | Exceptional conditions and safe failure | Platform | intermediate | 60 |

## Evidence

Every lab requires:

- a short finding that states what happened and why it matters;
- the request, response, or artifact that supports it;
- the failed or missing control;
- the fix and a verification step;
- a confidence statement and one alternative explanation.

A flag or a solved challenge alone is not completion evidence.

## Lab notes

### A01 — access control

Use two accounts on the same object route. Prove whether the server enforces
ownership. Write the missing server-side check and the regression test.

### A02 — misconfiguration

Review CSP, CORS, HSTS, docs exposure, and error bodies. Explain which control
is preventive and which is detective. Add a regression check for one finding.

### A03 — supply chain

Read the signed supply-chain lock and a package provenance record. Find one
unpinned or unreviewed dependency. Write the pin, hash, and review action.

### A04 — cryptography

Identify the password hash and token signing algorithm. Explain why a fast hash
or a client-side secret fails. Write a rotation and verification step.

### A05 — injection

Trace one input to a query, command, or browser sink. Prove the result with a
harmless marker. Replace concatenation with a parameterized query or safe API.

### A06 — insecure design

Draw the checkout trust boundaries and abuse cases. Identify one missing
business rule. Add a server-side control and a test. Use OpenCRE to link the
design requirement to a standard if it helps the review.

### A07 — authentication

Review login, reset, MFA, and session behaviour. Test one weak control in a
local copy. Document the server-side fix and the user-visible effect.

### A08 — integrity

Verify a signed lock and a lab image digest. Change one byte and observe the
failure. Explain why a hash without a trust anchor is insufficient.

### A09 — logging and alerting

Trace a sensitive action to its security event. Check the actor, reason,
target, and outcome. Write one alert rule and one false-positive note.

### A10 — exceptional conditions

Send malformed and oversized input to a local endpoint. Compare the validation
error with a server failure. Add a bounded error path and a cleanup check.

## Safety and reset

- Use the pinned Juice Shop image and digest from `JUICE-SHOP-LABS.md`.
- No internet egress, no published ports, no host mounts.
- Reset the target between learners.
- Use fictional accounts and data only.
- Do not run destructive or third-party tests.
- Do not paste real tokens, passwords, or personal data into a report.

## References

- [OWASP Top 10 2025](https://top10.owasp.org/2025/)
- [OWASP Threat Modeling Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Threat_Modeling_Cheat_Sheet.html)
- [Threat Modeling Manifesto](https://www.threatmodelingmanifesto.org/)
- [OWASP Security Terminology Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Security_Terminology_Cheat_Sheet.html)
- [OpenCRE Explorer](https://www.opencre.org/explorer)

## Attribution

OWASP Top 10 2025 is CC BY 3.0, OWASP Top 10 Team. OWASP Cheat Sheet Series is
CC BY-SA 4.0, OWASP Cheat Sheet Series Team. The Threat Modeling Manifesto is
CC BY 4.0, the Threat Modeling Manifesto working group. Juice Shop is MIT,
Bjoern Kimminich and the OWASP Juice Shop contributors. OpenCRE is CC0-1.0,
OWASP OpenCRE project. See [`THIRD_PARTY_NOTICES.md`](../THIRD_PARTY_NOTICES.md).
