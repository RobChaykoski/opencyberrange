# SFIA 9 ingestion plan

Status: **planning. No SFIA content or mappings are included yet.**

SFIA 9 is the current version of the Skills Framework for the Information Age,
published in October 2024. It defines seven levels of responsibility, a
professional-skills catalogue, and generic attributes and behavioural factors.
The official framework and its cyber-security and AI views are at
[sfia-online.org/en/sfia-9](https://sfia-online.org/en/sfia-9).

This page is the ingestion contract for adding SFIA 9 as a career and
competency crosswalk. It exists so a future change can import the framework
without copying unlicensed content or inventing mappings.

## Why SFIA 9

SFIA is widely used by employers and professional bodies. It adds a
responsibility-level vocabulary that complements the platform's existing
crosswalks:

- NICE/NIST work roles for cyber workforce alignment;
- ACM/IEEE CS2023 knowledge areas for computing curricula;
- CAE-CD outcomes for institutional accreditation;
- SFIA 9 for employer-facing skills and responsibility levels.

SFIA is **not** a certification, a grade, or a claim that a learner is ready for
a role. A SFIA level describes responsibility and accountability; it is not a
score on a lab.

## Licensing gate

The SFIA Foundation publishes the framework and documentation under its own
terms. The skills, responsibilities, generic attributes, and spreadsheet are
available through the official site; the documents require registration and are
subject to the SFIA licence. The trade mark and copyright remain with the SFIA
Foundation.

Before any SFIA text, skill definition, level descriptor, or spreadsheet row is
committed:

1. Record the licence or permission that allows this repository and its
   deployments to store and display the content.
2. Keep the licence reference and snapshot date beside the imported data.
3. Do not copy SFIA prose into a lab, workbook, or public page unless the
   licence explicitly allows it.
4. If the licence does not allow redistribution, store only the *mapping*
   (competency id to SFIA skill code and level range) with an attribution and a
   link to the official source.

Until that gate is cleared, this repository will not contain SFIA skill
definitions or a lab-to-SFIA mapping.

## Proposed data model

```text
sfia_version
  version             "9"
  published_at        2024-10
  source_url          https://sfia-online.org/en/sfia-9
  snapshot_date       YYYY-MM-DD
  content_hash        SHA-256 of the licensed snapshot
  licence_reference   institutional record or permission id

sfia_skill
  skill_code          official SFIA code
  skill_name          official name
  category            official category or view
  level_min           lowest defined responsibility level
  level_max           highest defined responsibility level

competency_sfia
  competency_id       platform taxonomy id, e.g. NET-031
  sfia_skill_code     official code
  sfia_level_min      minimum defensible level
  sfia_level_max      maximum defensible level
  confidence          low | medium | high
  rationale           why the observable behaviour maps
  review_status       draft | reviewed | rejected
  reviewed_at         UTC timestamp
  reviewer_id         curriculum reviewer
```

A competency may map to more than one SFIA skill. A lab does not map directly to
SFIA; it maps through its reviewed competency contract.

## Mapping rules

- Map **observable behaviour**, not a job title.
- Use a level **range**, not a single level, unless the evidence supports one.
- Do not infer a SFIA level from a flag, a completion, or a quiz score.
- Do not map a competency to a skill that is not in the licensed snapshot.
- A mapping is `draft` until a subject-matter reviewer records a rationale.
- A rejected mapping is kept as a rejected row so the decision is auditable.
- Re-import a new SFIA version as a new snapshot; never edit a published mapping
  in place.

## Ingestion steps

1. Obtain the licensed SFIA 9 spreadsheet or API access.
2. Snapshot the version, date, and content hash; record the licence reference.
3. Import the official skill codes, names, categories, and level ranges.
4. Map the platform taxonomy to SFIA skills in a review queue.
5. Review each mapping for behaviour, level range, and rationale.
6. Publish a read-only API and a manual page that cites the official source.
7. Add a release check that fails on an unknown skill code, an unknown
   competency, or a missing licence reference.
8. Refresh on a new SFIA version; keep the old snapshot for historical reports.

## API and UI

Proposed read-only endpoints:

| Endpoint | Purpose |
|---|---|
| `GET /api/frameworks/sfia/versions` | Available SFIA snapshots |
| `GET /api/frameworks/sfia/skills` | Imported skill catalogue |
| `GET /api/competencies/{id}/sfia` | SFIA mappings for one competency |
| `GET /api/frameworks/sfia/coverage` | Mapped competencies and gaps |

The learner-facing page should explain the difference between a competency
score and a SFIA responsibility level, and should never present a mapping as a
job guarantee.

## Acceptance criteria

- A licensed SFIA 9 snapshot with a version, date, hash, and licence reference.
- Every imported skill code and level range validates against the snapshot.
- Every mapping references a known competency and a known SFIA skill.
- A reviewer rationale exists for every published mapping.
- No SFIA prose is committed unless the licence allows redistribution.
- The manual page cites the official SFIA 9 source and states the limits.
- A boundary test fails on an unknown code or an unlicensed snapshot.

## Current blocker

The repository does not yet have a licensed SFIA 9 snapshot or a recorded
permission to redistribute the skill definitions. The next action is to obtain
that snapshot or permission, then draft the first mapping set for the cyber
security view.
