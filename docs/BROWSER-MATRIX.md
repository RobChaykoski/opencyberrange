# Browser and device matrix

The automated UI smoke runs each browser engine with the same desktop and mobile
viewport checks. The workflow is `.github/workflows/ui-smoke.yml` and runs
nightly, on demand, and against the configured deployment.

## Automated

| Engine | Desktop | Mobile viewport |
|---|---|---|
| Chromium | Yes | Yes |
| Firefox | Yes | Yes |
| WebKit | Yes | Yes |

`UI_BROWSER` selects the engine in `scripts/ui-smoke.mjs`. Each matrix job
installs only its engine with `playwright install --with-deps`.

Current automated coverage:

- sign-in and token storage
- dashboard, profile, privacy settings, celebration wall
- RangeBox page shell
- consent and privacy settings
- desktop (1440x900) and mobile (390x844) viewports

## Manual noVNC pass

Automated screenshots cannot prove keyboard/mouse behaviour inside a VNC
canvas. Before a release, run this on each supported browser:

1. Launch a RangeBox lab.
2. Move the pointer, click, type, and use Ctrl/Alt/Cmd combinations.
3. Use the browser's zoom controls and a high-DPI display.
4. Resize the window and open the mobile layout.
5. Copy/paste text between the browser and the desktop.
6. Disconnect/reconnect the network and confirm the VNC session recovers.
7. Confirm the browser's back/forward and refresh do not leave a stale session.

Record the browser version, OS, and result in the release notes.

## Supported baseline

- Chromium-based: current stable Chrome/Edge
- Firefox: current stable
- Safari/WebKit: current Safari on macOS and iOS
- Mobile: current iOS Safari and Android Chrome

Older browsers may work but are not part of the release gate.
