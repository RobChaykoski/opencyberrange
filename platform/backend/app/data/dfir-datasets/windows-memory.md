# Windows memory case brief

Synthetic case `DFIR-2026-041`.

- Image: `win2008-lab.raw` (fictional, 512 MiB)
- Source: isolated Windows Server 2008 analysis host
- Acquisition: offline copy supplied with the lab
- SHA-256: `1111111111111111111111111111111111111111111111111111111111111111`
- Investigator: `analyst@example.org`
- Question: Which processes were running, and did any local account material
  appear in memory?

Record the image hash, the Volatility version, and each command. A process list
is an observation, not proof of execution. Report the finding and confidence.
