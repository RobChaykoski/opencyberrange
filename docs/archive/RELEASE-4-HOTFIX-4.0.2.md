# Release 4 hotfix 4.0.2: RangeBox workspace tabs

Status: **deployed to production** `172.16.16.41` on 2026-11-14.

## What changed

- The RangeBox exercise workspace now uses three full-size tabs: **Desktop**,
  **Exercise**, and **Workbook**. The old split grid put the briefing and
  workbook in cramped frames.
- RangeBox stays mounted while hidden, so the VNC session survives tab
  switches.
- The RangeBox toolbar wraps its controls in narrow panels instead of clipping
  Minimize/Fullscreen/Close.

## Scope

Frontend only. No backend, database, migration, or configuration change.
Production stayed on the Release 4 schema and API (`/api/version` = 4).

## Verification

- Pulled `main` `89c4e9f8`; rebuilt and recreated only `ocr-frontend`.
- Frontend healthy; previous image preserved as
  `ocr-frontend:pre-rangebox-tabs` for rollback.
- Live production check with a temporary admin and a spawned RangeBox lab:
  Desktop connected, Exercise and Workbook tabs rendered full-size, and the
  desktop was still connected after switching back.
- Temporary session and account were stopped and deleted.

## Rollback

```bash
docker tag ocr-frontend:pre-rangebox-tabs ocr-frontend:latest
cd ~/opencyberrange/platform
docker compose -f docker-compose.prod.yml -f docker-compose.adopt.yml \
  -f docker-compose.override.yml up -d frontend
```
