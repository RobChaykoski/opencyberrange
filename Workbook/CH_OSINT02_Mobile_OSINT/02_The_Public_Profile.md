# Exercise 2.1 -- The Public Profile

**Track:** OSINT · **Difficulty:** Beginner · **Estimated time:** 20 minutes

**Framework alignment:** [MITRE ATT&CK](https://attack.mitre.org/) Reconnaissance
T1593.001 Search Open Websites/Domains: Social Media.

## Before You Begin

- This exercise uses a **fictional** public profile. Riley Chen and Northstar
  Community Cloud are invented for the lab; they are not real people or
  organisations.
- The assessed path is the local mirror served by the lab. There is no live
  social-media account, no QR code, and no phone requirement.
- Do not search for a real person, send connection requests, or collect personal
  data. The lab records no free-text input.

## Scenario

A fictional community cloud engineer has a public profile. A research marker is
in the public **About** section. Your job is to find it the way a researcher
would: read the public page, record the marker, and explain why a public field is
not a secret.

!!! warning "Fictional target only"
    Riley Chen and Northstar Community Cloud are training personas. Do not reuse
    the technique on a real person, employer, or third-party service. Do not
    collect email addresses, phone numbers, connections, or any other personal
    data.

## Objectives

1. Open the local profile mirror.
2. Inventory the visible fields and the less-obvious fields.
3. Open the conference page and correlate the identifier.
4. Map each field to the exposure it enables.
5. Explain why a public marker is not a secret.
6. Submit the marker as the flag.

## Background: public profiles are OSINT

A public professional profile is a public website. The person chose to publish
it, but that does not mean every field is safe to expose. Public profiles can
reveal role, employer, team, technology interests, contact routes, and the
language a person uses about their work.

The marker in this exercise is a training flag, not real sensitive data. The
defensive lesson is about the habit: review what you publish, separate personal
and professional presence, and assume a public field can be copied, indexed, and
retained.

## Walkthrough

### 1. Open the local mirror

Use the lab target shown in the exercise panel:

```text
http://<target>:8080/
```

The mirror is offline and contains only fictional text. It does not contact a
social network.

### 2. Build the field inventory

Do not stop at the About section. Separate the obvious fields from the
less-obvious ones:

| Visible | Less obvious |
|---|---|
| Job title | Conference dates |
| Company | Employer naming pattern in the email domain |
| Skills and technologies | Reused handle |
| Public email | Timezone |
| | Conference travel window |

### 3. Open the conference page

Follow the conference link or open:

```text
/talk
```

The page repeats the handle and adds a session, a location, and travel dates.
That is a second public source. It can confirm the identifier and extend the
timeline.

### 4. Correlate the fields

Ask: **what information could be correlated?**

| Finding | Correlates with | What it enables |
|---|---|---|
| `@rileybuilds` | Profile and conference page | Links the same person across sources; a starting point for other accounts |
| `riley.chen@northstar-community.example` | Employer domain | Reveals the naming pattern and a phishing or account-discovery target |
| Conference dates and timezone | Travel note | Suggests an absence window and a location |
| Kubernetes, Terraform, Grafana | Role and team | Narrows targeted vulnerability research |

A single field is a fact. Two correlated fields are an exposure.

### 5. Complete the exposure map

| Field | Source | What it enables | Risk | Action |
|---|---|---|---|---|
| Job title | Profile | Role targeting | Low | Keep; the role needs it |
| Public email | Profile | Phishing, account discovery | Medium | Replace with a role address or a contact form |
| Reused handle | Profile + conference | Cross-source correlation | High | Use a unique handle or separate identities |
| Conference dates | Conference page | Absence window, physical context | Medium | Publish only the city or a general availability note |
| Technologies | Profile | Targeted research | Low | Keep high-level; remove exact versions |

Risk is a judgement. High means direct correlation, location, or
account-recovery exposure. Low means limited context on its own.

### 6. Submit the flag

Copy the marker exactly as it appears and submit it on the exercise page.

## Concept Check

??? question "Which field enables the most cross-source correlation?"
    A. Job title.  
    B. Reused handle.  
    C. Company name.  
    D. Skills list.

    **Correct answer: B.** A reused handle links the profile, the conference
    page, and any other public account that uses it. The job title and company
    are context; the handle is the correlation key.

## Analysis Questions

1. What did the public profile tell you about the fictional person's role and
   work?
2. Which fields were intentionally public, and which fields would you avoid
   publishing?
3. What information could be correlated across the profile and the conference
   page?
4. Which field enables the most cross-source correlation, and why?
5. Which field is the highest risk, and what would you remove first?
6. Why is a marker in a public profile not a secret?
7. Why is it safer to practise on a fictional mirror than on a real person's
   profile?

## Defensive Takeaways

- Treat every public profile field as permanent and copyable.
- Separate personal and professional presence where possible.
- Review public contact details and remove anything the role does not need.
- Use a unique marker for a training exercise; never put a real credential in a
  public profile.
- If you find sensitive data in a public profile, stop and report it privately
  instead of collecting or sharing it.

## If You Get Stuck

- The lab is offline by design. Use the mirror at the lab target; there is no
  live profile to open.
- The marker is in the About section, not in a connection list or a private
  message.
- If the flag is rejected, copy the marker exactly and confirm the uppercase
  `OCR` prefix.
