# Lab review backlog

Status: **open — Release 6 input**

This page turns the November 2026 curriculum review into tracked work. Each item
is a content fix, a QA rule, or a Release 6 design decision. A row is closed only
after the lab contract, workbook, and QA gate agree.

## Closed in the first batch

| Item | What changed | Evidence |
|---|---|---|
| Flag source of truth | `lab_qa.py` ignores redacted examples, compares every test step to `lab.yaml`, and requires `allow_flag_mismatch: true` for a deliberate decoy or stage marker | `scripts/lab_qa.py`; schema `$defs.step` |
| Metadata contract | Added `competency_tags`, `defensive_skills`, `evidence_required`, `report_questions`, and `learning_concepts` | `platform/backend/lab_metadata.schema.json` |
| Generic and duplicated guidance | `generic-defensive`, `duplicate-defensive`, `generic-skill`, and `missing-evidence` checks; `--strict-content` promotes them to a release gate | `scripts/lab_qa.py` |
| `software-security-1-1-hidden-export-route` | Client-side code is public; no secrets, tokens, privileged routes, or admin logic in the bundle; remove retired routes and test that they stay gone | lab contract and workbook |
| `software-security-2-1-diagnostics-command-injection` | Shell-free invocation, argument arrays, host allowlist, least privilege, metacharacter regression tests; `id` → `ls` → `cat` progression; vulnerable vs secure reflection | lab contract, hints, workbook |
| `high-school-9-3-cyberchef-base64-basics` | Encoding-vs-encryption concept check, data-representation competency, evidence capture | workbook and lab contract |
| `high-school-9-4-cyberchef-caesar-shift` | ROT13 concept check, encoding/obfuscation/encryption comparison table, evidence capture | workbook and lab contract |
| `high-school-9-6-read-the-link` | Phishing and URL-analysis competencies, safe-action concept check, evidence capture | workbook and lab contract |
| `high-school-9-7-know-the-file` | File-type concept check, evidence-over-labels competency, evidence capture | workbook and lab contract |
| `high-school-9-8-forwarded-message` | Two required evidence answers: the userinfo URL trick and the extension/type mismatch | lab contract and workbook |
| `high-school-10-1-rangebox-network-basics` | `nmap` was listed but not used; the defensive takeaway was inherited from another lesson | Added one bounded `nmap -p 8080` observation and replaced the takeaway with response-header and metadata guidance |
| `high-school-10-2-rangebox-browser-and-source` | The defensive takeaway did not match the HTML-comment lesson | Replaced it with source-review guidance and added a “why was the token visible?” concept check |
| `high-school-10-3-email-metadata` | The verdict required a header but not the reasoning; evidence was too coarse | Require both the header and the reason; record SPF, DKIM, DMARC, the Received chain, and the verdict as separate evidence |
| `high-school-10-4-mfa-lost-phone` | Recovery succeeded without comparing the recovery options; the quiz lacked a lost-phone scenario and a passkey question | Added the security-question → recovery-code → secondary-authenticator → hardware-key hierarchy, plus ranking evidence, a lost-phone scenario question, and a passkey phishing-resistance question |
| `high-school-10-5-rangebox-log-review` | Framed as “read a small access log” but the work is a SOC collect/analyze/interpret/document cycle | Added the SOC workflow table, SOC competency tags, evidence for the log inventory, pattern, interpretation, and incident note, and an evidence-based concept check |
| `high-school-11-1-rangebox-log-detective` | The defensive takeaway was inherited and did not match the log lesson; confidence was not explicit | Replaced it with log-as-evidence guidance and added a confidence/alternative-explanation table, SOC competencies, and evidence fields |
| `high-school-11-2-media-provenance` | Rated `beginner` while requiring corroboration, metadata limits, and uncertainty; the assessment only asked what the evidence did not prove | Raised to `intermediate` and require one supported and one unsupported statement, with evidence and confidence |
| `high-school-12-1-devfest-community-portal` | The defensive takeaway did not match the metadata lesson; the Grade 12 path was heavily guided | Replaced it with file-publication guidance and added an optional PNG/PDF/document metadata comparison that asks which artifact leaks the most context |
| `osint-1-2-image-intelligence` | Rated `beginner` while requiring metadata, file signatures, PNG structure, steganography, and an extractor; defensive guidance was generic | Raised to `intermediate`, added the publication-sanitisation takeaway, and required metadata/signature/extraction evidence |
| `osint-1-3-exif-metadata` | Difficulty is appropriately `beginner`, but the defensive guidance was generic and the quiz tested definitions rather than situations | Replaced it with GPS/timestamp/device/author review and sanitized-copy guidance; added a field-trip scenario question and an observation-vs-interpretation question |
| `osint-1-4-researcher-self-audit` | Findings had no risk rating, the ticket promised a verification date but did not show one, search results were too clean, and exposure was not scored | Added Low/Medium/High ratings, the +2/+3/+3/+4 exposure score, owner/due/verified columns, and a false lead plus a cached duplicate in the search results |
| `osint-2-1-source-code-intelligence` | The defensive takeaway described public metadata, not client-side source review | Replaced it with the “all client-side code is public” rule, static-asset review, and secret-removal guidance |
| `osint-2-2-public-homepage` | Overlapped earlier “view source, find a comment” labs; the lesson was not clearly metadata enumeration | Added author/generator/keywords/Open Graph/Twitter/custom metadata, a metadata inventory, and “which field is most useful?” analysis |
| `osint-2-4-public-profile` | The workflow was “open profile, read About, copy marker” with almost no correlation or reasoning | Added visible vs less-obvious fields, a conference page that repeats the handle and travel window, an exposure map, and a correlation question |
| `osint-2-5-public-banner` | The lab found the banner and flag but did not analyse the exposed product version | Added a product/version table, a version-risk question, the version-as-lead caveat, and an observation-vs-interpretation check |
| `identity-1-1-secure-authentication` | The session comparison showed `staff:staff` and `admin:admin` but did not ask which design choices were actually broken | Added a four-problem comparison (client-side role, no server lookup, predictable structure, no integrity validation) and a “all of them” concept check |
| `identity-1-2-oauth-oidc-sso` | Token validation stopped at audience; ID-token claims were not taught | Added `iss`, `aud`, `exp`, `iat`, `nonce`, and `sub` guidance, a validation table, and an `aud` concept check |
| `identity-1-3-nhi-oauth-abuse` | Rotation was mentioned but not turned into an incident-response lifecycle | Added revoke → replace → automatic rotation → log review → scope reduction, plus a “revoke first” concept check |
| `identity-2-1-identity-lifecycle` | The title said joiners, movers, and leavers, but the exercise only tested a leaver | Added a mover account (`priya`) with stale `finance:read`, a mover checklist, and a mover concept check |
| `ot-1-1-modbus-register-analysis` | The defensive takeaway was shorter than the modern OT practice it teaches | Expanded it to segmentation, TCP 502 restriction, jump hosts, OT firewalls, register monitoring, asset inventory, and no direct enterprise exposure |
| Platform-wide | Lab compose files lack healthchecks and port validation | Add a shared healthcheck pattern and a QA gate; track as Release 6 infrastructure work |
| Security audit | Docker, IDOR, SSO, async, flag races, and the Celebration Wall were reviewed | Recorded in `docs/security/ATTACK-SURFACE-AUDIT.md`; added Celebration Wall toggle/minor tests and a residual-risk list |
| Per-session flags | Static labs embed the shared `FLAG`; `seeded_flag_hash` is not set by the static launch path | **Release blocker** for certificate integrity; implement the launcher change and a per-session render step |
| Upstream image pinning | 227 upstream `FROM`/`image:` references use tags, not `@sha256:` digests | **Release blocker** for supply-chain drift; pin the common bases, then run `scripts/check-image-pins.py --strict` in CI |
| Scaling roadmap | Single-host today; worker queue, microVMs, registry, and external audit sink are future work | `docs/architecture/SCALING-ROADMAP.md` |
| Startup friction | Browser RangeBox is the zero-config path; WireGuard is advanced. Progress is polled; warm pools are not implemented | Add SSE progress, health-gated Open Lab, and warm pools for the introductory labs |
| Hint and reset UX | Hints unlock on a timer and the workbook opens beside RangeBox; a learner-facing target reset is not consistently exposed | Add tiered cost-weighted hints, a split-pane workspace, and a target-only reset |
| `high-school-12-2-crypto-rug-pull` | `difficulty: beginner` conflicted with the evidence text; the assessment named red flags but not the strongest supporting evidence | Raised to `intermediate` and require the strongest-evidence statement, with ledger and fraud competencies |
| `high-school-9-1-rangebox-first-steps` | Inherited takeaway; the first terminal session had no evidence record | Replaced it with scoped-command and command-note guidance; added orientation evidence |
| `high-school-9-2-rangebox-file-hunt` | Inherited takeaway; file triage was not formalised | Replaced it with filename-as-label guidance and added file-inventory and evidence-path requirements |

## Open lab findings

| Lab | Finding | Next action |
|---|---|---|
| `web-1-1-basic-directory-enumeration` | Generic defensive takeaway; `web_api` is too broad; assessment rewards the flag only | Write enumeration-specific guidance, add `competency_tags`, require a directory inventory and risk ranking |
| `web-1-2-technology-identification` | `X-Framework: WordPress` is artificial; guidance and competency are generic | Use realistic WordPress indicators (`wp-content`, generator meta, `X-Powered-By`, `Server`); update the test and workbook |
| `web-1-3-http-methods-enumeration` | The flag rewards PUT exploitation, not enumeration; the lab mixes recon with exploitation | Move the flag to the enumeration result; create a separate HTTP method-abuse lab |
| `web-1-4-header-analysis` | `X-Debug-Mode` is unrealistic; HSTS is discussed on an HTTP target; guidance is generic | Use realistic banner and error-page disclosure; clarify that HSTS is a TLS-layer control; move the HSTS exercise to a TLS lab |
| `web-1-5-subdomain-discovery` | The title promises DNS subdomain discovery, but the lab sweeps a subnet with no DNS | Rename to **Host and Service Discovery**; add the DNS/certificate-transparency note; write asset-inventory guidance |
| `web-1-6-comprehensive-web-reconnaissance` | `T1190` describes exploitation, not reconnaissance; guidance is generic | Map to reconnaissance (for example `T1595`); add asset-inventory guidance and a required recon report |
| 24 Web labs | The same defensive sentence is copied across the track | Replace with lab-specific controls; then enable `--strict-content` |
| 2 High School labs (`9-1`, `9-2`) | Still use the inherited “verify with a trusted adult” takeaway | Write a takeaway for each lesson |
| Reviewed labs | Concept checks live only in workbook prose | Add 5–6 question banks under each lab's `quiz.yaml` and link the evidence to `competency_tags` |
| Onboarding | Only a flag marks the first terminal success | Add `First Terminal Command`, `The First Step`, and `Pathfinder I` achievement definitions |
| `high-school-10-1-rangebox-network-basics` | The title says “Network Basics” but the lab is mostly HTTP response and metadata analysis | Deferred: the title is acceptable as a Grade 10 networking introduction; revisit only if the track adds a separate HTTP-analysis lab |

## Release 6 design items

| Item | Why it matters |
|---|---|
| Cyber Foundations competency cluster | The Grade 9 CyberChef, link, file, and capstone labs form a progression: representation → URL analysis → file evidence → decision |
| Evidence-first capstone | Store the two evidence answers as `evidence_required` records, not only workbook text |
| Data-literacy cluster | Base64, ROT13, percent-encoding, and metadata are one skill family across APIs, logs, malware, and network analysis |
| HTTP method-abuse lab | Keep enumeration and exploitation as separate learning boundaries |
| Achievement milestones | Recognise the first command, first safe decision, and first evidence submission, not only flags |

## Recurring theme: don’t trust the claim, investigate the evidence

The reviewed labs keep returning to the same habit. It is becoming the
curriculum’s differentiator, not a single lab’s lesson.

| Lab | The claim | The evidence habit |
|---|---|---|
| `high-school-10-1` / `10-3` | The message says who sent it | Read the headers: authentication results, return path, routing |
| `high-school-10-5` / `11-1` | Something looks suspicious | Separate observation from interpretation; state confidence |
| `high-school-11-2` | The image looks real | Check source, metadata, and independent corroboration |
| `high-school-12-2` | The token promises returns | Follow the liquidity, not the marketing |
| `software-security-1-1` | The route is hidden in the bundle | Client-side code is public; enforce authorization on the server |
| `high-school-9-7` | The file is a PNG | Check the magic bytes, not the extension |

Keep this theme explicit in new labs: name the claim, name the evidence, and
state what the evidence does not prove.

## Review rule

A lab is not complete when the flag works. It is complete when:

1. the lab contract states the concept, the competency, and the evidence;
2. the workbook teaches the concept and asks the learner to explain it;
3. the assessment rewards the concept, not only the flag;
4. the QA gate rejects placeholder flags, copied guidance, and missing evidence.
