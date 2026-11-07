# Troubleshooting and escalation

## First five checks

1. **Is it one user or everyone?** Try a second account and a private browser
   window.
2. **Is it one page or the whole platform?** Check the health endpoint and login.
3. **Did something change?** Check the last deployment, configuration change, or
   certificate renewal.
4. **Is the host healthy?** Check disk, memory, CPU, and container status.
5. **Is it a known issue?** Search the release notes and issue tracker before
   changing anything.

## FastAPI-specific checks

The API is a FastAPI application. When it is unhealthy:

- read the backend container logs first;
- check that the database is reachable;
- check that required environment variables are present;
- check the health endpoint from the host and from the frontend network;
- check for an import error after a code update;
- check the OpenAPI docs only on a trusted internal address, not the public
  internet;
- never paste a full traceback that contains secrets, connection strings, or
  learner records.

Useful commands:

```bash
docker compose logs --tail=200 backend
docker compose exec backend python -c "import app.main; print('import ok')"
curl -fsS http://127.0.0.1:8000/api/health
```

If the API imports but requests fail, check the database and the reverse proxy
before changing application code.

## What to capture for a support request

- time and timezone;
- platform version and commit;
- affected URL or action;
- expected result and actual result;
- error text with secrets removed;
- `docker compose ps`;
- last 50–100 relevant log lines;
- whether the issue affects one account or all;
- what changed immediately before the issue;
- whether a backup and rollback are available.

## Stop and escalate immediately if

- data may have been deleted or overwritten;
- a database restore is being considered;
- secret keys or learner data may have been exposed;
- the same fix has already failed twice;
- a command would remove a volume, drop a table, or rewrite Git history;
- you cannot explain what the next command will delete or stop.

## Communication template

> **What is affected:** [login / course page / lab launch / reports]
> **Who is affected:** [one learner / one course / everyone]
> **Started:** [time and timezone]
> **Current state:** [working / degraded / stopped]
> **What changed:** [version, configuration, certificate, network]
> **What I checked:** [health, logs, disk, second account]
> **What I need:** [review, rollback approval, database help]
> **Data risk:** [none known / possible / confirmed]
