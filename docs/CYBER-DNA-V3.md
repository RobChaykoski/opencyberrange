# Cyber DNA v3 — talent discovery graph

Status: **Phase 1 implemented; the Phase 2 learner UI shipped in v5.31.0 and is
live in 5.56.1.** Development has the v3 surface and evidence; production has
the feature flag on with a small consenting cohort. No consenting learner meets
the affinity gate yet. The next work is Phase 3 weight tuning after a term of
evidence, not UI delivery. See the production state below.

Owner: OpenCyberRange curriculum and platform
Target: Release 5.17 line (phased)
Decision log:

- The output is **career affinity**, not a probability.
- The **employer view is out of scope**.
- **Cyber DNA is a separate bounded context.** It does not read exercise
  tables and has no foreign keys into them. The exercise platform emits a
  versioned activity event; Cyber DNA owns the evidence, behavior, interest,
  affinity, and snapshots.
- Affinity is **hidden until 30+ labs, 3+ domains, and 100+ competency
  observations**. No score is shown below the gate.
- Evidence is append-only; snapshots are immutable and versioned.

## 1. Summary

The current Cyber DNA implementation is not a badge engine. It already has a
competency taxonomy, an eight-axis evidence radar, six DNA traits, growth
velocity, career pathways, role readiness, a portfolio, and immutable report
snapshots. What it lacks is a first-class **evidence record**, a persisted
**behavior profile**, a persisted **interest vector**, and a **career-affinity
score with confidence**.

This RFC adds those layers as an independent context. It answers:

> What kind of cybersecurity work does this learner's evidence point toward,
> how strong is the evidence, and what should they try next?

It does not answer:

> What job will this learner get?

## 2. Goals and non-goals

### Goals

- Own a competency vocabulary, evidence ledger, behavior, interest, affinity,
  and snapshots in one extractable module.
- Accept only versioned activity events from the exercise platform.
- Store evidence once per event and competency, idempotently.
- Gate affinity until enough evidence exists to make it meaningful.
- Make every score explainable with evidence counts, contributing activities,
  formula version, and weights.
- Preserve historical reports through DNA snapshots.
- Stay owner-only and privacy-first.

### Non-goals

- Employer or recruiter access, public profiles, or hiring recommendations.
- A probability of employment or a prediction of job performance.
- Ranking learners against each other.
- Telemetry from inside RangeBox (keystrokes, shell history, packet captures).
  Investigation is a documented exploration proxy.
- Replacing `skill_dna`, `cyber_gps`, `competency_radar`, or role readiness.
- Reading `labs`, `lab_completions`, `courses`, or enrollments from the DNA
  service.

## 3. Bounded context

```
Exercise platform                         Cyber DNA context
-----------------                         ------------------
labs, workbooks, tracks, courses          competency vocabulary
completions, attempts, hints, time   --->  evidence ledger (dna_evidence_records)
course assignments, voluntary flag        behavior / interest / affinity
                                          snapshots (dna_snapshots)
```

Rules:

1. **Exercise content owns the mapping.** The adapter resolves a lab or
   workbook chapter to competency IDs and emits an event. Cyber DNA never loads
   `competency-mapping.yaml` or a `Lab` row.
2. **No shared foreign keys.** `learner_id` is a plain integer in DNA tables.
   There is no FK to `users`, `labs`, `lab_completions`, or `courses`.
3. **One direction.** Exercise code calls DNA ingestion. DNA code does not
   import exercise models, routers, or services.
4. **Erasure is explicit.** The erasure service calls
   `cyber_dna.erase_learner(learner_id)`; there is no database cascade across
   the boundary.
5. **Extractable.** The package can move to its own service and schema by
   replacing the ingestion call with an HTTP/queue consumer.

## 4. Event contract

`app/cyber_dna/events.py` — `ActivityCompleted`, version `2026.1`.

| Field | Type | Meaning |
|---|---|---|
| `event_id` | string | Stable idempotency key, e.g. `completion:1234` |
| `learner_id` | int | Platform user id; no PII |
| `activity_id` | string | Opaque activity id, usually the lab slug |
| `activity_category` | string | Neutral category used for interest and speed baselines |
| `competency_weights` | map[str, float] | Competency IDs and normalized shares |
| `difficulty` | string | beginner / intermediate / advanced / expert |
| `attempts` | int | Attempts before success |
| `hints_used` | int | Hints used |
| `duration_minutes` | int? | Active time, if known |
| `prior_failed_attempts` | int | Failed attempts before success |
| `voluntary` | bool | Not assigned to an active course enrollment |
| `occurred_at` | datetime | Activity completion time (naive UTC) |
| `source_version` | string | Exercise adapter version |

The adapter in `app/services/dna_events.py` is the only exercise-side reader.
It maps the lab to competencies, checks active course assignments for the
`voluntary` flag, and counts prior failed attempts.

## 5. Data model

### 5.1 `dna_evidence_records` (migration `0032_cyber_dna`)

| Column | Type | Notes |
|---|---|---|
| `id` | integer PK | |
| `learner_id` | integer | plain id, indexed, no FK |
| `event_id` | varchar(120) | idempotency key |
| `activity_id` | varchar(160) | opaque activity id |
| `activity_category` | varchar(64) | neutral category |
| `competency_id` | varchar(32) | taxonomy ID |
| `domain_id` | varchar(16) | taxonomy domain |
| `mapping_weight` | float | normalized share from the event |
| `score_contribution` | float | `difficulty * weight * independence` |
| `difficulty` | varchar(20) | event snapshot |
| `attempts` | integer | event snapshot |
| `hints_used` | integer | event snapshot |
| `duration_minutes` | integer? | event snapshot |
| `prior_failed_attempts` | integer | event snapshot |
| `voluntary` | boolean | event snapshot |
| `source_version` | varchar(32) | adapter version |
| `occurred_at` | datetime | completion time |
| `created_at` | datetime | server time |

- `UNIQUE (event_id, competency_id)` makes replay a no-op.
- Indexes: `(learner_id, competency_id, occurred_at)`, `(learner_id, occurred_at)`.
- Append-only. A correction is a new event, never an update.

### 5.2 `dna_snapshots`

| Column | Type | Notes |
|---|---|---|
| `id` | integer PK | |
| `learner_id` | integer | no FK |
| `kind` | varchar(32) | behavior_profile / interest_profile / career_affinity |
| `schema_version` | varchar(32) | |
| `formula_version` | varchar(32) | |
| `weights` | text JSON | exact weights used |
| `payload` | text JSON | immutable payload |
| `content_sha256` | varchar(64) | content hash, generation metadata excluded |
| `created_at` | datetime | |

- `UNIQUE (learner_id, kind, content_sha256)` deduplicates unchanged reports.
- Snapshots are JSON only; there is no Markdown/HTML renderer for v3 kinds.

### 5.3 Backfill

`scripts/backfill-evidence.py` is an **exercise-side adapter**. It reads existing
completions, builds the same `ActivityCompleted` event, and calls DNA ingestion.
It is idempotent. DNA never reads the completions table itself.

## 6. Scoring model

Notation:

- `d` difficulty weight: beginner 1.0, intermediate 1.5, advanced 2.0, expert 2.5.
- `m` normalized competency share from the event.
- `i` independence multiplier: `1.0 + 0.35 * clean + 0.20 * first_attempt`.
- `r` recency: 1.0 (≤14 days), 0.99 (≤30), 0.97 (≤60), 0.94 (≤90), 0.90 (>90).
- `E_c = Σ (d * m * i * r)` for competency `c`.

### 6.1 Competency score

```
score_c = round(100 * (1 - exp(-E_c / 4)))
```

Saturating by design. Examples: `E=1 → 22`, `E=2 → 39`, `E=4 → 63`,
`E=8 → 86`, `E=12 → 95`; cap 99.

| Score | Band | Meaning |
|---:|---|---|
| 0–24 | Awareness | Recognises the term |
| 25–44 | Foundational | Guided procedure completed |
| 45–64 | Practitioner | Applied in a familiar exercise |
| 65–84 | Specialist | Applied under friction with evidence |
| 85–99 | Lead | Repeated, varied, current evidence |

Every score carries `evidence_count` and `last_practised_at`.

### 6.2 Behavior profile

Computed from events in the last 30 days. One representative row per event.

| Signal | Formula | Minimum |
|---|---|---|
| Persistence | `100 * (0.6 * attempt_depth + 0.4 * recovery)`; `attempt_depth = min(1, (mean_attempts - 1) / 6)`; `recovery = share of events with ≥5 prior failures` | 5 events |
| Independence | `100 * (0.6 * hint_free_rate + 0.4 * (1 - min(hints_per_event, 5) / 5))` | 5 events |
| Speed | `100 * (mean(clamp(median_for_category_and_difficulty / duration, 0.5, 1.5)) - 0.5)` | 5 timed events |
| Consistency | `100 * min(active_weeks / 4, 1)` | 2 active weeks |
| Investigation proxy | `100 * (0.6 * min(distinct_categories / 6, 1) + 0.4 * attempt_depth)` | 5 events; **proxy only** |

Each signal returns `value` (or null), `sample_size`, and `confidence`.

### 6.3 Interest vector

Only `voluntary=true` events. Recency-weighted category shares. Minimum 5
voluntary events across 2 categories; otherwise `available=false` and an empty
vector. Optional survey answers are not stored in v3.

### 6.4 Career affinity — gated

**Affinity is not computed or shown until all three thresholds are met:**

| Gate | Minimum |
|---|---:|
| Distinct completed activities | **30 labs** |
| Competency domains with evidence | **3 domains** |
| Competency observations (evidence rows) | **100 observations** |

Below the gate the API returns:

```json
{
  "available": false,
  "gate": {
    "labs": {"have": 6, "need": 30},
    "domains": {"have": 3, "need": 3},
    "observations": {"have": 12, "need": 100}
  },
  "pathways": [],
  "disclaimer": "Career affinity unlocks at 30 labs, 3 domains, and 100 competency observations."
}
```

This prevents the common failure mode of predicting a career after five
exercises. The gate is learner-wide, not per pathway.

Once the gate is met:

```
coverage = Σ critical_weight * [score >= 60] / Σ critical_weight
depth    = Σ critical_weight * min(score / 100, 1) / Σ critical_weight
behavior = Σ behavior_weight * signal / 100
affinity = 100 * (0.50 * coverage + 0.20 * depth
                  + 0.15 * behavior + 0.15 * interest)
```

- Missing behavior or interest components are dropped and the remaining
  weights renormalize.
- `confidence_band` is low/medium/high from the number of critical
  competencies with evidence. It is an evidence band, never a probability.

## 7. API contracts

Prefix: `/api/dna`. All learner endpoints are owner-only, gated by
`cyber_dna_v3_enabled`, and return `Cache-Control: no-store`.

| Method | Path | Purpose |
|---|---|---|
| GET | `/v3/evidence` | Evidence rows, filterable by competency or domain |
| GET | `/v3/competencies` | Per-competency scores and bands |
| GET | `/v3/behavior` | Five-signal behavior profile |
| GET | `/v3/interest` | Voluntary interest vector |
| GET | `/v3/affinity` | Gated career affinity |
| GET | `/v3/dna` | Aggregate payload |
| POST | `/v3/snapshots?kind=...` | Record a behavior, interest, or affinity snapshot |
| GET | `/v3/snapshots` | List snapshots |
| GET | `/v3/snapshots/{id}` | Stored payload and weights |

Example affinity payload when the gate is met:

```json
{
  "version": "affinity-2026.1",
  "available": true,
  "gate": {
    "labs": {"have": 34, "need": 30},
    "domains": {"have": 4, "need": 3},
    "observations": {"have": 112, "need": 100}
  },
  "pathways": [
    {
      "pathway_id": "soc-analyst",
      "title": "SOC Analyst",
      "affinity": 78,
      "confidence_band": "medium",
      "evidence_count": 11,
      "components": {"coverage": 0.82, "depth": 0.71, "behavior": 0.74, "interest": 0.66},
      "strongest_competencies": ["FOR-011", "NET-035"],
      "gaps": ["TH-003", "SOC-001"],
      "why": ["8 of 10 critical competencies have practitioner evidence."],
      "formula_version": "affinity-2026.1",
      "weights": {"coverage": 0.5, "depth": 0.2, "behavior": 0.15, "interest": 0.15}
    }
  ]
}
```

## 8. Anti-gaming and fairness

1. Evidence is accepted only through the server-side adapter or backfill; the
   browser cannot post an event.
2. `event_id + competency_id` is unique; replay is a no-op.
3. One event contributes at most once per competency.
4. Hints reduce independence, not competency evidence.
5. Sub-minute or impossible durations are flagged by the adapter and excluded
   from behavior; the evidence row remains for audit.
6. No cohort ranking, public leaderboard, or instructor ranking.
7. Affinity is hidden below 30 labs / 3 domains / 100 observations.
8. No retroactive rewrite: formula and weights are stored with each snapshot.
9. Interest uses voluntary activities only; assigned labs are excluded by the
   adapter.
10. Every score returns its evidence count, contributing activities, formula
    version, and weights.

## 9. Privacy and retention

- DNA rows carry `learner_id` but no name, email, or exercise prose.
- Owner-only APIs; no employer or public endpoint in v3.
- Erasure calls `cyber_dna.erase_learner(learner_id)` and removes evidence and
  snapshots before the user row is deleted.
- The data dictionary documents the DNA tables and the new feature flag.
- FERPA/minor rules are unchanged: no public display, no cohort comparison.

## 10. Migration and rollout

1. Migration `0032_cyber_dna` creates `dna_evidence_records` and
   `dna_snapshots`. It is additive and idempotent.
2. Evidence ingestion is live on the completion path and must not fail the
   completion; failures are logged and repaired by the backfill adapter.
3. The read APIs are gated by `cyber_dna_v3_enabled` (default false).
4. Backfill: dry-run on a copy, then dev, then production. Idempotent.
5. Phase 2 adds the learner UI; it shipped in v5.31.0 as the Profile career
   affinity panel and the dashboard DNA band, with consent and gate states.
   Phase 3 tunes the behavior weights and the affinity formula after a term of
   evidence.
6. Rollback: set the flag false. Tables remain inert. Dropping them is a later
   destructive migration.

### Phase 1 development rollout — 2026-11-15

- Migration `0032_cyber_dna` applied to development; both DNA tables exist.
- Backfill dry-run and write: 233 completions, 740 evidence rows, 53 learners,
  63 activities, 9 domains. Fourteen completions had no competency mapping and
  were skipped.
- `cyber_dna_v3_enabled` enabled on development only.
- API verification with a real learner: 170 evidence rows, behavior signals
  populated, interest available, affinity gate met (39 labs, 8 domains, 170
  observations) with 13 pathways; a low-evidence learner correctly returned
  `available: false` at 4 labs, 1 domain, 16 observations.
- A behavior snapshot was recorded, read back, and removed after the test.

### Production state - 2026-11-22

- `cyber_dna_v3_enabled=true` and `advanced_dna_insights_enabled=true` on
  production, although both settings default to false.
- The first production backfill (dry run 130 completions, 274 rows) bypassed the
  consent gate and wrote 271 rows for 15 learners, including 12 learners with no
  granted consent. The live completion path already checked consent; the
  backfill adapter did not.
- The 230 rows belonging to the 12 non-consenting learners were purged with
  `erase_learner`. `dna_evidence_records` now holds 44 rows for the 3 consenting
  learners (13, 1, and 194), across 11 activities and 3 domains;
  `dna_snapshots` holds 0 rows.
- The consenting data does not meet the affinity gate yet. Learner 13 has 38
  observations, 3 domains, and 11 activities; learners 1 and 194 have 3
  observations each. The API therefore returns `available: false` for every
  consenting learner.
- Fixed in 5.30.2: the backfill is now a shared `backfill_completions` service
  that applies `consent_allows_processing` per learner, and a regression test
  proves a revoked learner's surviving completion cannot recreate evidence
  after the purge.
- HTTP verification after the fix: the four `/api/dna/v3/*` read endpoints
  return `200` for a consenting student, with the affinity gate reporting
  `available: false` (1/30 labs, 2/3 domains, 3/100 observations). A revoked
  learner receives `403 ConsentRequired` from the consent middleware.
- The Phase 2 learner UI is not shipped, so the enabled read APIs have no
  learner-facing surface yet. Keep the flag on for API readiness; the consent
  middleware returns `403` for a revoked learner and the gate hides affinity
  below its thresholds.

### Production state - 2026-11-26

- Production runs `5.56.1` with the Phase 2 learner UI shipped in v5.31.0:
  `/profile` shows the career-affinity panel and the dashboard shows the DNA
  band.
- `cyber_dna_v3_enabled=true` and `advanced_dna_insights_enabled=true`.
- `dna_evidence_records` holds **47 rows for 4 learners**; `dna_snapshots` holds
  **0**. The cohort is still below the affinity gate (30 labs, 3 domains, 100
  observations), so the panel correctly shows the gate rather than a score.
- Development holds 503 rows for 2 learners, also with 0 snapshots; it remains
  the tuning environment.
- Next: let the consenting cohort accumulate evidence, then run Phase 3 weight
  tuning. Re-run the consent-gated backfill after consent changes; it is
  idempotent and will not recreate revoked learners' evidence.

## 10.1 Consent and revocation

Cyber DNA is learner-controlled. The feature gate
(`cyber_dna_v3_enabled`) decides whether the v3 surface ships; consent decides
whether this learner may use it.

- **Central enforcement.** `/api/dna/*`, `/api/profile/skill-dna`,
  `/api/profile/competencies`, and `/api/profile/career-dossier` pass through
  `app/consent/middleware.py` before the route runs. A revoked or purging
  consent returns `403` with `X-Consent-Status`.
- **Ingestion stops immediately.** The exercise-side adapter checks the consent
  state and the suppression ledger before writing evidence. A replayed
  completion after revocation writes zero rows.
- **Revocation deletes derived data.** DNA evidence, DNA snapshots, career
  affinity, and derived reports are removed. Completions, attempts, transcripts,
  certificates, achievements, and course progress are educational records and
  remain.
- **Transactional.** All purge targets for one revocation run in one database
  transaction; a mid-purge failure leaves every table untouched. Verification
  runs immediately, at 24 hours, and at 7 days.
- **Proof, not payload.** The audit records the consent version, completed
  targets, verification slots, and timestamps. It never stores deleted evidence.
- **Suppression wins.** A keyed file ledger blocks restore/replay, and the
  sweep flips a restored `granted` row back to revoked before purging.
- **Re-grant.** New activity may be recorded again; deleted evidence is not
  restored.

The learner UI is **Profile → Security & privacy → AI and career data**. See
[Consent revocation](CONSENT-REVOCATION.md) for the full workflow.

## 11. Testing

- Event validation and normalization.
- Idempotent ingestion; duplicate event is a no-op.
- Competency scores at boundaries and saturation.
- Behavior signals with nulls and small samples.
- Interest below/above the minimum.
- Affinity gate: 29 labs, 2 domains, or 99 observations → unavailable.
- Affinity gate: 30 labs, 3 domains, 100 observations → available.
- Snapshot immutability, dedupe, owner scoping.
- Erasure removes evidence and snapshots.
- API feature gate returns 404 when off.
- Migration `0032` runs on a schema stamped at `0031`.

## 12. Open questions

1. **Behavior weights.** The constants are proposals; calibrate after a term.
2. **Speed baseline.** Category + difficulty median; confirm it is stable.
3. **Interest minimum.** Five voluntary events may be low; confirm.
4. **Investigation telemetry.** If RangeBox telemetry is ever collected, it
   needs a separate privacy review.
5. **Cohort aggregates.** Instructor gap reporting is separate and needs
   suppression; out of scope for v3.

## 13. Acceptance criteria

- The exercise platform emits an event; DNA writes evidence without reading
  exercise tables.
- Replaying an event writes zero rows.
- Competency scores reproduce from evidence and stored versions.
- Behavior returns value, sample size, confidence, and proxy labeling.
- Interest is unavailable below 5 voluntary events or 2 categories.
- Affinity is unavailable below 30 labs, 3 domains, or 100 observations.
- Affinity returns components, gaps, confidence band, and formula version once
  the gate is met.
- No endpoint returns a probability, a rank, or an employer view.
- Erasure removes every DNA row and snapshot.
- The existing DNA, GPS, radar, and report flows are unchanged when the flag is
  off.
