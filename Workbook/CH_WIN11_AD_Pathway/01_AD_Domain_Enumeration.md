# Active Directory: Domain Enumeration and Attack-Path Mapping

**Track:** Windows · **Level:** 11 · **Time:** 60 minutes · **Difficulty:** beginner

## Scenario

The range hosts a simulated LAB domain. You have a training analyst account. Enumerate the directory, find the service account, and recover the assessment token from its description.

## What you will practise

- Bind to a directory and enumerate users, groups, and computers
- Identify service accounts and their group membership
- Map a path from a low-privilege account to a privileged group
- Record the evidence needed for a defensive report

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
