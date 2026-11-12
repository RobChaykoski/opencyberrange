# Career Atlas and Momentum

Status: **Development preview** on the development host. Production keeps the
feature off until this review is signed off.

Audience: learners, instructors, programme leads, and administrators.

Related: [Skill DNA](SKILL-DNA.md),
[Career and certification resources](CAREER-AND-CERTIFICATION-RESOURCES.md),
[Programme reports](PROGRAMME-REPORTS.md), and
[Analytics governance](ANALYTICS-GOVERNANCE.md).

## Why this layer exists

Cyber DNA answers "what have I practised?" It is deliberately a character
sheet, not a grade. Two questions were still missing:

1. **Where is practice gaining or under friction right now?** A learner can see
   a trait score but not whether hints, reattempts, time pressure, or unfinished
   exercises are concentrated in one branch.
2. **What kind of work does this practice resemble, and what does it pay?**
   Affinities name a direction. They do not show a role ladder, a next practice
   step, or the labour-market context around that direction.

Momentum and the Career Atlas add those two layers. They **do not change the
Cyber DNA formula**.

| Layer | Version | What it answers | Changes trait scores? |
|---|---|---|---|
| Cyber DNA | `2026.14` | What have I practised? | Yes, by design |
| Momentum | `2026.1` | Where is practice gaining or under friction? | No |
| Career Atlas | `2026.1` | Which career families and roles does that practice resemble? | No |

## Development-only gate

The surfaces are controlled by the platform setting
`advanced_dna_insights_enabled` in **Admin -> Settings -> Features**. The default
is `false`.

- Development host: enable it for review.
- Production: keep it `false` until the review checklist below is complete.
- Turning it off hides the Momentum panel, the **Careers** tab, and the extended
  career-dossier sections. It does not delete learner records.
- The gate is read with `get_setting_fresh`, so every worker sees an
  administrator's change immediately.

The same code ships to every deployment. The setting, not a branch or an
environment variable, decides whether the surface is visible.

## Momentum and friction

### Data sources

Momentum reads only existing records for the signed-in learner:

- `lab_completions` — completed exercises, hints, attempts, time, completion
  time;
- `lab_sessions` — exercises opened but not completed;
- `labs.duration_minutes` — the exercise estimate used for time pressure.

No new tracking is added.

### Definitions

| Signal | Definition |
|---|---|
| Completed | Completed exercises in the branch. |
| Started | Union of exercises with a session and exercises with a completion. |
| Unfinished | Started exercises with no completion. |
| Hint rate | Completions with at least one hint / completions. |
| First-attempt rate | Completions with one attempt / completions. |
| Time ratio | Median of `time_spent_minutes / duration_minutes` for completions with both values. |
| Clean solve | No hints and one attempt. |
| Movement | Recent-half clean-solve rate minus earlier-half clean-solve rate, in percentage points. |

### Friction score

```text
friction = 100 × (
    0.35 × hint_rate
  + 0.35 × (1 - first_attempt_rate)
  + 0.20 × unfinished_rate
  + 0.10 × min(max(time_ratio - 1, 0) / 1.5, 1)
)
```

Every rate is a proportion from 0 to 1. The score is capped at 0–100. The
weights sum to 1.0. The score is descriptive; it is not a grade.

### Status

| Status | Rule |
|---|---|
| Gaining | Movement at least +8 points and friction below 55. |
| Friction | Friction at least 55, or movement at most -8 points. |
| Steady | Evidence exists and neither rule applies. |
| No evidence yet | No completed or started exercises in the branch. |

A branch with no evidence is never shown as a zero.

### Stuck points

Up to three exercises are named, with a reason:

- started but not finished;
- high hint use (two or more hints);
- repeated attempts (three or more);
- took much longer than the estimate (two times or more).

These are review prompts, not labels. The copy never asserts that a learner used
outside help, failed, or is disengaged.

## Career Atlas

### Career families

The atlas has eleven families across the six Cyber DNA branches:

| Branch | Families |
|---|---|
| Explorer | Threat Intelligence / OSINT |
| Builder | Application Security, Cloud Security, Identity & Access Management |
| Tester | Offensive Security / Penetration Testing |
| Defender | Defensive Security / SOC, OT / ICS Security |
| Investigator | DFIR / Investigation, AI Security |
| Leader | Security Leadership / Education, Governance, Risk & Compliance |

Each family has an entry, core, and advanced role ladder. Roles are broad
examples, not a job ontology.

### Matching

```text
match = min(100,
    60 × min(affinity_evidence_count, 6) / 6
  + 40 × average(dimension scores for the family) / 100
)
```

- `affinity_evidence_count` comes from the existing Cyber DNA affinity evidence.
- `dimension scores` are the existing 0–100 Cyber DNA branch scores.
- A family with no affinity uses the dimension term only.

Unlock states:

| State | Threshold | Meaning |
|---|---|---|
| Unlocked | match >= 35 | The learner has enough practice evidence to explore the family. |
| One step away | 15 <= match < 35 | A small amount of additional practice moves the node. |
| Locked | match < 15 | The branch has little or no evidence. The node remains readable. |

The recommended family is the highest match with a non-zero score. It is a
practice suggestion, not a prediction.

### Salary bands

Salary data is curated from official public sources. It is static in the code
and versioned with the atlas.

| Region | Source | As of | Basis |
|---|---|---|---|
| Canada | Canada Job Bank / Statistics Canada Labour Force Survey | 2025-11-19 | National low, median, and high hourly wages for the 2023–2024 reference period, annualised at 2,080 hours. |
| United States | U.S. Bureau of Labor Statistics OEWS, May 2025 | 2026-05-15 | National annual 10th, 50th, and 90th percentiles via O*NET OnLine. |

Rules:

- Show the official occupation code or title beside the band.
- Show the currency, region, source, and as-of date.
- Low is the 10th percentile, not entry-level pay.
- The band is a national planning range, not an offer, a starting salary, or a
  prediction.
- Regional, sector, experience, certification, and employer differences are
  large.
- Verify every figure with the source before using it in an application,
  advising conversation, or programme decision.

### Salary table and print output

The UI includes an expandable salary table for all roles and both regions. The
career dossier Markdown and printable HTML include the same data, with the source
notes. The table is a table alternative to the visual salary lens, so the
information is available without colour or pointer interaction.

## Privacy, ethics, and limits

- The profile and dossier are private to the learner and staff who already have
  user-detail access.
- The atlas is descriptive. Do not use it for admissions, hiring, ranking,
  discipline, or any high-stakes decision.
- Do not use salary bands to set a learner's expectation or to imply a promise of
  employment.
- A locked family is a route to explore, not a negative label.
- No new learner data is collected. The feature reads existing records.
- The dossier exports are logged and send `Cache-Control: no-store`.
- The feature is off by default in production.

## API and data contract

When the setting is on, `GET /api/profile/skill-dna` and the `skill_dna` object in
`GET /api/profile/summary` include:

```text
momentum: {
  version, window, summary, branches, gaining, friction,
  stuck_points, next_move, disclaimer
}
career_atlas: {
  version, regions, sources, summary, branches, families,
  recommended_family_key, disclaimer, salary_note
}
```

`GET /api/profile/career-dossier`, `.md`, and `.html` include `momentum` and
`career_atlas` when the setting is on. They omit the keys when it is off.

The API returns only the signed-in learner's own data. There is no staff-wide
atlas endpoint and no cross-learner ranking.

## UI design

- The atlas is a skill tree, not a dashboard table: six branch lanes, a central
  class core, progress rings, lock/spark/check glyphs, and a detail panel.
- Unlocked, one-step-away, and locked states use text, shape, and colour. Colour
  is never the only signal.
- The salary lens is a range bar with low, median, and high labels, plus a table
  alternative.
- Both dark and light themes use the existing tokens. No second palette is
  introduced.
- The layout is verified at 375, 768, 1024, and 1440 px.
- Motion is limited to progress and selection transitions and respects
  `prefers-reduced-motion: reduce`.
- The nodes are native buttons with visible focus and `aria-pressed` selection
  state. Progress bars expose `role="progressbar"` and text values.

## Review checklist before production

- [ ] Institutional review of career framing and salary data.
- [ ] Confirm the salary sources and as-of dates are current for the release.
- [ ] Confirm the Canadian and US occupation mappings with a subject-matter
      reviewer.
- [ ] Run the backend tests for Momentum and Career Atlas.
- [ ] Run frontend lint and build.
- [ ] Verify dark and light themes at 375, 768, 1024, and 1440 px.
- [ ] Verify keyboard order and visible focus on every node, role card, region
      switch, and table toggle.
- [ ] Verify the empty state (no evidence) and the locked state.
- [ ] Verify the feature-off state: no Careers tab, no Momentum panel, no new
      dossier sections.
- [ ] Verify the career dossier Markdown and HTML escape learner-controlled
      values.
- [ ] Record the review date and approver in the release notes.

## Deployment notes

The feature is enabled on the development host only:

1. Pull the reviewed tree on the development host using the commands in
   [Deployment runbook](DEPLOYMENT-RUNBOOK.md).
2. Build and restart the backend and frontend with the root Compose files.
3. In **Admin -> Settings -> Features**, set **Advanced DNA Insights** to
   **Enabled**. On the development host you can also run
   `bash scripts/dev-insights.sh on`.
4. Reload the profile and verify the **Careers** tab and the Momentum panel.
5. Capture the manual screenshots with
   `scripts/ui-manual-screenshots.mjs` (see [Next steps](NEXT-STEPS.md)).
6. Leave production on the default **Disabled** until the checklist is signed
   off.
