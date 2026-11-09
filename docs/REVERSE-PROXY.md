# Reverse proxy and Nginx Proxy Manager

Status: **Operator guidance**
Applies to: Community / Academic profile, Professional 2.5.0, Enterprise preview

The platform is designed to run behind a TLS-terminating reverse proxy. This
page records the settings that matter and the edge controls that complement
[anti-scraping](ANTI-SCRAPING.md).

## Nginx Proxy Manager

### Proxy host

| Field | Value |
|---|---|
| Domain names | your real public hostname, e.g. `labs.example.com` (placeholder) |
| Scheme | `http` |
| Forward hostname / IP | the Docker host running `ocr-frontend` |
| Forward port | `80` |
| Block common exploits | On |
| Websockets support | **On** (RangeBox/noVNC) |
| Cache assets | Off (the app sets its own cache rules) |
| Force SSL | On |
| HTTP/2 support | On |
| HSTS enabled | On |

!!! warning "Use the real hostname, not the placeholder"
    `labs.example.com` is documentation shorthand. If you edit an existing
    proxy host, keep its real public hostname (for example
    `ctfd.example.edu`) and add any new name as an additional domain. Replacing
    the live hostname with the placeholder removes the TLS server block for the
    real name and the edge will reject the handshake with
    `SSL_ERROR_UNRECOGNIZED_NAME_ALERT` (TLS alert 112).

Point the public DNS at Nginx Proxy Manager, not at the platform host. Restrict
the platform host's ports `80` and `443` to the proxy's address so the origin
cannot be reached directly.

### Advanced configuration

Paste this into the proxy host's **Advanced** tab. It covers WebSockets, SSE,
large workbook uploads, client identity, the public scheme, and the crawler
block.

```nginx
# Workbook ZIP uploads are capped at 50 MB in the app; leave headroom.
client_max_body_size 64m;

# WebSockets for RangeBox/noVNC. Nginx Proxy Manager defines
# $connection_upgrade; if your version rejects it, use "upgrade" here.
proxy_http_version 1.1;
proxy_set_header Upgrade $http_upgrade;
proxy_set_header Connection $connection_upgrade;

# Long-lived VNC sessions and server-sent events (exercise tests, exports).
proxy_connect_timeout 60s;
proxy_read_timeout 3600s;
proxy_send_timeout 3600s;

# Stream SSE and uploads instead of buffering them.
proxy_buffering off;
proxy_request_buffering off;
proxy_cache off;

# Keep the public host and scheme for certificate QR links, mail links, and
# audit records. Overwriting X-Forwarded-For stops clients spoofing the first
# address in the chain.
proxy_set_header Host $host;
proxy_set_header X-Real-IP $remote_addr;
proxy_set_header X-Forwarded-For $remote_addr;
proxy_set_header X-Forwarded-Proto $scheme;
proxy_set_header X-Forwarded-Host $host;

# Block crawlers before they reach the platform. The origin repeats this
# check, so this is an early drop rather than the only control.
if ($http_user_agent ~* "(GPTBot|OAI-SearchBot|ChatGPT-User|Google-Extended|ClaudeBot|Claude-Web|anthropic-ai|PerplexityBot|CCBot|Bytespider|Amazonbot|Applebot-Extended|Meta-ExternalAgent|Meta-ExternalFetcher|cohere-ai|YouBot|Diffbot|omgili|omgilibot|Scrapy|AhrefsBot|SemrushBot|MJ12bot|DotBot|PetalBot|Barkrowler|DataForSeoBot|Googlebot|Bingbot|Slurp|DuckDuckBot|Baiduspider|YandexBot|Sogou|Exabot|Qwantify|SeznamBot|NaverBot|Yeti|ia_archiver)") {
    return 403;
}

# One X-Robots-Tag at the edge instead of the origin's copy plus this one.
proxy_hide_header X-Robots-Tag;
add_header X-Robots-Tag "noindex, nofollow, noarchive, nosnippet, noimageindex, noai, noimageai" always;
```

If Cloudflare or another CDN sits in front of Nginx Proxy Manager,
`$remote_addr` is the CDN edge, not the learner. In that case configure the
proxy's real-IP module for the CDN ranges and use the CDN's client-IP header
before relying on `X-Forwarded-For` for audit or rate limiting.

### Scheme and public URLs

Nginx Proxy Manager terminates TLS and usually forwards to the origin over
HTTP. The frontend nginx now preserves an incoming `X-Forwarded-Proto` when it
calls the backend, so the advanced configuration above is enough for generated
certificate links and mail links to use `https://`.

As a belt-and-braces measure, set both of these in **Admin → Settings** to the
public HTTPS URL:

- `certificate_verify_url` — e.g. `https://labs.example.com`
- `mail_public_url` — e.g. `https://labs.example.com`

They also cover deployments that use a different proxy or an internal hostname.

### WireGuard and other non-HTTP traffic

Do **not** put WireGuard behind an HTTP proxy host. Forward `51820/UDP` directly
to the platform host, or use Nginx Proxy Manager's **Streams** tab for TCP/UDP.
The same applies to any optional WSTunnel TCP port. HTTP proxy hosts only carry
HTTP and WebSocket traffic.

## Why these settings

| Setting | Reason |
|---|---|
| WebSockets on | The browser noVNC client opens a WebSocket under `/api/rangebox/.../vnc`. |
| 3600s read/send timeout | A lab terminal or SSE stream can stay open far longer than the 60s default. |
| Buffering off | SSE responses (`text/event-stream`) must reach the browser as they are produced. |
| 64 MB body limit | Workbook ZIPs are capped at 50 MB in the backend; the default 1 MB would reject them. |
| `X-Forwarded-For $remote_addr` | The app records client IPs for audit and rate limiting; do not trust a client-supplied chain. |
| Crawler `403` | The platform is private; search and AI crawlers have no legitimate reason to fetch it. |

## Capacity tuning (Nginx Proxy Manager 2.16+)

Nginx Proxy Manager leaves its `events` block empty, so nginx uses the built-in
`worker_connections` value of 512 per worker. That is fine for a small class,
but not for a room full of noVNC/WebSocket sessions and SSE streams: every
proxied browser session consumes a client socket and an upstream socket, so the
connection ceiling is reached long before CPU or memory is.

Set the limits through NPM's custom include points, not by editing generated
host files.

`/data/nginx/custom/root_top.conf`:

```nginx
worker_rlimit_nofile 65535;
```

`/data/nginx/custom/events.conf`:

```nginx
worker_connections 16384;
multi_accept on;
```

Size `worker_connections` for at least **twice the peak number of proxied
sessions per worker**, plus headroom for ordinary requests. With
`worker_processes auto`, the total ceiling is `worker_connections x workers`,
but the per-worker file-descriptor limit must be raised as well. A WebSocket
uses two descriptors (browser and backend); listening sockets, logs, and cache
files need descriptors too.

Do not put `worker_connections` in an `http` block; it belongs in `events`.
Apply custom event settings with a reload rather than a restart:

```bash
docker exec <npm-container> nginx -t
docker exec <npm-container> nginx -T | grep -E 'worker_connections|worker_rlimit_nofile'
docker exec <npm-container> nginx -s reload
```

### Where per-host settings land

NPM writes a proxy host's **Advanced** text at **server** level, then includes
`conf.d/include/proxy.conf` inside `location /`. That include sets `Host`,
`X-Forwarded-*`, and `X-Real-IP`, so a `proxy_set_header` added in Advanced does
not override those values; header changes belong in NPM's host/forwarding
settings or a location-level custom include.

The server-level directives below are inherited by `location /` and are the
ones that matter for interactive traffic:

```nginx
# Long-lived WebSocket and SSE sessions
proxy_connect_timeout 60s;
proxy_read_timeout 3600s;
proxy_send_timeout 3600s;

# Stream SSE and uploads instead of buffering them
proxy_buffering off;
proxy_request_buffering off;
proxy_socket_keepalive on;

# Workbook ZIPs are capped at 50 MB in the app; leave headroom
client_max_body_size 64m;
```

Keep timeouts and buffering scoped to the interactive host rather than global.
A static or download-heavy host can use buffering and shorter timeouts, while
an interactive host needs long-lived streams. A large `client_max_body_size` on
every host also removes a useful upload limit.

NPM regenerates `/data/nginx/proxy_host/*.conf` from its database when a host is
saved, so edit hosts through the UI or API; hand edits to those generated files
are replaced on the next save. Files under `/data/nginx/custom/` are not
regenerated.

### Restart and certificate note

Prefer `nginx -s reload` for configuration changes. A full container restart
also runs NPM's certificate renewal pass at startup; on a busy edge, repeated
restarts can trigger a burst of forced renewals and hit Let's Encrypt rate
limits. Restart only when the image, database settings, or startup wiring
actually changes.

## Verification

```bash
# WebSocket upgrade reaches the backend
curl -fsSI -H 'Connection: Upgrade' -H 'Upgrade: websocket' \
  https://labs.example.com/api/rangebox/standalone/vnc

# Large-upload path is not rejected by the proxy
curl -fsSI https://labs.example.com/api/admin/curriculum/upload

# Public scheme is preserved
curl -fsS https://labs.example.com/api/version
```

WebSocket requests without a valid ticket are expected to close with an
authentication error; what matters is that the proxy upgrades the request
rather than returning `400` or `426`.

## Troubleshooting TLS

### `SSL_ERROR_UNRECOGNIZED_NAME_ALERT` (TLS alert 112)

This alert comes from the **edge**, not the platform. It means the edge has no
enabled proxy host and certificate for the SNI name the browser sent. Nginx
Proxy Manager's default `443` server uses `ssl_reject_handshake on;`, so an
unknown name is rejected before the request reaches the origin.

Confirm the split:

```bash
# Edge: fails with alert 112
echo | openssl s_client -connect <edge-ip>:443 \
  -servername <public-host> -brief

# Origin: should complete with the origin certificate
echo | openssl s_client -connect <origin-ip>:443 \
  -servername <public-host> -brief
```

If the origin succeeds and the edge fails, fix the edge:

1. Open Nginx Proxy Manager (`http://<edge-ip>:81`).
2. Open **Hosts → Proxy Hosts** and find the entry for the public hostname.
   If it is missing, recreate it with the same domain, the origin IP, port `80`,
   WebSockets on, and the existing certificate.
3. If it exists, confirm it is **Enabled**, the domain matches exactly, and the
   **SSL** tab has a certificate attached and **Force SSL** is on.
4. If the certificate is missing or expired, request a new Let's Encrypt
   certificate for the real hostname or upload a valid certificate. NPM will
   not serve a name it has no certificate for.
5. Save and test again:

```bash
curl -vkI https://<public-host>/
openssl s_client -connect <edge-ip>:443 -servername <public-host> -brief
```

Do not point DNS at the origin as a workaround unless the origin has a
certificate for the public name. The platform certificate is usually
self-signed for the host IP; browsers will still warn.

### `502` or `504` after TLS succeeds

TLS is healthy but the proxy cannot reach the origin. Check the proxy host's
forward IP and port (`80` for the platform frontend), then test from the proxy
host with `curl -I http://<origin-ip>/`. Do not forward to `443` unless the
origin is intentionally serving TLS.

### WebSocket connects then closes

Check that **Websockets support** is on and that the advanced configuration
keeps `Upgrade` and `Connection` headers. The backend still requires a valid
ticket, so an authentication close is expected.
