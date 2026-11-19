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
| **OpenEMR / DRButler** | Clinical operations | PHI protection, identity, endpoint compliance, vendor risk, HIPAA evidence, clinician workflow |
| **Ralph** | Asset inventory | Asset ownership, lifecycle, network/device inventory |
| **Fleet** | Endpoint management | Device posture, OS/package state, endpoint compliance evidence |

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
| Data classification/DLP | OpenDLP | Privacy labels and export classification | Privacy/control evidence | Core classification and DLP | PHI classification and DLP evidence |
| Privacy and reporting | Shared role model | Privacy office and auditor dashboards | Evidence requests and audit packs | Classification and discovery reports | PHI access and retention evidence |

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
