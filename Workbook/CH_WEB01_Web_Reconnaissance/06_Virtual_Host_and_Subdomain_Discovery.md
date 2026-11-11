# Exercise W1.6: Virtual Host and Subdomain Discovery

## Before You Begin

Targets: `main.lab`, `admin.lab`, and `api.lab` on port `80`. These are the only
approved names in this exercise.

Do not brute-force a public domain. Do not test a name merely because it
resolves.

## Words to Know

| Term | Meaning |
|---|---|
| **Hostname** | A name that resolves to an address. |
| **Subdomain** | A name below a parent domain, such as `admin.main.lab`. |
| **Virtual host** | A site selected by the HTTP `Host` header on a shared server. |
| **DNS record** | A mapping from a name to an address or another record. |
| **Host header** | The HTTP header that names the requested site. |
| **SNI** | The hostname sent during a TLS handshake. This lab uses HTTP. |
| **Certificate SAN** | The names listed in a TLS certificate. This lab uses HTTP. |
| **Wildcard DNS** | A DNS rule that resolves every name under a domain. |

## Walkthrough

### Step 1: Confirm the approved names

In the exercise panel, confirm the target hostnames:

```text
main.lab
admin.lab
api.lab
```

If the panel shows different names, stop and ask. Do not add names from a public
wordlist.

### Step 2: Compare the three responses

```bash
curl -I http://main.lab/
curl -I http://admin.lab/
curl -I http://api.lab/
```

**Expected:** three responses with different titles, headers, or content. The
same IP address can host all three as virtual hosts.

**If all three are identical:** suspect a wildcard or default virtual host.
Stop and record it as an observation.

### Step 3: Confirm application identity

```bash
curl -s http://main.lab/ | head -20
curl -s http://admin.lab/ | head -20
curl -s http://api.lab/ | head -20
```

Record the visible title or purpose of each. Do not copy sensitive content.

### Step 4: Retrieve the lab flag

The admin virtual host carries the lab flag:

```bash
curl http://admin.lab/flag.txt
```

Copy the complete `OCR{...}` value into the exercise panel.

## Evidence

| Host | Status | Title/purpose | Different from main? | In scope? |
|---|---|---|---|---|
| `main.lab` | | | — | Yes |
| `admin.lab` | | | | Yes |
| `api.lab` | | | | Yes |

Record one sentence explaining why a resolving name is not automatically an
authorised target.

## Stop Conditions

Stop if:

- a response redirects to a name outside `main.lab`, `admin.lab`, or `api.lab`;
- a certificate or Host header names a different domain;
- you find a new subdomain and are tempted to test it;
- the service returns `429` or becomes unstable;
- the panel shows a different target set.

## If You Get Stuck

| Problem | Safe next step |
|---|---|
| Name does not resolve | Confirm the exercise name and lab status. Do not use public DNS. |
| All names look identical | Record a probable wildcard/default vhost and stop. |
| Admin host has no flag | Recheck `http://admin.lab/` and the exact path. |
| Redirect to another host | Stop. Do not follow it. |
| You find another name | Do not test it. Ask your teacher. |

## What Success Looks Like

You can show three distinct host responses, one sentence about virtual-host
identity, one sentence about scope, and the flag. Submit the lab flag.
