# Simulated cloud range

Local reference stack for the labs described in
[Simulated cloud](../../docs/SIMULATED-CLOUD.md). It is **not** part of the
production OpenCyberRange deployment.

Students practise IAM policy, storage security, secrets management, detection,
and incident response against synthetic services, with no cloud account and no
real credentials.

## Services

| Service | Role | URL |
|---|---|---|
| Keycloak | Entra-like OIDC identity provider | http://localhost:8080 |
| OpenLDAP | Directory for identity-federation practice | `ldap://localhost:389` |
| MinIO | S3-compatible storage and evidence | http://localhost:9000 |
| MinIO console | Local administration | http://localhost:9001 |
| Vault | Key Vault-like secret store | http://localhost:8200 |
| OpenSearch | Log store | http://localhost:9200 |
| OpenSearch Dashboards | Sentinel-like search and dashboards | http://localhost:5601 |
| n8n | Logic Apps-like automation | http://localhost:5678 |
| LocalStack | AWS-like IAM, S3, Secrets Manager, CloudTrail | http://localhost:4566 |
| Azurite | Azure Storage-compatible Blob/Queue/Table | http://localhost:10000–10002 |
| Wazuh manager |Optional SIEM manager for the `siem` profile | `localhost:1514/1515/55000` |
| Scanner | Posture scanner for MinIO, IAM, Kubernetes, and secrets | on demand |

Kubernetes is host-side. Use `kind` or `k3d`; do not run a privileged cluster
inside this Compose stack.

## Quick start

```bash
cp .env.example .env
# Change every password in .env before use.

docker compose up -d                       # core services
docker compose --profile aws up -d         # add LocalStack
docker compose --profile azure up -d       # add Azurite
docker compose --profile siem up -d        # add Wazuh
docker compose --profile tools up -d --build scanner
```

Check:

```bash
docker compose ps
curl -fsS http://localhost:9200/_cluster/health
curl -fsS http://localhost:9000/minio/health/live
```

## First-run setup

### Keycloak

The `ocr-cloud` realm, roles, and clients are imported on first start. No user
passwords are stored in the repository. Create the lab users after the first
start, either in the admin console or with `kcadm.sh`:

- console: http://localhost:8080/admin

```bash
docker compose exec keycloak /opt/keycloak/bin/kcadm.sh config credentials \
  --server http://localhost:8080 --realm master \
  --user "$KEYCLOAK_ADMIN" --password "$KEYCLOAK_ADMIN_PASSWORD"

docker compose exec keycloak /opt/keycloak/bin/kcadm.sh create users -r ocr-cloud \
  -s username=student -s enabled=true -s email=student@example.invalid

docker compose exec keycloak /opt/keycloak/bin/kcadm.sh set-password -r ocr-cloud \
  --username student --new-password "$STUDENT_PASSWORD"

docker compose exec keycloak /opt/keycloak/bin/kcadm.sh add-roles -r ocr-cloud \
  --uusername student --rolename student --rolename cloud-analyst
```

Create an `auditor` user with the `cloud-auditor` role the same way. The realm
has `sslRequired: none` for local HTTP only.

### MinIO buckets

Create the lab buckets with the console or `mc`:

```bash
docker run --rm --network ocr-cloud-control \
  -e MC_HOST_local="http://ocr-cloud-admin:change-me-minio@minio:9000" \
  minio/mc mb --ignore-existing local/evidence local/tofu-state local/patient-data
```

Set the admin password to match `.env`. For the public-bucket lab, a learner
will intentionally create a public policy and then remove it.

### Vault

Dev mode starts unsealed with the root token from `.env`. Seed a lab secret:

```bash
export VAULT_ADDR=http://localhost:8200
export VAULT_TOKEN=change-me-vault
vault kv put secret/healthcare-prod/app username=svc-cloud app_secret=example-not-a-secret
```

Never use Vault dev mode outside this range.

### OpenSearch

Create the event index:

```bash
curl -X PUT http://localhost:9200/cloud-events -H 'Content-Type: application/json' -d '{
  "mappings": {
    "properties": {
      "@timestamp": {"type": "date"},
      "event": {"type": "keyword"},
      "user": {"type": "keyword"},
      "source_ip": {"type": "ip"},
      "app": {"type": "keyword"},
      "action": {"type": "keyword"},
      "outcome": {"type": "keyword"}
    }
  }
}'
```

Seed the sample events:

```bash
curl -s -X POST http://localhost:9200/_bulk \
  -H 'Content-Type: application/x-ndjson' \
  --data-binary @datasets/cloud-events.ndjson
```

### OpenTofu

```bash
cd opentofu/aws-local
tofu init -backend-config=backend.hcl.example
tofu apply -var student_id=s42
```

The example creates a bucket, an intentionally broad IAM policy, and a secret.
The learner replaces the policy with a least-privilege version and proves the
denied actions.

### Kubernetes

```bash
k3d cluster create ocr-cloud --agents 1
kubectl apply -f k8s/rbac-lab.yaml
kubectl apply -f k8s/secret-lab.yaml
kubectl apply -f k8s/network-policy.yaml
```

The manifests include an intentionally over-permissive role, a lab-only secret,
and a default-deny network policy. Read `k8s/README.md` before applying.

### Scanner

```bash
docker compose --profile tools run --rm scanner \
  --root /workspace \
  --minio-endpoint http://minio:9000 \
  --minio-user "$MINIO_ROOT_USER" \
  --minio-password "$MINIO_ROOT_PASSWORD" \
  --localstack-endpoint http://localstack:4566
```

Mount the repository or a lab directory if you want the scanner to inspect
manifests. The script also accepts `--skip-*` flags and writes `findings.json`.

## Lab scenarios

- [OAuth consent incident](labs/ir-oauth-consent.md)
- [Compromised storage account](labs/compromised-storage-account.md)
- [Excessive IAM privilege](labs/excessive-iam-privilege.md)
- [Posture scan and triage](labs/posture-scan-triage.md)

Each lab states the Azure concept, the local service, the learner tasks, the
evidence, and the reset step.

## Reset

```bash
docker compose down -v
```

`-v` deletes the local volumes, including MinIO evidence and Vault dev data.
For a classroom, use a per-learner prefix and a reset job that deletes only that
prefix.

## Safety

- Synthetic data only. No real patient, learner, or institutional data.
- No real cloud key, API key, or payment method.
- No real malware.
- Do not publish the stack to a public interface. The ports bind to `127.0.0.1`.
- Change every `.env` secret before a class.
- Pin images by digest for a release.
- Keep this stack off the production network.

## Design references

- [Simulated cloud design](../../docs/SIMULATED-CLOUD.md)
- [AI governance and security pathway](../../docs/AI-GOVERNANCE-AND-SECURITY-PATHWAY.md)
- [Supply chain security pathway](../../docs/SUPPLY-CHAIN-SECURITY-PATHWAY.md)
- [Progressive disclosure](../../docs/INFORMATION-DESIGN-PROGRESSIVE-DISCLOSURE.md)
