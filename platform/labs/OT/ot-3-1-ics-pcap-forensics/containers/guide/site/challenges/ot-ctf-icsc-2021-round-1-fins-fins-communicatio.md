# ICSC 2021 — Round 1 — Fins协议通讯 (FINS communication)

**CTF &amp; conference labs** · **Medium** · 0.0 MB · 0 capture file(s)

> CTF: Round 1 — Fins协议通讯 (FINS communication) (Omron FINS).

> ⚠️ **Safety:** OT capture analysis is passive and safe. Never replay this traffic onto a real industrial network or send these commands to a real controller.

## Scenario

A capture-the-flag challenge from 工业信息安全技能大赛 2021 — Industrial Information Security Skills Competition. Omron FINS on TCP 1355.

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
pcapper 'data/ctf-icsc-2021/round-1-fins-fins-communication/Fins协议通讯.pcap' --ctf --overview
```

**2. Let Pcapper hunt for the flag**

--ctf runs Pcapper's flag finder and decoders; --strings surfaces cleartext that a flag may hide in.

```bash
pcapper 'data/ctf-icsc-2021/round-1-fins-fins-communication/Fins协议通讯.pcap' --ctf --strings
```

**3. Map it to ATT&amp;CK for ICS**

Pcapper maps its detections to MITRE ATT&amp;CK (Enterprise + ICS) and draws the attack path.

```bash
pcapper 'data/ctf-icsc-2021/round-1-fins-fins-communication/Fins协议通讯.pcap' --mitre
```

### With tshark / Wireshark

The by-hand route: display filters, field extraction and statistics.

**1. Let Pcapper hunt the flag**

```bash
capinfos 'data/ctf-icsc-2021/round-1-fins-fins-communication/Fins协议通讯.pcap'
tshark -r 'data/ctf-icsc-2021/round-1-fins-fins-communication/Fins协议通讯.pcap' -q -z io,phs | head -40
```

**2. Map the Omron FINS conversation**

Who polls whom? Masters/clients vs. outstations/servers, and the operation mix per pair.

```bash
tshark -r 'data/ctf-icsc-2021/round-1-fins-fins-communication/Fins协议通讯.pcap' -Y omron -T fields -e ip.src -e ip.dst -e omron.command | sort | uniq -c | sort -rn | head -25
```

**3. Hunt the dangerous operations**

Flag memory-area write (0x0102), RUN (0x0401) and STOP (0x0402); controller data read (0x0501) identifies the PLC.

```bash
tshark -r 'data/ctf-icsc-2021/round-1-fins-fins-communication/Fins协议通讯.pcap' -Y 'omron' -T fields -e frame.time -e ip.src -e ip.dst -e _ws.col.Info | head -40
```

**4. Decode the protocol fields**

Register values, write payloads and odd function codes are the usual hiding places — try ASCII.

```bash
tshark -r 'data/ctf-icsc-2021/round-1-fins-fins-communication/Fins协议通讯.pcap' -Y 'omron.data' -T fields -e omron.data | head -60
strings -n 6 'data/ctf-icsc-2021/round-1-fins-fins-communication/Fins协议通讯.pcap' | grep -iE 'flag|ctf|\{' | head
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

A public write-up exists — work it yourself first, then compare: https://github.com/fghcvjk/icsc2021/tree/master/%E7%BA%BF%E4%B8%8A%E8%B5%9B%E7%AC%AC1%E5%9C%BA

**Computed evidence (auto-extracted with tshark — verify it yourself):** Omron FINS packets matching `omron`: 25,136; top conversations in Fins协议通讯.pcap: 172.31.0.73↔172.31.0.90 (40,347 pkts), 172.31.0.201↔224.0.0.251 (19 pkts), 172.31.0.90↔172.31.255.255 (10 pkts); flag-like strings found by `strings`: none in plain text (decode protocol fields) (basis: 1 of 1 capture file(s), first 300,000 packets each)

_Dataset credit: Competition organisers; attachments archived by fghcvjk/icsc2021 (2021) · License: None stated — credit the competition._

</details>

## Dataset & credit

**Competition organisers; attachments archived by fghcvjk/icsc2021 (2021)** — license: None stated — credit the competition

- [Dataset source — 工业信息安全技能大赛 2021 — Industrial Information Security Skills Com](https://github.com/fghcvjk/icsc2021)
- [Write-up / solution](https://github.com/fghcvjk/icsc2021/tree/master/%E7%BA%BF%E4%B8%8A%E8%B5%9B%E7%AC%AC1%E5%9C%BA)
- [MITRE ATT&amp;CK for ICS](https://attack.mitre.org/matrices/ics/)

<details><summary>Capture files (1)</summary>

- `data/ctf-icsc-2021/round-1-fins-fins-communication/Fins协议通讯.pcap`

</details>
