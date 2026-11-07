---
name: Education Support Technologist
description: Use when an education support technologist, lab coordinator, instructor, or non-specialist administrator must deploy, update, back up, troubleshoot, or hand over a teaching platform. Explains file and folder structure, Git, Docker, environment files, volumes, logs, safe rollback, and classroom change management in plain language, with checklists and escalation rules.
---

# Education Support Technologist

This skill is for the person who keeps a teaching platform running without being
a full-time systems administrator. The goal is successful, reversible
deployments that protect learners, instructors, and their data. Technical
accuracy matters, but clarity and safety matter more.

## The core stance

1. **You are managing change, not proving technical skill.** A boring deployment
   that is documented and reversible is better than a clever one nobody can
   explain.
2. **Back up before you change anything.** A backup you have not restored at
   least once is only a hope.
3. **One change at a time.** If two things change, you cannot tell which one
   caused the result.
4. **Read a command before you run it.** If you cannot explain what it deletes,
   stops, or overwrites, stop and ask.
5. **Protect learner data first.** Names, emails, passwords, VPN keys, and lab
   activity are sensitive. Do not paste them into tickets, screenshots, chat, or
   AI tools.
6. **Write down what you did.** The next person may be you, six months later, at
   8 a.m. before a class.

## Start with these references

- `references/files-and-folders.md` — paths, config, data, permissions, and
  backups in plain language.
- `references/git-plain-language.md` — repositories, commits, branches, pull,
  push, conflicts, tags, and rollback.
- `references/docker-plain-language.md` — images, containers, Compose, volumes,
  networks, ports, logs, and safe restart/stop.
- `references/deployment-runbook.md` — the repeatable deployment, update, verify,
  and rollback sequence.
- `references/troubleshooting-and-escalation.md` — what to check, what to capture,
  when to stop, and how to ask for help.
- `templates/deployment-checklist.md` — a copyable checklist for a change window.

## The five-part mental model

Use this model for every platform, not just Docker or Git.

| Part | Plain-language question | Example |
|---|---|---|
| **Code** | What files make the application work? | A project folder with a frontend, backend, and Compose file |
| **Configuration** | What values make this installation different? | `.env`, ports, domain name, email settings, secrets |
| **State** | What must survive a restart? | Database, uploaded files, backups, certificate files |
| **Runtime** | What is running right now? | Containers, services, processes, health checks |
| **Evidence** | How do I know it worked? | Logs, health endpoint, a test login, a learner smoke test |

If a proposed change does not say which part it touches, it is not ready.

## Non-negotiable safety rules

- **Never run `docker compose down -v`** unless you have a verified backup and a
  written reason. The `-v` removes named volumes, which may contain the database.
- **Never delete `.git`.** It is the project's history. Deleting it removes your
  rollback path.
- **Never commit `.env`, passwords, keys, database dumps, or learner exports.**
  Use `.env.example` for documentation.
- **Never edit files inside a running container** as a deployment method. The
  change is lost when the container is recreated. Edit the source, then rebuild.
- **Never restore a backup over production without checking the version.** A
  newer schema restored into an older platform can fail or corrupt data.
- **Never test with real learner data** when a demo account will do.
- **Never guess at a destructive command.** Stop and escalate.

## Deployment workflow at a glance

1. **Confirm the change window.** Who is affected? When is the class? Is there a
   rollback window?
2. **Capture the current state.** Version, health, running containers, and a
   screenshot of a working login.
3. **Back up.** Database, configuration, uploads, and any platform-specific
   volume. Verify the backup path and size.
4. **Read the release note.** Identify database migrations, new environment
   variables, port changes, and manual steps.
5. **Apply one change.** Pull the approved version, update configuration, rebuild
   or restart only what is needed.
6. **Verify from the outside in.** Health endpoint, login, course page, one lab
   launch, one report or export, and an administrator page.
7. **Record the outcome.** Version, time, operator, commands, checks, and any
   follow-up.
8. **Roll back if a critical check fails.** Do not keep debugging a broken
   production system during a class.

## Explaining technology to non-specialists

- Start with the **learner outcome**, then the technical step: "Students can log
  in again" before "the frontend container restarted".
- Use one analogy, then the real term: "A container is a sealed lunchbox; the
  image is the recipe used to pack it."
- Say **what will change**, **what will not change**, and **how we will know**.
- Avoid "just", "simply", "obviously", and "everyone knows".
- Give one command at a time, with the expected result.
- If a step can destroy data, say so before the command, not after.

## FastAPI in one page

This platform's API is a **FastAPI** application. You do not need to be a Python
developer to deploy it safely, but you should recognise the parts:

| Part | What it means for you |
|---|---|
| `platform/backend/app/main.py` | The application entry point. |
| `platform/backend/app/routers/` | Feature endpoints such as profile, reports, and admin. |
| `platform/backend/app/services/` | Shared business logic and report generation. |
| `.env` / environment variables | Database URL, JWT secret, encryption key, mail, and feature settings. |
| `/api/health` | The first check when the site is unavailable. |
| `/docs` | FastAPI's generated API documentation. Keep it internal; do not expose it publicly by default. |
| Alembic | Database migration tool. Run only documented migrations, and back up first. |

FastAPI safety rules:

- **Do not edit Python files inside a running container.** Edit the source,
  rebuild, and restart.
- **Do not change the database by hand** to work around an API error. Capture the
  error and use the documented migration or restore path.
- **Do not paste a traceback** until you remove connection strings, secrets, and
  learner data.
- **Check imports before blaming the database.** After a code update, an import
  error can look like a database outage.
- **Run one worker change at a time.** The platform uses a scheduler leader lock;
  changing worker counts can affect background jobs.
- **Verify with an API response, not only a running container.** A container can
  be "up" while the API returns errors.

Useful read-only checks:

```bash
docker compose ps
docker compose logs --tail=200 backend
docker compose exec backend python -c "import app.main; print('import ok')"
curl -fsS http://127.0.0.1:8000/api/health
```

## Education-specific rules

- Respect the academic calendar. Avoid changes during class, assessment, or
  registration peaks unless the change fixes an active outage.
- Keep a **demo or staging** copy for showing new features. Do not use the live
  teaching instance as a demonstration playground.
- Treat learner records as protected. Export only what is needed, keep the reason,
  and delete the export when the task is done.
- Check accessibility after changes: keyboard navigation, readable contrast,
  screen-reader labels, and no new horizontal scrolling.
- Tell instructors what changed in plain language, including any action they must
  take.
- Check the backup restore path before the term starts, not during an incident.

## What to capture when something breaks

Collect only non-sensitive evidence:

- the time and timezone;
- the page or action that failed;
- the exact error text, with names/emails removed;
- the platform version;
- `docker compose ps` output;
- the last 50–100 relevant log lines with secrets removed;
- what changed immediately before the failure;
- whether a rollback is available.

Do not send passwords, VPN private keys, full `.env` files, database dumps, or
complete learner records.

## Definition of done

A deployment is done when:

- the intended version is running and reported by the platform;
- the health check passes;
- a real user path works (login, course, lab, report);
- configuration and secrets are present without being exposed;
- a backup exists and the restore path is known;
- the change is recorded;
- the rollback path is written down;
- the instructor or operator knows what changed.
