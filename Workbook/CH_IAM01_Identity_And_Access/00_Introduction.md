# IAM01: Identity and Access Foundations

<!-- BEGIN GENERATED CHAPTER POSITION -->
!!! note "Curriculum position"
    **Chapter:** `IAM01` — Identity and Access Foundations
    **Prerequisites:** `NET00` — Network Foundations
    **Recommended next:** `FOR01` — Memory Forensics
<!-- END GENERATED CHAPTER POSITION -->

## What this course is

Identity is the control plane for almost everything else. If an attacker can
become another user, borrow a session, or reuse a leaver's token, the rest of
the security stack may never see a break-in.

This short course covers three parts of identity and access management:

| Lab | Theme | What you will do |
|---|---|---|
| 1 | Secure authentication | Decode a session cookie, forge an admin session, and explain the fixes |
| 2 | OAuth and OpenID Connect | Send an authorization code to the wrong callback and read a victim profile |
| 3 | Identity lifecycle | Review a directory, find a leaver's active token, and write the offboarding fix |

You do **not** need prior identity experience. You do need to be comfortable
opening a browser's developer tools or running a short `curl` command. Each lab
offers both paths.

## Why this matters

- **For defenders:** session theft, token replay, and dormant accounts are
  common and quiet. They often look like a valid user doing valid things.
- **For builders:** authentication is not one checkbox. It is password storage,
  session handling, MFA, federation, token validation, and offboarding.
- **For everyone:** the person who leaves an organisation is still in the
  directory until someone removes them.

## The three questions to keep asking

1. **Who is making the request?** Authentication answers this.
2. **What are they allowed to do?** Authorization answers this.
3. **How long does that trust last?** Sessions, tokens, and lifecycle answer
   this.

A control that answers one question does not automatically answer the others.
A login form can authenticate a person and still hand them a session that
claims to be an administrator.

## Safety and ethics

- Every account, token, portal, and provider in this course is fictional.
- The targets are isolated. They do not call real identity providers or store
  real credentials.
- The labs are deliberately vulnerable in one taught area. That is the lesson,
  not permission to attack anything else.
- Never use a real session cookie, API token, or password in a lab.
- If you find a real secret outside the lab, stop and tell your instructor.

## How to work

1. **Read** the scenario and the goal.
2. **Observe** the page, cookie, URL, or directory before changing anything.
3. **Change one thing** and record what you sent.
4. **Explain** the result in your own words.
5. **Name the fix** before you submit the flag.

Using hints is allowed. The first hint is a starting point, not a penalty.

## Start here

- [Secure Authentication](01_Secure_Authentication.md)
- [OAuth and OpenID Connect](02_OAuth_OIDC.md)
- [Identity Lifecycle](03_Identity_Lifecycle.md)
- [Chapter Review](04_Chapter_Review.md)
