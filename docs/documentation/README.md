# Documentation governance

This is the entry point for the documentation set. The
[documentation index](../README.md) is the reader-facing map; this page is the
maintainer-facing one.

The set is grouped by the decision a reader is trying to make, using the
project's bounded contexts and the NIST Cybersecurity Framework 2.0 functions.
Every Markdown file under `docs/` belongs to exactly one group in
[`documentation-map.yaml`](documentation-map.yaml).

## Groups

| Group | Use it for | NIST CSF 2.0 |
|---|---|---|
| [Governance, risk and assurance](groups/governance.md) | Policy, control mapping, risk, privacy, retention, procurement, audits, reviews | GV |
| [Architecture, design and decisions](groups/architecture.md) | System and data architecture, interfaces, schemas, ADRs | ID, PR |
| [Operations and service management](groups/operations.md) | Deployment, runbooks, backup and restore, availability, database integrity, upgrades | PR, RC |
| [Security engineering and assurance](groups/security.md) | Authentication, authorization, tenancy, consent, scanning, security evidence | PR, DE, RS |
| [Curriculum, learning and assessment](groups/curriculum.md) | Learning design, tracks, labs, competencies, assessment, analytics, transcripts | PR.AT |
| [Integrations and ecosystem](groups/integrations.md) | SSO, LMS/LTI, OpenGRC, reporting boundaries, evidence exchange | GV.SC, ID.IM |
| [Product, releases and change](groups/product.md) | Scope, releases, deliverables, editions, roadmaps, counts, handoffs | GV |
| [Research, pilots and community](groups/research.md) | Pilots, studies, community events, proposals not yet committed | GV, ID.IM |
| [Archive](groups/archive.md) | Superseded plans and historical records | GV |
| [Documentation system](groups/documentation.md) | This standard, the form, the register, and generated indexes | GV |

## Review workflow

1. Pick a document from a group page or the register.
2. Open [the review form](DOCUMENT-REVIEW-FORM.md) or the GitHub issue form
   `.github/ISSUE_TEMPLATE/documentation-review.yml`.
3. Acknowledge the requirement it serves and record the evidence.
4. Give a subjective relevance score (1-5) and a weighted quality score (0-100).
5. Set the cadence, last review, next review, reviewer, and approver.
6. Confirm the labels, classification, storage, and retention.
7. Record the NIST SP 800-53A method (examine, interview, test) and findings.
8. Update [`documentation-map.yaml`](documentation-map.yaml), then run
   `python scripts/documentation_map.py --write` and
   `python scripts/documentation_map.py --check`.

## Standard and labels

The full rules are in the [documentation standard](DOCUMENTATION-STANDARDS.md):

- the ten groups and their NIST CSF and SP 800-53 anchors;
- the label set (`doc_type`, `audience`, `classification`, `lifecycle`,
  `sensitivity`, `review.status`, `storage.retention`);
- the relevance rubric (1-5) and the quality rubric (0-100);
- review cadence and trigger-based reviews;
- storage, publication, retention classes, and handling rules;
- roles, measures, and exceptions.

Classification follows [Data classification](../DATA-CLASSIFICATION.md).
Retention follows [Retention policies](../RETENTION-POLICIES.md). Neither is
replaced by this standard.

## Commands

```bash
python scripts/documentation_map.py --check
python scripts/documentation_map.py --check --fail-on-overdue
python scripts/documentation_map.py --write
python scripts/check-links.py --mkdocs
```

## Current state

The register starts honest: documents are labelled by group and type, and the
review status is `unreviewed` until a reviewer completes the form. The
[group pages](groups/governance.md) show the queue, the score, and the next
review date for each document.
