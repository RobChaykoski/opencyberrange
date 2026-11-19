# Cloud posture scanner

A small teaching scanner for MinIO, LocalStack IAM, Kubernetes manifests, and
plaintext secrets. It writes `findings.json` and can index the findings into
OpenSearch for the Sentinel-like dashboards.

## Run

```bash
docker compose --profile tools run --rm scanner \
  --root /workspace \
  --minio-endpoint http://minio:9000 \
  --minio-user "$MINIO_ROOT_USER" \
  --minio-password "$MINIO_ROOT_PASSWORD" \
  --localstack-endpoint http://localstack:4566 \
  --opensearch-url http://opensearch:9200
```

The container does not mount the repository by default. Add a volume in the
Compose service or pass a directory that is present in the image if you want
manifest scanning. Object-store and IAM scanning work without a mount.

## Checks

- public bucket policy;
- missing bucket versioning;
- wildcard IAM action or resource;
- access key older than 90 days;
- privileged container, host network, hostPath, root user, or privilege
  escalation in Kubernetes YAML;
- possible plaintext password, secret, AWS key, or private key.

## Limitations

- This is not a compliance scanner.
- It does not prove exploitability.
- It can produce false positives; the learner must validate each finding.
- It does not scan a real cloud account.
