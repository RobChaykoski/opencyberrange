# CISCN 2023 — modbus

**CTF &amp; conference labs** · **Medium** · 0.0 MB · 0 capture file(s)

> CTF: CISCN 2023 — modbus (Modbus/TCP).

> ⚠️ **Safety:** OT capture analysis is passive and safe. Never replay this traffic onto a real industrial network or send these commands to a real controller.

## Scenario

A capture-the-flag challenge from Chinese ICS competition challenges (CISCN, Fujian, Panda Cup, Qiangwang, Zhejiang, VCTF). Same traffic as ICSC 2021 '损坏的风机', different question.

ICS CTF flags usually hide in protocol fields — register values, write payloads, function codes or timing — rather than in plain text. Work it like an analyst: map the protocol, find the operations that don't belong, then decode.

## Objectives

- Identify the protocol(s), roles and endpoints.
- Find the anomalous operations or payloads.
- Extract and decode the flag.

## 📥 Get the captures

The commands on this page read the captures from `data/`. Fetch the dataset first, from the repo root:

```bash
python3 scripts/fetch.py ctf-cn-competitions-misc
```

- **[Chinese ICS competition challenges (CISCN, Fujian, Panda Cup, Qiangwang, Zhejiang, VCTF)](../DATASETS.md#ctf-cn-competitions-misc)** (`ctf-cn-competitions-misc`), ~24.4 MB once fetched
  - **Not mirrored** (no licence that allows re-hosting): `fetch.py` downloads it from the original source
  - **Original source:** [github.com/CTF-Archives](https://github.com/CTF-Archives)

## Work it step by step

Two complete walkthroughs — pick your tool. Run every command from the repo root.

### With Pcapper

[Pcapper](https://github.com/SackOfHacks/pcapper) runs the OT protocol analyzers for you.

**1. The capture won't open — work out why**

Its header and block markers have been tampered with (it begins aa aa aa aa), so no tool recognises it. Compare the bytes with the pcap global header (24 bytes: magic d4c3b2a1, version 2.4, snaplen, linktype) and with pcapng blocks (0a0d0d0a SHB, 1a2b3c4d byte-order magic). Recurring 4-byte timestamps (e.g. a27d6064 = 0x64607da2 = 2023-05-14) mark the record boundaries.

```bash
xxd 'data/ctf-cn-competitions-misc/ciscn-2023-modbus/modbus.pcap' | head -8
python3 -c "import sys;d=open(sys.argv[1],'rb').read();import re;print([m.start() for m in re.finditer(bytes.fromhex('a27d6064'), d)][:12])" 'data/ctf-cn-competitions-misc/ciscn-2023-modbus/modbus.pcap'
```

**2. Let Pcapper hunt the flag**

--ctf runs Pcapper's flag finder and decoders; --overview runs the right OT analyzer.

```bash
pcapper 'data/ctf-cn-competitions-misc/ciscn-2023-modbus/modbus-fixed.pcap' --ctf --overview
```

**3. Let Pcapper hunt for the flag**

--ctf runs Pcapper's flag finder and decoders; --strings surfaces cleartext that a flag may hide in.

```bash
pcapper 'data/ctf-cn-competitions-misc/ciscn-2023-modbus/modbus.pcap' --ctf --strings
```

**4. Map it to ATT&amp;CK for ICS**

Pcapper maps its detections to MITRE ATT&amp;CK (Enterprise + ICS) and draws the attack path.

```bash
pcapper 'data/ctf-cn-competitions-misc/ciscn-2023-modbus/modbus.pcap' --mitre
```

### With tshark / Wireshark

The by-hand route: display filters, field extraction and statistics.

**1. The capture won't open — work out why**

Its header and block markers have been tampered with (it begins aa aa aa aa), so no tool recognises it. Compare the bytes with the pcap global header (24 bytes: magic d4c3b2a1, version 2.4, snaplen, linktype) and with pcapng blocks (0a0d0d0a SHB, 1a2b3c4d byte-order magic). Recurring 4-byte timestamps (e.g. a27d6064 = 0x64607da2 = 2023-05-14) mark the record boundaries.

```bash
xxd 'data/ctf-cn-competitions-misc/ciscn-2023-modbus/modbus.pcap' | head -8
python3 -c "import sys;d=open(sys.argv[1],'rb').read();import re;print([m.start() for m in re.finditer(bytes.fromhex('a27d6064'), d)][:12])" 'data/ctf-cn-competitions-misc/ciscn-2023-modbus/modbus.pcap'
```

**2. Rebuild a readable capture**

Once you know the real structure, restore the markers (or re-wrap the records in a fresh pcap header) into a copy, then verify it opens.

```bash
cp 'data/ctf-cn-competitions-misc/ciscn-2023-modbus/modbus.pcap' 'data/ctf-cn-competitions-misc/ciscn-2023-modbus/modbus-fixed.pcap'
# ... patch the header/markers in 'data/ctf-cn-competitions-misc/ciscn-2023-modbus/modbus-fixed.pcap' with your fix (xxd -r / python) ...
capinfos 'data/ctf-cn-competitions-misc/ciscn-2023-modbus/modbus-fixed.pcap'
tshark -r 'data/ctf-cn-competitions-misc/ciscn-2023-modbus/modbus.pcap' -q -z io,phs | head -40
```

**3. Let Pcapper hunt the flag**

```bash
capinfos 'data/ctf-cn-competitions-misc/ciscn-2023-modbus/modbus-fixed.pcap'
```

**4. Map the Modbus/TCP conversation**

Who polls whom? Masters/clients vs. outstations/servers, and the operation mix per pair.

```bash
tshark -r 'data/ctf-cn-competitions-misc/ciscn-2023-modbus/modbus-fixed.pcap' -Y mbtcp -T fields -e ip.src -e ip.dst -e mbtcp.unit_id -e modbus.func_code | sort | uniq -c | sort -rn | head -25
```

**5. Hunt the dangerous operations**

Flag writes (FC 5/6/15/16/22/23), diagnostics (FC 8 — restart / force-listen-only), device identification (FC 43/14, recon) and Schneider UMAS (FC 90, engineering).

```bash
tshark -r 'data/ctf-cn-competitions-misc/ciscn-2023-modbus/modbus-fixed.pcap' -Y 'modbus.func_code in {5, 6, 15, 16, 22, 23, 8, 43, 90}' -T fields -e frame.time -e ip.src -e ip.dst -e _ws.col.Info | head -40
```

**6. Decode the protocol fields**

Register values, write payloads and odd function codes are the usual hiding places — try ASCII.

```bash
tshark -r 'data/ctf-cn-competitions-misc/ciscn-2023-modbus/modbus-fixed.pcap' -Y 'modbus.regval_uint16' -T fields -e modbus.regval_uint16 | head -60
strings -n 6 'data/ctf-cn-competitions-misc/ciscn-2023-modbus/modbus-fixed.pcap' | grep -iE 'flag|ctf|\{' | head
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

**Computed evidence (auto-extracted with tshark — verify it yourself):** Modbus/TCP operations — Read Holding Registers ×226, Write Single Register ×16; dangerous-operation matches: 16 (top sources: 192.168.3.130 ×8, 192.168.3.164 ×8); top conversations in modbus.pcap: 192.168.3.130↔192.168.3.164 (362 pkts), 192.168.3.164↔192.168.3.255 (72 pkts), 192.168.3.164↔224.0.0.252 (46 pkts); flag-like strings found by `strings`: none in plain text (decode protocol fields) (basis: 1 of 1 capture file(s), first 300,000 packets each)

_Dataset credit: Competition organisers; archived by CTF-Archives, C1oudfL0w0, TajangSec, ChaMd5 · License: None stated — credit each competition._

</details>

## Dataset & credit

**Competition organisers; archived by CTF-Archives, C1oudfL0w0, TajangSec, ChaMd5** — license: None stated — credit each competition

- [Dataset source — Chinese ICS competition challenges (CISCN, Fujian, Panda Cup](https://github.com/CTF-Archives)
- [MITRE ATT&amp;CK for ICS](https://attack.mitre.org/matrices/ics/)

<details><summary>Capture files (1)</summary>

- `data/ctf-cn-competitions-misc/ciscn-2023-modbus/modbus.pcap`

</details>
