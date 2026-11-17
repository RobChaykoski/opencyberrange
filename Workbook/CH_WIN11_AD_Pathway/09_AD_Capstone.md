# Active Directory: Attack Path and Remediation Capstone

**Track:** Windows · **Level:** 11 · **Time:** 160 minutes · **Difficulty:** advanced

## Scenario

The LAB domain contains several weaknesses from the pathway. Build the path from analyst to domain admin, collect evidence, and write the remediation plan.

## What you will practise

- Chain enumeration, credential access, and privilege escalation
- Produce an evidence-backed attack path
- Prioritise remediation by risk and blast radius
- Write an executive and technical summary

## Work through the exercise

1. Open the exercise from the Windows track, level 11.
2. Work from the scenario; use the lab hints only when you are stuck.
3. Recover the assessment token and write the evidence the exercise asks for.

## Evidence

- The assessment flag.
- A short note that names the weakness and the defensive control.

## Analysis Questions

**1. Which findings form the attack chain, and what evidence supports each link?**

**2. Which weakness would you fix first, and why?**

**3. How do you distinguish a confirmed finding from an inference?**

**4. What belongs in the executive summary versus the technical report?**

## Defensive takeaway

Tier administration, managed service accounts, least-privilege ACLs, and directory-change auditing remove this class of path.

> The directory is an LDAP simulation of Active Directory. Kerberos
> concepts are discussed in the chapter; binds use LDAP.
