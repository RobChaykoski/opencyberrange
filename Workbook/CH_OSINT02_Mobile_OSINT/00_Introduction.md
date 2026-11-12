# OSINT02: Mobile OSINT

<!-- BEGIN GENERATED CHAPTER POSITION -->
!!! note "Curriculum position"
    **Chapter:** `OSINT02` — Mobile OSINT
    **Prerequisites:** `OSINT01` — OSINT Foundations
    **Recommended next:** `IAM01` — Identity and Access Foundations
<!-- END GENERATED CHAPTER POSITION -->

This short chapter uses the device in your pocket as a separate research and
verification surface. The exercises are deliberately small: each one shows how a
different renderer, client, or public source can expose information that the
other view never shows.

The chapter starts with **The Mobile Build** and **The Public Profile**. The
staff portal serves a different profile to phones than to desktop browsers. The
mobile template contains a contact card that the desktop template does not
render. The public-profile exercise uses the instructor-owned profile as an
authorised OSINT source. The third exercise searches a synthetic Shodan-style
mirror for a verbose service banner.

!!! warning "Authorised, synthetic targets only"
    Every target in this chapter is fictional and isolated. Do not point these
    techniques at a real employer, a real person, or a live third-party service.
    The lesson is about renderer and client differences, not about bypassing
    someone else's access control.

!!! tip "Further reading"
    Trail of Bits' [CTF Field Guide](https://trailofbits.github.io/ctf/index.html)
    is a useful companion for vulnerability discovery, operational tradecraft,
    and toolkit building. It is an external reference, not a copy of this
    chapter.

## What you will practise

- Comparing the same URL from two different clients.
- Reading a server response instead of only the rendered page.
- Using a phone as an out-of-band research device.
- Explaining why a mobile-only field is not a security boundary.
