# CybICS — Whispering PLC — Modbus covert C2

**CTF &amp; conference labs** · **Medium** · 0.0 MB · 0 capture file(s)

> CTF: Whispering PLC — Modbus covert C2 (Modbus/TCP).

> ⚠️ **Safety:** OT capture analysis is passive and safe. Never replay this traffic onto a real industrial network or send these commands to a real controller.

## Scenario

A capture-the-flag challenge from CybICS training platform — incident modules. Read-allowlist bypass / covert channel.

ICS CTF flags usually hide in protocol fields — register values, write payloads, function codes or timing — rather than in plain text. Work it like an analyst: map the protocol, find the operations that don't belong, then decode.

## Objectives

- Identify the protocol(s), roles and endpoints.
- Find the anomalous operations or payloads.
- Extract and decode the flag.

## 📥 Get the captures

The commands on this page read the captures from `data/`. Fetch the dataset first, from the repo root:

```bash
python3 scripts/fetch.py training-cybics
```

- **[CybICS training platform — incident modules](../DATASETS.md#training-cybics)** (`training-cybics`), ~0.3 MB once fetched
  - **Mirror:** this repo's [`data-v1` release](https://github.com/SackOfHacks/ICS-PCAP-Challenges/releases/tag/data-v1), 1 part (0.1 MB compressed): [part000](https://github.com/SackOfHacks/ICS-PCAP-Challenges/releases/download/data-v1/training-cybics.tar.part000) (0.1 MB)
  - **Original source:** [github.com/mniedermaier/CybICS](https://github.com/mniedermaier/CybICS)

Without `fetch.py`: download every part of the dataset, run `cat <dataset>.tar.part* | tar -x`, then `gunzip` the files listed in its `MIRROR-GZIPPED.txt`.

## Work it step by step

Two complete walkthroughs — pick your tool. Run every command from the repo root.

### With Pcapper

[Pcapper](https://github.com/SackOfHacks/pcapper) runs the OT protocol analyzers for you.

**1. Let Pcapper hunt the flag**

--ctf runs Pcapper's flag finder and decoders; --overview runs the right OT analyzer.

```bash
pcapper 'data/training-cybics/whispering-plc-modbus-covert-c2/baseline.pcap' --ctf --overview
```

**2. Let Pcapper hunt for the flag**

--ctf runs Pcapper's flag finder and decoders; --strings surfaces cleartext that a flag may hide in.

```bash
pcapper 'data/training-cybics/whispering-plc-modbus-covert-c2/baseline.pcap' --ctf --strings
```

**3. Map it to ATT&amp;CK for ICS**

Pcapper maps its detections to MITRE ATT&amp;CK (Enterprise + ICS) and draws the attack path.

```bash
pcapper 'data/training-cybics/whispering-plc-modbus-covert-c2/baseline.pcap' --mitre
```

### With tshark / Wireshark

The by-hand route: display filters, field extraction and statistics.

**1. Let Pcapper hunt the flag**

```bash
capinfos 'data/training-cybics/whispering-plc-modbus-covert-c2/baseline.pcap'
tshark -r 'data/training-cybics/whispering-plc-modbus-covert-c2/baseline.pcap' -q -z io,phs | head -40
```

**2. Map the Modbus/TCP conversation**

Who polls whom? Masters/clients vs. outstations/servers, and the operation mix per pair.

```bash
tshark -r 'data/training-cybics/whispering-plc-modbus-covert-c2/baseline.pcap' -Y mbtcp -T fields -e ip.src -e ip.dst -e mbtcp.unit_id -e modbus.func_code | sort | uniq -c | sort -rn | head -25
```

**3. Hunt the dangerous operations**

Flag writes (FC 5/6/15/16/22/23), diagnostics (FC 8 — restart / force-listen-only), device identification (FC 43/14, recon) and Schneider UMAS (FC 90, engineering).

```bash
tshark -r 'data/training-cybics/whispering-plc-modbus-covert-c2/baseline.pcap' -Y 'modbus.func_code in {5, 6, 15, 16, 22, 23, 8, 43, 90}' -T fields -e frame.time -e ip.src -e ip.dst -e _ws.col.Info | head -40
```

**4. Decode the protocol fields**

Register values, write payloads and odd function codes are the usual hiding places — try ASCII.

```bash
tshark -r 'data/training-cybics/whispering-plc-modbus-covert-c2/baseline.pcap' -Y 'modbus.regval_uint16' -T fields -e modbus.regval_uint16 | head -60
strings -n 6 'data/training-cybics/whispering-plc-modbus-covert-c2/baseline.pcap' | grep -iE 'flag|ctf|\{' | head
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

A public write-up exists — work it yourself first, then compare: https://github.com/mniedermaier/CybICS/blob/main/training/modbus_covert_c2/README.md

**Computed evidence (auto-extracted with tshark — verify it yourself):** Modbus/TCP operations — Read Holding Registers ×2016, Read Coils ×480; dangerous-operation matches: 0 for the Modbus/TCP filter (2,496 Modbus/TCP packets present, so the zero is real); top conversations in baseline.pcap: 172.18.0.3↔172.18.0.5 (1,824 pkts), 172.18.0.3↔172.18.0.4 (1,440 pkts); flag-like strings found by `strings`: none in plain text (decode protocol fields) (basis: 1 of 1 capture file(s), first 300,000 packets each)

_Dataset credit: Matthias Niedermaier (CybICS) (2026) · License: Repository MIT (training files not separately licensed) — credit CybICS._

</details>

## Dataset & credit

**Matthias Niedermaier (CybICS) (2026)** — license: Repository MIT (training files not separately licensed) — credit CybICS

- [Dataset source — CybICS training platform — incident modules](https://github.com/mniedermaier/CybICS)
- [Write-up / solution](https://github.com/mniedermaier/CybICS/blob/main/training/modbus_covert_c2/README.md)
- [MITRE ATT&amp;CK for ICS](https://attack.mitre.org/matrices/ics/)

<details><summary>Capture files (1)</summary>

- `data/training-cybics/whispering-plc-modbus-covert-c2/baseline.pcap`

</details>
