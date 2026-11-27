# NICE Framework ingestion and lab mapping

OpenCyberRange ingests the official NIST NICE Framework components and uses
them as a controlled vocabulary for lab authoring.

## Source

| Item | Value |
|---|---|
| Framework | NICE Framework Components v2.2.0 |
| Official JSON | `https://csrc.nist.gov/csrc/media/Projects/cprt/documents/nice/v2-2-0_nf_components.json` |
| Bundled snapshot | `platform/backend/app/data/nice/nice-v2.2.0.json.gz` |
| Component counts | 42 work roles, 962 tasks, 693 knowledge, 556 skills |

The snapshot is compressed and generated from the official JSON. Rebuild it
when NIST publishes a new component release:

```bash
python scripts/build-nice-snapshot.py
```

The script refuses a file whose document version does not start with `2.2`.
Update `NICE_VERSION` and the target filename in
`app/services/nice_framework.py` for a later major release.

## Database

| Table | Purpose |
|---|---|
| `nice_components` | One row per work role, task, knowledge, or skill statement |
| `nice_links` | Work-role to task/knowledge/skill relationships |
| `nice_framework_meta` | Installed version, source, timestamp, and counts |
| `lab_nice_components` | Selected components for one lab |

Component codes are the stable identity. A refresh updates statement text and
marks components that disappeared as inactive; it does not delete a component
that a lab still references.

## API

| Endpoint | Access | Purpose |
|---|---|---|
| `GET /api/nice/status` | Instructor | Installed version and counts |
| `GET /api/nice/components` | Instructor | Search by type, text, and optional work role |
| `GET /api/nice/labs/{lab_id}` | Instructor | Current lab mapping |
| `PUT /api/nice/labs/{lab_id}` | Admin | Replace the lab mapping |
| `POST /api/nice/refresh` | Admin | Refresh from NIST or the bundled snapshot |

The authoring dropdown calls the component search endpoint. It stores codes, and
the backend validates every code against an active component before saving.

## First boot and refresh

On first boot, the backend seeds the database from the bundled snapshot when the
component table is empty. This keeps the dropdown usable without outbound
network access. An administrator can refresh from NIST with:

```http
POST /api/nice/refresh
{"source": "official"}
```

If the network is unavailable, use `{"source": "snapshot"}`. A failed refresh
returns a useful error and leaves the existing version in place.

## Existing lab coverage

The repository includes `platform/backend/app/data/nice/lab-mappings.yaml`, a
provisional mapping for all 222 labs. It is generated from each lab's competency
keys and category:

```bash
python scripts/generate-nice-lab-mappings.py
python scripts/generate-nice-lab-mappings.py --check
```

The mapping is deliberately labelled `provisional`. It only fills labs with no
mapping, and a manual save in the exercise editor marks that lab `reviewed`.
`GET /api/nice/coverage` returns mapped/unmapped totals and the review queue;
`POST /api/nice/labs/seed` fills empty labs from the seed file.

Do not present a provisional mapping as reviewed curriculum evidence. The review
queue exists so a curriculum owner can confirm the work roles, tasks, and KSATs
against the actual lab.

## Mapping rule

Every new lab should select:

- one or more work roles;
- one or more tasks;
- at least one knowledge or skill statement.

The lab page and API show the installed framework version next to the mapping so
a reviewer can see whether it was made against v2.2.0 or a later release.

SFIA, ECSF, and the CISA Workforce Framework are the next catalogs. They should
follow the same pattern: an official source, a versioned snapshot, validated
codes, and a refresh path. The SFIA 9 licensing, data model, mapping rules, and
review gate are defined in [SFIA 9 ingestion](SFIA-9-INGESTION.md).
