# ICSC 2026 (GY10) — 工控协议流量迷局 (ICS protocol traffic puzzle)

**CTF &amp; conference labs** · **Medium** · 0.0 MB · 0 capture file(s)

> CTF: 工控协议流量迷局 (ICS protocol traffic puzzle) (S7comm).

> ⚠️ **Safety:** OT capture analysis is passive and safe. Never replay this traffic onto a real industrial network or send these commands to a real controller.

## Scenario

A capture-the-flag challenge from 第十届工业信息安全技能大赛 工控安全锦标赛 2026 (GY10). S7comm + Modbus.

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
pcapper 'data/ctf-icsc-2026-gy10/ics-protocol-traffic-puzzle/plc_maintenance.pcapng' --ctf --overview
```

**2. Let Pcapper hunt for the flag**

--ctf runs Pcapper's flag finder and decoders; --strings surfaces cleartext that a flag may hide in.

```bash
pcapper 'data/ctf-icsc-2026-gy10/ics-protocol-traffic-puzzle/plc_maintenance.pcapng' --ctf --strings
```

**3. Map it to ATT&amp;CK for ICS**

Pcapper maps its detections to MITRE ATT&amp;CK (Enterprise + ICS) and draws the attack path.

```bash
pcapper 'data/ctf-icsc-2026-gy10/ics-protocol-traffic-puzzle/plc_maintenance.pcapng' --mitre
```

### With tshark / Wireshark

The by-hand route: display filters, field extraction and statistics.

**1. Let Pcapper hunt the flag**

```bash
capinfos 'data/ctf-icsc-2026-gy10/ics-protocol-traffic-puzzle/plc_maintenance.pcapng'
tshark -r 'data/ctf-icsc-2026-gy10/ics-protocol-traffic-puzzle/plc_maintenance.pcapng' -q -z io,phs | head -40
```

**2. Map the S7comm conversation**

Who polls whom? Masters/clients vs. outstations/servers, and the operation mix per pair.

```bash
tshark -r 'data/ctf-icsc-2026-gy10/ics-protocol-traffic-puzzle/plc_maintenance.pcapng' -Y s7comm -T fields -e ip.src -e ip.dst -e s7comm.header.rosctr -e s7comm.param.func -e s7comm.param.userdata.funcgroup -e s7comm.param.userdata.subfunc | sort | uniq -c | sort -rn | head -25
```

**3. Hunt the dangerous operations**

Flag write variable (0x05), program download (0x1A–0x1C), program upload (0x1D–0x1F — logic theft), PI-service (0x28 — start/restart/compress), PLC STOP (0x29) and security/password userdata (function group 5); SZL reads (function group 4) are device recon.

```bash
tshark -r 'data/ctf-icsc-2026-gy10/ics-protocol-traffic-puzzle/plc_maintenance.pcapng' -Y 's7comm.param.func in {0x05, 0x1a, 0x1b, 0x1c, 0x1d, 0x1e, 0x1f, 0x28, 0x29} || s7comm.param.userdata.funcgroup == 5' -T fields -e frame.time -e ip.src -e ip.dst -e _ws.col.Info | head -40
```

**4. Decode the protocol fields**

Register values, write payloads and odd function codes are the usual hiding places — try ASCII.

```bash
tshark -r 'data/ctf-icsc-2026-gy10/ics-protocol-traffic-puzzle/plc_maintenance.pcapng' -Y 's7comm.resp.data' -T fields -e s7comm.resp.data | head -60
strings -n 6 'data/ctf-icsc-2026-gy10/ics-protocol-traffic-puzzle/plc_maintenance.pcapng' | grep -iE 'flag|ctf|\{' | head
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

**Computed evidence (auto-extracted with tshark — verify it yourself):** S7comm operations — Mode transition ×156, Write Var ×152, Read Var ×4; dangerous-operation matches: 152 (top sources: 192.168.1.100 ×152); top conversations in plc_maintenance.pcapng: 192.168.1.100↔192.168.1.200 (340 pkts), 192.168.1.101↔192.168.1.200 (168 pkts); flag-like strings found by `strings`: none in plain text (decode protocol fields) (basis: 1 of 1 capture file(s), first 300,000 packets each)

_Dataset credit: Competition organisers; archived by CTF-Archives (2026) · License: None stated — credit the competition._

</details>

## Dataset & credit

**Competition organisers; archived by CTF-Archives (2026)** — license: None stated — credit the competition

- [Dataset source — 第十届工业信息安全技能大赛 工控安全锦标赛 2026 (GY10)](https://github.com/CTF-Archives/2026-ICSC-ICS-Champ)
- [Write-up / solution](https://github.com/CTF-Archives/2026-ICSC-ICS-Champ/blob/main/README.md)
- [MITRE ATT&amp;CK for ICS](https://attack.mitre.org/matrices/ics/)

<details><summary>Capture files (1)</summary>

- `data/ctf-icsc-2026-gy10/ics-protocol-traffic-puzzle/plc_maintenance.pcapng`

</details>
