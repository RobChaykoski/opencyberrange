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
| `high-school` | Beginner Cybersecurity | New learners with everyday computer experience and no assumed cybersecurity background. | beginner | None | 18 | 7h 00m | RangeBox with browser, terminal, and beginner lab targets | `netfor` | Entry-level Cyber Defense Analyst; IT Support; SOC Analyst (entry) | published |
| `netfor` | Network Security | Beginner-to-intermediate learners who need network foundations, log analysis, and packet evidence. | beginner | BEG04 | 16 | 14h 00m | RangeBox with terminal, browser, and network lab targets | `webpt` | Network Defender; SOC Analyst; Network Engineer | published |
| `webpt` | Web Application Security | Intermediate learners who can use a terminal and understand HTTP basics. | intermediate | NET00, NET01 | 16 | 21h 35m | RangeBox with browser, terminal, and web lab targets | `software-security` | Application Security Tester; Penetration Tester; Secure Developer | published |
| `software-security` | Software Security | Intermediate learners who can read code and understand web requests. | intermediate | WEB02 | 2 | 30m | RangeBox with browser and software-security lab targets | `malware` | Secure Developer; Application Security Engineer; Penetration Tester | published |
| `malware` | Malware Analysis | Intermediate learners with networking and forensic evidence experience. | intermediate | NET02, FOR01 | 8 | 6h 15m | RangeBox with terminal and isolated malware-analysis targets | `forensics` | Malware Analyst; Incident Responder; Threat Intelligence Analyst | published |
| `forensics` | Digital Forensics | Intermediate learners who want to investigate memory and network evidence. | intermediate | NET02 | 2 | 1h 35m | RangeBox with forensic evidence images and PCAPs | `osint` | Digital Forensics Examiner; Incident Responder; Threat Intelligence Analyst | published |
| `osint` | OSINT | Beginner-to-intermediate learners who want public-source investigation skills. | beginner | NET00 | 5 | 2h 55m | Browser and RangeBox; public-source simulation | `identity` | OSINT Analyst; Threat Intelligence Analyst; Investigator | published |
| `identity` | Identity & Access | Intermediate learners interested in authentication, federation, and account lifecycle. | intermediate | NET00 | 3 | 2h 15m | RangeBox with browser and identity lab targets | `forensics` | IAM Analyst; SOC Analyst; Identity Engineer | published |
| `ot` | OT/ICS Security | Intermediate learners interested in industrial control systems and Modbus. | intermediate | NET00 | 1 | 40m | RangeBox with terminal and Modbus lab target | `ai` | OT Security Analyst; ICS Engineer; SOC Analyst | published |
| `ai` | AI Hacking | Intermediate learners exploring prompt injection, policy bypass, and AI-assisted security. | intermediate | WEB02 | 3 | 1h 50m | RangeBox with browser and mock AI lab target | `winpt` | AI Security Analyst; Red Team Operator; Secure AI Developer | published |
| `winpt` | Windows Penetration Testing | Intermediate learners who have completed the beginner pathway or have equivalent terminal and networking experience. | intermediate | BEG04, NET00 | 51 | 102h 00m | RangeBox with terminal, browser, and Windows lab targets | `linpt` | Penetration Tester; Red Team Operator; SOC Analyst | published |
| `linpt` | Linux Fundamentals | Intermediate learners building Linux enumeration, SSH access, privilege escalation, and detection skills. | intermediate | WIN09 | 30 | 38h 45m | RangeBox with terminal and Linux lab targets | `webpt` | Penetration Tester; Linux Administrator; Incident Responder | published |

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
| `NET02` | PCAP Forensics | `CH_NET02_PCAP_Forensics` | intermediate | NET01B | 5 | 5h 30m | `NET03` | published |
| `NET03` | Firewalls and Network Policy | `CH_NETSY12_Firewalls` | intermediate | NET02 | 2 | 2h 15m | `WEB01` | published |
| `WEB01` | Web Reconnaissance | `CH_WEB01_Web_Reconnaissance` | beginner | NET00 | 6 | 12h 00m | `WEB01B` | published |
| `WEB01B` | Advanced Recon and Traversal | `CH_WEB01B_Advanced_Recon` | intermediate | WEB01 | 2 | 1h 15m | `WEB02` | published |
| `WEB02` | SQL Injection and Web Exploitation | `CH_WEB02_Web_Exploitation` | intermediate | WEB01B | 1 | 2h 00m | `WEB02B` | published |
| `WEB02B` | API and Injection | `CH_WEB02B_API_And_Injection` | intermediate | WEB02 | 4 | 2h 50m | `WEB03` | published |
| `WEB03` | Advanced Web Exploitation | `CH_WEB03_Advanced_Exploitation` | intermediate | WEB02B | 3 | 3h 30m | `SWSEC01` | published |
| `SWSEC01` | Software Security Foundations | `CH_SWSEC_Software_Security` | intermediate | WEB02 | 2 | 30m | `MAL01` | published |
| `MAL01` | Malware Fundamentals | `CH_MAL01_Malware_Fundamentals` | intermediate | NET02 | 7 | 5h 25m | `MAL02` | published |
| `MAL02` | Executable Analysis | `CH_MAL02_Executable_Analysis` | intermediate | MAL01 | 1 | 50m | `FOR01` | published |
| `FOR01` | Memory Forensics | `CH_FOR01_Memory_Forensics` | intermediate | NET02 | 1 | 50m | `FOR02` | published |
| `FOR02` | Network Forensics | `CH_FOR02_Network_Forensics` | intermediate | FOR01 | 1 | 45m | `OSINT01` | published |
| `OSINT01` | OSINT Foundations | `CH_OSINT01_OSINT_Foundations` | beginner | NET00 | 5 | 2h 55m | `IAM01` | published |
| `IAM01` | Identity and Access Foundations | `CH_IAM01_Identity_And_Access` | intermediate | NET00 | 3 | 2h 15m | `FOR01` | published |
| `OT01` | Modbus Fundamentals | `CH_OT01_Modbus_Fundamentals` | intermediate | NET00 | 1 | 40m | `AI01` | published |
| `AI01` | AI Security Foundations | `CH_AI01_AI_Foundations` | intermediate | WEB02 | 3 | 1h 50m | `WIN01` | published |
| `WIN01` | Enumeration | `CH01_Enumeration` | beginner | None | 5 | 10h 00m | `WIN02` | published |
| `WIN02` | SMB Reconnaissance | `CH02_SMB_Reconnaissance` | beginner | WIN01 | 8 | 16h 00m | `WIN03` | published |
| `WIN03` | SMB Credential Attacks | `CH03_SMB_Credential_Attacks` | intermediate | WIN02 | 5 | 10h 00m | `WIN04` | published |
| `WIN04` | RDP Exploitation | `CH04_RDP_Exploitation` | intermediate | WIN03 | 6 | 12h 00m | `WIN05` | published |
| `WIN05` | WinRM Exploitation | `CH05_WinRM_Exploitation` | intermediate | WIN04 | 6 | 12h 00m | `WIN06` | published |
| `WIN06` | MSSQL Exploitation | `CH06_MSSQL_Exploitation` | intermediate | WIN05 | 7 | 14h 00m | `WIN07` | published |
| `WIN07` | LDAP Enumeration | `CH07_LDAP_Enumeration` | intermediate | WIN06 | 6 | 12h 00m | `WIN08` | published |
| `WIN08` | Credential Reuse and Lateral Movement | `CH08_Credential_Reuse` | intermediate | WIN07 | 5 | 10h 00m | `WIN09` | published |
| `WIN09` | Complete Network Assessment | `CH09_Assessment` | intermediate | WIN08 | 3 | 6h 00m | `LIN01` | published |
| `LIN01` | Linux Service Enumeration | `CH_LIN01_Linux_Service_Enumeration` | beginner | WIN01 | 6 | 12h 00m | `LIN01B` | published |
| `LIN01B` | Network Discovery | `CH_LIN01B_Network_Discovery` | beginner | LIN01 | 2 | 1h 10m | `LIN02` | published |
| `LIN02` | SSH Authentication and Discovery | `CH_LIN02_SSH_Authentication` | intermediate | LIN01B | 3 | 6h 00m | `LIN02B` | published |
| `LIN02B` | SMB and SNMP Enumeration | `CH_LIN02B_SMB_SNMP` | intermediate | LIN02 | 4 | 2h 35m | `LIN03` | published |
| `LIN03` | SSH Post-Exploitation and Privilege Escalation | `CH_LIN03_SSH_Post_Exploitation` | intermediate | LIN02B | 3 | 6h 00m | `LIN03B` | published |
| `LIN03B` | Privilege Escalation and Password Hashes | `CH_LIN03B_Privilege_Hashes` | intermediate | LIN03 | 4 | 3h 10m | `LIN04` | published |
| `LIN04` | Lateral Movement | `CH_LIN04_Lateral_Movement` | intermediate | LIN03B | 4 | 3h 20m | `LIN05` | published |
| `LIN05` | Detection and Response | `CH_LIN05_Detection` | intermediate | LIN04 | 2 | 2h 30m | `LIN09` | published |
| `LIN09` | Capstone Assessments | `CH_LIN09_Assessments` | intermediate | LIN05 | 2 | 2h 00m | `WEB01` | published |

## Track details

### Beginner Cybersecurity (`high-school`)

- **Audience:** New learners with everyday computer experience and no assumed cybersecurity background.
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
- **Exercises:** 16
- **Estimated duration:** 14h 00m
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
| `NET03` — Firewalls and Network Policy | `CH_NETSY12_Firewalls` | NET02 | `WEB01` |

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
- **Exercises:** 8
- **Estimated duration:** 6h 15m
- **Required environment:** RangeBox with terminal and isolated malware-analysis targets
- **Recommended next track:** `forensics`
- **Role alignment:** Malware Analyst, Incident Responder, Threat Intelligence Analyst
- **Status:** published

| Chapter | Directory | Prerequisites | Recommended next |
|---|---|---|---|
| `MAL01` — Malware Fundamentals | `CH_MAL01_Malware_Fundamentals` | NET02 | `MAL02` |
| `MAL02` — Executable Analysis | `CH_MAL02_Executable_Analysis` | MAL01 | `FOR01` |

### Digital Forensics (`forensics`)

- **Audience:** Intermediate learners who want to investigate memory and network evidence.
- **Difficulty:** intermediate
- **Track prerequisites:** NET02
- **Exercises:** 2
- **Estimated duration:** 1h 35m
- **Required environment:** RangeBox with forensic evidence images and PCAPs
- **Recommended next track:** `osint`
- **Role alignment:** Digital Forensics Examiner, Incident Responder, Threat Intelligence Analyst
- **Status:** published

| Chapter | Directory | Prerequisites | Recommended next |
|---|---|---|---|
| `FOR01` — Memory Forensics | `CH_FOR01_Memory_Forensics` | NET02 | `FOR02` |
| `FOR02` — Network Forensics | `CH_FOR02_Network_Forensics` | FOR01 | `OSINT01` |

### OSINT (`osint`)

- **Audience:** Beginner-to-intermediate learners who want public-source investigation skills.
- **Difficulty:** beginner
- **Track prerequisites:** NET00
- **Exercises:** 5
- **Estimated duration:** 2h 55m
- **Required environment:** Browser and RangeBox; public-source simulation
- **Recommended next track:** `identity`
- **Role alignment:** OSINT Analyst, Threat Intelligence Analyst, Investigator
- **Status:** published

| Chapter | Directory | Prerequisites | Recommended next |
|---|---|---|---|
| `OSINT01` — OSINT Foundations | `CH_OSINT01_OSINT_Foundations` | NET00 | `IAM01` |

### Identity & Access (`identity`)

- **Audience:** Intermediate learners interested in authentication, federation, and account lifecycle.
- **Difficulty:** intermediate
- **Track prerequisites:** NET00
- **Exercises:** 3
- **Estimated duration:** 2h 15m
- **Required environment:** RangeBox with browser and identity lab targets
- **Recommended next track:** `forensics`
- **Role alignment:** IAM Analyst, SOC Analyst, Identity Engineer
- **Status:** published

| Chapter | Directory | Prerequisites | Recommended next |
|---|---|---|---|
| `IAM01` — Identity and Access Foundations | `CH_IAM01_Identity_And_Access` | NET00 | `FOR01` |

### OT/ICS Security (`ot`)

- **Audience:** Intermediate learners interested in industrial control systems and Modbus.
- **Difficulty:** intermediate
- **Track prerequisites:** NET00
- **Exercises:** 1
- **Estimated duration:** 40m
- **Required environment:** RangeBox with terminal and Modbus lab target
- **Recommended next track:** `ai`
- **Role alignment:** OT Security Analyst, ICS Engineer, SOC Analyst
- **Status:** published

| Chapter | Directory | Prerequisites | Recommended next |
|---|---|---|---|
| `OT01` — Modbus Fundamentals | `CH_OT01_Modbus_Fundamentals` | NET00 | `AI01` |

### AI Hacking (`ai`)

- **Audience:** Intermediate learners exploring prompt injection, policy bypass, and AI-assisted security.
- **Difficulty:** intermediate
- **Track prerequisites:** WEB02
- **Exercises:** 3
- **Estimated duration:** 1h 50m
- **Required environment:** RangeBox with browser and mock AI lab target
- **Recommended next track:** `winpt`
- **Role alignment:** AI Security Analyst, Red Team Operator, Secure AI Developer
- **Status:** published

| Chapter | Directory | Prerequisites | Recommended next |
|---|---|---|---|
| `AI01` — AI Security Foundations | `CH_AI01_AI_Foundations` | WEB02 | `WIN01` |

### Windows Penetration Testing (`winpt`)

- **Audience:** Intermediate learners who have completed the beginner pathway or have equivalent terminal and networking experience.
- **Difficulty:** intermediate
- **Track prerequisites:** BEG04, NET00
- **Exercises:** 51
- **Estimated duration:** 102h 00m
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
| `WIN09` — Complete Network Assessment | `CH09_Assessment` | WIN08 | `LIN01` |

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

## Recommended pathway

`BEG01` → `BEG02` → `BEG03` → `BEG04` → `NET00` → `NET01` → `NET01B` → `NET02` → `NET03` → `WEB01` → `WEB01B` → `WEB02` → `WEB02B` → `WEB03` → `SWSEC01` → `MAL01` → `MAL02` → `FOR01` → `FOR02` → `OSINT01` → `IAM01` → `OT01` → `AI01` → `WIN01` → `WIN02` → `WIN03` → `WIN04` → `WIN05` → `WIN06` → `WIN07` → `WIN08` → `WIN09` → `LIN01` → `LIN01B` → `LIN02` → `LIN02B` → `LIN03` → `LIN03B` → `LIN04` → `LIN05` → `LIN09`

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
