# ICSC 2026 (GY10) — 时间域隐蔽通道 'scan ghost' (timing covert channel)

**CTF &amp; conference labs** · **Medium** · 0.0 MB · 0 capture file(s)

> CTF: 时间域隐蔽通道 'scan ghost' (timing covert channel) (Modbus/TCP).

> ⚠️ **Safety:** OT capture analysis is passive and safe. Never replay this traffic onto a real industrial network or send these commands to a real controller.

## Scenario

A capture-the-flag challenge from 第十届工业信息安全技能大赛 工控安全锦标赛 2026 (GY10). A covert channel hidden in packet timing.

ICS CTF flags usually hide in protocol fields — register values, write payloads, function codes or timing — rather than in plain text. Work it like an analyst: map the protocol, find the operations that don't belong, then decode.

## Objectives

- Identify the protocol(s), roles and endpoints.
- Find the anomalous operations or payloads.
- Extract and decode the flag.

## 📥 Get the captures

The commands on this page read the captures from `data/`. Fetch the dataset first, from the repo root:

```bash
python3 scripts/fetch.py ctf-icsc-2026-gy10
```

- **[第十届工业信息安全技能大赛 工控安全锦标赛 2026 (GY10)](../DATASETS.md#ctf-icsc-2026-gy10)** (`ctf-icsc-2026-gy10`), ~5.0 MB once fetched
  - **Not mirrored** (no licence that allows re-hosting): `fetch.py` downloads it from the original source
  - **Original source:** [github.com/CTF-Archives/2026-ICSC-ICS-Champ](https://github.com/CTF-Archives/2026-ICSC-ICS-Champ)

## Work it step by step

Two complete walkthroughs — pick your tool. Run every command from the repo root.

### With Pcapper

[Pcapper](https://github.com/SackOfHacks/pcapper) runs the OT protocol analyzers for you.

**1. Let Pcapper hunt the flag**

--ctf runs Pcapper's flag finder and decoders; --overview runs the right OT analyzer.

```bash
pcapper 'data/ctf-icsc-2026-gy10/scan-ghost-timing-covert-channel/plc_protocol_id.pcapng' --ctf --overview
```

**2. Let Pcapper hunt for the flag**

--ctf runs Pcapper's flag finder and decoders; --strings surfaces cleartext that a flag may hide in.

```bash
pcapper 'data/ctf-icsc-2026-gy10/scan-ghost-timing-covert-channel/plc_protocol_id.pcapng' --ctf --strings
```

**3. Map it to ATT&amp;CK for ICS**

Pcapper maps its detections to MITRE ATT&amp;CK (Enterprise + ICS) and draws the attack path.

```bash
pcapper 'data/ctf-icsc-2026-gy10/scan-ghost-timing-covert-channel/plc_protocol_id.pcapng' --mitre
```

### With tshark / Wireshark

The by-hand route: display filters, field extraction and statistics.

**1. Let Pcapper hunt the flag**

```bash
capinfos 'data/ctf-icsc-2026-gy10/scan-ghost-timing-covert-channel/plc_protocol_id.pcapng'
tshark -r 'data/ctf-icsc-2026-gy10/scan-ghost-timing-covert-channel/plc_protocol_id.pcapng' -q -z io,phs | head -40
```

**2. Map the Modbus/TCP conversation**

Who polls whom? Masters/clients vs. outstations/servers, and the operation mix per pair.

```bash
tshark -r 'data/ctf-icsc-2026-gy10/scan-ghost-timing-covert-channel/plc_protocol_id.pcapng' -Y mbtcp -T fields -e ip.src -e ip.dst -e mbtcp.unit_id -e modbus.func_code | sort | uniq -c | sort -rn | head -25
```

**3. Hunt the dangerous operations**

Flag writes (FC 5/6/15/16/22/23), diagnostics (FC 8 — restart / force-listen-only), device identification (FC 43/14, recon) and Schneider UMAS (FC 90, engineering).

```bash
tshark -r 'data/ctf-icsc-2026-gy10/scan-ghost-timing-covert-channel/plc_protocol_id.pcapng' -Y 'modbus.func_code in {5, 6, 15, 16, 22, 23, 8, 43, 90}' -T fields -e frame.time -e ip.src -e ip.dst -e _ws.col.Info | head -40
```

**4. Decode the protocol fields**

Register values, write payloads and odd function codes are the usual hiding places — try ASCII.

```bash
tshark -r 'data/ctf-icsc-2026-gy10/scan-ghost-timing-covert-channel/plc_protocol_id.pcapng' -Y 'modbus.regval_uint16' -T fields -e modbus.regval_uint16 | head -60
strings -n 6 'data/ctf-icsc-2026-gy10/scan-ghost-timing-covert-channel/plc_protocol_id.pcapng' | grep -iE 'flag|ctf|\{' | head
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

A public write-up exists — work it yourself first, then compare: https://github.com/CTF-Archives/2026-ICSC-ICS-Champ/blob/main/README.md

**Computed evidence (auto-extracted with tshark — verify it yourself):** Modbus/TCP operations — Read Holding Registers ×90, Write Single Register ×12, Write Multiple Registers ×10; dangerous-operation matches: 22 (top sources: 192.168.1.10 ×11, 192.168.1.200 ×11); top conversations in plc_protocol_id.pcapng: 192.168.1.10↔192.168.1.200 (312 pkts); flag-like strings found by `strings`: none in plain text (decode protocol fields) (basis: 1 of 1 capture file(s), first 300,000 packets each)

_Dataset credit: Competition organisers; archived by CTF-Archives (2026) · License: None stated — credit the competition._

</details>

## Dataset & credit

**Competition organisers; archived by CTF-Archives (2026)** — license: None stated — credit the competition

- [Dataset source — 第十届工业信息安全技能大赛 工控安全锦标赛 2026 (GY10)](https://github.com/CTF-Archives/2026-ICSC-ICS-Champ)
- [Write-up / solution](https://github.com/CTF-Archives/2026-ICSC-ICS-Champ/blob/main/README.md)
- [MITRE ATT&amp;CK for ICS](https://attack.mitre.org/matrices/ics/)

<details><summary>Capture files (1)</summary>

- `data/ctf-icsc-2026-gy10/scan-ghost-timing-covert-channel/plc_protocol_id.pcapng`

</details>
