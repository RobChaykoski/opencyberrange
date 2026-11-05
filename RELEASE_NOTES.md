# OpenCyberRange Community / Academic 1.1.3

Edition: **Community / Academic** — supported single-host teaching platform,
lab and workbook improvements, exercise authoring, maintenance, and security.
Professional 2.1 adds analytics, reporting, cohort analysis, competency
evidence, accreditation support, and research exports. Enterprise 3.0 adds HA,
SSO, enterprise reporting, multi-tenant support, LMS integration, and
compliance reporting.

Released: 5 November 2026

OpenCyberRange 1.1.3 adds the learner **Skill DNA** character sheet and
achievement titles to the profile. It keeps the 1.1 deployment and upgrade path.

## Highlights

### Skill DNA

- Five activity-based traits: **Explorer**, **Builder**, **Defender**,
  **Investigator**, and **Leader**.
- A current class and tier: Pathfinder, Artificer, Warden, Seeker, or Commander,
  from Initiate to Master.
- Each trait bar shows a 0–100 score, the evidence behind it, and a next-step
  suggestion.
- A **Career alignment** card maps the current class to the existing
  certification roadmap: OSINT, Web/AppSec, Network/SOC, Forensics/DFIR, or
  general foundations.
- Scores are descriptive, not predictive. They are not a grade or a ranking.

### Achievement titles

- Achievements unlock cosmetic titles with a rarity from common to legendary.
- Learners can equip one unlocked title or clear it to return to the class title.
- Hidden achievement titles show as **Secret title** until unlocked.
- The profile shows the equipped title next to the learner's name and in the
  Cyber DNA class card.
- The title collection is collapsible and available on every profile.

### Profile and accessibility

- The profile stacks the class card, traits, certification card, and title
  collection cleanly on narrow screens.
- Trait bars expose text scores and accessible progress-bar values.
- The sidebar collapse control now has an accessible name and expanded state.
- The metric model is documented in `docs/SKILL-DNA.md`.

### Retained from 1.1.2

- Admin users show last sign-in and support status, role, last-sign-in, and VPN
  filters.
- Rate limiting degrades safely when Redis is unavailable.
- The OpenCyberRange Design Tester skill is available for UI review.

## Upgrade notes

1. Take a database snapshot.
2. Pull the `v1.1.3` tag or the matching release commit.
3. Rebuild the backend and frontend images.
4. Start the stack. The startup migration adds the nullable
   `users.equipped_title` column; existing accounts are unchanged.
5. Verify `GET /api/version` reports `1.1.3`.
6. Open **Profile** and confirm the Cyber DNA section, class card, and title
   collection.

## Supported scope

- Ubuntu 22.04 LTS and Ubuntu 24.04 LTS for the 1.x maintenance line.
- Self-hosted Docker Compose deployments.
- WireGuard learner access, with optional WSTunnel deployments.

## Known limitations

- Skill DNA is a practice summary, not a competency assessment or a prediction
  of job performance.
- The formula is versioned (`2026.11`) and may change as the curriculum grows.
- Titles are cosmetic. They do not grant lab access, change scores, or rank
  learners.
- The transcription PDF does not yet include the Skill DNA section.
- SMTP delivery is best effort. A failed relay never blocks account creation.

## Previous release

See the `v1.1.2` tag for the 1.1.2 release notes.
