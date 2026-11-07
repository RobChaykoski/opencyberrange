# Files and folders in plain language

## The four kinds of files

| Kind | Examples | Safe to edit? | Safe to delete? |
|---|---|---|---|
| **Code** | `platform/backend/`, `platform/frontend/`, scripts | Only with a change plan and a backup | No |
| **Configuration** | `.env`, Compose files, nginx config, TLS paths | Yes, with a backup; never commit secrets | No, unless you have a copy |
| **State** | Database, Docker volumes, uploaded files, backups, erasure ledger | No direct editing | Never without a verified backup |
| **Evidence** | Logs, exports, screenshots, audit records | Read-only | Only after the retention period |

If you are unsure which kind a file is, treat it as **code or state** and stop.

## Paths

- **Absolute path**: starts at the root, for example `/opt/opencyberrange/.env`.
  It means the same place from anywhere.
- **Relative path**: starts from where you are, for example `../.env` or
  `./scripts/deploy-updates.sh`. It changes meaning if you change directory.
- **Home directory**: usually `/home/yourname`; `~` means this folder.
- **Current directory**: `.` means "here"; `..` means "one level up".

Before a command that changes files, run `pwd` (print working directory) and
check that you are where you think you are.

## The project folder

Keep one approved project folder, for example:

```text
/opt/opencyberrange/
  .env                  # local configuration and secrets, never committed
  .env.example          # documented variable names, no real secrets
  docker-compose.yml    # how the platform containers run
  platform/
    backend/            # API code
    frontend/           # web application
  scripts/              # install, upgrade, backup, and validation scripts
  data/                 # local state or generated data, depending on setup
```

Do not copy the project into a second folder and edit both. Two copies become
two different platforms. Use Git or a documented staging copy.

## What belongs in Git and what does not

Commit:

- source code;
- configuration templates such as `.env.example`;
- documentation;
- scripts;
- tests.

Do not commit:

- `.env` with real values;
- database dumps or learner exports;
- VPN private keys, TLS private keys, API tokens;
- large generated files or logs;
- `node_modules/`, build output, or caches.

If a secret was committed, stop. Rotating the secret is safer than deleting the
commit, because the value may already be in history or in someone's clone.

## Permissions

- If a service cannot read its config, check ownership and permissions before
  changing the whole folder.
- Prefer the narrowest permission that works.
- Do not run every command as `root` just to avoid a permission error.
- Do not make `.env` world-readable.

## Backups

A backup is only useful if you know:

1. **what** it contains (database, config, uploads, volumes);
2. **where** it is stored;
3. **when** it was taken;
4. **how** to restore it;
5. **what version** it came from.

Keep the backup outside the folder you are about to change. A backup on the same
broken disk is not a backup.
