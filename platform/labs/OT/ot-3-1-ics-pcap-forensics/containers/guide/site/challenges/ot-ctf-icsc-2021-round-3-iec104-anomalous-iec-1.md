# ICSC 2021 — Round 3 — 异常的IEC104分析 (anomalous IEC-104)

**CTF &amp; conference labs** · **Medium** · 0.0 MB · 0 capture file(s)

> CTF: Round 3 — 异常的IEC104分析 (anomalous IEC-104) (IEC-104).

> ⚠️ **Safety:** OT capture analysis is passive and safe. Never replay this traffic onto a real industrial network or send these commands to a real controller. This capture carries executable files (Windows PE / Linux ELF) inside the traffic, and some may be malware: work offline, hash anything you extract and never run it.

## Scenario

A capture-the-flag challenge from 工业信息安全技能大赛 2021 — Industrial Information Security Skills Competition. 57 MB — the first part is mostly background noise.

ICS CTF flags usually hide in protocol fields — register values, write payloads, function codes or timing — rather than in plain text. Work it like an analyst: map the protocol, find the operations that don't belong, then decode.

## Objectives

- Identify the protocol(s), roles and endpoints.
- Find the anomalous operations or payloads.
- Extract and decode the flag.

## 📥 Get the captures

The commands on this page read the captures from `data/`. Fetch the dataset first, from the repo root:

```bash
python3 scripts/fetch.py ctf-icsc-2021
```

- **[工业信息安全技能大赛 2021 — Industrial Information Security Skills Competition](../DATASETS.md#ctf-icsc-2021)** (`ctf-icsc-2021`), ~82.6 MB once fetched
  - **Not mirrored** (no licence that allows re-hosting): `fetch.py` downloads it from the original source
  - **Original source:** [github.com/fghcvjk/icsc2021](https://github.com/fghcvjk/icsc2021)

## Work it step by step

Two complete walkthroughs — pick your tool. Run every command from the repo root.

### With Pcapper

[Pcapper](https://github.com/SackOfHacks/pcapper) runs the OT protocol analyzers for you.

**1. Let Pcapper hunt the flag**

--ctf runs Pcapper's flag finder and decoders; --overview runs the right OT analyzer.

```bash
pcapper 'data/ctf-icsc-2021/round-3-iec104-anomalous-iec-104/01.pcapng' --ctf --overview
```

**2. Let Pcapper hunt for the flag**

--ctf runs Pcapper's flag finder and decoders; --strings surfaces cleartext that a flag may hide in.

```bash
pcapper 'data/ctf-icsc-2021/round-3-iec104-anomalous-iec-104/01.pcapng' --ctf --strings
```

**3. Map it to ATT&amp;CK for ICS**

Pcapper maps its detections to MITRE ATT&amp;CK (Enterprise + ICS) and draws the attack path.

```bash
pcapper 'data/ctf-icsc-2021/round-3-iec104-anomalous-iec-104/01.pcapng' --mitre
```

### With tshark / Wireshark

The by-hand route: display filters, field extraction and statistics.

**1. Let Pcapper hunt the flag**

```bash
capinfos 'data/ctf-icsc-2021/round-3-iec104-anomalous-iec-104/01.pcapng'
tshark -r 'data/ctf-icsc-2021/round-3-iec104-anomalous-iec-104/01.pcapng' -q -z io,phs | head -40
```

**2. Map the IEC-104 conversation**

Who polls whom? Masters/clients vs. outstations/servers, and the operation mix per pair.

```bash
tshark -r 'data/ctf-icsc-2021/round-3-iec104-anomalous-iec-104/01.pcapng' -Y iec60870_asdu -T fields -e ip.src -e ip.dst -e iec60870_asdu.typeid -e iec60870_asdu.causetx | sort | uniq -c | sort -rn | head -25
```

**3. Hunt the dangerous operations**

Flag control commands (TypeID 45 single, 46 double, 47 regulating step, 48–50 set-points, 51 bitstring, 58–64 time-tagged variants), interrogations (100 general, 101 counter), read (102), clock sync (103) and reset process (105).

```bash
tshark -r 'data/ctf-icsc-2021/round-3-iec104-anomalous-iec-104/01.pcapng' -Y 'iec60870_asdu.typeid in {45, 46, 47, 48, 49, 50, 51, 58, 59, 60, 61, 62, 63, 64, 100, 101, 102, 103, 105}' -T fields -e frame.time -e ip.src -e ip.dst -e _ws.col.Info | head -40
```

**4. Decode the protocol fields**

Register values, write payloads and odd function codes are the usual hiding places — try ASCII.

```bash
tshark -r 'data/ctf-icsc-2021/round-3-iec104-anomalous-iec-104/01.pcapng' -Y 'iec60870_asdu.ioa' -T fields -e iec60870_asdu.ioa | head -60
strings -n 6 'data/ctf-icsc-2021/round-3-iec104-anomalous-iec-104/01.pcapng' | grep -iE 'flag|ctf|\{' | head
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

**Computed evidence (auto-extracted with tshark — verify it yourself):** IEC-104 operations — C_SC_NA_1 ×32; dangerous-operation matches: 32 (top sources: 172.16.1.40 ×16, 172.16.1.42 ×16); top conversations in 01.pcapng: 112.30.216.1↔172.16.1.40 (15,738 pkts), 117.161.100.1↔172.16.1.40 (15,704 pkts), 120.220.203.1↔172.16.1.40 (9,973 pkts); flag-like strings found by `strings`: none in plain text (decode protocol fields) (basis: 1 of 1 capture file(s), first 300,000 packets each)

_Dataset credit: Competition organisers; attachments archived by fghcvjk/icsc2021 (2021) · License: None stated — credit the competition._

</details>

## Dataset & credit

**Competition organisers; attachments archived by fghcvjk/icsc2021 (2021)** — license: None stated — credit the competition

- [Dataset source — 工业信息安全技能大赛 2021 — Industrial Information Security Skills Com](https://github.com/fghcvjk/icsc2021)
- [MITRE ATT&amp;CK for ICS](https://attack.mitre.org/matrices/ics/)

<details><summary>Capture files (1)</summary>

- `data/ctf-icsc-2021/round-3-iec104-anomalous-iec-104/01.pcapng`

</details>
