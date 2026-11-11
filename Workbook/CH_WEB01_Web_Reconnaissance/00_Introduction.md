# WEB01: Web Reconnaissance

<!-- BEGIN GENERATED CHAPTER POSITION -->
!!! note "Curriculum position"
    **Chapter:** `WEB01` — Web Reconnaissance
    **Prerequisites:** `NET00` — Network Foundations
    **Recommended next:** `WEB01B` — Advanced Recon and Traversal
<!-- END GENERATED CHAPTER POSITION -->

## Welcome

Web reconnaissance is the authorised mapping of a web application and its
exposed interfaces. It is **observation and bounded discovery**, not exploitation.

You will learn to:

- confirm the exact application identity and scope;
- read HTTP requests and responses precisely;
- use browser developer tools passively;
- fingerprint technologies with corroboration;
- discover content and virtual hosts within explicit limits;
- review public metadata, inputs, sessions, TLS, cookies, and security headers;
- turn observations into an attack-surface map and a defensible report.

This chapter is for learners from software development or general IT. HTTP,
APIs, frameworks, routes, and deployment environments should feel familiar. You
do not need prior penetration-testing experience.

## Words to Know

| Term | Meaning |
|---|---|
| **Web application** | Software delivered through a browser and an HTTP server. |
| **Client** | The browser or tool that sends a request. |
| **Server** | The system that accepts the request and returns a response. |
| **Reverse proxy** | A server in front of an application that forwards requests and may hide the origin. |
| **Route** | The application rule that maps a method and path to behaviour. |
| **Endpoint** | A specific method-and-path target, such as `GET /api/status`. |
| **Hostname** | A name that resolves to an address, such as `target.lab`. |
| **Virtual host** | A website selected by the HTTP `Host` header on a shared server. |
| **Reconnaissance** | Authorised collection of information about an application and its exposed interfaces. |
| **Enumeration** | Systematic listing of resources, names, or services within scope. |
| **Attack surface** | The set of reachable hosts, routes, inputs, identities, and data that an application exposes. |

## Scope for This Chapter

This chapter uses several isolated practice targets. **Each exercise names its own target.** Use only the target shown in that exercise.

| Exercise | Target | Port | Purpose |
|---|---|---:|---|
| W1.4 Technology Fingerprinting | `target.lab` | 80 | Technology evidence |
| W1.5 Content Discovery | `recon.lab` | 80 | Directory and file discovery |
| W1.6 Virtual Hosts | `main.lab`, `admin.lab`, `api.lab` | 80 | Virtual-host identity |
| W1.8 HTTP/API Inputs | `api.lab` | 80 | Method and input mapping |
| W1.9 Headers | `secure.lab` | 80 | Cookies and security headers |
| W1.11 Comprehensive | `target.lab` | 80 | Full bounded workflow |

Rules:

- Use **HTTP** and the hostname shown in the exercise. Do not substitute an IP,
  a public domain, or an adjacent lab.
- No credentials are required for these labs. Do not enter real credentials or
  personal information.
- Use only the wordlist, candidate names, methods, and request limits named in
  each exercise.
- Do not use exploit payloads, credential attacks, access-control bypasses, or
  mass parameter discovery.
- Do not test a name just because it resolves. A resolving or reachable name is
  not automatically authorised.
- Stop on a target mismatch, unexpected redirect, certificate mismatch,
  rate-limiting warning, unstable service, sensitive data, or an out-of-scope
  name.

## Chapter Roadmap

1. **Scope preflight** — URL, host, port, base path, virtual host, redirect boundary.
2. **HTTP orientation** — methods, status, headers, bodies, cookies, redirects.
3. **Browser developer tools** — passive observation of requests and storage.
4. **Technology fingerprinting** — evidence, corroboration, confidence.
5. **Content discovery** — bounded wordlists, validation, false positives.
6. **Virtual hosts and subdomains** — DNS, Host header, SNI, certificate names.
7. **Public metadata** — robots, sitemaps, JavaScript, comments, source maps.
8. **Forms, parameters, APIs, sessions** — benign input mapping.
9. **TLS, cookies, security headers** — controls, context, limitations.
10. **Findings and attack-surface map** — defensible evidence.
11. **Comprehensive reconnaissance** — repeatable bounded workflow.
12. **Chapter review** — knowledge check and readiness gate.

## Estimated Time

Plan for about **4–6 hours** across the chapter. Each conceptual page is about
**15–25 minutes**; each lab is about **25–40 minutes**. This is an estimate,
not a deadline.

## What You Need

- RangeBox with a browser and terminal.
- The exercise panel open in the **Web Application Security** track.
- A notes file for requests, responses, and redacted evidence.
- A text editor or screenshot tool for redacted evidence.

## Evidence Standard

Record, for each observation:

- exact URL and method;
- target hostname, port, and base path;
- request headers/body only where relevant;
- status code and relevant response headers;
- timestamp;
- what you observed;
- what you inferred;
- confidence and one alternative explanation;
- what the evidence does **not** prove;
- redactions applied.

Use the evidence ladder: **Observed → Inferred → Validated → Impacted → Remediated → Verified**.

Never paste passwords, session cookies, tokens, personal data, or proprietary
source into shared notes. Redact them.

## Completion Criteria

You are ready to continue when you can:

- state where commands run and which target is authorised;
- explain the difference between observation, discovery, reachability,
  authentication, authorisation, exposure, misconfiguration, and confirmed
  vulnerability;
- show a baseline request and a bounded discovery result;
- validate at least one automated result manually;
- produce a redacted attack-surface summary with confidence and limitations;
- explain one safe next step and one stop condition.

Start with [WEB01 Exercise W1.1 -- Web Target and Scope Preflight](01_Web_Target_and_Scope_Preflight.md).
