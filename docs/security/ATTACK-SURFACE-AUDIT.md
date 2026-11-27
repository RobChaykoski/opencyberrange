# Attack-surface audit: five high-impact areas

Status: **code review complete; residual gaps tracked**

This page records the code-level audit of the five surfaces that sit between
untrusted learner traffic and privileged host infrastructure. It is a review
record, not a claim that the platform is penetration-tested. The live drills are
in [`SECURITY-VALIDATION-PLAN.md`](SECURITY-VALIDATION-PLAN.md).

## 1. Docker orchestration and command injection

**Risk:** lab spawn, `/24` allocation, and WireGuard management need Docker or
host utilities. Unsanitised lab parameters could become host commands.

**Verified controls**

- No `shell=True` in `platform/backend/app`.
- Host commands use argument lists, not interpolated shell strings:
  `admin.py` restore (`psql`), `docker_manager.py` compose/teardown and network
  helpers, `backups.py`, `workbook_builder.py`, `wireguard_manager.py`.
- Container and network names are derived from the database lab slug and the
  authenticated user id; launch requests are Pydantic models.
- The Docker SDK is used for container lifecycle (`containers.run`), not a
  shell wrapper.

**Residual risk**

- An imported lab manifest is trusted content. A malicious compose file,
  environment value, or port mapping can still affect the host within the
  container's privileges. Keep lab import behind the admin review workflow and
  do not enable untrusted authors without a compose policy review.
- Add a regression test that a lab slug containing shell metacharacters cannot
  reach a subprocess argument, and fuzz the subnet/port parameters.

## 2. Broken object-level authorization (IDOR)

**Risk:** transcript, artifact, container-reset, and roster endpoints can leak or
mutate another learner's object even when the caller has the right role.

**Verified controls**

- One decision point: `app/services/authorization.py`.
- Course scope recognises `CourseStaff` membership, so teaching assistants,
  mentors, and co-instructors match the reviewed matrix.
- Object checks are covered by `test_idor_matrix.py`,
  `test_horizontal_privilege.py`, `test_access_matrix.py`,
  `test_authorization_matrix.py`, and `test_route_authorization.py`.
- Tenant RLS is a second backstop for tenant-scoped tables.

**Residual risk**

- A new route can omit the dependency. `test_route_authorization.py` is the
  guard; keep it mandatory in CI.
- Add object-level cases for every new export, evidence, and roster route.

## 3. SSO assertion and break-glass edge cases

**Risk:** linking an external identity by email or username can take over a
local account; a weak SAML validation or break-glass path can bypass MFA.

**Verified controls**

- `ExternalIdentity` keys on `(provider_id, subject)`, not email. Email is
  diagnostic only, and a unique constraint stops two local accounts claiming the
  same external identity.
- SAML settings use `strict=True`, `wantAssertionsSigned=True`, and
  `rejectDeprecatedAlgorithm=True`.
- SSO login state is stored server-side and consumed atomically to prevent
  replay; OIDC stores nonce and PKCE verifier, SAML stores the AuthnRequest id.
- Break-glass requires the permission, recent re-authentication, MFA, and a
  separate approver. Private permissions always require a second operator.

**Residual risk**

- `wantMessagesSigned=False` is acceptable only because assertions are signed.
  Do not relax `wantAssertionsSigned`.
- Put the local break-glass admin endpoint behind the edge rate limit and an
  IP/network restriction in addition to the application re-auth.
- Add a test that an assertion signed by the wrong key is rejected, and a test
  that the same email on two providers does not link to one local account.

## 4. Async event-loop blocking

**Risk:** container provisioning, WireGuard key generation, and PDF/report
rendering are slow. Running them inline in `async def` stalls the Uvicorn worker.

**Verified controls**

- Lab spawn, health checks, and teardown use
  `loop.run_in_executor` / `asyncio.to_thread` in `routers/labs.py`.
- The exercise tester offloads Docker work (`asyncio.to_thread`).
- Scheduler jobs use `asyncio.to_thread` for backups, consent cleanup, security
  operations, and metrics.
- Admin release checks and heavy maintenance use `run_in_executor` / `to_thread`.

**Residual risk**

- A new `async def` route can call Docker, `subprocess`, or a PDF renderer
  directly. Review every new route and prefer a plain `def` route or an explicit
  `to_thread` wrapper.
- Add a lightweight CI grep that fails on `subprocess`/Docker SDK calls inside
  `async def` route bodies without a thread offload.

## 5. Flag submission races and brute force

**Risk:** concurrent correct submissions can double-claim points or duplicate
achievements; unlimited guesses can brute-force a flag.

**Verified controls**

- `POST /labs/{lab_id}/submit-flag` is limited to `10/minute`.
- `check_rate_limit()` adds a per-user/per-lab cooldown.
- `lab_completions` has a unique `(user_id, lab_id)` index
  (`ix_completion_user_lab`); the route catches `IntegrityError`, rolls back, and
  updates the winner instead of returning a 500.
- Comparison uses `hmac.compare_digest`; per-student seeded flags are preferred
  over the shared lab hash.
- Achievement award tests assert idempotency.

**Residual risk**

- Two correct requests still create two `FlagAttempt` rows; that is expected.
  The completion row and achievement award are the idempotent boundary.
- Add a concurrency test that fires two correct submissions at once and asserts
  one completion, one achievement, and no 5xx.

## 6. Celebration Wall: XSS, privacy, write authorization, and query shape

**Risk:** a shared wall of learner wins can become a stored-XSS surface, leak a
learner who opted out, accept a forged milestone, or generate N+1 queries.

**Verified controls**

- The wall has **no user-authored messages or free-text posts**. It projects
  achievement rows generated by the scoring engine. There is no client-writable
  endpoint that creates a milestone.
- Frontend rendering uses Vue mustache interpolation (`{{ ... }}`), not
  `v-html`, for names, lab names, and course names. Avatar images are restricted
  to validated `data:image/(png|jpeg|webp);base64` values.
- Visibility filters: active, `show_on_scoreboard`, not minor, and not admin in
  both the wall query and `_public_achievement_or_404`.
- The wall never returns a stable learner id (`user_id: None`); anonymous mode
  removes the username and avatar.
- Celebrations are one row per `(achievement_id, user_id)` with a unique index;
  the endpoint requires auth, rejects self-celebration, and returns only
  `{celebrated, count}`.
- Recent wins use `joinedload` for user, course, and lab; celebration counts and
  “celebrated by me” are set-based queries; the limit is capped at 50.

**Residual risk**

- The celebrate toggle has no per-user rate limit. The unique index bounds the
  data, but rapid toggling can still create write churn. Add a small limiter
  (for example `30/minute`) if abuse appears.
- Account erasure must cascade achievements and celebrations through the
  existing foreign keys; the privacy tests cover opt-out, not a full erasure
  replay. Add an erasure test that confirms wall rows disappear after deletion.
- Add a CSP regression check so a future rich-text wall cannot introduce
  `v-html` without the sanitizer.

## 7. Six-trait scoring and the 250-point competition score

**Risk:** a raw competition score with speed and first-blood bonuses could leak
into the learner's six Cyber DNA traits, or an aborted session could inflate a
historical average.

**Verified controls**

- The 250-point competition score and Skill DNA are separate models. Competition
  scoring does not write the six trait scores. Skill DNA is derived in
  `app/services/skill_dna.py` from completion, attempt, hint, time, quiz,
  achievement, and course/instructor signals.
- The six dimensions are `explorer`, `builder`, `tester`, `defender`,
  `investigator`, and `leader`. Each is capped at 99, recency-weighted, and
  published with a `FORMULA_VERSION`.
- `_completion_rows()` now filters `flag_submitted IS NOT NULL` and non-empty.
  A hint placeholder completion (empty flag) no longer counts as a solve for
  Builder, Tester, Defender, Investigator, or Leader.
- An opened-but-unfinished lab still counts toward **Explorer**, which is
  defined as breadth of labs opened, not as a completion average.
- Aborted sessions do not add minutes or attempts to the completion-based
  traits.

**Residual risk**

- Explorer intentionally counts a lab session even when the learner abandons it.
  That is a breadth signal, not a success rate; do not relabel it as completion.
- Add a regression test for a placeholder completion, and one for an aborted
  session that asserts Explorer changes while Builder does not. The placeholder
  test is in `test_skill_dna.py`.
- If a future formula consumes the 250-point score, document the mapping and add
  a separate formula version before changing the traits.

## 8. Profile visibility and Cyber DNA access

**Risk:** a learner could read another learner's coaching notes, VPN state, or
unshared DNA breakdown through a profile or DNA endpoint.

**Verified controls**

- `GET /api/profile/skill-dna` is self-only (`current_user`) and requires the
  `cyber_dna` consent. It never accepts a user id.
- The profile, career dossier, competency, and Skill DNA routers are in the
  consent middleware's `cyber_dna` path list.
- The only `/users/{id}` routes are under the admin router and require the admin
  dependency; there is no public `GET /users/{id}/profile`.
- Public portfolio data is opt-in and filtered by the portfolio visibility
  rules; private coaching and VPN state are not in the public projection.
- Celebration wall projections set `user_id: None` and omit username/avatar in
  anonymous mode.

**Residual risk**

- Add an explicit IDOR test for every new profile or DNA route that accepts an
  object id. The `test_idor_matrix.py` and `test_horizontal_privilege.py` suites
  are the pattern.
- Confirm the public portfolio projection never joins coaching notes or VPN
  peers; keep those in instructor-only responses.

## 9. Cyber GPS: data sources, access, cold start, and query shape

**Verified controls**

- `build_gps()` uses the competency assessment, completion/quiz/achievement
  evidence, and optional interest answers. Answers are validated against the
  published option ids and are **not stored**; they only shape the current view.
- The GPS route is self-only and requires the `cyber_gps` consent
  (`/api/profile/gps`, `/api/profile/role-readiness`).
- Cold start is null-safe: `max(1, len(critical_ids))` avoids division by zero,
  `interest_max` defaults to `0`, and missing competency rows produce a zero
  growth signal rather than a crash.
- Recommendation cards are links, not launch bypasses. The underlying lab and
  flag routes still call the lab-access check and course scoping.

**Residual risk**

- `build_gps()` calls `build_role_readiness()` for each flagship role. Confirm
  the readiness builder reuses the assessment and does not issue a query per
  competency; if it does, cache the per-request readiness result or precompute a
  user roadmap.
- Add a cold-start test for a user with zero completions and one for a user with
  only a placeholder completion, asserting a foundational recommendation and no
  500.
- Keep the GPS consent gate in front of every new GPS/role-readiness route.

## 10. Lab access, course locks, and Cyber GPS links

**Verified controls**

- Lab launch and flag submission call the shared lab-access assertion, which
  applies visibility, course assignment, and level/track checks.
- Course-staff scope is handled in the central authorization service.
- A GPS recommendation does not grant access; it only links to the normal lab
  route, where the access check runs again.

**Residual risk**

- Add an explicit test that a locked advanced-lab URL from a GPS card returns the
  same denial as a direct URL.
- Re-run the launch/flag tests whenever a new recommendation surface is added.

## 11. Frontend rendering and viewport safety

**Verified controls**

- `v-html` appears only in `TrackDetail.vue`, `ExerciseBrief.vue`, and
  `TicketPanel.vue`, and each call goes through the DOMPurify wrapper in
  `src/utils/markdown.js`.
- Cyber GPS, profile, and Celebration Wall views use mustache interpolation for
  names, labels, and track text.
- Inline SVG is authored markup, not user content.
- The UI smoke and accessibility kits cover mobile and desktop viewports.

**Residual risk**

- Add a CI grep that rejects a new `v-html` without the DOMPurify wrapper and a
  `security-delta` annotation.
- Add a visual regression at 390 px and 1440 px in light and dark mode for the
  GPS map and profile gauges.

## 12. Per-session flags

**Implemented for 112 of 222 labs.** Environment-driven labs rotate through their
compose `FLAG`/`*_FLAG` values. Dockerfile-baked labs use a
`flag_path`/`flag_service`/`flag_command` contract: the launcher overrides the
service entrypoint with a small `/bin/sh` wrapper that writes `$LAB_FLAG` to the
declared path, chowns it when requested, then execs the original command. The
session hash is stored only after the compose bring-up succeeds.

**Residual risk**

- 110 labs still bake the flag into an image or a static file. They continue to
  grade against the shared hash until they adopt the render contract.
- Do not log the generated flag; it is visible in `docker inspect` and the
  transient compose override, which is acceptable for a session the learner owns.

**Follow-up**

1. Roll the render contract through the remaining Dockerfile-baked labs.
2. Use the same wrapper for standalone static flag files; add an nginx template
   only for flags embedded in HTML.
3. Add a lab test that proves a copied flag from one session is rejected by a
   second session on an env-driven or rendered lab.

## 13. Resource limits and orphan cleanup

**Verified controls**

- `docker_manager._apply_default_service_limits()` applies `mem_limit`,
  `memswap_limit`, `cpus`, `pids_limit`, and a default `cap_drop` to compose
  services that do not declare their own limits.
- RangeBox containers set `mem_limit`, `cpu_quota`, and `pids_limit` directly.
- `scheduler._cleanup_expired_sessions_once()` reaps expired and stale sessions
  and destroys standalone RangeBox containers.

**Residual risk**

- The default-limit helper skips `mem_limit`/`cpus` when a service declares any
  `deploy` block, even if that block has no `resources.limits`. Treat a
  `deploy` block without limits as missing and apply the default.
- Review direct `containers.run` helper containers for limits; compose is
  covered, direct SDK calls need the same treatment.
- Add a scheduled test that an expired session is destroyed and its `/24` is
  released.

## 14. Upstream image pinning

**Finding:** many lab Dockerfiles use a tag such as `ubuntu:22.04`,
`python:3.11-slim`, or `alpine:3.18` without an immutable digest. Locally built
`ocr-*:latest` images are a different case: they are built from this repository,
not pulled from an upstream registry.

**Current controls**

- The supply-chain lock hashes the lab definitions and the reviewed runtime
  files.
- Release image scanning covers the platform images.

**Required follow-up**

1. Add a CI check for `FROM <upstream>:<tag>` without `@sha256:` and for
   `image: <upstream>:latest` outside `ocr-*`.
2. Resolve and pin the common bases (`ubuntu:22.04`, `python:3.11-slim`,
   `alpine:3.18`, `debian:bookworm-slim`, `kalilinux/kali-rolling`) by digest.
3. Rebuild and re-run the lab harness after each digest update.

## Review commands

```bash
# No shell execution in the backend
rg -n "shell=True|os\\.system" platform/backend/app

# Route authorization and object checks
python -m pytest platform/backend/tests/test_route_authorization.py \
  platform/backend/tests/test_idor_matrix.py \
  platform/backend/tests/test_horizontal_privilege.py -q

# Flag submission and achievements
python -m pytest platform/backend/tests/test_flag_submit.py \
  platform/backend/tests/test_achievements.py \
  platform/backend/tests/test_concurrency.py -q
```
