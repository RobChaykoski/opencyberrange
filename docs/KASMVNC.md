# KasmVNC transport for RangeBox

Status: **implemented for the Kali RangeBox image; mixed deployments remain
supported.** UbuntuBox and RemnuxBox continue to serve noVNC until their images
are rebuilt with the same change.

## Why the transport changed

KasmVNC was deferred from Release 5 after an evaluation. The original plan
assumed it was a drop-in replacement for `x11vnc` + `websockify` + noVNC. It is
not:

- noVNC can complete the RFB handshake with KasmVNC and render the framebuffer.
- noVNC **cannot send keyboard or pointer input** to KasmVNC, and its
  `resizeSession` and clipboard messages are ignored.
- KasmVNC's own client uses KasmVNC's protocol extensions and works for input,
  resize, clipboard, and its control bar.

Measured on the development host (1280x800 desktop, 1000x700 and 1400x900
viewport tests):

| Check | noVNC + x11vnc | KasmVNC + its client |
|---|---|---|
| Desktop resize to the browser viewport | Not measured | 1000x700 and 1400x900, exact |
| Idle WebSocket traffic over 6 s | 2 frames / 44 chars | 0 frames |
| Pointer activity over 6 s | 102 frames / 844 chars | 113 frames / 22,828 chars |
| Input | Works | Works |
| Clipboard | Works through the platform toolbar | Works through the KasmVNC control bar |

The activity byte count is not a like-for-like compression benchmark: the two
clients encode different update regions and cursor state. It is recorded to
show that KasmVNC is not a bandwidth-free win and must be tuned on school
networks.

## Architecture

```
Browser
  └── RangeBox.vue
        ├── GET /api/rangebox/transport   (probes the container)
        ├── iframe /kasm/vnc.html         (trusted, vendored KasmVNC client)
        │     └── WebSocket /api/rangebox/{session}/vnc?token=...
        └── noVNC RFB                     (older images only)
                                              │
                                     FastAPI WebSocket proxy
                                              │
                                  KasmVNC in the RangeBox container :6080
```

The platform's WebSocket proxy is unchanged: it authenticates the short-lived
ticket, enforces session ownership, and drops browser-to-container frames for
admin "View As" sessions. KasmVNC runs with `SecurityTypes None` and
`DisableBasicAuth`; the port is only reachable on the internal Docker network.

### Client trust

The KasmVNC web client is **not** loaded from the student's container. A student
has root in that container and could otherwise serve arbitrary JavaScript into
an instructor's browser. The client is vendored from the pinned release into
`platform/frontend/public/kasm/` and served by the platform's nginx under
`/kasm/` with a tailored CSP. Comments in the client are unmodified.

### Transport detection

`GET /api/rangebox/transport` fetches the container's `/vnc.html` and checks for
the `KasmVNC` title. This keeps rolling rebuilds working: an old noVNC image
gets the old viewer, a KasmVNC image gets the iframe. If the probe fails, the
safe default is noVNC.

## Pinned inputs

| Input | Value |
|---|---|
| KasmVNC release | `v1.5.2` |
| Debian package | `kasmvncserver_kali_kali-rolling_1.5.2_amd64.deb` |
| SHA-256 | `f57bba80fe7f0ca95e598c395a6a5292d16e04be1e09949410415492ead62fba` |
| Source | <https://github.com/kasmtech/KasmVNC/tree/v1.5.2> |
| Licence | GPL-2.0 (`THIRD_PARTY_LICENSES/GPL-2.0.txt`) |

The vendored client is unmodified from the release. Its HTML uses inline
event handlers, so the `/kasm/` location allows `'unsafe-inline'` for scripts;
the SPA keeps its hash-pinned policy. The CSP also allows `data:`/`blob:` for
the client's WebAssembly decoder and same-origin workers.

`RangeBox/Dockerfile` downloads, verifies, and installs that package. The
vendored client in `platform/frontend/public/kasm/` is the same release's
`/usr/share/kasmvnc/www` tree. Bumping one requires rebuilding the other and
re-checking the `/kasm/` CSP.

## Behaviour and limits

- **Control bar**: KasmVNC's own control bar provides clipboard, Ctrl+Alt+Del,
  quality/stream settings, and fullscreen. The platform hides its noVNC-only
  quality, clipboard, and Ctrl+Alt+Del controls for KasmVNC sessions.
- **Flag capture**: the desktop-to-browser clipboard event used to populate the
  flag field is not available inside the iframe. Copy the flag in the desktop,
  then use the existing "Paste and clean the flag from your clipboard" button.
- **Reconnect**: the iframe uses a single-use WebSocket ticket, so automatic
  reconnect is disabled. Use **Reload desktop**; it mints a fresh ticket.
- **File transfer**: the open-source KasmVNC client does not add a file-transfer
  panel. The "text only" rule in the clipboard panel remains the contract.
- **WebRTC/UDP**: not enabled. The platform proxies the WebSocket on the same
  origin, which works through the existing reverse proxy.
- **TLS**: KasmVNC's own HTTPS listener is disabled (`sslOnly 0`) because the
  platform terminates TLS and proxies plain WebSocket on the internal network.
  The container still generates the Debian snakeoil certificate so KasmVNC can
  start.

## Rollout

1. Build the image on the host:
   `docker build -t opencyberrange/rangebox:lite --target lite RangeBox/`
2. Existing sessions keep their container; new sessions detect the new image.
3. No platform environment flag is required. The transport probe selects the
   viewer per container.
4. To roll back, retag the previous image and restart the session. The platform
   keeps the noVNC viewer and served client for compatibility.

## Validation

- `platform/backend/tests/test_rangebox_transport.py` covers probe selection.
- The platform frontend build includes `/kasm/` and the CSP tested with the
  KasmVNC client.
- End-to-end: launch a RangeBox, confirm the iframe connects, type into a
  terminal, resize the browser window, and verify the desktop dimensions track
  the viewport. Admin "View As" must remain read-only.
