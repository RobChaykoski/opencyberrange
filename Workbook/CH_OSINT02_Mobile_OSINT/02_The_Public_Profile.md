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
2. Read the public About section and identify the research marker.
3. Explain why a public marker is not a secret.
4. Submit the marker as the flag.

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

### 2. Read the public About section

Look for the **Research marker** line. The marker is the flag. Copy it exactly.

### 3. Submit the flag

Paste the marker into the exercise page and submit it.

## Analysis Questions

1. What did the public profile tell you about the fictional person's role and
   work?
2. Which fields were intentionally public, and which fields would you avoid
   publishing?
3. Why is a marker in a public profile not a secret?
4. What would you check before posting a public profile in your own name?
5. Why is it safer to practise on a fictional mirror than on a real person's
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
