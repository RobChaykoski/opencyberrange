# Deployment and update runbook

Use this sequence for a planned platform change. Stop at any failed critical
check; do not improvise a second change to fix the first one.

## 0. Before the window

- Confirm the class, assessment, and registration calendar.
- Announce the change and the expected downtime.
- Confirm who can approve a rollback.
- Download or locate the release notes and the target version.
- Confirm disk space and memory.
- Confirm the backup destination is separate from the server.

## 1. Record the current state

```bash
git rev-parse HEAD
docker compose ps
docker compose logs --tail=50 backend
curl -fsS http://127.0.0.1:8000/api/health
```

Record the version, commit, time, and operator.

## 2. Back up

- Database dump.
- `.env` and Compose configuration.
- Uploaded files, workbook/wiki volume, and erasure ledger.
- TLS certificates and WireGuard configuration if they are not in the backup
  scope.
- Verify the files exist and are non-zero. Copy them off the host.

## 3. Read the release note

Look for:

- database migrations;
- new or changed environment variables;
- changed ports or URLs;
- new volumes or storage requirements;
- manual steps;
- known issues;
- the supported rollback path.

## 4. Apply the change

```bash
git pull
# review the diff and the release note
docker compose build
docker compose up -d
```

If the release note says to run a migration or seed command, run only the
documented command.

## 5. Verify from the outside in

1. Health endpoint returns success.
2. Login works for a test student and a test instructor.
3. The dashboard and course list load.
4. One lab launches and can be stopped.
5. One report page loads and one export works.
6. An administrator page loads.
7. Logs show no repeated errors.
8. The page footer shows the expected version.

## 6. Record and hand over

Write down:

- target version and commit;
- start and end time;
- commands run;
- checks passed or failed;
- backup location;
- rollback decision;
- follow-up items;
- who was told.

## 7. Rollback

If a critical check fails:

1. Stop applying new changes.
2. Capture logs and the exact error.
3. Return to the recorded commit or release tag.
4. Restore the matching backup if the schema changed.
5. Bring the platform up.
6. Repeat the verification checks.
7. Record the rollback and notify the teaching team.

Do not restore a newer database into older code without checking compatibility.
