# Next steps

Status: **Release 5.55.2 is deployed to development and production.** The
read-only HA status panel (endpoint, Admin card, witness endpoint, host
collector) is implemented; the witness/collector install and live drills
remain. The exercise workspace now has a read-only Briefing tab and pop-out.
The threat-awareness snapshots are refreshed and a weekly operations
automation is scheduled. Dependency maintenance cleared the dev/tooling
Dependabot backlog; runtime and OS updates remain for review. This page tracks
what is left; the deployment record is
[`RELEASE-5-PRODUCTION-READINESS.md`](RELEASE-5-PRODUCTION-READINESS.md).

## 5.55.2

- **Pathway mapping fix.** Manifest ids such as `webpt`, `linpt`, `winpt`, and
  `netfor` now translate to the database track slugs before filtering. The
  Penetration Tester focus shows Web, Linux, Windows, and Network; SOC Analyst
  again includes its core tracks. Role readiness uses the same mapping for next
  workbooks and completed-role evidence.
- **Regression coverage:** the catalogue and alias translation tests include the
  full Penetration Tester track set.

## 5.55.1

- **URL-backed focus.** `?view=focused|all` and `?target=<pathway>` survive
  refresh, shared links, and back/forward.
- **Server-side narrowing.** `GET /api/exercises/tracks?role=<pathway>` filters
  after the existing visibility and course-assignment checks, so a focused page
  downloads only the visible tracks for that pathway. The response includes
  `total_tracks` for the "X of Y" label.
- **Least privilege.** The pathway filter can only narrow the visible set; it
  cannot add a hidden or unavailable track. Unknown pathways return an empty
  focused list and the UI offers the full catalogue.
- **Cleanup:** the pathway catalogue no longer exposes the unused `categories`
  field, and the API manual documents the `role` query parameter.

## 5.55.0

- **Career-focused exercise catalogue.** New learners start on the
  Cybersecurity Foundations pathway and see only the tracks aligned with their
  career target. The career-target selector is on the Exercises page, the full
  catalogue is one click away, and completing every focused track marks the
  pathway complete and invites exploration. The dashboard track list follows the
  same focus.
- **Role catalogue:** `GET /api/profile/roles` exposes each pathway's `tracks`,
  so the catalogue and dashboard use one source of truth. Release 5.55.1 removes
  the unused `categories` field and adds the server-side filter.

## 5.54.0-5.54.2

- **Split-layout wiki build.** The split updater imported a removed
  `build_all_wikis` helper and required a root `mkdocs.yml` that this repository
  does not track, so the development wiki volume was never rebuilt. It now uses
  the same one-shot `wiki-builder` service as production, adds the service to
  the dev compose, and writes a local override for legacy root compose files.
- **Briefing workbook link.** The pop-out recomputes the workbook URL from the
  shared wiki-origin reference, so the link follows `/api/config/public` when
  that asynchronous config sets a separate wiki origin. Covered by a frontend
  regression test.
- **Exercise briefing.** A read-only Briefing tab sits beside Desktop, Exercise,
  and Workbook; the selected tab stays in `?tab=briefing`. **Pop out briefing**
  opens the same `ExerciseBrief` component on
  `/exercises/:trackSlug/briefing` without app chrome or an opener reference.
  The scenario, objectives, hostnames, workbook link, and unlocked hints use
  the sanitized markdown path; the flag and learner PII are not included. The
  pop-out supports print and a 375 px viewport.

## Current wave (5.52.6–5.53.1)

- **HA status panel.** `GET /api/admin/system/ha`, the Admin card, replication
  and witness attention entries, the read-only witness endpoint, the 30-second
  host collector, and the `/var/lib/ocr-ha` mount are implemented. The full
  witness → collector → backend chain passed on development. Install and live
  drills remain.
- **RangeBox lifecycle.** Proxy networks allocate a free `/29`, VNC peers are
  derived from the real subnet, backend reattach follows the allocated block,
  and `get_rangebox_ip()` fails closed instead of guessing a base `.2`.
- **Workbook origin.** A TLS deployment derives `https://<host>:8443` when
  `wiki_origin` is empty; enrolled and admin course wikis receive the dynamic
  frame-ancestor policy.
- **Threat awareness.** Hostile-infrastructure snapshots now combine FireHOL
  with curated DShield, Blocklist.de, abuse.ch Feodo, OffSeq Mirage, and IPsum
  feeds; RansomLook is refreshed. A weekly ops automation and helper script
  keep the review moving.
- **Maintenance.** Fixed the duplicate `psycopg` pin, documented `ws_tickets`,
  and merged the green dev/tooling dependency PRs. Backend tests are 671;
  frontend 77; HA 91.

## Earlier completed

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

1. **HA status panel rollout.** Install the witness compose on the Unraid
   witness, run `install-ha-status-collector.sh` on `.41` and `.44`, then run the
   drills in the
   [HA status-panel drill runbook](https://github.com/RobChaykoski/opencyberrange-ha/blob/main/docs/14-ha-status-drills.md)
   (HA repository). The card is hidden until the snapshot exists.
2. **Runtime dependency review.** Open Dependabot PRs remain for `axios`,
   `marked`, the nginx digest, and Ubuntu 25.10. They were intentionally left
   for runtime/OS review; the dev/tooling updates are merged.
3. **Cyber DNA v3 Phase 3.** The Phase 2 learner UI shipped in v5.31.0 and is
   live: the Profile career-affinity panel and the dashboard DNA band. Production
   has 47 evidence rows for 4 learners and 0 snapshots; development has 503 rows
   for 2 learners and 0 snapshots. The affinity gate is unmet. Next: let the
   consenting cohort accumulate evidence, re-run the consent-gated backfill
   after consent changes, then tune the behavior weights and affinity formula
   after a term. See [`CYBER-DNA-V3.md`](CYBER-DNA-V3.md). Affinity only;
   employer access is out of scope.
4. **Python 3.15** when it reaches GA. Three interpreter CVEs are fixed only on
   the 3.15/3.16 branches; do not chase alpha releases.
5. **Docker CLI Go findings** move with Docker Inc.'s next trixie package.
6. **Weekly threat-feed review.** The OpenCode automation runs Monday 09:00 ET;
   review the aggregate diff, then ship a signed snapshot release when it
   changes.

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
