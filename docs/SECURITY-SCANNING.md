# Security scanning: Syft, Grype, and Lynis

Status: **manual scans completed on development and production, 15 November
2026.** Image hardening from this round is in the current `Unreleased`
changelog; the host-hardening suggestions in this note are tracked, not all
applied.

Three scanners cover different questions:

- **Syft** inventories what is inside an image or directory (SBOM).
- **Grype** matches that inventory against vulnerability data.
- **Lynis** audits the host configuration rather than container contents.

Trivy (filesystem, secret, and misconfiguration scan) and the dependency-audit
workflow already run in CI. This note covers the scans that need a built image
or a real host and therefore stay manual.

## What already runs automatically

| Control | Where | Blocking |
| --- | --- | --- |
| Trivy filesystem scan (`vuln,secret,misconfig`, CRITICAL/HIGH, unfixed ignored) | `.github/workflows/trivy.yml` | Yes |
| `pip-audit` and `npm audit --omit=dev` | `.github/workflows/dependency-audit.yml` | No (baseline, PR and weekly) |
| CodeQL, OpenSSF Scorecard, security delta review | `.github/workflows/` | Yes |
| Container digest updates | `renovate.json` (`pinDigests`) | PR |

At the time of these scans both dependency audits were clean: `npm audit`
reported 0 vulnerabilities (222 packages, including dev) and `pip-audit`
reported "No known vulnerabilities found" for `platform/backend/requirements.txt`.

## Reproducing the scans

Syft and Grype run as containers, so no host install is needed:

```bash
docker run --rm -v /var/run/docker.sock:/var/run/docker.sock \
  anchore/syft:latest "docker:opencyberrange-backend:latest" -o cyclonedx-json \
  > sbom-backend.json

docker run --rm -v /var/run/docker.sock:/var/run/docker.sock \
  -v ocr-grype-cache:/root/.cache/grype \
  anchore/grype:latest "docker:opencyberrange-backend:latest" -o json \
  > grype-backend.json
```

Use the container ID (`docker inspect -f '{{.Image}}' ocr-frontend`) when an
image has no repository tag; Grype resolves `docker:<id>` but Syft needs
`docker:<name:tag>`.

Lynis is installed per user so it does not need root or a package manager:

```bash
mkdir -p ~/.local/lynis ~/.local/bin
curl -sSfL https://github.com/CISOfy/lynis/archive/refs/tags/3.1.7.tar.gz \
  | tar -xz -C ~/.local --strip-components=1 --one-top-level=lynis
~/.local/lynis/lynis audit system --quick --no-colors > /tmp/lynis-report.txt
```

Lynis must run from its own directory, so keep a small wrapper on `PATH`:

```sh
#!/bin/sh
cd "$HOME/.local/lynis" || exit 1
exec ./lynis "$@"
```

Installed this way: Syft/Grype `v1.57.1`, Lynis `3.1.7` on development
(`172.16.16.44`) and production (`172.16.16.41`).

## Image findings

Backend (`opencyberrange-backend`), frontend (`ocr-frontend`), and the two lab
targets were scanned at revision `e1ebe575`. The backend and frontend were then
rebuilt with pinned base digests, `apt-get upgrade` / `apk upgrade`, and a
reduced runtime package set; the numbers below are before and after that
rebuild.

| Image | Before (crit/high/medium/low/neg/unknown) | After (crit/high/medium/low/neg/unknown) |
| --- | --- | --- |
| backend | 574 (17/230/142/39/105/41) | 345 (1/105/101/19/78/41) |
| frontend | 8 (1/3/4/0/0/0) | 3 (0/0/3/0/0/0) |

The remaining backend critical is a Debian `wont-fix` entry (see triage below),
not a missed upgrade.

### What changed in the images

- Backend and frontend base images are pinned by multi-arch index digest, so a
  rebuild cannot silently change the base. Renovate updates the digests.
- Backend runtime runs `apt-get upgrade` before installing its packages, so
  Debian point-release fixes that landed after the pinned digest are applied.
- Frontend runtime runs `apk upgrade` before adding `curl`, so Alpine security
  fixes for musl, zlib, and libxml2/libxslt are applied.
- The backend runtime no longer installs `curl` or `gnupg`: the Docker apt key
  is downloaded in the build stage and copied in. Application code uses the
  Python `requests` client, and the healthcheck uses the image's Python.
- The backend runtime removes `pip`, `setuptools`, and `wheel` after copying
  the pre-built wheels. Nothing in the application installs packages at
  runtime, so these were only vulnerability surface.
- Frontend base moved to the current `nginx:alpine` digest, which resolves the
  libxslt and zlib findings (1 critical, 3 high) that the previous digest
  carried.

### Remaining backend findings and their triage

One critical match remains: `CVE-2026-6653` in `libxml2`
(`2.12.7+dfsg+really2.9.14-2.1+deb13u3`). Debian marks it `wont-fix` for
trixie. The high-severity `libkrb5*` entries are in the same position: Debian
has no fixed version, and the image already carries the newest trixie package
set. These are vendor assessments, not missed upgrades.

The 14 findings that do show a fixed version split into two groups:

- Python interpreter CVEs fixed only on the 3.12/3.13/3.14 branches (for
  example CVE-2025-12781, CVE-2026-12345). The fix is a minor-version migration,
  not a rebuild.
- Go library CVEs inside the Docker Inc. `docker-ce-cli` binary
  (`GO-2026-4887`, `github.com/moby/go-archive`, `klauspost/compress`,
  `go.opentelemetry.io/otel`). They move when Docker publishes a new package.

Compensating controls for the remaining library findings:

- The backend is not internet-facing. Only nginx on the private bridge reaches
  port 8000, and the backend itself has no direct ingress.
- Lab and platform egress is default-deny; the backend talks to PostgreSQL,
  Valkey, and the Docker socket proxy on internal networks.
- The backend runs as UID 10001 with no host socket, and the socket proxy only
  exposes the container endpoints the launcher needs.
- The affected libraries are used for backup tooling and XML parsing, not for
  parsing untrusted input from the public internet.

The frontend's remaining three matches are one `busybox` CVE
(`CVE-2025-60876`) reported against `busybox`, `busybox-binsh`, and
`ssl_client`. Alpine has not published a fixed package; the frontend serves
static files, and busybox applets are not exposed to requests.

Two follow-ups remain open:

1. **Python 3.11 branch.** Several interpreter CVEs are fixed only on newer
   minor branches. Python 3.11 is in security-only maintenance until October
   2027. Plan a migration to the current stable minor release rather than
   backporting.
2. **Docker CLI Go findings** move when Docker Inc. publishes a new trixie
   package. Renovate tracks the base image, and the weekly Trivy scan surfaces
   changes.

### Lab target images

`ocr-ubuntu-memory` (692 matches, 6 critical) and `ocr-metasploitable2` (834
matches, 6 critical) are intentionally vulnerable teaching targets. Patching
them would remove the exercise. They are accepted as-is with these constraints:

- They run only on per-session lab networks with default-deny egress.
- They are never published or committed; images are built locally from pinned
  sources documented in `docs/METASPLOIT-TRACK.md` and
  `docs/LIVE-MEMORY-FORENSICS.md`.
- Students reach them through the lab proxy, not from the internet, and each
  session is destroyed after use.

Do not copy these images into a general-purpose deployment, and do not add them
to the same network as the platform services.

## Host hardening (Lynis)

Lynis was run as a non-privileged user, so it skips root-only tests. Treat the
index as a baseline, not an audit certificate.

| Host | Hardening index | Warnings | Suggestions | Tests |
| --- | --- | --- | --- | --- |
| development | 62 | 1 | 33 | 261 |
| production | 63 | 0 | 34 | 260 |

The single development warning is `KRNL-5830`, "reboot most likely needed"
after kernel and library updates. Production had no warnings.

Suggestions that matter for this deployment, and their status:

| Suggestion | Status |
| --- | --- |
| `BOOT-5122` GRUB password | Deferred: physical/console access is controlled; GRUB passwords complicate unattended recovery. Revisit for on-premise installs. |
| `AUTH-9230` password hashing rounds in `/etc/login.defs` | Deferred: authentication is application-level (argon2/bcrypt), not system accounts. |
| `AUTH-9262` PAM password-quality module | Deferred: no interactive system logins; the platform enforces password policy in the app. |
| `AUTH-9328` umask `027` | Candidate: low risk, no known breakage. |
| `KRNL-5820` disable core dumps | Candidate: limits crash data that can contain secrets. |
| `FILE-6310` separate `/tmp`, `/var`, `/home` partitions | Accepted: LVM has a single root logical volume; splitting now requires downtime and a reinstall path. Documented in the production readiness record. |
| `USB-1000` disable USB storage | Deferred: host is in a datacentre; physical access is the boundary. |

No Lynis finding was treated as a release blocker. The two "candidate" rows are
cheap wins for the next maintenance window.

## Re-running after a change

1. Rebuild the image.
2. Re-run Syft and Grype and diff the counts. A new critical with a `fixed`
   state means an upgrade is available; a new `wont-fix` needs a triage note
   here.
3. Re-run `npm audit` and `pip-audit` when dependencies change.
4. Re-run Lynis after kernel, OpenSSH, or PAM changes, and after a reboot to
   clear `KRNL-5830`.
