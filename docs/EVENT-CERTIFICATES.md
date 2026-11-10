# Event certificates

Event certificates are awarded to opted-in competition participants after the
event ends. They reuse the competition record, its logo, and its sponsors, so a
single event can issue participation, placement, and trophy-challenge
certificates without a separate certificate table.

## Award types

| Award key | Certificate ID code | Required event badge | Meaning |
| --- | --- | --- | --- |
| `participation` | `p` | none | Joined and took part in the event |
| `first` | `1` | `ch` (Champion) | Finished first |
| `second` | `2` | `ru` (Runner-up) | Finished second |
| `third` | `3` | `tp` (Third Place) | Finished third |
| `first_blood` | `fb` | `fb` (Event First Blood) | First solve in the event |
| `clean_sweep` | `cs` | `cs` (Event Clean Sweep) | Solved every event exercise |
| `perfect` | `pr` | `pr` (Perfect Event) | Every event exercise without hints, first attempt |

Participation is always available to an eligible participant. Placement and
trophy awards require the matching `comp_<competition_id>_<code>` achievement,
so a learner cannot claim an award they did not earn.

## Eligibility

A certificate is issued only when:

1. The account is active and approved.
2. The learner has an explicit `CompetitionParticipant` opt-in.
3. The competition `end_at` has passed.
4. For placement or trophy awards, the matching event achievement exists.
5. Public verification is enabled on the account for the public verifier to
   confirm the certificate.

Before the event ends, the API returns `409` with
`Event certificates are available after the event ends.` A learner who has not
joined receives `403`.

## Certificate ID

```
OCR-EVT-<competition_id>-<user_id>-<award_code>-<digest>
```

`digest` is the first 10 uppercase hex characters of
`SHA-256("<user_id>:event:<competition_id>:<award_key>")`. The ID is
deterministic: re-downloading a certificate produces the same ID. The public
verifier recomputes it and rejects tampered digests.

Examples:

```
OCR-EVT-12-34-p-3F9A0C1B22
OCR-EVT-12-34-fb-7C41D0E9AA
```

## API

| Method | Path | Purpose |
| --- | --- | --- |
| `GET` | `/api/competitions/{id}/certificates` | List the awards the learner earned |
| `GET` | `/api/competitions/{id}/certificate/{award}` | Certificate JSON |
| `GET` | `/api/competitions/{id}/certificate/{award}?format=pdf` | Certificate PDF |
| `GET` | `/api/exercises/verify/certificate/{certificate_id}` | Public verification |

The JSON payload includes:

- `kind`: `event`
- `certificate_id`, `award`, `award_label`, `award_description`
- `title`, `role_label`, `body_line`
- `recipient`, `event_name`, `event_start`, `event_end`, `event_dates`
- `event_logo` (data URL or `null`)
- `sponsors`: ordered list of `{name, logo_data, tier}`
- `issued_on`, `issued_display`, `issuer`
- `public_verification`, `verify_url`, `qr_code`

Public verification returns event and award metadata only. It never returns
scores, usernames, email addresses, or account identifiers.

## Logos and sponsors

- The event logo is `Competition.logo_data`.
- Sponsors are `CompetitionSponsor` rows, ordered gold, silver, bronze, then
  `sort_order` and name.
- The PDF renders up to six sponsor marks. Images are decoded from data URLs,
  converted to PNG, and never fetched from a remote host.
- The in-app certificate shows the event logo in place of the SWOCTS mark and a
  "Supported by" sponsor strip.

## Privacy

Event certificates respect the account's `certificates_public` setting:

- The holder can always open and download their own certificate.
- When public verification is disabled, the payload omits `verify_url` and
  `qr_code`, and public verification returns the generic invalid result.
- Verification confirms the event, award, recipient display name, event dates,
  issue date, and certificate ID. It does not expose standings or scores.

## Frontend routes

- `/certificate/event/:eventId/:award` renders and downloads an event
  certificate.
- `/verify/certificate/:certificateId` accepts both track and event IDs.
- The competition detail page lists available certificates after the event ends.

The verification form validates the ID shape in the browser before enabling
**Verify**:

- track: `OCR-<track prefix>-L<level>-<10 hex>`
- event: `OCR-EVT-<competition>-<user>-<award code>-<10 hex>`

The backend remains the authority and re-validates the format and digest.

## Tests

`platform/backend/tests/test_event_certificates.py` covers:

- participation, placement, and trophy certificate listings;
- JSON and PDF output;
- public verification and tampered IDs;
- certificate opt-out;
- `409` before the event ends;
- `403` for a non-participant.
