# Next steps

Status: **Release 5 is deployed to development and production.** The platform
runs Python 3.13, the security hardening wave is live, the OT track has three
exercises (read, write, gateway), and the user manual reflects the current UI.
This page tracks what is left; the deployment record is
[`RELEASE-5-PRODUCTION-READINESS.md`](RELEASE-5-PRODUCTION-READINESS.md).

## Recently completed

- Security review fixes: sanitised client IPs, pinned GPG verification,
  instructor grouped counts, compose host-escape guard, lab capability and
  process limits, and the Compose `pids_limit` shape fix.
- Image hardening: pinned base digests, build-time OS upgrades, no `curl`,
  `gnupg`, `pip`, `setuptools`, or `wheel` in the backend runtime.
- Python 3.13 runtime and CI migration, with the full suite green on 3.13.
- Host hardening: umask 027 and disabled core dumps on dev and production.
- OT 1.1 (read registers) and OT 1.2 (setpoint write).
- Manual refresh: live screenshots, corrected navigation and course/admin
  instructions, and the redesigned footer.

## Open queue

1. **Network-appliance lab.** Add an OpenWrt or pfSense target on the existing
   Docker topology for firewall and routing exercises. Larger than an OT lab
   because it introduces a second network segment.
2. **Automated image scans.** Move Syft and Grype from manual runs into a weekly
   CI job with SBOM artifacts and a critical-finding gate.
3. **Manual publishing.** CI builds every MkDocs site, but the repository has no
   publish workflow. Decide where the built manual is hosted (release artifact,
   internal web root, or documentation host) and add that step.
4. **Python 3.15** when it reaches GA. Three interpreter CVEs are fixed only on
   the 3.15/3.16 branches; do not chase alpha releases.
5. **Docker CLI Go findings** move with Docker Inc.'s next trixie package.

## Deliberately deferred

- **Windows labs.** Each needs a licensed guest image and a KVM host. Save for a
  dedicated wave; do not ship a half-built Windows target.
- **Multi-tenancy and the TA role.** Release 5 is a single-tenant appliance.
  Changing that is an architecture project, not a setting.
- **Distroless frontend.** The nginx entrypoint selects the HTTP/HTTPS config;
  a distroless migration needs header and auth parity tests first.
- **External Backpack validation, terminal-only RangeBox, VPAT/SOC 2/ISO
  certifications.** Not held or shipped by this release.

## Historical

The Release 3/4 queue was closed by the Release 4 tag and the Release 5 work
above. See `RELEASE-4-CLOSE-OUT.md` for that record.
