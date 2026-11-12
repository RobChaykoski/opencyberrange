# Exercise 2.1 -- The Public Profile

**Track:** OSINT · **Difficulty:** Beginner · **Estimated time:** 20 minutes

**Framework alignment:** [MITRE ATT&CK](https://attack.mitre.org/) Reconnaissance
T1593.001 Search Open Websites/Domains: Social Media and T1589.002 Gather Victim
Identity Information: Email Addresses.

## Before You Begin

- This exercise uses the instructor's own public professional profile with
  explicit consent. The marker is intentionally public.
- Only the profile linked in the lab brief is in scope. Do not search another
  person's profile, send connection requests, or collect personal data.
- A phone is recommended. The lab also serves a training mirror for offline
  practice.

## Scenario

The instructor has placed a research marker in the public **About** section of
their own professional profile. Your job is to find it the way a researcher
would: open the public profile, read the public section, and record the marker.

<figure markdown>

![QR code linking to the instructor-owned public profile](img/profile-qr.png)

<figcaption>Scan this code with your phone. The committed QR points at a placeholder URL; regenerate it with the instructor's real public profile URL before class.</figcaption>
</figure>

!!! warning "Authorised target only"
    This is an authorised, instructor-owned profile. Do not reuse the technique
    on another person, a real employer, or a third-party service. Do not collect
    email addresses, phone numbers, connections, or any other personal data.

## Objectives

1. Open the public profile on your phone.
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

### 1. Open the profile on your phone

Scan the QR code above, or open the profile URL from the lab brief. If the live
profile is not reachable, use the training mirror at the lab target:

```text
http://<target>:8080/
```

The training mirror contains the same public About text for offline practice.

### 2. Read the public About section

Look for the **Research marker** line. The marker is the flag. Copy it exactly.

!!! note "Flag case"
    The platform expects the uppercase `OCR{...}` form. If the live profile still
    shows a lowercase `ocr{...}` marker, the instructor should update the public
    text to the uppercase form so the live path and the platform flag match.

### 3. Submit the flag

Paste the marker into the exercise page and submit it.

## Analysis Questions

1. What did the public profile tell you about the person's role and work?
2. Which fields were intentionally public, and which fields would you avoid
   publishing?
3. Why is a marker in a public profile not a secret?
4. What would you check before posting a public profile in your own name?
5. How would you verify that the profile you found is the authorised target and
   not someone with the same name?

## Defensive Takeaways

- Treat every public profile field as permanent and copyable.
- Separate personal and professional presence where possible.
- Review public contact details and remove anything the role does not need.
- Use a unique marker for a training exercise; never put a real credential in a
  public profile.
- If you find sensitive data in a public profile, stop and report it privately
  instead of collecting or sharing it.

## If You Get Stuck

- The QR code may point at a placeholder. Use the training mirror at the lab
  target if the live profile is unavailable.
- The marker is in the About section, not in a connection list or a private
  message.
- If the flag is rejected, copy the marker exactly and confirm the uppercase
  `OCR` prefix.
