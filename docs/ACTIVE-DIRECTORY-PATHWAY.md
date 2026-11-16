# Active Directory attack and remediation pathway

This pathway closes the largest Windows-track gap: it bridges the existing
LDAP/SMB exercises into a full Active Directory attack path and a remediation
debrief. The source of truth is
`platform/backend/app/data/ad-pathway.yaml`.

## Why this pathway

The Windows track already teaches SMB, RDP, WinRM, MSSQL, and LDAP
enumeration. It does not yet teach domain attack paths. The RangeBox already
ships `netexec`, `evil-winrm`, `impacket`, and a Python environment suitable for
`bloodhound-python`; this pathway uses that toolchain against a disposable,
synthetic domain instead of a real one.

## Progression

| Module | Title | Level | Minutes | Focus |
|---|---|---|---|---|
| AD-01 | Directory Fundamentals and Trust Boundaries | beginner | 60 | domain, forest, OU, DN, service accounts |
| AD-02 | Domain Enumeration and Attack-Path Mapping | beginner | 90 | LDAP, trusts, sessions, BloodHound data |
| AD-03 | Kerberoasting | intermediate | 100 | SPNs, service tickets, offline cracking |
| AD-04 | AS-REP Roasting and Password Spray | intermediate | 90 | pre-auth, AS-REP, lockout policy |
| AD-05 | ACL and DACL Abuse | advanced | 120 | GenericAll, WriteDACL, ForceChangePassword |
| AD-06 | Delegation Abuse | advanced | 120 | unconstrained, constrained, RBCD |
| AD-07 | AD CS Abuse | advanced | 120 | templates, enrollment, ESC-style paths |
| AD-08 | Credential Dumping and Ticket Abuse | advanced | 140 | DCSync, Golden and Silver tickets |
| AD-09 | GPO, LAPS, and Tiered Administration Defence | intermediate | 90 | GPO links, LAPS, gMSA, tiering |
| AD-10 | Capstone: AD Attack Path and Remediation Report | advanced | 180 | full path, evidence, remediation |

The first module uses the existing `windows-2-9-ad-fundamentals-basics` and
`windows-2-10-ad-to-smb-scenario` labs. The rest are the nine `windows-11-*`
labs implemented in 5.17.3.

## Evidence contract

Every module requires an attack path or evidence artifact and a defensive
finding. The capstone requires:

- one defensible path from a low-privilege account to a domain objective;
- each hop with the misconfiguration, evidence, timestamp, and confidence;
- a separation of observation, inference, and missing telemetry;
- a remediation plan with owner, effort, verification, and residual risk.

A flag alone is not completion evidence.

## Safety and isolation

- The target is a disposable, synthetic domain such as `lab.example`.
- No real domain, production trust, or real credential is used.
- No internet egress from the domain or the learner host.
- Credential dumps and tickets stay in the lab and are never published.
- The domain is reset after the exercise.
- A private, approved environment is required for any real Windows evaluation
  media; the public repository does not ship a Windows image or a live domain.

## Labs

Foundation labs:

- `windows-2-9-ad-fundamentals-basics`
- `windows-2-10-ad-to-smb-scenario`

Pathway labs (implemented in 5.17.3; each has a competency contract, a tester
manifest, and a directory-backed exercise):

- `windows-11-1-ad-domain-enumeration`
- `windows-11-2-kerberoasting`
- `windows-11-3-asrep-spray`
- `windows-11-4-acl-dacl-abuse`
- `windows-11-5-delegation-abuse`
- `windows-11-6-adcs-abuse`
- `windows-11-7-dcsync-tickets`
- `windows-11-8-gpo-laps-defence`
- `windows-11-9-ad-capstone`

## Validation

`platform/backend/tests/test_ad_pathway.py` checks ordering, weighting,
prerequisites, taxonomy references, lab existence, planned slug uniqueness,
ATT&CK mappings, evidence requirements, and coverage of Kerberos, ACL,
delegation, AD CS, DCSync, and LAPS.

## Related documents

- [Windows penetration testing workbook](../Workbook/index.md)
- [RBAC and PBAC](RBAC-PBAC.md)
- [Detection engineering pathway](DETECTION-ENGINEERING-PATHWAY.md)
- [DFIR pathway](DFIR-PATHWAY.md)
- [Supply chain](SUPPLY-CHAIN.md)
