# Exercise W1.9: TLS, Cookies, and Security Headers

## Before You Begin

Target: `http://secure.lab/` port `80`. No credentials are required.

This lab uses **HTTP**, so the TLS terms below are conceptual here. Do not run
TLS checks against another host. If your teacher provides an HTTPS target, use
only that target.

## Words to Know

| Term | Meaning |
|---|---|
| **Certificate** | A signed statement binding a name to a public key. |
| **SAN** | Subject Alternative Name: a name listed in a certificate. |
| **Issuer** | The certificate authority that signed the certificate. |
| **Validity** | The start and end dates of a certificate. |
| **TLS** | The protocol that protects HTTPS traffic. |
| **HSTS** | A header that tells browsers to use HTTPS for future requests. |
| **CSP** | Content-Security-Policy: restricts which sources a page may load. |
| **X-Content-Type-Options** | Prevents some content-type sniffing. |
| **Referrer-Policy** | Controls how much referrer information is sent. |
| **Secure cookie** | A cookie sent only over HTTPS. |
| **HttpOnly** | A cookie attribute that blocks JavaScript access. |
| **SameSite** | A cookie attribute that limits cross-site sending. |

## Walkthrough

### Step 1: Confirm the target

Confirm `secure.lab` port `80`. Stop on any mismatch.

### Step 2: Read the root headers

```bash
curl -I http://secure.lab/
```

Record the status, `Server`, cache headers, and any security headers. Note that
the lab is HTTP, so `Strict-Transport-Security` is a conceptual control here.

### Step 3: Read the diagnostics endpoint

```bash
curl -I http://secure.lab/headers.php
```

Look for `X-Debug-Mode` and `X-Secret-Key`. The lab advertises
`X-Debug-Mode: enabled` and carries the training flag in `X-Secret-Key`.

### Step 4: Retrieve the flag

```bash
curl -I http://secure.lab/headers.php | grep -o 'OCR{[^}]*}'
```

Copy the complete `OCR{...}` value into the exercise panel.

### Step 5: Classify the controls

| Observation | Classification | Why |
|---|---|---|
| A header is missing | Missing control | It may matter, but context is required. |
| A header is present but weak | Weak configuration | Not automatically exploitable. |
| A cookie lacks `Secure` on HTTP | Contextual risk | The lab is HTTP; do not overclaim. |
| A debug header is enabled | Information exposure clue | Confirm with the lab owner. |
| A flag appears in a header | Training token | Not a real secret or vulnerability. |

A missing header is not automatically a vulnerability. Severity requires context
and impact.

## Evidence

| Field | Your note |
|---|---|
| URL | `http://secure.lab/` |
| Status | |
| Security headers observed | |
| `X-Debug-Mode` | |
| `X-Secret-Key` | Redact the value in shared notes |
| Cookie attributes observed | |
| Missing controls | |
| Confidence | Low / Medium / High |
| What the evidence does not prove | |

## Rules

- Do not claim exploitability from a missing header.
- Do not copy cookie or token values into shared notes.
- Do not run TLS commands against a public or different host.
- Do not test another port.

## If You Get Stuck

| Problem | Safe next step |
|---|---|
| No security headers | Record the absence; do not overclaim. |
| `headers.php` is 404 | Recheck the exercise path. |
| Flag not in output | Recheck `X-Secret-Key` and the exact endpoint. |
| TLS warning | This lab is HTTP; confirm the target. |
| A cookie value appears | Redact it. |

## What Success Looks Like

You can show the header observations, the flag, one missing/weak control, and a
contextual-risk statement that does not claim exploitability. Submit the lab flag.
