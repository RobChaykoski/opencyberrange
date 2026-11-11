# Educational material provenance

Status: **Current for the 2.6.0 line**
Last reviewed: **11 November 2026**

This page records where the OpenCyberRange / SWOCTS Cyber Range educational
material comes from, how it is reviewed, and what its limits are. It covers
workbook chapters, lab scenarios, hints, quizzes, framework mappings, and the
generated curriculum pages.

## Ownership and attribution

- The platform and the updated curriculum build are maintained by **Robert
  Chaykoski** for SWOCTS.
- The original Open Cyber Range (OCR-Lite) project was designed and built by
  **Lewis Heuermann** and published at
  [syntaxoverride/opencyberrange](https://github.com/syntaxoverride/opencyberrange).
  This repository is an independent updated build, not an official upstream
  release, and is not endorsed by the original author.
- The original copyright and the PolyForm Noncommercial 1.0.0 licence remain in
  force. See [LICENSE](../LICENSE) and [BUILD_NOTICE.md](../BUILD_NOTICE.md).
- SWOCTS brand assets are owned by SWOCTS and are not covered by the software
  licence. See [BRANDING.md](../BRANDING.md).

## Source of truth

| Material | Authoritative file | Notes |
|---|---|---|
| Chapter order, display IDs, prerequisites | `curriculum-manifest.yaml` | Drives generated curriculum pages and chapter labels in the platform. |
| Competency and framework references | `curriculum-frameworks.yaml` | One primary competency and one or two framework references per lab. |
| Shared terminology | `curriculum-glossary.yaml` | Defines terms at first use; generated into the terminology page. |
| Lab behaviour, targets, flags, hints | `platform/labs/<Track>/<slug>/lab.yaml` | The runnable contract. Flags are stored as hashes in the database. |
| Workbook chapters | `Workbook/CH_*/` | Learner-facing explanation, walkthrough, evidence, and review. |
| Generated curriculum, terminology, and framework pages | `CURRICULUM.md`, `TERMINOLOGY.md`, `FRAMEWORKS.md` | Do not hand-edit; regenerate with the scripts below. |

## Per-lab provenance fields

Every lab carries review metadata in `lab.yaml`:

| Field | Meaning |
|---|---|
| `owner` | The curriculum owner accountable for the content. |
| `content_version` | The content revision; it changes when the walkthrough or target contract changes. |
| `reviewed_at` | The date of the most recent review. |
| `review_status` | What was actually verified, for example automated static proof or live walkthrough. |
| `difficulty_evidence` | The evidence behind the declared difficulty, including its quality and sample size. |
| `mapped_skills` | The internal skill categories used by analytics and reporting. |
| `mitre_attack` | The ATT&CK tactic and technique used for defensive context, not a claim of coverage. |

A `provisional` difficulty or a review status that says a live walkthrough is
pending is deliberate. It means the content has passed automated validation but
has not yet been demonstrated end to end in a live session by a reviewer.

## Review and validation workflow

1. The author updates the lab contract and the workbook together.
2. `python scripts/validate-lab.py <lab-directory>` checks the manifest and
   target contract.
3. `python scripts/generate-workbook-coverage.py` confirms that workbook pages
   and lab references agree.
4. `python scripts/validate-framework-map.py` checks chapter IDs and framework
   references against the manifest and registry.
5. The supply-chain lock is refreshed and `python scripts/supply_chain.py
   --check` verifies that the reviewed lab and workbook inputs have not drifted.
6. A reviewer walks the lab as a student, records the result, and updates
   `review_status` and `difficulty_evidence`.
7. `python scripts/check-links.py Manual-Lite docs Workbook --mkdocs` runs before
   release.

Automated checks prove consistency, not instructional quality. A lab that passes
every script can still be confusing, too long, or based on a misleading clue;
that is what the student-tester and design-tester reviews are for.

## Framework references

Framework references are **alignment aids**, not certifications or accreditation
claims. The curriculum maps to:

- **NIST NICE Workforce Framework** work roles and task areas, recorded in
  [NICE mapping](NICE-MAPPING.md).
- **MITRE ATT&CK** tactics and techniques for defensive context.
- **OWASP Top 10** and the OWASP Cheat Sheet Series for web content.
- Vendor certification pathways (CompTIA, ISC2, OffSec, and others) as career
  guidance only. A lab completing a mapped objective does not confer a
  certification or continuing-education credit.

The framework registry and the selective mapping rules are in
`curriculum-frameworks.yaml`. Each lab has one primary competency and at most
two framework references so the mapping remains reviewable.

## Fictional and synthetic content

- Organisations, people, domains, credentials, flags, logs, emails, and
  artefacts are fictional unless a page explicitly cites a public source.
- Lab targets resolve only inside the isolated lab network. Do not test the
  commands against real hosts.
- Training flags (`OCR{...}`) are not secrets and must not be reused outside the
  lab.
- Third-party names and trademarks belong to their owners and are used for
  identification and interoperability only.
- No real learner record, personal data, live credential, or malware sample is
  required to complete an exercise.

## AI assistance disclosure

AI tools helped draft code, workbook text, diagrams, and documentation. A human
maintainer remains responsible for accuracy, safety, licensing, and review. AI
output is treated as a draft: it is checked against the lab contract, the
framework registry, and the repository's validation scripts before release. The
full disclosure is in [BUILD_NOTICE.md](../BUILD_NOTICE.md).

AI assistance does not make the material an authoritative legal, medical, or
professional certification source. Operators remain responsible for adapting
content to their jurisdiction, programme, and learner cohort.

## Change control

- Workbook and lab changes are committed together with the regenerated coverage
  and curriculum pages.
- `supply-chain.lock.json` records hashes for lab and workbook inputs; a drift
  fails install, update, and prebuild gates.
- `CHANGELOG.md` records learner-visible changes.
- A correction that changes a target, flag, command, or safety boundary requires
  a new `content_version` and a fresh review entry.

## Reporting an error

Report a factual error, unsafe instruction, broken command, or missing
attribution through the repository issue tracker. For a security or privacy
problem, follow [SECURITY.md](../SECURITY.md) and do not open a public issue.
Include the page or lab slug, the exact text or command, what you expected, and
what happened.

## Related documents

- [Learning framework](LEARNING-FRAMEWORK.md)
- [Lab metadata schema](LAB-METADATA-SCHEMA.md)
- [NICE mapping](NICE-MAPPING.md)
- [Curriculum manifest](../curriculum-manifest.yaml)
- [Framework registry](../curriculum-frameworks.yaml)
- [Build notice](../BUILD_NOTICE.md)
- [Third-party notices](../THIRD_PARTY_NOTICES.md)
