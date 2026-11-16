# MITRE ATT&CK Navigator tool

The platform exposes the [MITRE ATT&CK Navigator](https://mitre-attack.github.io/attack-navigator/)
in the same Tools panel as CyberChef and the OT scan assistant.

## What it is for

Navigator is a technique-coverage workspace. Instructors and learners use it to:

- inspect tactics and techniques from the ATT&CK matrix;
- build a coverage layer for a lab, course, or detection review;
- compare what a lab exercises with what a rule or control covers;
- export a layer for a report or peer review.

It is a planning and reporting aid, not an evidence source. A layer is a claim
about coverage; the learner still has to support that claim with lab evidence.

## Access and security

- **Where:** **Tools → ATT&CK** in the sidebar, or **ATT&CK** in the active-lab
  panel.
- **Network:** Navigator is hosted at `mitre-attack.github.io` and needs
  internet access. If the deployment blocks the origin, the panel shows an
  error and offers **Open in new tab**; no lab state is lost.
- **Isolation:** the tool runs in a sandboxed iframe. Its origin is separate
  from the platform. `allow-same-origin` is set only so Navigator can use its
  own browser storage for layers; it does not grant access to the platform
  origin.
- **CSP:** the application `frame-src` allows only the exact Navigator origin
  in addition to the existing self/8443 entries. Do not widen this to `https:`
  or `*`.
- **Data:** do not enter learner names, emails, credentials, or incident data
  into a layer. Use lab IDs, technique IDs, and synthetic case identifiers.
- **Availability:** the tool is external and may change independently. A
  blocked or unavailable Navigator must not block a lab; the lab continues in
  the panel behind the tool drawer.

## Attribution

MITRE ATT&CK Navigator is an Apache-2.0 project by The MITRE Corporation.
ATT&CK is a registered trademark of The MITRE Corporation. The platform links
to the hosted tool and does not copy its source into this repository.

## Verification

- The Tools panel opens the Navigator by allow-listed key; the URL is never
  taken from a route, query string, or learner input.
- The iframe uses the explicit origin in the Content-Security-Policy.
- The panel keeps the existing **Open in new tab** fallback and timeout state.
- No platform session, learner record, or secret is passed to the tool.
