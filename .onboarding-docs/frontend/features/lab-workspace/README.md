# Lab workspace (frontend)

## Purpose

Run one exercise: show the briefing, start and stop the lab, display the
RangeBox desktop when needed, submit the flag, and show progress without
confusing a technical failure with a learning failure.

## Routes and views

| Route | View | Notes |
|---|---|---|
| `/exercises/:trackSlug/briefing` | `ExerciseBriefing.vue` | scenario, hints, flag form |
| `/rangebox` | `RangeBoxHome.vue` | standalone RangeBox |
| `/rangebox/:sessionId` | `RangeBoxView.vue` | desktop and session controls |
| lab quiz route | `ExerciseQuiz.vue` | optional check |
| `/workbook-answers` | `WorkbookAnswers.vue` | answer workspace |

Supporting components include `ExerciseBrief.vue`, `FlagCelebration.vue`,
`LabAccessDiagram.vue`, `HaStatusCard.vue`, and the noVNC wrapper.

## API calls

| Action | Endpoint |
|---|---|
| Start lab | `POST /api/labs/spawn/{lab_slug}` |
| Poll readiness | `GET /api/labs/spawn-status/{session_id}` |
| Stop / extend | `POST /api/labs/stop`, `/extend` |
| Pause / resume | `POST /api/labs/pause`, `/resume` |
| Active sessions | `GET /api/labs/active` |
| VPN config | `GET /api/labs/vpn-config` |
| Submit flag | `POST /api/exercises/labs/{lab_id}/submit-flag` |
| Hint | `GET /api/exercises/labs/{lab_id}/hint` |

## Behaviour that matters

- **Start is asynchronous.** The SPA polls the spawn status and shows each
  stage; it does not assume a container is ready.
- **RangeBox waits for VNC.** The desktop is shown only after port 6080 is
  reachable.
- **One session at a time.** The backend enforces the quota; the UI explains
  the limit instead of retrying blindly.
- **Flag feedback.** A wrong flag is a normal outcome, not an error page. A
  correct flag triggers the celebration and refresh.
- **Hints are part of the exercise.** They can cost points; the UI shows the
  cost.
- **Failure language.** A target failure is reported as a technical issue with a
  reset path, not as the learner's mistake.
- **Cleanup.** Leaving the page does not silently leave a session forever; the
  backend expiry still applies.

## Storage

No lab data is persisted in the browser. The session id comes from the backend.
VPN setup may use a one-time config download; do not store a private key in
`localStorage`.

## Run and test

```bash
cd platform/frontend
npm run dev
npm test
npm run lint
```

Backend coverage: `tests/test_lab_preflight.py`,
`tests/test_rangebox_transport.py`, `tests/test_rangebox_capacity.py`,
`tests/test_lab_network_cleanup.py`, `tests/test_flag_submit.py`.

## Extension checklist

- Add a state for every backend status, including `starting`, `error`, `expired`.
- Do not expose a host port or a raw container address.
- Keep the noVNC proxy on the backend; never connect the browser directly to a
  lab network.
- Add a test for the poll and the error path.
- Update the accessibility labels for the desktop frame.

## Related

- [Backend labs and sessions](../../../backend/features/labs-and-sessions/README.md)
- [Backend flags and scoring](../../../backend/features/flags-and-scoring/README.md)
- [Lab runtime](../../../lab-runtime/subsystem-overview.md)
