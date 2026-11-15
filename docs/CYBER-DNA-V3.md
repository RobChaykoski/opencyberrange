# Cyber DNA v3 — talent discovery graph

Status: **Draft for approval.** No implementation is included in this change.

Owner: OpenCyberRange curriculum and platform
Target: Release 5.17 line (phased)
Decision log:

- The output is **career affinity**, not a probability. A probability requires
  calibration data, consent, and a much larger evidence base.
- The **employer view is out of scope**. This RFC defines learner-facing data
  and export payloads only.
- Evidence is an **append-only ledger**; behavior, interest, and affinity are
  **immutable snapshots** built from it. Live dashboards still compute on read.

## 1. Summary

The current Cyber DNA implementation is already more than a badge engine. It
has a competency taxonomy, an eight-axis evidence radar, six DNA traits, growth
velocity, career pathways, role readiness, a portfolio, and immutable report
snapshots. What it lacks is a first-class **evidence record**, a persisted
**behavior profile**, a persisted **interest vector**, and a persisted
**career-affinity score with confidence**.

This RFC adds those four layers without replacing the existing DNA, GPS, or
competency radar. The new model answers:

> What kind of cybersecurity work does this learner's evidence point toward,
> how strong is the evidence, and what should they try next?

It does **not** answer:

> What job will this learner get?

## 2. Goals and non-goals

### Goals

- Store one auditable evidence row per learner, completion, and competency.
- Turn existing actions into a five-signal behavior profile.
- Detect interest from voluntary lab choices, not from a survey alone.
- Score career affinity from competency coverage, evidence depth, behavior fit,
  and interest fit.
- Make every score explainable: evidence count, contributing labs, formula
  version, weights, and confidence.
- Preserve historical reports through `learner_snapshots`.
- Stay owner-only and privacy-first.

### Non-goals

- Employer or recruiter access, public profiles, or hiring recommendations.
- A probability of employment or a prediction of job performance.
- Ranking learners against each other, publicly or privately.
- Telemetry from inside RangeBox (keystrokes, shell history, packet captures).
  Investigation depth is a documented proxy until a separate telemetry design
  is approved.
- Replacing `skill_dna`, `cyber_gps`, `competency_radar`, or role readiness.
  The new layers feed them and are exposed alongside them.

## 3. Current foundation

| Capability | Code | Reuse |
|---|---|---|
| Competency taxonomy, 14 domains, competency IDs | `app/data/competency-taxonomy.yaml`, `services/competency_taxonomy.py` | Evidence joins `competency_id` to this taxonomy |
| Chapter-to-competency mapping | `app/data/competency-mapping.yaml` | Backfill and evidence creation |
| Completion snapshot | `models.LabCompletion` (`competency_mapping`, `lab_difficulty_snapshot`) | Source for evidence |
| Eight-axis radar | `services/competency_radar.py` | Aggregates evidence; remains the UI source |
| Six DNA traits | `services/skill_dna.py` | Existing traits remain; `factor_weights` already returned |
| Growth velocity / momentum | `services/growth_velocity.py`, `skill_momentum.py` | Inputs for behavior signals |
| Career pathways and readiness | `app/data/curriculum-roles.yaml`, `services/role_readiness.py` | Affinity weights and critical competencies |
| Immutable reports | `models.LearnerSnapshot`, migration `0031`, `services/learner_snapshots.py` | New snapshot kinds need no schema change |
| Behavioral achievements | `services/achievements.py` (`comeback_labs`, `no_hint_labs`, `perfect_labs`, `night_labs`) | Corroborating evidence, not a score source |

## 4. Architecture

```
lab completion
   |
   +--> evidence_records (append-only, one row per competency)
   |        |
   |        +--> competency score (derived, live)
   |        +--> behavior profile (snapshot)
   |        +--> interest vector (snapshot)
   |        +--> career affinity (snapshot)
   |
   +--> learner_snapshots (immutable payload + formula/mapping versions)
```

Rules:

1. **One write path.** Evidence rows are written only by the backend when a
   verified completion is created. No client-supplied scores.
2. **Derived on read, persisted on export.** Live pages compute from
   `evidence_records`; a snapshot is written when a report or identity export is
   generated.
3. **Never rewrite.** A formula change bumps `formula_version`; existing rows
   and snapshots keep their original versions and weights.
4. **One source of truth per number.** A score is reproducible from the
   evidence rows and the stored weights.

## 5. Data model

### 5.1 `evidence_records` (new, migration `0032_evidence_records`)

| Column | Type | Notes |
|---|---|---|
| `id` | integer PK | |
| `user_id` | FK users, cascade | owner |
| `lab_id` | FK labs, cascade | source lab |
| `source_completion_id` | FK lab_completions, cascade | audit link |
| `competency_id` | varchar(32) | taxonomy ID, e.g. `NET-011` |
| `domain_id` | varchar(16) | e.g. `NET` |
| `mapping_weight` | numeric(5,4) | normalized chapter/axis weight |
| `score_contribution` | numeric(6,3) | pre-saturation weight (see 6.1) |
| `difficulty` | varchar(20) | snapshot at completion |
| `attempts` | integer | snapshot |
| `hints_used` | integer | snapshot |
| `time_spent_minutes` | integer nullable | snapshot |
| `formula_version` | varchar(32) | e.g. `evidence-2026.1` |
| `mapping_version` | varchar(32) | taxonomy/mapping version |
| `created_at` | timestamptz | server time |

Constraints and indexes:

- `UNIQUE (source_completion_id, competency_id)` so replay is idempotent.
- `INDEX (user_id, competency_id, created_at)` for scoring.
- `INDEX (user_id, created_at)` for behavior windows.
- No update path after insert. A correction is a new row plus a superseding
  completion, not an edit.

### 5.2 Reused tables

- `lab_completions` keeps `competency_mapping`, `lab_difficulty_snapshot`,
  `competency_model_version`, attempts, hints, and time. It remains the event.
- `learner_snapshots` gains three kinds: `behavior_profile`,
  `interest_profile`, `career_affinity`. The table already stores payload,
  schema/formula versions, weights, hash, and owner. No migration is required
  because `kind` is a string.
- `achievements` are not evidence inputs. They are shown as corroboration and
  may be referenced in behavior explanations, never added as points.

### 5.3 Backfill

Existing completions have axis-level mappings, not per-competency rows.

Backfill algorithm (`scripts/backfill-evidence.py`, dry-run first):

1. For each completion, resolve the lab's `chapter_id`.
2. Read the chapter competency list from `competency-mapping.yaml`.
3. If the chapter is mapped, assign `1 / len(competencies)` to each competency.
4. If not mapped, expand the completion's `competency_mapping` domain to its
   taxonomy competencies and divide equally.
5. Write `mapping_version = "backfill-1"`, `formula_version = "evidence-2026.1"`,
   and `score_contribution` using the completion snapshot.
6. Idempotent: skip `(source_completion_id, competency_id)` pairs that exist.

Backfill is marked as approximate in API metadata (`"source": "backfill"`) and
is never mixed silently with live evidence in a snapshot's `weights` block.

## 6. Scoring model

Notation:

- `d` difficulty weight: beginner `1.0`, intermediate `1.5`, advanced `2.0`,
  expert `2.5`.
- `m` normalized mapping weight from `competency_mapping` (0–1).
- `i` independence multiplier: `1.0 + 0.35 * clean + 0.20 * first_attempt`,
  where `clean = hints == 0`, `first_attempt = attempts == 1`.
- `r` recency factor, reusing the existing DNA steps: 1.0 (≤14 days), 0.99
  (≤30), 0.97 (≤60), 0.94 (≤90), 0.90 (>90).
- `E_c` weighted evidence for competency `c`:
  `E_c = Σ (d * m * i * r)` over its evidence rows.

### 6.1 Competency score

```
score_c = round(100 * (1 - exp(-E_c / 4)))
```

The curve is intentionally saturating: a single clean beginner lab is evidence,
not mastery. Examples: `E=1 → 22`, `E=2 → 39`, `E=4 → 63`, `E=8 → 86`,
`E=12 → 95`. Scores cap at 99, matching DNA.

Proficiency bands (descriptive, not grades):

| Score | Band | Meaning |
|---:|---|---|
| 0–24 | Awareness | Recognises the term; little practice evidence |
| 25–44 | Foundational | Guided procedure completed |
| 45–64 | Practitioner | Applied in a familiar exercise |
| 65–84 | Specialist | Applied under friction with evidence |
| 85–99 | Lead | Repeated, varied, current evidence |

Evidence count and `last_practised_at` must accompany every score in API output.

### 6.2 Behavior profile

Only signals the platform can observe. Each is `null` below its minimum sample.

| Signal | Formula | Minimum | Notes |
|---|---|---|---|
| Persistence | `100 * (0.6 * attempt_depth + 0.4 * recovery)`; `attempt_depth = min(1, (mean_attempts_before_success - 1) / 6)`; `recovery = share of completions with ≥5 prior failed attempts` | 5 completions | Higher attempts are not punished; recovery is the positive signal |
| Independence | `100 * (0.6 * hint_free_rate + 0.4 * (1 - min(hints_per_completion, 5) / 5))` | 5 completions | Hints reduce the signal, not the competency evidence |
| Speed | `100 * (mean(clamp(median_time_for_difficulty / max(time, 1), 0.5, 1.5)) - 0.5)` | 5 timed completions | Median is per difficulty and per track; slow and fast both bounded |
| Consistency | `100 * min(active_weeks / 4, 1)` over 30 days | 2 active weeks | Calendar weeks with at least one completion |
| Investigation proxy | `100 * (0.6 * breadth + 0.4 * attempt_depth)`; `breadth = min(distinct_categories_30d / 6, 1)` | 5 completions | **Proxy only.** Not logs, packets, or commands. Label it “exploration breadth” in the UI |

Every behavior payload includes `sample_size`, `window_days`, `confidence`
(low/medium/high), and a note naming the proxy. No behavior score is shown
without its sample size.

### 6.3 Interest vector

Interest is derived from **voluntary** completions: a completion that is not
in an assigned lab for an active enrollment at completion time.

```
interest_c = 100 * (recency_weighted_voluntary_completions_c
                    / max_c(recency_weighted_voluntary_completions))
```

- Minimum 5 voluntary completions across at least two categories.
- Otherwise `interest_vector` is `null`, and affinity falls back to evidence.
- GPS answers remain transient and are **not** an input in v3. If optional
  answers are added later, they require explicit consent and a separate
  retention decision.
- The API returns category and track shares, not raw lab history.

### 6.4 Career affinity

Pathway weights come from `curriculum-roles.yaml`. Add a `behavior_weights`
block per pathway (new data, not a new table):

```yaml
pathways:
  - id: soc-analyst
    behavior_weights:
      consistency: 0.40
      investigation: 0.40
      independence: 0.20
  - id: penetration-tester
    behavior_weights:
      persistence: 0.40
      independence: 0.40
      speed: 0.20
```

Affinity formula:

```
coverage = Σ critical_weight * [score >= 60] / Σ critical_weight
depth    = Σ critical_weight * min(score / 100, 1) / Σ critical_weight
behavior = Σ behavior_weight * signal / 100
affinity = 100 * (0.50 * coverage + 0.20 * depth
                  + 0.15 * behavior + 0.15 * interest)
```

If interest is unavailable, renormalize the remaining weights by `1 / 0.85`
(0.588 / 0.235 / 0.176). Missing behavior signals are dropped and the remaining
weights renormalize the same way.

Confidence gates:

| Evidence | Output |
|---:|---|
| 0–2 | No score; “not enough evidence yet” |
| 3–7 | Low confidence; show range `score ± 8`, label “early signal” |
| 8–14 | Medium confidence; show range `score ± 5` |
| 15+ | High confidence; show range `score ± 3` |

The range is an evidence-band, **not** a statistical confidence interval. The
API field is `confidence_band`, never `probability`.

Every affinity result includes:

```json
{
  "pathway_id": "soc-analyst",
  "title": "SOC Analyst",
  "affinity": 78,
  "confidence_band": "medium",
  "evidence_count": 11,
  "components": {
    "coverage": 0.82,
    "depth": 0.71,
    "behavior": 0.74,
    "interest": 0.66
  },
  "strongest_competencies": ["FOR-011", "NET-035"],
  "gaps": ["TH-003", "SOC-001"],
  "why": [
    "8 of 10 critical competencies have practitioner evidence.",
    "Consistency and investigation signals are above the pathway median.",
    "Voluntary forensics work is the strongest interest signal."
  ],
  "formula_version": "affinity-2026.1",
  "weights": { "...": "the exact weights used" }
}
```

## 7. API contracts

All endpoints are owner-only, `Cache-Control: no-store`, and gated by the
`cyber_dna_v3_enabled` platform setting (default `false` until rollout).

### 7.1 Evidence

`GET /api/profile/evidence?competency_id=&domain=&limit=50&offset=0`

```json
{
  "version": "evidence-2026.1",
  "items": [
    {
      "evidence_id": 1234,
      "competency_id": "NET-011",
      "competency_name": "IPv4 Addressing",
      "domain_id": "NET",
      "lab_id": 27,
      "lab_name": "RDP Brute Force Attack",
      "score_contribution": 2.13,
      "mapping_weight": 0.5,
      "attempts": 1,
      "hints_used": 0,
      "time_spent_minutes": 42,
      "practised_at": "2026-11-15T20:00:00Z",
      "source": "live"
    }
  ],
  "total": 1
}
```

### 7.2 Behavior

`GET /api/profile/behavior`

```json
{
  "version": "behavior-2026.1",
  "window_days": 30,
  "signals": {
    "persistence": { "value": 91, "sample_size": 9, "confidence": "medium" },
    "independence": { "value": 88, "sample_size": 9, "confidence": "medium" },
    "speed": { "value": 73, "sample_size": 8, "confidence": "medium" },
    "consistency": { "value": 80, "sample_size": 3, "confidence": "low" },
    "investigation": {
      "value": 95,
      "sample_size": 9,
      "confidence": "medium",
      "kind": "proxy",
      "note": "Exploration breadth from distinct categories and attempt depth; not telemetry."
    }
  },
  "weights": { "...": "formula constants" }
}
```

### 7.3 Interest

`GET /api/profile/interest`

```json
{
  "version": "interest-2026.1",
  "available": true,
  "voluntary_completions": 14,
  "vector": { "malware": 91, "forensics": 82, "web": 22 },
  "basis": "voluntary lab categories, recency weighted",
  "note": "Optional answers are not stored in v3."
}
```

### 7.4 Affinity

`GET /api/profile/affinity?pathway_id=soc-analyst`

Returns the object in 6.4, or a list with `?all=true`. Owner-only; no cohort
comparison, no ranking, no public endpoint.

### 7.5 Snapshots

The existing endpoints remain:

- `GET /api/profile/snapshots?kind=behavior_profile|interest_profile|career_affinity`
- `GET /api/profile/snapshots/{id}`
- `GET /api/profile/snapshots/{id}/markdown` / `/html` (only for
  `career_dossier` and `portfolio`; new kinds return JSON only)

Export generation records the relevant snapshot and returns
`X-OCR-Snapshot-ID` as it does today. A new snapshot kind does not require a
migration.

## 8. Anti-gaming and fairness

1. **Server-verified events only.** Evidence is created from a verified flag
   completion; the client cannot post a score.
2. **One row per completion and competency.** Replays are idempotent.
3. **Caps per lab.** A lab contributes at most once to a competency score.
4. **Time and attempt sanity.** Completions under 60 seconds, duplicate
   sessions, or impossible concurrency are flagged and excluded from behavior,
   not deleted from history.
5. **Hints reduce independence, not competency evidence.** A hinted solve still
   proves exposure; it does not prove independence.
6. **No cohort ranking.** Affinity is owner-only and never shown in a
   scoreboard, leaderboard, or instructor ranking.
7. **Minimum evidence.** No percentages below 3 practices; no affinity below 8
   critical-evidence points; no behavior score below its sample minimum.
8. **No retroactive rewrite.** Snapshots store formula and mapping versions.
9. **Interest is voluntary.** Assigned labs do not count toward interest;
   optional answers are not persisted in v3.
10. **Explainability.** Every score returns its evidence count, contributing
    labs, formula version, and weights.

## 9. Privacy and retention

- Evidence, behavior, interest, and affinity are personal data. Owner-only.
- Erasure deletes `evidence_records` with the account (FK cascade and the
  explicit erasure list) and records the deletion in the ledger.
- Snapshots are deleted with the account.
- No employer, public, or cross-tenant endpoint is part of v3.
- The data dictionary and privacy notice must add the new table and the new
  snapshot kinds before rollout.
- FERPA/minor rules apply unchanged: no public display, no cohort comparison.

## 10. Migration and rollout

1. **Schema.** Migration `0032_evidence_records` (idempotent, additive). No
   changes to existing tables.
2. **Backfill.** Dry-run on a copy, then dev; idempotent by unique key. Record
   counts and skips in the deployment log.
3. **Feature flag.** `cyber_dna_v3_enabled = false` by default. Phase 1 exposes
   APIs only; the UI stays on the existing DNA and radar.
4. **Writes.** Add evidence creation to the completion path after the
   existing `LabCompletion` insert, in the same transaction. A failure to write
   evidence must not fail the completion; it is logged and retried by a
   reconciliation job.
5. **Snapshots.** Record `behavior_profile`, `interest_profile`, and
   `career_affinity` on export or explicit request.
6. **UI.** Phase 2 adds a learner-facing “Evidence and affinity” panel. No
   employer view.
7. **Rollback.** Set the flag false; the table and backfilled rows remain,
   inert. Drop the table only in a later destructive migration.

## 11. Testing

- Unit tests for each formula at boundary values, nulls, and saturation.
- DB tests for idempotent evidence writes, cascade deletion, and backfill.
- Snapshot tests: immutable payload, formula version, owner scoping.
- API tests: auth, feature flag, no-store headers, pagination.
- Anti-gaming tests: duplicate completion, sub-minute completion, replay.
- Privacy test: erasure removes evidence, behavior, interest, and affinity.
- Migration test: `0032` runs on a schema stamped at `0031`.

## 12. Open questions

1. **Behavior weights.** The first constants are proposals; calibrate them
   against a term of learner evidence before calling them stable.
2. **Speed baseline.** Use track median or difficulty median? Proposal:
   difficulty median within the same track, falling back to global.
3. **Interest minimum.** Five voluntary completions may be too low for a
   stable vector; confirm after one term.
4. **Investigation telemetry.** If RangeBox command or workbook-step telemetry
   is ever collected, it needs a separate privacy review and consent.
5. **Cohort context.** Instructors may want aggregate gaps. That is a separate
   aggregate endpoint with suppression, not part of this RFC.

## 13. Acceptance criteria

- A completed lab produces one evidence row per mapped competency, idempotently.
- Competency scores reproduce from evidence rows and stored weights.
- Behavior signals expose value, sample size, confidence, and proxy labeling.
- Interest is null until the minimum voluntary sample is met.
- Affinity returns components, gaps, confidence band, and formula version.
- No endpoint returns a probability, a rank, or an employer view.
- Erasure removes every new row and snapshot.
- The existing DNA, GPS, radar, and report flows are unchanged when the flag is
  off.
