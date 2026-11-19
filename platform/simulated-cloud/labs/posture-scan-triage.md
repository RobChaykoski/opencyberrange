# Lab: posture scan and triage

**Azure concept:** Microsoft Defender for Cloud surfaces a mix of high and low
severity findings. The analyst must prioritise by exposure and business impact.

**Local simulation:** the `scanner` service reviews MinIO policies, LocalStack
IAM, Kubernetes manifests, and plaintext secrets.

**Goal:** triage the finding list, reproduce the top findings, fix them, and
rescan.

## Tasks

1. Run the scanner against the local stack and a lab directory.
2. Read the finding list. Group by severity and resource.
3. Choose the top three to fix first. Explain the exposure and business impact.
4. Reproduce each finding with a command or policy document.
5. Fix the configuration.
6. Rescan and confirm the finding is gone.
7. Record the residual risk and the review date.
8. Map each finding to a NIST CSF 2.0 control and an Azure concept.

## Finding examples

| Finding | Azure concept | Local service |
|---|---|---|
| Public bucket policy | Public blob container | MinIO |
| Wildcard IAM policy | Excessive role assignment | LocalStack IAM |
| Stale access key | Access key rotation | LocalStack IAM |
| Privileged container | AKS pod security | k3s/kind |
| Plaintext secret | Key Vault | Vault |

## Evidence

- scanner output before and after;
- prioritisation table with rationale;
- reproduction command for each fixed finding;
- fix diff;
- residual risk and control mapping;
- rescan result.

## Rubric

| Dimension | Weight |
|---|---:|
| Prioritisation | 30% |
| Reproduction | 20% |
| Fix quality | 25% |
| Verification and rescan | 15% |
| Control mapping and report | 10% |

## Run

```bash
docker compose --profile tools run --rm scanner \
  --root /workspace \
  --minio-endpoint http://minio:9000 \
  --minio-user "$MINIO_ROOT_USER" \
  --minio-password "$MINIO_ROOT_PASSWORD" \
  --localstack-endpoint http://localstack:4566
```

Mount the repository or a lab directory at `/workspace` if the scanner should
inspect manifests.

## Safety

- The scanner is a teaching tool, not a compliance product.
- Do not scan a real cloud account or a production cluster.
- Do not include real secrets in the finding output.
