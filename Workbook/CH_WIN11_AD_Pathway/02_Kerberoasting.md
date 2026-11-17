# Active Directory: Kerberoasting

**Track:** Windows · **Level:** 11 · **Time:** 90 minutes · **Difficulty:** intermediate

## Scenario

The LAB domain has a SQL service account with an SPN. Enumerate the account, recover the assessment token from its service metadata, and write the remediation.

## What you will practise

- Explain how SPNs and service tickets enable Kerberoasting
- Identify kerberoastable service accounts
- Extract a service-ticket artifact and assess password strength
- Recommend managed service accounts and rotation

## Work through the exercise

1. Open the exercise from the Windows track, level 11.
2. Work from the scenario; use the lab hints only when you are stuck.
3. Recover the assessment token and write the evidence the exercise asks for.

## Evidence

- The assessment flag.
- A short note that names the weakness and the defensive control.

## Analysis Questions

**1. What makes a service account kerberoastable?**

**2. Why can a service ticket be attacked offline once it is requested?**

**3. Which account-type and password changes reduce the risk without breaking the service?**

**4. What ticket-request pattern should detection alert on?**

## Defensive takeaway

Tier administration, managed service accounts, least-privilege ACLs, and directory-change auditing remove this class of path.

> The directory is an LDAP simulation of Active Directory. Kerberos
> concepts are discussed in the chapter; binds use LDAP.
