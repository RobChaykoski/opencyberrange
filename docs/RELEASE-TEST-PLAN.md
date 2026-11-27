# Release test plan

This is the pre-release gate for the platform. It covers the 20 tests that
matter most for a teaching deployment: onboarding, labs, authorization,
privacy, deletion, restore, accessibility, mobile, and the complete learner
journey.

The executable matrix lives in
[`platform/tester/release-tests.yaml`](../platform/tester/release-tests.yaml).
Run it with:

```bash
python scripts/release_tests.py --list
python scripts/release_tests.py --automated-only
python scripts/release_tests.py --automated-only --json release-tests.json
python scripts/release_tests.py --live --test lab-launch --test docker-isolation
```

Manual tests are never marked passed by the runner. They need a completed
evidence page and a named reviewer. A skipped automated test is a gap, not a
pass; use `--strict` in a release gate.

## 1. The 20 tests

| # | Test | Type | Pass criteria | Evidence |
|---:|---|---|---|---|
| 1 | First-time student onboarding | Manual | Median under 15:00 for every persona; >=80% under 15:00 with L0/L1 help | [First-time user test](research/FIRST-TIME-USER-TEST.md) |
| 2 | VPN setup | Manual | Fresh user installs, imports, connects, reaches only the assigned `/24` | [VPN separation](#vpn-separation) |
| 3 | Lab launch | Live | Build, start, health, ports, isolation, flag, repeat, resources, teardown | `lab_harness.py` JSON |
| 4 | Flag submission | Automated | Wrong denied, correct accepted, hint-only not counted | pytest |
| 5 | Course enrollment | Automated | Join, roster, order, scoped progress | pytest |
| 6 | Instructor course creation | Automated | Owner can create; another instructor cannot read | pytest |
| 7 | Achievement unlocking | Automated | Idempotent award; owner-only visibility | pytest |
| 8 | Certificate generation | Automated | PDF, hash/manifest, verification | pytest + PDF |
| 9 | Transcript generation | Automated | Completions and labels; no other learner rows | pytest |
| 10 | Data export | Automated | Required sections present; secrets and other learners absent | pytest + Karate |
| 11 | Account deletion | Automated + drill | Rows/files/peers gone; API revoked; suppression proof retained | pytest + [deletion drill](#deletion-and-suppression) |
| 12 | Backup restore | Manual | Restore drill passes; deleted account does not reappear | [Backup and restore](BACKUP-RESTORE-TEST.md) |
| 13 | Docker isolation | Live | No host network, published ports, control-plane, other-lab network, or host mount | `lab_harness.py` + drill |
| 14 | RBAC verification | Automated | Role matrix matches reviewed grants | pytest + [matrix](#rbac-matrix) |
| 15 | API authorization | Automated | Every protected route has a dependency; BOLA/IDOR denied | pytest + Karate |
| 16 | Concurrent lab launches | Automated | Quota and capacity hold under concurrent spawns | pytest |
| 17 | Workbook accuracy | Automated | Links/images/commands/IPs/flags/tool versions/path plans | `lab_qa.py --static` |
| 18 | Accessibility review | Manual | WCAG 2.2 AA review; keyboard-only lab; NVDA/JAWS/Narrator; charts | [Accessibility test](ACCESSIBILITY-TEST.md) |
| 19 | Mobile responsiveness | Automated + manual | 390x844 shell, lab, flag form, navigation; no overflow | `ui-smoke.mjs` |
| 20 | Complete learner journey | Manual | Register to delete, with evidence at each stage | [Journey](#complete-learner-journey) |

## 2. Release gate

A release is blocked when:

- any automated test fails;
- any manual test has no evidence page and named reviewer;
- a live lab can reach the host, the control plane, another learner, or a
  database service;
- a deleted account reappears after a restore;
- a learner can see another learner's container, data, or flags;
- a workbook exposes a flag that does not match the lab;
- a keyboard-only learner cannot complete the first lab;
- a screen reader cannot understand an achievement or a chart's summary.

A warning is not automatically a blocker, but the release notes must list it
with an owner and target date.

## 3. Isolation testing

### Container isolation

Run the live harness and keep the JSON evidence:

```bash
python scripts/lab_harness.py --lab <slug> --runs 1 --json lab-isolation.json
```

The harness proves:

- the lab starts from its compose file;
- no container uses `network_mode: host`;
- no container publishes a host port;
- every container is on the project network only;
- the solver can reach the declared ports;
- the flag is obtainable and repeatable;
- resources stay under the manifest ceiling;
- teardown removes the project.

The harness is necessary but not sufficient. Also inspect a running lab:

```bash
docker inspect <container> --format '{{json .HostConfig}}' | jq '{
  Privileged, NetworkMode, PidMode, IpcMode, CapAdd, CapDrop,
  ReadonlyRootfs, Binds, PortBindings
}'
```

Reject: `Privileged=true`, `NetworkMode=host`, `PidMode=host`, a bind of
`/var/run/docker.sock`, a host root/home mount, or a published `0.0.0.0` port.

### Network traversal

From inside the lab or the tester sidecar, attempt:

```bash
getent hosts ocr-db ocr-backend ocr-valkey docker-socket-proxy
nc -z -w 2 ocr-db 5432
nc -z -w 2 ocr-backend 8000
nc -z -w 2 docker-socket-proxy 2375
nc -z -w 2 169.254.169.254 80
nc -z -w 2 host.docker.internal 2375
```

All must fail or resolve to nothing from the lab network. A success is a
release blocker. The tester sidecar runs on the lab network, so it is a good
proxy for the learner's reachable network.

### VPN separation

Use two test learners, A and B, on two client machines or two WireGuard
interfaces:

1. Connect A and B.
2. Confirm A can reach A's lab `/24` and B can reach B's.
3. From A, try B's lab `/24`, the platform `10.100.0.0/16` outside A's `/24`,
   the management LAN, the database, and the host.
4. Repeat from B.
5. Confirm A's peer cannot route the whole `10.100/16` or `10.255/16`.

Pass: each peer reaches only its own lab `/24`; everything else is denied.
Record the peer addresses in the evidence, not in a public document.

### Storage isolation

- The lab has no bind mount to the host except its declared read-only lab source.
- The lab cannot read `workbook_data`, `backups_data`, `postgres_data`, or
  another learner's volume.
- Uploaded files are scoped to the uploader's tenant or course.
- A lab container has no Docker socket and no host path outside its project.

## 4. RBAC matrix

Test every role. `Course only` means the actor must own the course or be staff
on it.

| Feature | Anonymous | Student | Instructor | Admin |
|---|---|---|---|---|
| View users | No | No | Course only | Yes |
| Delete users | No | No | No | Yes |
| View plaintext lab flag | No | No | No | Yes (lab editor/export) |
| Create course | No | No | Yes | Yes |
| Launch lab | No | Assigned only | Preview/own course | Yes |
| View cohort analytics | No | Own progress | Own course | All |
| Export learner data | No | Own | Course reports | Aggregate/all |
| Change platform settings | No | No | No | Yes |
| Impersonate | No | No | No | Yes, audited |

Automated proof:

```bash
cd platform/backend
python -m pytest tests/test_access_matrix.py tests/test_authorization_matrix.py \
  tests/test_idor_matrix.py tests/test_route_authorization.py \
  tests/test_horizontal_privilege.py -q
```

Blackbox proof:

```bash
cd security-tests/karate
.\run-security-tests.ps1 -Tags '@security'
```

Add any new object route to the access matrix and the Karate suite. A UI guard
is not authorization.

## 5. API security

| Test | Method | Pass |
|---|---|---|
| BOLA | Student requests another learner's object id | 403/404, no data |
| JWT manipulation | Change `sub`, `role`, `sec`, or signature | 401 |
| `alg=none` | Unsigned token | 401 |
| IDOR | Session, snapshot, share, or evidence id from another user | 403/404 |
| Rate limit | Login, registration, flag, report | 429 with a bounded window |
| Session fixation | Inject a chosen session id or reuse a refresh token | rejected; rotation/reuse detection |
| Mass assignment | Send `role`, `is_admin`, `is_approved` in a profile update | ignored; no elevation |
| Path traversal | Upload `chapter_dir` and about-file paths | 400/404 |
| Upload | Anonymous/student, non-ZIP, no markdown, traversal | 401/403/400 |

Tools:

- **Burp Suite / ZAP**: manual request tampering, auth matrix, and replay.
- **Postman**: saved role-based collections for repeatable checks.
- **StackHawk**: CI API scan against a staging host with a test account.

Do not run an active scanner against production. Use staging and a disposable
account.

## 6. Data export

A learner requests "my data". The export must contain:

- account identity and profile (no password, MFA secret, recovery codes, or
  private key);
- courses and enrolments;
- lab sessions, completions, flag attempts, and quiz attempts;
- achievements and certificates;
- progress and transcript data;
- consent state and history.

It must not contain another learner, an instructor note about another learner,
a plaintext flag, or a secret. Verify with a two-learner test: A's export does
not contain B's username, email, completion, or evidence.

```bash
cd platform/backend
python -m pytest tests/test_privacy.py tests/test_export_labels.py -q
```

## 7. Deletion and suppression

### Deletion checklist

1. Create a disposable learner with a completion, an achievement, an avatar, a
   VPN peer, and a session.
2. Export the account and confirm the data is present.
3. Delete the account through the self-service path.
4. Confirm:
   - login fails and old tokens return 401;
   - the user row and cascaded learning rows are gone;
   - the avatar is gone;
   - the VPN peer is revoked;
   - the API rejects the old token and refresh token;
   - the consent suppression proof remains under a keyed subject hash.
5. Restore a pre-deletion database backup plus the `workbook_data`
   suppression ledger.
6. Run `enforce_suppressions`.
7. Confirm the deleted account does not reappear and cannot log in.

```bash
cd platform/backend
python -m pytest tests/test_erasure.py tests/test_purge_erased_accounts.py -q
```

A restore that resurrects the account is a release blocker.

## 8. Complete learner journey

Run once on staging with a new account and record each timestamp:

```text
register -> approve/login -> join course -> VPN -> launch lab -> read brief
-> submit flag -> achievement -> certificate -> transcript -> export -> delete
```

Pass: every stage works, the learner can explain what happened, and the deleted
account is gone after the restore drill.

The same path is exercised by `app/scripts/simulate_student.py` for synthetic
activity, but that script is not a substitute for a human journey.

## 9. Evidence bundle

Attach to the release record:

- `release-tests.json` from the runner;
- `lab-harness.json` from the live canary;
- the Karate report and cleanup result;
- the onboarding timing sheet and analysis;
- the accessibility report and issue log;
- the deletion/restore evidence page;
- the mobile screenshots;
- the workbook QA report;
- the signed tag and supply-chain lock hash.

## 10. Known gaps

- Full VPN separation is a host drill, not a CI job.
- Docker breakout testing is a controlled inspection and probe, not a
  penetration test of the host.
- Backup restore is a manual drill with a disposable host.
- Accessibility needs human testers with NVDA, JAWS, and Narrator.
- The 197 pending competency contracts are a content gate, not a test failure.

## Related

- [Security validation plan](security/SECURITY-VALIDATION-PLAN.md)
- [Accessibility test](ACCESSIBILITY-TEST.md)
- [First-time user test](research/FIRST-TIME-USER-TEST.md)
- [Lab QA pipeline](LAB-QA-PIPELINE.md)
- [Backup and restore](BACKUP-RESTORE-TEST.md)
