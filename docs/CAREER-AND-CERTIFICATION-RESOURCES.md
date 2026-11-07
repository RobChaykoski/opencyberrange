# Career and certification resources

Status: **Active curriculum guidance**
Edition: **Community / Academic 1.1** (inherited by Professional 2.1.4 and
Enterprise 3.0)
Owner: Curriculum

This page records the external references that shape career guidance in the
platform. It is guidance, not an official mapping, and not a promise that a
learner will pass a certification or get a role.

## References

| Reference | What it informs | Link |
|---|---|---|
| **Security Certification Roadmap** by Paul Jerimy | Vendor certification families, entry-to-advanced progression, and role paths | <https://pauljerimy.com/security-certification-roadmap/> |
| **CISO MindMap 2026** by Rafeeq Rehman | The breadth of a security leadership role: operations, IAM, governance, risk, architecture, cloud, AI, OT, data, and team management | <https://rafeeqrehman.com/wp-content/uploads/2026/04/CISO-MindMap-2026.pdf> |
| **SWOCTS Resources** | Free training platforms, certification programs, community, and academic resources | <https://swocts.com/resources> |
| **MalOps Peaky Blinders challenge** | An external malware-analysis practice reference and a different platform's challenge format. Useful for showing a route from broader security practice into malware analysis. | <https://malops.io/challenges/peakyblinders> |
| **Hack The Box Academy** | External hands-on labs and structured learning paths for offensive, defensive, and general security practice. | <https://academy.hackthebox.com/> |
| **PacketLabs** | External penetration-testing and security-research reference material. | <https://www.packetlabs.net/> |
| **Cisco Networking Academy** | External networking and cybersecurity courses, useful for learners building foundations. | <https://www.netacad.com/> |

These are third-party works. Link to them; do not copy their content, charts,
challenge text, or course material into the platform. Attribute the author and
keep the link current. The platform links are references for exploration only.

## Development career profiles

The development seed creates three demonstration learners and exports a
readable dossier for each:

- `demo_career_ready` — fairly well versed across offensive, defensive, and
  investigative exercises.
- `demo_career_starting` — just starting, with a small number of beginner
  completions.
- `demo_career_changer` — changing career direction, with evidence gathering in
  OSINT, forensics, network analysis, and adjacent offensive work.

Run inside the backend container:

```bash
python -m app.scripts.seed_career_profiles --output-dir /app/data/career_profiles
python -m app.scripts.export_career_profiles --output-dir /app/data/career_profiles
```

The seed is development-only, idempotent for its own demo users, and leaves real
learner records alone. It generates a one-time demo password and writes it to
`career_demo_credentials.txt` with mode `0600` beside the export directory; set
`CAREER_DEMO_PASSWORD` before seeding if you need a known workshop password.
Each export contains a JSON dossier, a Markdown dossier,
and a self-contained printable HTML page. The dossier combines Cyber DNA,
learning evidence, course participation, reflection questions, and the external
references above. It is a conversation aid, not a job prediction or ranking.

The signed-in learner can also request the same dossier through the authenticated
`/api/profile/career-dossier`, `/api/profile/career-dossier.md`, and
`/api/profile/career-dossier.html` endpoints. They return only that learner's own
data, send `Cache-Control: no-store`, HTML-escape all values, and write an audit
record. They do not expose staff-only fields or another learner's activity.

## How the references are used

### Exercise and track guidance

Each track shows a compact **Certification pathways** panel with three steps:

- **Start here** — entry-level or prerequisite certifications.
- **Build on it** — the certifications that match the track's core work.
- **Go further** — advanced or specialist certifications.

The panel also lists the roles the track can lead toward and links to all three
references. The panel is in `platform/frontend/src/data/certificationPaths.js`
and `platform/frontend/src/views/TrackDetail.vue`.

### CISO MindMap: beyond the first certification

The CISO MindMap is deliberately broader than a certification path. It is used
to keep the curriculum from training only for the first job. The map's major
branches inform future lab and course design:

| Branch | Curriculum implication |
|---|---|
| Security operations, threat detection, incident response | Keep SOC, DFIR, detection engineering, and tabletop exercises in the core |
| Identity and access management | Add SSO, MFA, PAM, federation, and identity lifecycle labs |
| Governance, risk, and compliance | Add policy, risk register, audit evidence, privacy, and regulatory mapping |
| Security architecture | Add segmentation, zero trust, cloud, SASE/SSE, and resilience design |
| Cloud and SaaS | Add CSPM, cloud identity, containers, serverless, and shared-responsibility labs |
| AI security and AI use | Add LLM/agent risk, RAG and vector data, model supply chain, and AI governance |
| OT, IoT, and physical convergence | Add ICS/SCADA, device identity, and safety-aware exercises |
| Data-centric security | Add data discovery, classification, DLP, retention, and encryption |
| Team and business leadership | Add communication, metrics, budgeting, business cases, and board-ready reporting |
| Legal, privacy, and third-party risk | Add contracts, vendor risk, breach notification, and investigation handling |

This does not turn every track into a CISO course. It keeps advanced learners
aware of the wider system their technical work sits inside.

### SWOCTS resources

The SWOCTS resources page provides free training and community entry points that
complement the platform:

- free training from The Linux Foundation, Cisco NetAcad, Fortinet, Splunk,
  PortSwigger, TryHackMe, KC7 Cyber, CyLab Security Academy, and OverTheWire;
- certification programs including ISC2 Certified in Cybersecurity, IBM
  SkillsBuild, Cato Networks SASE, Palo Alto Networks Beacon, and Professor
  Messer's Security+ course;
- community and academic resources from the Canadian Cyber Security Centre and
  the SWOCTS LinkedIn community.

Use these as **next-step** links, not as replacements for the platform's own
labs. The platform remains the guided practice environment.

## Design implications for future labs

1. **Career context is part of the brief.** Each track should answer "what work
   does this look like?" and "what could I do next?" without turning the lab into
   an advertisement.
2. **Competency first, certification second.** Map labs to observable
   competencies. Certifications are signals, not the curriculum.
3. **Add breadth, not noise.** Use the CISO MindMap to identify missing domains
   (IAM, GRC, cloud, AI, OT, data, leadership) rather than adding certificates
   to every lab.
4. **Keep the learner's data private.** Career guidance is general. Do not infer
   a learner's career potential or rank them.
5. **Review annually.** Vendor certification names and requirements change; the
   CISO MindMap is refreshed annually; SWOCTS resources change more often.

## Maintenance

- Review certification names and links at least annually.
- Review the CISO MindMap when a new edition is published.
- Review SWOCTS resources quarterly or when the page changes.
- Update the track mapping when a track is added or renamed.
- Record the review date in the release notes.

## Attribution and disclaimers

- **Security Certification Roadmap** — Paul Jerimy. The roadmap is linked with
  attribution; its full chart is not reproduced here.
- **CISO MindMap 2026** — Rafeeq Rehman. The map is linked with attribution; the
  platform summarizes only the branches that affect curriculum design.
- **SWOCTS Resources** — SWOCTS Hub. Links are provided for learner convenience.

Vendor certifications, prices, prerequisites, and renewal rules change. Verify
them with the vendor before relying on them.
