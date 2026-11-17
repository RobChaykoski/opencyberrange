# Active Directory: Credential Dumping and Ticket Abuse

**Track:** Windows · **Level:** 11 · **Time:** 130 minutes · **Difficulty:** advanced

## Scenario

A service account in the LAB domain can request directory replication. Identify the grant, recover the token, and write the detection rule.

## What you will practise

- Explain DCSync and the replication rights it abuses
- Identify accounts with replication permissions
- Describe golden and silver ticket risks
- Recommend tier-0 controls and replication auditing

## Work through the exercise

1. Open the exercise from the Windows track, level 11.
2. Work from the scenario; use the lab hints only when you are stuck.
3. Recover the assessment token and write the evidence the exercise asks for.

## Evidence

- The assessment flag.
- A short note that names the weakness and the defensive control.

## Defensive takeaway

Tier administration, managed service accounts, least-privilege ACLs, and directory-change auditing remove this class of path.

> The directory is an LDAP simulation of Active Directory. Kerberos
> concepts are discussed in the chapter; binds use LDAP.
