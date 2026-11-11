# Exercise 3.2: Media Provenance: Is It Real?

## Before You Begin

- [ ] You have completed **MFA and the Lost Phone**
- [ ] You have the exercise panel open
- [ ] You can open the archive and the provenance record
- [ ] You will use only the fictional images in this lab
- [ ] You will not upload a real person's image to a third-party service

!!! note "Source first, pixels second"
    Metadata is often stripped on upload, and a visual artefact can have an
    ordinary explanation. The stronger questions are: who published it first,
    what does the provenance record say, and does anything independent support
    the claim?

## Scenario

You are volunteering at a community newsroom. Two images were submitted for the
same weekend: a staff photo from a river cleanup and an anonymous lantern
festival picture with a dramatic caption.

The editor wants a decision, not a vibe. Check the source, the provenance
record, the metadata, and whether anything independent supports the claim. Then
request a verification token for the item you can support.

## Background

Use the checks in this order:

| Check | Question |
|---|---|
| **1. Source** | Who published it first, and is that account verifiable? |
| **2. Provenance** | Is there an original file, hash, camera record, or signed provenance data? |
| **3. Corroboration** | Does an independent record, venue log, or second photographer support it? |
| **4. Clues** | Are there visual artefacts? What else could explain them? |

A synthetic image can look perfect. A real image can look strange after
compression or editing. That is why clues come last.

## Walkthrough

### Step 1: Open the archive

Open the exercise page and choose **Open the archive**. Two items are listed
with captions, media, source notes, and provenance records.

### Step 2: Compare the sources

Open each item's **Source note**:

- The river cleanup came from the community centre staff page, with a venue log
  and a second photographer.
- The lantern festival arrived anonymously. There is no original upload and no
  independent report.

### Step 3: Read the provenance data

Open `/provenance.json` or each item's provenance record. Compare:

- source;
- upload time;
- camera and software;
- GPS;
- corroboration;
- SHA-256.

One record names a synthetic-media tool and has no camera or GPS. That is a
strong signal, but it is not the only evidence. The source and corroboration
point the same way.

### Step 4: Check the claim, not just the file

The staff photo supports the claim that the cleanup happened and that a known
photographer submitted the image. The anonymous image supports only the claim
that someone uploaded a file.

### Step 5: Request verification

Open:

```text
http://provenance.lab:8080/verify?id=river-cleanup
```

The supported item returns the training token. The anonymous item returns 403
because it has no independent provenance. Copy the `OCR{...}` value into the
flag box.

### Step 6: Write the evidence brief

Use three lines:

```text
What the evidence supports:
What it does not prove:
What I would do next:
```

A strong answer names the source and corroboration, and states that the
evidence does not prove every detail of the event.

## What Just Happened?

- The synthetic item had a polished image but no independent provenance.
- The supported item had a known source, a hash, a venue log, and a second
  photographer.
- Metadata helped, but it was not the whole decision.
- Visual clues are prompts to check provenance, not verdicts.
- The evidence brief stated its limits instead of overclaiming.

## The Fixes

| Problem | Fix |
|---|---|
| Anonymous upload with no original | Require a source and an original file before publishing |
| Metadata-only decision | Combine source, provenance, corroboration, and clues |
| No provenance record | Capture a hash, source, upload time, and reviewer |
| Visual artefacts treated as proof | Use them as prompts to investigate, not as a verdict |
| Synthetic media of a real person | Require consent, legal review, and clear labelling |

## Analysis Questions

**1. Why is source usually stronger than a visual clue?**

**2. What can metadata prove? What can it not prove?**

**3. What counts as independent corroboration?**

**4. Why can a real photo look artificial after compression or editing?**

**5. What should an evidence brief say when the evidence is inconclusive?**

**6. What would you do if the image depicted a real person in a compromising
context?**

## Accessibility

- The archive and provenance records are text and SVG images with alt text.
- You can complete the exercise with a keyboard and copy/paste.
- If an image does not render, open its media URL directly.
- Do not use a real reverse-image service with a real person's image; the lab
  source notes are the simulated equivalent.
