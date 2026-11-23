# Context service (Release 6 MVP)

This service builds the policy context for a data action and asks OPA for a
decision. It is deliberately separate from the catalog: OpenMetadata remains the
authority of record, while this service holds a short-lived policy view.

## Endpoints

- `GET /health`
- `POST /context` — metadata lookup and hash
- `POST /decide` — metadata + OPA decision
- `POST /scan` — detect and redact publication-sensitive content
- `POST /scan-and-decide` — scan content, derive metadata, and ask OPA

All POST endpoints require `X-Context-Token` when `CONTEXT_SERVICE_TOKEN` is
set.

## Local development

```bash
cd services/context-service
CONTEXT_SERVICE_TOKEN=dev-context-token docker compose up --build
curl -s http://127.0.0.1:8090/health
```

Fixture metadata is in `fixtures/metadata.json`. Set `METADATA_MODE=http` and
`METADATA_LOOKUP_URL` to use the normalized OpenMetadata adapter endpoint.

## Decision example

```bash
curl -s -X POST http://127.0.0.1:8090/decide \
  -H 'Content-Type: application/json' \
  -H 'X-Context-Token: dev-context-token' \
  -d '{
    "subject": {"id": "user-1", "role": "student"},
    "resource": {"id": "dataset:lumenpay-audit", "type": "dataset"},
    "action": "export"
  }'
```

## Publication scan example

```bash
curl -s -X POST http://127.0.0.1:8090/scan-and-decide \
  -H 'Content-Type: application/json' \
  -H 'X-Context-Token: dev-context-token' \
  -d '{
    "source": "repo:public-docs",
    "text": "host 10.20.30.40 flag OCR{example_flag}",
    "subject": {"id": "user-1", "role": "instructor"},
    "action": "publish"
  }'
```

Detected classes are `private_ip`, `public_ip`, `internal_hostname`, `flag`,
and `secret`. The response contains a redacted copy, never the raw match.
`contains_infrastructure_metadata`, `contains_assessment_answer_key`,
`contains_secrets`, and `publication_safe` are passed to the same OPA policy as
an export decision.

## Tests

```bash
python -m pytest services/context-service/tests -q
```

Policy tests:

```bash
docker run --rm -v "$PWD/deploy/opa/policies:/policies" \
  openpolicyagent/opa:1.2.0 test /policies
```

## Integration rule

The platform calls this service only when `POLICY_CONTEXT_URL` is configured.
If the service or metadata is unavailable, the platform's
`POLICY_CONTEXT_FAIL_CLOSED` setting decides whether to block or allow. The
default is fail-closed for a restricted-data export path.
