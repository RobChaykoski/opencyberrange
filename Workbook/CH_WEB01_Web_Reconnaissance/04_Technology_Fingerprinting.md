# Exercise W1.4: Technology Fingerprinting

## Before You Begin

Target: `http://target.lab/` port `80`. No credentials are required. This lab is
read-only until the final flag request.

Run commands in the RangeBox terminal.

## Words to Know

| Term | Meaning |
|---|---|
| **Web server** | Software that accepts HTTP requests, such as nginx or Apache. |
| **Reverse proxy** | A front server that forwards requests to an application. |
| **Framework** | Application software that provides routing, templating, or data handling. |
| **Runtime** | The language environment, such as PHP, Python, or Node.js. |
| **CMS** | A content management system, such as WordPress. |
| **Client library** | JavaScript or CSS code loaded by the browser. |
| **Dependency** | Third-party code the application relies on. |
| **Fingerprint** | A clue about the technology stack. |
| **Corroboration** | A second independent clue that supports the same conclusion. |

## Walkthrough

### Step 1: Confirm the target

Confirm `target.lab` on port `80` in the exercise panel. Stop on any mismatch.

### Step 2: Fetch headers

```bash
curl -I http://target.lab/
```

**Expected:** an HTTP status line and headers. Look for `Server`,
`X-Powered-By`, `X-Framework`, cookies, and cache headers.

The test lab advertises `X-Framework: WordPress`. Treat that as one clue, not a
complete product or version proof.

### Step 3: Run whatweb

```bash
whatweb http://target.lab/
```

**Expected:** a compact list of technologies. The output may include the server,
framework, CMS, and libraries.

Do not add aggressive modes or extra targets. One run against `target.lab` is
the limit.

### Step 4: Corroborate

Look for a second clue, such as:

- a CMS-specific path;
- a cookie name;
- a generator meta tag;
- a JavaScript asset path.

Record whether the clues agree. If they disagree, lower your confidence.

### Step 5: Retrieve the lab flag

The lab places its training flag in a CMS-specific path:

```bash
curl http://target.lab/wp-admin/flag.txt
```

Copy the complete `OCR{...}` value into the exercise panel.

## Evidence

| Field | Your note |
|---|---|
| URL | `http://target.lab/` |
| Server header | |
| Framework clue | |
| CMS clue | |
| Runtime clue | |
| Client library clue | |
| Corroborating clue | |
| Confidence | Low / Medium / High |
| Alternative explanation | |
| What the evidence does not prove | |

## Rules

- Do not claim a CVE or vulnerability from a fingerprint.
- Do not guess a version that is not shown.
- Do not run aggressive whatweb modes.
- Do not test another hostname.

## If You Get Stuck

| Problem | Safe next step |
|---|---|
| No headers | Confirm the lab is running and the target is `target.lab`. |
| whatweb is missing | Use `curl -I` and the page source only. Ask before installing anything. |
| Fingerprints disagree | Record both and lower confidence. |
| Flag path is 404 | Recheck the CMS clue; do not scan other paths. |
| Another host appears | Stop. Do not follow it. |

## What Success Looks Like

You can state one server clue, one framework/CMS clue, one corroborating clue,
your confidence, and one thing the evidence does not prove. Submit the lab flag.
