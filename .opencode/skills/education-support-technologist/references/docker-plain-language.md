# Docker and Compose in plain language

## The lunchbox analogy

- **Image** — the sealed recipe and ingredients. It does not change while it
  runs.
- **Container** — a lunchbox made from an image. It can start, stop, and be
  replaced.
- **Volume** — a labelled storage shelf that survives when the lunchbox is
  replaced. The database usually lives here.
- **Network** — the private corridor that lets containers talk to each other.
- **Compose** — the instructions for a whole lunch table: which containers,
  which volumes, which ports, and which settings.
- **Port** — the numbered door on the host that lets traffic reach a container.

## The commands you are most likely to need

```bash
docker compose ps                 # what is running and whether it is healthy
docker compose logs --tail=100    # recent logs
docker compose logs -f backend    # follow one service's logs
docker compose up -d              # start or recreate services in the background
docker compose restart backend    # restart one service
docker compose stop               # stop without deleting containers or volumes
docker compose down               # stop and remove containers and networks
```

## Red lines

- **`docker compose down -v` removes volumes.** That can remove your database.
  Do not run it unless a verified backup exists and the rollback plan says so.
- **Do not `docker cp` files into a container as a permanent fix.** Recreating
  the container loses the change. Edit the source and rebuild.
- **Do not edit files inside a running container.** Use the project files.
- **Do not expose the database or backend API to the internet.** Only the
  intended public ports belong in the firewall.
- **Do not paste container logs containing secrets or learner data.**

## Inspecting without changing anything

```bash
docker compose ps
docker compose config
docker inspect <container-name>
docker volume ls
docker network ls
docker stats --no-stream
```

`docker compose config` is useful because it shows the effective configuration
without starting anything. It may print secrets, so do not share the output.

## Updates

1. Read the release note.
2. Back up the database and volumes.
3. Pull the approved version.
4. Check for new environment variables in `.env.example`.
5. Rebuild changed images: `docker compose build`.
6. Start: `docker compose up -d`.
7. Confirm health and logs.
8. Test login, one course, one lab, and one report.

## Volumes and state

List volumes before deleting anything:

```bash
docker volume ls
```

If a volume name looks like `*_db_data`, `*_uploads`, or `*_wiki_data`, treat it
as state. It may contain data that cannot be regenerated from code.

## When a container keeps restarting

Read the logs first:

```bash
docker compose ps
docker compose logs --tail=200 <service>
```

Check configuration, missing environment variables, port conflicts, and disk
space. Do not repeatedly restart without reading the error.
