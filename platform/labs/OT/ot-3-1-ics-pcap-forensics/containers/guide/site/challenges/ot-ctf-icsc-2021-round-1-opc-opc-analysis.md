# ICSC 2021 — Round 1 — OPC协议分析 (OPC analysis)

**CTF &amp; conference labs** · **Medium** · 0.0 MB · 0 capture file(s)

> CTF: Round 1 — OPC协议分析 (OPC analysis) (OPC DA (DCOM)).

> ⚠️ **Safety:** OT capture analysis is passive and safe. Never replay this traffic onto a real industrial network or send these commands to a real controller.

## Scenario

A capture-the-flag challenge from 工业信息安全技能大赛 2021 — Industrial Information Security Skills Competition. OPC DA over DCE-RPC.

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
pcapper 'data/ctf-icsc-2021/round-1-opc-opc-analysis/OPC协议分析.pcap' --ctf --overview
```

**2. Let Pcapper hunt for the flag**

--ctf runs Pcapper's flag finder and decoders; --strings surfaces cleartext that a flag may hide in.

```bash
pcapper 'data/ctf-icsc-2021/round-1-opc-opc-analysis/OPC协议分析.pcap' --ctf --strings
```

**3. Map it to ATT&amp;CK for ICS**

Pcapper maps its detections to MITRE ATT&amp;CK (Enterprise + ICS) and draws the attack path.

```bash
pcapper 'data/ctf-icsc-2021/round-1-opc-opc-analysis/OPC协议分析.pcap' --mitre
```

### With tshark / Wireshark

The by-hand route: display filters, field extraction and statistics.

**1. Let Pcapper hunt the flag**

```bash
capinfos 'data/ctf-icsc-2021/round-1-opc-opc-analysis/OPC协议分析.pcap'
tshark -r 'data/ctf-icsc-2021/round-1-opc-opc-analysis/OPC协议分析.pcap' -q -z io,phs | head -40
```

**2. Map the OPC DA (DCOM) conversation**

Who polls whom? Masters/clients vs. outstations/servers, and the operation mix per pair.

```bash
tshark -r 'data/ctf-icsc-2021/round-1-opc-opc-analysis/OPC协议分析.pcap' -Y dcerpc -T fields -e ip.src -e ip.dst -e dcerpc.cn_bind_to_uuid -e dcom.iid -e dcerpc.opnum | sort | uniq -c | sort -rn | head -25
```

**3. Hunt the dangerous operations**

Flag clients using OPC DA's I/O interfaces (IOPCSyncIO 39c13a52, IOPCAsyncIO2 39c13a71) read and write live process items.

```bash
tshark -r 'data/ctf-icsc-2021/round-1-opc-opc-analysis/OPC协议分析.pcap' -Y 'dcerpc.cn_bind_to_uuid in {39c13a52-011e-11d0-9675-0020afd8adb3, 39c13a71-011e-11d0-9675-0020afd8adb3} || dcom.iid in {39c13a52-011e-11d0-9675-0020afd8adb3, 39c13a71-011e-11d0-9675-0020afd8adb3}' -T fields -e frame.time -e ip.src -e ip.dst -e _ws.col.Info | head -40
```

**4. Decode the protocol fields**

Register values, write payloads and odd function codes are the usual hiding places — try ASCII.

```bash
tshark -r 'data/ctf-icsc-2021/round-1-opc-opc-analysis/OPC协议分析.pcap' -Y 'data.data' -T fields -e data.data | head -60
strings -n 6 'data/ctf-icsc-2021/round-1-opc-opc-analysis/OPC协议分析.pcap' | grep -iE 'flag|ctf|\{' | head
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

**Computed evidence (auto-extracted with tshark — verify it yourself):** OPC DA (DCOM) packets matching `dcerpc`: 4,394; dangerous-operation matches: 2 (top sources: 192.168.1.21 ×2); top conversations in OPC协议分析.pcap: 192.168.1.11↔192.168.1.21 (9,586 pkts), 192.168.1.11↔192.168.1.255 (48 pkts), 192.168.1.11↔255.255.255.255 (40 pkts); flag-like strings found by `strings`: none in plain text (decode protocol fields) (basis: 1 of 1 capture file(s), first 300,000 packets each)

_Dataset credit: Competition organisers; attachments archived by fghcvjk/icsc2021 (2021) · License: None stated — credit the competition._

</details>

## Dataset & credit

**Competition organisers; attachments archived by fghcvjk/icsc2021 (2021)** — license: None stated — credit the competition

- [Dataset source — 工业信息安全技能大赛 2021 — Industrial Information Security Skills Com](https://github.com/fghcvjk/icsc2021)
- [MITRE ATT&amp;CK for ICS](https://attack.mitre.org/matrices/ics/)

<details><summary>Capture files (1)</summary>

- `data/ctf-icsc-2021/round-1-opc-opc-analysis/OPC协议分析.pcap`

</details>
