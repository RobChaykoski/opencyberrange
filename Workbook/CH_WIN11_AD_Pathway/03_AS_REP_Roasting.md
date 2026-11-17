# Active Directory: AS-REP Roasting and Password Spray

**Track:** Windows · **Level:** 11 · **Time:** 80 minutes · **Difficulty:** intermediate

## Scenario

A legacy service account in the LAB domain has pre-authentication disabled. Find it and recover the assessment token from its metadata.

## What you will practise

- Identify accounts that do not require Kerberos pre-authentication
- Explain why AS-REP roasting works
- Recognise password-spray patterns and lockout risk
- Apply pre-authentication and lockout policy

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
