# Active Directory: AD CS Abuse

**Track:** Windows · **Level:** 11 · **Time:** 110 minutes · **Difficulty:** advanced

## Scenario

The LAB domain publishes a certificate template with an over-broad enrolment right. Find the template, recover the token, and harden it.

## What you will practise

- Explain how misconfigured certificate templates enable escalation
- Identify an enrollee-supplied subject and client-authentication EKU
- Assess the certificate-based attack path
- Recommend template hardening and issuance approval

## Work through the exercise

1. Open the exercise from the Windows track, level 11.
2. Work from the scenario; use the lab hints only when you are stuck.
3. Recover the assessment token and write the evidence the exercise asks for.

## Evidence

- The assessment flag.
- A short note that names the weakness and the defensive control.

## Analysis Questions

**1. Which two certificate-template settings combine into the dangerous path?**

**2. Why does an enrollee-supplied subject matter for client authentication?**

**3. What approval and enrolment controls harden the template?**

**4. Which events detect unexpected certificate issuance?**

## Defensive takeaway

Tier administration, managed service accounts, least-privilege ACLs, and directory-change auditing remove this class of path.

> The directory is an LDAP simulation of Active Directory. Kerberos
> concepts are discussed in the chapter; binds use LDAP.
