# API error codes

Status: **convention and first migrations.** The frontend still renders
`detail`, so every migrated endpoint keeps its human-readable message. New and
migrated endpoints add a stable `X-Error-Code` header that a client can
translate.

## Contract

```http
HTTP/1.1 400 Bad Request
X-Error-Code: username_taken
Content-Type: application/json

{"detail": "Username already exists"}
```

- `detail` stays human-readable for compatibility and for clients that do not
  read the header.
- `X-Error-Code` is stable, lower_snake_case, and never changes meaning.
- The code is for the client, not for logging. The server still logs the
  request and the actor.
- Do not put a translated sentence in `detail` as the only signal. Add the code
  first, then translate on the client.
- CORS exposes `X-Error-Code` and the existing re-authentication/session
  headers.

## Helper

```python
from app.api_errors import api_error

raise api_error(400, "username_taken", "Username already exists")
```

The helper returns an `HTTPException` with the code header. Existing
`raise HTTPException(...)` sites can migrate incrementally; do not change the
message and the status in the same change.

## Initial codes

| Code | Status | Meaning |
|---|---|---|
| `username_taken` | 400 | The requested username is already in use |
| `email_taken` | 400 | The requested email is already in use |
| `student_id_taken` | 400 | The requested student ID is already in use |
| `account_exists` | 400 | Registration matches an existing account |
| `lab_slug_taken` | 400 | The exercise slug is already in use |
| `reauth_required` | 403 | A recent re-authentication is required |
| `session_invalid` | 401 | The session is expired, revoked, or bound elsewhere |
| `security_version_stale` | 401 | The account security version changed; sign in again |
| `impersonation_read_only` | 403 | A mutating action was blocked during View As |
| `consent_required` | 403 | A consent gate blocks the requested derived-data service |
| `evidence_not_found` | 404 | The evidence record does not exist or is outside the caller's scope |
| `evidence_forbidden` | 403 | The caller cannot review or read this evidence |
| `evidence_learner_not_found` | 404 | The learner id does not exist |
| `evidence_rubric_unknown` | 400 | The rubric id or version is not in the registry |
| `evidence_competency_unknown` | 400 | A competency id is not in the taxonomy |
| `evidence_competency_invalid` | 400 | A competency link has no criteria, a duplicate, or an invalid weight |
| `evidence_source_type_invalid` | 400 | The evidence source type is not supported |
| `evidence_source_not_allowed` | 400 | The rubric does not accept this evidence type |
| `evidence_source_invalid` | 400 | The source id is missing |
| `evidence_confidence_invalid` | 400 | Confidence is not low, medium, or high |
| `evidence_visibility_invalid` | 400 | Visibility is not learner, instructor, or both |
| `evidence_artifact_invalid` | 400 | The artifact metadata is incomplete or the SHA-256 is malformed |
| `evidence_review_invalid` | 400 | A decision is missing scores, notes, or a next step |
| `evidence_review_conflict` | 409 | The evidence already has a final decision |
| `evidence_appeal_invalid` | 400 | The evidence is not rejected, or the appeal reason/decision is incomplete |
| `evidence_appeal_conflict` | 409 | An appeal is already pending, or the appeal was already decided |
| `evidence_appeal_not_found` | 404 | The appeal does not exist or is outside the caller's scope |
| `evidence_appeal_forbidden` | 403 | The caller cannot appeal or decide this evidence |
| `journey_invalid` | 400 | The journey id is not in the reviewed catalogue |
| `impact_dimension_invalid` | 400 | The contribution dimension is not build, protect, teach, or serve |
| `impact_kind_invalid` | 400 | The contribution kind is not valid for the dimension |
| `impact_title_invalid` | 400 | The contribution title is missing or outside its length limit |
| `impact_originality_invalid` | 400 | Originality is not copied, modified, original, or innovative |
| `impact_duplicate` | 409 | The same learner already submitted this contribution |
| `impact_not_found` | 404 | The contribution does not exist |
| `impact_forbidden` | 403 | The caller cannot verify or review this contribution |
| `impact_already_verified` | 409 | The contribution is already verified |
| `impact_validation_invalid` | 400 | Validation is self, peer, instructor, industry, or adoption only (self is rejected on verify) |
| `impact_validation_forbidden` | 403 | Only an administrator can record industry or adoption validation |
| `impact_rating_required` | 400 | Verification requires a quality rating |
| `impact_rating_invalid` | 400 | Quality is below 3.0 or above 5.0 |
| `impact_reach_invalid` | 400 | Reach cannot be negative |
| `impact_notes_required` | 400 | A rejection needs an explanation |
| `impact_reason_invalid` | 400 | A stewardship reason is shorter than 10 characters |
| `impact_category_invalid` | 400 | Stewardship category is not positive, negative, or restoration |
| `impact_delta_invalid` | 400 | The stewardship change is zero or has the wrong sign for its category |
| `impact_evidence_required` | 400 | A negative stewardship event needs an evidence reference |
| `impact_visibility_invalid` | 400 | Stewardship visibility is not private or instructor |
| `achievement_forbidden` | 403 | Only an administrator can award recognition manually |
| `achievement_unknown` | 404 | The recognition key is not in the catalogue |
| `achievement_not_manual` | 400 | The recognition key is not manually awardable |
| `achievement_evidence_required` | 400 | A manual award needs an evidence reference |
| `achievement_note_required` | 400 | A manual award needs a note of at least 10 characters |
| `achievement_locked` | 400 | The previous stage of a hidden chain is not earned |

The existing `X-Reauth-Required`, `X-Session-Invalid`, `X-Security-Version`, and
`X-Impersonating` headers remain. Do not duplicate them with a code unless the
endpoint needs a more specific reason.

## Migration order

1. Authentication and registration.
2. Course and exercise authoring validation.
3. Consent and privacy-request flows.
4. Export and report validation.
5. Everything else as a file is touched.

## Frontend use

The shared axios client can read `error.response.headers['x-error-code']` and
map it to a locale key. Until the mapping exists, keep the current `detail`
rendering. Do not show the raw code to a learner.

## Rules

- A code is a contract. Rename it only with a versioned API change.
- A code must be specific enough to choose a different next step.
- Do not use a code for a server error that the user cannot act on.
- Do not include PII, a username, an email, or a secret in a code.
