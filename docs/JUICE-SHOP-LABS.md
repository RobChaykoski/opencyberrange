# OWASP Juice Shop software-security labs

> **Status: author guidance / plan.** Juice Shop exercises are not all shipped.
> Verify a slug under `platform/labs` before calling one runnable. Shipped
> software-security labs are counted in [Lab and content counts](COUNTS.md).

Audience: software-security lab authors, instructors, and reviewers.

**OWASP Juice Shop** is an intentionally insecure web application built for
security education. It is MIT-licensed and maintained by Bjoern Kimminich and
the OWASP Juice Shop contributors. It is not affiliated with or endorsed by
OpenCyberRange.

This page is a lab blueprint, not a public running instance. The platform
registers Juice Shop as a pinned lab application in
`platform/backend/app/data/external-datasets.yaml`; the licence and attribution
are in `THIRD_PARTY_LICENSES/Juice-Shop-MIT.txt` and
[`THIRD_PARTY_NOTICES.md`](../THIRD_PARTY_NOTICES.md).

## Why Juice Shop

It gives learners a realistic single-page application with a REST API, a
client-side JavaScript bundle, authentication, JWTs, a basket, reviews, file
handling, and a challenge scoreboard. That is enough to teach the difference
between a missing control, a weak control, and a control that only exists in the
browser.

The scoreboard is a practice aid. It is **not** the assessment. A learner must
show the request, the response, the impact, and a defensive fix. A solved
challenge with no evidence is not completion.

## Safety and isolation

Every Juice Shop lab must:

- run the official image pinned by tag and digest;
- run on the platform's isolated lab network with **no internet egress**;
- publish no host port and use no host bind mount;
- use disposable storage and be reset between learners;
- contain only fictional accounts, baskets, reviews, and files;
- forbid denial of service, destructive file operations, real phishing, and
  attacks on any system outside the lab;
- keep authentication tokens, passwords, and personal data out of screenshots
  and reports;
- use the learner's own low-privilege account unless the exercise explicitly
  teaches privilege boundaries.

The image reference is:

```text
bkimminich/juice-shop:v20.4.0@sha256:9bbaecc41791f00b002bc65931cc5ff355fbdb941fa72b06558c18dace43197b
```

A reviewed compose shape is:

```yaml
services:
  juice-shop:
    image: bkimminich/juice-shop:v20.4.0@sha256:9bbaecc41791f00b002bc65931cc5ff355fbdb941fa72b06558c18dace43197b
    hostname: juice
    mem_limit: 512m
    cpus: 0.5
    read_only: true
    tmpfs:
      - /juice-shop/data:size=64m,mode=1777
      - /tmp:size=16m,mode=1777
    security_opt:
      - no-new-privileges:true
    cap_drop:
      - ALL
    restart: unless-stopped
```

Do not add `ports`, `network_mode`, `volumes`, `extra_hosts`, or a custom
`dns`. The platform attaches the lab network and the hostname. The writable
tmpfs is disposable; removing the container resets the application.

## Lab sequence

The sequence is ordered. It starts browser-only and adds one evidence type at a
time. The API-focused sequence is in
[`API-SECURITY-LABS.md`](API-SECURITY-LABS.md); the OWASP Top 10 2025 sequence is
in [`OWASP-TOP10-LABS.md`](OWASP-TOP10-LABS.md).

### JSEC-JS-01 — Application reconnaissance and threat model

- **Level:** beginner, 45–60 minutes.
- **Goal:** map the application before touching a vulnerability.
- **Tasks:** read the page and JavaScript bundle; identify the API base,
  authentication flow, basket and review endpoints, and the client-side routes;
  draw a trust-boundary diagram; list three assets and three plausible threats.
- **Evidence:** request/response table, route map, threat model with a stated
  assumption.
- **Defensive takeaway:** an asset inventory and a trust boundary are design
  artefacts, not afterthoughts.
- **Mapping:** OWASP A04 Insecure Design; CWE-1053 (missing documentation) as a
  discussion point.

### JSEC-JS-02 — Broken access control in the basket

- **Level:** beginner, 60 minutes.
- **Goal:** show that object identifiers are not authorization.
- **Tasks:** create a basket as the learner account; inspect the basket ID in
  the API response; attempt to read or modify another fictional basket; record
  the exact request, status, and response difference.
- **Evidence:** two requests with different object IDs, the authorization
  decision, and the impact statement.
- **Defensive takeaway:** enforce object ownership on the server for every
  read and write.
- **Mapping:** OWASP A01 Broken Access Control; CWE-639 Authorization Bypass
  Through User-Controlled Key.

### JSEC-JS-03 — Injection in a search or login path

- **Level:** intermediate, 75 minutes.
- **Goal:** distinguish a database error from a successful injection.
- **Tasks:** start with a benign query; add a minimal payload; compare the
  response, timing, and server error; retrieve only the lab's own fictional
  record; explain why input validation alone is not the fix.
- **Evidence:** payload, request, response, extracted fictional field, and a
  parameterized-query fix.
- **Defensive takeaway:** use parameterized queries and least-privilege
  database accounts; do not build queries by string concatenation.
- **Mapping:** OWASP A03 Injection; CWE-89 SQL Injection.

### JSEC-JS-04 — Cross-site scripting and the browser boundary

- **Level:** intermediate, 75 minutes.
- **Goal:** show how untrusted data becomes executable in a browser.
- **Tasks:** place a harmless marker in a review or profile field; identify the
  sink and the encoding context; demonstrate the marker in a second browser
  session; explain why CSP is defence in depth, not a substitute for output
  encoding.
- **Evidence:** source field, rendered sink, browser result, and a fix that
  encodes at the sink.
- **Defensive takeaway:** encode for the exact context and treat every
  client-side store as untrusted.
- **Mapping:** OWASP A03 Injection; CWE-79 Cross-site Scripting.

### JSEC-JS-05 — Authentication, JWT, and session trust

- **Level:** intermediate, 90 minutes.
- **Goal:** separate authentication from authorization and from token trust.
- **Tasks:** inspect the login response and token claims; test an expired or
  tampered token in a local copy; compare a low-privilege and a higher-privilege
  route; explain which check belongs on the server.
- **Evidence:** token header/claims with secrets redacted, two authorization
  decisions, and a server-side validation plan.
- **Defensive takeaway:** validate signature, issuer, audience, expiry, and
  authorization on the server; never trust a client-side role.
- **Mapping:** OWASP A07 Identification and Authentication Failures; CWE-287
  Improper Authentication and CWE-345 Insufficient Verification of
  Authenticity.

### JSEC-JS-06 — Capstone: chain, impact, and fix

- **Level:** advanced, 120–150 minutes.
- **Goal:** combine two findings into one defensible mini-report.
- **Tasks:** choose a non-destructive chain from the earlier labs; collect a
  timeline; state the business impact; propose one preventive and one detective
  control; show a regression test or a concrete verification step.
- **Evidence:** analyst report, request/response appendix, timeline, and a fix
  or verification plan.
- **Defensive takeaway:** a finding is not a fix; the report must say what
  changes and how the change will be verified.
- **Mapping:** OWASP A01, A03, and A07; CWE depends on the chosen chain.

## Assessment

Each lab requires:

- a short finding that states what happened and why it matters;
- the exact request and response, with secrets redacted;
- the impact in the lab's fictional context;
- the control that failed and the control that should replace it;
- a confidence statement and one alternative explanation.

The Juice Shop scoreboard may be used for practice and hints. It does not
replace the report. A flag alone is not completion evidence.

## Reset and teardown

1. Stop and remove the lab container and network.
2. Discard the tmpfs data with the container; do not reuse a learner's state.
3. Recreate the container from the pinned image for the next session.
4. Confirm the challenge score is reset and the default fictional data is
   restored.
5. Keep only the learner's submitted evidence, not the live application state.

If a lab needs a per-session platform flag, store it in the lab record and
reveal it only after the evidence check. Do not bake a public flag into the
image or the compose file.

## Review checklist

- [ ] Image is pinned by tag and `sha256` digest.
- [ ] No published ports, host mounts, host networking, or custom DNS.
- [ ] No internet egress; the only target is the lab instance.
- [ ] Storage is disposable and reset between learners.
- [ ] Accounts, baskets, reviews, and files are fictional.
- [ ] The exercise is non-destructive and does not attack a third party.
- [ ] Evidence includes a request/response and a defensive fix.
- [ ] Licence and attribution are retained.
- [ ] `python scripts/check-external-datasets.py` passes.

## Attribution

OWASP Juice Shop is Copyright (c) 2014-2026 Bjoern Kimminich and the OWASP
Juice Shop contributors, licensed under the MIT License. See
`THIRD_PARTY_LICENSES/Juice-Shop-MIT.txt`.

Project pages: <https://juice-shop.github.io/> and
<https://github.com/juice-shop/juice-shop>.
