# MinIO object storage: design note

Status: **proposal only** (18 November 2026). No runtime configuration is
changed by this document.

Audience: deployment operators, security reviewers, and procurement.

## 1. Question

Should OpenCyberRange add [MinIO](https://github.com/minio/minio) as a
self-hosted, S3-compatible object store for backups and generated artifacts?

The current platform already treats object storage as the long-term home for
wiki builds, backups, and evidence artifacts in the HA design
([HA and Kubernetes](HA-AND-KUBERNETES.md)). The single-host Compose profile
still uses local volumes and an off-host backup copy. MinIO is one way to close
that gap without depending on a public cloud account.

## 2. What MinIO provides

- S3-compatible API, so existing S3 tooling and rclone work unchanged.
- Erasure-coded storage on a single node with multiple drives, or a distributed
  multi-node deployment.
- Bucket versioning, lifecycle rules, object lock (WORM), and replication.
- Server-side encryption with a local KMS or an external KMS.
- Bucket policies and service accounts with scoped credentials.
- Bucket notifications and audit logs.

MinIO is not a database, a shared filesystem, or a replacement for PostgreSQL.
It is an object store: immutable blobs addressed by key. Do not put the live
database files, WireGuard state, or container image layers on it.

## 3. Licensing boundary

The MinIO server is distributed under the **GNU AGPL v3**. The client SDKs are
Apache-2.0. Running MinIO as a separate service for backups is ordinary
aggregation and does not change the licence of the OpenCyberRange application.
Bundling MinIO inside an OpenCyberRange image, modifying it, or offering it as
part of a hosted service needs legal review and may trigger AGPL source-offer
obligations.

The platform itself remains under its existing PolyForm Noncommercial licence.
This note does not relicense the platform.

Decision required before adoption: deployment as a separate container or host
service, with no MinIO code linked into the application.

## 4. Fit with the current backup path

`scripts/backup-production.sh` already:

1. creates a PostgreSQL dump;
2. hashes it;
3. encrypts it with GPG when `BACKUP_GPG_RECIPIENT` is set;
4. copies the encrypted set to one or more transports.

The existing rclone transport is the natural integration point:

```bash
BACKUP_RCLONE_REMOTE='ocr-minio:ocr-backups/prod'
```

An rclone S3 remote points at MinIO. The files remain GPG-encrypted before they
leave the host, so MinIO is transport and retention, not the only protection.

Recommended bucket layout:

```text
ocr-backups/
  prod/
    database/YYYY/MM/ocr-backup-<stamp>.dump.gpg
    database/YYYY/MM/ocr-backup-<stamp>.dump.sha256
    config/ocr-backup-<stamp>-env.gpg
  restore-drills/
  releases/
```

Use separate buckets or prefixes per environment. Never let development write
to the production prefix.

## 5. Deployment options

| Option | Shape | Fit | Main risk |
|---|---|---|---|
| Development single drive | One container, one volume | Local testing only | No redundancy; not a backup target |
| Single node, four drives | One MinIO server, four data drives, erasure coding | Small production or a second host | Host loss is still a full outage |
| Distributed MinIO | Four or more nodes, four or more drives each | HA control plane | More stateful infrastructure to operate |
| External S3-compatible service | Wasabi, Backblaze B2, AWS S3, institutional S3 | Teams without storage operations | Recurring cost and data-residency review |

The reference recommendation for the current single-host deployment is a
**single-node, four-drive MinIO service on a separate host or separate physical
disks**, with an off-site copy to institutional storage. A MinIO container on
the same host and same disk as PostgreSQL does not protect against host loss.

For the HA profile, use distributed MinIO or an external S3 service. Do not run
a single MinIO container as the only copy for an HA control plane.

## 6. Bucket policy

Minimum policy for the backup writer:

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": ["s3:PutObject", "s3:AbortMultipartUpload", "s3:ListBucket"],
      "Resource": [
        "arn:aws:s3:::ocr-backups",
        "arn:aws:s3:::ocr-backups/prod/*"
      ]
    }
  ]
}
```

The application and backup writer must not use the MinIO root account. Use one
service account per job, and separate read-only credentials for restore drills.
The console should be disabled or bound to an administrative network only.

## 7. Protection settings

- **Versioning:** on for the backup and evidence buckets.
- **Object lock:** on for evidence and release artifacts that must not be
  overwritten; use a retention period that matches the institution's schedule.
- **Lifecycle:** expire incomplete multipart uploads, transition old backups to
  colder storage if the backend supports it, and delete only after the
  off-site copy and restore drill have passed.
- **Encryption:** keep the existing GPG envelope encryption. Enable SSE as a
  second layer if the KMS is operated properly.
- **Immutability:** object lock is not a substitute for an off-site copy. A
  compromised MinIO administrator can still delete a bucket if the backend does
  not enforce WORM.

## 8. Network and security

- Terminate TLS at the MinIO service or a reverse proxy; never expose the S3
  port in plaintext outside the private network.
- Restrict access to the backup host and the restore workstation. The MinIO
  console is not a learner-facing surface.
- Keep MinIO off the lab network and out of the RangeBox egress path.
- Pin the MinIO image by digest in any deployment file and include it in the
  supply-chain lock and vulnerability scan.
- Audit bucket policy changes, service-account creation, and object-lock
  changes.
- Test restore credentials separately from backup credentials.

## 9. Performance notes

- Backups are large sequential writes. Throughput matters more than IOPS.
- Use multipart upload for large dumps; rclone handles this with
  `--s3-chunk-size` and `--s3-upload-concurrency`.
- Avoid millions of tiny objects. One dump plus one checksum plus one config
  archive per run is the intended shape.
- Distributed MinIO needs consistent clocks (NTP) and a low-latency private
  network. Erasure coding adds CPU and network overhead.
- Measure restore time, not only upload time. A backup that restores in six
  hours does not meet an RTO of one hour.
- Keep local retention long enough to restore without the network, then rely on
  MinIO and off-site copies for disaster recovery.

## 10. Restore drill

The existing drill remains the acceptance test:

```bash
rclone copy ocr-minio:ocr-backups/prod/database/2026/11/ocr-backup-<stamp>.dump.gpg .
rclone copy ocr-minio:ocr-backups/prod/database/2026/11/ocr-backup-<stamp>.dump.sha256 .
gpg --decrypt --output ocr-backup-<stamp>.dump ocr-backup-<stamp>.dump.gpg
sha256sum -c ocr-backup-<stamp>.dump.sha256
bash scripts/restore-drill.sh
```

Record the download time, decrypt time, restore time, row counts, and any
warnings. A successful upload is not evidence of recoverability.

## 11. Migration path

1. Stand up MinIO on a non-production host with four data drives.
2. Create the `ocr-backups` bucket, enable versioning, and create a scoped
   writer account.
3. Configure an rclone S3 remote and run a manual backup to a test prefix.
4. Download, verify, decrypt, and restore that copy into a scratch database.
5. Add the MinIO remote as a second `BACKUP_RCLONE_REMOTE` target and keep the
   existing off-host copy until two drills pass.
6. Move the primary off-host copy to MinIO and retain the old copy for the
   agreed overlap period.
7. Add monitoring for bucket age, failed uploads, capacity, and certificate
   expiry.

Do not move wiki builds or evidence artifacts to MinIO in the same change. Those
need an object-store abstraction and presigned-URL design first.

## 12. Recommendation

Adopt MinIO **only as an additional S3-compatible backup target** when the
institution can operate another stateful service and accepts the AGPL boundary.
Keep the existing GPG envelope encryption, off-site copy, and restore drill.

If the institution already provides S3-compatible storage, use that instead.
MinIO is a good fit for a lab, a teaching institution, or a private deployment
that wants no cloud dependency. It is not automatically the right choice for a
single-disk host, and it does not remove the need for an off-site copy.

## 13. Open questions

- Who operates MinIO, and what is the on-call path for a failed drive?
- Where is the off-site copy, and what is its retention?
- Is object lock required for evidence, or is versioning sufficient?
- Does the institution's legal review accept AGPL v3 for a separate service?
- What is the measured restore time from MinIO over the production network?
