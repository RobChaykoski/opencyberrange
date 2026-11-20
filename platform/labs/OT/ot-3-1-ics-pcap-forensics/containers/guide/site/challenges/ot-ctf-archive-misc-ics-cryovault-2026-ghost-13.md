# Cryovault 2026 — GHOST_13

**CTF &amp; conference labs** · **Medium** · 0.0 MB · 0 capture file(s)

> CTF: Cryovault 2026 — GHOST_13 (Modbus/TCP).

> ⚠️ **Safety:** OT capture analysis is passive and safe. Never replay this traffic onto a real industrial network or send these commands to a real controller.

## Scenario

A capture-the-flag challenge from ICS challenges from public CTF archives (sajjadium/ctf-archives). Multi-artifact challenge (firmware, OTA, UART log); this is the PLC traffic piece.

ICS CTF flags usually hide in protocol fields — register values, write payloads, function codes or timing — rather than in plain text. Work it like an analyst: map the protocol, find the operations that don't belong, then decode.

## Objectives

- Identify the protocol(s), roles and endpoints.
- Find the anomalous operations or payloads.
- Extract and decode the flag.

## 📥 Get the captures

The commands on this page read the captures from `data/`. Fetch the dataset first, from the repo root:

```bash
python3 scripts/fetch.py ctf-archive-misc-ics
```

- **[ICS challenges from public CTF archives (sajjadium/ctf-archives)](../DATASETS.md#ctf-archive-misc-ics)** (`ctf-archive-misc-ics`), ~9.5 MB once fetched
  - **Not mirrored** (no licence that allows re-hosting): `fetch.py` downloads it from the original source
  - **Original source:** [github.com/sajjadium/ctf-archives](https://github.com/sajjadium/ctf-archives)

## Work it step by step

Two complete walkthroughs — pick your tool. Run every command from the repo root.

### With Pcapper

[Pcapper](https://github.com/SackOfHacks/pcapper) runs the OT protocol analyzers for you.

**1. Let Pcapper hunt the flag**

--ctf runs Pcapper's flag finder and decoders; --overview runs the right OT analyzer.

```bash
pcapper 'data/ctf-archive-misc-ics/cryovault-2026-ghost-13/plc_traffic.pcap' --ctf --overview
```

**2. Let Pcapper hunt for the flag**

--ctf runs Pcapper's flag finder and decoders; --strings surfaces cleartext that a flag may hide in.

```bash
pcapper 'data/ctf-archive-misc-ics/cryovault-2026-ghost-13/plc_traffic.pcap' --ctf --strings
```

**3. Map it to ATT&amp;CK for ICS**

Pcapper maps its detections to MITRE ATT&amp;CK (Enterprise + ICS) and draws the attack path.

```bash
pcapper 'data/ctf-archive-misc-ics/cryovault-2026-ghost-13/plc_traffic.pcap' --mitre
```

### With tshark / Wireshark

The by-hand route: display filters, field extraction and statistics.

**1. Let Pcapper hunt the flag**

```bash
capinfos 'data/ctf-archive-misc-ics/cryovault-2026-ghost-13/plc_traffic.pcap'
tshark -r 'data/ctf-archive-misc-ics/cryovault-2026-ghost-13/plc_traffic.pcap' -q -z io,phs | head -40
```

**2. Map the Modbus/TCP conversation**

Who polls whom? Masters/clients vs. outstations/servers, and the operation mix per pair.

```bash
tshark -r 'data/ctf-archive-misc-ics/cryovault-2026-ghost-13/plc_traffic.pcap' -Y mbtcp -T fields -e ip.src -e ip.dst -e mbtcp.unit_id -e modbus.func_code | sort | uniq -c | sort -rn | head -25
```

**3. Hunt the dangerous operations**

Flag writes (FC 5/6/15/16/22/23), diagnostics (FC 8 — restart / force-listen-only), device identification (FC 43/14, recon) and Schneider UMAS (FC 90, engineering).

```bash
tshark -r 'data/ctf-archive-misc-ics/cryovault-2026-ghost-13/plc_traffic.pcap' -Y 'modbus.func_code in {5, 6, 15, 16, 22, 23, 8, 43, 90}' -T fields -e frame.time -e ip.src -e ip.dst -e _ws.col.Info | head -40
```

**4. Decode the protocol fields**

Register values, write payloads and odd function codes are the usual hiding places — try ASCII.

```bash
tshark -r 'data/ctf-archive-misc-ics/cryovault-2026-ghost-13/plc_traffic.pcap' -Y 'modbus.regval_uint16' -T fields -e modbus.regval_uint16 | head -60
strings -n 6 'data/ctf-archive-misc-ics/cryovault-2026-ghost-13/plc_traffic.pcap' | grep -iE 'flag|ctf|\{' | head
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

No public write-up was located for this one — the computed evidence below lists any flag-like strings found automatically; confirm them by finding the packets that carry them.

**Computed evidence (auto-extracted with tshark — verify it yourself):** Modbus/TCP operations — Write Multiple Registers ×12, Read Holding Registers ×3, Read Input Registers ×2; dangerous-operation matches: 12 (top sources: 10.13.0.1 ×11, 10.13.0.88 ×1); top conversations in plc_traffic.pcap: 10.13.0.1↔10.13.0.13 (63 pkts), 10.13.0.1↔10.13.0.88 (1 pkts); flag-like strings found by `strings`: none in plain text (decode protocol fields) (basis: 1 of 1 capture file(s), first 300,000 packets each)

_Dataset credit: Event organisers; archived by sajjadium/ctf-archives · License: Archive repository MIT (challenge files not separately licensed) — credit each event._

</details>

## Dataset & credit

**Event organisers; archived by sajjadium/ctf-archives** — license: Archive repository MIT (challenge files not separately licensed) — credit each event

- [Dataset source — ICS challenges from public CTF archives (sajjadium/ctf-archi](https://github.com/sajjadium/ctf-archives)
- [MITRE ATT&amp;CK for ICS](https://attack.mitre.org/matrices/ics/)

<details><summary>Capture files (1)</summary>

- `data/ctf-archive-misc-ics/cryovault-2026-ghost-13/plc_traffic.pcap`

</details>
