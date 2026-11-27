# Framework Alignment

Generated from `curriculum-frameworks.yaml`. Do not edit this page by hand.

Framework mapping is **selective**. Each exercise resolves to:

- **one primary competency**;
- **one or two framework references** that actually govern the work;
- **one measurable outcome**.

An explicit value in a lab's `lab.yaml` overrides the chapter default. Lab-level overrides are listed below.

## Framework registry

| ID | Framework | Version | Purpose | Used? |
|---|---|---|---|---|
| `NICE` | NICE Workforce Framework for Cybersecurity | NIST SP 800-181 Rev. 1 | Cybersecurity roles and work tasks | Yes |
| `NIST_CSF` | NIST Cybersecurity Framework 2.0 | 2.0 | General cyber capability and risk management | Yes |
| `NIST_SSDF` | NIST Secure Software Development Framework | SP 800-218 | Secure development practices | Yes |
| `CWE` | Common Weakness Enumeration | Current CWE list | Software weakness classification | Yes |
| `OWASP_TOP10` | OWASP Top 10 | Current web risk categories | Web risk categories | Yes |
| `OWASP_ASVS` | OWASP Application Security Verification Standard | Current ASVS | Web verification requirements | Yes |
| `NIST_AI_RMF` | NIST AI Risk Management Framework | AI RMF 1.0 | AI risk management | Yes |
| `OWASP_LLM` | OWASP Top 10 for LLM Applications | Current LLM Top 10 | AI application risks | Yes |
| `MITRE_ATTACK` | MITRE ATT&CK | Current enterprise matrix | Adversary behaviour | Yes |
| `MITRE_ATLAS` | MITRE ATLAS | Current ATLAS matrix | AI adversary behaviour | Yes |
| `NIST_800_82` | NIST SP 800-82 Rev. 3 | Rev. 3 | OT/ICS security practices | Yes |
| `IEC_62443` | IEC 62443 | Current industrial automation and control systems series | OT/ICS security practices | Yes |
| `CYCLONEDX` | CycloneDX | Current specification | SBOM formats | Not yet |
| `SPDX` | SPDX | Current specification | SBOM formats | Not yet |

Frameworks registered but not mapped yet are shown as **Not yet**. They remain in the registry so future SBOM or supply-chain exercises can use them without inventing a local variant.

## Primary competencies

| ID | Competency | Description |
|---|---|---|
| `network_systems` | Network Systems | Network foundations, service discovery, traffic, and protocol behaviour. |
| `identity_access` | Identity and Access | Authentication, credentials, sessions, accounts, and access boundaries. |
| `web_api` | Web and API Security | Web reconnaissance, request handling, injection, and application verification. |
| `incident_forensics` | Incident Forensics | Logs, packet captures, memory evidence, timelines, and defensive explanation. |
| `malware` | Malware Analysis | Static and dynamic analysis of malicious files and command-and-control traffic. |
| `osint` | Open-Source Intelligence | Public-source collection, metadata, provenance, and responsible reporting. |
| `ot_ics` | OT/ICS Security | Industrial protocols, control-system assets, and operational risk. |
| `ai_security` | AI Security | Prompt injection, model policy, AI application risk, and AI adversary behaviour. |
| `secure_development` | Secure Development | Code review, weakness classification, secure design, and remediation. |
| `digital_safety` | Digital Safety | Account safety, privacy, link and file checks, and responsible reporting. |
| `system_administration` | System Administration | Terminal use, files, permissions, processes, and safe local system practice. |

## Chapter alignment

| Chapter | Display name | Track | Primary competency | Framework references |
|---|---|---|---|---|
| `WIN01` | Enumeration | Windows Penetration Testing | `network_systems` | `NICE` (NICE Workforce Framework for Cybersecurity), `MITRE_ATTACK` (MITRE ATT&CK) |
| `WIN02` | SMB Reconnaissance | Windows Penetration Testing | `network_systems` | `NICE` (NICE Workforce Framework for Cybersecurity), `MITRE_ATTACK` (MITRE ATT&CK) |
| `WIN03` | SMB Credential Attacks | Windows Penetration Testing | `identity_access` | `NICE` (NICE Workforce Framework for Cybersecurity), `CWE` (Common Weakness Enumeration) |
| `WIN04` | RDP Exploitation | Windows Penetration Testing | `identity_access` | `NICE` (NICE Workforce Framework for Cybersecurity), `MITRE_ATTACK` (MITRE ATT&CK) |
| `WIN05` | WinRM Exploitation | Windows Penetration Testing | `identity_access` | `NICE` (NICE Workforce Framework for Cybersecurity), `MITRE_ATTACK` (MITRE ATT&CK) |
| `WIN06` | MSSQL Exploitation | Windows Penetration Testing | `network_systems` | `NICE` (NICE Workforce Framework for Cybersecurity), `CWE` (Common Weakness Enumeration) |
| `WIN07` | LDAP Enumeration | Windows Penetration Testing | `identity_access` | `NICE` (NICE Workforce Framework for Cybersecurity), `CWE` (Common Weakness Enumeration) |
| `WIN08` | Credential Reuse and Lateral Movement | Windows Penetration Testing | `identity_access` | `NICE` (NICE Workforce Framework for Cybersecurity), `MITRE_ATTACK` (MITRE ATT&CK) |
| `WIN09` | Complete Network Assessment | Windows Penetration Testing | `network_systems` | `NICE` (NICE Workforce Framework for Cybersecurity), `MITRE_ATTACK` (MITRE ATT&CK) |
| `WIN10` | Active Directory and Authentication | Windows Penetration Testing | `identity_access` | `NICE` (NICE Workforce Framework for Cybersecurity), `MITRE_ATTACK` (MITRE ATT&CK) |
| `WIN11` | Active Directory Attack Pathway | Windows Penetration Testing | `identity_access` | `NICE` (NICE Workforce Framework for Cybersecurity), `MITRE_ATTACK` (MITRE ATT&CK) |
| `LIN01` | Linux Service Enumeration | Linux Fundamentals | `network_systems` | `NICE` (NICE Workforce Framework for Cybersecurity), `MITRE_ATTACK` (MITRE ATT&CK) |
| `LIN01B` | Network Discovery | Linux Fundamentals | `network_systems` | `NICE` (NICE Workforce Framework for Cybersecurity), `MITRE_ATTACK` (MITRE ATT&CK) |
| `LIN02` | SSH Authentication and Discovery | Linux Fundamentals | `identity_access` | `NICE` (NICE Workforce Framework for Cybersecurity), `CWE` (Common Weakness Enumeration) |
| `LIN02B` | SMB and SNMP Enumeration | Linux Fundamentals | `network_systems` | `NICE` (NICE Workforce Framework for Cybersecurity), `CWE` (Common Weakness Enumeration) |
| `LIN03` | SSH Post-Exploitation and Privilege Escalation | Linux Fundamentals | `system_administration` | `NICE` (NICE Workforce Framework for Cybersecurity), `MITRE_ATTACK` (MITRE ATT&CK) |
| `LIN03B` | Privilege Escalation and Password Hashes | Linux Fundamentals | `identity_access` | `NICE` (NICE Workforce Framework for Cybersecurity), `CWE` (Common Weakness Enumeration) |
| `LIN04` | Lateral Movement | Linux Fundamentals | `network_systems` | `NICE` (NICE Workforce Framework for Cybersecurity), `MITRE_ATTACK` (MITRE ATT&CK) |
| `LIN05` | Detection and Response | Linux Fundamentals | `incident_forensics` | `NICE` (NICE Workforce Framework for Cybersecurity), `NIST_CSF` (NIST Cybersecurity Framework 2.0) |
| `LIN09` | Capstone Assessments | Linux Fundamentals | `incident_forensics` | `NICE` (NICE Workforce Framework for Cybersecurity), `NIST_CSF` (NIST Cybersecurity Framework 2.0) |
| `MSF01` | Metasploit Framework Fundamentals | Metasploit Operations | `network_systems` | `NICE` (NICE Workforce Framework for Cybersecurity), `MITRE_ATTACK` (MITRE ATT&CK) |
| `MSF02` | Exploitation and Post-Exploitation | Metasploit Operations | `network_systems` | `NICE` (NICE Workforce Framework for Cybersecurity), `MITRE_ATTACK` (MITRE ATT&CK) |
| `NET00` | Network Foundations | Network Security | `network_systems` | `NICE` (NICE Workforce Framework for Cybersecurity), `NIST_CSF` (NIST Cybersecurity Framework 2.0) |
| `NET01` | Log Analysis | Network Security | `incident_forensics` | `NICE` (NICE Workforce Framework for Cybersecurity), `NIST_CSF` (NIST Cybersecurity Framework 2.0) |
| `NET01B` | Traffic and Log Correlation | Network Security | `incident_forensics` | `NICE` (NICE Workforce Framework for Cybersecurity), `NIST_CSF` (NIST Cybersecurity Framework 2.0) |
| `NET02` | PCAP Forensics | Network Security | `incident_forensics` | `NICE` (NICE Workforce Framework for Cybersecurity), `NIST_CSF` (NIST Cybersecurity Framework 2.0) |
| `NET03` | Firewalls and Network Policy | Network Security | `network_systems` | `NICE` (NICE Workforce Framework for Cybersecurity), `NIST_CSF` (NIST Cybersecurity Framework 2.0) |
| `NET04` | Device Topology and Routed Paths | Network Security | `network_systems` | `NICE` (NICE Workforce Framework for Cybersecurity), `NIST_CSF` (NIST Cybersecurity Framework 2.0) |
| `WEB01` | Web Reconnaissance | Web Application Security | `web_api` | `OWASP_TOP10` (OWASP Top 10), `OWASP_ASVS` (OWASP Application Security Verification Standard) |
| `WEB01B` | Advanced Recon and Traversal | Web Application Security | `web_api` | `OWASP_TOP10` (OWASP Top 10), `OWASP_ASVS` (OWASP Application Security Verification Standard) |
| `WEB02` | SQL Injection and Web Exploitation | Web Application Security | `web_api` | `OWASP_TOP10` (OWASP Top 10), `CWE` (Common Weakness Enumeration) |
| `WEB02B` | API and Injection | Web Application Security | `web_api` | `OWASP_TOP10` (OWASP Top 10), `OWASP_ASVS` (OWASP Application Security Verification Standard) |
| `WEB03` | Advanced Web Exploitation | Web Application Security | `web_api` | `OWASP_TOP10` (OWASP Top 10), `OWASP_ASVS` (OWASP Application Security Verification Standard) |
| `WEB11` | Modern Application Security | Web Application Security | `web_api` | `OWASP_TOP10` (OWASP Top 10), `OWASP_ASVS` (OWASP Application Security Verification Standard) |
| `MAL01` | Malware Fundamentals | Malware Analysis | `malware` | `NICE` (NICE Workforce Framework for Cybersecurity), `MITRE_ATTACK` (MITRE ATT&CK) |
| `MAL02` | Executable Analysis | Malware Analysis | `malware` | `NICE` (NICE Workforce Framework for Cybersecurity), `MITRE_ATTACK` (MITRE ATT&CK) |
| `MAL03` | Detection and Triage | Malware Analysis | `malware` | `NICE` (NICE Workforce Framework for Cybersecurity), `MITRE_ATTACK` (MITRE ATT&CK) |
| `OT01` | Modbus Fundamentals | OT/ICS Security | `ot_ics` | `NIST_800_82` (NIST SP 800-82 Rev. 3), `IEC_62443` (IEC 62443) |
| `OT02` | S7comm and PLC Data Blocks | OT/ICS Security | `ot_ics` | `NIST_800_82` (NIST SP 800-82 Rev. 3), `IEC_62443` (IEC 62443) |
| `AI01` | AI Security Foundations | AI Hacking | `ai_security` | `NIST_AI_RMF` (NIST AI Risk Management Framework), `OWASP_LLM` (OWASP Top 10 for LLM Applications) |
| `AI02` | Agentic AI Security | AI Hacking | `ai_security` | `NIST_AI_RMF` (NIST AI Risk Management Framework), `OWASP_LLM` (OWASP Top 10 for LLM Applications) |
| `OSINT01` | OSINT Foundations | OSINT | `osint` | `NICE` (NICE Workforce Framework for Cybersecurity), `MITRE_ATTACK` (MITRE ATT&CK) |
| `OSINT02` | Mobile OSINT | OSINT | `osint` | `NICE` (NICE Workforce Framework for Cybersecurity), `MITRE_ATTACK` (MITRE ATT&CK) |
| `OSINT03` | Canary Tokens and Deception | OSINT | `osint` | `NICE` (NICE Workforce Framework for Cybersecurity), `MITRE_ATTACK` (MITRE ATT&CK) |
| `BEG01` | RangeBox Foundations | Beginner Cybersecurity | `system_administration` | `NICE` (NICE Workforce Framework for Cybersecurity), `NIST_CSF` (NIST Cybersecurity Framework 2.0) |
| `BEG02` | Command Line, Files, and Networks | Beginner Cybersecurity | `system_administration` | `NICE` (NICE Workforce Framework for Cybersecurity), `NIST_CSF` (NIST Cybersecurity Framework 2.0) |
| `BEG03` | Defensive Evidence | Beginner Cybersecurity | `incident_forensics` | `NICE` (NICE Workforce Framework for Cybersecurity), `NIST_CSF` (NIST Cybersecurity Framework 2.0) |
| `BEG04` | Applied Challenges | Beginner Cybersecurity | `digital_safety` | `NICE` (NICE Workforce Framework for Cybersecurity), `NIST_CSF` (NIST Cybersecurity Framework 2.0) |
| `SWSEC01` | Software Security Foundations | Software Security | `secure_development` | `NIST_SSDF` (NIST Secure Software Development Framework), `CWE` (Common Weakness Enumeration) |
| `SWSEC02` | API Testing with Karate | Software Security | `secure_development` | `NIST_SSDF` (NIST Secure Software Development Framework), `CWE` (Common Weakness Enumeration) |
| `IAM01` | Identity and Access Foundations | Identity & Access | `identity_access` | `NICE` (NICE Workforce Framework for Cybersecurity), `NIST_CSF` (NIST Cybersecurity Framework 2.0) |
| `IAM02` | Active Directory and Kerberos | Identity & Access | `identity_access` | `NICE` (NICE Workforce Framework for Cybersecurity), `NIST_CSF` (NIST Cybersecurity Framework 2.0) |
| `IAM03` | Entra ID and Hybrid Identity | Identity & Access | `identity_access` | `NICE` (NICE Workforce Framework for Cybersecurity), `NIST_CSF` (NIST Cybersecurity Framework 2.0) |
| `IAM04` | Keycloak and OIDC | Identity & Access | `identity_access` | `NICE` (NICE Workforce Framework for Cybersecurity), `NIST_CSF` (NIST Cybersecurity Framework 2.0) |
| `IAM05` | Authentik and MFA | Identity & Access | `identity_access` | `NICE` (NICE Workforce Framework for Cybersecurity), `NIST_CSF` (NIST Cybersecurity Framework 2.0) |
| `IAM06` | Federation: SAML and OIDC | Identity & Access | `identity_access` | `NICE` (NICE Workforce Framework for Cybersecurity), `NIST_CSF` (NIST Cybersecurity Framework 2.0) |
| `IAM07` | Access Review and Joiner/Mover/Leaver | Identity & Access | `identity_access` | `NICE` (NICE Workforce Framework for Cybersecurity), `NIST_CSF` (NIST Cybersecurity Framework 2.0) |
| `IAM08` | OpenIAM Identity Governance | Identity & Access | `identity_access` | `NICE` (NICE Workforce Framework for Cybersecurity), `NIST_CSF` (NIST Cybersecurity Framework 2.0) |
| `IAM09` | IAM Capstone | Identity & Access | `identity_access` | `NICE` (NICE Workforce Framework for Cybersecurity), `NIST_CSF` (NIST Cybersecurity Framework 2.0) |
| `FOR01` | Memory Forensics | Digital Forensics | `incident_forensics` | `NICE` (NICE Workforce Framework for Cybersecurity), `NIST_CSF` (NIST Cybersecurity Framework 2.0) |
| `FOR02` | Network Forensics | Digital Forensics | `incident_forensics` | `NICE` (NICE Workforce Framework for Cybersecurity), `NIST_CSF` (NIST Cybersecurity Framework 2.0) |
| `FOR03` | Topology Forensics | Digital Forensics | `incident_forensics` | `NICE` (NICE Workforce Framework for Cybersecurity), `NIST_CSF` (NIST Cybersecurity Framework 2.0) |
| `FOR03B` | Live Memory Acquisition | Digital Forensics | `incident_forensics` | `NICE` (NICE Workforce Framework for Cybersecurity), `NIST_CSF` (NIST Cybersecurity Framework 2.0) |
| `VM01` | Asset Inventory and Exposure | Vulnerability Management | `system_administration` | `NICE` (NICE Workforce Framework for Cybersecurity), `NIST_CSF` (NIST Cybersecurity Framework 2.0) |
| `VM02` | Authenticated Scanning with OpenVAS | Vulnerability Management | `system_administration` | `NICE` (NICE Workforce Framework for Cybersecurity), `NIST_CSF` (NIST Cybersecurity Framework 2.0) |
| `VM03` | Nessus Concepts and Web Scanning with Nikto and OWASP ZAP | Vulnerability Management | `system_administration` | `NICE` (NICE Workforce Framework for Cybersecurity), `NIST_CSF` (NIST Cybersecurity Framework 2.0) |
| `VM04` | Risk Scoring and Prioritisation | Vulnerability Management | `system_administration` | `NICE` (NICE Workforce Framework for Cybersecurity), `NIST_CSF` (NIST Cybersecurity Framework 2.0) |
| `VM05` | Patch Validation | Vulnerability Management | `system_administration` | `NICE` (NICE Workforce Framework for Cybersecurity), `NIST_CSF` (NIST Cybersecurity Framework 2.0) |
| `VM06` | Exceptions and Remediation Workflow | Vulnerability Management | `system_administration` | `NICE` (NICE Workforce Framework for Cybersecurity), `NIST_CSF` (NIST Cybersecurity Framework 2.0) |
| `VM07` | Host Hardening with Lynis | Vulnerability Management | `system_administration` | `NICE` (NICE Workforce Framework for Cybersecurity), `NIST_CSF` (NIST Cybersecurity Framework 2.0) |
| `VM08` | Vulnerability Management Capstone | Vulnerability Management | `system_administration` | `NICE` (NICE Workforce Framework for Cybersecurity), `NIST_CSF` (NIST Cybersecurity Framework 2.0) |
| `SOC01` | Telemetry Foundations | Security Operations | `incident_forensics` | `NICE` (NICE Workforce Framework for Cybersecurity), `NIST_CSF` (NIST Cybersecurity Framework 2.0) |
| `SOC02` | Network Detection with Suricata | Security Operations | `incident_forensics` | `NICE` (NICE Workforce Framework for Cybersecurity), `NIST_CSF` (NIST Cybersecurity Framework 2.0) |
| `SOC03` | Network Metadata and Hunting with Zeek | Security Operations | `incident_forensics` | `NICE` (NICE Workforce Framework for Cybersecurity), `NIST_CSF` (NIST Cybersecurity Framework 2.0) |
| `SOC04` | Endpoint and Vulnerability Detection with Wazuh | Security Operations | `incident_forensics` | `NICE` (NICE Workforce Framework for Cybersecurity), `NIST_CSF` (NIST Cybersecurity Framework 2.0) |
| `SOC05` | Alert Triage and Case Management | Security Operations | `incident_forensics` | `NICE` (NICE Workforce Framework for Cybersecurity), `NIST_CSF` (NIST Cybersecurity Framework 2.0) |
| `SOC06` | Detection as Code | Security Operations | `incident_forensics` | `NICE` (NICE Workforce Framework for Cybersecurity), `NIST_CSF` (NIST Cybersecurity Framework 2.0) |
| `SOC07` | Host Defense with Fail2Ban | Security Operations | `incident_forensics` | `NICE` (NICE Workforce Framework for Cybersecurity), `NIST_CSF` (NIST Cybersecurity Framework 2.0) |
| `SOC08` | Security Onion Capstone | Security Operations | `incident_forensics` | `NICE` (NICE Workforce Framework for Cybersecurity), `NIST_CSF` (NIST Cybersecurity Framework 2.0) |
| `PLAT01` | Docker and Container Security | Platform Engineering | `system_administration` | `NICE` (NICE Workforce Framework for Cybersecurity), `NIST_CSF` (NIST Cybersecurity Framework 2.0) |
| `PLAT02` | Kubernetes Fundamentals and Hardening | Platform Engineering | `system_administration` | `NICE` (NICE Workforce Framework for Cybersecurity), `NIST_CSF` (NIST Cybersecurity Framework 2.0) |
| `PLAT03` | CI/CD with GitHub Actions, GitLab, SonarQube, and Dependency-Check | Platform Engineering | `system_administration` | `NICE` (NICE Workforce Framework for Cybersecurity), `NIST_CSF` (NIST Cybersecurity Framework 2.0) |
| `PLAT04` | Terraform and Infrastructure as Code | Platform Engineering | `system_administration` | `NICE` (NICE Workforce Framework for Cybersecurity), `NIST_CSF` (NIST Cybersecurity Framework 2.0) |
| `PLAT05` | Ansible and Configuration Management | Platform Engineering | `system_administration` | `NICE` (NICE Workforce Framework for Cybersecurity), `NIST_CSF` (NIST Cybersecurity Framework 2.0) |
| `PLAT06` | Cilium eBPF Networking, Security, and Hubble | Platform Engineering | `system_administration` | `NICE` (NICE Workforce Framework for Cybersecurity), `NIST_CSF` (NIST Cybersecurity Framework 2.0) |
| `PLAT07` | Calico Network Policy and eBPF | Platform Engineering | `system_administration` | `NICE` (NICE Workforce Framework for Cybersecurity), `NIST_CSF` (NIST Cybersecurity Framework 2.0) |
| `PLAT08` | Istio Service Mesh | Platform Engineering | `system_administration` | `NICE` (NICE Workforce Framework for Cybersecurity), `NIST_CSF` (NIST Cybersecurity Framework 2.0) |
| `PLAT09` | Platform Engineering Capstone | Platform Engineering | `system_administration` | `NICE` (NICE Workforce Framework for Cybersecurity), `NIST_CSF` (NIST Cybersecurity Framework 2.0) |
| `NENG01` | Network Source of Truth with NetBox | Network Engineering and Infrastructure | `network_systems` | `NICE` (NICE Workforce Framework for Cybersecurity), `NIST_CSF` (NIST Cybersecurity Framework 2.0) |
| `NENG02` | Monitoring with LibreNMS | Network Engineering and Infrastructure | `network_systems` | `NICE` (NICE Workforce Framework for Cybersecurity), `NIST_CSF` (NIST Cybersecurity Framework 2.0) |
| `NENG03` | Configuration Backup with Oxidized | Network Engineering and Infrastructure | `network_systems` | `NICE` (NICE Workforce Framework for Cybersecurity), `NIST_CSF` (NIST Cybersecurity Framework 2.0) |
| `NENG04` | Firewall and Segmentation with OPNsense/pfSense | Network Engineering and Infrastructure | `network_systems` | `NICE` (NICE Workforce Framework for Cybersecurity), `NIST_CSF` (NIST Cybersecurity Framework 2.0) |
| `NENG05` | NAC and Zero Trust with PacketFence | Network Engineering and Infrastructure | `network_systems` | `NICE` (NICE Workforce Framework for Cybersecurity), `NIST_CSF` (NIST Cybersecurity Framework 2.0) |
| `NENG06` | Identity Integration with OpenIAM | Network Engineering and Infrastructure | `network_systems` | `NICE` (NICE Workforce Framework for Cybersecurity), `NIST_CSF` (NIST Cybersecurity Framework 2.0) |
| `NENG07` | Network Automation with NAPALM | Network Engineering and Infrastructure | `network_systems` | `NICE` (NICE Workforce Framework for Cybersecurity), `NIST_CSF` (NIST Cybersecurity Framework 2.0) |
| `NENG08` | Open vSwitch and Mininet Virtual Networks | Network Engineering and Infrastructure | `network_systems` | `NICE` (NICE Workforce Framework for Cybersecurity), `NIST_CSF` (NIST Cybersecurity Framework 2.0) |
| `NENG09` | Network Engineering Capstone | Network Engineering and Infrastructure | `network_systems` | `NICE` (NICE Workforce Framework for Cybersecurity), `NIST_CSF` (NIST Cybersecurity Framework 2.0) |

## Lab-level overrides

| Lab slug | Primary competency | Framework references |
|---|---|---|
| `ai-1-3-indirect-prompt-injection` | `—` | `NIST_AI_RMF` (NIST AI Risk Management Framework), `MITRE_ATLAS` (MITRE ATLAS) |
| `software-security-1-1-hidden-export-route` | `—` | `NIST_SSDF` (NIST Secure Software Development Framework), `CWE` (Common Weakness Enumeration) |
| `software-security-2-1-diagnostics-command-injection` | `—` | `NIST_SSDF` (NIST Secure Software Development Framework), `CWE` (Common Weakness Enumeration) |
| `software-security-3-3-authentication-and-reuse` | `identity_access` | `OWASP_ASVS` (OWASP Application Security Verification Standard), `CWE` (Common Weakness Enumeration) |
| `software-security-3-4-negative-tests-and-evidence` | `web_api` | `OWASP_TOP10` (OWASP Top 10), `CWE` (Common Weakness Enumeration) |
| `high-school-9-3-cyberchef-base64-basics` | `digital_safety` | `NICE` (NICE Workforce Framework for Cybersecurity), `NIST_CSF` (NIST Cybersecurity Framework 2.0) |
| `high-school-9-4-cyberchef-caesar-shift` | `digital_safety` | `NICE` (NICE Workforce Framework for Cybersecurity), `NIST_CSF` (NIST Cybersecurity Framework 2.0) |
| `high-school-9-5-cyberchef-layered-message` | `digital_safety` | `NICE` (NICE Workforce Framework for Cybersecurity), `NIST_CSF` (NIST Cybersecurity Framework 2.0) |
| `high-school-9-6-read-the-link` | `digital_safety` | `NICE` (NICE Workforce Framework for Cybersecurity), `NIST_CSF` (NIST Cybersecurity Framework 2.0) |
| `high-school-9-7-know-the-file` | `digital_safety` | `NICE` (NICE Workforce Framework for Cybersecurity), `NIST_CSF` (NIST Cybersecurity Framework 2.0) |
| `high-school-9-8-forwarded-message` | `digital_safety` | `NICE` (NICE Workforce Framework for Cybersecurity), `NIST_CSF` (NIST Cybersecurity Framework 2.0) |
| `high-school-10-1-rangebox-network-basics` | `network_systems` | `NICE` (NICE Workforce Framework for Cybersecurity), `NIST_CSF` (NIST Cybersecurity Framework 2.0) |
| `high-school-10-2-rangebox-browser-and-source` | `web_api` | `NICE` (NICE Workforce Framework for Cybersecurity), `OWASP_TOP10` (OWASP Top 10) |
| `high-school-10-3-email-metadata` | `incident_forensics` | `NICE` (NICE Workforce Framework for Cybersecurity), `NIST_CSF` (NIST Cybersecurity Framework 2.0) |
| `high-school-10-4-mfa-lost-phone` | `identity_access` | `NICE` (NICE Workforce Framework for Cybersecurity), `NIST_CSF` (NIST Cybersecurity Framework 2.0) |
| `high-school-10-5-rangebox-log-review` | `incident_forensics` | `NICE` (NICE Workforce Framework for Cybersecurity), `NIST_CSF` (NIST Cybersecurity Framework 2.0) |
| `high-school-10-6-rangebox-beginner-challenge` | `incident_forensics` | `NICE` (NICE Workforce Framework for Cybersecurity), `NIST_CSF` (NIST Cybersecurity Framework 2.0) |
| `high-school-11-2-media-provenance` | `osint` | `NICE` (NICE Workforce Framework for Cybersecurity), `NIST_CSF` (NIST Cybersecurity Framework 2.0) |
| `high-school-12-1-devfest-community-portal` | `osint` | `NICE` (NICE Workforce Framework for Cybersecurity), `NIST_CSF` (NIST Cybersecurity Framework 2.0) |
| `high-school-12-2-crypto-rug-pull` | `osint` | `NICE` (NICE Workforce Framework for Cybersecurity), `NIST_CSF` (NIST Cybersecurity Framework 2.0) |
| `linux-5-5-capstone-ctf` | `network_systems` | `NICE` (NICE Workforce Framework for Cybersecurity), `MITRE_ATTACK` (MITRE ATT&CK) |
| `linux-5-7-black-box-ctf` | `network_systems` | `NICE` (NICE Workforce Framework for Cybersecurity), `MITRE_ATTACK` (MITRE ATT&CK) |
| `linux-final-1-branch-office-practice` | `network_systems` | `NICE` (NICE Workforce Framework for Cybersecurity), `MITRE_ATTACK` (MITRE ATT&CK) |
| `linux-final-2-clinic-final` | `network_systems` | `NICE` (NICE Workforce Framework for Cybersecurity), `MITRE_ATTACK` (MITRE ATT&CK) |
| `linux-final-3-architecture-mock` | `network_systems` | `NICE` (NICE Workforce Framework for Cybersecurity), `MITRE_ATTACK` (MITRE ATT&CK) |
| `linux-midterm-2-full-penetration-test` | `network_systems` | `NICE` (NICE Workforce Framework for Cybersecurity), `MITRE_ATTACK` (MITRE ATT&CK) |
| `linux-midterm-3-blind-penetration-test` | `network_systems` | `NICE` (NICE Workforce Framework for Cybersecurity), `MITRE_ATTACK` (MITRE ATT&CK) |
| `windows-10-1-network-enumeration-assessment` | `network_systems` | `NICE` (NICE Workforce Framework for Cybersecurity), `MITRE_ATTACK` (MITRE ATT&CK) |
| `windows-10-2-midterm-assessment` | `network_systems` | `NICE` (NICE Workforce Framework for Cybersecurity), `MITRE_ATTACK` (MITRE ATT&CK) |
| `network-2-7-arkime-session-triage` | `network_systems` | `NICE` (NICE Workforce Framework for Cybersecurity), `NIST_CSF` (NIST Cybersecurity Framework 2.0) |
| `ot-3-1-ics-pcap-forensics` | `ot_ics` | `NIST_800_82` (NIST SP 800-82 Rev. 3), `IEC_62443` (IEC 62443) |

## Measurable outcomes

Each lab uses its explicit `measurable_outcome` when present. Otherwise it uses the first learning outcome that is not a flag-submission statement. If neither exists, the generator supplies one observation/interpretation/confidence sentence. The validation script rejects a missing or too-short outcome.

## Validation

```bash
python scripts/validate-framework-map.py
```

The validator checks every lab for exactly one known competency, one or two known framework references, and one measurable outcome.

