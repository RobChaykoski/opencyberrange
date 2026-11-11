# Glossary

This glossary defines the terms used across SWOCTS Cyber Range. Where a term has a
standard meaning in cyber threat intelligence, the definition follows the
[MISP data model](https://www.misp-project.org/datamodels/) and the
[MISP taxonomies](https://github.com/MISP/misp-taxonomies). The MISP machine tag
is shown so the same term can be used consistently in notes, reports, and
exports.

Two kinds of entry appear here:

- **Standard term** — follows MISP or another named standard.
- **Platform term** — specific to the SWOCTS Cyber Range training workflow. It is
  not a MISP concept and should not be tagged as one.

## How MISP machine tags work

MISP taxonomies use machine tags in the form `namespace:predicate="value"`.
Some taxonomies have a single level, such as `tlp:clear`; others have a
predicate and a value, such as `malware_classification:malware-category="Ransomware"`.
Use the exact namespace, predicate, and value from the taxonomy. Do not invent
local variants.

Examples:

```text
tlp:clear
PAP:GREEN
admiralty-scale:source-reliability="a"
estimative-language:likelihood-probability="likely"
kill-chain:Reconnaissance
malware_classification:malware-category="Ransomware"
workflow:state="complete"
```

## MISP core model

| Term | Definition | MISP reference |
|---|---|---|
| Event | A container for attributes, objects, and context about one incident, observation, report, collection, or analysis. | `misp:event-type="incident"` |
| Attribute | A single piece of information in an event, such as an IP address, domain, hash, filename, or email address. An attribute may or may not be used as an indicator. | Attribute type plus `misp:ids="true"` or `misp:ids="false"` |
| Object | A structured group of related attributes, such as a file object with a name, hash, size, and type. | MISP object template |
| Galaxy | A collection of related clusters, such as threat actors, malware families, tools, or ATT&CK techniques. | MISP galaxy |
| Cluster | One entry in a galaxy, such as a named threat actor or malware family. | Galaxy cluster |
| Taxonomy | A controlled vocabulary with a namespace, predicates, and values. | Taxonomy namespace |
| Tag | A label applied to an event, attribute, or object. A tag may come from a taxonomy or be free text. | `namespace:predicate="value"` |
| Sighting | Evidence that an attribute or object was observed, such as a matching file hash or network connection. | MISP sighting |
| Indicator | An attribute or object used to detect likely malicious activity. In MISP this is controlled with the IDS flag. | `misp:ids="true"` |
| Observable | An observed fact without a judgement about whether it is malicious. In MISP, model it as an attribute with the IDS flag disabled. | `misp:ids="false"` |
| Feed | An external source that supplies events or attributes to a MISP instance. | MISP feed |
| Sharing group | A defined group of organisations and instances that may receive an event. | MISP sharing group |
| MISP instance | A MISP server that stores, correlates, and shares events. | MISP instance |

## Cyber threat intelligence terms

| Term | Definition | MISP reference |
|---|---|---|
| Indicator of compromise (IOC) | An observable that is assessed as malicious or associated with malicious activity, such as a known C2 domain or malware hash. | `ioc:artifact-state="malicious"` |
| Indicator of attack (IOA) | Behaviour or telemetry that indicates an attack in progress, such as a suspicious process chain. It is behavioural rather than a single atomic value. | No single taxonomy; describe the behaviour with an ATT&CK technique or `common-taxonomy` value |
| TTP | Tactics, techniques, and procedures. The broad description of how an adversary operates. Do not use TTP as a synonym for one ATT&CK technique. | `kill-chain:*` for phase; `mitre-attack-pattern` galaxy for technique |
| Threat actor | The person, group, or organisation responsible for an attack. | MISP `threat-actor` galaxy |
| Campaign | A set of related malicious activities conducted over a period of time. | MISP `campaign` galaxy |
| Kill chain | The Lockheed Martin phase model: Reconnaissance, Weaponization, Delivery, Exploitation, Installation, Command and Control, and Actions on Objectives. | `kill-chain:Reconnaissance` (and the other phase names) |
| Diamond model | An intrusion analysis model built from four features: Adversary, Capability, Infrastructure, and Victim. | `diamond-model:Adversary` (and the other features) |
| Command and control (C2) | The infrastructure and channel an adversary uses to task and control an implant. | `common-taxonomy:malware="command-and-control"` |
| Exfiltration | Unauthorised transfer of data from a victim environment. | `pentest:post_exploitation="data_exfiltration"` |
| Lateral movement | Movement from one compromised host or account to another inside the same environment. | Use the ATT&CK technique; no single MISP taxonomy value |
| Persistence | A mechanism that lets an adversary keep access across reboots, logons, or service restarts. | `pentest:post_exploitation="persistence"` |
| Privilege escalation | Gaining a higher privilege level than the attacker was granted. | `pentest:post_exploitation="privilege_escalation"` |
| False positive | A finding that is not actually malicious. The alert fired, but the underlying behaviour is benign or expected. | `false-positive:risk="high"` for expected rate; `false-positive:confirmed="false"` for a specific alert |
| True positive | A finding that is correctly identified as malicious or unwanted. | No single taxonomy value; use `false-positive:confirmed="true"` only when the taxonomy semantics fit |
| Benign true positive | A detection that correctly fired on real behaviour, but the behaviour is authorised or harmless. It is not a false positive. | No single taxonomy value; explain in the event |
| Confidence | How strongly an analyst trusts a judgement. Keep analytic confidence separate from source reliability. | `misp:confidence-level="usually-confident"` or `estimative-language:confidence-in-analytic-judgment="high"` |
| Source reliability | How trustworthy the source of the information is, on the Admiralty A–F scale. | `admiralty-scale:source-reliability="a"` |
| Information credibility | How likely the information itself is true, on the Admiralty 1–6 scale. | `admiralty-scale:information-credibility="1"` |
| Likelihood | The probability that a stated event will occur. Use estimative-language terms instead of bare percentages. | `estimative-language:likelihood-probability="likely"` |
| TLP | Traffic Light Protocol 2.0 sharing label: CLEAR, GREEN, AMBER, AMBER+STRICT, or RED. | `tlp:clear`, `tlp:green`, `tlp:amber`, `tlp:amber+strict`, `tlp:red` |
| PAP | Permissible Actions Protocol: what a recipient may do with the information, from passive-only to unrestricted. | `PAP:RED`, `PAP:AMBER`, `PAP:GREEN`, `PAP:CLEAR` |
| Workflow state | The maturity of an analysis: incomplete, complete, draft, ongoing, rejected, or release. | `workflow:state="complete"` |
| Malware category | The broad class of malware, such as virus, worm, trojan, ransomware, rootkit, downloader, spyware, or botnet. | `malware_classification:malware-category="Ransomware"` |
| Ransomware type | The ransomware mechanism: scareware, locker ransomware, or crypto-ransomware. | `ransomware:type="crypto-ransomware"` |
| Vulnerability | A weakness that can be exploited. Record the identifier and exploit status separately. | `vulnerability:sighting="exploited"`; also CVE, CWE, CVSS |
| Event type | The purpose of an event: observation, incident, report, collection, analysis, or automatic-analysis. | `misp:event-type="incident"` |
| Threat level | The assessed risk level of the information: no-risk, low-risk, medium-risk, or high-risk. | `misp:threat-level="high-risk"` |

## Forensics terms

| Term | Definition | MISP reference |
|---|---|---|
| PCAP | A packet capture file containing network traffic. It is evidence, not an indicator by itself. | Share as an attribute or file object; do not tag the PCAP as an IOC without context |
| Packet | One unit of network data with headers and a payload. | No taxonomy value |
| Flow | A series of packets that share a source, destination, and protocol, often identified by a five-tuple. | No taxonomy value |
| Memory dump | A copy of the contents of volatile memory, also called a memory image. Treat it as sensitive evidence. | Share as a file object when needed; no single taxonomy value |
| Acquisition | The process of capturing volatile or non-volatile evidence before it changes. | No taxonomy value |
| Chain of custody | The documented history of who handled evidence, when, and how. | No taxonomy value |
| Artifact | Any object or trace with forensic value, such as a file, log entry, registry key, packet, or memory structure. | No single taxonomy value |
| Timeline | A chronological ordering of events from one or more evidence sources. | No taxonomy value |
| Hash | A fixed-length fingerprint of data, used to identify and verify evidence. Use the algorithm name in the attribute type. | MISP attribute types such as `md5`, `sha1`, `sha256` |
| Volatility | An open-source memory forensics framework used to inspect memory images. | Tool name; do not force it into `misp:tool` |
| Process list | The set of processes that were running when a memory image was captured. | No taxonomy value |
| Injected code | Code placed into another process's memory, often to hide execution or evade detection. | Describe with an ATT&CK technique; no single taxonomy value |

## Network and enumeration terms

These are teaching terms used in the workbook. They are not MISP taxonomy
values. Terms that already appear in another section are not repeated here.

| Term | Definition |
|---|---|
| Host | A device on a network with an IP address, such as a server, workstation, or lab container. |
| Hostname | A human-readable name that resolves to an IP address. |
| Target | The specific host assigned to an exercise. Only the target shown in the exercise is in scope. |
| IP address | Internet Protocol address: a numeric address that identifies a host on a network. |
| Subnet | A block of IP addresses on the same network. The platform assigns each student session its own subnet. |
| Loopback / localhost | The local host address `127.0.0.1`. A service bound only to loopback is reachable only from that host. |
| Port | A numbered logical endpoint on a host, from `0` to `65535`. The operating system uses the port number to decide which program receives a connection. |
| Port list | A comma-separated set of ports selected with `-p`, such as `-p 22,80,443`. A list does not include ports that are not named. |
| Port range | A start-to-end port selection, such as `-p 1-65535`. A range includes every port between the endpoints. |
| Baseline | A first scan result kept as a comparison point for a later, broader scan. |
| Non-standard port | A port number other than the service's conventional port, such as SSH on a port other than 22. |
| Probe | A test packet or request sent to a port so its response can be observed. |
| Security through obscurity | Relying on a hidden port, name, or detail instead of real access control. |
| Protocol | The rules two systems use to communicate. TCP and UDP are transport protocols. |
| TCP | Transmission Control Protocol: a reliable, connection-based transport protocol used by most services in Chapter 1. |
| UDP | User Datagram Protocol: a connectionless transport protocol. UDP scanning is outside Chapter 1. |
| SYN | The first packet in a TCP connection. A port scan sends SYN probes to test whether a port accepts connections. |
| SYN-ACK | The target's acceptance response to a SYN. It indicates that a service is listening on the port. |
| RST | A reset response. It indicates that the target refused the connection because nothing is listening on the port. |
| ICMP | Internet Control Message Protocol: the protocol used by tools such as `ping`. A target may block ICMP while still accepting TCP connections. |
| Share | A folder or resource exposed over SMB. An anonymous share allows access without credentials. |
| Service | A program that listens on a port and responds to connections, such as a web server, SSH server, file-sharing service, or database. |
| Port scan | Probing a host's ports to learn which are open, closed, or filtered. |
| Scan breadth | The number of ports or hosts a scan covers. Broader scans provide more coverage but take longer and create more noise. |
| Scan noise | The traffic, log entries, and alert volume a scan creates. Broader scans generally create more noise. |
| Well-known port | A port in the 0–1023 range, conventionally assigned to standard services such as SSH, HTTP, and HTTPS. |
| Registered port | A port in the 1024–49151 range, used by registered applications and custom services. |
| Dynamic or ephemeral port | A port in the 49152–65535 range, commonly used for temporary client connections. |
| IANA | Internet Assigned Numbers Authority: the organisation that maintains port-number and protocol registries. |
| Version detection | Asking an open service to reveal its software product and version. Nmap's `-sV` option performs this. |
| Service name | Nmap's label for the protocol or service, often based on the port or a protocol signature. It is a label, not a guarantee of the underlying product. |
| Product | The software family or application name reported by version detection, such as nginx, Samba, or xrdp. |
| Version | The specific release string reported by a service or inferred by a scanner. It may be missing, partial, or inaccurate. |
| Banner | The text or protocol response a service returns when probed. Scanners use banners and other responses to infer product and version. A banner may be missing, masked, or misleading. |
| Signature | A pattern a scanner matches against a service response to identify a product or protocol. |
| Observation | A factual record of what a tool or service returned, kept separate from interpretation. |
| Conclusion | An interpretation supported by observations. A conclusion should state its uncertainty and must not claim more than the evidence supports. |
| `tcpwrapped` | An Nmap state or service label meaning the service accepted a connection but did not reveal enough information to identify itself. |
| OS fingerprinting | Inferring a host's operating system from how it responds to network probes. Nmap's `-O` option performs this. |
| Enumeration | The systematic discovery of hosts, ports, services, versions, and operating-system details. |
| Scope | The set of systems, ports, and actions an assessment is authorized to test. In the workbook, scope is the target shown in the exercise. |
| Open port | A port where a service is listening and accepting connections. |
| Closed port | A port on a reachable host where nothing is listening. |
| Filtered port | A port where a firewall or network control is silently dropping probes. The scan cannot tell whether a service is behind it. |
| Nmap | Network Mapper: a free, open-source network discovery and security-auditing tool. |
| NSE | Nmap Scripting Engine: the part of Nmap that runs scripts against discovered services for deeper enumeration. |
| OS | Operating system, such as Linux or Windows. |
| OS family | A broad platform group, such as Windows, Linux, or Unix. |
| OS version | A specific release within an operating-system family, when it can be inferred. |
| OS confidence | Nmap's estimate of how closely a fingerprint matches a known operating system. A low value means the guess is weak. |
| Fingerprint | The pattern of network responses a scanner compares with a database to infer an operating system or service. Fingerprinting is inference, not direct access. |
| TTL | Time To Live: a packet field that limits how many network hops a packet can traverse. Different systems use different defaults. |
| TCP window size | A TCP flow-control value that can differ between operating-system implementations. |
| DF (Don't Fragment) | A flag in the IP header that controls whether a packet may be fragmented. Its behaviour can contribute to an OS fingerprint. |
| TCP options | Optional fields in a TCP header. Their order and presence can differ between operating-system implementations. |
| Network distance | The number of network hops between the scanner and the target. |
| Aggressive OS guess | A lower-confidence operating-system candidate that Nmap lists when it cannot make an exact match. It is a guess, not a confirmed result. |
| sudo | A command that runs another command with elevated privileges, usually as the administrative `root` user. |
| Root | The administrative account on Linux and Unix systems, with broad permission to change the system. |
| Privilege | The level of access a user or process has. Elevated privilege means more power to read or change the system. |
| CPE | Common Platform Enumeration: a standardized identifier for a product and version, used when looking up vulnerabilities. |
| CVE | Common Vulnerabilities and Exposures: a standardized identifier for a publicly known vulnerability, such as `CVE-2024-12345`. |
| NVD | National Vulnerability Database: the NIST database that enriches CVE records with severity, weakness, and product information. |
| Exploitability | Whether a weakness can actually be exploited in a specific configuration. A version match alone does not establish exploitability. |
| Backport | Applying a security fix to an older software version without changing its version number. A version string may therefore be older than the patch level suggests. |
| Security auditing | Checking systems for unintended exposure, configuration weaknesses, or policy drift. |
| Raw packet | A hand-crafted network packet that bypasses the normal networking stack and requires privileged access. |
| Exploitation (general) | Using a discovered weakness to gain access or control. The kill chain also has a phase named Exploitation; that phase is narrower. |
| Penetration test | An authorized security assessment that mimics an attacker's discovery and exploitation steps to find weaknesses before a real attacker does. |
| VPN | Virtual Private Network: an encrypted tunnel that places a remote machine on the lab network. |
| Kali Linux | A Linux distribution that ships with security and penetration-testing tools. |

### Common service acronyms

| Acronym | Expansion | Typical port |
|---|---|---|
| SSH | Secure Shell | 22 |
| HTTP | Hypertext Transfer Protocol | 80 |
| HTTPS | HTTP Secure | 443 |
| MSRPC | Microsoft Remote Procedure Call | 135 |
| NetBIOS | Network Basic Input/Output System | 139 |
| SMB | Server Message Block | 445 |
| MSSQL | Microsoft SQL Server | 1433 |
| RDP | Remote Desktop Protocol | 3389 |
| WinRM | Windows Remote Management | 5985 (HTTP), 5986 (HTTPS) |

## SWOCTS Cyber Range platform terms

These are training-platform terms. They are deliberately not mapped to MISP
taxonomies because they do not describe threat intelligence.

| Term | Definition |
|---|---|
| Lab | A self-contained exercise environment with one or more target containers and a scoped objective. |
| Exercise | A single task inside a lab, usually with a flag and a set of hints. |
| Track | A themed collection of labs, such as Network Security or Malware Analysis. |
| Level | A difficulty grouping inside a track. |
| Course | An instructor-created collection of labs, students, assignments, and due dates. |
| Academy | The course area of the platform. Students see their courses; staff see the programme and course workspaces. |
| Programme | An optional institutional grouping of courses and semester goals. A course can exist without a programme. |
| Course workspace | The course page with Overview, Feedback, and Analytics (staff). |
| Flag | The token a student submits to prove completion, usually in `OCR{...}` format. It is a training marker, not an IOC. |
| Hint | A staged clue that unlocks after a configured time or condition. |
| RangeBox | The browser-based Kali, Ubuntu, or REMnux desktop used to work on a lab. |
| Session | One running instance of a lab assigned to one student. |
| Attempt | One submission of a flag or one launch of a lab, depending on the context. |
| Completion | The recorded state after a student submits the correct flag. |
| Achievement | A badge or micro-credential awarded for a defined piece of practice, progress, or participation. |
| Certificate | The record issued when a track level is completed. It can be downloaded as a PDF and verified by ID. |
| Celebration | A voluntary, anonymous signal of appreciation for a public achievement. One person can celebrate a win once; only the count is shown. |
| Celebration Wall | The cross-course view of public achievements and celebrations. It is not a leaderboard. |

## Orientation and safety terms

These are introductory terms for new learners. They are teaching language, not
MISP taxonomy values. Terms that already appear in another section are not
repeated here.

| Term | Definition |
|---|---|
| Cybersecurity | Keeping computers, accounts, and information safe. It includes defence and careful investigation. |
| Cyber range | A safe, separate practice space for cybersecurity. The computers inside are for practice, not real-world targets. |
| OpenCyberRange | The training platform used to open exercises and the practice desktop. |
| Virtual machine | A computer that runs inside another computer. A lab desktop provided through the web is not installed on the learner's device. |
| Browser | The application used to visit websites, such as Chrome, Edge, Firefox, or Safari. |
| Browser tab | One page area inside a web browser. Keep the exercise tab open while working. |
| Student device | The laptop, desktop, or tablet in front of the learner. It is not the RangeBox desktop or the target. |
| Local device | The laptop, desktop, or tablet in front of the learner. Same as student device. |
| Browser controls | The parts of a web browser, such as the address bar, tabs, back and forward buttons, refresh button, and browser window buttons. |
| Address bar | The field at the top of a web browser that shows the page address. |
| OpenCyberRange page | The website where a learner signs in, opens exercises, and launches RangeBox. |
| Sign in | Enter a username and password to start a session on the platform. |
| Session | The time a learner is signed in to the platform. |
| Dashboard | The first page after sign-in, with shortcuts to the learner's work. |
| Workspace | The page or desktop where an activity is performed. |
| Verification code | A short code from an authenticator app or teacher, used when an account asks for a second sign-in step. |
| Pop-up | A new browser window or tab that a browser may block. |
| Training token | A code in a practice file that helps the learner find the activity flag. It is not a real secret. |
| Desktop | The screen with windows, icons, and open apps. |
| Remote workspace | The RangeBox desktop running on the platform and shown inside the learner's browser. |
| Panel | The bar on a desktop that shows open applications and shortcuts. Also called a taskbar. |
| Application | A program that runs on a desktop, such as File Manager or Terminal. |
| Approved application | An application the activity says is safe to open. |
| Window | A framed area that holds an application. It usually has a title bar, content area, and window controls. |
| Title bar | The top bar of a window. It shows the window title and controls. |
| Minimize | Hide a window without closing it. The application keeps running. |
| Maximize | Make a window fill the desktop. |
| Restore | Return a maximized window to its previous size. |
| Close | Close an application window. Closing an application does not stop the lab. |
| RangeBox controls | The toolbar in the RangeBox viewer, including Clipboard, Minimize, Fullscreen, and Close when the viewer is opened as its own page. |
| Fullscreen | A RangeBox viewer control that expands the remote desktop. It is different from browser fullscreen. |
| Disconnect | Lose or close the remote viewer connection. The lab may keep running. |
| Stop | End the lab or RangeBox session. Unsaved work in the desktop may be lost. |
| Terminal | A text window where a learner types commands. |
| Shell | The program inside a terminal that reads a command, runs it, and prints the result. |
| Prompt | The text at the start of a terminal line that shows the shell is ready. Same as command prompt. |
| Command | An instruction typed into a terminal. |
| Option | A setting that changes how a command works. It often starts with a hyphen, such as `-l`. |
| Argument | Extra information a command acts on, such as a file name or folder name. |
| Output | The text a command prints after the learner presses Enter. |
| Cursor | The blinking line or block that shows where typing will appear. |
| Enter key | The key pressed to run a command. |
| Case sensitivity | Treating uppercase and lowercase letters as different. Linux command names are usually lowercase. |
| Replaceable value | A word in capitals, such as `FILE` or `FOLDER`, that is replaced with a real name. |
| Command not found | A message that means the shell could not find a command with that exact spelling. |
| Directory | Another word for a folder. |
| Continuation prompt | A prompt such as `>` that shows the shell is waiting for the rest of a command. Press `Ctrl` + `C` to cancel and return to the normal prompt. |
| Command prompt | The place in a terminal where text is typed. It often shows the account and current folder. |
| Account | A learner's login for OpenCyberRange. The password must remain private. |
| RangeBox account | The temporary Linux account inside the RangeBox desktop. It is not the OpenCyberRange login. |
| Authorized activity | Work a teacher or the platform asks a learner to do inside OpenCyberRange. If unsure, stop and ask first. |
| Linux | A type of operating system used by the practice desktop. Prior Linux experience is not required. |
| Server | A computer that provides something to other computers, such as a web page. |
| File | A named piece of data, such as a document, picture, or text file. |
| Folder | A container that holds files. |
| Link | Clickable text or an image that opens a page in a browser. |
| URL | A web address, such as the address of a page or file. |
| Taskbar | The bar on a desktop that shows open apps and shortcuts. |
| Application menu | The menu used to open programs on a desktop. |
| Digital safety | Habits that protect a learner online, such as checking a link or file before clicking or opening it. |
| CyberChef | A browser tool for encoding, decoding, and transforming data. |
| Decode | Change encoded or scrambled data back into a form that can be read. |
| Encode | Change data into another form. Encoding does not keep data secret. |
| Encoding | Changing data into another representation. Encoding is not encryption and does not protect data by itself. |
| Base64 | A common encoding that represents data using letters, numbers, and symbols. It does not protect data. |
| Caesar shift | A simple cipher that moves each letter by a fixed number of places. |
| Capstone | A final activity that brings earlier skills together. |
| Accessibility options | Ways to make an activity easier to use, such as zoom, keyboard navigation, less motion, or extra time. |
| Reduced motion | A device setting that reduces animation and motion effects. |
| Clipboard | A temporary place for copied text. RangeBox has a Clipboard button for moving text between the browser and the desktop. |

## Programme, learning, and analytics terms

These terms describe the teaching, feedback, and programme layer. They are
descriptive, not grades or predictions.

| Term | Definition |
|---|---|
| Course health | A private, descriptive summary of how a course is landing: completion, student experience, response rate, instructor coaching, and knowledge checks. Shown as Healthy, Watch, or Needs attention. |
| Overall feedback | The weighted 0–100 summary of the available course feedback. It is not a grade and is not shown publicly. |
| Response rate | Unique students who gave feedback divided by enrolled students. |
| Coaching coverage | Students with at least one instructor coaching note divided by enrolled students. |
| Knowledge check | Optional benchmark practice attached to an exercise. It shows 2–3 randomised questions per attempt, allows unlimited retries, and explains the answer and reference after submission. It is never an exam item or a gate. |
| Cyber DNA (Skill DNA) | The learner character sheet: six descriptive traits, a class, and practice affinities built from existing activity. It is not a grade, a ranking, or a prediction. |
| Trait | One of the six Cyber DNA dimensions: Explorer, Builder, Tester, Defender, Investigator, or Leader. Each is scored 0–100. |
| Affinity | A positive practice direction suggested by completed work, such as offensive security, defensive operations, DFIR, or security leadership. It is not a job label. |
| Individual success profile | The eight-dimension view used by a student and their instructor: progress, pace, independence, persistence, understanding, experience, capability, and support. It ends with one next step. |
| Dean | The institutional role that sets semester goals, reviews programme health, supports instructors, and owns the end-of-term evidence. In 2.5.0 it maps to an administrator or programme lead; it is not a separate database role. |
| Programme lead | The staff role that turns semester goals into a course portfolio and supports instructors. |
| Executive view | The staff-only Academy view of overall progress: goals, trends, projections, course portfolio, student voice, and risks. |
| Projection (forecast) | A transparent estimate of where a programme metric may land, using goal pace, run rate, a moving average, or a trend direction. It always includes a method, sample size, and uncertainty band. It is not an individual prediction. |
| Baseline | The starting value for a goal or course. A projection without a baseline is not a trend. |
| Feeling vs doing | Two separate signals: self-reported feeling from the check-in, and progress against assigned work. They are shown together to prompt a conversation, never as a grade. |
| Small cohort | Fewer than five learners in a group. Counts are shown; percentages are treated as an early signal and may be suppressed. |
| Early signal | A finding based on few responses or few time points. It is not a trend and should not drive a high-stakes decision. |
| Learning evidence | The record used to support a programme or learner review: completion, practice, feedback, knowledge checks, Cyber DNA movement, and certificates. It is descriptive. |

## Security and supply-chain terms

| Term | Definition |
|---|---|
| Trust boundary | A point where data, identity, or permission changes hands, such as the browser to the API, the API to Docker, or a learner to a lab network. |
| STRIDE | A threat-enumeration method: Spoofing, Tampering, Repudiation, Information disclosure, Denial of service, and Elevation of privilege. |
| DREAD | A threat-prioritisation heuristic: Damage, Reproducibility, Exploitability, Affected users, and Discoverability. |
| Supply-chain lock | A committed SHA-256 manifest of platform build inputs and lab content. It detects drift; it does not replace dependency audits, SBOMs, or a signed release. |
| Release evidence | The artefacts that show a release was verified: test and build output, smoke evidence, screenshots, and the supply-chain check. |

## Preferred usage

Use the standard term in new text. Keep direct quotations as they are.

| Prefer | Avoid | Why |
|---|---|---|
| command and control (C2) | C&C, CNC | C2 is the term used by MISP and MITRE ATT&CK. |
| indicator of compromise (IOC) | IOC indicator | The expansion is already in the acronym. |
| observable | IOC, when no malicious judgement has been made | An observable is a fact; an indicator carries a judgement. |
| MITRE ATT&CK technique | TTP, when referring to one technique | TTP is the broader tactics, techniques, and procedures umbrella. |
| threat actor | hacker, bad guy | Neutral, standard attribution language. |
| malware family | virus, unless it is specifically a virus | Virus is one category in `malware_classification`. |
| ransomware | crypto locker, unless it is specifically a locker | Locker ransomware and crypto-ransomware are different types. |
| false positive | benign, when the alert was correct | A benign true positive is not a false positive. |
| TLP:CLEAR | TLP:WHITE in new text | TLP 2.0 uses CLEAR; WHITE is retained for backward compatibility. |
| PAP:CLEAR | PAP:WHITE in new text | CLEAR is the current unrestricted PAP label. |
| analytic confidence: high | probably | Use estimative-language terms and keep confidence separate from likelihood. |
| source reliability: A | trusted source | The Admiralty scale is explicit and repeatable. |
| Cyber DNA | Skill DNA, when talking to learners | Cyber DNA is the learner-facing name; Skill DNA is the implementation and API name. |
| knowledge check | quiz, when describing the optional benchmark | A knowledge check is optional practice, not an exam or a gate. |
| celebration | like, upvote, or applause ranking | A celebration is anonymous and voluntary; the wall shows a count, not a popularity order. |
| course health | scoreboard or ranking | Course health is a private, descriptive summary for the teaching team. |
| programme | department or faculty | A programme is the course-and-goal grouping in this platform. |
| dean | administrator | The dean is an institutional role; the administrator owns platform operations. |
| projection | prediction | A projection is a transparent planning estimate with a method, band, and sample size. |
| early signal | trend | An early signal has too few points or responses to support a trend claim. |
| small cohort | weak cohort | A small cohort is a sample-size limitation, not a judgement about the learners. |

## Sources and review

- [MISP data models](https://www.misp-project.org/datamodels/)
- [MISP taxonomies](https://github.com/MISP/misp-taxonomies)
- [TLP 2.0](https://www.first.org/tlp/)
- [PAP taxonomy](https://www.misp-project.org/taxonomies.html#_pap)
- [MITRE ATT&CK](https://attack.mitre.org/)
- [Lockheed Martin Cyber Kill Chain](https://www.lockheedmartin.com/en-us/capabilities/cyber/cyber-kill-chain.html)
- [Admiralty scale](https://www.misp-project.org/taxonomies.html#_admiralty_scale)
- [ICD 203 estimative language](https://www.dni.gov/files/documents/ICD/ICD-203.pdf)

Reviewed: 2026-11-08 against the MISP taxonomies repository. Recheck when a
taxonomy version changes or when a new term is added to this glossary.
