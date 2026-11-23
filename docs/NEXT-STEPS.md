# Next steps

Status: **Release 5.30.1 is deployed to development and production
(`deployment_mode=production`, `sso_enabled=false`). Cyber DNA v3 Phase 1 is
enabled on development only.** The platform runs Python 3.13, the
security hardening wave is live, the OT track has three exercises plus an
offline scan assistant, and the user manual reflects the current UI.
This page tracks what is left; the deployment record is
[`RELEASE-5-PRODUCTION-READINESS.md`](RELEASE-5-PRODUCTION-READINESS.md).

## Recently completed

- **Release 5.30.1 and pilot cleanup.** LTI launches no longer depend on the
  SSO switch, so production runs with `sso_enabled=false`. Moodle's cURL
  blocked-host list is narrowed to the NPM JWKS address only. The remaining
  pilot item is the Cloudflare DDNS token rotation before the next cohort.
- **Release 5.30.0.** Self-service password reset, pilot workspace and
  RangeBox fixes, workbook cards that open the learner's current exercise, a
  career-target switcher, the sidebar tools drawer, privacy-first account
  defaults with age bands, LTI instructor-role mapping, and the post-pilot
  infrastructure cleanup. See the [changelog](../CHANGELOG.md).
- **Cyber DNA v3 Phase 1.** The event-driven DNA context, evidence ledger,
  behavior/interest/affinity derivation, snapshot API, gated `30/3/100`
  affinity, backfill adapter, and erasure hook are implemented and enabled on
  development. Migration `0032` applied; backfill wrote 740 evidence rows for
  53 learners; both sides of the affinity gate were verified. Production
  remains gated. See [`CYBER-DNA-V3.md`](CYBER-DNA-V3.md).
- Network-appliance lab `network-12-6-appliance-segment`: a dual-homed OpenWrt
  24.10.5 appliance with a protected internal segment, a default-deny forward
  chain, and an SSH local-forward pivot. Includes a workbook page, the NET04
  framework mapping, and the pinned image notices.
- Manual publishing: `docs-publish.yml` builds the manual (or every site for
  inspection), checks the built output, and publishes a checksummed artifact.
  The decision and internal-web-root recipe are in `MANUAL-PUBLISHING.md`.
- Persisted learner snapshots: `learner_snapshots` stores the career dossier and
  portfolio payload, schema/formula versions, and the factor weights used.
  Stored reports re-render from the snapshot, so a later scoring change cannot
  rewrite an old report.
- Release 5.15.0: RangeBox-by-default launch choice with an in-app stop dialog,
  pending-approval and inactive-account login states, the offline OT Scan
  assistant, and OT 1.3 (gateway bypass). Tagged as `v5.15.0`.
- Weekly built-image scan in CI (Syft SBOM plus Grype SARIF, failing on a
  fixable critical), replacing the manual scan runs.
- Security review fixes: sanitised client IPs, pinned GPG verification,
  instructor grouped counts, compose host-escape guard, lab capability and
  process limits, and the Compose `pids_limit` shape fix.
- Image hardening: pinned base digests, build-time OS upgrades, no `curl`,
  `gnupg`, `pip`, `setuptools`, or `wheel` in the backend runtime, and readable
  copied source/static files after the 027 umask.
- Python 3.13 runtime and CI migration, with the full suite green on 3.13.
- Host hardening: umask 027 and disabled core dumps on dev and production, with
  a post-pull permission normalisation for bind-mounted lab content.
- OT 1.1 (read registers), OT 1.2 (setpoint write), and OT 1.3 (gateway
  bypass).
- First-run "Discover your Cyber DNA" flow, dashboard DNA band, growth velocity
  with 30/60/90 trends, and confidence gates for career recommendations.
- Manual refresh: live screenshots, corrected navigation and course/admin
  instructions, and the redesigned footer.

## Open queue

1. **Cyber DNA v3 rollout.** Development is enabled and backfilled. Production
   is now backfilled too (274 evidence rows, 15 learners, 41 activities) and the
   gate is verified: learner 16 is available with 13 pathways, while below-gate
   learners return none. Next: ship the Phase 2 learner UI, then tune the
   behavior weights after a term of evidence. See
   [`CYBER-DNA-V3.md`](CYBER-DNA-V3.md). Affinity only; employer access is out
   of scope.
2. **Python 3.15** when it reaches GA. Three interpreter CVEs are fixed only on
   the 3.15/3.16 branches; do not chase alpha releases.
3. **Docker CLI Go findings** move with Docker Inc.'s next trixie package.

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
