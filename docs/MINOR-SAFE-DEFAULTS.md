# Minor-safe defaults (Grades 9-12)

Audience: curriculum designers, instructors, and platform operators who deliver
the Beginner Cybersecurity / Grades 9-12 stream.

The platform cannot infer a learner's age. It can enforce a conservative
default for the minor-facing pathway and fail the build if adult content leaks
into it.

## Defaults

Every `platform/labs/High School/*/lab.yaml` declares:

```yaml
audience: grades_9_12
offline_only: true
external_targets: []
personal_data: none
free_text: false
public_profiles: false
phone_required: false
analytics: aggregate_only
minor_safe_defaults: true
```

The current High School stream has 18 labs across four chapters. A deployment
may show a smaller visible subset depending on the course, level, or assigned
labs; the six Grade 10 labs are the only subset that explicitly sets
`counts_toward_certificate: true`. The governance applies to every High School
lab in the repository, not only the currently visible ones.

A lab that cannot meet these defaults does not belong in the stream; move it to
an adult track or provide an offline, synthetic replacement.

## What the defaults mean

- **Offline only.** Every target is a lab host or a reserved documentation
  address. No High School lab requires a live public site.
- **No personal data.** The labs use fictional people, `.example` addresses,
  reserved documentation IP ranges, and synthetic images.
- **No free text.** A learner cannot type a real password, recovery answer, or
  personal fact into a High School target. The MFA recovery lab uses a fixed
  choice list.
- **No public profiles or phone OSINT.** Those exercises are adult-only and are
  in the OSINT track, not the minor-facing pathway.
- **Aggregate-only analytics.** Existing under-18 exclusions from reports,
  analytics, and public leaderboards continue to apply.
- **No live targets.** The OSINT live targets are adult-only, visibility
  `course`, and must be assigned by an instructor. A learner who declares
  themselves under 18 does not see `category: osint` labs.

## High School wiki scope

`mkdocs-highschool.yml` builds from the shared `Workbook` tree, so it uses
`exclude_docs` to keep non-High-School chapters out. The built
`platform/frontend/wiki/range/high-school` tree must contain only the HS
chapters, assets, scripts, and styles. The validator rejects stale OSINT or
malware directories, `linkedin.com/in/`, `instructor-owned`, `profile-qr.png`,
and `swocts.com` in that tree.

## Validation

```bash
python scripts/check-minor-safe.py
```

The check fails if:

- a High School lab is missing or contradicts any default;
- a High School lab is categorised as OSINT;
- a scenario, hint, or test contains a non-local URL;
- real location data appears in the metadata;
- an advanced OSINT lab is not `audience: adult` and `visibility: course`;
- the High School wiki has no `exclude_docs`, or still contains OSINT/malware
  pages, the instructor-profile QR, or live-target text.

## Operational rules

1. Assign the High School pathway only to a minor cohort.
2. Do not assign OSINT 2.x labs to Grades 9-12. They are instructor-assigned
   adult extensions.
3. Keep the High School wiki rebuild in the deploy path. A stale built tree is
   a privacy defect even when the source is correct.
4. Review any new external target against
   `platform/backend/app/data/external-targets.yaml`. A live target must have an
   offline mirror, a content hash, and a daily check.
5. Report a safety concern through the institution's safeguarding channel, not
   in a public issue.
