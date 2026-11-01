# RemnuxBox

Browser-based REMnux desktop for the OpenCyberRange platform, selectable next
to **Kali** and **Ubuntu** on the dashboard.

REMnux is a Linux distribution for malware analysis and reverse engineering. The
upstream `remnux/remnux-distro` image is built for CLI use (SSH, or GUI over an
SSH tunnel), so this image adds the same Xvfb + XFCE4 + x11vnc + noVNC stack that
`UbuntuBox` uses. Students then reach the REMnux toolkit through the platform's
existing noVNC viewer, with no tunnel setup.

## Size

The base image is roughly **6 GB compressed / 14 GB on disk**. Build or pull it
during provisioning, not at a student's first launch.

## Build

```bash
docker build -t opencyberrange/remnuxbox:noble RemnuxBox/
```

The platform resolves the `remnux` shorthand to `REMNUX_IMAGE`
(`opencyberrange/remnuxbox:noble` by default). Override it to point at a
different build or registry:

```bash
REMNUX_IMAGE=registry.example.com/remnuxbox:noble
```

## Run (standalone smoke test)

```bash
docker run --rm -p 6080:6080 --shm-size=256m opencyberrange/remnuxbox:noble
```

Open <http://localhost:6080/vnc.html>. The VNC port itself is unauthenticated by
design: in the platform it is only reachable on the internal lab network, and
the browser connects through FastAPI's authenticated WebSocket proxy.

## Notes

- The desktop runs as the distro's own `remnux` user so PATH, virtualenvs and
  tool configuration match the upstream image. Passwordless `sudo` is added.
- Image and OSINT extras are included for the OSINT track: `exiftool`,
  `binwalk`, `foremost`, `steghide`, `pngcheck`, `zsteg`, ImageMagick, and
  Python Pillow.
- Wine-dependent tools (`scdbg`, `ssview`, `shellcode2exe-bat`, `runsc`) and
  VS Code are excluded from the upstream container. Install them with
  `remnux install --user remnux` if an exercise needs them.
- `supervisord.conf` is an alternative to `entrypoint.sh` for deployments that
  want automatic process restart; the Dockerfile uses the entrypoint.
