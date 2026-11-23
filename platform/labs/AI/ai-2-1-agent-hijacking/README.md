# Poisoned Vendor Report and TrailGuard AI Agent Hijacking

TrailGuard AI is Trailline's simulated GRC intake agent. It reads a vendor SOC 2
report, summarises it, and can call two internal tools: a vendor lookup and an
audit-record export.

The target treats the vendor document as trusted context. A report author can
therefore embed instructions that the agent follows. The exercise is to make the
agent export client audit records through the over-privileged
`svc-trailguard-bot` identity and capture the internal marker.

## Target

- `http://trailguard.lab:8080` — web intake form
- `http://trailguard.lab:8080/api/ticket` — POST form field `ticket`
- `http://trailguard.lab:8080/health` — health probe

## Run locally

```bash
cd platform/labs/AI/ai-2-1-agent-hijacking
docker compose up --build
```

Then open `http://localhost:8080` or use the API:

```bash
curl -s -X POST \
  --data-urlencode 'ticket=Vendor: LumenPay. SOC 2 readiness review.' \
  http://localhost:8080/api/ticket
```

## Safety

The service is a deterministic mock. It has no model weights, no external
network access, and no real client, vendor, or employee data. The container runs
read-only, unprivileged, with all capabilities dropped.

## Design notes

- The benign report produces a summary and no tool calls.
- The payload must name an instruction to the assistant and an export action.
- The vulnerability is the missing boundary between retrieved content and
  instructions, combined with an over-broad service identity and export tool.
- Defensive controls: tool allow-lists, argument schemas, scoped credentials,
  explicit human approval for exports, and tool-call provenance logging.
