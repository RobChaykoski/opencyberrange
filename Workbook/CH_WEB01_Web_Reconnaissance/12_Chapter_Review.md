# Chapter Review: Web Reconnaissance

## Purpose

This review checks whether you can run controlled discovery and interpret the
evidence accurately. It does not reward the number of paths found or the speed
of a scan.

## Part A: Scope and Safety

Answer briefly.

1. The exercise panel names `recon.lab`, but a DNS lookup also resolves
   `admin.recon.lab`. May you test the second name? Why or why not?
2. A response redirects from `target.lab` to `example.com`. What do you do next?
3. A public `robots.txt` lists `/backup/`. Does that authorize you to open it?
4. Your scan returns `429`. What should you change first: the thread count, the
   wordlist, or nothing?
5. A certificate names `secure.lab` but you requested `secure.test`. Is the
   certificate valid for your request?

### Answer Key

1. **No.** A resolving name is not automatically authorized. Test only the names
   named in the exercise.
2. **Stop.** Do not follow an out-of-scope redirect. Record it and report it.
3. **No.** A public file is a clue, not permission. Access only paths the
   exercise names.
4. **Nothing.** Stop and wait. Increasing threads or changing wordlists makes
   the rate-limit problem worse.
5. **No.** The certificate must cover the requested hostname. Treat the mismatch
   as a stop condition.

## Part B: Request and Response Interpretation

For each response, state whether it proves a vulnerability, a misconfiguration,
a normal access result, or only an observation.

| Response | Your classification |
|---|---|
| `200 OK` with a login page | |
| `403 Forbidden` on `/admin/` | |
| `Server: nginx` | |
| `X-Debug-Mode: enabled` | |
| `Set-Cookie: session=...` without `HttpOnly` on HTTP | |
| `301` to another hostname | |

### Answer Key

| Response | Classification |
|---|---|
| `200 OK` with a login page | Normal access result; authentication is required or offered. |
| `403 Forbidden` on `/admin/` | Access result; authorization is enforced. Do not bypass it. |
| `Server: nginx` | Observation; the banner may be accurate, stale, or altered. |
| `X-Debug-Mode: enabled` | Misconfiguration clue; confirm the impact before calling it a vulnerability. |
| Cookie without `HttpOnly` on HTTP | Contextual weakness; the transport already lacks TLS in this lab. |
| `301` to another hostname | Scope boundary; stop and do not follow it. |

## Part C: False-Positive Validation

A directory scan reports `200` for every candidate path, and every response has
the same title and body length.

1. What is the most likely cause?
2. What should you do before recording the paths as discoveries?
3. What evidence would change your conclusion?

### Answer Key

1. A wildcard response or a soft `404` page.
2. Compare a known-invalid path with a known-valid path and check the response
   body, title, and length.
3. A different status, title, body, or content hash for the specific path, and a
   second confirmation with a manual request.

## Part D: Tool Reference

| Tool or action | Purpose | Target input | Traffic impact | Sensitive output | Validation step | Stop condition |
|---|---|---|---|---|---|---|
| `curl -v` | Inspect one request and response | Exact URL | One request | Headers, cookies | Read status and `Host` | Redirect leaves scope |
| `curl -I` | Read response headers | Exact URL | One request | Server banners, custom headers | Confirm the header context | Target mismatch |
| Browser DevTools | Observe requests and storage | Approved page | Normal page load | Cookies, tokens, storage | Record key names only | Third-party host appears |
| `whatweb` | Collect technology clues | One URL | Small number of requests | Banners, paths | Corroborate with a second clue | Aggressive mode or new target |
| `gobuster dir` | Bounded path discovery | One URL and one wordlist | Many requests | Hidden paths | Validate representative results | `429`, instability, wildcard |
| `OPTIONS` | List advertised methods | One URL | One request | Method list | Treat as a capability clue | Method testing drifts into exploitation |
| `getent hosts` | Confirm name resolution | Exact hostname | None | Address | Compare with the panel | Name outside scope |

## Part E: Small Attack-Surface Summary

Complete this table for one lab target. Use only evidence you collected.

| Host | Route | Method | Input | Authentication | Role | Technology evidence | Data type | Confidence | Limitation |
|---|---|---|---|---|---|---|---|---|---|
| | | | | | | | | | |

Then write one finding using this structure:

```text
Finding ID:
Title (observation, not conclusion):
Exact URL:
Method:
Request evidence:
Response evidence:
Timestamp:
Observation:
Interpretation:
Confidence:
Limitation:
Next safe test:
Redactions:
```

## Part F: Readiness Checklist

- [ ] I can state where commands run and which host is authorized.
- [ ] I can separate observation, discovery, reachability, authentication,
      authorization, exposure, misconfiguration, and confirmed vulnerability.
- [ ] I can show one baseline request and one bounded discovery result.
- [ ] I validated at least one automated result manually.
- [ ] I recorded a request count and a stop condition.
- [ ] I produced a redacted attack-surface summary with confidence and limits.
- [ ] I can explain one safe next step and one reason to stop.
- [ ] I cleaned up the session and local evidence.

## Remediation Pointers

Use these as defensive discussion points, not as exploit instructions:

- Disable diagnostic headers and verbose error pages in production.
- Apply least privilege and server-side authorization to every route.
- Serve only intended files; keep backups and configuration outside the web
  root.
- Set explicit security headers and cookie attributes appropriate to the
  transport.
- Rate-limit and monitor enumeration patterns, and alert on unusual request
  volume.
- Review public metadata for stale paths and remove secrets from comments and
  bundles.

## What Comes Next

You are ready for **WEB01B: Advanced Recon and Traversal** when you can complete
the checklist without looking back at the earlier pages.
