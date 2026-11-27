# Security validation plan

This plan proves the isolation and authorization claims that matter for a
teaching deployment: a learner cannot reach another learner's container, an
instructor's data, or host infrastructure; every role sees only what it should;
and an account deletion survives a restore.

It is the detailed companion to the [release test plan](../RELEASE-TEST-PLAN.md).

## 1. Threat boundaries

| Boundary | Must never cross |
|---|---|
| Learner ↔ learner | containers, networks, volumes, evidence, flags, sessions |
| Learner ↔ instructor | cohort analytics, private notes, other learners' records |
| Learner ↔ host | Docker socket, host filesystem, management LAN, metadata service |
| Instructor ↔ platform admin | user deletion, break-glass, platform settings |
| Tenant ↔ tenant | PostgreSQL rows, exports, object ids |
| Platform ↔ GRC | learner rows, PCAP, payloads, prompts |

## 2. Isolation tests

### 2.1 Container

Run a lab, then inspect every container:

```bash
docker inspect <container> --format '{{json .HostConfig}}' | jq '{
  Privileged, NetworkMode, PidMode, IpcMode, CapAdd, CapDrop,
  ReadonlyRootfs, Binds, PortBindings
}'
```

Pass:

- `Privileged` is false.
- `NetworkMode` is not `host`.
- `PidMode` and `IpcMode` are not `host`.
- No bind of `/var/run/docker.sock`, `/`, `/home`, `/etc`, or a platform volume.
- No `0.0.0.0`/`::` published port.
- Capabilities are dropped or explicitly bounded.

The harness automates the start, health, isolation, port, flag, repeat, resource,
and teardown checks:

```bash
python scripts/lab_harness.py --lab <slug> --runs 1 --json lab-isolation.json
```

### 2.2 Network traversal

From the lab network (or the tester sidecar on that network), attempt:

```bash
getent hosts ocr-db ocr-backend ocr-valkey docker-socket-proxy
nc -z -w 2 ocr-db 5432
nc -z -w 2 ocr-backend 8000
nc -z -w 2 docker-socket-proxy 2375
nc -z -w 2 169.254.169.254 80
nc -z -w 2 host.docker.internal 2375
```

All must fail. A DNS answer for a control-plane name or an open port is a
release blocker. The lab may reach its own services only.

### 2.3 VPN separation

Use two test peers, A and B, on separate clients:

1. Connect both.
2. A reaches A's lab `/24`; B reaches B's.
3. From A, try B's `/24`, the rest of `10.100.0.0/16`, `10.255.0.0/16`, the
   management LAN, the database, and the host.
4. Repeat from B.
5. Confirm the peer routes only its own `/24`, not the whole range.

Pass: only the assigned lab `/24` is reachable. Record peer addresses privately;
do not put them in a public report.

### 2.4 Storage

- The lab has no host bind except the declared read-only lab source.
- The lab cannot read `workbook_data`, `backups_data`, `postgres_data`, or
  another learner's volume.
- Uploads are scoped to the uploader's tenant or course.
- The erasure/suppression ledger is not writable from a lab.

## 3. Authorization matrix

| Feature | Anonymous | Student | Instructor | Admin |
|---|---|---|---|---|
| View users | No | No | Course only | Yes |
| Delete users | No | No | No | Yes |
| View plaintext lab flag | No | No | No | Yes |
| Create course | No | No | Yes | Yes |
| Launch lab | No | Assigned only | Preview/own course | Yes |
| View cohort analytics | No | Own progress | Own course | All |
| Export learner data | No | Own | Course reports | Aggregate/all |
| Platform settings | No | No | No | Yes |
| Impersonate | No | No | No | Yes, audited |
| Break-glass | No | No | No | Time-boxed, reviewed |

Automated proof:

```bash
cd platform/backend
python -m pytest tests/test_access_matrix.py tests/test_authorization_matrix.py \
  tests/test_idor_matrix.py tests/test_route_authorization.py \
  tests/test_horizontal_privilege.py tests/test_institution_admin.py -q
```

Blackbox proof:

```bash
cd security-tests/karate
.\run-security-tests.ps1 -Tags '@security'
```

Rules:

- A UI guard is not authorization.
- Every route has an auth or permission dependency; `OCR_AUTHZ_STRICT=1` fails
  startup if one is missing.
- Tenant scope comes from the session, never a request header.
- An object read checks ownership, not just existence.

## 4. API security tests

| Test | How | Pass |
|---|---|---|
| BOLA / API1 | Two learners; request the other's object id | 403/404, no data |
| IDOR | Session, snapshot, share, evidence ids | 403/404 |
| JWT tampering | Change `sub`, `role`, `sec`, or signature | 401 |
| `alg=none` | Unsigned token | 401 |
| Refresh replay | Rotate then replay the old refresh token | 401 + reuse header |
| Session fixation | Inject a chosen session id | rejected |
| Rate limit | Login, registration, flag, report | 429 with a bounded window |
| Mass assignment | Send `role`/`is_admin` in a profile update | ignored |
| Upload | Anonymous/student, non-ZIP, no markdown, traversal | 401/403/400 |
| Path traversal | `chapter_dir`, about file paths | 400/404 |

Tooling:

- **Burp Suite**: intercept and replay role-based requests; test object ids and
  JWT claims.
- **OWASP ZAP**: baseline and authenticated scan on staging only.
- **Postman**: a saved collection per role for repeatable authorization checks.
- **StackHawk**: CI API scan with a disposable staging account.

Never run an active scanner against production.

## 5. Data export

A learner's export must include:

- account identity and profile (secrets excluded);
- courses and enrolments;
- sessions, completions, flag attempts, quiz attempts;
- achievements and certificates;
- progress and transcript data;
- consent state and history.

It must not include another learner, an instructor note about another learner,
a plaintext flag, a password hash, MFA secret, recovery code, or VPN private key.

```bash
cd platform/backend
python -m pytest tests/test_privacy.py tests/test_export_labels.py -q
```

## 6. Deletion and suppression

1. Create a disposable learner with a completion, achievement, avatar, VPN peer,
   and session.
2. Export; confirm the data is present.
3. Delete through the self-service path.
4. Confirm:
   - old access and refresh tokens return 401;
   - user and cascaded learning rows are gone;
   - avatar and VPN peer are gone;
   - the API rejects the deleted identity;
   - the suppression proof remains under a keyed subject hash.
5. Restore a pre-deletion database backup and the `workbook_data` suppression
   ledger.
6. Run `enforce_suppressions`.
7. Confirm the account does not reappear and cannot log in.

```bash
cd platform/backend
python -m pytest tests/test_erasure.py tests/test_purge_erased_accounts.py \
  tests/test_consent_revocation.py -q
```

A restore that resurrects the account is a release blocker.

## 7. Evidence and sign-off

| Test | Evidence | Reviewer |
|---|---|---|
| Container isolation | `lab-isolation.json` + inspect output | Lab platform |
| Network traversal | probe log | Security |
| VPN separation | two-peer drill log | Platform operations |
| Storage isolation | mount/volume inspection | Security |
| RBAC | pytest output + Karate report | Security |
| API authorization | pytest + Karate report | Security |
| Export | two-learner export diff | Privacy |
| Deletion/restore | deletion evidence page | Privacy + operations |

Do not publish learner rows, peer addresses, tokens, or real hostnames in the
evidence.

## Related

- [Release test plan](../RELEASE-TEST-PLAN.md)
- [Security events](../SECURITY-EVENTS.md)
- [Tenant isolation status](../TENANT-ISOLATION-STATUS.md)
- [Consent revocation](../CONSENT-REVOCATION.md)
- [Privacy and data deletion](../PRIVACY-AND-DATA-DELETION.md)
