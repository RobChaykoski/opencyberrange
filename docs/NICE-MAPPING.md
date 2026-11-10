# NICE mapping matrix

This matrix maps the platform's tracks to the **NICE Workforce Framework for
Cybersecurity** (NIST SP 800-181r1). It is an indicative curriculum crosswalk,
not a formal certification, accreditation, or work-role validation. Validate
work-role names, task IDs, and KSA IDs against the current NICE Framework before
using this in a programme review, grant application, or REB submission.

## How to read the matrix

- **NICE category** uses the framework's seven categories: Securely Provision
  (SP), Operate and Maintain (OM), Oversee and Govern (OV), Protect and Defend
  (PR), Analyze (AN), Collect and Operate (CO), and Investigate (IN).
- **Representative work roles** are the roles the track most directly supports.
  A track can support more than one role and does not cover every task in a role.
- **Task/KSA focus** describes the observable activities the labs practise. It
  is deliberately phrased as behaviour, not as a claim that the platform teaches
  every KSA for a role.
- **Platform evidence** is what an instructor can point to: labs, workbook
  exercises, flags, quizzes, capstones, and certificates.

## Track mapping

| Track | NICE category | Representative NICE work roles | Task/KSA focus | Platform evidence |
|---|---|---|---|---|
| **Windows Penetration Testing** | Protect and Defend (PR); Analyze (AN) | Vulnerability Assessment Analyst; Exploitation Analyst; Cyber Defense Analyst | Reconnaissance, SMB/RDP/WinRM/MSSQL/LDAP enumeration, credential attacks, AD reconnaissance, lateral movement, full-scope assessment | 53 labs, sequential levels, capstone and final assessments, flags, hints, level certificates |
| **Linux Fundamentals** | Operate and Maintain (OM); Protect and Defend (PR); Analyze (AN) | Network Operations Specialist; Systems Administrator; Cyber Defense Analyst | Linux service discovery, SSH authentication and post-exploitation, privilege escalation, pivoting, detection, capstone assessment | 37 labs, levels 1–5 plus capstone, flags, quizzes, certificates |
| **Web Application Security** | Securely Provision (SP); Protect and Defend (PR); Analyze (AN) | Secure Software Assessor; Vulnerability Assessment Analyst; Exploitation Analyst | Web reconnaissance, directory traversal, SQL injection, command injection, API and authentication testing, full web-to-root chain | 16 labs, levels 1–3, flags, workbook analysis questions |
| **Network Security** | Operate and Maintain (OM); Protect and Defend (PR); Analyze (AN) | Network Operations Specialist; Cyber Defense Analyst; Cyber Defense Incident Responder | Packet capture, DNS and HTTP analysis, firewall policy, traffic correlation, exfiltration, incident reconstruction | 16 labs, Network Foundations through Traffic Analysis, packet captures, flags |
| **Malware Analysis** | Analyze (AN); Protect and Defend (PR); Investigate (IN) | Cyber Defense Forensics Analyst; Cyber Defense Analyst; Exploitation Analyst | Static and dynamic triage, strings and PE analysis, Ghidra reversing, C2 traffic, document and attachment analysis | 8 labs, evidence workstations, PCAPs, workbook walkthroughs |
| **OT/ICS Security** | Protect and Defend (PR); Operate and Maintain (OM) | Cyber Defense Analyst; Cyber Defense Incident Responder | Modbus/ICS discovery, safe scanning, register analysis, OT incident response | 1 foundational lab; suitable as an entry point before a fuller ICS programme |
| **AI Hacking** | Analyze (AN); Securely Provision (SP) | Exploitation Analyst; Secure Software Assessor | Prompt injection, jailbreak policy bypass, indirect prompt injection, AI application testing and remediation | 3 labs, chatbot targets, flags, workbook analysis |
| **OSINT** | Collect and Operate (CO); Analyze (AN) | Exploitation Analyst; Cyber Operations Planner | Public-surface mapping, image metadata and steganography, source-code and public-repository leaks, responsible collection | 5 labs, OSINT workbook, synthetic personas, flags |
| **High School Cybersecurity** | Operate and Maintain (OM); Protect and Defend (PR) | Network Operations Specialist; Cyber Defense Analyst (entry) | Digital safety, link and file inspection, email metadata, networking foundations, browser and source inspection, defensive log reading, guided RangeBox practice | 13 labs across Grades 9–12, browser-first targets, workbook pages, certificates |
| **Software Security** | Securely Provision (SP); Protect and Defend (PR) | Secure Software Assessor; Vulnerability Assessment Analyst | Source review, hidden export routes, command injection, secure coding and remediation | 2 labs, source-review targets, flags, workbook exercises |
| **Digital Forensics** | Investigate (IN); Analyze (AN) | Cyber Defense Forensics Analyst; Cyber Defense Incident Responder | Memory analysis, VoIP call reconstruction, evidence handling, timeline and artefact interpretation | 2 labs, evidence workstations, PCAPs, workbook walkthroughs, certificates |

## Coverage by NICE category

| NICE category | Tracks that contribute | Coverage note |
|---|---|---|
| **Securely Provision (SP)** | Web Application Security; Software Security; AI Hacking | Secure design and code review are covered; this is not a full secure-development lifecycle programme |
| **Operate and Maintain (OM)** | Linux Fundamentals; Network Security; High School Cybersecurity | Service administration, network operations, and defensive foundations |
| **Oversee and Govern (OV)** | Instructor and administrator workflows; privacy and consent modules | Governance content is platform-operational, not a dedicated GRC track |
| **Protect and Defend (PR)** | Windows; Linux; Web; Network; Malware; OT/ICS; High School; Software Security | The largest coverage area: prevention, detection, response, and assessment |
| **Analyze (AN)** | Windows; Linux; Web; Network; Malware; AI; OSINT; Forensics | Evidence interpretation, exploitation analysis, and assessment |
| **Collect and Operate (CO)** | OSINT | Collection planning and responsible public-source work |
| **Investigate (IN)** | Digital Forensics; Malware Analysis | Forensic artefact handling and incident reconstruction |

## Evidence an instructor can collect

For each lab, the platform records completion, flag attempts, hints used, time
spent, and optional quiz results. At the level, it issues a certificate when
every visible exercise is complete. At the course level, it provides assignment
completion, scoreboards, and PDF reports. These signals can support a NICE-
aligned programme review when paired with a syllabus, assessment rubric, and
instructor judgement.

## What this matrix is not

- It is **not** a claim that OpenCyberRange is NICE-certified or that a learner
  who completes a track is qualified for a work role.
- It is **not** a complete task/KSA crosswalk. NICE work roles contain many
  tasks and KSAs that a lab platform cannot assess on its own.
- It does **not** replace a formal curriculum review, accreditation, or
  workplace competency assessment.

## Maintenance

Review this matrix at least annually or when the NICE Framework is updated:

1. Confirm the category and work-role names against the current NICE Framework.
2. Add or remove tracks and labs, and update the evidence column.
3. Record the NICE Framework version and review date in the change log.
4. Keep the wording behavioural: describe what learners do, not what they are
   guaranteed to become.

## Related documents

- [System architecture](ARCHITECTURE.md)
- [Learning framework](LEARNING-FRAMEWORK.md)
- [REB-ready survey package](research/REB-SURVEY-PACKAGE.md)
- [NICE Framework](https://www.nist.gov/itl/applied-cybersecurity/nice/nice-framework-resource-center)
