# Active Directory and Authentication: Choose the Depth

Two exercises connect directory fundamentals to the SMB skills already used in
the Windows track.

| Exercise | Focus | Time |
|---|---|---|
| 2.9 AD Fundamentals | Domain, DN, users, groups, service accounts, LDAP filters | 35 min |
| 2.10 Directory to Share | Leaked service credential reused against an SMB share | 40 min |

The first exercise is a beginner directory walkthrough. The second is a scenario
that combines the new competency with the existing SMB enumeration strength.

## Modelling note

These labs use an LDAP directory with Active Directory-style objects (domain,
organizational units, users, groups, service accounts) so they run without a
Windows domain controller. The concepts map to AD; Kerberos is discussed below,
but the lab authenticates with LDAP. A follow-up lab can use a real KDC.

## Kerberos in one paragraph

In a Windows domain, the domain controller is the KDC. A user authenticates once
and receives a ticket-granting ticket; service tickets are requested per service.
That is why a leaked service credential is valuable: it can request service
tickets without the user's password prompt. The same least-privilege and rotation
rules apply to both LDAP binds and Kerberos tickets.

## Rules

- Use only the accounts and addresses shown in the exercise.
- Treat the leaked credential as evidence, not as permission to access anything
  outside the lab.
- Do not put the token in a shared document.
