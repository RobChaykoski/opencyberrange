# Git in plain language

Git is the project's **save history**. It records what changed, who changed it,
and lets you return to a known version.

## The words you need

| Word | Plain meaning |
|---|---|
| **Repository (repo)** | The project folder plus its history. |
| **Commit** | A labelled save point. |
| **Branch** | A parallel line of work. |
| **Remote** | A copy of the repository on a server, such as GitHub. |
| **Pull** | Bring remote changes into your local copy. |
| **Push** | Send your committed changes to the remote. |
| **Merge** | Combine two lines of work. |
| **Conflict** | Git cannot choose between two changes and needs a person. |
| **Tag** | A permanent label for a release, such as `v2.5.0`. |
| **Clone** | Make a new local copy of a remote repository. |

## The safe daily sequence

```bash
git status
git pull
# make or review changes
git status
git diff
git add <specific files>
git commit -m "Describe the change and why"
git push
```

Never use `git add -A` or `git add .` on a server until you have checked
`git status` and confirmed that no secret, dump, or learner export is included.

## Rules for non-specialists

- **Do not delete `.git`.** It contains the history and your rollback path.
- **Do not force-push** (`git push --force`) to a shared branch. It can erase
  other people's work.
- **Do not rewrite history** to hide a mistake. Record the fix.
- **Pull before you edit** so you are not working on an old copy.
- **Commit one logical change.** "Fix report export reason" is useful; "updates"
  is not.
- **Read a conflict.** If you do not understand both sides, stop and ask.

## Undo without panic

| Situation | Safe action |
|---|---|
| You changed a file and want it back | `git diff` to see it, then `git restore <file>` if you are sure |
| You staged a file by mistake | `git restore --staged <file>` |
| You committed but did not push | Make a new corrective commit; do not rewrite unless you understand the risk |
| You need a known released version | Check out the release tag in a separate folder, do not overwrite production |
| A pull created a conflict | Stop, read the conflict markers, and ask for review |

## Releases and rollback

- A release should have a **tag** or a recorded commit hash.
- Before an update, record `git rev-parse HEAD`.
- Rollback means returning to the recorded commit and restoring the matching
  backup. Code and database must match.

Do not assume that checking out older code is enough. Database migrations may
need a restore.
