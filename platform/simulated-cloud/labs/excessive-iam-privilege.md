# Lab: excessive IAM privilege

**Azure concept:** a role assignment grants more access than the workload needs.

**Local simulation:** LocalStack IAM user with `s3:*` on `*`, then a scoped
policy.

**Goal:** enumerate effective permissions, rewrite the policy, and prove the
allowed and denied actions.

## Scenario

The `s42-analyst` user was created for a reporting job. The policy allows every
S3 action on every resource. The learner must reduce it to read and write on the
`patient-data` bucket only.

## Local mapping

| Azure concept | Local service |
|---|---|
| Role assignment | IAM user policy attachment |
| Custom role | IAM policy document |
| Resource scope | Bucket ARN |
| Access Analyzer | Manual enumeration and scanner finding |
| Activity log | LocalStack CloudTrail-like events |

## Tasks

1. List the user's attached policies and the policy document.
2. Identify every action and resource the policy allows.
3. Create a least-privilege policy for `patient-data`:
   - `s3:ListBucket` on the bucket;
   - `s3:GetObject` and `s3:PutObject` on the objects;
   - nothing else.
4. Attach the new policy and detach the broad one.
5. Test allowed actions: list the bucket, read an object, write an object.
6. Test denied actions: list another bucket, delete an object, read IAM.
7. Record the before/after policy and the test results.
8. Write a short explanation of why `s3:*` on `*` is risky.

## Evidence

- original policy JSON;
- least-privilege policy JSON;
- attachment diff;
- allowed and denied test output;
- explanation for a release manager.

## Rubric

| Dimension | Weight |
|---|---:|
| Permission enumeration | 25% |
| Least-privilege policy | 30% |
| Verification | 25% |
| Explanation | 20% |

## Reset

```bash
cd opentofu/aws-local
tofu destroy -var student_id=s42
tofu apply -var student_id=s42
```

## Safety

- Synthetic account and credentials only.
- No real cloud key or account.
- Do not leave a wildcard policy attached after the lab.
