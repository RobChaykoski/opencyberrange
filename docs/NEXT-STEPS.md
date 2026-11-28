# Next steps

Status: **Release `5.60.0` is tagged and pending deployment.** This
page tracks what is left; the deployed state is
[`PRODUCTION-DEPLOYMENT-STATEMENT.md`](PRODUCTION-DEPLOYMENT-STATEMENT.md).

## Now

1. **Competency review is the hard blocker.** 25 of 222 contracts are reviewed;
   197 baseline contracts await subject-matter review. Work the
   [review queue](COMPETENCY-REVIEW-QUEUE.md) in track-sized batches.
2. **Capstone Builder (6.1).** The planner, saved plans, approval gate, API,
   `/capstone-builder` editor, and Markdown/PDF exports exist; publication to a
   course and LMS packaging remain.
3. **OpenGRC first slice.** Define the evidence export schema, map one track or
   capstone to a small control set, and add the boundary test that proves zero
   learner rows leave the platform.
4. **Cyber DNA decisions.** Confirm whether `advanced_dna_insights_enabled`
   stays on in production while the Career Atlas review is unsigned, and record
   which strand is the new pathway.
5. **Rotate the remaining static lab flags.** 111 labs still publish their graded
   value in `lab.yaml` and the compose file; see
   [flag exposure](FLAG-EXPOSURE.md). Start with the graded, high-stakes labs.
6. **Licensing and legal readiness.** No licence change until the upstream author
   gives written permission ([request draft](UPSTREAM-LICENSE-PERMISSION-REQUEST.md));
   work the [legal readiness](LEGAL-READINESS.md) checklist before pilots.

Blocked: HA witness/collector install and live failover drills (host access);
`opencyberrange-ha` runtime workflow (GitHub billing); SFIA 9 mapping
(commercial/academic licence).

## 5.58.0

- **Per-session flags for baked labs:** coverage is 112 of 222, up from 70.
- **`LAB_FLAG` for runtime labs:** the four OT PLC servers and the OSINT canary
  read it at startup with a static fallback.
- **Digest-pinned lab images:** 225 upstream references in 218 Dockerfiles.
- **Instructor reporting:** course lab friction CSV and Canvas, Brightspace,
  Moodle, and generic gradebook exports.

---

**Historical records.** The sections below describe earlier waves and keep
their original counts.

## 5.56.1

- **Generated records:** refreshed the competency review queue, lab outcomes,
  and NICE v2.2.0 provisional mappings for all 218 labs.
- **NICE reference:** the mapping matrix now cites the NIST CPRT catalogue and
  records the v2.2.0 snapshot and review date.
- **Tests:** the catalogue-size and pending-review assertions now cover 218
  labs and 193 pending reviews.

## 5.56.0

- **Researcher self-audit lab.** `osint-1-4-researcher-self-audit` is a safe,
  offline mirror of a fictional researcher's search footprint, breach record,
  photo metadata, and stale forum trail. Learners write a finding, action,
  owner, and verification step, then recover the flag from the review ticket
  source.
- **Workbook integration:** OSINT Foundations now has six exercises, the chapter
  review includes the self-audit, and the chapter links the University of
  Toronto OSINT self-audit guide as additional reading.
- **Content counts:** 218 lab definitions, 207 workbook-mapped labs, 171 public
  exercises, and 218 tester manifests/contracts.

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
