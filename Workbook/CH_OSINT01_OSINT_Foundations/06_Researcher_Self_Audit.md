# Exercise 1.4: The Researcher's Mirror

## Before You Begin

- [ ] Launched the exercise and opened the lab browser or a terminal
- [ ] `selfaudit.lab` resolves to the target shown in the exercise panel
- [ ] You can reach `http://selfaudit.lab:8080`
- [ ] You understand that every person and record in this lab is fictional

## Scenario

Dr. Maya Chen is a fictional coastal-resilience researcher preparing for a
conference. A colleague searched her name and found her public email, an old
forum handle, and a photo with location metadata in the same afternoon. Maya
has asked for a pre-trip privacy review.

The **Researcher Self-Audit Mirror** reconstructs what a stranger can see. It is
a safe, offline model of a public profile, a breach record, a published photo,
and a reviewer's ticket. No page is connected to the real internet, and no
detail belongs to a real person.

Your task is not to "find everything." It is to decide what a professional
contact actually needs, what creates unnecessary correlation or physical risk,
and what Maya should change before she travels.

## Your Objectives

- Search the name, handle, and public email the way an outsider would
- Compare the public profile with the breach record and photo metadata
- Identify which details are necessary and which are over-sharing
- Write a finding with an action, an owner, and a verification step
- Recover the flag from the review ticket's source

## Background: A Self-Audit Is a Review, Not a Scavenger Hunt

A useful self-audit answers four questions:

1. **What is public?** Search results, profiles, forum posts, images, and old
   pages that still resolve.
2. **What does it correlate?** A reused handle or public email can connect
   accounts that were meant to stay separate.
3. **What does it enable?** Office room numbers and travel dates support
   physical tracking. Metadata can confirm a device, a time, and a place.
4. **What will change?** Each finding needs an action, an owner, and a date when
   someone checks that the action actually happened.

A breach record is a verification lead, not a password. Never try to use a
credential from a breach record, and never test these techniques against a real
person. The lab uses synthetic records so you can practise the reasoning.

## Walkthrough

### Step 1: Start with the mirror

Open `http://selfaudit.lab:8080` in the lab browser. Read the overview, then open
the search mirror.

Try:

- `Maya Chen`
- `mayachen_lab`
- `maya.chen.research@example.edu`

The results are fixed teaching records. Confirm an identifier on the page it
points to instead of treating the result title as proof.

### Step 2: Read the public profile

Open the profile result. Make a three-column list:

| Field | Necessary for professional contact? | Why |
|---|---|---|
| Public email |  |  |
| Lab handle |  |  |
| Office room |  |  |
| Conference dates |  |  |
| ORCID / GitHub |  |  |

Do not fill in a real person's details. This table is about Maya.

### Step 3: Compare the breach record

Open the **Breach record** page. It shows a synthetic 2024 archive with the
public email and the same handle. Record:

- the identifier that was exposed;
- the other public page where the identifier appears;
- one account-recovery or session action Maya should take.

### Step 4: Inspect the photo metadata

Open **Photo metadata**. The record names a camera, a capture time, a synthetic
GPS placeholder, and an internal building. Ask:

- Which fields are needed to publish the photo?
- Which fields should be stripped before publishing?
- Is stripping enough if the original file remains in a public share?

### Step 5: Follow the reviewer's trail

A public page can carry a note that is invisible in the rendered view. Inspect
the profile source for a reviewer path:

```bash
curl -s http://selfaudit.lab:8080/profile/maya-chen | grep -o '/review/[A-Z0-9-]*'
```

Open the review ticket and read its source. The flag is in an HTML comment:

```bash
curl -s http://selfaudit.lab:8080/review/OSINT-SELF-001 | grep -o 'OCR{[^}]*}'
```

### Step 6: Write the remediation note

Complete this table in your own words:

| Finding | Risk | Evidence | Action | Owner | Due | Verified |
|---|---|---|---|---|---|---|
| Public email | Low |  |  |  |  |  |
| Reused handle | High |  |  |  |  |  |
| Office and travel detail | Medium |  |  |  |  |  |
| Photo metadata | High |  |  |  |  |  |
| Stale forum page | Medium |  |  |  |  |  |

Risk is a judgement about impact. Use **Low** for limited context, **Medium** for
useful correlation, and **High** for direct location, contact, or
account-recovery exposure.

Then calculate the exposure score:

| Signal | Weight | Present? | Score |
|---|---:|---|---:|
| Public email | +2 |  |  |
| Handle reuse | +3 |  |  |
| Travel schedule | +3 |  |  |
| Photo metadata | +4 |  |  |
| **Total** |  |  |  |

Use the score to order the remediation. The score supports the risk rating; it
does not replace it.

A useful action is specific: "replace the public personal address with a role
address and remove the old address from the profile" is testable. "Be more
careful" is not. A finding is not closed until the verification date is recorded.

### Step 7: Check the search results for noise

Real OSINT results contain false leads. Look for the result for a different Maya
Chen at a community school. It is a different person, with no research
affiliation. Do not merge it into the researcher's record.

Also look for the cached duplicate of the institute profile. It points at the
same page. Record the canonical URL once, not twice.

## Evidence to Capture

- One screenshot or text capture of the search result page.
- One false lead or duplicate you rejected, with the reason.
- One profile field you would remove and why.
- One breach-record action you would take.
- One metadata field you would strip.
- The risk rating and exposure score.
- The remediation table with an owner, due date, and verification date.
- The flag from the review ticket source.

## Defensive Takeaways

- Publish the minimum contact detail a role requires.
- Keep personal and professional identifiers separate.
- Strip metadata before publishing images, and keep originals out of public
  shares.
- Retire stale profiles and old links; a page that still resolves is still
  public.
- After a breach notice, review sessions, MFA, and password reuse across every
  account that shares the identifier.
- Verify the fix. A removal request is not a removal.

## Checkpoint

1. Why is a public email more sensitive when the same handle appears on a forum?
2. What is the difference between a search result and confirmed evidence?
3. Which photo metadata fields would you remove, and which would you keep?
4. What makes a remediation action testable?
5. Why should you never test this workflow against a real person?

## Flag

Submit the flag from the review ticket source. It begins with `OCR{`.
