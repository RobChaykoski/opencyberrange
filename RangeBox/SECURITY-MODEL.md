# RangeBox security model

RangeBox is a disposable Kali/Ubuntu/REMnux desktop for training. The learner is
intentionally the administrator **inside** the container; the isolation boundary
is the container network and the host firewall, not the Linux user inside the
desktop.

## Accepted design

- The desktop user (`kali`/`student`) has passwordless sudo because the exercises
  install tools, edit system files, and practise privilege escalation. Removing
  sudo would break the teaching contract.
- Firefox runs with `MOZ_DISABLE_CONTENT_SANDBOX=1`. The desktop is Xvfb inside a
  container without the user-namespace support needed for the browser sandbox.
  The compensating control is that the browser has no host filesystem, no host
  network, and the container is destroyed after the session.
- The container is not privileged, does not use host networking, and has no
  access to the Docker socket. Lab networks are separate bridges with host
  firewall rules applied by the installer/Peer Manager.

## Boundary

The learner may be root inside RangeBox, but must not be able to:

- reach the host management interface or the Docker socket;
- reach another learner's network;
- persist data after the session is stopped;
- reach the public internet unless the lab explicitly needs it.

Host firewall/routing rules and the isolation audit
(`scripts/audit-lab-isolation.py`) are the enforcement points. Re-verify them
after any firewall, Docker, or VPN change.

## Data

RangeBox holds no learner records, credentials to the platform, or persistent
personal data. The platform account, workbook, and flag delivery live outside
the desktop container. Treat anything typed into a lab as disposable.

## Validation

- `scripts/audit-lab-isolation.py` checks the host network rules.
- The workspace regression spawns a live RangeBox and verifies the desktop,
  flag dock, and stop path.
- Two builds from the pinned Kali digest and SecLists commit are expected to be
  equivalent; changing either input requires a new image validation run.
