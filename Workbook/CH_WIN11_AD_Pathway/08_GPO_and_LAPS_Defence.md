# Active Directory: GPO, LAPS, and Tiered Administration Defence

**Track:** Windows · **Level:** 11 · **Time:** 90 minutes · **Difficulty:** intermediate

## Scenario

The LAB domain has a workstation baseline. Review the LAPS and GPO settings, recover the token, and list the missing controls.

## What you will practise

- Review a GPO baseline for authentication hardening
- Explain how LAPS removes shared local-admin passwords
- Design tiered administration boundaries
- Recommend monitoring for GPO and LAPS abuse

## Work through the exercise

1. Open the exercise from the Windows track, level 11.
2. Work from the scenario; use the lab hints only when you are stuck.
3. Recover the assessment token and write the evidence the exercise asks for.

## Evidence

- The assessment flag.
- A short note that names the weakness and the defensive control.

## Analysis Questions

**1. How does LAPS remove the shared local-administrator password problem?**

**2. Why is GPO delegation a privilege boundary, not just an administration setting?**

**3. Which baseline controls are missing in this lab's scenario?**

**4. What would you monitor for GPO and LAPS abuse?**

## Defensive takeaway

Tier administration, managed service accounts, least-privilege ACLs, and directory-change auditing remove this class of path.

> The directory is an LDAP simulation of Active Directory. Kerberos
> concepts are discussed in the chapter; binds use LDAP.
