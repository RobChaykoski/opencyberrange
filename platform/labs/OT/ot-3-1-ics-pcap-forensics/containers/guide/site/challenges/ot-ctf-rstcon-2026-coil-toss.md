# RSTCON 2026 — Coil Toss

**CTF &amp; conference labs** · **Medium** · 0.0 MB · 0 capture file(s)

> CTF: Coil Toss (Modbus/TCP).

> ⚠️ **Safety:** OT capture analysis is passive and safe. Never replay this traffic onto a real industrial network or send these commands to a real controller.

## Scenario

A capture-the-flag challenge from RSTCON CTF 2026 — forensics. 

ICS CTF flags usually hide in protocol fields — register values, write payloads, function codes or timing — rather than in plain text. Work it like an analyst: map the protocol, find the operations that don't belong, then decode.

## Objectives

- Identify the protocol(s), roles and endpoints.
- Find the anomalous operations or payloads.
- Extract and decode the flag.

## 📥 Get the captures

The commands on this page read the captures from `data/`. Fetch the dataset first, from the repo root:

```bash
python3 scripts/fetch.py ctf-rstcon-2026
```

- **[RSTCON CTF 2026 — forensics](../DATASETS.md#ctf-rstcon-2026)** (`ctf-rstcon-2026`), ~0.1 MB once fetched
  - **Not mirrored** (no licence that allows re-hosting): `fetch.py` downloads it from the original source
  - **Original source:** [github.com/RST-Group/RSTCON-CTF-2026-public](https://github.com/RST-Group/RSTCON-CTF-2026-public)

## Work it step by step

Two complete walkthroughs — pick your tool. Run every command from the repo root.

### With Pcapper

[Pcapper](https://github.com/SackOfHacks/pcapper) runs the OT protocol analyzers for you.

**1. Let Pcapper hunt the flag**

--ctf runs Pcapper's flag finder and decoders; --overview runs the right OT analyzer.

```bash
pcapper 'data/ctf-rstcon-2026/coil-toss/coil-toss.pcap' --ctf --overview
```

**2. Let Pcapper hunt for the flag**

--ctf runs Pcapper's flag finder and decoders; --strings surfaces cleartext that a flag may hide in.

```bash
pcapper 'data/ctf-rstcon-2026/coil-toss/coil-toss.pcap' --ctf --strings
```

**3. Map it to ATT&amp;CK for ICS**

Pcapper maps its detections to MITRE ATT&amp;CK (Enterprise + ICS) and draws the attack path.

```bash
pcapper 'data/ctf-rstcon-2026/coil-toss/coil-toss.pcap' --mitre
```

### With tshark / Wireshark

The by-hand route: display filters, field extraction and statistics.

**1. Let Pcapper hunt the flag**

```bash
capinfos 'data/ctf-rstcon-2026/coil-toss/coil-toss.pcap'
tshark -r 'data/ctf-rstcon-2026/coil-toss/coil-toss.pcap' -q -z io,phs | head -40
```

**2. Map the Modbus/TCP conversation**

Who polls whom? Masters/clients vs. outstations/servers, and the operation mix per pair.

```bash
tshark -r 'data/ctf-rstcon-2026/coil-toss/coil-toss.pcap' -Y mbtcp -T fields -e ip.src -e ip.dst -e mbtcp.unit_id -e modbus.func_code | sort | uniq -c | sort -rn | head -25
```

**3. Hunt the dangerous operations**

Flag writes (FC 5/6/15/16/22/23), diagnostics (FC 8 — restart / force-listen-only), device identification (FC 43/14, recon) and Schneider UMAS (FC 90, engineering).

```bash
tshark -r 'data/ctf-rstcon-2026/coil-toss/coil-toss.pcap' -Y 'modbus.func_code in {5, 6, 15, 16, 22, 23, 8, 43, 90}' -T fields -e frame.time -e ip.src -e ip.dst -e _ws.col.Info | head -40
```

**4. Decode the protocol fields**

Register values, write payloads and odd function codes are the usual hiding places — try ASCII.

```bash
tshark -r 'data/ctf-rstcon-2026/coil-toss/coil-toss.pcap' -Y 'modbus.regval_uint16' -T fields -e modbus.regval_uint16 | head -60
strings -n 6 'data/ctf-rstcon-2026/coil-toss/coil-toss.pcap' | grep -iE 'flag|ctf|\{' | head
```

## Hints

<details><summary>Hint 1</summary>

Pcapper --ctf tries common encodings automatically.

</details>

<details><summary>Hint 2</summary>

Read writes, not just reads — the flag is often written.

</details>

<details><summary>Hint 3</summary>

Concatenate register values in order and decode the 16-bit words as ASCII.

</details>

## Solution

<details><summary>Reveal walkthrough / answer</summary>

A public write-up exists — work it yourself first, then compare: https://github.com/RST-Group/RSTCON-CTF-2026-public/blob/main/forensic/coil-toss/writeup/solution.md

**Computed evidence (auto-extracted with tshark — verify it yourself):** Modbus/TCP operations — Read Holding Registers ×144, Write Single Register ×40, Write Single Coil ×12; dangerous-operation matches: 52 (top sources: 192.168.95.40 ×26, 192.168.95.10 ×26); top conversations in coil-toss.pcap: 192.168.95.10↔192.168.95.40 (398 pkts); flag-like strings found by `strings`: none in plain text (decode protocol fields) (basis: 1 of 1 capture file(s), first 300,000 packets each)

_Dataset credit: RST Group (official public repo) (2026) · License: None stated — credit RST Group._

</details>

## Dataset & credit

**RST Group (official public repo) (2026)** — license: None stated — credit RST Group

- [Dataset source — RSTCON CTF 2026 — forensics](https://github.com/RST-Group/RSTCON-CTF-2026-public)
- [Write-up / solution](https://github.com/RST-Group/RSTCON-CTF-2026-public/blob/main/forensic/coil-toss/writeup/solution.md)
- [MITRE ATT&amp;CK for ICS](https://attack.mitre.org/matrices/ics/)

<details><summary>Capture files (1)</summary>

- `data/ctf-rstcon-2026/coil-toss/coil-toss.pcap`

</details>
