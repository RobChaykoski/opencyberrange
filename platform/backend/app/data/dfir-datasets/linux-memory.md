# Live Linux memory case brief

Synthetic case `DFIR-2026-043`.

- Host: `linux-ir-01.lab.example`
- Source: isolated live Linux guest
- Acquisition: AVML to `/tmp/mem.lime`
- Question: Which process held the volatile marker, and what would be lost on
  reboot?

Record the acquisition command, image size, SHA-256, time, and custodian. Analyse
a verified copy, not the original. Do not read unrelated process secrets.
