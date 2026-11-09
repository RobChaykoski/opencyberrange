# Lab metadata schema

Every `platform/labs/<Track>/<lab-slug>/lab.yaml` starts with the same
machine-readable metadata header. The header is the contract used by catalog
generation, curriculum planning, analytics, competency mapping, and
recommendations.

```yaml
title: SMB Null Session Share Enumeration
category: enumeration
difficulty: beginner
estimated_time: 120
prerequisites:
  - windows-2-5-smb-null-session-connection
learning_outcomes:
  - Enumerate SMB shares over a null session
  - Identify shares that expose more data than authenticated access
mapped_skills:
  - identity_access
  - network_systems
assessment_criteria:
  - Submit the correct flag.
  - Pass every automated test step in the lab manifest.
```

## Required fields

| Field | Type | Rules |
|---|---|---|
| `title` | string | 1-100 characters, unique across the catalog |
| `category` | string | lower-case kebab-case, e.g. `network-analysis` |
| `difficulty` | string | `beginner`, `intermediate`, or `advanced` |
| `estimated_time` | integer | estimated learner minutes, greater than zero |
| `prerequisites` | list of strings | lab slugs from this catalog; may be empty |
| `learning_outcomes` | list of strings | measurable outcomes, non-empty |
| `mapped_skills` | list of strings | competency keys, non-empty |
| `assessment_criteria` | list of strings | how the lab is graded, non-empty |

Legacy keys `name`, `duration_minutes`, `objectives`, and
`learning_objectives` are no longer used. The loader still accepts them during a
transition, but repository labs and uploads should emit the canonical keys.

## Prerequisites

`prerequisites` mirrors the sequential unlock graph:

- the first lab in the first level has no prerequisites;
- the first lab in a later level lists every lab in the previous existing
  level, so the level gate is explicit;
- later labs in the same level list the immediately preceding lab;
- an optional level `0` does not gate the first graded level.

When a lab is added, removed, or reordered, regenerate the graph with the
standardizer instead of editing lists by hand.

## Mapped skills

`mapped_skills` uses the eight competency axes from
`app/services/competency_model.py`:

- `network_systems`
- `web_api`
- `identity_access`
- `incident_forensics`
- `osint`
- `malware`
- `ot_ics`
- `ai_security`

Authored mappings take precedence over the old track/category heuristic. A
completion snapshot therefore records the lab's declared skills, and the
competency radar and analytics follow the manifest.

## Tooling

Run the standardizer from the repository root:

```bash
python platform/backend/app/scripts/standardize_lab_metadata.py --check
python platform/backend/app/scripts/standardize_lab_metadata.py --write
```

`--check` exits non-zero when a lab is missing metadata or when the generated
prerequisites are stale. `--write` rewrites only the metadata header and leaves
the scenario, hints, credentials, topology, and test steps untouched.

The static checker also enforces the header:

```bash
python platform/backend/app/services/workbook_linters/check_labyaml.py
```

The backend test suite includes `tests/test_lab_metadata_schema.py`, which
validates every lab without needing a database.

## Discovery and API

Discovery reads `title` and `estimated_time`, with legacy fallbacks, and stores
the three new arrays in `labs.prerequisites`, `labs.mapped_skills`, and
`labs.assessment_criteria`. Learning outcomes continue to use the existing
`labs.objectives` column for backward compatibility.

`GET /api/curriculum/tracks/{track_slug}` returns both the legacy
`duration_minutes` / `objectives` keys and the canonical
`estimated_time` / `learning_outcomes` / `prerequisites` / `mapped_skills` /
`assessment_criteria` keys.
