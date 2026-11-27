# OSINT resources

Status: **reference register for the OSINT and forensics tracks.** These tools
are not vendored, and none is required to complete a lab.

The platform teaches with deterministic, offline evidence. External tools are
listed so instructors can extend a lab or a capstone without turning a hosted
exercise into a live-internet investigation.

| Tool | Licence | What it adds | Platform handling |
|---|---|---|---|
| [ArchiveBox](https://archivebox.io/) | MIT | Capture a dated, hashed snapshot of a public page as evidence | Optional external service; safe to bundle with the MIT notice |
| [OSINT Case](https://osintcase.com/) | GPL-3.0 | Organise subjects, links, timelines, and an evidence vault into a report | Reference only; learner installs it locally |
| [Gephi](https://gephi.org/) | GPL-3.0 | Turn an entity graph into centrality and shortest-path findings | Reference only; learner installs it locally |
| [Cytoscape](https://cytoscape.org/) | LGPL-2.1 (desktop); MIT (Cytoscape.js) | General graph platform for lab, network, metadata, and traffic maps | Reference only; Cytoscape.js for an in-app graph |

The licence, attribution, and redistribution record lives in
`platform/backend/app/data/external-datasets.yaml`; the handling rules are in
[External open datasets](SECURITY-DATASETS.md).

## ArchiveBox

A self-hosted web archiver. It saves a page, its media, and a timestamp so a
finding can be reproduced after the page changes.

- **Good fit:** `osint-1-1-public-footprint` (snapshot your own public
  footprint), `osint-1-4-researcher-self-audit` (attach a dated capture to the
  finding), `osint-2-2-public-homepage` (capture the synthetic target page), and
  web-evidence work in the Digital Forensics track.
- **Classroom rule:** capture only the synthetic or permissioned pages the lab
  provides. Do not point it at a real person, employer, or third-party site.
- **Licensing:** MIT. An institution may run it beside the platform, or bake an
  unmodified copy into an image, provided the MIT notice travels with it.

## OSINT Case

A local investigation workspace: subjects with identifier types, confirmed,
probable, and doubtful links, a timeline, an evidence vault with an audit log,
and PDF or single-file HTML reports.

- **Good fit:** `osint-1-4-researcher-self-audit` (findings, owner, due date,
  verification), `osint-2-1-source-code-intelligence` and
  `osint-2-4-public-profile` (entity and link mapping), and a capstone that
  needs a defensible case file.
- **Classroom rule:** use the fictional sample cases or the learner's own
  synthetic evidence. The tool is local and sends no telemetry.
- **Licensing:** GPL-3.0. Reference-only by default: the learner installs it
  with `pipx` or the distribution package. If an institution bakes it into a
  shared lab image, it must keep the tool unmodified, include
  `THIRD_PARTY_LICENSES/GPL-3.0.txt`, and offer the corresponding source. The
  platform is a separate program, not a derivative work.

## Gephi

A desktop graph-analysis application for link analysis.

- **Good fit:** `osint-1-1-public-footprint` (map the identifiers a stranger can
  correlate), `osint-2-4-public-profile` (confirmed versus probable links), and
  any exercise that asks for centrality or a shortest path across synthetic
  entities. It also suits network and directory graph discussions where the
  data is synthetic.
- **Classroom rule:** export a small synthetic edge list; do not import learner
  records or real personal data.
- **Licensing:** GPL-3.0, with the same source-offer rule as OSINT Case.

## Cytoscape

A general network-analysis and visualization platform. The desktop application
is LGPL-2.1; Cytoscape.js is the MIT-licensed browser library.

- **Good fit:** the same link-analysis labs as Gephi, plus lab and network
  topology diagrams and the OpenGRC metadata and AI-call graphs described in the
  [Ecosystem tooling map](ECOSYSTEM-TOOLING-MAP.md).
- **Classroom rule:** synthetic edge lists only. Do not import learner records,
  prompts, or payloads.
- **Licensing:** LGPL-2.1 for the desktop app, which permits use and linking with
  a notice and source access; Cytoscape.js is MIT and is the preferred option for
  an in-app graph.

## Decision on new labs

No new lab is added in this change. The four tools are strong extensions, but a
hosted lab must stay deterministic and offline, and the GPL tools carry a source
offer if they are baked into an image. The registry and this page let an
instructor extend an existing lab now.

If a lab is added later, the best candidates are:

1. **OSINT-1-5 — Evidence capture.** Capture a synthetic page with ArchiveBox,
   record the hash and timestamp, and attach both to a finding.
2. **OSINT-2-6 — Link analysis.** Given a synthetic entity table, build the
   graph in Gephi and defend a centrality or shortest-path conclusion.
3. **A capstone case file.** Use OSINT Case to organise the evidence a learner
   already collected, then export the report.
