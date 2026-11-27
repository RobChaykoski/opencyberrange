# Scaling and hardening roadmap

Status: **planning — single-host today, multi-node later**

The current release is a single-host Community/Academic deployment: Nginx,
Vue, FastAPI, PostgreSQL, Docker, and WireGuard on one machine. That is the right
shape for a classroom or a small institution. The items below are ordered by
what protects the current deployment first, then what unlocks multi-node scale.

## Target-scale assumption

| Scale | Shape | Priority |
|---|---|---|
| One classroom / small institution | Single host, 30–60 concurrent labs | Harden the current host |
| Department or multi-course | 2–4 lab worker nodes, shared control plane | Decouple orchestration |
| Institution or consortium | Worker pool, external audit sink, registry cache | Full multi-node |

Do not start with multi-node. The single-host risks are cheaper to close and
they remain risks in every later shape.

## Phase 1: close single-host integrity and supply-chain gaps

These are release blockers, not future architecture.

| Item | Why it comes first | Action |
|---|---|---|
| Per-session flags | 112 of 222 labs rotate: 75 env-driven plus 37 Dockerfile-baked through the render wrapper | Roll the render contract through the remaining 110 baked labs |
| Upstream image pinning | Moving tags cause build rot and unexpected CVEs | Pin `ubuntu`, `python`, `alpine`, `debian`, and Kali bases by `@sha256:`. Add `scripts/check-image-pins.py --strict` to CI after the pin pass. |
| Off-host integrity evidence | A database superuser can disable triggers | Keep the signed manifest, ledger archive, and WAL/backups off-host. A restore is not trusted until it matches the off-host manifest. |
| Lab schema gate | Missing limits, privileged flags, or inconsistent metadata | Keep `validate_lab_metadata.py`, `validate-lab.py`, and `lab_qa.py --static` mandatory in CI. Add image-pin and per-session-flag checks. |
| Resource defaults | A runaway lab can starve the host | Keep the launcher's default `mem_limit`, `cpus`, `pids_limit`, and `cap_drop`. Fix the helper so a `deploy` block without `resources.limits` still gets defaults. |

## Phase 2: decouple orchestration from the control plane

**Trigger:** one host can no longer hold a full class, or lab spawn latency
affects the web tier.

**Shape:**

```text
Nginx -> FastAPI (stateless web/API)
             |
             +-- PostgreSQL (state, ledger)
             +-- Redis (queue, short-lived state)
             |
             +-- Lab worker agent 1  (Docker + WireGuard + /24 pool)
             +-- Lab worker agent 2
             +-- Lab worker agent N
```

**Rules:**

- FastAPI never talks to a remote Docker socket directly; it submits a signed
  job to a worker.
- Each worker owns a disjoint `/24` pool and its own WireGuard peers.
- The worker reports health, capacity, and the lab session id; the control plane
  records the assignment.
- A lost worker is drained, not failed over mid-session. Lab sessions are
  ephemeral; the learner restarts on another worker.
- Keep the current single-host launcher as the first worker implementation so
  the API contract is tested before a second node exists.

## Phase 3: harden the lab runtime

**Trigger:** the catalogue includes kernel, network, or offensive labs that
should not share the host kernel.

| Option | Use |
|---|---|
| gVisor (`runsc`) | Drop-in runtime for high-risk user-space labs; lower operational change than a microVM |
| Kata Containers | Stronger isolation with a lightweight VM per pod/container |
| Firecracker | Custom microVM orchestration; highest engineering cost |

Start with a reviewed allowlist: run the highest-risk labs under `runsc` first,
keep the rest on runc, and record the runtime in the lab contract so the choice
is auditable.

## Phase 4: externalise audit and telemetry

- Stream ledger events and security events to an append-only external sink
  (WORM S3, Loki, or a SIEM). The on-host ledger stays the fast local check; the
  external stream is the evidence of record.
- Replace polling for lab provisioning and container health with SSE. A single
  SSE endpoint per learner is cheaper than a room full of 2-second polls.
- Keep the Celebration Wall on a short cache; it does not need real-time push.

## Phase 5: registry and lab supply chain

- Mirror base and prebuilt lab images into Harbor or Zot.
- Scan on push with Trivy/Grype and generate CycloneDX SBOMs.
- Pin by digest in the mirror, not only in the Dockerfile.
- Keep `supply-chain.lock.json` as the reviewed set; a digest change requires a
  rebuild and a lab harness run.

## Experience backlog (post-release)

These are learner- and instructor-facing improvements that do not change the
trust boundary. They are grouped so the next release can pick a theme instead of
a long flat list.

| Theme | Current state | Next step |
|---|---|---|
| Lab metadata and workbook rhythm | All 222 labs now carry the five metadata fields; `validate_lab_metadata.py` and `validate-lab.py` pass | Standardise every workbook to Scenario → Objectives → Environment → Guided tasks → Flag → Remediation |
| Lab smoke tests | `lab_qa.py --static` and `lab_harness.py` cover workbook accuracy and live startup/solve/teardown | Run the harness nightly on a canary set and publish the result |
| Right-size the runtime | RangeBox is a full desktop; browser tools cover many labs | Tag CLI-only labs for a fast web terminal and reserve the full desktop for tools that need it |
| Error and expiry states | Generic errors still exist; expiry is a background cleanup | Plain-English recovery actions, 10/2-minute warnings, and “Extend session” |
| Copy and interpolation | Some IPs and commands are copyable | Interpolate target IP/host/port from the active session; add copy buttons everywhere |
| Command palette and onboarding | Sidebar navigation and a first-run tour exist | Add `Ctrl/Cmd+K` and a 3-step first-lab tour |
| Cyber DNA explainability | Every dimension returns evidence and a next step | Surface the evidence in a tooltip on the radar and a cold-start baseline |
| Cyber GPS action cards | GPS returns directions and next steps | Turn the top three into launch cards with minutes, points, and trait impact |
| Celebration Wall polish | Milestone-driven, no free text, opt-out filters | Add batching, privacy preview, and cohort/certificate/first-blood filter pills |
| Certificate and VPN UX | Certificate verification and VPN config exist | Add a QR code, last-handshake status, and key regeneration |
| Instructor reports | Live sessions and analytics exist; `scripts/lab_friction_report.py` ranks completion, failed-flag, and hint rates | Add the in-UI live matrix and LMS CSV export |
| Learner benchmarks and transcript | Cohort aggregates and profile exports exist | Add opt-in anonymised percentile/velocity context and a competency transcript with MITRE tags and DNA scores |
| Admin ledger viewer | Integrity summary and chain checks exist | Add actor badges, JSON diffs, and a live “verify chain” banner |
| Import and erasure previews | Suppression ledger and restore checks exist | Add dry-run summaries before bulk import or erasure |

## Student-experience polish

| Moment | Current state | Next step |
|---|---|---|
| Lab kickoff | Lab cards show title, difficulty, and time; prerequisites are in the contract | Surface “What you’ll need”, tool list, and the recommended prior lab before launch |
| Environment cheat sheet | Target IPs and credentials live in the briefing and workbook | Pin attacker IP, target IPs, credentials, and the session countdown in the workspace |
| Terminal paste | Browser terminal supports keyboard paste | Add a “Paste to terminal” button and a first-launch shortcut hint |
| Wrong-flag feedback | The API returns a generic incorrect message | Add gentle checks for common mistakes: command output, trailing space, missing `OCR{}` |
| Flag capture | Achievement and completion feedback exists | Add a short visual pulse and an optional sound toggle |
| Auto-save | Workbook answers and notes are saved on submit | Save checkboxes and scratchpad notes continuously so a refresh or sleep does not lose work |
| Resume | Dashboard shows current work | Make “Resume active lab” or “Next recommended step” the first hero card |
| Catalog search | Tracks and exercises are browsable | Add status, difficulty, time-under-20, tool, and trait filters |
| Mobile companion | Mobile shell and workbook reading work | Optimise workbook reading, progress, due dates, and the wall for phones |
| Interview bridge | Labs have defensive takeaways | Add a two-sentence “How to talk about this in an interview” per lab |
| Point breakdown | The 250-point score exists | Show base, speed/accuracy bonus, hint deduction, and the resulting trait impact |

## Operations telemetry backlog

| Metric | Current state | Next step |
|---|---|---|
| Peak concurrency and `/24` pool use | Live sessions and the allocator expose current state | Record a time series and alert at 80% pool use |
| Time-to-ready (P50/P95) | `LabSession` has start and status timestamps; the harness measures some runs | Add per-lab boot histograms and flag the slowest images for pre-warm |
| Security and governance summary | Security events, the ledger, erasure, break-glass, and SSO events are recorded | Generate a monthly/quarterly report: unattributed SQL, export justifications, erasure, failed break-glass/SSO spikes |
| Failed launch reasons | Admin health and logs record failures | Group failures by reason (pool full, image missing, health timeout) and show the top causes |

## Privacy officer reporting backlog

The platform already records the raw evidence: DSAR exports, erasure
suppression, operator export reasons, consent, retention, and the integrity
ledger. The next step is to package it as six exportable reports. Start with
DSAR, erasure, and administrative-access reports.

| Report | Existing evidence | Next step |
|---|---|---|
| DSAR / access and portability | Self-service and admin exports, profile, completions, DNA, certificates | Add a JSON/CSV/PDF package with a secret-exclusion statement and a 30-day SLA tracker |
| Erasure and backup-resurrection suppression | Erasure hooks, suppression ledger, restore checks | Add a per-account certificate of erasure and a suppression-ledger verification |
| Administrative access and PII disclosure | Export reasons, security events, audit log, ledger | Add a report of exports/views with justification, actor, IP, request id, and unattributed SQL |
| Record of processing and data minimisation | Data dictionary, consent registry, integrations | Add a RoPA/data-residency manifest and consent/opt-out counts |
| Profiling and algorithmic transparency | Skill DNA/GPS formulas, formula versions, no social metrics | Add a plain-language disclosure that traits are telemetry-based and human-reviewed |
| Retention, purge, and breach readiness | Retention jobs, integrity script, backup policy | Add purge counts, legal holds, and an integrity/breach-scope summary for the 72-hour clock |

## Compliance export packs (post-release)

| Pack | Existing evidence | Next step |
|---|---|---|
| Privacy pack | DSAR, erasure suppression, PII access log, RoPA data, integrity chain | Build the six reports in the privacy backlog as one exportable pack |
| Academic integrity pack | Attempt timeline, dynamic-flag hash, hint unlocks, overrides, ledger | Add a per-student grade-dispute export and a cohort collusion/anomaly summary |
| Security and AUP pack | SBOM, supply-chain lock, image scans, firewall checks, MFA/SSO, AUP acceptance | Bundle the evidence and add an AUP/acceptable-use acceptance ledger |
| Accessibility and accommodation log | Accessibility test kit, accommodation overrides, extended time | Add a VPAT/ACR link and an accommodation audit export |

## Emerging technology watch

These are evaluated, not adopted. Each has a clear trigger.

| Technology | Use | Trigger |
|---|---|---|
| gVisor / Firecracker / Kata | Per-lab kernel isolation for high-risk exploit labs | A lab needs kernel or network behaviour that runc cannot safely share |
| eBPF (Cilium Tetragon) | Behavioural auto-grading and ATT&CK timelines from process/file/network events | Flag-only grading is insufficient for defensive labs |
| WebTransport (HTTP/3/QUIC) | Lower-latency RangeBox terminal and desktop streams on lossy campus Wi-Fi | WebSocket head-of-line blocking becomes a support issue |
| Open Badges 3.0 / W3C VC | Exportable, offline-verifiable credentials | Institutions ask for wallet or CLR-compatible badges |
| Local SLM + MCP | Self-hosted Socratic tutor with read-only workbook/hint tools | Data residency rules block external model APIs |
| Passkeys / WebAuthn / CAEP | Phishing-resistant login and continuous session evaluation | Privileged MFA and shared-credential risk become the priority |

## Non-goals and anti-patterns

These are deliberate product constraints, not missing features.

| Not doing | Why |
|---|---|
| Unmoderated public chat or open social feeds | Flag leaks, spoilers, spam, and constant moderation cost. The Celebration Wall stays milestone-driven with structured reactions. |
| Global all-time speedrun or first-blood leaderboard | Rewards the top fraction and automated submissions, demotivates the class. Use short, cohort-scoped events if a board is needed. |
| Hard trait decay or complex spaced repetition | Watching a skill score fall after a break creates anxiety. Use bounded recency weighting and forward progress. |
| User-hosted unstructured write-ups | Leaked flags, stale commands, broken images, and moderation load. Keep curated walkthroughs and remediation cards. |
| Full GUI desktop by default | A full VM costs 3–5× the RAM/CPU and lags on campus Wi-Fi. Default to a web terminal; use the desktop only for tools that need it. |

## What not to do yet

- Do not split PostgreSQL from the control plane before the worker queue exists;
  it adds latency without removing the host bottleneck.
- Do not move to Kubernetes to solve a single-host classroom problem. The
  compose launcher and a worker agent are enough until the lab count and
  concurrency justify it.
- Do not treat a shared static flag as certificate evidence. Fix that first.
