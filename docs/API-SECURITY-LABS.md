# API security labs

These labs follow the OWASP API Security Top 10 2023. The machine-readable
plan is in `platform/backend/app/data/owasp-security-baseline.yaml`; the
validation matrix is in [`OWASP-SECURITY-BASELINE.md`](OWASP-SECURITY-BASELINE.md).

Most labs use the pinned Juice Shop target described in
[`JUICE-SHOP-LABS.md`](JUICE-SHOP-LABS.md). API-LAB-07 and API-LAB-10 use a
local mock so learners can test SSRF and unsafe upstream consumption without
touching a real service.

## Sequence

| Lab | Risk | Title | Target | Level | Minutes |
|---|---|---|---|---|---|
| API-LAB-01 | API1 | Basket object authorization | Juice Shop | beginner | 60 |
| API-LAB-02 | API2 | Token claims and session trust | Juice Shop | intermediate | 75 |
| API-LAB-03 | API3 | Mass assignment and property exposure | Juice Shop | intermediate | 75 |
| API-LAB-04 | API4 | Pagination and rate-limit behaviour | Platform | beginner | 45 |
| API-LAB-05 | API5 | Function-level authorization on an admin route | Platform | intermediate | 60 |
| API-LAB-06 | API6 | Sensitive flow abuse review | Platform | intermediate | 75 |
| API-LAB-07 | API7 | SSRF and outbound fetch design | Local mock | advanced | 90 |
| API-LAB-08 | API8 | API misconfiguration review | Platform | beginner | 45 |
| API-LAB-09 | API9 | API inventory and deprecation | Platform | intermediate | 60 |
| API-LAB-10 | API10 | Unsafe upstream consumption | Local mock | advanced | 75 |

## Evidence

Every lab requires:

- the exact request and response, with secrets redacted;
- the authorization or business decision and its reason;
- the impact in the fictional lab context;
- one preventive or detective control;
- a verification step for the fix.

A solved Juice Shop challenge is not enough. The scoreboard is a practice aid.

## Lab notes

### API1 — object authorization

Use two fictional accounts. Read a basket ID from the first account, then use
the second account to attempt the same object. Record the status and body
difference. The fix must be server-side ownership, not a hidden identifier.

### API2 — token trust

Inspect the login response and token claims. Test an expired or tampered token
against a local copy. State which checks belong on the server: signature,
issuer, audience, expiry, revocation, and authorization.

### API3 — mass assignment

Find a writable property that the UI does not display. Test it with a
low-privilege account and compare the response with the schema the client
expects. Bind only allow-listed fields and project responses explicitly.

### API4 — resource limits

Read the documented pagination and rate-limit behaviour. Send a bounded
sequence and record the 429. Explain why a shared counter is required when the
API runs multiple workers.

### API5 — function authorization

Compare a learner token with an instructor token on an admin route. Record the
denial and the permission that should have allowed it. Hiding the button is not
an authorization control.

### API6 — sensitive flows

Map a registration, flag, or export flow and its abuse cases. Identify the rate
limit, approval, or reauthentication gate. Propose one additional control and
show how it would be verified.

### API7 — SSRF

Review an outbound fetch that accepts a URL. Test an allow-list against
localhost, the metadata address, and lab ranges. Replace the fetch with a fixed
destination or a reviewed allow-list. Never test against a real external host.

### API8 — misconfiguration

Check CORS, security headers, API docs, and error bodies. Confirm docs are off
by default and origins are explicit. Add a regression check for each finding.

### API9 — inventory

Generate the route and object-route inventory. Find one route with no owner or
version note. Write a deprecation and retirement record. Use OpenCRE to link
the requirement to a standard if it helps the review.

### API10 — upstream consumption

Review an outbound integration's timeout, TLS, response validation, and error
handling. Simulate a malformed upstream response in a local mock. Show that the
failure is contained and auditable.

## Safety and reset

- Use the pinned Juice Shop image and digest from `JUICE-SHOP-LABS.md`.
- No internet egress, no published ports, no host mounts.
- Reset the target between learners; discard the disposable data.
- Use fictional accounts and data only.
- Do not run denial-of-service, destructive, or third-party tests.
- Do not paste real tokens, passwords, or personal data into a report.

## References

- [OWASP API Security Top 10 2023](https://api-security.owasp.org/editions/2023/en/0x00-header/)
- [OWASP FastAPI Security Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/FastAPI_Security_Cheat_Sheet.html)
- [OWASP REST Security Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/REST_Security_Cheat_Sheet.html)
- [OWASP Multi-Tenant Security Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Multi_Tenant_Security_Cheat_Sheet.html)
- [OpenCRE Explorer](https://www.opencre.org/explorer)

## Attribution

OWASP API Security Top 10 2023 is CC BY-SA 4.0, OWASP API Security Project team.
OWASP Cheat Sheet Series is CC BY-SA 4.0, OWASP Cheat Sheet Series Team.
Juice Shop is MIT, Bjoern Kimminich and the OWASP Juice Shop contributors.
OpenCRE is CC0-1.0, OWASP OpenCRE project. See
[`THIRD_PARTY_NOTICES.md`](../THIRD_PARTY_NOTICES.md).
