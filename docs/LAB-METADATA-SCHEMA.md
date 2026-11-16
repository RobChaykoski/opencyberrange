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
# By completion students will be able to:
learning_outcomes:
  - Enumerate SMB shares over a null session
  - Identify shares that expose more data than authenticated access
  - Explain the defensive control that prevents anonymous enumeration
mapped_skills:
  - identity_access
  - network_systems
assessment_criteria:
  - Submit the correct flag.
  - Pass every automated test step in the lab manifest.
mitre_attack:
  - tactic: Credential Access
    technique: T1003
    technique_name: OS Credential Dumping
    detection: Monitor credential-store access and LSASS or memory-analysis activity.
```

## Required fields

| Field | Type | Rules |
|---|---|---|
| `title` | string | 1-100 characters, unique across the catalog |
| `category` | string | lower-case kebab-case, e.g. `network-analysis` |
| `difficulty` | string | `beginner`, `intermediate`, `advanced`, or `expert` |
| `estimated_time` | integer | estimated learner minutes, greater than zero |
| `prerequisites` | list of strings | lab slugs from this catalog; may be empty |
| `learning_outcomes` | list of strings | 3-5 measurable outcomes, each introduced by `# By completion students will be able to:` |
| `mapped_skills` | list of strings | competency keys, non-empty |
| `assessment_criteria` | list of strings | how the lab is graded, non-empty |
| `analyst_finding_required` | boolean | when true, a short analyst finding or evidence artifact is required in addition to the flag |
| `mitre_attack` | list of mappings | at least one `tactic`, `technique`, and `detection` |

Legacy keys `name`, `duration_minutes`, `objectives`, and
`learning_objectives` are **not accepted**. The loader reads only the canonical
keys, and the JSON Schema rejects the aliases. All 191 repository labs use the
canonical names.

## Machine contract

The canonical contract is enforced in three places:

- `platform/backend/lab_metadata.schema.json` — JSON Schema draft 2020-12.
  Unknown keys are rejected at every level, so a typo fails instead of silently
  producing an incomplete lab.
- `scripts/validate_lab_metadata.py` — walks every `lab.yaml`, parses it, and
  validates it against the schema with a per-file report.
- The backend CI job runs the validator after linting.

Run it locally:

```bash
python scripts/validate_lab_metadata.py
python scripts/validate_lab_metadata.py --labs-dir platform/labs --quiet
```

`jsonschema` is pinned in `platform/backend/requirements-dev.txt`; it is a
validation dependency, not a runtime one.

## Competency contract

Every lab also has a competency contract in
`platform/backend/app/data/competency-contracts.yaml`. The contract is
generated from `competency-taxonomy.yaml`, `competency-mapping.yaml`,
`lab.yaml`, and the curated high-use overrides. It records:

- competency taxonomy IDs with explicit weights (sum `1.0`);
- prerequisites, difficulty, and expected duration;
- four evidence types with weights (sum `1.0`): lab flag, automated validation
  steps, workbook analyst answers, and a submitted artifact;
- an assessment-reliability level, score, determinism, evidence completeness,
  independent-validation status, and rationale;
- a prohibited-collection list: keystrokes, mouse movement, and exhaustive
  terminal history are never collected.

The 25 labs with the most production completions are curated first in
`competency-contract-overrides.yaml`. A generated baseline covers every other
lab and is marked `baseline_derived` until a reviewer records a live three-run
harness result. See [`COMPETENCY-CONTRACTS.md`](COMPETENCY-CONTRACTS.md) for the
coverage and review queue.

```bash
python scripts/generate-competency-contracts.py
python scripts/generate-competency-contracts.py --check
```

## Learning outcomes

Every lab introduces its outcomes with the fixed line:

```yaml
# By completion students will be able to:
learning_outcomes:
  - Configure a Linux firewall
  - Analyze web server logs
  - Detect brute-force authentication attempts
  - Identify malicious processes
```

Rules:

- exactly 3 to 5 outcomes;
- each outcome starts with an observable action (for example `Configure`,
  `Analyze`, `Detect`, `Identify`, `Enumerate`, `Exploit`, `Document`);
- avoid vague verbs such as `Understand`, `Learn`, `Know`, or `Appreciate`;
- do not list flag capture as a learning outcome; that belongs under
  `assessment_criteria`.

The standardizer rewrites vague openers (`Understand` to `Explain`, `Learn` to
`Explain`, `Know` to `Identify`), fills short lists from concrete tester steps or
a category fallback, and trims long lists to five.

## MITRE ATT&CK mapping

Every offensive and defensive exercise declares at least one mapping:

```yaml
mitre_attack:
  - tactic: Credential Access
    technique: T1003
    technique_name: OS Credential Dumping
    detection: Monitor credential-store access and LSASS or memory-analysis activity.
```

Rules:

- `tactic` uses the MITRE ATT&CK tactic name, such as `Credential Access`;
- `technique` uses an Enterprise or ICS technique ID, such as `T1003`,
  `T1021.001`, or `T0846`;
- `technique_name` is the human-readable technique name;
- `detection` states the log source or control that would reveal the activity;
- multiple mappings are allowed for multi-stage labs.

The mapping is stored in `labs.mitre_attack` and returned by the curriculum API
so reports, learner briefs, and future coverage views use the same taxonomy.

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

## Audience and minor-safe defaults

The optional `audience` field is `general`, `grades_9_12`, or `adult`. It
describes the intended cohort, not a learner's declared age. The advanced
OSINT labs (2.x) are `audience: adult` and `visibility: course`; they are
instructor-assigned extensions. A learner whose account is marked under 18 does
not see `category: osint` labs in the main list.

Every High School lab also declares:

```yaml
offline_only: true
external_targets: []
personal_data: none
free_text: false
public_profiles: false
phone_required: false
analytics: aggregate_only
minor_safe_defaults: true
```

`scripts/check-minor-safe.py` fails if a High School lab is missing these
values, uses a non-local scenario target, carries real location data, or if the
built High School wiki contains an OSINT/malware chapter or live-target text.
See [Minor-safe defaults](MINOR-SAFE-DEFAULTS.md).

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
