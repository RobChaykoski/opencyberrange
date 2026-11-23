# Host-script security

The Docker and application layers are not the largest root surface. The host
scripts are: they run as root, they install packages, they write systemd units,
and one of them is the update mechanism. A bug here is root on every production
server.

## What runs as root

| Script or unit | Why root | Reviewed gate |
|---|---|---|
| `scripts/setup-range-server.sh` | Installs Docker, WireGuard, packages, and systemd units | `bash -n`, ShellCheck, explicit root check, no `eval` |
| `scripts/install-platform.sh` | Writes `/opt` or the user home, installs the Compose plugin, starts containers | Signed-tag checkout before running; supply-chain check |
| `scripts/deploy-updates.sh` | Pulls, verifies, backs up, rebuilds, restarts | **Signed tag verified before checkout**; supply-chain check before apply |
| `scripts/harden-lab-egress.sh` | Writes host firewall rules | Reviewed separately; run only on the range host |
| `scripts/fix-wireguard-client-route.sh` | Writes a host route for the WireGuard client pool | Reviewed separately; idempotent |
| `deploy/systemd/ocr-db-integrity.*` | Runs the read-only integrity check | Root for the container exec; evidence outside the database |

## The update trust path

`deploy-updates.sh` used to `git pull` first and verify the supply-chain lock
afterwards. That is not a trust boundary: the verifier, the public key, and the
lock all came from the tree being verified. The current order is:

```text
fetch tags
  -> prove the release public key matches the pinned fingerprint
  -> verify the signed tag
  -> check out the verified tag
  -> run supply_chain.py --check on the verified tree
  -> back up, apply, rebuild, restart
```

The pinned fingerprint is
`68A817762C831475F00DB54E775050A4C4921814`. The key is imported into a temporary
GnuPG home, so a compromised tree cannot replace the verifier or the key and
still pass. A ZIP update is refused unless `ALLOW_UNSIGNED_ZIP=1` is set
explicitly; that mode is for a controlled offline update, not production.

`SUPPLY_CHAIN_STRICT=1` is the default. A missing lock is a failure, not a
warning.

### Overrides

| Variable | Default | Meaning |
|---|---|---|
| `DEPLOY_TAG` | latest `v*` tag | Tag to verify and check out |
| `RELEASE_GPG_FINGERPRINT` | pinned release key | Trust anchor |
| `ALLOW_UNSIGNED_MAIN` | `0` | Permit an unsigned `main` update for development |
| `ALLOW_UNSIGNED_ZIP` | `0` | Permit a ZIP update without a signed tag |
| `SUPPLY_CHAIN_STRICT` | `1` | Fail when the supply-chain lock is missing |

Do not set an override in production without a dated exception and an owner.

## Install path

The documented path is a clone followed by `sudo bash
scripts/setup-range-server.sh --install`. It is **not** a curl-pipe-to-shell
install. The clone must be a signed tag:

```bash
git clone https://github.com/RobChaykoski/opencyberrange.git
cd opencyberrange
git fetch --tags
git verify-tag <release-tag>
git checkout --detach <release-tag>
```

Replace `<release-tag>` with the current signed release tag, for example
`v5.36.0` after it is cut.

If a future page adds a download-and-run snippet, it must download a versioned
artifact, verify a published SHA-256 or signature, and then execute the local
file. Never pipe an unverified response into `bash` or `sh`.

## Downloads inside the scripts

The last-resort Docker Compose install downloads the binary from GitHub. The
script now fetches the matching `.sha256` file and verifies it before installing
the binary. It is still a `latest` fallback; prefer the distribution package
(`docker-compose-v2` or `docker-compose-plugin`). Pin a version if the host
cannot use the package.

## Systemd units

- The integrity unit runs as root because it executes a read-only container
  check and writes evidence outside the database. It does not expose a network
  listener.
- `OnFailure=` is wired to an alert unit, but the shipped alert only writes to
  syslog. Point it at the external watchdog or your alerting webhook before
  relying on it.
- Unit files use absolute paths. Change the checkout path during install, and
  keep the unit file root-owned and not group-writable.

## Review checklist for a host-script change

- [ ] `set -Eeuo pipefail` at the top.
- [ ] Explicit root check where root is required; no silent privilege
      escalation.
- [ ] No `eval`, no unquoted variable expansion, no `curl | bash`.
- [ ] Every download is versioned and verified by SHA-256 or a signature.
- [ ] `git` runs as the repository owner, not root, or ownership is restored.
- [ ] Backups are taken before a destructive step.
- [ ] The script is idempotent on a second run.
- [ ] `bash -n` passes, and ShellCheck has no error-level finding.
- [ ] The systemd unit is root-owned and has no writable group/world bits.
- [ ] The change is exercised on a disposable host before production.

## Residual risks

- A compromised release signing key defeats the tag gate. Keep the key offline,
  rotate it with a signed announcement, and treat any use as an incident.
- The host OS package repository and the Docker apt key remain part of the
  supply chain. They are outside this repository and need their own review.
- Root-run scripts can still be wrong. The checklist reduces the chance; it
  does not prove correctness.

## If the remote or a host script is compromised

1. Stop the update path. Do not run `deploy-updates.sh` or `setup-range-server.sh`.
2. Reinstall from a known-good signed tag on a clean host.
3. Rotate the release key, the deploy keys, the platform secrets, and the
   database credentials.
4. Preserve `scripts/deploy.log`, `scripts/install.log`, shell history, and
   systemd journal for the incident review.
5. Re-run the supply-chain check and the lab isolation audit before restoring
   service.
