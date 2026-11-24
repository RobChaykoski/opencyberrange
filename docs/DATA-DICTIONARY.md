# Data dictionary

Status: **Release 5 in progress** (LTI 1.3, AGS, NRPS, and Deep Linking added)
Owner: Platform / Privacy
Review cadence: each release and at least annually
Related: [Privacy notice](PRIVACY-NOTICE.md),
[Privacy, erasure, and backups](PRIVACY-AND-DATA-DELETION.md),
[Analytics governance](ANALYTICS-GOVERNANCE.md),
[Analytics event schema](ANALYTICS-EVENT-SCHEMA.md)

This dictionary documents the personal information the platform collects, why
it is collected, the authority for processing, how long it is kept, who can see
it, whether it appears in an export, and what happens on account deletion. It is
an engineering and privacy reference, not legal advice. Each operator must
confirm the lawful basis, retention, and minor-consent rules for its own
institution.

## Conventions

- **Field** uses `table.column` where the value is stored, or `derived.*` for a
  calculated metric.
- **Authority** uses the platform's intended basis: **Service** (account and
  course delivery), **Security** (legitimate interest in protecting the
  service), **Consent** (optional survey or research), **Legal** (institutional
  or statutory obligation), or **Public** (minimal certificate verification).
- **Exports** lists the paths that can include the field:
  - `self` — `GET /api/auth/export`
  - `admin-users` — Admin user import/export
  - `activity` — activity-log CSV/JSON
  - `reports` — course, student, assignment, and ops CSV/PDF
  - `analytics` — cross-course analytics CSV/PDF
  - `certificate` — public certificate verification
- **On deletion** is one of **Deleted**, **Anonymised**, **Nulled**, **Kept**
  (non-personal content), or **Suppression hash**.
- A field marked **Derived** is never accepted directly from a learner; it is
  computed from the listed sources and is suppressed when the cohort is below
  the minimum.

## Identity and account

| Field | Description | Purpose | Authority | Retention | Access | Exports | On deletion |
|---|---|---|---|---|---|---|---|
| `users.id` | Internal numeric identifier | Link records and enforce uniqueness | Service | Account lifetime | Admin; scoped joins for instructors | `self`, `admin-users` | Deleted |
| `users.username` | Login handle | Authentication and display | Service | Account lifetime | Self; instructor for enrolled learners; admin | `self`, `admin-users`, `activity`, `reports` | Deleted |
| `users.email` | Account email | Sign-in, security notices, optional confirmation | Service | Account lifetime | Self; admin; instructor only where course roster requires | `self`, `admin-users`, `reports` | Deleted |
| `users.student_id` | Institution student number (optional) | Match the learner to the institution's roster | Service / institutional | Account lifetime | Self; admin; assigned instructor | `self`, `admin-users`, `reports` | Deleted |
| `users.first_name`, `users.last_name` | Display name (optional) | Certificates, rosters, celebration wall choice | Service | Account lifetime | Self; instructor for enrolled learners; admin | `self`, `admin-users`, `reports`, `certificate` (display name only) | Deleted |
| `users.registration_source`, `users.registration_campaign` | Normalized signup source (gdg, linkedin, swocts, direct, or a sanitized campaign label) from a tracked QR link or registration query | Attribute registrations and build aggregate usage reports | Service | Account lifetime | Admin; aggregate dashboards never expose learner identities | `admin-users`; aggregate reports only | Deleted with the account |
| `users.organization` | School, employer, or programme (optional) | Context for reporting and support | Service | Account lifetime | Self; admin | `self`, `admin-users` | Deleted |
| `users.avatar_data` | Small profile image as a data URL | Optional profile personalisation | Service | Until replaced or account deletion | Self; other signed-in users where the profile is visible | Not exported by default | Deleted |
| `users.role` | student, instructor, or admin | Authorisation | Service / Security | Account lifetime | Admin | `self`, `admin-users` | Deleted |
| `users.is_active`, `users.is_approved`, `users.is_locked` | Account state | Access control and moderation | Security | Account lifetime plus audit window | Admin | `admin-users` | Deleted |
| `users.created_at` | Account creation time | Support, audit, retention | Service / Security | Account lifetime | Admin | `self`, `admin-users` | Deleted |

## Authentication and security

| Field | Description | Purpose | Authority | Retention | Access | Exports | On deletion |
|---|---|---|---|---|---|---|---|
| `users.hashed_password` | Argon2id hash | Authentication | Security | Until password change or deletion | No one can read the password; auth service only | Never | Deleted |
| `users.totp_secret`, `users.mfa_recovery_codes`, `users.mfa_enabled` | MFA material | Second factor and recovery | Security | Until MFA disabled or deletion | Auth service only; admin can reset | Never | Deleted |
| `users.trusted_devices` | Device labels and timestamps | Session awareness | Security | Until revoked or deletion | Self | `self` (metadata only) | Deleted |
| `users.last_login_at`, `users.last_login_ip`, `users.login_streak`, `users.last_login_day` | Sign-in metadata | Security notices, streak, abuse review | Security | Account lifetime plus 90-day review window | Self; admin | `self`; IP is not in learner reports | Deleted |
| `users.failed_attempts`, `users.locked_at` | Lockout state | Brute-force protection | Security | Until reset or deletion | Admin; auth service | `admin-users` | Deleted |
| `revoked_tokens.jti`, `revoked_tokens.revoked_at` | Revoked session identifiers | Token revocation | Security | JWT lifetime plus short window | Auth service; admin | Never | Deleted with user or expired |
| `wireguard_configs.private_key` | Fernet-encrypted peer key | VPN access | Service / Security | Until peer removed or deletion | VPN service only | Never | Deleted and peer removed |
| `wireguard_configs.public_key`, `client_ip` | VPN peer identity | Route the learner's tunnel | Service | Until peer removed or deletion | Self; admin | `self` (metadata only) | Deleted |
| `activity_events.ip_address` | Request source address | Abuse and security investigation | Security | 90-day review window by default | Admin | `activity` | Anonymised |
| `identity_providers.name`, `kind`, `enabled`, `is_default`, `config` | Registered OIDC/SAML/LDAP connection metadata and endpoints | Institution sign-in | Service / Security | Until deleted by an admin | Admin | Not exported | Kept while the provider is configured |
| `identity_providers.secrets` | Encrypted client secret, bind password, or signing key | Authenticate to the identity provider | Security | Until rotated or deleted | Auth service only | Never | Deleted |
| `external_identities.provider_id`, `subject` | Pseudonymous subject from the institution IdP or LMS | Link an external login to one local account | Service / Security | Account lifetime | Self as an opaque link; admin | `self` (provider name only) | Deleted |
| `external_identities.email`, `last_login_at` | Email returned by the provider and last external sign-in | Account matching and support | Service / Security | Account lifetime | Self; admin | `self` | Deleted |
| `sso_sessions.user_id`, `provider_id`, `session_state`, `expires_at` | Local record of an external session | Single sign-out and session awareness | Security | Until expiry or sign-out | Auth service; admin | Never | Deleted |
| `sso_sessions.id_token` | Encrypted ID token from the provider | Refresh identity claims without a second login | Security | Until expiry or sign-out | Auth service only | Never | Deleted |
| `sso_login_states.state`, `nonce`, `code_verifier`, `redirect_uri`, `return_to` | In-flight OIDC/SAML login state | CSRF and replay protection | Security | Minutes until consumed or expiry | Auth service only | Never | Deleted |
| `sso_login_tickets.ticket`, `user_id`, `return_to` | Single-use hand-off from the provider callback to the SPA | Complete sign-in without exposing tokens | Security | Minutes until consumed or expiry | Auth service only | Never | Deleted |

## LMS integration (LTI 1.3)

| Field | Description | Purpose | Authority | Retention | Access | Exports | On deletion |
|---|---|---|---|---|---|---|---|
| `lti_platforms.name`, `issuer`, `client_id`, `deployment_id`, `auth_login_url`, `token_url`, `jwks_url`, `enabled` | Registered LMS deployment and endpoints | Launch and grade-passback trust | Service / Security | Until removed by an admin | Admin | Not exported | Kept while the platform is configured |
| `lti_platforms.private_key` | Encrypted tool private key for `private_key_jwt` and response signing | Prove the tool to the LMS | Security | Until rotated or deleted | Signing service only | Never | Deleted |
| `lti_login_states.state`, `nonce`, `platform_id`, `target_link_uri` | In-flight LTI login state | Bind a launch to the registered platform and stop replay | Security | Minutes until consumed or expiry | Auth service only | Never | Deleted |
| `lti_links.resource_link_id`, `context_id`, `title`, `lab_id` | LMS assignment link to a local lab | Open the right exercise and reuse the line item | Service | Course lifetime | Instructor; admin | Not in learner exports | Kept as course structure; learner link removed |
| `lti_links.context_title`, `ags_lineitem_url`, `ags_lineitems_url`, `ags_scopes`, `nrps_url`, `nrps_versions` | LMS course label and service endpoints | Grade passback and roster sync | Service | Course lifetime | Admin | Not exported | Kept while the link exists |
| `lti_scores.link_id`, `user_id`, `score`, `max_score`, `status`, `created_at` | Append-only record of each score passback | Grade audit and reconciliation | Service / Security | Institution schedule | Self; instructor; admin | `self` (score only) | Deleted with the learner |
| `lti_scores.reviewer_id`, `reason`, `lms_response` | Reviewer, review note, and LMS response | Prove the human review gate | Security | Institution schedule | Admin | Not in learner exports | Reviewer reference nulled |
| `lti_roster_members.subject`, `roles`, `status`, `context_id` | Minimum NRPS membership record from the LMS | Roster reconciliation without importing directory data | Service | Until the next sync or link removal | Admin | Not exported | Deleted when the link or platform is removed |
| `lti_deep_link_sessions.token`, `user_id`, `platform_id`, `return_url`, `data`, `nonce`, `accept_multiple` | Single-use Deep Linking picker session | Return selected exercises to the LMS safely | Security | Minutes until consumed or expiry | Auth service only | Never | Deleted |

Names, email addresses, and other directory fields from NRPS are deliberately
not stored. The roster keeps only the LMS subject, roles, status, and context.

## Course, cohort, and assignment

| Field | Description | Purpose | Authority | Retention | Access | Exports | On deletion |
|---|---|---|---|---|---|---|---|
| `courses.id`, `courses.name`, `courses.code`, `courses.semester` | Course identity | Deliver and report on the course | Service | Institution schedule | Self where enrolled; assigned instructor; admin | `self`, `reports` | Course kept; learner link removed |
| `courses.description`, `courses.start_date`, `end_date`, `is_active`, `is_archived` | Course context and dates | Scheduling and reporting windows | Service | Institution schedule | Enrolled learners; instructor; admin | `self`, `reports` | Course kept |
| `courses.invite_code` | Join code | Course enrolment | Service / Security | Until rotated or course deleted | Instructor; admin | Not exported in learner reports | Course kept |
| `courses.retention_until`, `retention_note`, `retention_set_by_id`, `retention_set_at` | Cohort retention date, note, and who set it | Term-end retention review | Service / Legal | Course lifetime plus audit window | Admin | Not in learner reports | Kept as course policy |
| `retention_runs.course_id`, `actor_id`, `action`, `counts`, `note`, `reference`, `created_at` | Append-only retention preview and completion evidence | Prove the cohort was reviewed and completed | Security / Legal | Institution audit window | Admin | Not exported | Kept as audit evidence |
| `readiness_student_notes.course_id`, `learner_id`, `kind`, `key`, `state`, `note`, `outcome`, `start_at`, `end_at`, `follow_up_at`, `owner_id`, `priority`, `created_by_id`, `created_at` | Instructor context, support action, flag state, case ownership, and band calibration review | Triage support without automated decisions; preserve the support record, assigned follow-up, and instructor judgement of the pilot band | Service / Security | Course retention window | Assigned instructor; admin | Not in learner reports; learner may see their own support record in a later phase | Deleted with the learner or course; owner link nulled on instructor erasure |
| `readiness_lab_reviews.course_id`, `lab_id`, `status`, `finding`, `action`, `outcome`, `owner_id`, `reviewed_at` | Lab-health review and outcome | Separate platform friction from learner risk and keep review history | Service / Security | Course retention window | Assigned instructor; admin | Not learner-facing | Deleted with the course |
| `nice_components.component_type`, `code`, `name`, `statement`, `category_code`, `category_name`, `version`, `is_active` | NIST NICE Framework v2.2.0 work roles, tasks, knowledge, and skills | Validate curriculum mappings against the official framework | Public reference data | Until superseded by a newer NICE version | Curriculum author; admin | Not learner data | Replaced by refresh; inactive rows retained for mappings |
| `nice_links.source_id`, `target_id`, `link_type` | Work-role to task/knowledge/skill relationships | Resolve relevant components in the authoring dropdown | Public reference data | Until superseded by a newer NICE version | Curriculum author; admin | Not learner data | Rebuilt on refresh |
| `nice_framework_meta.version`, `source`, `source_url`, `fetched_at`, `counts` | Installed NICE version and ingestion provenance | Show mapping freshness and source | Public reference data | Until superseded | Curriculum author; admin | Not learner data | Replaced on refresh |
| `lab_nice_components.lab_id`, `component_id`, `created_by_id`, `created_at` | Lab to NICE component selection | Prevent mapping drift and expose workforce alignment | Service / Security | Lab lifetime plus audit window | Curriculum author; admin | Not learner-facing | Deleted with the lab; author link nulled on erasure |
| `lab_nice_metadata.lab_id`, `review_status`, `source`, `confidence`, `policy_version`, `reviewed_at`, `reviewed_by_id` | Lab mapping review status and provenance | Separate provisional derivations from reviewed mappings | Service / Security | Lab lifetime plus audit window | Curriculum author; admin | Not learner-facing | Deleted with the lab; reviewer link nulled on erasure |
| `review_requests.user_id`, `course_id`, `lab_id`, `source`, `reason`, `status` | Learner request for a human decision | Appeal a deterministic result | Service / Legal | Course lifetime plus audit window | Self; assigned instructor; admin | `self` (status and note) | Deleted with the learner |
| `review_requests.rule_version`, `primary_factors`, `decision_note`, `decided_by_id`, `requested_at`, `decided_at` | Rule, factors, decision, and reviewer | Explain and audit the outcome | Security / Legal | Institution audit window | Admin; assigned instructor | Not in learner exports | Reviewer reference nulled; explanation retained in the audit trail |
| `course_enrollments.course_id`, `user_id`, `enrolled_at` | Enrolment link | Roster and cohort membership | Service | Institution schedule | Self; instructor; admin | `self`, `reports` | Deleted |
| `course_enrollments.seat_number`, `scope_token` | Per-course pseudonymous seat and scoping token | Private scoreboard and per-student lab scoping | Service | Course lifetime | Self; instructor; admin | `reports` (seat only where configured) | Deleted |
| `course_enrollments.consent_reference`, `consent_recorded_at`, `consent_recorded_by_id` | Institution parental/guardian consent reference for a minor enrollment | Record that consent was obtained without storing identity documents | Service / Legal | Course lifetime plus audit window | Assigned instructor; admin | `reports` (status only; reference not exported) | Deleted |
| `course_lab_assignments.lab_id`, `sort_order`, `display_name` | Exercises assigned to the course | Curriculum delivery | Service | Course lifetime | Enrolled learners; instructor; admin | `reports` | Kept as course content |
| `assignments.name`, `description`, `due_date`, `start_date`, `locked` | Assignment grouping | Organise work and deadlines | Service | Course lifetime | Enrolled learners; instructor; admin | `reports` | Kept as course content |
| `assignment_labs.lab_id` | Labs in an assignment | Scope reports and due work | Service | Course lifetime | Enrolled learners; instructor; admin | `reports` | Kept |

## Learning activity

| Field | Description | Purpose | Authority | Retention | Access | Exports | On deletion |
|---|---|---|---|---|---|---|---|
| `lab_sessions.id`, `user_id`, `lab_id`, `started_at`, `expires_at`, `stopped_at`, `status` | Lab session lifecycle | Launch, stop, troubleshoot, and measure active time | Service / Security | Session history for the institution window; 90-day operational review | Self; instructor for assigned course; admin | `self`, `reports` | Deleted |
| `lab_sessions.paused_at`, `paused_seconds`, `pause_reason` | Clock pause state and reason | Accommodation pause/resume without losing access | Service / Security | Session history | Self; instructor; admin | `self` (state only) | Deleted |
| `lab_sessions.network_id`, `network_subnet` | Isolated network identifiers | Routing and cleanup | Security | Session lifetime plus cleanup | Admin/system | Not in learner reports | Deleted |
| `lab_sessions.is_diagnostic`, `rangebox_enabled`, `impersonated_by` | Mode and support context | Separate diagnostic runs and admin support | Security | Session history | Admin | `self` (mode only) | Deleted |
| `lab_sessions.seeded_flag_hash` | Per-session flag hash | Per-student flag validation | Security | Session lifetime | Auth/flag service only | Never | Deleted |
| `lab_completions.user_id`, `lab_id`, `started_at`, `completed_at` | Exercise start and completion | Progress, certificates, analytics | Service | Institution schedule | Self; instructor for assigned course; admin | `self`, `reports`, `analytics` | Deleted |
| `lab_completions.flag_submitted` | Submitted flag text | Completion evidence and audit | Service / Security | Institution schedule | Admin; auth service | `self` (redacted where configured) | Deleted |
| `lab_completions.attempts`, `hints_used`, `time_spent_minutes` | Attempts, hints, and self-reported time | Learning analytics and hint coaching | Service | Institution schedule | Self; instructor aggregate; admin | `self`, `reports`, `analytics` | Deleted |
| `flag_attempts.flag_submitted`, `is_correct`, `attempted_at` | Every flag attempt | Diagnose stuck learners and detect guessing | Service / Security | Institution schedule | Self; instructor aggregate; admin | `self` (redacted), `reports` (aggregate) | Deleted |
| `quiz_attempts.score`, `correct`, `total`, `passed`, `answers`, `taken_at` | Level quiz results | Knowledge checks and progress | Service | Institution schedule | Self; instructor aggregate; admin | `self`, `reports` | Deleted |
| `exercise_quiz_attempts.*` | Optional per-exercise quiz results | Formative feedback | Service | Institution schedule | Self; instructor aggregate; admin | `self`, `reports` | Deleted |
| `achievements.achievement_type`, `awarded_at`, `course_id`, `lab_id` | Micro-credentials | Progress and celebration | Service | Institution schedule | Self; instructor; admin | `self`, `reports` | Deleted |
| `custom_achievements.*` | Admin-defined achievement definition: name, description, icon, trigger, threshold, group, tier, difficulty, points | Programme-specific goals | Service | Until deleted | Admin | Not learner data | Kept as course/programme content |
| `derived.achievement_points` | Tier × difficulty point value for each badge | Show value and progress | Service | Computed on read | Self; instructor aggregate; admin | `self`, `reports` | Recomputed |
| `achievement_celebrations.*` | Anonymous celebration count | Community recognition | Consent (public action) | Until withdrawn or deletion | Aggregate only | Never linked to identity | Deleted |
| `course_completion_resets.*` | Instructor reset events | Reset rate and report accuracy | Service / Security | Course lifetime | Instructor; admin | `reports` | Deleted or anonymised |
| `user_accommodations.user_id`, `time_multiplier`, `due_date_extension_days`, `notes` | Per-student accessibility accommodation | Scale timed sessions and shift assignment due dates | Service | Account lifetime | Self (own multiplier); assigned instructor; admin | `self` (values only; notes excluded) | Deleted |
| `user_accommodations.updated_by_id`, `updated_at` | Staff member and time of the last change | Accountability | Security | Account lifetime | Admin | Not exported | Reviewer reference nulled |
| `accommodation_events.user_id`, `actor_id`, `action`, `time_multiplier`, `due_date_extension_days`, `reason`, `created_at` | Append-only accommodation change history | Audit and dispute resolution | Security | Institution audit window | Admin | Not exported | Deleted with the learner |

## Feedback, surveys, and confidence

| Field | Description | Purpose | Authority | Retention | Access | Exports | On deletion |
|---|---|---|---|---|---|---|---|
| `exercise_pulse_surveys.difficulty`, `learning` | 1–5 pulse ratings | Exercise health and learning value | Consent (survey opt-in) | Until consent withdrawn or study close | Self; instructor aggregate above minimum cohort; admin | `self`, `analytics` (aggregate) | Deleted |
| `exercise_pulse_surveys.unclear`, `topic_interest` | Optional free text and topic signal | Identify unclear instructions and topics | Consent | Until consent withdrawn or study close | Instructor for assigned course above minimum cohort; admin | `self`; `analytics` only as counts/themes | Deleted |
| `exercise_reactions.reaction` | Like/dislike | Lightweight feedback | Service | Institution schedule | Self; instructor aggregate | `reports`, `analytics` (aggregate) | Deleted |
| `course_feedback.clarity`, `challenge`, `engagement`, `confidence`, `comment` | Course check-in and coaching notes | Teaching improvement and learner support | Service for course check-in; Consent for optional free text | Institution schedule | Student's own check-in; assigned instructor aggregate; admin | `self`; `reports` aggregate | Deleted |
| `exercise_quiz_feedback.satisfaction`, `relevance`, `usefulness`, `ease_of_use`, `comment` | Post-quiz feedback | Course experience metrics | Consent | Institution schedule | Instructor aggregate; admin | `analytics` aggregate | Deleted |
| `survey_responses.*` | Instructor survey answers | Programme evaluation | Consent | Study retention, then aggregate or delete | Instructor aggregate; approved researcher only if consented | `analytics` aggregate | Deleted |
| `survey_consent_events.*` | Consent decisions and policy version | Prove consent and withdrawal | Legal / Consent | Account lifetime plus audit window | Privacy officer; admin | `self` | Kept as consent evidence, identity removed where required |

## Certificates, transcripts, and public verification

| Field | Description | Purpose | Authority | Retention | Access | Exports | On deletion |
|---|---|---|---|---|---|---|---|
| `derived.certificate_id` | Deterministic certificate identifier | Public verification | Public | Certificate validity period | Anyone with the ID | `certificate` | Certificate remains verifiable only while the completion record exists; after deletion it resolves invalid |
| `derived.certificate_display_name` | Learner display name | Certificate presentation | Service | Certificate validity period | Certificate holder; verifier | `certificate` | Deleted with account; previously downloaded copies cannot be revoked |
| `derived.transcript_events` | Completion, quiz, and certificate events | Learner transcript | Service | Institution schedule | Self; admin | `self` (JSON/PDF) | Deleted with account |
| `certificate verification request` | Certificate ID and timestamp | Abuse monitoring | Security | Short operational window | Security/admin | Not exported | Not linked to the learner beyond the ID |

## Curriculum, competition, and authoring

| Field | Description | Purpose | Authority | Retention | Access | Exports | On deletion |
|---|---|---|---|---|---|---|---|
| `tracks.*`, `levels.*` | Track and level catalogue | Organise exercises | Service | Curriculum lifetime | All signed-in users | Not personal | Kept |
| `level_quizzes.*`, `quiz_questions.*` | Optional level quiz and question bank | Knowledge checks | Service | Curriculum lifetime | Learners see questions; answers revealed after submit; admin/instructor authoring | `self` (results) | Kept as curriculum content |
| `survey_attachments.*` | Files attached to an instructor survey | Survey delivery | Consent | Until survey closed | Survey owner; consented respondents | Not exported by default | Deleted with the survey |
| `invite_codes.code`, `email`, `created_by`, `used_by`, `used_at`, `expires_at` | Single-use registration invite, optionally pinned to an email | Controlled registration | Service / Security | Until used or expired | Admin | Not in learner exports | Deleted or email nulled |
| `report_exports.*` | Immutable report manifest: report id, requester, format, hash | Export accountability | Security / Legal | Institution audit schedule | Admin; report owner | Not a learner export | Kept; identity link nulled |
| `data_integrity_reviews.*` | Admin review of an unattributed ledger write | Tamper investigation | Security | Institution audit schedule | Admin; auditor | Not exported | Kept; contains no row contents |
| `competitions.*`, `competition_sponsors.*`, `competition_labs.*` | Event definition, sponsors, and selected labs | Run optional events | Service | Event lifetime plus archive | Signed-in users; admin | Event results only | Kept as event content |
| `competition_participants.user_id`, `joined_at`, `source` | Explicit opt-in to a competition leaderboard | Event participation | Consent | Event lifetime plus archive | Self; admin | Event leaderboard | Deleted |
| `exercise_test_results.*` | Latest test result per lab slug | Exercise QA | Service | Until replaced | Admin/instructor | Not personal | Kept |
| `exercise_templates.*` | Reusable vetted lab templates | Authoring | Service | Curriculum lifetime | Admin/instructor | Not personal | Kept; author link nulled |
| `template_instances.*` | Instructor instance of a template with cosmetic overrides | Authoring | Service | Until deleted | Owner; admin | Not personal | Deleted or author link nulled |
| `studio_pending_review.*` | Admin approval queue for staged instances | Authoring safety | Security | Until reviewed | Admin | Not personal | Deleted or author link nulled |
| `instructor_api_keys.*` | Encrypted LLM provider profile (key is Fernet-encrypted, never plaintext) | Optional AI authoring | Service / Security | Until removed or instructor deletion | Instructor only; admin cannot read the key | Never | Deleted with the instructor |
| `exercise_gen_jobs.*`, `exercise_gen_items.*` | AI generation job and planned items | Optional authoring | Service | Until deleted | Owner; admin | Not personal | Deleted with the job |

## Career readiness, competency, and question banks

| Field | Description | Purpose | Authority | Retention | Access | Exports | On deletion |
|---|---|---|---|---|---|---|---|
| `derived.competency_evidence` | Per-competency counts and dimensions from completions, quizzes, and workbook evidence | Show practice coverage and gaps | Service | Computed on read | Self; instructor aggregate; admin | `self` (learner profile), `reports` (aggregate) | Recomputed without deleted learner |
| `derived.competency_assessment` | Five-dimension score and provisional/validated state | Career-readiness evidence | Service | Computed on read | Self; instructor aggregate; admin | `self`, `reports` (aggregate) | Recomputed |
| `derived.role_readiness` | Pathway score, domain readiness, gaps, next workbooks, capstone, certifications | Answer "what do I need for this role?" | Service | Computed on read | Self only | `self` | Recomputed |
| `derived.career_gps` | Evidence, growth, and optional interest fit by direction | Optional direction finding | Service | Computed on read; answers are **not stored** | Self only | `self` (current view only) | Nothing to delete; answers are transient |
| `learner_snapshots.*` | Immutable career-dossier or portfolio payload, schema/formula versions, factor weights, and content hash | Re-render an old report without recomputing it | Service | Until account deletion | Self only | `self` (the stored report itself) | Deleted with the account |
| `dna_evidence_records.*` | Append-only Cyber DNA evidence: learner id, opaque activity id/category, competency id and domain, difficulty, attempts, hints, duration, prior failures, voluntary flag, formula/source versions | Evidence ledger for competency, behavior, and interest scores | Service | Until account deletion | Self only; no names or exercise prose | `self` (aggregate evidence only) | Deleted by `cyber_dna.erase_learner` before the user row |
| `dna_snapshots.*` | Immutable behavior, interest, or career-affinity payload with schema/formula versions, weights, and content hash | Preserve an old DNA report when a formula changes | Service | Until account deletion | Self only | `self` (the stored report) | Deleted by `cyber_dna.erase_learner` |
| `evidence_records.*` | Append-only evidence record: learner, source type and id, rubric id and version, confidence, provenance, visibility, status, artifact SHA-256, formula version | Demonstrate a capability rather than only a completion | Service / Security | Until learner erasure | Self; instructor for covered learners; tenant-wide reviewers; admin | `self` (evidence API); artifact content is not copied | Deleted with the learner; review audit follows the erasure policy |
| `evidence_competencies.*` | Competency link with the rubric criteria and weight it addresses | Map evidence to taxonomy competencies | Service | With the evidence record | Same as the evidence record | `self` (evidence API) | Deleted with the record |
| `evidence_reviews.*` | Append-only reviewer decision: per-criterion scores, weighted result, notes, next step | Instructor review and audit trail | Service / Security | With the evidence record | Self; instructor; admin | `self` (review feedback) | Deleted with the record |
| `workbook_answers.*` | Learner's current answer for one exercise prompt, with created/updated timestamps | Capture an analyst answer for instructor review | Service | Until learner erasure | Self; instructor for covered learners; admin | `self` (own answer); evidence export includes the submitted snapshot | Deleted with the learner or exercise |
| `evidence_appeals.*` | Learner's reason for a second review, status, reviewer, decision notes, and timestamps | Appeal an adverse evidence decision and preserve the decision trail | Service / Security | With the evidence record | Self; instructor; admin | `self` (own appeal history) | Deleted with the evidence record |
| `learner_journeys.*` | Learner-chosen direction, primary flag, status, and choice time | Keep the learner's chosen mission and history | Service | Until learner erasure | Self; admin | `self` | Deleted with the learner |
| `impact_contributions.*` | Contribution type, title, summary, base value, reach, reviewer rating, validation level, originality, status, timestamps, verifier, evidence link, and dedupe hash | Record build, protect, teach, and serve contribution and its verification | Service | Until learner erasure | Self; instructor for covered learners to verify; admin | `self` | Deleted with the learner; the linked evidence follows its own policy |
| `stewardship_events.*` | Trust event change, category, reason, evidence reference, recorder, visibility, and time | Record responsible conduct or a confirmed breach of trust | Service / Security | Until learner erasure, plus the audit window | Self; instructor where visibility allows; admin | `self` | Deleted with the learner; the admin audit line keeps the action, not the learner's content |
| `achievement_awards.*` | Recognition key, auto or manual source, awarder, evidence reference, note, and seen time | Recognise values-based contribution without changing a score or permission | Service | Until learner erasure | Self; admin; instructor only for public awards in course scope | `self` | Deleted with the learner |
| `derived.curriculum_demand` | Aggregate topic demand, exercise friction, and competency gaps | Instructor planning | Service | Computed on read | Instructor for assigned courses above the minimum cohort; admin | `analytics` aggregate | Recomputed |
| `certification_question_banks.*` | Admin-curated original questions, options, correct index, explanation, objective, and public reference | Certification-aligned sampled checks | Service / Security | Until the bank is replaced | Admin only; learners receive a sampled prompt without answers | Not exported | Kept as curriculum content |
| `derived.quiz_platinum` | Perfect score on a three-question sampled check | Recognise short, relevant practice | Service | Computed on award | Self; instructor; admin | `self`, `reports` | Deleted with the achievement |
| `devfest_2027.*` | Event plan: sessions, exercises, pathways, certificate template | Plan the DevFest experience | Service | Until the event is archived | Admin/instructor | Not personal | Kept as event content |

The GPS answers are the one place where the platform deliberately does **not**
persist user input. They are accepted in the request body for the current
response, used to weight interest, and discarded. The response states this in the
UI and the API documentation.

## Operational, audit, and derived analytics

| Field | Description | Purpose | Authority | Retention | Access | Exports | On deletion |
|---|---|---|---|---|---|---|---|
| `activity_events.event_type`, `target_type`, `target_id`, `target_label`, `detail`, `created_at` | Activity feed and audit context | Support, security, teaching review | Security / Service | 90-day review window by default | Admin; instructor only for assigned course | `activity` (admin) | Anonymised |
| `impersonation_sessions.session_id`, `actor_username`, `target_username`, `mode`, `course_id`, `started_at`, `expires_at`, `ended_at`, `end_reason`, `ip_address` | Server-side record of an impersonation token and its live/ended state | Prove who viewed as whom and when | Security / Legal | Audit window | Admin | Not exported | Actor/target names snapshotted; IDs nulled on user deletion |
| `system_metrics.load1`, `load5`, `load15`, `mem_used_mb`, `disk_used_gb`, `active_sessions`, `rangebox_count`, `docker_containers`, `docker_images`, `db_connections`, `created_at` | Sampled host/platform capacity and load | Capacity planning, support, upgrade decisions | Service / Security | 30 days | Admin | Not exported | Aggregate only; no learner identifiers |
| `course_cohorts.id`, `course_id`, `name`, `description`, `created_at` | Learner group inside one course | Target different exercise requirements by group | Service / Legal | Course lifetime | Assigned instructor; admin | Course export | Deleted with the course |
| `course_cohort_members.cohort_id`, `user_id` | Cohort membership | Resolve requirement coverage | Service / Legal | Course lifetime | Assigned instructor; admin | Course export | Deleted with the cohort or learner |
| `course_staff.course_id`, `user_id`, `staff_role`, `created_by_id`, `created_at` | Mentor, teaching-assistant, or co-instructor assignment | Scope report and teaching access to the course | Service / Security | Course lifetime plus audit window | Course instructor; admin | Own assignment | Deleted with course or staff account |
| `exercise_sets.id`, `course_id`, `name`, `description`, `sort_order`, `created_at` | Named group of exercises | Define a requirement's scope | Service | Course lifetime | Assigned instructor; admin | Course export | Deleted with the course |
| `exercise_set_items.set_id`, `lab_id`, `sort_order`, `required` | Exercises in a set | Compute required pairs and coverage | Service | Course lifetime | Assigned instructor; admin | Course export | Deleted with the set or exercise |
| `course_requirements.id`, `course_id`, `cohort_id`, `set_id`, `rule_type`, `threshold`, `due_at`, `note`, `created_at` | Requirement attached to a cohort | Decide whether a learner met the plan | Service / Legal | Course lifetime plus audit window | Assigned instructor; admin | Course export | Deleted with the course |
| `open_badge_credentials.user_id`, `certificate_id`, `track_slug`, `level_id`, `subject_id`, `jti`, `achievement_name`, `achievement_description`, `criteria_url`, `evidence_url`, `issued_at`, `recipient_name_opt_in`, `revoked_at`, `revoked_by_id`, `revocation_reason` | Hosted Open Badges 3.0 credential and revocation state | Portable proof of level completion | Service / Legal | Learner lifetime plus audit window | Self; admin | `self` (own credentials) | Deleted with the learner; revocation retained in audit |
| `data_integrity_ledger.*` | Row hashes and actor type | Tamper evidence | Security / Legal | Institution audit schedule | Admin; auditor | Not exported through learner reports | Kept; contains no row contents |
| `platform_settings.*` | Runtime configuration | Operate the platform | Service / Security | Until changed | Admin | Not in learner exports | Kept |
| `derived.active_time_minutes` | Bounded session time per learner-lab pair | Learning-time metrics | Service | Computed on read; no separate store | Self; instructor aggregate; admin | `reports`, `analytics` | Deleted with source rows |
| `derived.completion_rate`, `started_rate`, `abandonment_rate` | Cohort metrics | Exercise health | Service | Computed on read | Instructor aggregate above minimum cohort; admin | `reports`, `analytics` | Recomputed without deleted learner |
| `derived.first_attempt_rate`, `median_attempts`, `hint_use_rate` | Attempt and hint metrics | Difficulty and hint scaffolding | Service | Computed on read | Instructor aggregate; admin | `reports`, `analytics` | Recomputed |
| `derived.reset_rate`, `technical_failure_rate` | Reliability metrics | Separate technical failure from learning difficulty | Service | Computed on read | Instructor aggregate; admin | `reports`, `analytics` | Recomputed |
| `derived.difficulty_rating`, `clarity_rating`, `learning_value_rating` | Self-reported experience metrics | Exercise health | Consent | Computed on read | Instructor aggregate above minimum cohort; admin | `analytics` aggregate | Recomputed |
| `derived.competency_score` | Evidence summary across mapped exercises | Show growth, not mastery | Service | Computed on read | Self; instructor aggregate; admin | `self`, `reports` | Recomputed |
| `derived.free_text_themes` | Aggregated themes from comments | Identify recurring confusion | Consent | Computed on read; source comments retained per consent | Instructor aggregate above minimum cohort; admin | `analytics` aggregate only | Recomputed |

## Sessions, RBAC, and security evidence

| Field | Description | Purpose | Authority | Retention | Access | Exports | On deletion |
|---|---|---|---|---|---|---|---|
| `auth_sessions.id`, `user_id`, `institution_id`, `created_at`, `last_seen_at`, `expires_at`, `revoked_at`, `revoked_reason` | Server-side session bound to one tenant | Session lifecycle and immediate revocation | Security | Session lifetime plus audit window | Auth service; admin | `self` (metadata only) | Deleted |
| `auth_sessions.ip_address`, `user_agent`, `mfa_verified_at`, `reauth_at`, `created_by` | Session context and recent reauthentication evidence | Abuse review and high-impact operation gates | Security | Session lifetime plus audit window | Auth service; admin | Not in learner reports | Deleted |
| `refresh_tokens.jti`, `session_id`, `user_id`, `family_id`, `token_hash`, `institution_id`, `created_at`, `expires_at`, `rotated_at`, `revoked_at`, `replaced_by_jti`, `reuse_detected_at` | Rotating opaque refresh-token record; only a SHA-256 hash is stored | Session renewal and reuse/theft detection | Security | Token/session lifetime | Auth service only | Never | Deleted |
| `refresh_tokens.ip_address`, `user_agent` | Refresh context | Abuse investigation | Security | Session lifetime | Auth service; admin | Never | Deleted |
| `rbac_roles.key`, `label`, `description`, `rank`, `is_system` | Reviewed role catalog | Role-based access control | Security | Release lifetime | Admin; authorization service | Not exported | Kept as configuration |
| `rbac_permissions.key`, `description`, `category`, `sensitivity` | Reviewed permission catalog | Permission-based access control | Security | Release lifetime | Admin; authorization service | Not exported | Kept as configuration |
| `rbac_role_permissions.role_key`, `permission_key` | Role-to-permission grants | Effective RBAC grants | Security | Release lifetime | Admin; authorization service | Not exported | Kept as configuration |
| `rbac_user_roles.user_id`, `role_key`, `granted_by`, `granted_at`, `expires_at` | Expiring extra role assignment | Temporary elevation | Security | Grant lifetime plus audit window | Admin; authorization service | Not exported | Deleted with the user |
| `network_access_rules.scope`, `kind`, `value`, `action`, `note`, `created_by_id`, `expires_at` | Allow or deny rule for sign-in and registration by IP, network, or email domain | Restrict access to institution networks and domains | Security / Institutional | Until removed or expired | Admin; auth service | Not in learner exports | Deleted; actor reference nulled |
| `security_events.id`, `occurred_at`, `category`, `severity`, `event_type`, `action`, `outcome` | Append-only security, audit, and privacy event | Detection, investigation, and evidence | Security / Legal | 365 days recommended; operator archive/prune | Admin; auditor; security service | Not in learner exports | Kept; actor references anonymised |
| `security_events.actor_id`, `actor_username`, `actor_role`, `institution_id` | Actor context for an event | Attribution and tenant review | Security | Event retention | Admin; auditor | Not in learner exports | Actor references anonymised |
| `security_events.target_type`, `target_id`, `target_label`, `path`, `method`, `status_code`, `ip_address`, `user_agent`, `detail`, `request_id` | Target and request context | Reproduce and scope an event | Security | Event retention | Admin; auditor | Not in learner exports | Target/learner identifiers anonymised; IP removed by erasure |
| `break_glass_grants.user_id`, `permission`, `reason`, `reference`, `status`, `approved_by`, `expires_at`, `use_count`, `review_status` | Time-bound emergency access evidence | Controlled exception handling | Security / Legal | Audit retention | Admin; privacy officer; auditor | Not in learner exports | Kept as audit evidence; actor references anonymised |
| `service_credentials.name`, `username`, `scopes`, `token_hash`, `created_at`, `expires_at`, `last_used_at`, `revoked_at` | Non-human service identity; only a token hash is stored | Machine-to-machine access | Security | Credential lifetime plus audit window | Admin; service identity owner | Never | Revoked; non-personal record retained |
| `portfolio_share_tokens.token_hash`, `user_id`, `scope`, `expires_at`, `single_use`, `used_at`, `revoked_at` | Hashed portfolio/certificate share link | Explicit, revocable sharing | Consent / Service | Until expiry or revocation | Self; share holder for the shared fields | Shared fields only | Deleted or revoked |
| `settings_change_requests.ticket_number`, `reason`, `environment`, `status`, `actor_id`, `actor_username` | Ticket-gated settings change metadata; ticket and reason are Fernet-encrypted | Change control and auditability | Security / Legal | Audit retention; at least 1 year, institution schedule | Admin; auditor | Not exported | Kept as audit evidence; actor references anonymised |
| `settings_change_requests.before_values`, `after_values`, `secret_keys`, `change_hash`, `applied_at`, `reverted_at`, `reverted_by_username`, `revert_reason` | Revertible before/after snapshots; secret setting values are replaced with `[secret]`; revert reason is encrypted | Prove what changed and restore safely | Security / Legal | Audit retention | Admin; auditor | Not exported | Kept as audit evidence; no secret values stored |
| `production_cutovers.actor_id`, `actor_username`, `ticket_number`, `notes`, `cutover_at`, `sample_data_summary`, `password_confirmed`, `evidence_hash` | One-way production transition evidence; ticket and notes are encrypted, summary contains counts only, no password is stored | Prove authorised cutover and data cleanup | Security / Legal | Permanent audit evidence | Admin; auditor | Not exported | Immutable; kept |

## Masking, encryption, and change control

- Secret platform settings (SMTP password, IdP secrets, Open Badge signing key, and similar) are Fernet-encrypted at rest by `settings_service`; the API returns a fixed mask and never the stored value.
- Passwords are stored only as Argon2id hashes. Refresh tokens, service tokens, and portfolio share tokens store only SHA-256 hashes.
- `settings_change_requests` encrypts the ticket number and reason. It never stores a secret setting value: secret keys are recorded as `[secret]` in before/after snapshots and listed in `secret_keys`.
- `production_cutovers` encrypts the ticket and approval notes, stores only deletion counts and an evidence hash, and never stores the administrator password.
- The production cutover is one-way from the application. It requires a ticket, the current password, the exact `GO PRODUCTION` phrase, and explicit data-loss and one-way acknowledgements. Every apply, revert, denied cutover, and completed cutover is written to the append-only security event store and audit log.
- Sample/test accounts matching the documented test patterns are erased through the privacy erasure path. Security and audit evidence is retained or anonymised, not silently deleted.

## Retention schedule

| Data class | Default retention | Notes |
|---|---|---|
| Active account and profile | Until account deletion or institution schedule | The platform does not auto-delete active accounts. |
| Course, enrolment, and learning records | Institution schedule | Used for progress, certificates, and programme reporting. |
| Lab sessions and active-time inputs | Institution schedule; 90-day operational review | Needed for support and technical-failure analysis. |
| Activity and audit events | 90 days by default | Adjust to the institution's audit schedule. |
| Backups | 30 days by default | Restores re-apply the live erasure suppression ledger. |
| VPN peer records | Until peer removed or account deletion | Private key is encrypted at rest. |
| Pulse, feedback, and survey free text | Until consent withdrawn or study close | Aggregate metrics may be retained after de-identification. |
| Research extracts | Approved study period, then destruction | See [Analytics governance](ANALYTICS-GOVERNANCE.md). |
| Suppression ledger | Indefinite | Keyed hashes only; prevents restore from resurrecting erased accounts. |
| Downloaded exports | Not stored by the platform | The recipient is responsible for secure storage and deletion. |

## Deletion outcomes

Account deletion:

- deletes identity, credentials, MFA, VPN, enrolments, sessions, completions,
  flag attempts, quiz attempts, achievements, recognition awards, journeys,
  impact contributions, stewardship events, competition entries, and survey
  responses linked to the account;
- anonymises activity events by removing actor, target, label, detail, and IP;
- nulls author links on labs and templates while keeping the course content;
- keeps only keyed suppression hashes so a backup restore cannot resurrect the
  account;
- leaves previously downloaded certificates, transcripts, and exports outside
  the platform's control.

Instructor accounts that still own courses are blocked until the courses are
transferred, so another cohort's records are not destroyed by accident. See
[Privacy, erasure, and backups](PRIVACY-AND-DATA-DELETION.md).

## Review checklist

- [ ] Every new field has a purpose, authority, retention, access role, export
      status, and deletion outcome.
- [ ] New exports use the versioned schemas in
      [Analytics governance](ANALYTICS-GOVERNANCE.md).
- [ ] New free-text fields are included in the input-safety and export-safety
      tests.
- [ ] New derived metrics have a written definition and a minimum sample size.
- [ ] Certification question banks are reviewed against current public
      objectives, every reference is an external https source, and
      `python scripts/check-question-banks.py` passes.
- [ ] The privacy notice and retention schedule are updated in the same release.
- [ ] The data dictionary is reviewed with the institution's privacy office.
