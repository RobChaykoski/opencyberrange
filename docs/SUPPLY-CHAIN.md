# Supply-chain verification

The repository ships a committed SHA-256 lock for the platform build inputs and
every lab. It detects drift between the reviewed release tree and the tree that
is about to be built, tested, or deployed.

## What is covered

`supply-chain.lock.json` records:

- dependency and version files (`requirements*.txt`, `package.json`,
  `package-lock.json`, `versions.yaml`);
- platform container and proxy inputs (Dockerfiles, Compose files, nginx
  configuration, entrypoint, SPA index);
- deployment and verification scripts;
- the licence inventory and pinned container images. Redis is pinned to 7.2
  because 7.4 and later are RSALv2/SSPLv1; see
  [`../THIRD_PARTY_NOTICES.md`](../THIRD_PARTY_NOTICES.md);
- GitHub Actions workflows that build, scan, or smoke-test the release;
- every lab directory, including `lab.yaml`, `README.md`, `quiz.yaml`, and build
  contexts.

Text line endings are normalised to LF before hashing, so a Windows checkout and
a Linux CI checkout of the same commit produce the same hash. Binary files are
hashed as-is.

## Commands

```bash
python scripts/supply_chain.py --check
python scripts/supply_chain.py --check --json
python scripts/supply_chain.py --check --labs-only
python scripts/supply_chain.py --check-pins
python scripts/supply_chain.py --update
```

`--check` fails on a changed file, a changed lab, a new lab that is not in the
lock, a removed lab, or a release-version mismatch. `--update` rewrites the lock
only when the change is intentional and reviewed.

`--check-pins` reports base images that do not use an `@sha256:` digest. It is a
warning by default; use `--strict-pins` to make it blocking.

## Trust model

The lock is part of the repository, so the trust anchor is the reviewed commit
or release tag. A hash lock detects accidental or malicious drift; it does not
prove the repository, the build host, or the registry is trustworthy.

For a release, sign the lock and verify the signature:

```bash
gpg --detach-sign --armor supply-chain.lock.json
python scripts/supply_chain.py --check \
  --signature supply-chain.lock.json.asc
```

Release 2.5.3 is signed with:

- Key: `SWOCTS Cyber Range Release <release@swocts.com>`
- Fingerprint: `8636 08A2 EAD7 850D DD51 95A0 C788 625B AFA7 22CE`
- Public key: [`../supply-chain-release-key.asc`](../supply-chain-release-key.asc)
- Signature: `supply-chain.lock.json.asc`

Import the public key before verifying:

```bash
gpg --import supply-chain-release-key.asc
python scripts/supply_chain.py --check \
  --signature supply-chain.lock.json.asc
```

The private key stays with the release owner and is not committed. Rotate the
key and publish the new fingerprint if the release owner changes.

`minisign` is also supported with `--public-key`. If neither verifier is
installed, the signature check fails.

## Enforcement

- **CI:** the Quality workflow runs `--check` on every push and pull request.
- **Deploy/update:** `install-platform.sh` and `deploy-updates.sh` verify the
  lock before copying files or rebuilding. A mismatch stops the deployment.
- **Prebuild:** `prebuild-labs.sh` refuses to build lab sources that have
  drifted from the reviewed lock. Set `ALLOW_LAB_DRIFT=1` only for an
  intentional local working tree.
- **Verification:** `verify-lab-builds.sh` checks the lock alongside the lab
  compose files and images.

## What it does not replace

- `pip-audit` and `npm audit` for known vulnerabilities.
- CodeQL, Trivy, and the SBOM for code and image analysis.
- A signed release tag, a reviewed commit, and a trusted build host.

## Updating the lock

1. Make the dependency, build, workflow, or lab change.
2. Run the relevant tests and scans.
3. Run `python scripts/supply_chain.py --update`.
4. Review the lock diff. It should match the intended change and nothing else.
5. Commit the change and the lock together.

Do not update the lock to silence a mismatch you have not explained.
