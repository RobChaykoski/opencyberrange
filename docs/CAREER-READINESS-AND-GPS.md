# Career readiness and the Cybersecurity GPS

Status: **development preview** (11 November 2026). Gated by
`advanced_dna_insights_enabled`, which is off by default.

This layer answers three questions on the learner's **Portfolio** tab:

1. **Where am I?** Evidence by domain, category, and competency.
2. **I want to become a SOC Analyst. What do I need?** Role readiness, gaps, next
   workbooks, capstone, certifications, and employer evidence.
3. **Where could I go?** An optional Cybersecurity GPS built from evidence,
   recent growth, and answers the learner can skip.

It sits on top of Cyber DNA. The Cyber DNA formula stays **2026.14**. Readiness
and GPS are separate, versioned reporting layers, so a change here cannot move a
trait score.

## The pipeline

```
Skills Earned → Evidence Collected → Competencies Validated → Career Readiness → Employment Outcomes
```

The platform can evidence the first four stages. It does **not** track employment
outcomes, and it does not claim that a learner will be hired. The last stage is
shown as a portfolio-readiness state, with an explicit note that outcomes are not
tracked. The transcript and professional portfolio are the shareable evidence.

## Data files

| File | Purpose | Version |
|---|---|---|
| `app/data/competency-taxonomy.yaml` | Domains, categories, and 212 competencies. | 1.0 |
| `app/data/competency-mapping.yaml` | Chapter, track, category, and primary-axis mapping to competencies. | 1.0 |
| `app/data/competency-assessment.yaml` | Five-dimension rubric, proficiency levels, evidence requirements. | 1.0 |
| `app/data/curriculum-roles.yaml` | 13 pathways, 5 flagship, critical competencies, readiness model. | 1.0 |
| `app/data/cyber-gps.yaml` | Optional questions, interest weights, pace guidance. | 1.0 |

The files are loaded once per process and cached. A missing or malformed file
fails loudly at startup rather than silently returning empty data.

## Assessment model

Each competency is scored across five dimensions:

| Dimension | Weight | Evidence |
|---|---:|---|
| Knowledge | 20% | Exercise quiz attempts, best score per lab. |
| Execution | 30% | Hands-on lab completions, clean solves, advanced labs. |
| Troubleshooting | 20% | Clean-solve share plus advanced-lab bonus. |
| Documentation | 15% | Completions mapped to a workbook chapter. |
| Communication | 15% | Capstone completion or repeated practice. |

A score is **provisional** when one or more dimensions have no evidence. The
weighted score is renormalised over the dimensions that are available, and the
API reports the coverage percentage. A competency is **validated** only when the
score is at least 60 **and** the learner has a workbook or capstone evidence
entry. A completion alone is not an award.

## Evidence bands in the interface

Each career family carries the evidence behind its match:

| Band | Evidence | Meaning |
|---|---|---|
| **Established** | 5 or more completed labs in the branch | The match has a stable practice base |
| **Growing** | 1–4 completed labs | Directionally supported; a few more labs stabilise it |
| **No evidence yet** | 0 labs | A starting suggestion from the branch profile, not an assessment |

The band appears in the family detail and the screen-reader label. It is not a
confidence score or a probability.

## Readiness model

Readiness uses five components:

| Component | Weight | Source |
|---|---:|---|
| Workbook | 30% | Documentation dimension across the role's critical competencies. |
| Lab assessment | 20% | Execution dimension. |
| Independent | 20% | Troubleshooting dimension. |
| Scenario | 10% | Communication dimension. |
| Capstone | 20% | Completed capstone evidence. |

A missing component is listed in `provisional_components` rather than counted as
zero. The role's `career_ready_threshold` and `domain_floor` decide the
**Career Ready** flag. The label is a curriculum-readiness label, not a hiring
prediction.

### Colour thresholds

| Colour | Domain coverage | Lab readiness | Meaning |
|---|---:|---:|---|
| Green | ≥ 85% | ≥ 75 | Strong evidence. |
| Amber | 60–84% | 60–74 | Worth exploring; keep practising. |
| Red | < 60% | < 60 | Build first. |
| Grey | No evidence | No evidence | Nothing to judge yet. |

Colour is always paired with a text label and a sample size. It is never the only
signal.

## Cybersecurity GPS

The GPS combines three signals:

- **Evidence** (55%): the role's readiness score.
- **Interest** (25%): optional answers, normalised across roles. If no answers are
  given, this term is omitted and the evidence and growth weights are used.
- **Growth** (20%): recent completions in the role's critical competencies, with
  a 30-day window.

Fit labels: **Strong fit** (≥ 75), **Worth exploring** (50–74), **Stretch
direction** (< 50). A stretch direction is a prompt to explore, not a closed
door.

Questions are optional. Answers are sent in the request body, used for that
response only, and are **not stored, logged, or shared**. The UI keeps them in
component state and offers **Clear answers**.

### Signal and fading interest

The GPS header shows a practice-signal badge based on completions in the last 30
days:

- **Signal active** (at least one recent completion) shimmers, and domain cards
  with recent work pulse.
- **Signal fading** (no recent completion) fades, and the GPS names the domains
  the learner has worked in before as **fading interest signals**.

A fading domain is a subject with prior evidence, not a deficit. The prompt asks
whether a short exercise would show that the interest is still there. It is not a
ranking, a grade, or a reason to remove the domain from the learner's record.
The signal is derived from completion timestamps; it does not persist any new
data and does not change the GPS fit scores.

## API

All endpoints require an authenticated learner and the advanced insights gate.

| Method | Path | Purpose |
|---|---|---|
| GET | `/api/profile/competencies` | Taxonomy evidence and assessment scores. |
| GET | `/api/profile/roles` | Pathway catalogue and readiness model. |
| GET | `/api/profile/role-readiness?role=soc-analyst` | The role-readiness answer. |
| POST | `/api/profile/gps` | Direction finding; body `{ "answers": { ... } }` is optional. |
| GET | `/api/analytics/reports/curriculum-demand` | Instructor curriculum demand. |

All responses use `Cache-Control: no-store`.

## Instructor curriculum demand

The instructor view aggregates the courses the instructor owns (administrators
see all active courses) and combines:

- pulse topic requests;
- exercise friction: completion, abandonment, hint pressure, attempts, failures;
- cohort competency coverage.

It emits planning cards with a priority, a sample size, an evidence source, and a
suggested action. Courses below the configured minimum cohort size contribute
nothing. The output is aggregate-only and never names a learner.

## Privacy and responsible use

- Readiness and GPS describe the learner's own evidence. No staff-wide learner
  atlas endpoint exists.
- The GPS does not persist answers.
- The instructor dashboard uses the same suppression threshold as the rest of
  analytics.
- Every surface carries a disclaimer: no grades, no rankings, no hiring
  decisions, no employment predictions.
- Salary and certification content in the Career Atlas is sourced and dated;
  verify it with the source before using it in advising.

## Tests

```bash
python -m pytest tests/test_curriculum_demand.py tests/test_career_readiness.py -q
```

DB-backed profile tests use `TEST_DATABASE_URL` and skip cleanly without it.
