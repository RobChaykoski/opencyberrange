# ocr-labd host agent (spike)

Status: **spike; do not enable on production.** This directory validates the
boundary proposed in
[ADR 0007](../docs/decisions/0007-docker-host-isolation.md), not a finished
orchestrator.

The agent is a small stdlib HTTP service that binds to loopback and requires a
bearer token. It exposes a fixed operation list:

- `spawn`, `stop`, `status`;
- `ensure_isolation`;
- `mirror_gretap`;
- `logs`.

`GET /v1/status/<lab_id>` is implemented read-only: it validates the lab id and
runs a fixed `docker inspect` on `ocr-lab-<lab_id>`. Every other mutating route
returns `501 not_implemented`. The agent never exposes arbitrary `exec`, image
build, volume, or host-filesystem operations, and the lab id never reaches a
shell.

## Run locally

```bash
export OCR_LABD_TOKEN="$(python3 -c 'import secrets; print(secrets.token_urlsafe(32))')"
python3 platform/labd/ocr_labd.py --host 127.0.0.1 --port 8099
curl -s http://127.0.0.1:8099/health
curl -s -H "Authorization: Bearer $OCR_LABD_TOKEN" \
  http://127.0.0.1:8099/v1/capabilities
curl -s -H "Authorization: Bearer $OCR_LABD_TOKEN" \
  http://127.0.0.1:8099/v1/status/linux-1
```

`status` returns `state`, `running`, `paused`, `restarting`, `oom_killed`,
`exit_code`, `started_at`, and `finished_at`. It returns `404` when the container
does not exist, `400` for an invalid lab id, and `503` when Docker cannot answer.

The token can come from `OCR_LABD_TOKEN` or `--token-file` (default
`/etc/ocr-labd/token`). Every mutating request and denial is appended to
`--audit-log` (default `/var/log/ocr-labd/audit.jsonl`).

## Install as a systemd service (spike host only)

```bash
sudo useradd --system --shell /usr/sbin/nologin ocr-labd
sudo install -d -m 0750 -o ocr-labd -g ocr-labd /etc/ocr-labd /var/log/ocr-labd
sudo install -m 0600 -o ocr-labd -g ocr-labd /dev/null /etc/ocr-labd/token
python3 -c 'import secrets; print(secrets.token_urlsafe(32))' | \
  sudo tee /etc/ocr-labd/token >/dev/null
sudo install -m 0644 deploy/systemd/ocr-labd.service /etc/systemd/system/
# Edit ExecStart if the checkout is not /opt/opencyberrange.
sudo systemctl daemon-reload
sudo systemctl enable --now ocr-labd.service
```

The unit uses `NoNewPrivileges=yes` and `ProtectSystem=strict`. That is
deliberately stricter than the final agent, which will need the Docker group and
network-namespace privileges. Adjust only after the security review.

## Validation

```bash
python scripts/check-labd-agent.py
```

The check starts the server on an ephemeral port, verifies `/health`, rejects a
missing token, verifies `/v1/capabilities`, exercises `status` with a fake
provider and with mocked `docker inspect` results, and confirms mutating routes
return `501`.

## Validation record

`status` was exercised on the development host against a live `ocr-backend`
container on 24 November 2026 with `--container-prefix ocr-`:

| Request | Result |
|---|---|
| `/health` | `200` |
| `/v1/status/backend` without a token | `401` |
| `/v1/status/backend` with a token | `200`, `state: running`, `running: true` |
| `/v1/status/does-not-exist` | `404` |
| `/v1/status/Bad_ID` | `400` |
| Audit log | Denial, not-found, and invalid-id lines written |

## Next steps

1. Validate `status` against a real lab container, then replace the 501
   handlers one operation at a time, starting with `stop`.
2. Authenticate the backend with a short-lived token or mTLS.
3. Add idempotency keys and per-operation audit fields.
4. Add response schemas and a client adapter in `docker_manager.py`.
5. Run the lab harness for network, ICS, and RangeBox labs.
6. Remove the backend Docker socket mount only after the harness passes.
