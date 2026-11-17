# Active Directory: ACL and DACL Abuse

**Track:** Windows · **Level:** 11 · **Time:** 110 minutes · **Difficulty:** advanced

## Scenario

The helpdesk group has an unexpected right over a privileged group. Find the grant, recover the assessment token, and propose the fix.

## What you will practise

- Read a directory ACL and identify dangerous rights
- Explain GenericAll, WriteDACL, and GenericWrite abuse
- Map an ACL edge to a privileged group
- Recommend tiered administration and ACL review

## Work through the exercise

1. Open the exercise from the Windows track, level 11.
2. Work from the scenario; use the lab hints only when you are stuck.
3. Recover the assessment token and write the evidence the exercise asks for.

## Evidence

- The assessment flag.
- A short note that names the weakness and the defensive control.

## Analysis Questions

**1. What is the difference between an ACE, a DACL, and an ACL?**

**2. Why are GenericAll, WriteDACL, and GenericWrite dangerous on a privileged group?**

**3. Which group membership and ACL edge creates the escalation path in this lab?**

**4. How would you audit and tier the excessive right?**

## Defensive takeaway

Tier administration, managed service accounts, least-privilege ACLs, and directory-change auditing remove this class of path.

> The directory is an LDAP simulation of Active Directory. Kerberos
> concepts are discussed in the chapter; binds use LDAP.
