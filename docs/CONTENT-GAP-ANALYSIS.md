# Content gap analysis — November 2026

Status: **planning** (12 November 2026). This is a curriculum roadmap, not a
release commitment.

The catalogue covers 12 track folders and roughly 160 labs. Classic pentest
enumeration is deep (Windows services, Linux privilege escalation, web
reconnaissance to injection, network analysis). The gaps below are ranked by
learner value and by how much of the existing RangeBox/tester toolchain they
reuse.

## Priority gaps

### 1. Active Directory

The Windows track is strong on SMB, RDP, WinRM, MSSQL, and LDAP enumeration but
has no AD attack content. The RangeBox already ships `netexec`, `evil-winrm`,
and `impacket`, so the tooling is installed and unused.

Suggested arc:

- basic AD enumeration with `ldapdomaindump` and user/group mapping;
- Kerberoasting with `impacket-GetUserSPNs`, then hashcat;
- AS-REP roasting and password-spray policy;
- lateral movement with `evil-winrm` and `impacket-wmiexec`;
- path analysis (a small Neo4j sidecar if BloodHound-style labs are added);
- a defensive debrief: LAPS, tiered administration, and the misconfiguration
  the learner abused.

### 2. OT/ICS

There is one Modbus lab against a tester sidecar that already ships `pymodbus`,
`python-snap7` (musl-built), `pycomm3`, and `asyncua`. Four more labs are
low-cost and high-differentiation:

- S7comm register read/write;
- EtherNet/IP CIP enumeration;
- OPC-UA browse and weak-auth testing;
- DNP3 raw-socket polling.

Keep the `plc1.masa.local` naming pattern and pair each offensive lab with an
operations-safe defensive debrief.

### 3. Software security

Two labs is thin for a full track. Add the standard web-application set:

- reflected and stored XSS;
- IDOR and broken access control;
- CSRF;
- SSRF;
- insecure file upload;
- JWT and session handling;
- deserialization basics.

Pair the track with the Web track for a "build then break" module.

### 4. Container and CI/CD security

Students use Docker directly (RangeBox). Labs that need no new images:

- container introspection and misconfiguration discovery;
- capabilities and privileged-container risk;
- image supply-chain basics, using the platform's own signed lockfiles and
  checksum gates as the teaching example;
- secrets in images;
- a poisoned CI/CD pipeline (action or artifact).

### 5. Blue-team depth

Offence coverage is strong; defence is thin (Suricata, log correlation, one
firewall pair). Add:

- a SIEM exercise that queries the platform's own event schema;
- a threat-hunting exercise that finds the pivot in a provided capture from the
  network tap;
- a workbook-format incident-response tabletop;
- Linux disk forensics with the `sleuthkit`/`foremost` tools already installed,
  complementing the Windows memory lab.

## Smaller gaps

- Applied cryptography for adults: hashing, password storage, TLS interception,
  and certificate pinning. The high-school track has Caesar/Base64 only.
- Windows privilege escalation: service misconfiguration, UAC, and token
  escalation. Linux has a full SUID arc.
- Defender-angle phishing analysis: write the verdict for an email, not just
  reverse the attachment.
- AI track depth: model output validation, media provenance for adults, and
  AI-assisted reconnaissance from the defender's side.

## Deliberately not recommended

- Mobile: emulator infrastructure and low lab-network value.
- Wireless/RFID: requires physical hardware the platform does not ship.
- Deep binary exploitation: steep prerequisite curve; a specialist track if
  ever.
- Cloud-provider labs: real account and cost risk; revisit only with a sponsor.

## Emulator and routing opportunities

Docker-only options, ranked by fit. None requires KVM or a redistributed vendor
image:

1. **FRRouting containers.** Real BGP/OSPF/MPLS on plain containers. Route
   hijack and origin-authentication labs pair directly with the network tap.
2. **containerlab.** Declares FRR/cEOS/SR Linux topologies as data; needs
   privileged containers, so borrow its topology format for a compose extension.
3. **CAN bus (python-can, cantools, ICSim).** A virtual interface makes one
   container a whole bus; supports spoofing, replay, and IDS labs.
4. **OpenPLC / pyModbus.** Extends the OT track with a debrief-friendly target.
5. **Mininet.** SDN/OpenFlow labs; heavier and more niche than the options above.
6. **FirmAE/Firmadyne.** IoT firmware emulation; needs KVM, so schedule it after
   the others.

Avoid Cisco Packet Tracer (proprietary, licence-incompatible) and committed
vendor images (IOS, cEOS). Ship the lab and let instructors supply images
out-of-band, as the Wordlists policy already does.

## Backlog: teach the platform you built

Cheapest and most differentiated labs, because the tooling already ships:

| Lab | Reuses | Cost |
|---|---|---|
| C2 tunnelling with wstunnel | The wstunnel binary the platform installs | Low |
| Valkey attack surface (unauthenticated `CONFIG SET`, then the hardened fix) | The platform's own rate-limit store | Low |
| Applied crypto: bcrypt/argon2, salting, MultiFernet key rotation | The platform's `crypto.py` rotation path | Low |
| Capstone: audit your own range | Supply-chain lock, CSP-hash, and header scripts | Low |
| BGP route hijack and detection | FRR plus the network tap | Medium |
| Network forensics with RemnuxBox | The RemnuxBox image | Low |
| CAN bus spoofing and IDS | python-can virtual bus | Low-Medium |

Every emulator and capture lab should set `x-ocr-network-tap: true` so students
watch their own traffic on the wire.

## Sequencing

1. Quick wins: wstunnel tunnelling, Valkey attack surface, applied crypto, and
   the audit-your-own-range capstone.
2. OT labs: the tester image is ready.
3. AD labs: the RangeBox toolchain is ready.
4. Container/CI/CD labs: no new images.
5. BGP route hijack with FRR and the tap.
6. Network forensics with RemnuxBox, then CAN bus.
7. Software-security arc and blue-team depth.

Add each new track's `_track_quiz.yaml` and framework mapping in the same PR as
its labs; `validate-lab.py` and the new-lab scaffolding enforce the metadata.
Keep the existing pattern of pairing every offensive lab with a defensive
debrief in the workbook.
