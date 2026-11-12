# Content gap analysis — November 2026

Status: **planning** (12 November 2026). This is a curriculum roadmap, not a
release commitment.

The catalogue covers 13 tracks and roughly 150 labs. Classic pentest
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

## Sequencing

1. OT labs: the tester image is ready.
2. AD labs: the RangeBox toolchain is ready.
3. Container/CI/CD labs: no new images.
4. Software-security arc.
5. Blue-team depth.

Add each new track's `_track_quiz.yaml` and framework mapping in the same PR as
its labs; `validate-lab.py` and the new-lab scaffolding enforce the metadata.
Keep the existing pattern of pairing every offensive lab with a defensive
debrief in the workbook.
