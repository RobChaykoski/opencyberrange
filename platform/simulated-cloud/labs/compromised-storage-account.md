# Lab: compromised storage account

**Azure concept:** a storage account or blob container is left publicly readable.

**Local simulation:** a MinIO bucket with an anonymous read policy.

**Goal:** find the exposure, remove public access, prove the fix, and preserve
evidence.

## Scenario

`patient-data` is intended for an internal reporting service. A change request
adds an anonymous read policy so a vendor can download a file. The policy is
never removed. The bucket now exposes every object.

## Local mapping

| Azure concept | Local service |
|---|---|
| Storage account | MinIO server |
| Blob container | MinIO bucket `patient-data` |
| Container access level | Bucket policy |
| Defender for Cloud finding | Local posture scanner |
| Activity log | MinIO audit / `cloud-events` |

## Tasks

1. **Discover.** List buckets and policies. Which bucket is public? Use the
   console, `mc`, or the scanner.
2. **Confirm exposure.** Read an object without credentials and record the
   response.
3. **Scope the data.** List the objects and classify the synthetic contents.
4. **Contain.** Remove the anonymous policy and enable block-public-access.
5. **Protect.** Enable versioning and, where supported, object lock for evidence.
6. **Verify.** Repeat the anonymous read and confirm it is denied.
7. **Detect.** Write a Sigma rule or query for `bucket.policy.public`.
8. **Report.** Finding, impact, fix, evidence, and residual risk.

## Evidence

- public policy before the fix;
- anonymous read result before and after;
- object inventory and classification;
- fixed policy and versioning status;
- detection rule or query;
- report.

## Rubric

| Dimension | Weight |
|---|---:|
| Exposure confirmation | 20% |
| Scope and data classification | 20% |
| Containment and protection | 25% |
| Verification | 15% |
| Detection and report | 20% |

## Reset

```bash
# Recreate the bucket and remove the public policy.
docker run --rm --network ocr-cloud-control \
  -e MC_HOST_local="http://ocr-cloud-admin:change-me-minio@minio:9000" \
  minio/mc anonymous set none local/patient-data
```

Re-upload the synthetic objects and re-seed the event index.

## Safety

- Synthetic files only. Name them `synthetic-*.txt`.
- Do not use real patient data, real names, or real identifiers.
- Do not expose the MinIO port beyond `127.0.0.1`.
