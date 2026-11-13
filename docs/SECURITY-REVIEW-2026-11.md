# Security review — November 2026

Status: **implemented fixes and recorded findings** (12 November 2026).

This pass covered the backend, frontend, RangeBox images, and installer
scripts. Production was not changed. The development deployment remains the
verification target.

## Secret scan

A history scan for high-confidence secret patterns (private keys, AWS keys,
GitHub/Slack/OpenAI tokens, JWT/encryption keys, database URLs) was run against:

- `opencyberrange-next` (current tree, all refs);
- `opencyberrange-backup` (353 commits, all refs).

Result: **no production credentials found.** The only high-confidence matches
are two synthetic SSH private-key blocks in
`platform/labs/Linux/linux-2-6-ssh-privilege-escalation/lab.yaml`. They are lab
content, not deployment keys. Recommendation: replace them with keys generated at
lab-build time, or keep them with a clear synthetic-only comment.

The scan script is intentionally local and does not print values. It is not
committed as a CI gate because it needs full history and a curated allowlist for
lab credentials.

## Frontend

### Fixed

- **API access logs on HTTPS now use the `no_tokens` format.** `nginx-ssl.conf`
  previously used the default format, which could log query strings (including
  WebSocket tickets or other tokens). It now matches `nginx.conf`.
- **Security headers on asset and download locations.** `/downloads/`,
  `/assets/`, and the image/font locations now include
  `security-headers.conf`, so `X-Content-Type-Options: nosniff` and the rest of
  the policy apply to the unauthenticated wstunnel binaries and static assets.
- **`connect-src` narrowed to `'self'`.** noVNC connects same-origin, so the
  bare `wss:`/`ws:` scheme sources were unnecessary.
- **Axios 401 handler safe parse.** A malformed impersonation value can no
  longer throw inside the 401 handler and strand the user.
- **`vue/no-v-html` is enforced.** The rule is on, with explicit exceptions for
  the two DOMPurify-sanitized sites (`TicketPanel.vue`, `TrackDetail.vue`).
- **CSP hash CI check.** `scripts/check-csp-hash.py` recomputes the
  `index.html` inline-script hash and fails when the nginx CSP is stale.

### Findings and follow-ups

- **JWT in `localStorage` (roadmap item).** The SPA stores the access token in
  `localStorage`, and `wiki_auth` is a JavaScript-set cookie so nginx can
  authenticate wiki subrequests. The strict CSP and the DOMPurify-only markdown
  path are the mitigations. A future move to an HttpOnly cookie plus a refresh
  flow would remove the XSS token-theft path; see the session-cookie roadmap
  below. This is a larger architectural change than this pass and is not a
  Release 4 blocker.
- **Workbook iframe isolation (origin split supported, safe fallback deployed).**
  Deployments with a second hostname for the same instance set `WIKI_BASE_URL`
  and give the wiki an HttpOnly `wiki_session` cookie scoped by
  `WIKI_COOKIE_DOMAIN`. The SPA keeps its token in `localStorage`; the framed
  wiki cannot read the parent origin or the HttpOnly cookie. The wiki CSP gains
  the app origin in `frame-ancestors`, and the legacy `X-Frame-Options` header is
  removed from wiki responses. See [`WIKI-ORIGIN-SPLIT.md`](WIKI-ORIGIN-SPLIT.md).
  Where no same-instance second hostname exists, the frame stays same-origin but
  is sandboxed without `allow-same-origin`; the JWT is still unreachable because
  the cookie is HttpOnly and the opaque document cannot read parent storage.
  The split is the preferred boundary; the fallback is the deployable one.
- **Wiki CSP.** The generated wiki no longer allows `unpkg.com` or
  `cdnjs.cloudflare.com`. Mermaid 11, html2pdf 0.10.2, and the theme CSS/JS are
  vendored or built locally, and `theme.font: false` prevents the Google Fonts
  request. Remaining inline script allowance is for the Material bootstrap.
- **Frontend Dockerfile.** The duplicate healthcheck and the unpinned
  `nginx:alpine` tag remain; pin by digest during the supply-chain pass.

## Session cookie roadmap (planned)

Status: **planned architectural hardening.** Keep the current design until the
migration below is implemented and tested.

Current design:

- the SPA keeps the JWT in `localStorage` and sends it as a Bearer token;
- `wiki_auth` is a JavaScript-set cookie used by nginx for wiki subrequests;
- CSP and DOMPurify reduce the chance of XSS, but any XSS that executes still
  has a readable token.

Target design:

- an **HttpOnly, Secure, SameSite=Lax** session cookie set by the backend on
  local login and SSO exchange;
- a short-lived access token plus rotating refresh, or a server-side session
  record with immediate revocation;
- CSRF defence for cookie-authenticated mutations (SameSite plus a
  double-submit token or strict Origin check);
- the app token held in memory only, never `localStorage`;
- the wiki gate validated server-side (`auth_request` or a backend-issued
  cookie) so JavaScript never has to create an authentication cookie;
- local administrator break-glass login unchanged.

Migration steps:

1. Add cookie issuance and a dual-auth window that accepts either Bearer or the
   session cookie.
2. Move the SPA to in-memory token state; remove token persistence and the
   `Authorization` header where the cookie is present.
3. Add CSRF tokens/origin checks and tests for state-changing endpoints.
4. Move the wiki gate to server-side validation; keep the current JS cookie only
   as a transitional fallback.
5. Revoke/rotate cookies on logout, password change, MFA change, and account
   erasure; confirm session revocation is immediate.
6. Remove the Bearer path and the JS cookie after the compatibility window.

Acceptance criteria:

- a simulated XSS cannot read a session token from `localStorage`;
- the session cookie is HttpOnly/Secure/SameSite and is not exposed to JS;
- cookie-authenticated mutations reject missing/invalid CSRF tokens;
- wiki access and workbook links still work;
- logout and account erasure invalidate the session immediately.

## RangeBox

### Fixed

The image ends with `USER kali`, but `entrypoint.sh` ran `iptables`, started
`dnsmasq`, and rewrote `/etc/resolv.conf`. `cap_add: NET_ADMIN` grants the
capability to the container's root, not to UID 10001, so those operations could
fail and the non-fatal `|| echo WARNING` paths would hide it.

- All privileged operations now use `sudo -n` (the image already grants kali
  NOPASSWD sudo).
- `block_gateways` counts applied rules and logs a warning when none apply.
- The comments now state that this layer is hygiene, not a security boundary:
  students have NOPASSWD sudo inside their own box and can flush the rules. The
  host `DOCKER-USER` policy is the real boundary.
- `scripts/audit-lab-isolation.py` now has a static `entrypoint-privilege` check
  that fails when a non-root image entrypoint runs `iptables`, `dnsmasq`, or
  `/etc/resolv.conf` writes without `sudo`.

### Follow-ups

- Switch the entrypoint to the shipped `supervisord.conf` so a crashed XFCE,
  x11vnc, or websockify process restarts instead of leaving a frozen desktop.
- Pin `kalilinux/kali-rolling` and the pip/SecLists inputs by digest or commit;
  this is the least reproducible image in the tree.
- The VNC port is unauthenticated (`-nopw`) under per-user isolation. If shared
  or team lab networks are ever added, put authentication or a per-box firewall
  in front of 5900/6080.

## Installer scripts

### Fixed

- **`/tmp/wstunnel` fallback removed.** `setup-wstunnel.sh` no longer copies an
  unverified binary from world-writable `/tmp` into `/usr/local/bin`. It
  downloads the official GitHub archive, verifies the published SHA256 for
  amd64/arm64, and refuses a mismatch.
- **Strict mode.** `install-platform.sh` and `deploy-updates.sh` now use
  `set -Eeuo pipefail`, matching the other root scripts.
- **`eval` removed from the verification phase.** `setup-range-server.sh` runs
  its static check strings in `bash -c` instead of `eval`.
- **Non-interactive install.** `setup-range-server.sh` accepts
  `--non-interactive`/`--yes`, requires `PUBLIC_IP` in internet mode, and uses
  explicit defaults for start, discover, prebuild, and wstunnel prompts.
  `GDG-Deploy.sh` passes the instance's external IP and the flag instead of
  piping `yes ''` into the installer.
- **ShellCheck gate.** `quality.yml` now runs `shellcheck --severity=error` on
  `scripts/*.sh`. The current tree passes at error severity; warning-level
  cleanup (SC2155 and friends) is a follow-up.

### Follow-ups

- Add a shellcheck warning-level baseline with a documented ignore list.
- Re-run the installer scripts in a disposable VM after the strict-mode change;
  `set -u` can expose latent unset variables that static checks miss.

## Peer Manager

### Fixed

- **Bind default.** `PEER_MANAGER_BIND` no longer defaults to `0.0.0.0`. It
  resolves to the `docker0` gateway when Docker is present (the backend reaches
  it through `host.docker.internal`) and falls back to `127.0.0.1`. An explicit
  `0.0.0.0` is refused and replaced with the Docker gateway or loopback.
- **Fail-closed auth.** The generated Peer Manager refuses to start without a
  `PEER_MANAGER_API_KEY` of at least 32 characters. `check_auth()` uses
  `hmac.compare_digest`.
- **Input validation.** `allowed_ips` is parsed with `ipaddress` and must be
  inside `WG_CLIENT_CIDR`, so a backend bug cannot add `0.0.0.0/0`.
- **Preshared keys are not returned.** The peer list nulls `preshared_key`.
- **Unit hardening.** The systemd unit sets `NoNewPrivileges=true` while keeping
  `ReadWritePaths=/etc/wireguard`.

### Follow-ups

- A loopback-only bind cannot be reached from a containerized backend. The
  current bridge-gateway bind is the safe compromise; a Unix socket proxy is
  the cleaner long-term answer.
- The Flask development server remains acceptable only because the service is
  loopback/bridge-bound and single-caller.

## Mail and sidecars

### Fixed

- **`mail_password` is encrypted at rest.** `settings_service` encrypts every
  `is_secret` setting with `crypto.encrypt_secret` and decrypts it for the mail
  service. The re-encryption script now includes `platform_settings` secret
  rows, so existing plaintext values migrate on the next `--apply`.
- **Snap7 download is checksum-verified.** `platform/tester/Dockerfile` pins the
  SourceForge archive SHA256 before unpacking.

### Follow-ups

- `db/ensure-db-password.sh` passes the password through `psql` argv; a
  `PGPASSWORD`-via-stdin variant would hide it from a same-host `ps`.
- The desktop boxes should standardize on `/etc/sudoers.d/` drop-ins; RangeBox
  and UbuntuBox currently append to `/etc/sudoers` directly.

## Image handling

- **Uploads are raster-only and re-encoded.** Avatars and competition logos
  accept a PNG, JPEG, or WebP data URL. The backend checks the data-URL shape,
  base64, byte cap, file signature, dimensions, and Pillow decode, then rebuilds
  the image from decoded pixels into a fresh PNG. Original bytes, EXIF, trailing
  data, and polyglot payloads are discarded. SVG and documents are rejected.
- **Profile updates are rate-limited.** `PUT /api/auth/settings` is limited to
  20 requests per minute per client.
- **External images are prohibited in learner content.** Workbook and manual
  images must be hosted locally; `scripts/check-external-images.py` fails CI on
  any external image reference so a learner's browser never fetches a
  third-party image the platform did not validate.

## Network tap

### Fixed

- **The capture no longer contains itself.** The tap mirrors every lab frame,
  including a student's own connection to port 9999. The `not port 9999` BPF
  filter is restored, so captures show lab traffic instead of the pcap stream.
- **Dead promiscuous-mode copy removed.** `platform/labs/_shared/network-tap/`
  duplicated the old design that the backend comments call insufficient. The
  live sidecar is `platform/network-tap/`.
- **Healthcheck added.** The image probes the 9999 listener, so a failed tap
  reports unhealthy instead of looking like an empty capture inside a lab.

Verification on development: the rebuilt image listens on 9999, emits a valid
pcap header (`d4 c3 b2 a1`) through `socat`, and accepts the filter expression.
`validate-lab.py --all` still reports 167 labs, 0 errors, 0 warnings.

### Follow-up

- Run the tap as a non-root user with `NET_RAW`/`NET_ADMIN` file capabilities
  (`setcap` on `tcpdump`) to match the backend non-root work.

## Performance

- Postgres now runs with explicit `shared_buffers`, `effective_cache_size`,
  `work_mem`, `maintenance_work_mem`, `wal_compression`, the slow-query log,
  and `idle_in_transaction_session_timeout` in both Compose files. Every value
  is env-overridable.
- `MPLBACKEND=Agg` is set for the backend, so report plots never probe for a
  display.
- `orjson` is **not** added yet; it is a dependency change that needs the
  supply-chain lock update and a rebuild. Treat it as a separate performance
  PR.

## Remaining backlog

1. Move the SPA token to an HttpOnly cookie and add a refresh flow.
2. Remove `'unsafe-inline'` from the wiki CSP once the Material bootstrap can be
   replaced with a hash-pinned script. The wiki JS/CSS are already self-hosted.
3. Switch RangeBox to supervisord and pin its toolchain.
4. Run the network tap as non-root with file capabilities.
5. Add warning-level shellcheck and a disposable-VM installer rehearsal;
   error-level shellcheck already runs in `quality.yml`.
6. Add a CI regression check for the host `DOCKER-USER` isolation rules.
7. Archive or delete the stale `opencyberrange-backup` repository after the
   secret scan is accepted; keep the scan evidence with the release notes.
