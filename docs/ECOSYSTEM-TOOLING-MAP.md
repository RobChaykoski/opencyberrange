# Ecosystem tooling map

This page places the shared security, identity, network, platform, and privacy
tools in the project that should own them. It is deliberately a map, not a
mandate: a tool can appear in more than one project when the projects use it for
different jobs.

## Training lab stack

The dev-only training stack lives in `deploy/ecosystem-test/` and is documented
in `docs/TRAINING-ECOSYSTEM.md`. It runs Moodle, Authentik, NetBox, Ralph, and
Fleet with synthetic data so capstones can be exercised across realistic tools.
It is never deployed to production and never receives production credentials or
records. OpenIAM is fetched separately as its own compose stack.

## Project roles

| Project | Primary job | What it should own |
|---|---|---|
| **OpenCyberRange (OCR)** | Teaching and workforce development | Lab tracks, NICE mapping, readiness evidence, instructor workflows, learner-facing practice |
| **OpenGRC** | Governance, risk, and compliance | Control catalogue, framework mapping, evidence requests, audits, exceptions, training-to-control links |
| **OpenDetectionEngine / OpenDLP** | Data discovery, classification, and protection | Data sources, classifiers, DLP policy, discovery evidence, classification reports |
| **DefectDojo** | Vulnerability and finding management | Finding ingestion, cross-scanner deduplication, exploitability ranking, SLA and remediation tracking |
| **Steampipe / Powerpipe** | Read-only cloud and SaaS inventory | Scheduled SQL collection, benchmark results, configuration evidence snapshots |
| **Cloud Custodian** | Cloud guardrails and remediation | Policy-as-code filters/actions, lab-account TTL, tag enforcement, public-exposure remediation, dry-run evidence |
| **Sigstore / Cosign** | Supply-chain trust | Keyless artifact signing, provenance attestations, transparency-log evidence, release verification |
| **OpenMetadata** | Metadata authority | Classification, ownership, lineage, jurisdiction, retention, controls, policy context |
| **OPA** | Policy decision engine | Versioned policy bundles, allow/deny/mask/approval decisions, decision audit records |
| **OpenEMR / DRButler** | Clinical operations | PHI protection, identity, endpoint compliance, vendor risk, HIPAA evidence, clinician workflow |
| **Ralph** | Asset inventory | Asset ownership, lifecycle, network/device inventory |
| **Fleet** | Endpoint management | Device posture, OS/package state, endpoint compliance evidence |
| **Velociraptor** | Endpoint DFIR and hunting | VQL hunts, artifact collection, offline collectors, timeline evidence, scoped response |

## Tool map

| Capability | Tools | OCR | OpenGRC | OpenDetectionEngine | OpenEMR |
|---|---|---|---|---|---|
| Identity and SSO | Authentik, Keycloak, OpenIAM | Authentik for operational SSO; Keycloak and OpenIAM as IAM labs | Authentik SSO; OpenIAM access reviews and certification evidence | Authentik SSO; OpenIAM role/lifecycle evidence | Authentik SSO; OpenIAM access reviews for clinical roles |
| Network source of truth | NetBox | NENG01 lab; topology/inventory exercises | Asset and control scope references | Data-source network context | Clinical network and device inventory reference |
| Network monitoring | LibreNMS | NENG02 lab | Availability control evidence | Sensor/source health | Clinical network availability evidence |
| Config backup/drift | Oxidized, NAPALM | NENG03/NENG07 labs | Change-management evidence | Collector configuration evidence | Network device change evidence |
| Firewall/segmentation | OPNsense, pfSense | NENG04 lab | Network control evidence | Sensor segmentation evidence | Clinical segmentation and PHI boundary evidence |
| NAC / zero trust | PacketFence | NENG05 lab | Access-control evidence | Sensor/collector onboarding | Clinical device onboarding and access evidence |
| Virtual switching | Open vSwitch, Mininet | NENG08 lab | Lab/reference topology only | Test topology only | Test topology only |
| Endpoint detection | Wazuh, Sysmon, Fail2Ban, Lynis | SOC01/SOC04/SOC07 labs | Endpoint control evidence | Collector host hardening | Clinical endpoint compliance |
| Network detection | Suricata, Zeek, Security Onion | SOC02/SOC03/SOC08 labs | Detection-control evidence | Sensor detection evidence | Clinical network monitoring evidence |
| Web/VM scanning | OpenVAS, Nessus, Nikto, OWASP ZAP | VM02/VM03/VM05 labs | Vulnerability-management control evidence | Web service exposure evidence | Clinical web app vulnerability evidence |
| Asset ownership | Ralph, NetBox | Asset ownership report | Asset/control scope | Data-source ownership | Clinical asset ownership |
| Endpoint compliance | Fleet | Endpoint compliance report | Control evidence | Collector posture | Clinical device posture |
| Containers/Kubernetes | Docker, Kubernetes, Cilium, Calico, Istio | PLAT01/PLAT02/PLAT06/PLAT07/PLAT08 labs | SDLC and platform control evidence | Collector deployment | Clinical service platform evidence |
| CI/CD and code quality | GitHub Actions, GitLab CI, SonarQube, OWASP Dependency-Check, ScanCode | PLAT03 lab | Build/release control evidence | Build pipeline evidence | Build pipeline and vendor evidence |
| Data classification/DLP | OpenDLP, OpenMetadata | Privacy labels and export classification | Privacy/control evidence | Core classification and DLP | PHI classification and DLP evidence |
| Vulnerability management | DefectDojo, OpenVAS, Trivy, Grype | Vulnerability labs and remediation exercises | Risk, control, and SLA evidence | Scanner findings and exposure context | Clinical application and vendor vulnerability evidence |
| Cloud/SaaS configuration evidence | Steampipe, Powerpipe | Cloud and SaaS security labs | Benchmark and control evidence snapshots | Cloud data-source and exposure context | Cloud-hosted PHI configuration evidence |
| Endpoint DFIR and hunting | Velociraptor, Wazuh, Fleet | DFIR labs, VQL hunts, artifact collection | Forensic evidence and control testing | Endpoint evidence for data exposure | Clinical endpoint DFIR |
| Cloud guardrails and remediation | Cloud Custodian, OPA | Cloud lab guardrails, TTL, and cleanup | Cloud control evidence and exceptions | Cloud data-source protection context | Cloud-hosted PHI guardrails |
| Supply-chain trust | Sigstore, Cosign, Syft | Release signing and verification labs | Build and release control evidence | Collector and policy-bundle verification | Vendor artifact and image verification |
| Metadata and policy context | OpenMetadata, OPA, Authentik | Learner and lab metadata context | Decision evidence and policy version | Classification and policy context | PHI policy context and access decisions |
| Privacy and reporting | Shared role model | Privacy office and auditor dashboards | Evidence requests and audit packs | Classification and discovery reports | PHI access and retention evidence |

## Enforcement boundaries

The tools overlap in vocabulary but not in authority. Keep these boundaries
explicit so a query tool never becomes an enforcement engine and a policy engine
never becomes a scanner.

| Layer | Tools | Allowed role | Not allowed |
|---|---|---|---|
| Observe | Steampipe, Powerpipe, OpenMetadata, Ralph, NetBox, Fleet, Wazuh, Velociraptor, OpenDLP | Scheduled read-only collection and evidence snapshots | Synchronous request-path dependency or system of record |
| Decide | OPA, Authentik, OpenCyberRange context service | Application and data authorization, identity, policy decisions | Mutating cloud resources |
| Enforce cloud | Cloud Custodian | Scoped remediation in lab or sandbox accounts after dry-run and approval | Production remediation without approval, change window, and audit record |
| Track findings | DefectDojo | Deduplicate, rank, assign, SLA, retest | Owning control, risk, or exception decisions |
| Govern | OpenGRC | Controls, risks, evidence requests, exceptions, audits | Running scanners or storing raw secrets |
| Trust | Sigstore, Cosign | Sign and verify artifacts, provenance, and transparency-log entries | Replacing access control or runtime authorization |
| Train | OpenCyberRange | Labs, readiness evidence, instructor workflows | Production data or real credentials |

### Data flow

```text
Steampipe / Powerpipe ─┐
OpenDLP / OpenMetadata ─┼─> DefectDojo ──> OpenGRC
Cloud Custodian ────────┘        │
                                 └─> remediation, retest, SLA evidence

OpenMetadata ──> context service ──> OPA ──> OCR / OpenGRC / OpenDLP
Sigstore ──────> verify release artifacts, SBOMs, and policy bundles
```

### Rules

1. **Steampipe is read-only.** It observes cloud and SaaS APIs; it never becomes
   the system of record or an inline dependency.
2. **Cloud Custodian is the only tool allowed to mutate cloud resources.** Run
   `--dry-run` first, scope credentials to a lab or sandbox account, require an
   approval for any non-dry-run action, and record the policy version, target,
   before/after state, actor, and evidence hash.
3. **OPA decides application and data actions.** It does not remediate cloud
   resources; Cloud Custodian does not authorize learner exports.
4. **DefectDojo tracks findings.** OpenGRC consumes the aggregate evidence and
   owns the risk, control, exception, and audit decision.
5. **Sigstore is a release gate.** Verify signatures and provenance before a
   deploy or a policy-bundle load, not on every learner request.
6. **No synchronous collector calls in the request path.** Materialize evidence
   on a schedule and serve the last reviewed snapshot.
7. **Every automated action is attributable.** Actor, policy version, target,
   before/after, approval, and evidence hash are mandatory.

## Identity architecture

```text
                    OpenIAM
             (identity governance)

                         |
                         v

                   Authentik
              (primary identity)

        /          |          |          \
   OpenCyberRange  OpenGRC  OpenDetection  OpenEMR

                         |
                         v

                     Keycloak
           (advanced federation lab)
```

Authentik is the operational SSO platform. Keycloak is an advanced lab and
reference environment. OpenIAM owns lifecycle, provisioning, access review,
certification, and segregation of duties.

## Shared reporting model

All four projects should use the same boundaries:

- **Privacy office** sees aggregate inventory, consent, retention, erasure,
  minor safeguards, processor inventory, and classification evidence.
- **Auditor** sees evidence-bound manifests, access reviews, change ledgers,
  control coverage, and exceptions.
- **Mentor** sees assigned learners only: progress, readiness, context, actions,
  outcomes, and follow-ups.
- **Teaching assistant** sees assigned-course lab health, stuck learners, hint
  and attempt patterns, and delegated feedback queues.
- **Administrator** sees platform health, backups, security events, tenant
  isolation, and access inventory.

No report should make a grade, admission, employment, or disciplinary decision.
Use small-cell suppression, purpose-bound access, export labels, and access
audit events.

## Shared visual and design rules

- Summary first, detail on request.
- One primary action per view.
- Use the project's component system; do not import a foreign CSS framework into
  a Laravel/Filament, Django, or PHP application just for visual parity.
- Share tokens and guidance, not a single implementation.
- Accessible by keyboard, screen reader, colour independence, and small screens.
- Exports carry purpose, owner, audience, retention, and classification.
- Privacy and audit views are quiet, dense, and evidence-led, not marketing
  dashboards.

## Adoption order

1. Shared identity: Authentik for SSO, then OpenIAM for access reviews.
2. Shared evidence vocabulary: NICE mappings in OCR, control IDs in OpenGRC,
   classification labels in OpenDLP, PHI categories in OpenEMR.
3. Shared reporting boundaries: privacy, auditor, mentor, teaching assistant,
   administrator.
4. Shared CI gates: SonarQube, Dependency-Check, ScanCode, signed artifacts.
5. Shared network/asset context: NetBox to Ralph, LibreNMS/Oxidized/NAPALM for
   operational evidence, Fleet for endpoint posture.
