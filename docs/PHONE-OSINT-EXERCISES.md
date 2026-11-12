# Phone OSINT exercises

Status: **All three exercises implemented.**

Audience: OSINT learners and instructors.

Related: [Career Atlas and Momentum](CAREER-ATLAS-AND-MOMENTUM.md),
[Educational provenance](EDUCATIONAL-PROVENANCE.md), and
[MITRE ATT&CK](https://attack.mitre.org/).

## Purpose

These exercises use the learner's phone as a **separate research surface**. The
laptop stays on the lab target; the phone is used to compare renderers, read a
public profile, or search a public-data mirror. The goal is to teach:

- out-of-band research and OPSEC;
- renderer and client-class differences;
- public-data exposure;
- why "hidden" content is not the same as authorised content.

## Further reading

- [Trail of Bits CTF Field Guide](https://trailofbits.github.io/ctf/index.html) —
  use the vulnerability discovery, operational tradecraft, and toolkit chapters
  as pre-reading. The guide is an external reference and is not copied into the
  platform.

## Safety and authorisation

- All targets are fictional and isolated, except the instructor-owned public
  profile in Exercise 2.
- Exercise 2 uses the instructor's own profile with explicit consent. The flag is
  intentionally public. Do not search another person's profile, send connection
  requests, or collect personal data.
- Exercise 3 uses a **synthetic Shodan mirror**. Do not query real Shodan for
  third-party hosts. Real Shodan queries can expose real systems, are not
  reproducible for a class, and require a key and terms review.
- Never collect, store, or share real personal data found during an exercise.
- If a learner is not comfortable using a phone or a public social platform, use
  the training mirror or the terminal path.

## Exercise 1 -- The Mobile Build (implemented)

**Lab:** `platform/labs/OSINT/osint-2-3-responsive-leak`
**Workbook:** `Workbook/CH_OSINT02_Mobile_OSINT/01_The_Mobile_Build.md`

The staff portal serves a different profile to phones than to desktop browsers.
The mobile template includes a contact card that the desktop template does not
render. The learner opens the profile on the phone, compares the two responses,
and recovers the flag from the mobile-only card.

**ATT&CK:** T1593 Search Open Websites/Domains; T1592.004 Gather Victim Host
Information: Client Configurations.

**Defensive lesson:** authorise every request before choosing a template. Return
only the fields the authenticated user may see, regardless of the client class.

## Exercise 2 -- The Public Profile (implemented)

**Lab:** `platform/labs/OSINT/osint-2-4-public-profile`
**Workbook:** `Workbook/CH_OSINT02_Mobile_OSINT/02_The_Public_Profile.md`

The instructor places a marker in the **About** section of their own public
LinkedIn profile. The learner uses the phone to open the profile and find the
marker. A training mirror of the same text is served by the lab for offline
practice and automated validation. The lab's `PROFILE_URL` environment variable
is a placeholder until the instructor sets the real public profile URL; the QR
code in the workbook must be regenerated for the same URL.

**Flag:** `OCR{linkedIn_0s1nt_m4st3r_2026}`

!!! note "Flag case"
    The platform validator expects `OCR{...}`. If the LinkedIn About currently
    contains `ocr{...}`, update the public text to the uppercase form so the live
    path and the platform flag match exactly.

**Setup:**

1. Put the uppercase marker in the instructor's public LinkedIn About section.
2. Set `PROFILE_URL` in the lab environment to the public profile URL.
3. Generate the QR code for the phone with
   `python scripts/generate-osint-qr.py --url "<profile-url>" --out <lab>/assets/profile-qr.png`.
4. Confirm the profile is public and contains no other personal data that the
   exercise does not need.

**ATT&CK:** T1593.001 Search Open Websites/Domains: Social Media; T1589.002
Gather Victim Identity Information: Email Addresses (only if the public profile
shows one; do not collect it).

**Defensive lesson:** public profiles are an OSINT source. Minimise what is
public, review it periodically, and separate personal and professional presence.

## Exercise 3 -- The Public Banner (implemented)

**Lab:** `platform/labs/OSINT/osint-2-5-public-banner`
**Workbook:** `Workbook/CH_OSINT02_Mobile_OSINT/03_The_Public_Banner.md`

The learner uses a **synthetic Shodan mirror** on the lab target. The mirror
supports a small subset of Shodan-style filters (`org`, `hostname`, `port`,
`product`, `country`) and returns fictional hosts. One host exposes a verbose
banner with a marker.

Example queries:

```text
org:"Kestrel Ridge"
product:nginx
port:8080
hostname:build.kestrel-ridge.example
```

**ATT&CK:** T1596.005 Search Open Technical Databases: Scan Databases; T1590.005
Gather Victim Network Information: IP Addresses.

**Defensive lesson:** public scan data exposes banners, ports, and product
versions. Reduce the banner, remove default pages, and monitor your own public
footprint.

**Why synthetic:** real Shodan queries can expose third-party hosts, are not
reproducible, and require a key and terms review. A synthetic mirror gives the
same query practice without touching a real system. If a programme wants a real
Shodan variant, restrict it to the organisation's own domains, use a
teacher-provided API key, and record the acceptable-use decision.

## Implementation plan

1. Add a `phone_osint` lab mode to `platform/labs/OSINT/_shared/app.py` for the
   public-profile mirror and the synthetic Shodan search.
2. Add the two lab directories with `lab.yaml` and `docker-compose.yml`.
3. Add the workbook chapters and the `mkdocs-osint.yml` nav entries.
4. Add the QR generator and a test that the lab page includes the QR and the
   profile URL, but not the flag in the desktop response.
5. Update `curriculum-manifest.yaml` with the new chapter and exercise counts.
6. Run `validate-lab.py`, `check-doc-assets.py`, `check-links.py --mkdocs`, and
   the security delta review.
7. Capture the real screenshots on the development host.
