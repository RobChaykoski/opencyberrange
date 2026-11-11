# Exercise W1.1: Web Target and Scope Preflight

## Before You Begin

This preflight uses the first lab target, `http://target.lab/`, on port `80`.
Later exercises name their own target. If the exercise panel shows a different
hostname or port, **stop and ask**.

Run commands in the RangeBox terminal. No credentials are required.

## Words to Know

| Term | Meaning |
|---|---|
| **Scheme** | The protocol in a URL, such as `http` or `https`. |
| **Hostname** | The name in the URL, such as `target.lab`. |
| **IP address** | The numeric address the hostname resolves to. |
| **Port** | The service number. This lab uses `80`. |
| **Base path** | The starting path, `/` for the application root. |
| **Virtual host** | The site selected by the HTTP `Host` header. |
| **DNS** | The naming system that resolves a hostname to an address. |
| **TLS SNI** | The hostname sent during a TLS handshake. This lab uses HTTP, so SNI is not used. |
| **Certificate name** | A name in a TLS certificate. This lab uses HTTP, so no certificate is presented. |
| **Redirect boundary** | The destinations you may follow without leaving scope. |

## Target Card

Copy this into your notes before using a tool:

| Field | Value |
|---|---|
| Exercise | W1.1 |
| Scheme | `http` |
| Hostname | `target.lab` |
| Port | `80` |
| Base path | `/` |
| Virtual host | `target.lab` |
| Account | None |
| Redirect boundary | Same hostname only |
| Source | Exercise panel |

## Walkthrough

### Step 1: Confirm the exercise target

Open the exercise panel and compare the displayed hostname and port with the
Target Card.

**Expected:** `target.lab` on port `80`.

**Stop if:** the panel shows another host, another port, a public domain, or no
target.

### Step 2: Confirm name resolution

```bash
getent hosts target.lab
```

**Expected:** one or more addresses returned by the lab DNS.

**If it returns nothing:** stop. Do not substitute a public DNS name or an IP
from another student.

### Step 3: Capture a baseline request

```bash
curl -v http://target.lab/ -o /dev/null
```

**Expected:** a connection to port `80`, a `Host: target.lab` request header,
and an HTTP status line such as `200 OK`.

**What to notice:** the IP address may differ from the hostname. The `Host`
header selects the virtual host. A reverse proxy may sit in front of the
application.

### Step 4: Check the redirect boundary

Look at the status line and any `Location` header.

- A same-host redirect is within scope.
- A redirect to another hostname, a public site, or a different port is a stop
  condition.

Do not follow an out-of-scope redirect.

### Step 5: Record application identity

Record:

- page title or visible application name;
- status code;
- server/proxy headers, if any;
- whether the page is a login, a public page, or an error;
- the exact URL you requested.

## Evidence

| Field | Your note |
|---|---|
| Timestamp | |
| URL | `http://target.lab/` |
| Resolved address | |
| Status | |
| `Host` header sent | |
| Redirect? | |
| Application title | |
| Confidence | Low / Medium / High |
| Stop condition seen? | |

## If You Get Stuck

| Problem | Safe next step |
|---|---|
| Name does not resolve | Stop. Check the exercise panel. Do not use a public name. |
| Connection refused | Confirm the lab is running and port `80` is correct. |
| Redirect to another host | Stop. Do not follow it. Ask your teacher. |
| Certificate warning | This lab is HTTP. If you see TLS, stop and confirm the target. |
| Target mismatch | Stop. Do not run tools against the new target. |

## What Success Looks Like

You can show the Target Card, the baseline request, the resolved address, the
status, the application title, and one sentence explaining why the target is in
scope. This preflight has **no flag**.
