# Security tests (Karate)

`security-tests/karate/` is a blackbox API suite for authentication, access
control, input safety, uploads, and privacy. It runs against a Docker deployment
over an SSH tunnel and creates disposable identities for the run.

## What it covers

| Feature | Checks |
|---|---|
| `01-auth-owasp` | valid login, generic errors, SQLi/XSS/null/oversize input, JSON login rejection, malformed/absent bearer, tampered JWT, `alg=none` |
| `02-access-control` | learner/instructor to admin denial, unauthenticated admin, IDOR on admin user, self-delete denial, mass assignment, cross-user session revocation |
| `03-input-validation` | JSON type confusion, injection strings, control chars, privacy acknowledgment, under-13, oversized email, malformed JSON, path traversal |
| `04-upload-security` | anonymous/student upload denial, non-ZIP rejection, no-Markdown rejection, traversal `chapter_dir` rejection |
| `05-privacy` | account export scoping, profile summary scoping, denied admin response, public 404, DNA consent gate, public events feed |

## Prerequisites

- Java 17 (Karate 1.5.1). Karate 2.x requires Java 21 and is not used here.
- SSH access to the Docker host; set `OCR_TEST_SSH_HOST` or pass `-SshHost`.
- The backend container name (`ocr-backend`).
- PowerShell 5.1+ for the runner script.
- Network access to download the Karate jar once.

The jar is downloaded to `security-tests/karate/.tools/` and verified by SHA-256.

## Run

```powershell
$env:OCR_TEST_SSH_HOST = "<your docker host>"
cd security-tests/karate
.\run-security-tests.ps1 -Tags '@security'
```

The runner:

1. Creates three disposable identities in the backend container
   (`student_a`, `student_b`, `instructor`).
2. Writes `target/security-fixture.json` — the runtime fixture file.
3. Opens `127.0.0.1:18000` to the backend over SSH.
4. Runs Karate and writes `target/reports/karate-reports/karate-summary.html`.
5. Deletes the identities, removes the fixture, and closes the tunnel.

If cleanup cannot prove `remaining=0`, the fixture is kept for manual recovery.

## Why it is deterministic

- Each run creates fresh usernames with a unique run id.
- Tokens are created once per role with `karate.callSingle` and reused.
- Negative login attempts use distinct `X-Forwarded-For` values, so per-IP
  limits and per-username backoff do not couple scenarios.
- The backend trusts `X-Forwarded-For` only from loopback/Compose, which is why
  the runner uses an SSH tunnel to `127.0.0.1:8000`.
- Assertions target stable contracts, not timestamps or generated values.
- The suite has been run repeatedly with the same result: 44 scenarios passed,
  cleanup `remaining=0`.

## Safety

- Run against development only. Do not run it against production: it creates
  accounts and exercises login failures.
- It does not delete real users; cleanup targets only the fixture ids.
- It does not modify learner data, consent, or catalogue content.
- The upload tests reject before writing; no chapter is created.
- The report may contain fixture usernames and JWTs. Treat it as test evidence
  and do not publish it.

## Files

```text
security-tests/karate/
├── karate-config.js
├── features/
│   ├── 01-auth-owasp.feature
│   ├── 02-access-control.feature
│   ├── 03-input-validation.feature
│   ├── 04-upload-security.feature
│   ├── 05-privacy.feature
│   ├── common/
│   └── fixtures/
├── tools/
│   ├── provision_fixture.py
│   ├── cleanup_fixture.py
│   └── create_upload_fixtures.py
├── fixtures/            upload ZIP fixtures
├── run-security-tests.ps1
└── README.md
```

## Extending

- Add a feature under `features/`.
- Reuse `common/session-*.feature` for a role.
- Use a unique `X-Forwarded-For` for a new negative login or rate-limit case.
- Add cleanup if you create any other row.
- Run the suite twice and confirm the same result.
- Do not add a test that mutates a real learner or production data.

## Related

- [Testing and quality gates](../testing-and-quality-gates.md)
- [Backend login](../backend/features/login/README.md)
- [Backend roles and admin](../backend/features/roles-and-admin/README.md)
- [Backend uploads](../backend/features/uploads-and-workbook/README.md)
