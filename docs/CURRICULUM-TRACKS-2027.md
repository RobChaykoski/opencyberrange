# 2027 curriculum tracks: IAM, vulnerability management, SOC, platform engineering

Status: **scaffolded** (19 November 2026). The track and chapter structure is
in `curriculum-manifest.yaml`; the lab directories and runnable targets are the
next build phase. The tracks are marked `planned` so they do not appear as
completed curriculum.

This page is the build contract for the next four tracks. It also defines the
content lifecycle so the catalogue does not decay after launch.

## Why these tracks

Exploitation labs alone do not show whether a learner can operate, defend, or
maintain a real environment. These four tracks cover the work employers keep
asking for:

| Track | Work | Primary tools |
|---|---|---|
| Identity and Access Management | Authentication, federation, lifecycle, access review | Active Directory, Entra ID concepts, Keycloak, Authentik, OpenIAM, SAML, OIDC, MFA |
| Vulnerability Management | Asset inventory, scanning, risk, remediation | OpenVAS/Greenbone, Nessus concepts, CVSS, EPSS, KEV, patch baselines |
| Security Operations | Telemetry, detection, triage, hunting | Sysmon, Suricata, Zeek, Wazuh, Security Onion, Sigma |
| Platform Engineering | Build and operate the delivery platform | Docker, Kubernetes, GitHub Actions, Terraform, Ansible |

## Identity and Access Management (`identity`)

Identity is split into four learning stages with different platforms:

| Stage | Platform | Focus | Career target |
|---|---|---|---|
| Identity Fundamentals | Authentik | Users, groups, MFA, policies, application access | Junior Security Analyst, Helpdesk, System Administrator |
| Enterprise SSO | Authentik | OAuth2, OIDC, SAML, LDAP, federation | IAM Analyst, Identity Engineer |
| Enterprise IAM | Keycloak | Realms, clients, mappers, brokering, architecture | IAM Engineer, Security Architect |
| Identity Governance | OpenIAM | Joiner/mover/leaver, reviews, certification, role mining, SoD | IGA Analyst, Compliance Analyst, Identity Governance Specialist |

The operational target is Authentik for OpenCyberRange, OpenGRC, OpenDLP,
Moodle, and the wiki: LDAP integration, OIDC, MFA, and self-service password
reset. Keycloak is the advanced lab platform, not the default production SSO.
OpenIAM is the governance layer. See
[ADR 0006](decisions/0006-identity-platform-roles.md).

Existing chapter: `IAM01` Identity and Access Foundations. Planned sequence:

- `IAM02` Active Directory and Kerberos
- `IAM03` Entra ID and Hybrid Identity
- `IAM04` Keycloak and OIDC
- `IAM05` Authentik and MFA
- `IAM06` Federation: SAML and OIDC
- `IAM07` Access Review and Joiner/Mover/Leaver
- `IAM08` OpenIAM Identity Governance
- `IAM09` IAM Capstone

NICE v2.2.0 alignment: `PD-WRL-001`, `IO-WRL-005`, `IO-WRL-006`,
`DD-WRL-001`.

OpenIAM is the governance and administration anchor. The chapter follows the
official documentation: a proof-of-concept deployment, an Active Directory or
LDAP connector, identity correlation, role and entitlement design, provisioning,
access certification, and separation of duties.

## Vulnerability Management (`vm`)

- `VM01` Asset Inventory and Exposure
- `VM02` Authenticated Scanning with OpenVAS
- `VM03` Nessus Concepts and Web Scanning with Nikto and OWASP ZAP
- `VM04` Risk Scoring and Prioritisation
- `VM05` Patch Validation
- `VM06` Exceptions and Remediation Workflow
- `VM07` Host Hardening with Lynis
- `VM08` Vulnerability Management Capstone

NICE v2.2.0 alignment: `PD-WRL-007`, `PD-WRL-004`, `IO-WRL-006`,
`PD-WRL-001`.

Nessus stays conceptual and comparison-based unless the institution supplies a
licence. OpenVAS/Greenbone is the runnable scanner. Nikto covers web-server
scanning and finding triage. OWASP ZAP covers baseline and authenticated web
scans, alert triage, and evidence suitable for a remediation ticket. Lynis
covers host hardening and audit evidence.
Risk scoring uses CVSS plus EPSS and CISA KEV, but the lab asks for an owner, a
business context, and a decision, not a bare score.

## Security Operations (`soc`)

- `SOC01` Telemetry Foundations
- `SOC02` Network Detection with Suricata
- `SOC03` Network Metadata and Hunting with Zeek
- `SOC04` Endpoint and Vulnerability Detection with Wazuh
- `SOC05` Alert Triage and Case Management
- `SOC06` Detection as Code
- `SOC07` Host Defense with Fail2Ban
- `SOC08` Security Onion Capstone

NICE v2.2.0 alignment: `PD-WRL-001`, `PD-WRL-003`, `PD-WRL-006`,
`PD-WRL-002`.

Security Onion is the heaviest target. Keep it as an optional capstone profile
so a small host can still run the earlier chapters. Wazuh covers agent
enrolment, decoders and rules, vulnerability detection, file-integrity
monitoring, and active response.

## Platform Engineering (`platform`)

- `PLAT01` Docker and Container Security
- `PLAT02` Kubernetes Fundamentals and Hardening
- `PLAT03` CI/CD with GitHub Actions, GitLab, SonarQube, and Dependency-Check
- `PLAT04` Terraform and Infrastructure as Code
- `PLAT05` Ansible and Configuration Management
- `PLAT06` Cilium eBPF Networking, Security, and Hubble
- `PLAT07` Calico Network Policy and eBPF
- `PLAT08` Istio Service Mesh
- `PLAT09` Platform Engineering Capstone

NICE v2.2.0 alignment: `DD-WRL-003`, `DD-WRL-004`, `DD-WRL-005`,
`IO-WRL-005`, `DD-WRL-001`.

GitHub Actions labs use a local workflow fixture and a fake registry; they do
not require a live GitHub organisation. GitLab CI labs use a self-hosted GitLab
container and a Docker runner, installed with the official Docker instructions.
SonarQube is used as a quality gate: project onboarding, scanner configuration,
coverage import, and a reviewed quality profile. OWASP Dependency-Check covers
software composition analysis, suppression files, and a fail-build policy for
known vulnerable dependencies. ScanCode Toolkit covers licence and component
scanning for the SBOM and third-party notices. Kubernetes labs use a single-node
cluster with a strict resource budget. Cilium is used for eBPF network policy,
service identity, flow observability, and the Hubble UI. Calico is used for
network policy, IPAM, and the eBPF dataplane comparison, not as a second CNI at
the same time. Istio is used for service-to-service mTLS, authorization policy,
traffic shifting, and mesh observability.

## Network Engineering and Infrastructure (`neteng`)

- `NENG01` Network Source of Truth with NetBox
- `NENG02` Monitoring with LibreNMS
- `NENG03` Configuration Backup with Oxidized
- `NENG04` Firewall and Segmentation with OPNsense/pfSense
- `NENG05` NAC and Zero Trust with PacketFence
- `NENG06` Identity Integration with OpenIAM
- `NENG07` Network Automation with NAPALM
- `NENG08` Open vSwitch and Mininet Virtual Networks
- `NENG09` Network Engineering Capstone

NICE v2.2.0 alignment: `IO-WRL-004`, `IO-WRL-005`, `PD-WRL-004`,
`PD-WRL-001`, `DD-WRL-001`.

NetBox is the source of truth: sites, racks, devices, interfaces, prefixes, IP
addresses, VLANs, and API automation. LibreNMS covers SNMP polling and alerting.
Oxidized covers configuration backup, diffs, and drift evidence. NAPALM covers
multi-vendor configuration retrieval, state validation, and controlled change.
Open vSwitch covers virtual switching, VLANs, tunnels, and flow inspection.
Mininet covers reproducible virtual topologies, links, controllers, and SDN
experiments. OPNsense and pfSense cover firewall policy, NAT, VPN, and
segmentation.
PacketFence covers NAC, onboarding, device registration, and zero-trust access
decisions. The OpenIAM chapter connects identity lifecycle and access review to
network and application access.

## NICE mapping rule

Every new lab must select, at authoring time:

- at least one NICE work role;
- at least one task;
- at least one knowledge or skill statement;
- the framework version used for the selection.

The authoring dropdown reads the installed NICE v2.2.0 components. The backend
stores component codes, not free text, and validates them again on save. A
framework refresh updates statement text while preserving the codes and the lab
mapping.

SFIA, ECSF, and CISA are the next mapping layer. Do not add free-text framework
names to a lab; add a validated component set when those catalogs are ingested.
SFIA 9 follows the licensing and review plan in
[SFIA 9 ingestion](SFIA-9-INGESTION.md).

## Content lifecycle

Every lab carries an owner, a content version, a last-reviewed date, a
next-review date, and a lifecycle status.

| Status | Meaning |
|---|---|
| `draft` | Authored but not learner-visible |
| `active` | Current and supported |
| `review_due` | Past the quarterly review date; still visible |
| `deprecated` | Superseded or unsafe; visible only with a warning or hidden |
| `archived` | Removed from the active catalogue; retained for evidence |

Cadence:

- **Quarterly**: review screenshots, links, vulnerable software, flags, and
  workbook answers. Update `reviewed_at` and advance `review_due`.
- **Annual**: refresh the target image, dependencies, and lab narrative. Bump
  `content_version`.
- **Deprecation**: record the reason, the replacement lab, and the last supported
  date. Keep the lab definition in the repository for audit, but remove it from
  the active catalogue.
- **Archive**: move the track or lab to `platform/labs/_archive/` with a
  `DEPRECATED.md` note. Never silently delete learner evidence.

Suggested fields for the lab header:

```yaml
lifecycle:
  status: active
  owner: "OpenCyberRange Curriculum"
  reviewed_at: "2026-11-19"
  review_due: "2027-02-19"
  next_refresh: "2027-11-19"
  supersedes: null
  superseded_by: null
  archive_reason: null
```

## Build order

1. NICE ingestion and authoring dropdown (foundation).
2. IAM chapter `IAM04` Keycloak/OIDC and `IAM05` Authentik/MFA.
3. IAM `IAM06` federation and `IAM08` OpenIAM governance.
4. VM `VM01`/`VM02` inventory and OpenVAS.
5. SOC `SOC01`/`SOC02` telemetry and Suricata.
6. Platform `PLAT01`/`PLAT03` Docker and Actions.
7. Remaining chapters, then capstones.

Each lab is done only when it has a runnable target, a workbook, a test step,
at least one NICE work role/task/KSK mapping, and a review date.
