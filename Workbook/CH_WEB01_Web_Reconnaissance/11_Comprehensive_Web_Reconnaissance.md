# Exercise W1.11: Comprehensive Web Reconnaissance

## Before You Begin

Target: `http://target.lab/` port `80`. No credentials are required.

This is a repeatable workflow across one approved application. It combines
scope, observation, bounded discovery, input mapping, header review, findings,
and cleanup. It does **not** authorize exploitation, credential attacks, or a
second target.

Use one wordlist and one directory run. Do not add extensions, recursion, a
larger wordlist, or another hostname.

## Words to Know

| Term | Meaning |
|---|---|
| **Preflight** | Confirming the scheme, host, port, path, account, and redirect boundary before testing. |
| **Baseline** | One known request and response used for comparison. |
| **Bounded discovery** | Automated requests with a fixed target, wordlist, rate, and depth. |
| **Finding** | A recorded observation with evidence, confidence, and limitations. |
| **Cleanup** | Stopping the session and removing local notes or files you no longer need. |

## Workflow

1. Scope preflight.
2. Baseline request.
3. Browser observation.
4. Technology evidence.
5. Bounded content discovery.
6. Input and method mapping.
7. TLS, cookie, and header review.
8. Findings and attack-surface map.
9. Cleanup.

## Walkthrough

### Step 1: Scope preflight

Confirm the exercise panel shows `target.lab` on port `80`.

```bash
getent hosts target.lab
curl -v http://target.lab/ -o /dev/null
```

**Expected:** a resolved address, a `Host: target.lab` request header, and a
status line such as `200 OK`.

**Stop if:** the panel shows another host or port, the redirect leaves
`target.lab`, or the service is unstable.

### Step 2: Baseline and browser observation

Record the page title, status, and visible purpose. In the RangeBox browser,
open Developer Tools once and note the document request, one script or style
request, and any request to another host.

**Stop if:** a request goes to a public domain or a host outside `target.lab`.

### Step 3: Technology evidence

```bash
curl -I http://target.lab/
whatweb http://target.lab/
```

Record each clue separately: server, framework, CMS, runtime, and client
library. A header is one clue. Confirm it with a second source before assigning
a product or version.

Do not claim a CVE or vulnerability from a fingerprint.

### Step 4: Bounded content discovery

```bash
gobuster dir -u http://target.lab -w /usr/share/wordlists/dirb/common.txt
```

Record the wordlist, thread count, request count, and status codes. Validate the
most relevant result manually:

```bash
curl -I http://target.lab/<discovered-path>/
```

Replace `<discovered-path>` with one result from your run. Do not request every
result automatically.

**Stop if:** you see a wildcard or soft `404`, a `429`, an unstable service, or a
redirect outside `target.lab`.

### Step 5: Method and input mapping

```bash
curl -X OPTIONS http://target.lab/ -v
```

Record the advertised methods exactly. An advertised method is a capability
clue, not a vulnerability.

Do not send `PUT`, `DELETE`, `TRACE`, injection strings, or a mass parameter
list in this exercise.

### Step 6: Header and path evidence

Review the diagnostic endpoint named by the application:

```bash
curl -sI http://target.lab/headers.php
```

Record the status and any custom headers. This lab's diagnostic response
advertises an internal path through `X-Internal-Path`. Read it as a clue and
confirm the path the application names:

```bash
curl -s http://target.lab/headers.php | grep -i 'X-Internal-Path'
```

Use the returned path exactly as shown. Do not guess other internal paths.

### Step 7: Recover the lab flag

The diagnostic clue points to the lab's private flag file:

```bash
curl -s http://target.lab/private/flag.txt
```

Copy the complete `OCR{...}` value into the exercise panel.

### Step 8: Build the finding and attack-surface map

Complete the map from W1.10 using only this exercise's evidence. For the flag
finding, record:

| Field | Your note |
|---|---|
| Exact URL | `http://target.lab/headers.php` |
| Observation | Diagnostic header names an internal path |
| Response evidence | `X-Internal-Path` value |
| Follow-up URL | `http://target.lab/private/flag.txt` |
| Timestamp | |
| Interpretation | Information disclosure of a path in the lab |
| Confidence | High for the header, Medium for impact outside the lab |
| Limitation | Does not prove the same path exists in another deployment |
| Next safe test | None in this chapter; report the observation |
| Redactions | None required for the training flag |

### Step 9: Cleanup

- Stop the exercise from the panel.
- Remove local files that contain tokens, cookies, or personal data.
- Keep only the redacted evidence you can explain.
- Confirm the session timer has stopped.

## Evidence

| Field | Your note |
|---|---|
| Target | `http://target.lab/` |
| Baseline status | |
| Page title | |
| Technology clues | |
| Wordlist | `/usr/share/wordlists/dirb/common.txt` |
| Requests reported | |
| Validated discovery | |
| Advertised methods | |
| `X-Internal-Path` | |
| Flag path | `/private/flag.txt` |
| Findings written | |
| Confidence | Low / Medium / High |
| Cleanup complete? | Yes / No |

## Stop Conditions

Stop if:

- the target differs from `target.lab` or the port is not `80`;
- a redirect leaves `target.lab`;
- the service returns `429`, `500`, or becomes unstable;
- a discovered page contains personal data or a real-looking credential;
- you are tempted to add exploitation, credential guessing, or a second target.

## If You Get Stuck

| Problem | Safe next step |
|---|---|
| Target does not resolve | Confirm the exercise is running; do not use public DNS. |
| `whatweb` is missing | Use `curl -I` and page source; ask before installing anything. |
| All discovery results are `200` | Check for a wildcard or soft `404`; record it and stop. |
| `headers.php` is `404` | Recheck the exact path in the exercise panel. |
| Flag path is `404` | Re-read the `X-Internal-Path` value exactly; do not scan for other paths. |
| `429` or `500` | Stop and report; do not retry rapidly. |

## What Success Looks Like

You can show the scope preflight, one baseline request, one corroborated
technology clue, one bounded discovery run with a request count, one validated
path, the header clue, the flag, one finding with a limitation, and a completed
cleanup. Submit the lab flag.
