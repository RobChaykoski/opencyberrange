# Ubuntu next upgrade candidate

Status: **test candidate — not certified for production**

Requested label: **Ubuntu 26.06**
Available upstream baseline: **Ubuntu 26.04 LTS**

Ubuntu publishes LTS releases in April, not June. There is no Ubuntu 26.06
release; the next LTS after 24.04 is **26.04**. The workflow therefore defaults
to the GitHub-hosted `ubuntu-26.04` runner. If a custom 26.06 image or runner is
provided later, dispatch the workflow with that runner label.

## Why this is the next candidate

- Ubuntu 24.04 LTS is the certified 2.5.4 host baseline.
- Ubuntu 26.04 LTS is the next long-lived host baseline for the 2.5.x/2.6 line.
- The platform containers are unchanged (`python:3.11-slim`, `node:22-alpine`,
  `nginx:alpine`, `postgres:15-alpine`, `redis:7.2-alpine`).
- The host installer targets "Ubuntu 22.04 or newer", so 26.04 should mostly
  reuse the 24.04 path. The unknown is host tooling: Docker, nftables,
  WireGuard, KVM, and systemd behaviour.

## GitHub test build

Workflow: `.github/workflows/ubuntu-next.yml`

It runs manually and weekly on `ubuntu-26.04` and checks:

- host identity, Python, Node, Docker, and Compose versions;
- shell syntax for the installer, setup, update, upgrade, and post-install
  scripts;
- `setup-range-server.sh --help` and `install-platform.sh --help`;
- workbook coverage, quiz-bank validation, supply-chain lock, lab validation,
  and lab release proof;
- production Compose rendering;
- backend and frontend image builds.

## What still requires a real host

The GitHub runner validates the build and script layer, not the full network
appliance. These remain host-certification gates:

- KVM availability and Windows lab VMs;
- WireGuard peer management and firewall persistence across reboot;
- nftables/Docker isolation rules;
- backup and restore drill;
- large-cohort session and VPN load.

## Promotion rule

Do not move production to 26.04 until the real-host gates pass and
`docs/OS-SUPPORT.md` marks it **Certified**. Until then, 24.04 LTS remains the
supported production baseline.
