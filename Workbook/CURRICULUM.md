# Curriculum Map

Generated from `curriculum-manifest.yaml`. Do not edit this page by hand.
Directory names are stable; display IDs are the labels used in chapter
titles, navigation, prerequisite blocks, PDFs, analytics, and reports.

Exercise counts are labs that expose a workbook page. The platform also
contains labs without a workbook page; see [Workbook coverage](COVERAGE.md).

Framework alignment is selective. See [Framework alignment](FRAMEWORKS.md).

## Track overview

| Track ID | Display name | Audience | Difficulty | Prerequisites | Exercises | Duration | Required environment | Recommended next | Role alignment | Status |
|---|---|---|---|---|---:|---|---|---|---|---|
| `high-school` | Beginner Cybersecurity | Grades 9-12 learners with everyday computer experience and no assumed cybersecurity background. | beginner | None | 18 | 7h 00m | RangeBox with browser, terminal, and beginner lab targets | `netfor` | Entry-level Cyber Defense Analyst; IT Support; SOC Analyst (entry) | published |
| `netfor` | Network Security | Beginner-to-intermediate learners who need network foundations, log analysis, and packet evidence. | beginner | BEG04 | 22 | 19h 45m | RangeBox with terminal, browser, and network lab targets | `webpt` | Network Defender; SOC Analyst; Network Engineer | published |
| `webpt` | Web Application Security | Intermediate learners who can use a terminal and understand HTTP basics. | intermediate | NET00, NET01 | 16 | 21h 35m | RangeBox with browser, terminal, and web lab targets | `software-security` | Application Security Tester; Penetration Tester; Secure Developer | published |
| `software-security` | Software Security | Intermediate learners who can read code and understand web requests. | intermediate | WEB02 | 2 | 30m | RangeBox with browser and software-security lab targets | `malware` | Secure Developer; Application Security Engineer; Penetration Tester | published |
| `malware` | Malware Analysis | Intermediate learners with networking and forensic evidence experience. | intermediate | NET02, FOR01 | 10 | 7h 25m | RangeBox with terminal and isolated malware-analysis targets | `forensics` | Malware Analyst; Incident Responder; Threat Intelligence Analyst | published |
| `forensics` | Digital Forensics | Intermediate learners who want to investigate memory, disk, endpoint, email, browser, and network evidence. | intermediate | NET02 | 4 | 2h 35m | RangeBox with forensic evidence images, PCAPs, and the synthetic DFIR evidence pack | `osint` | Digital Forensics Examiner; Incident Responder; Threat Intelligence Analyst | published |
| `osint` | OSINT | Adult learners who want public-source investigation skills; Grades 9-12 are not assigned the live extensions. | beginner | NET00 | 9 | 4h 50m | Browser and RangeBox; offline mirrors, with optional read-only adult extensions | `identity` | OSINT Analyst; Threat Intelligence Analyst; Investigator | published |
| `identity` | Identity & Access | Intermediate learners interested in authentication, federation, and account lifecycle. | intermediate | NET00 | 39 | 75h 10m | RangeBox with browser and identity lab targets; Keycloak, Authentik, and OpenIAM containers or VMs | `forensics` | IAM Analyst; SOC Analyst; Identity Engineer | published |
| `ot` | OT/ICS Security | Intermediate learners interested in industrial control systems and Modbus. | intermediate | NET00 | 4 | 3h 00m | RangeBox with terminal and Modbus lab target | `ai` | OT Security Analyst; ICS Engineer; SOC Analyst | published |
| `ai` | AI Hacking | Intermediate learners exploring prompt injection, policy bypass, and AI-assisted security. | intermediate | WEB02 | 5 | 4h 15m | RangeBox with browser and mock AI lab target | `winpt` | AI Security Analyst; Red Team Operator; Secure AI Developer | published |
| `winpt` | Windows Penetration Testing | Intermediate learners who have completed the beginner pathway or have equivalent terminal and networking experience. | intermediate | BEG04, NET00 | 53 | 103h 15m | RangeBox with terminal, browser, and Windows lab targets | `linpt` | Penetration Tester; Red Team Operator; SOC Analyst | published |
| `linpt` | Linux Fundamentals | Intermediate learners building Linux enumeration, SSH access, privilege escalation, and detection skills. | intermediate | WIN09 | 30 | 38h 45m | RangeBox with terminal and Linux lab targets | `webpt` | Penetration Tester; Linux Administrator; Incident Responder | published |
| `msfpt` | Metasploit Operations | Learners who have completed the beginner pathway or have equivalent Linux and network service experience. | intermediate | LIN01, NET00 | 8 | 13h 15m | RangeBox with terminal, Kali tools, and a KVM-capable isolated Metasploitable 2 target | `soc` | Penetration Tester; Red Team Operator; SOC Analyst | published |
| `vm` | Vulnerability Management | Learners moving from exploitation into defensive exposure management, asset ownership, and remediation. | intermediate | BEG04, NET00 | 33 | 68h 00m | RangeBox with Linux and Windows targets, OpenVAS/Greenbone, and a synthetic asset inventory | `soc` | Vulnerability Management Analyst; Security Analyst; Risk Analyst; Patch Manager | planned |
| `soc` | Security Operations | Learners who want hands-on detection, triage, hunting, and case management with open-source telemetry. | intermediate | NET02, FOR01 | 34 | 70h 00m | RangeBox with Sysmon, Suricata, Zeek, and Wazuh; Security Onion as an optional heavy profile | `forensics` | SOC Analyst; Detection Engineer; Incident Responder; Threat Hunter | planned |
| `platform` | Platform Engineering | Learners who build and operate the delivery platform: containers, Kubernetes, CI/CD, infrastructure as code, and configuration management. | intermediate | LIN01, NET00 | 40 | 82h 00m | RangeBox with Docker, a local Kubernetes cluster, GitHub Actions workflow fixtures, Terraform, and Ansible | `soc` | Platform Engineer; DevSecOps Engineer; Cloud Security Engineer; Site Reliability Engineer | planned |
| `neteng` | Network Engineering and Infrastructure | Learners moving from packet-level analysis into network source of truth, monitoring, configuration control, segmentation, and network access control. | intermediate | NET00 | 35 | 72h 00m | RangeBox with NetBox, LibreNMS, Oxidized, OPNsense or pfSense, PacketFence, Open vSwitch, Mininet, and a small segmented network | `platform` | Network Engineer; Network Operations Specialist; Infrastructure Engineer; NOC Analyst | planned |

## Chapter map

| Chapter | Display name | Directory | Difficulty | Prerequisites | Exercises | Duration | Recommended next | Status |
|---|---|---|---|---|---:|---|---|---|
| `BEG01` | RangeBox Foundations | `CH_HS09_Grade_9_RangeBox_Basics` | beginner | None | 8 | 2h 40m | `BEG02` | published |
| `BEG02` | Command Line, Files, and Networks | `CH_HS10_Grade_10_RangeBox_Basics` | beginner | BEG01 | 6 | 2h 25m | `BEG03` | published |
| `BEG03` | Defensive Evidence | `CH_HS11_Grade_11_Defensive_Security` | beginner | BEG02 | 2 | 55m | `BEG04` | published |
| `BEG04` | Applied Challenges | `CH_HS12_Grade_12_Applied_Cybersecurity` | beginner | BEG03 | 2 | 1h 00m | `NET00` | published |
| `NET00` | Network Foundations | `CH_N0_Network_Foundations` | beginner | None | 3 | 1h 15m | `NET01` | published |
| `NET01` | Log Analysis | `CH_NET01_Log_Analysis` | beginner | NET00 | 4 | 3h 00m | `NET01B` | published |
| `NET01B` | Traffic and Log Correlation | `CH_NET01B_Traffic_And_Logs` | beginner | NET01 | 2 | 2h 00m | `NET02` | published |
| `NET02` | PCAP Forensics | `CH_NET02_PCAP_Forensics` | intermediate | NET01B | 6 | 6h 30m | `NET03` | published |
| `NET03` | Firewalls and Network Policy | `CH_NETSY12_Firewalls` | intermediate | NET02 | 2 | 2h 15m | `NET04` | published |
| `NET04` | Device Topology and Routed Paths | `CH_NET12_Device_Topology` | intermediate | NET03 | 5 | 4h 45m | `WEB01` | published |
| `WEB01` | Web Reconnaissance | `CH_WEB01_Web_Reconnaissance` | beginner | NET00 | 6 | 12h 00m | `WEB01B` | published |
| `WEB01B` | Advanced Recon and Traversal | `CH_WEB01B_Advanced_Recon` | intermediate | WEB01 | 2 | 1h 15m | `WEB02` | published |
| `WEB02` | SQL Injection and Web Exploitation | `CH_WEB02_Web_Exploitation` | intermediate | WEB01B | 1 | 2h 00m | `WEB02B` | published |
| `WEB02B` | API and Injection | `CH_WEB02B_API_And_Injection` | intermediate | WEB02 | 4 | 2h 50m | `WEB03` | published |
| `WEB03` | Advanced Web Exploitation | `CH_WEB03_Advanced_Exploitation` | intermediate | WEB02B | 3 | 3h 30m | `SWSEC01` | published |
| `SWSEC01` | Software Security Foundations | `CH_SWSEC_Software_Security` | intermediate | WEB02 | 2 | 30m | `MAL01` | published |
| `MAL01` | Malware Fundamentals | `CH_MAL01_Malware_Fundamentals` | intermediate | NET02 | 7 | 5h 25m | `MAL02` | published |
| `MAL02` | Executable Analysis | `CH_MAL02_Executable_Analysis` | intermediate | MAL01 | 1 | 50m | `MAL03` | published |
| `MAL03` | Detection and Triage | `CH_MAL03_Detection_And_Triage` | beginner | MAL02 | 2 | 1h 10m | `FOR01` | published |
| `FOR01` | Memory Forensics | `CH_FOR01_Memory_Forensics` | intermediate | NET02 | 1 | 50m | `FOR02` | published |
| `FOR02` | Network Forensics | `CH_FOR02_Network_Forensics` | intermediate | FOR01 | 1 | 45m | `FOR03` | published |
| `FOR03` | Topology Forensics | `CH_FOR03_Topology_Forensics` | intermediate | FOR02 | 2 | 1h 00m | `OSINT01` | published |
| `OSINT01` | OSINT Foundations | `CH_OSINT01_OSINT_Foundations` | beginner | NET00 | 5 | 2h 55m | `IAM01` | published |
| `OSINT02` | Mobile OSINT | `CH_OSINT02_Mobile_OSINT` | beginner | OSINT01 | 3 | 1h 10m | `OSINT03` | published |
| `OSINT03` | Canary Tokens and Deception | `CH_OSINT03_Canary_And_Deception` | intermediate | OSINT02 | 1 | 45m | `IAM01` | published |
| `IAM01` | Identity and Access Foundations | `CH_IAM01_Identity_And_Access` | intermediate | NET00 | 4 | 3h 10m | `IAM02` | published |
| `IAM02` | Active Directory and Kerberos | `CH_IAM02_Active_Directory_Kerberos` | intermediate | IAM01 | 6 | 12h 00m | `IAM03` | planned |
| `IAM03` | Entra ID and Hybrid Identity | `CH_IAM03_Entra_ID_Hybrid` | intermediate | IAM02 | 4 | 8h 00m | `IAM04` | planned |
| `IAM04` | Keycloak and OIDC | `CH_IAM04_Keycloak_OIDC` | intermediate | IAM02 | 5 | 10h 00m | `IAM05` | planned |
| `IAM05` | Authentik and MFA | `CH_IAM05_Authentik_MFA` | intermediate | IAM04 | 4 | 8h 00m | `IAM06` | planned |
| `IAM06` | Federation: SAML and OIDC | `CH_IAM06_Federation_SAML_OIDC` | advanced | IAM04, IAM05 | 6 | 12h 00m | `IAM07` | planned |
| `IAM07` | Access Review and Joiner/Mover/Leaver | `CH_IAM07_Access_Review_JML` | intermediate | IAM02 | 4 | 8h 00m | `IAM08` | planned |
| `IAM08` | OpenIAM Identity Governance | `CH_IAM08_OpenIAM_Governance` | advanced | IAM07 | 4 | 8h 00m | `IAM09` | planned |
| `IAM09` | IAM Capstone | `CH_IAM09_IAM_Capstone` | advanced | IAM03, IAM06, IAM08 | 2 | 6h 00m | `FOR01` | planned |
| `OT01` | Modbus Fundamentals | `CH_OT01_Modbus_Fundamentals` | intermediate | NET00 | 3 | 2h 15m | `OT02` | published |
| `OT02` | S7comm and PLC Data Blocks | `CH_OT02_S7comm_Data_Blocks` | intermediate | OT01 | 1 | 45m | `AI01` | published |
| `AI01` | AI Security Foundations | `CH_AI01_AI_Foundations` | intermediate | WEB02 | 3 | 1h 50m | `AI02` | published |
| `AI02` | Agentic AI Security | `CH_AI02_Agentic_AI_Security` | intermediate | AI01, WEB02 | 2 | 2h 25m | `WIN01` | published |
| `WIN01` | Enumeration | `CH01_Enumeration` | beginner | None | 5 | 10h 00m | `WIN02` | published |
| `WIN02` | SMB Reconnaissance | `CH02_SMB_Reconnaissance` | beginner | WIN01 | 8 | 16h 00m | `WIN03` | published |
| `WIN03` | SMB Credential Attacks | `CH03_SMB_Credential_Attacks` | intermediate | WIN02 | 5 | 10h 00m | `WIN04` | published |
| `WIN04` | RDP Exploitation | `CH04_RDP_Exploitation` | intermediate | WIN03 | 6 | 12h 00m | `WIN05` | published |
| `WIN05` | WinRM Exploitation | `CH05_WinRM_Exploitation` | intermediate | WIN04 | 6 | 12h 00m | `WIN06` | published |
| `WIN06` | MSSQL Exploitation | `CH06_MSSQL_Exploitation` | intermediate | WIN05 | 7 | 14h 00m | `WIN07` | published |
| `WIN07` | LDAP Enumeration | `CH07_LDAP_Enumeration` | intermediate | WIN06 | 6 | 12h 00m | `WIN08` | published |
| `WIN08` | Credential Reuse and Lateral Movement | `CH08_Credential_Reuse` | intermediate | WIN07 | 5 | 10h 00m | `WIN09` | published |
| `WIN09` | Complete Network Assessment | `CH09_Assessment` | intermediate | WIN08 | 3 | 6h 00m | `WIN10` | published |
| `WIN10` | Active Directory and Authentication | `CH_WIN10_AD_Authentication` | beginner | WIN02 | 2 | 1h 15m | `LIN01` | published |
| `LIN01` | Linux Service Enumeration | `CH_LIN01_Linux_Service_Enumeration` | beginner | WIN01 | 6 | 12h 00m | `LIN01B` | published |
| `LIN01B` | Network Discovery | `CH_LIN01B_Network_Discovery` | beginner | LIN01 | 2 | 1h 10m | `LIN02` | published |
| `LIN02` | SSH Authentication and Discovery | `CH_LIN02_SSH_Authentication` | intermediate | LIN01B | 3 | 6h 00m | `LIN02B` | published |
| `LIN02B` | SMB and SNMP Enumeration | `CH_LIN02B_SMB_SNMP` | intermediate | LIN02 | 4 | 2h 35m | `LIN03` | published |
| `LIN03` | SSH Post-Exploitation and Privilege Escalation | `CH_LIN03_SSH_Post_Exploitation` | intermediate | LIN02B | 3 | 6h 00m | `LIN03B` | published |
| `LIN03B` | Privilege Escalation and Password Hashes | `CH_LIN03B_Privilege_Hashes` | intermediate | LIN03 | 4 | 3h 10m | `LIN04` | published |
| `LIN04` | Lateral Movement | `CH_LIN04_Lateral_Movement` | intermediate | LIN03B | 4 | 3h 20m | `LIN05` | published |
| `LIN05` | Detection and Response | `CH_LIN05_Detection` | intermediate | LIN04 | 2 | 2h 30m | `LIN09` | published |
| `LIN09` | Capstone Assessments | `CH_LIN09_Assessments` | intermediate | LIN05 | 2 | 2h 00m | `WEB01` | published |
| `MSF01` | Metasploit Framework Fundamentals | `CH_MSF01_Framework_Fundamentals` | beginner | LIN01 | 4 | 6h 00m | `MSF02` | published |
| `MSF02` | Exploitation and Post-Exploitation | `CH_MSF02_Exploitation_and_Post_Exploitation` | intermediate | MSF01 | 4 | 7h 15m | `SOC01` | published |
| `VM01` | Asset Inventory and Exposure | `CH_VM01_Asset_Inventory_Exposure` | beginner | NET00 | 4 | 8h 00m | `VM02` | planned |
| `VM02` | Authenticated Scanning with OpenVAS | `CH_VM02_OpenVAS_Authenticated_Scanning` | intermediate | VM01 | 5 | 10h 00m | `VM03` | planned |
| `VM03` | Nessus Concepts and Web Scanning with Nikto and OWASP ZAP | `CH_VM03_Nessus_Nikto_ZAP` | intermediate | VM02 | 5 | 10h 00m | `VM04` | planned |
| `VM04` | Risk Scoring and Prioritisation | `CH_VM04_Risk_Scoring_Prioritisation` | intermediate | VM01 | 5 | 10h 00m | `VM05` | planned |
| `VM05` | Patch Validation | `CH_VM05_Patch_Validation` | intermediate | VM02, VM04 | 4 | 8h 00m | `VM06` | planned |
| `VM06` | Exceptions and Remediation Workflow | `CH_VM06_Exceptions_Remediation` | intermediate | VM04 | 4 | 8h 00m | `VM07` | planned |
| `VM07` | Host Hardening with Lynis | `CH_VM07_Lynis_Host_Hardening` | intermediate | VM01, VM05 | 4 | 8h 00m | `VM08` | planned |
| `VM08` | Vulnerability Management Capstone | `CH_VM08_VM_Capstone` | advanced | VM05, VM06, VM07 | 2 | 6h 00m | `SOC01` | planned |
| `SOC01` | Telemetry Foundations | `CH_SOC01_Telemetry_Foundations` | beginner | NET02 | 4 | 8h 00m | `SOC02` | planned |
| `SOC02` | Network Detection with Suricata | `CH_SOC02_Suricata_Detection` | intermediate | SOC01 | 5 | 10h 00m | `SOC03` | planned |
| `SOC03` | Network Metadata and Hunting with Zeek | `CH_SOC03_Zeek_Hunting` | intermediate | SOC02 | 4 | 8h 00m | `SOC04` | planned |
| `SOC04` | Endpoint and Vulnerability Detection with Wazuh | `CH_SOC04_Wazuh_Endpoint_Detection` | intermediate | SOC01 | 5 | 10h 00m | `SOC05` | planned |
| `SOC05` | Alert Triage and Case Management | `CH_SOC05_Alert_Triage_Cases` | intermediate | SOC02, SOC04 | 5 | 10h 00m | `SOC06` | planned |
| `SOC06` | Detection as Code | `CH_SOC06_Detection_As_Code` | advanced | SOC02, SOC04 | 4 | 8h 00m | `SOC07` | planned |
| `SOC07` | Host Defense with Fail2Ban | `CH_SOC07_Fail2Ban_Host_Defense` | intermediate | SOC01 | 4 | 8h 00m | `SOC08` | planned |
| `SOC08` | Security Onion Capstone | `CH_SOC08_Security_Onion_Capstone` | advanced | SOC03, SOC05, SOC06, SOC07 | 3 | 8h 00m | `FOR01` | planned |
| `PLAT01` | Docker and Container Security | `CH_PLAT01_Docker_Containers` | beginner | LIN01 | 5 | 10h 00m | `PLAT02` | planned |
| `PLAT02` | Kubernetes Fundamentals and Hardening | `CH_PLAT02_Kubernetes_Hardening` | intermediate | PLAT01 | 6 | 12h 00m | `PLAT03` | planned |
| `PLAT03` | CI/CD with GitHub Actions, GitLab, SonarQube, and Dependency-Check | `CH_PLAT03_GitHub_Actions_CI` | intermediate | PLAT01 | 6 | 12h 00m | `PLAT04` | planned |
| `PLAT04` | Terraform and Infrastructure as Code | `CH_PLAT04_Terraform_IaC` | intermediate | PLAT02 | 5 | 10h 00m | `PLAT05` | planned |
| `PLAT05` | Ansible and Configuration Management | `CH_PLAT05_Ansible_Configuration` | intermediate | PLAT01 | 4 | 8h 00m | `PLAT06` | planned |
| `PLAT06` | Cilium eBPF Networking, Security, and Hubble | `CH_PLAT06_Cilium_eBPF` | advanced | PLAT02 | 4 | 8h 00m | `PLAT07` | planned |
| `PLAT07` | Calico Network Policy and eBPF | `CH_PLAT07_Calico_Policy` | advanced | PLAT02 | 4 | 8h 00m | `PLAT08` | planned |
| `PLAT08` | Istio Service Mesh | `CH_PLAT08_Istio_Service_Mesh` | advanced | PLAT02 | 4 | 8h 00m | `PLAT09` | planned |
| `PLAT09` | Platform Engineering Capstone | `CH_PLAT09_Platform_Capstone` | advanced | PLAT03, PLAT04, PLAT05, PLAT06, PLAT07, PLAT08 | 2 | 6h 00m | `SOC01` | planned |
| `NENG01` | Network Source of Truth with NetBox | `CH_NENG01_NetBox_Source_Of_Truth` | beginner | NET00 | 4 | 8h 00m | `NENG02` | planned |
| `NENG02` | Monitoring with LibreNMS | `CH_NENG02_LibreNMS_Monitoring` | intermediate | NENG01 | 4 | 8h 00m | `NENG03` | planned |
| `NENG03` | Configuration Backup with Oxidized | `CH_NENG03_Oxidized_Config_Backup` | intermediate | NENG01 | 3 | 6h 00m | `NENG04` | planned |
| `NENG04` | Firewall and Segmentation with OPNsense/pfSense | `CH_NENG04_OPNsense_Segmentation` | intermediate | NET00 | 5 | 10h 00m | `NENG05` | planned |
| `NENG05` | NAC and Zero Trust with PacketFence | `CH_NENG05_PacketFence_NAC` | advanced | NENG04 | 5 | 10h 00m | `NENG06` | planned |
| `NENG06` | Identity Integration with OpenIAM | `CH_NENG06_OpenIAM_Network_Integration` | advanced | NENG05, IAM08 | 3 | 6h 00m | `NENG07` | planned |
| `NENG07` | Network Automation with NAPALM | `CH_NENG07_NAPALM_Automation` | advanced | NENG01, NENG03 | 4 | 8h 00m | `NENG08` | planned |
| `NENG08` | Open vSwitch and Mininet Virtual Networks | `CH_NENG08_Open_vSwitch_Mininet` | advanced | NENG04 | 5 | 10h 00m | `NENG09` | planned |
| `NENG09` | Network Engineering Capstone | `CH_NENG09_Network_Engineering_Capstone` | advanced | NENG02, NENG03, NENG06, NENG07, NENG08 | 2 | 6h 00m | `SOC01` | planned |

## Track details

### Beginner Cybersecurity (`high-school`)

- **Audience:** Grades 9-12 learners with everyday computer experience and no assumed cybersecurity background.
- **Difficulty:** beginner
- **Track prerequisites:** None
- **Exercises:** 18
- **Estimated duration:** 7h 00m
- **Required environment:** RangeBox with browser, terminal, and beginner lab targets
- **Recommended next track:** `netfor`
- **Role alignment:** Entry-level Cyber Defense Analyst, IT Support, SOC Analyst (entry)
- **Status:** published

| Chapter | Directory | Prerequisites | Recommended next |
|---|---|---|---|
| `BEG01` — RangeBox Foundations | `CH_HS09_Grade_9_RangeBox_Basics` | None | `BEG02` |
| `BEG02` — Command Line, Files, and Networks | `CH_HS10_Grade_10_RangeBox_Basics` | BEG01 | `BEG03` |
| `BEG03` — Defensive Evidence | `CH_HS11_Grade_11_Defensive_Security` | BEG02 | `BEG04` |
| `BEG04` — Applied Challenges | `CH_HS12_Grade_12_Applied_Cybersecurity` | BEG03 | `NET00` |

### Network Security (`netfor`)

- **Audience:** Beginner-to-intermediate learners who need network foundations, log analysis, and packet evidence.
- **Difficulty:** beginner
- **Track prerequisites:** BEG04
- **Exercises:** 22
- **Estimated duration:** 19h 45m
- **Required environment:** RangeBox with terminal, browser, and network lab targets
- **Recommended next track:** `webpt`
- **Role alignment:** Network Defender, SOC Analyst, Network Engineer
- **Status:** published

| Chapter | Directory | Prerequisites | Recommended next |
|---|---|---|---|
| `NET00` — Network Foundations | `CH_N0_Network_Foundations` | None | `NET01` |
| `NET01` — Log Analysis | `CH_NET01_Log_Analysis` | NET00 | `NET01B` |
| `NET01B` — Traffic and Log Correlation | `CH_NET01B_Traffic_And_Logs` | NET01 | `NET02` |
| `NET02` — PCAP Forensics | `CH_NET02_PCAP_Forensics` | NET01B | `NET03` |
| `NET03` — Firewalls and Network Policy | `CH_NETSY12_Firewalls` | NET02 | `NET04` |
| `NET04` — Device Topology and Routed Paths | `CH_NET12_Device_Topology` | NET03 | `WEB01` |

### Web Application Security (`webpt`)

- **Audience:** Intermediate learners who can use a terminal and understand HTTP basics.
- **Difficulty:** intermediate
- **Track prerequisites:** NET00, NET01
- **Exercises:** 16
- **Estimated duration:** 21h 35m
- **Required environment:** RangeBox with browser, terminal, and web lab targets
- **Recommended next track:** `software-security`
- **Role alignment:** Application Security Tester, Penetration Tester, Secure Developer
- **Status:** published

| Chapter | Directory | Prerequisites | Recommended next |
|---|---|---|---|
| `WEB01` — Web Reconnaissance | `CH_WEB01_Web_Reconnaissance` | NET00 | `WEB01B` |
| `WEB01B` — Advanced Recon and Traversal | `CH_WEB01B_Advanced_Recon` | WEB01 | `WEB02` |
| `WEB02` — SQL Injection and Web Exploitation | `CH_WEB02_Web_Exploitation` | WEB01B | `WEB02B` |
| `WEB02B` — API and Injection | `CH_WEB02B_API_And_Injection` | WEB02 | `WEB03` |
| `WEB03` — Advanced Web Exploitation | `CH_WEB03_Advanced_Exploitation` | WEB02B | `SWSEC01` |

### Software Security (`software-security`)

- **Audience:** Intermediate learners who can read code and understand web requests.
- **Difficulty:** intermediate
- **Track prerequisites:** WEB02
- **Exercises:** 2
- **Estimated duration:** 30m
- **Required environment:** RangeBox with browser and software-security lab targets
- **Recommended next track:** `malware`
- **Role alignment:** Secure Developer, Application Security Engineer, Penetration Tester
- **Status:** published

| Chapter | Directory | Prerequisites | Recommended next |
|---|---|---|---|
| `SWSEC01` — Software Security Foundations | `CH_SWSEC_Software_Security` | WEB02 | `MAL01` |

### Malware Analysis (`malware`)

- **Audience:** Intermediate learners with networking and forensic evidence experience.
- **Difficulty:** intermediate
- **Track prerequisites:** NET02, FOR01
- **Exercises:** 10
- **Estimated duration:** 7h 25m
- **Required environment:** RangeBox with terminal and isolated malware-analysis targets
- **Recommended next track:** `forensics`
- **Role alignment:** Malware Analyst, Incident Responder, Threat Intelligence Analyst
- **Status:** published

| Chapter | Directory | Prerequisites | Recommended next |
|---|---|---|---|
| `MAL01` — Malware Fundamentals | `CH_MAL01_Malware_Fundamentals` | NET02 | `MAL02` |
| `MAL02` — Executable Analysis | `CH_MAL02_Executable_Analysis` | MAL01 | `MAL03` |
| `MAL03` — Detection and Triage | `CH_MAL03_Detection_And_Triage` | MAL02 | `FOR01` |

### Digital Forensics (`forensics`)

- **Audience:** Intermediate learners who want to investigate memory, disk, endpoint, email, browser, and network evidence.
- **Difficulty:** intermediate
- **Track prerequisites:** NET02
- **Exercises:** 4
- **Estimated duration:** 2h 35m
- **Required environment:** RangeBox with forensic evidence images, PCAPs, and the synthetic DFIR evidence pack
- **Recommended next track:** `osint`
- **Role alignment:** Digital Forensics Examiner, Incident Responder, Threat Intelligence Analyst
- **Status:** published

| Chapter | Directory | Prerequisites | Recommended next |
|---|---|---|---|
| `FOR01` — Memory Forensics | `CH_FOR01_Memory_Forensics` | NET02 | `FOR02` |
| `FOR02` — Network Forensics | `CH_FOR02_Network_Forensics` | FOR01 | `FOR03` |
| `FOR03` — Topology Forensics | `CH_FOR03_Topology_Forensics` | FOR02 | `OSINT01` |

### OSINT (`osint`)

- **Audience:** Adult learners who want public-source investigation skills; Grades 9-12 are not assigned the live extensions.
- **Difficulty:** beginner
- **Track prerequisites:** NET00
- **Exercises:** 9
- **Estimated duration:** 4h 50m
- **Required environment:** Browser and RangeBox; offline mirrors, with optional read-only adult extensions
- **Recommended next track:** `identity`
- **Role alignment:** OSINT Analyst, Threat Intelligence Analyst, Investigator
- **Status:** published

| Chapter | Directory | Prerequisites | Recommended next |
|---|---|---|---|
| `OSINT01` — OSINT Foundations | `CH_OSINT01_OSINT_Foundations` | NET00 | `IAM01` |
| `OSINT02` — Mobile OSINT | `CH_OSINT02_Mobile_OSINT` | OSINT01 | `OSINT03` |
| `OSINT03` — Canary Tokens and Deception | `CH_OSINT03_Canary_And_Deception` | OSINT02 | `IAM01` |

### Identity & Access (`identity`)

- **Audience:** Intermediate learners interested in authentication, federation, and account lifecycle.
- **Difficulty:** intermediate
- **Track prerequisites:** NET00
- **Exercises:** 39
- **Estimated duration:** 75h 10m
- **Required environment:** RangeBox with browser and identity lab targets; Keycloak, Authentik, and OpenIAM containers or VMs
- **Recommended next track:** `forensics`
- **Role alignment:** IAM Analyst, SOC Analyst, Identity Engineer
- **Status:** published

| Chapter | Directory | Prerequisites | Recommended next |
|---|---|---|---|
| `IAM01` — Identity and Access Foundations | `CH_IAM01_Identity_And_Access` | NET00 | `IAM02` |
| `IAM02` — Active Directory and Kerberos | `CH_IAM02_Active_Directory_Kerberos` | IAM01 | `IAM03` |
| `IAM03` — Entra ID and Hybrid Identity | `CH_IAM03_Entra_ID_Hybrid` | IAM02 | `IAM04` |
| `IAM04` — Keycloak and OIDC | `CH_IAM04_Keycloak_OIDC` | IAM02 | `IAM05` |
| `IAM05` — Authentik and MFA | `CH_IAM05_Authentik_MFA` | IAM04 | `IAM06` |
| `IAM06` — Federation: SAML and OIDC | `CH_IAM06_Federation_SAML_OIDC` | IAM04, IAM05 | `IAM07` |
| `IAM07` — Access Review and Joiner/Mover/Leaver | `CH_IAM07_Access_Review_JML` | IAM02 | `IAM08` |
| `IAM08` — OpenIAM Identity Governance | `CH_IAM08_OpenIAM_Governance` | IAM07 | `IAM09` |
| `IAM09` — IAM Capstone | `CH_IAM09_IAM_Capstone` | IAM03, IAM06, IAM08 | `FOR01` |

### OT/ICS Security (`ot`)

- **Audience:** Intermediate learners interested in industrial control systems and Modbus.
- **Difficulty:** intermediate
- **Track prerequisites:** NET00
- **Exercises:** 4
- **Estimated duration:** 3h 00m
- **Required environment:** RangeBox with terminal and Modbus lab target
- **Recommended next track:** `ai`
- **Role alignment:** OT Security Analyst, ICS Engineer, SOC Analyst
- **Status:** published

| Chapter | Directory | Prerequisites | Recommended next |
|---|---|---|---|
| `OT01` — Modbus Fundamentals | `CH_OT01_Modbus_Fundamentals` | NET00 | `OT02` |
| `OT02` — S7comm and PLC Data Blocks | `CH_OT02_S7comm_Data_Blocks` | OT01 | `AI01` |

### AI Hacking (`ai`)

- **Audience:** Intermediate learners exploring prompt injection, policy bypass, and AI-assisted security.
- **Difficulty:** intermediate
- **Track prerequisites:** WEB02
- **Exercises:** 5
- **Estimated duration:** 4h 15m
- **Required environment:** RangeBox with browser and mock AI lab target
- **Recommended next track:** `winpt`
- **Role alignment:** AI Security Analyst, Red Team Operator, Secure AI Developer
- **Status:** published

| Chapter | Directory | Prerequisites | Recommended next |
|---|---|---|---|
| `AI01` — AI Security Foundations | `CH_AI01_AI_Foundations` | WEB02 | `AI02` |
| `AI02` — Agentic AI Security | `CH_AI02_Agentic_AI_Security` | AI01, WEB02 | `WIN01` |

### Windows Penetration Testing (`winpt`)

- **Audience:** Intermediate learners who have completed the beginner pathway or have equivalent terminal and networking experience.
- **Difficulty:** intermediate
- **Track prerequisites:** BEG04, NET00
- **Exercises:** 53
- **Estimated duration:** 103h 15m
- **Required environment:** RangeBox with terminal, browser, and Windows lab targets
- **Recommended next track:** `linpt`
- **Role alignment:** Penetration Tester, Red Team Operator, SOC Analyst
- **Status:** published

| Chapter | Directory | Prerequisites | Recommended next |
|---|---|---|---|
| `WIN01` — Enumeration | `CH01_Enumeration` | None | `WIN02` |
| `WIN02` — SMB Reconnaissance | `CH02_SMB_Reconnaissance` | WIN01 | `WIN03` |
| `WIN03` — SMB Credential Attacks | `CH03_SMB_Credential_Attacks` | WIN02 | `WIN04` |
| `WIN04` — RDP Exploitation | `CH04_RDP_Exploitation` | WIN03 | `WIN05` |
| `WIN05` — WinRM Exploitation | `CH05_WinRM_Exploitation` | WIN04 | `WIN06` |
| `WIN06` — MSSQL Exploitation | `CH06_MSSQL_Exploitation` | WIN05 | `WIN07` |
| `WIN07` — LDAP Enumeration | `CH07_LDAP_Enumeration` | WIN06 | `WIN08` |
| `WIN08` — Credential Reuse and Lateral Movement | `CH08_Credential_Reuse` | WIN07 | `WIN09` |
| `WIN09` — Complete Network Assessment | `CH09_Assessment` | WIN08 | `WIN10` |
| `WIN10` — Active Directory and Authentication | `CH_WIN10_AD_Authentication` | WIN02 | `LIN01` |

### Linux Fundamentals (`linpt`)

- **Audience:** Intermediate learners building Linux enumeration, SSH access, privilege escalation, and detection skills.
- **Difficulty:** intermediate
- **Track prerequisites:** WIN09
- **Exercises:** 30
- **Estimated duration:** 38h 45m
- **Required environment:** RangeBox with terminal and Linux lab targets
- **Recommended next track:** `webpt`
- **Role alignment:** Penetration Tester, Linux Administrator, Incident Responder
- **Status:** published

| Chapter | Directory | Prerequisites | Recommended next |
|---|---|---|---|
| `LIN01` — Linux Service Enumeration | `CH_LIN01_Linux_Service_Enumeration` | WIN01 | `LIN01B` |
| `LIN01B` — Network Discovery | `CH_LIN01B_Network_Discovery` | LIN01 | `LIN02` |
| `LIN02` — SSH Authentication and Discovery | `CH_LIN02_SSH_Authentication` | LIN01B | `LIN02B` |
| `LIN02B` — SMB and SNMP Enumeration | `CH_LIN02B_SMB_SNMP` | LIN02 | `LIN03` |
| `LIN03` — SSH Post-Exploitation and Privilege Escalation | `CH_LIN03_SSH_Post_Exploitation` | LIN02B | `LIN03B` |
| `LIN03B` — Privilege Escalation and Password Hashes | `CH_LIN03B_Privilege_Hashes` | LIN03 | `LIN04` |
| `LIN04` — Lateral Movement | `CH_LIN04_Lateral_Movement` | LIN03B | `LIN05` |
| `LIN05` — Detection and Response | `CH_LIN05_Detection` | LIN04 | `LIN09` |
| `LIN09` — Capstone Assessments | `CH_LIN09_Assessments` | LIN05 | `WEB01` |

### Metasploit Operations (`msfpt`)

- **Audience:** Learners who have completed the beginner pathway or have equivalent Linux and network service experience.
- **Difficulty:** intermediate
- **Track prerequisites:** LIN01, NET00
- **Exercises:** 8
- **Estimated duration:** 13h 15m
- **Required environment:** RangeBox with terminal, Kali tools, and a KVM-capable isolated Metasploitable 2 target
- **Recommended next track:** `soc`
- **Role alignment:** Penetration Tester, Red Team Operator, SOC Analyst
- **Status:** published

| Chapter | Directory | Prerequisites | Recommended next |
|---|---|---|---|
| `MSF01` — Metasploit Framework Fundamentals | `CH_MSF01_Framework_Fundamentals` | LIN01 | `MSF02` |
| `MSF02` — Exploitation and Post-Exploitation | `CH_MSF02_Exploitation_and_Post_Exploitation` | MSF01 | `SOC01` |

- `MSF01`: No 00_Introduction page; the track introduction is CH_MSF00_Track_Introduction.
- `MSF02`: No 00_Introduction page; the track introduction is CH_MSF00_Track_Introduction.

### Vulnerability Management (`vm`)

- **Audience:** Learners moving from exploitation into defensive exposure management, asset ownership, and remediation.
- **Difficulty:** intermediate
- **Track prerequisites:** BEG04, NET00
- **Exercises:** 33
- **Estimated duration:** 68h 00m
- **Required environment:** RangeBox with Linux and Windows targets, OpenVAS/Greenbone, and a synthetic asset inventory
- **Recommended next track:** `soc`
- **Role alignment:** Vulnerability Management Analyst, Security Analyst, Risk Analyst, Patch Manager
- **Status:** planned

| Chapter | Directory | Prerequisites | Recommended next |
|---|---|---|---|
| `VM01` — Asset Inventory and Exposure | `CH_VM01_Asset_Inventory_Exposure` | NET00 | `VM02` |
| `VM02` — Authenticated Scanning with OpenVAS | `CH_VM02_OpenVAS_Authenticated_Scanning` | VM01 | `VM03` |
| `VM03` — Nessus Concepts and Web Scanning with Nikto and OWASP ZAP | `CH_VM03_Nessus_Nikto_ZAP` | VM02 | `VM04` |
| `VM04` — Risk Scoring and Prioritisation | `CH_VM04_Risk_Scoring_Prioritisation` | VM01 | `VM05` |
| `VM05` — Patch Validation | `CH_VM05_Patch_Validation` | VM02, VM04 | `VM06` |
| `VM06` — Exceptions and Remediation Workflow | `CH_VM06_Exceptions_Remediation` | VM04 | `VM07` |
| `VM07` — Host Hardening with Lynis | `CH_VM07_Lynis_Host_Hardening` | VM01, VM05 | `VM08` |
| `VM08` — Vulnerability Management Capstone | `CH_VM08_VM_Capstone` | VM05, VM06, VM07 | `SOC01` |

### Security Operations (`soc`)

- **Audience:** Learners who want hands-on detection, triage, hunting, and case management with open-source telemetry.
- **Difficulty:** intermediate
- **Track prerequisites:** NET02, FOR01
- **Exercises:** 34
- **Estimated duration:** 70h 00m
- **Required environment:** RangeBox with Sysmon, Suricata, Zeek, and Wazuh; Security Onion as an optional heavy profile
- **Recommended next track:** `forensics`
- **Role alignment:** SOC Analyst, Detection Engineer, Incident Responder, Threat Hunter
- **Status:** planned

| Chapter | Directory | Prerequisites | Recommended next |
|---|---|---|---|
| `SOC01` — Telemetry Foundations | `CH_SOC01_Telemetry_Foundations` | NET02 | `SOC02` |
| `SOC02` — Network Detection with Suricata | `CH_SOC02_Suricata_Detection` | SOC01 | `SOC03` |
| `SOC03` — Network Metadata and Hunting with Zeek | `CH_SOC03_Zeek_Hunting` | SOC02 | `SOC04` |
| `SOC04` — Endpoint and Vulnerability Detection with Wazuh | `CH_SOC04_Wazuh_Endpoint_Detection` | SOC01 | `SOC05` |
| `SOC05` — Alert Triage and Case Management | `CH_SOC05_Alert_Triage_Cases` | SOC02, SOC04 | `SOC06` |
| `SOC06` — Detection as Code | `CH_SOC06_Detection_As_Code` | SOC02, SOC04 | `SOC07` |
| `SOC07` — Host Defense with Fail2Ban | `CH_SOC07_Fail2Ban_Host_Defense` | SOC01 | `SOC08` |
| `SOC08` — Security Onion Capstone | `CH_SOC08_Security_Onion_Capstone` | SOC03, SOC05, SOC06, SOC07 | `FOR01` |

### Platform Engineering (`platform`)

- **Audience:** Learners who build and operate the delivery platform: containers, Kubernetes, CI/CD, infrastructure as code, and configuration management.
- **Difficulty:** intermediate
- **Track prerequisites:** LIN01, NET00
- **Exercises:** 40
- **Estimated duration:** 82h 00m
- **Required environment:** RangeBox with Docker, a local Kubernetes cluster, GitHub Actions workflow fixtures, Terraform, and Ansible
- **Recommended next track:** `soc`
- **Role alignment:** Platform Engineer, DevSecOps Engineer, Cloud Security Engineer, Site Reliability Engineer
- **Status:** planned

| Chapter | Directory | Prerequisites | Recommended next |
|---|---|---|---|
| `PLAT01` — Docker and Container Security | `CH_PLAT01_Docker_Containers` | LIN01 | `PLAT02` |
| `PLAT02` — Kubernetes Fundamentals and Hardening | `CH_PLAT02_Kubernetes_Hardening` | PLAT01 | `PLAT03` |
| `PLAT03` — CI/CD with GitHub Actions, GitLab, SonarQube, and Dependency-Check | `CH_PLAT03_GitHub_Actions_CI` | PLAT01 | `PLAT04` |
| `PLAT04` — Terraform and Infrastructure as Code | `CH_PLAT04_Terraform_IaC` | PLAT02 | `PLAT05` |
| `PLAT05` — Ansible and Configuration Management | `CH_PLAT05_Ansible_Configuration` | PLAT01 | `PLAT06` |
| `PLAT06` — Cilium eBPF Networking, Security, and Hubble | `CH_PLAT06_Cilium_eBPF` | PLAT02 | `PLAT07` |
| `PLAT07` — Calico Network Policy and eBPF | `CH_PLAT07_Calico_Policy` | PLAT02 | `PLAT08` |
| `PLAT08` — Istio Service Mesh | `CH_PLAT08_Istio_Service_Mesh` | PLAT02 | `PLAT09` |
| `PLAT09` — Platform Engineering Capstone | `CH_PLAT09_Platform_Capstone` | PLAT03, PLAT04, PLAT05, PLAT06, PLAT07, PLAT08 | `SOC01` |

### Network Engineering and Infrastructure (`neteng`)

- **Audience:** Learners moving from packet-level analysis into network source of truth, monitoring, configuration control, segmentation, and network access control.
- **Difficulty:** intermediate
- **Track prerequisites:** NET00
- **Exercises:** 35
- **Estimated duration:** 72h 00m
- **Required environment:** RangeBox with NetBox, LibreNMS, Oxidized, OPNsense or pfSense, PacketFence, Open vSwitch, Mininet, and a small segmented network
- **Recommended next track:** `platform`
- **Role alignment:** Network Engineer, Network Operations Specialist, Infrastructure Engineer, NOC Analyst
- **Status:** planned

| Chapter | Directory | Prerequisites | Recommended next |
|---|---|---|---|
| `NENG01` — Network Source of Truth with NetBox | `CH_NENG01_NetBox_Source_Of_Truth` | NET00 | `NENG02` |
| `NENG02` — Monitoring with LibreNMS | `CH_NENG02_LibreNMS_Monitoring` | NENG01 | `NENG03` |
| `NENG03` — Configuration Backup with Oxidized | `CH_NENG03_Oxidized_Config_Backup` | NENG01 | `NENG04` |
| `NENG04` — Firewall and Segmentation with OPNsense/pfSense | `CH_NENG04_OPNsense_Segmentation` | NET00 | `NENG05` |
| `NENG05` — NAC and Zero Trust with PacketFence | `CH_NENG05_PacketFence_NAC` | NENG04 | `NENG06` |
| `NENG06` — Identity Integration with OpenIAM | `CH_NENG06_OpenIAM_Network_Integration` | NENG05, IAM08 | `NENG07` |
| `NENG07` — Network Automation with NAPALM | `CH_NENG07_NAPALM_Automation` | NENG01, NENG03 | `NENG08` |
| `NENG08` — Open vSwitch and Mininet Virtual Networks | `CH_NENG08_Open_vSwitch_Mininet` | NENG04 | `NENG09` |
| `NENG09` — Network Engineering Capstone | `CH_NENG09_Network_Engineering_Capstone` | NENG02, NENG03, NENG06, NENG07, NENG08 | `SOC01` |

## Recommended pathway

`BEG01` → `BEG02` → `BEG03` → `BEG04` → `NET00` → `NET01` → `NET01B` → `NET02` → `NET03` → `NET04` → `WEB01` → `WEB01B` → `WEB02` → `WEB02B` → `WEB03` → `SWSEC01` → `MAL01` → `MAL02` → `MAL03` → `FOR01` → `FOR02` → `FOR03` → `OSINT01` → `OSINT02` → `OSINT03` → `IAM01` → `IAM02` → `IAM03` → `IAM04` → `IAM05` → `IAM06` → `IAM07` → `IAM08` → `IAM09` → `OT01` → `OT02` → `AI01` → `AI02` → `WIN01` → `WIN02` → `WIN03` → `WIN04` → `WIN05` → `WIN06` → `WIN07` → `WIN08` → `WIN09` → `WIN10` → `LIN01` → `LIN01B` → `LIN02` → `LIN02B` → `LIN03` → `LIN03B` → `LIN04` → `LIN05` → `LIN09` → `MSF01` → `MSF02` → `VM01` → `VM02` → `VM03` → `VM04` → `VM05` → `VM06` → `VM07` → `VM08` → `SOC01` → `SOC02` → `SOC03` → `SOC04` → `SOC05` → `SOC06` → `SOC07` → `SOC08` → `PLAT01` → `PLAT02` → `PLAT03` → `PLAT04` → `PLAT05` → `PLAT06` → `PLAT07` → `PLAT08` → `PLAT09` → `NENG01` → `NENG02` → `NENG03` → `NENG04` → `NENG05` → `NENG06` → `NENG07` → `NENG08` → `NENG09`

## Evidence ladder

| Level | Term | Definition |
|---:|---|---|
| 1 | **Observed** | Directly present in output or evidence. |
| 2 | **Inferred** | A reasonable interpretation that still requires more verification. |
| 3 | **Validated** | Confirmed through an approved controlled test. |
| 4 | **Impacted** | A demonstrated effect on confidentiality, integrity, availability, identity, or process state. |
| 5 | **Remediated** | The root cause has been changed. |
| 6 | **Verified** | A regression test confirms the correction. |

See [Cross-Curriculum Terminology](TERMINOLOGY.md) for the full term list.
