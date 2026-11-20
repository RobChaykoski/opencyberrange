# DFRWS 2023 — The Troubled Elevator — network trace

**CTF &amp; conference labs** · **Medium** · 0.0 MB · 0 capture file(s)

> CTF: The Troubled Elevator — network trace (Modbus/TCP).

> ⚠️ **Safety:** OT capture analysis is passive and safe. Never replay this traffic onto a real industrial network or send these commands to a real controller.

## Scenario

A capture-the-flag challenge from DFRWS 2023 Forensic Challenge — The Troubled Elevator. A PLC-controlled elevator incident; the full challenge also ships a memory dump and CCTV.

ICS CTF flags usually hide in protocol fields — register values, write payloads, function codes or timing — rather than in plain text. Work it like an analyst: map the protocol, find the operations that don't belong, then decode.

## Objectives

- Identify the protocol(s), roles and endpoints.
- Find the anomalous operations or payloads.
- Extract and decode the flag.

## 📥 Get the captures

The commands on this page read the captures from `data/`. Fetch the dataset first, from the repo root:

```bash
python3 scripts/fetch.py ctf-dfrws-2023
```

- **[DFRWS 2023 Forensic Challenge — The Troubled Elevator](../DATASETS.md#ctf-dfrws-2023)** (`ctf-dfrws-2023`), ~30.6 MB once fetched
  - **Mirror:** this repo's [`data-v1` release](https://github.com/SackOfHacks/ICS-PCAP-Challenges/releases/tag/data-v1), 1 part (6.6 MB compressed): [part000](https://github.com/SackOfHacks/ICS-PCAP-Challenges/releases/download/data-v1/ctf-dfrws-2023.tar.part000) (6.6 MB)
  - **Original source:** [github.com/dfrws/dfrws2023-challenge](https://github.com/dfrws/dfrws2023-challenge)

Without `fetch.py`: download every part of the dataset, run `cat <dataset>.tar.part* | tar -x`, then `gunzip` the files listed in its `MIRROR-GZIPPED.txt`.

## Work it step by step

Two complete walkthroughs — pick your tool. Run every command from the repo root.

### With Pcapper

[Pcapper](https://github.com/SackOfHacks/pcapper) runs the OT protocol analyzers for you.

**1. Let Pcapper hunt the flag**

--ctf runs Pcapper's flag finder and decoders; --overview runs the right OT analyzer.

```bash
pcapper 'data/ctf-dfrws-2023/the-troubled-elevator-network-trace/142728_162728.pcapng' --ctf --overview
```

**2. Let Pcapper hunt for the flag**

--ctf runs Pcapper's flag finder and decoders; --strings surfaces cleartext that a flag may hide in.

```bash
pcapper 'data/ctf-dfrws-2023/the-troubled-elevator-network-trace/142728_162728.pcapng' --ctf --strings
```

**3. Map it to ATT&amp;CK for ICS**

Pcapper maps its detections to MITRE ATT&amp;CK (Enterprise + ICS) and draws the attack path.

```bash
pcapper 'data/ctf-dfrws-2023/the-troubled-elevator-network-trace/142728_162728.pcapng' --mitre
```

### With tshark / Wireshark

The by-hand route: display filters, field extraction and statistics.

**1. Let Pcapper hunt the flag**

```bash
capinfos 'data/ctf-dfrws-2023/the-troubled-elevator-network-trace/142728_162728.pcapng'
tshark -r 'data/ctf-dfrws-2023/the-troubled-elevator-network-trace/142728_162728.pcapng' -q -z io,phs | head -40
```

**2. Map the Modbus/TCP conversation**

Who polls whom? Masters/clients vs. outstations/servers, and the operation mix per pair.

```bash
tshark -r 'data/ctf-dfrws-2023/the-troubled-elevator-network-trace/142728_162728.pcapng' -Y mbtcp -T fields -e ip.src -e ip.dst -e mbtcp.unit_id -e modbus.func_code | sort | uniq -c | sort -rn | head -25
```

**3. Hunt the dangerous operations**

Flag writes (FC 5/6/15/16/22/23), diagnostics (FC 8 — restart / force-listen-only), device identification (FC 43/14, recon) and Schneider UMAS (FC 90, engineering).

```bash
tshark -r 'data/ctf-dfrws-2023/the-troubled-elevator-network-trace/142728_162728.pcapng' -Y 'modbus.func_code in {5, 6, 15, 16, 22, 23, 8, 43, 90}' -T fields -e frame.time -e ip.src -e ip.dst -e _ws.col.Info | head -40
```

**4. Decode the protocol fields**

Register values, write payloads and odd function codes are the usual hiding places — try ASCII.

```bash
tshark -r 'data/ctf-dfrws-2023/the-troubled-elevator-network-trace/142728_162728.pcapng' -Y 'modbus.regval_uint16' -T fields -e modbus.regval_uint16 | head -60
strings -n 6 'data/ctf-dfrws-2023/the-troubled-elevator-network-trace/142728_162728.pcapng' | grep -iE 'flag|ctf|\{' | head
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

A public write-up exists — work it yourself first, then compare: https://github.com/AmintheGHOUL/The-Troubled-Elevator-Forensic-Investigation

**Computed evidence (auto-extracted with tshark — verify it yourself):** Modbus/TCP operations — UMAS ×123529; dangerous-operation matches: 123529 (top sources: 192.168.10.45 ×61765, 192.168.10.130 ×35387, 192.168.10.121 ×24889); top conversations in 142728_162728.pcapng: 192.168.10.121↔192.168.10.45 (113,906 pkts), 192.168.10.130↔192.168.10.45 (75,497 pkts), 192.168.10.164↔192.168.10.45 (3,264 pkts); flag-like strings found by `strings`: none in plain text (decode protocol fields) (basis: 1 of 1 capture file(s), first 300,000 packets each)

_Dataset credit: DFRWS (Digital Forensics Research Workshop) (2023) · License: Repository Apache-2.0 (challenge files not separately licensed) — credit DFRWS._

</details>

## Dataset & credit

**DFRWS (Digital Forensics Research Workshop) (2023)** — license: Repository Apache-2.0 (challenge files not separately licensed) — credit DFRWS

- [Dataset source — DFRWS 2023 Forensic Challenge — The Troubled Elevator](https://github.com/dfrws/dfrws2023-challenge)
- [Write-up / solution](https://github.com/AmintheGHOUL/The-Troubled-Elevator-Forensic-Investigation)
- [MITRE ATT&amp;CK for ICS](https://attack.mitre.org/matrices/ics/)

<details><summary>Capture files (1)</summary>

- `data/ctf-dfrws-2023/the-troubled-elevator-network-trace/142728_162728.pcapng`

</details>
