# Velociraptor endpoint hunt case brief

Synthetic case `DFIR-2026-051`.

- Scope: 12 fictional Windows endpoints in `lab.example`
- Authorization: written lab authorization on file; read-only collection only
- Hunt ID: `H-2026-051-ENDPOINT`
- Collection hash: `2222222222222222222222222222222222222222222222222222222222222222`
- Investigator: `analyst@example.org`

## Question

Which endpoints created a suspicious scheduled task, what process tree preceded
it, and did the task run within the case window?

## Available evidence

- `Windows.System.TaskScheduler` output from the scoped hunt.
- `Windows.Sys.Processes` process ancestry for the same window.
- `Windows.Forensics.Prefetch` execution evidence for the task binary.
- A synthetic timeline with task creation, process start, and file-write events.

## Constraints

- Collect only the three named artifacts. Do not run a full-disk or memory
  collection for this question.
- Record the hunt scope, artifact parameters, collection hash, and custodian.
- Distinguish a scheduled task definition from proof that it executed.
- State what the evidence does not prove.

## Deliverable

A short analyst finding and a reviewed endpoint hunt report containing the
scope, artifact selection, query parameters, hashes, timeline, confidence, and
containment recommendation.
