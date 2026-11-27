# Exercise 1.4: Leaked TrailGuard Service Token

## Before You Begin

- [ ] Launched the exercise and opened the lab browser or a terminal
- [ ] `trailguard-nhi.lab` resolves to the target shown in the panel
- [ ] You can reach `http://trailguard-nhi.lab:8080`

## Scenario

TrailGuard AI reviews vendor evidence and exports client audit records. Its
worker runs as the non-human identity `svc-trailguard-bot`. Marcus Chen enabled
HTTP debug logging during the last rollout, and the logger wrote a live bearer
token into the service logs.

The internal audit API trusts the token without checking which workload is
presenting it. The token also carries more scope than the worker needs.

Your job is to find the credential, use it against the internal API, and read
the LumenPay audit exceptions. Then explain how the identity and the logging
should have been designed.

## Your Objectives

- Read the service health page and note the identity's scopes
- Open the debug logs and find the leaked bearer token
- Call the audit API without a token and confirm the refusal
- Use the leaked token to read the audit records and capture the flag
- Name the logging, scoping, binding, and rotation controls that failed

## Background: Why a Leaked Token Matters

A bearer token is a capability. Anyone who holds it can use it until it expires
or is revoked. When the token belongs to a service identity, the attacker does
not need a password, MFA, or a session. They only need the string.

```text
level=debug component=trailguard msg="refreshing service token"
level=debug component=trailguard msg="Authorization: Bearer ocr-svc-..."
```

The defect is not only the logger. It is the combination of a secret in a log,
an API that accepts it from any workload, and scopes broader than the task.

## Walkthrough

### Step 1: Review the service identity

Open `http://trailguard-nhi.lab:8080`. The page lists
`svc-trailguard@trailline.internal` and its scopes: `audit:read`,
`audit:export`, and `directory:read`.

### Step 2: Read the logs

Open `http://trailguard-nhi.lab:8080/logs`, or use the terminal:

```bash
curl -s http://trailguard-nhi.lab:8080/api/logs
```

Find the line that begins `Authorization: Bearer`. Copy the token that follows.

### Step 3: Confirm the API rejects anonymous access

```bash
curl -s -o /dev/null -w '%{http_code}\n' \
  http://trailguard-nhi.lab:8080/api/internal/audit
```

The API returns `401`. It needs a bearer token.

### Step 4: Use the leaked token

```bash
curl -s -H 'Authorization: Bearer ocr-svc-trailguard-7c1e4a9b' \
  http://trailguard-nhi.lab:8080/api/internal/audit
```

The response contains the LumenPay audit exceptions and the export marker, which
is the flag. Copy the `OCR{...}` value into the exercise flag box.

## What Just Happened?

You used a credential that was never meant to leave the workload. The application
did not distinguish a token used by the TrailGuard worker from a token used by a
learner with `curl`. The token's scopes allowed an export even though the task
only needed read access.

This is a **non-human identity** incident. The missing controls are:

- secret redaction in logs;
- audience and workload binding;
- least-privilege scopes;
- short lifetimes and automatic rotation;
- alerting on unexpected token use.

## What Should Happen After Discovery?

Finding the token is the start of an incident, not the end. Use this lifecycle:

| Step | Action | Why |
|---|---|---|
| 1 | **Revoke the token** | Stops the current credential from working, including any copy an attacker holds |
| 2 | **Issue a replacement** | Restores the worker with a new credential and only the scopes it needs |
| 3 | **Rotate automatically** | Removes the stale secret and prevents the same long-lived token from recurring |
| 4 | **Review logs for use** | Shows whether the token was used, from where, and what was accessed |
| 5 | **Reduce scopes** | Limits the blast radius if the next credential leaks |

Revocation contains the incident. Log review establishes scope. Replacement and
rotation recover the service. Scope reduction prevents a repeat. Do not skip
straight to “change the password” and leave the old token valid.

## Concept Check

??? question "What should happen first after a leaked service token is discovered?"
    A. Wait for it to expire.  
    B. Revoke the token.  
    C. Reduce the scopes only.  
    D. Delete the logs.

    **Correct answer: B.** Revoke first to stop the credential working. Then
    review the logs, issue a least-privilege replacement, rotate automatically,
    and reduce scopes. Deleting the logs destroys evidence.

## Defensive Controls

- **Redact at the logging layer.** Strip `Authorization`, cookies, and
  token-shaped values before they reach disk or a log aggregator.
- **Bind the token.** Use workload identity, mTLS, or a proof-of-possession
  token so a copied string is not enough.
- **Scope the identity.** Grant only the API and action the worker needs. Do not
  reuse a broad deployment token for a read-only review.
- **Keep lifetimes short.** Issue a token per task and rotate on a schedule.
- **Alert on anomalies.** A token used from a new workload, a new network, or
  outside the scheduled export window is suspicious.
- **Rotate on exposure.** Treat a leaked token as a credential incident: revoke,
  reissue, and review the audit log.

## Review Questions

1. Which log line leaked the credential, and what should the logger have written
   instead?
2. The API returned `401` without a token. Why is that not enough protection?
3. Which scope removal would have prevented the export?
4. What evidence would prove whether the token was used by TrailGuard or by an
   attacker?
