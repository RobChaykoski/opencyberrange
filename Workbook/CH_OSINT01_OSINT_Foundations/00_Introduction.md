# OSINT Foundations

## What Is OSINT?

Open-source intelligence (OSINT) is the practice of collecting and
correlating information from publicly available sources. In security work it
usually means looking at the same surface an outsider can see:

- public web pages and their source
- metadata inside images and documents
- JavaScript, CSS, and build artifacts
- search engines, code hosting, and social profiles
- naming patterns, identifiers, and mistakes people leave behind

OSINT is not guessing. It is a repeatable process: collect, verify, record,
and only then draw a conclusion.

## The Kestrel Ridge Scenario

In this track you are reviewing **Kestrel Ridge**, a fictional defence
analytics company. Kestrel Ridge runs an internal staff site called
**Kestrel Connect** with a dashboard, a people directory, a kudos wall, and
company announcements.

The company has asked for an outside-in review of what its staff site and
public artifacts reveal. You will:

1. map the visible intranet and find a review page that was meant to stay
   private;
2. analyse a public employee badge photo for hidden data;
3. review the site's front-end code and a public repository for leaked
   staging material.

Every target is simulated. The people, badges, and tokens are fictional, and
nothing in this track reaches the real internet.

## Track Map

| Exercise | Focus | Main source |
| --- | --- | --- |
| 1.1 The Public Footprint | Page discovery, `robots.txt`, source comments | Kestrel Connect intranet |
| 1.2 Badge Photo Intelligence | Metadata and LSB steganography | Public badge image |
| 1.3 EXIF Metadata Investigation | EXIF, GPS, device, and author metadata | FinanceCorp evidence image |
| 2.1 The Developer's Trail | Static assets, JavaScript comments, public code | `app.js` and the public repository |
| 2.2 The Public Homepage | Live page metadata and head section | SWOCTS Hub homepage |

## Ground Rules

- Stay inside the simulated target. Do not probe real Kestrel Ridge domains;
  they do not exist.
- Do not upload the badge image to a third-party service. Extract the payload
  locally, or use the lab's browser-based extractor.
- Record the exact source URL and the command that produced each finding.
- If you find something that looks like a real secret, stop and tell your
  instructor. The flags in this track are deliberately fake.

## Access and Privacy

- The image exercise has a browser-only extraction route for learners on a
  Chromebook, tablet, or shared computer without local tools.
- The public-homepage exercise uses a local mirror by default. The live SWOCTS
  page is the organisation's own intentionally published site; do not probe
  unrelated sites.
- Every persona, badge, token, and flag in this track is fictional. Do not use
  real names, real employee data, or real credentials in your notes.
- The public-repository bonus is a deliberately planted teaching artifact. If
  you find a real secret in any repository, stop and report it privately.

## Flag Format

Flags look like this:

```text
OCR{example_text}
```

They are case sensitive. Submit the whole value, including `OCR{` and `}`.
