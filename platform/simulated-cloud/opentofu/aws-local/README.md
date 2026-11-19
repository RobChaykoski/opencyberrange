# OpenTofu lab: AWS-like local stack

This example targets LocalStack and stores state in MinIO. It creates:

- an S3 bucket with versioning and public-access blocking;
- an IAM user with an intentionally broad policy in `lab_mode`;
- an access key;
- a Secrets Manager secret.

The learner replaces the broad policy with a least-privilege policy and proves
the denied actions.

## Run

```bash
cp backend.hcl.example backend.hcl
# Edit the MinIO endpoint and credentials.
tofu init -backend-config=backend.hcl
tofu apply -var student_id=s42
tofu output
```

## Fix the policy

Set `lab_mode=false`:

```bash
tofu apply -var student_id=s42 -var lab_mode=false
```

Then test:

```bash
aws --endpoint-url http://localhost:4566 s3 ls s42-patient-data
aws --endpoint-url http://localhost:4566 iam list-users
```

The first command should work with the scoped key; the second should fail.

## Destroy

```bash
tofu destroy -var student_id=s42
```

## Notes

- This is not real AWS. LocalStack is a simulator.
- The access key and secret are synthetic.
- Do not commit `backend.hcl`, `.terraform/`, or state files.
- The S3 backend must be created before `tofu init`; use `minio/mc` or the
  console to create the `tofu-state` bucket.
