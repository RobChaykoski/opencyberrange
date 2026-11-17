# Active Directory: Delegation Abuse

**Track:** Windows · **Level:** 11 · **Time:** 110 minutes · **Difficulty:** advanced

## Scenario

A web service account in the LAB domain is trusted for delegation. Identify the trust and the risk, then recover the token.

## What you will practise

- Distinguish unconstrained, constrained, and resource-based delegation
- Identify a delegation configuration that enables impersonation
- Assess the blast radius of the delegation
- Recommend the least-privilege configuration

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
