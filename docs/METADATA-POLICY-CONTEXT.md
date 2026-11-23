# Metadata-driven policy context

Status: **Release 6 MVP design and scaffold**. OpenMetadata is the authority of
record; OPA is the decision engine; the platform and OpenDLP are enforcement
points. OpenMetadata is not called synchronously from an application request.

## Why a context service

A catalog is not a policy database. OpenMetadata owns classification, ownership,
lineage, jurisdiction, retention, frameworks, and controls, but it is a heavier
service with its own availability and latency profile. Putting it directly in a
download or export path makes every request depend on the catalog.

The context service holds a short-lived, materialized view of the metadata a
decision needs:

```text
Application / OpenDLP / OpenCyberRange
        |
        v
  context-service  <-- OpenMetadata (cached policy view)
        |          <-- OpenGRC (controls/risk)
        |          <-- Authentik (subject attributes)
        v
      OPA (local, stateless)
        |
        v
  allow / deny / mask / require_approval / audit
```

OPA never calls OpenMetadata. The context service builds one input document,
calls OPA, and returns the decision plus the policy version and metadata
snapshot hash.

## Metadata contract

A resource must carry these fields before it can receive a policy decision:

| Field | Required | Purpose |
|---|---|---|
| `id` | yes | Stable resource identifier used by the caller |
| `classification` | yes | `public`, `internal`, `confidential`, or `restricted` |
| `owner` | yes | Business owner for approval and escalation |
| `steward` | no | Operational contact |
| `contains_pii` | yes | Personal information |
| `contains_phi` | yes | Health information |
| `contains_pci` | yes | Payment-card data |
| `contains_infrastructure_metadata` | yes | Private/public addresses, internal hosts, topology |
| `contains_assessment_answer_key` | yes | Lab flags and expected answer values |
| `contains_secrets` | yes | Credentials, tokens, private keys |
| `publication_safe` | yes | Content has been reviewed and redacted for publication |
| `jurisdiction` | no | `canada`, `eu`, `us`, or another policy label |
| `retention` | no | Retention rule, for lifecycle policy |
| `frameworks` | no | `nist`, `pci`, `pipeda`, `ferpa`, and similar |
| `controls` | no | Control identifiers the resource is subject to |
| `training_data` | no | Synthetic lab data used for teaching |

Free-form tags are not policy inputs. OpenMetadata tags and custom properties
must map to this contract through a reviewed adapter.

## Decision input

```json
{
  "subject": {
    "id": "user-123",
    "role": "instructor",
    "groups": ["swocts-instructors"],
    "tenant": "swocts"
  },
  "resource": {
    "id": "reports:instructor:all",
    "type": "report"
  },
  "action": "export",
  "environment": {
    "ip": "203.0.113.10",
    "network": "corporate-vpn",
    "device_managed": true,
    "country": "CA"
  }
}
```

The context service enriches the resource from its metadata view and builds the
OPA input:

```json
{
  "subject": {"role": "instructor", "groups": ["swocts-instructors"]},
  "resource": {
    "id": "reports:instructor:all",
    "classification": "confidential",
    "contains_pii": true,
    "owner": "compliance",
    "jurisdiction": "canada",
    "frameworks": ["pipeda"],
    "training_data": false
  },
  "action": "export",
  "environment": {"device_managed": true, "network": "corporate-vpn"}
}
```

## Decision outcomes

| Outcome | Meaning | Enforcement |
|---|---|---|
| `allow` | Policy permits the action | Proceed |
| `deny` | Policy forbids the action | Block with a reason |
| `mask` | Proceed with redaction | Apply the resource-specific masker |
| `require_approval` | Human approval is required | Queue an approval, block the direct action |
| `warn` | Proceed and record a warning | Proceed, show a warning |
| `audit` | Record only | Proceed |

Every decision is logged with a decision id, policy version, metadata hash,
subject hash, resource id, action, and outcome. The log does not contain learner
PII or the full metadata payload.

## MVP policies

- Public resources are allowed.
- Students cannot export `restricted` resources.
- Student access to `training_data` with PII returns `mask`.
- PII exported to an external destination with Canadian jurisdiction requires
  approval (`pipeda`).
- Security analysts may read `restricted` resources.
- Unknown or missing metadata is denied.

## Publication and answer-key gate

The same context service scans content that is about to leave the controlled
environment. `POST /scan` returns a classification, redacted text, and findings.
`POST /scan-and-decide` feeds the derived metadata into OPA.

| Content | Action | Outcome |
|---|---|---|
| Secret material | `publish`, `export`, `external_share` | `deny` |
| Assessment answer key | `publish`, `external_share` | `deny` |
| Unreviewed content (`publication_safe=false`) | `publish` | `deny` |
| Infrastructure metadata | `export`, `external_share` | `require_approval` + redact |
| Assessment answer key | `export` | `require_approval` + redact |
| Reviewed internal content | `publish` | `allow` |

The detector categories are `private_ip`, `public_ip`, `internal_hostname`,
`cloud_metadata_endpoint`, `flag`, and `secret`. A finding stores a redacted
value and a digest; the raw match is never persisted or returned. The same
vocabulary is used by OpenDiscoveryEngine and by OpenGRC policies `PUB-001`
through `PUB-004`.

## Deployment

- `services/context-service` — FastAPI service, fixture metadata in development,
  OpenMetadata adapter in integration.
- `deploy/opa` — policy source and an OPA server for development.
- The platform calls the service only when `POLICY_CONTEXT_URL` is configured;
  otherwise the existing behaviour is unchanged.
- Start with the instructor dashboard report export. Extend to OpenDLP,
  workbook downloads, and OpenGRC evidence after the first path is proven.

## Non-goals for the MVP

- No synchronous OpenMetadata call in the request path.
- No full knowledge-graph or AI reasoning.
- No automatic classification by the platform; OpenDLP discovers, OpenMetadata
  records, and the platform enforces.
- No production OpenMetadata deployment until the contract, cache, and one
  enforcement path pass validation.
