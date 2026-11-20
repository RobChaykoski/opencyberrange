# ICS CTF (工控CTF) — find the flag in industrial traffic

**CTF &amp; conference labs** · **Hard** · 0.0 MB · 0 capture file(s)

> An industrial-control CTF capture — the flag is hidden somewhere in the OT protocol traffic.

> ⚠️ **Safety:** OT capture analysis is passive and safe. Never replay this traffic onto a real industrial network or send these commands to a real controller.

## Scenario

An industrial-control CTF capture — the flag is hidden somewhere in the OT protocol traffic.

ICS CTF captures usually hide the flag in protocol fields rather than in plain text: register values that decode to ASCII, write payloads, file transfers over an industrial protocol, or an odd function code. Work it like a forensic analyst.

## Objectives

- Identify the protocols and endpoints.
- Find the anomalous operations or payloads.
- Extract and decode the flag.

## 📥 Get the captures

The commands on this page read the captures from `data/`. Fetch the dataset first, from the repo root:

```bash
python3 scripts/fetch.py ics-ctf-newbee119
```

- **[Chinese ICS CTF traffic (工控CTF) — NewBee119](../DATASETS.md#ics-ctf-newbee119)** (`ics-ctf-newbee119`), ~48.6 MB once fetched
  - **Not mirrored** (no licence that allows re-hosting): `fetch.py` downloads it from the original source
  - **Original source:** [github.com/NewBee119/ctf_ics_traffic](https://github.com/NewBee119/ctf_ics_traffic)

## Work it step by step

Two complete walkthroughs — pick your tool. Run every command from the repo root.

### With Pcapper

[Pcapper](https://github.com/SackOfHacks/pcapper) runs the OT protocol analyzers for you.

**1. Let Pcapper look for flags**

--ctf runs Pcapper's flag finder and decoders across the capture.

```bash
pcapper 'data/ics-ctf-newbee119/ics.pcapng' --ctf --overview
```

**2. Brute strings**

```bash
strings -n 6 'data/ics-ctf-newbee119/ics.pcapng' | grep -iE 'flag|ctf|key|\{' | head
```

**3. Let Pcapper hunt for the flag**

--ctf runs Pcapper's flag finder and decoders; --strings surfaces cleartext that a flag may hide in.

```bash
pcapper 'data/ics-ctf-newbee119/ics.pcapng' --ctf --strings
```

**4. Map it to ATT&amp;CK for ICS**

Pcapper maps its detections to MITRE ATT&amp;CK (Enterprise + ICS) and draws the attack path.

```bash
pcapper 'data/ics-ctf-newbee119/ics.pcapng' --mitre
```

### With tshark / Wireshark

The by-hand route: display filters, field extraction and statistics.

**1. Let Pcapper look for flags**

```bash
capinfos 'data/ics-ctf-newbee119/ics.pcapng'
```

**2. Protocol hierarchy**

```bash
tshark -r 'data/ics-ctf-newbee119/ics.pcapng' -q -z io,phs
```

**3. Decode the protocol payloads as ASCII**

In Modbus/TCP captures the flag usually hides in written values or payloads.

```bash
tshark -r 'data/ics-ctf-newbee119/ics.pcapng' -Y 'modbus.regval_uint16' -T fields -e modbus.regval_uint16 | head -80
```

**4. Brute strings**

```bash
strings -n 6 'data/ics-ctf-newbee119/ics.pcapng' | grep -iE 'flag|ctf|key|\{' | head
```

## Hints

<details><summary>Hint 1</summary>

Pcapper --ctf tries common encodings automatically.

</details>

<details><summary>Hint 2</summary>

Read writes, not just reads — attackers 'leave' the flag by writing it.

</details>

<details><summary>Hint 3</summary>

Concatenate register values in order and decode big-endian pairs to ASCII.

</details>

## Solution

<details><summary>Reveal walkthrough / answer</summary>

Work out where the flag is embedded; the computed evidence lists any flag-like strings found automatically — confirm them by locating the exact packets.

**Computed evidence (auto-extracted with tshark — verify it yourself):** Modbus/TCP operations — Read Holding Registers ×43579, Write Multiple Registers ×60, Write Multiple Coils ×2, Read Coils ×2; dangerous-operation matches: 62 (top sources: 192.168.1.12 ×17, 192.168.1.202 ×16, 192.168.1.201 ×12); top conversations in ics.pcapng: 192.168.1.12↔192.168.1.202 (45,302 pkts), 192.168.1.11↔192.168.1.201 (44,940 pkts), 192.168.1.10↔192.168.1.200 (42,193 pkts); flag-like strings found by `strings`: none in plain text (decode protocol fields) (basis: 1 of 1 capture file(s), first 300,000 packets each)

_Dataset credit: NewBee119 (GitHub) · License: No license stated in repo — credit the author._

</details>

## Dataset & credit

**NewBee119 (GitHub)** — license: No license stated in repo — credit the author

- [Dataset source — Chinese ICS CTF traffic (工控CTF) — NewBee119](https://github.com/NewBee119/ctf_ics_traffic)
- [MITRE ATT&amp;CK for ICS](https://attack.mitre.org/matrices/ics/)

<details><summary>Capture files (1)</summary>

- `data/ics-ctf-newbee119/ics.pcapng`

</details>
