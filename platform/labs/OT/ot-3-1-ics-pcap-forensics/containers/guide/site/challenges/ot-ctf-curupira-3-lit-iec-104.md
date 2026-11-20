# CTF Curupira 3.0 — LIT IEC-104

**CTF &amp; conference labs** · **Medium** · 0.0 MB · 0 capture file(s)

> CTF: LIT IEC-104 (IEC-104).

> ⚠️ **Safety:** OT capture analysis is passive and safe. Never replay this traffic onto a real industrial network or send these commands to a real controller.

## Scenario

A capture-the-flag challenge from CTF Curupira 3.0 (GoHacking) 2026 — OT/SCADA track. 

ICS CTF flags usually hide in protocol fields — register values, write payloads, function codes or timing — rather than in plain text. Work it like an analyst: map the protocol, find the operations that don't belong, then decode.

## Objectives

- Identify the protocol(s), roles and endpoints.
- Find the anomalous operations or payloads.
- Extract and decode the flag.

## 📥 Get the captures

The commands on this page read the captures from `data/`. Fetch the dataset first, from the repo root:

```bash
python3 scripts/fetch.py ctf-curupira-3
```

- **[CTF Curupira 3.0 (GoHacking) 2026 — OT/SCADA track](../DATASETS.md#ctf-curupira-3)** (`ctf-curupira-3`), ~0.8 MB once fetched
  - **Not mirrored** (no licence that allows re-hosting): `fetch.py` downloads it from the original source
  - **Original source:** [github.com/celoramalho/CTF_Curupira_3.0](https://github.com/celoramalho/CTF_Curupira_3.0)

## Work it step by step

Two complete walkthroughs — pick your tool. Run every command from the repo root.

### With Pcapper

[Pcapper](https://github.com/SackOfHacks/pcapper) runs the OT protocol analyzers for you.

**1. Let Pcapper hunt the flag**

--ctf runs Pcapper's flag finder and decoders; --overview runs the right OT analyzer.

```bash
pcapper 'data/ctf-curupira-3/lit-iec-104/lit-iec104.pcap' --ctf --overview
```

**2. Let Pcapper hunt for the flag**

--ctf runs Pcapper's flag finder and decoders; --strings surfaces cleartext that a flag may hide in.

```bash
pcapper 'data/ctf-curupira-3/lit-iec-104/lit-iec104.pcap' --ctf --strings
```

**3. Map it to ATT&amp;CK for ICS**

Pcapper maps its detections to MITRE ATT&amp;CK (Enterprise + ICS) and draws the attack path.

```bash
pcapper 'data/ctf-curupira-3/lit-iec-104/lit-iec104.pcap' --mitre
```

### With tshark / Wireshark

The by-hand route: display filters, field extraction and statistics.

**1. Let Pcapper hunt the flag**

```bash
capinfos 'data/ctf-curupira-3/lit-iec-104/lit-iec104.pcap'
tshark -r 'data/ctf-curupira-3/lit-iec-104/lit-iec104.pcap' -q -z io,phs | head -40
```

**2. Map the IEC-104 conversation**

Who polls whom? Masters/clients vs. outstations/servers, and the operation mix per pair.

```bash
tshark -r 'data/ctf-curupira-3/lit-iec-104/lit-iec104.pcap' -Y iec60870_asdu -T fields -e ip.src -e ip.dst -e iec60870_asdu.typeid -e iec60870_asdu.causetx | sort | uniq -c | sort -rn | head -25
```

**3. Hunt the dangerous operations**

Flag control commands (TypeID 45 single, 46 double, 47 regulating step, 48–50 set-points, 51 bitstring, 58–64 time-tagged variants), interrogations (100 general, 101 counter), read (102), clock sync (103) and reset process (105).

```bash
tshark -r 'data/ctf-curupira-3/lit-iec-104/lit-iec104.pcap' -Y 'iec60870_asdu.typeid in {45, 46, 47, 48, 49, 50, 51, 58, 59, 60, 61, 62, 63, 64, 100, 101, 102, 103, 105}' -T fields -e frame.time -e ip.src -e ip.dst -e _ws.col.Info | head -40
```

**4. Decode the protocol fields**

Register values, write payloads and odd function codes are the usual hiding places — try ASCII.

```bash
tshark -r 'data/ctf-curupira-3/lit-iec-104/lit-iec104.pcap' -Y 'iec60870_asdu.ioa' -T fields -e iec60870_asdu.ioa | head -60
strings -n 6 'data/ctf-curupira-3/lit-iec-104/lit-iec104.pcap' | grep -iE 'flag|ctf|\{' | head
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

**Computed evidence (auto-extracted with tshark — verify it yourself):** IEC-104 operations — C_IC_NA_1 ×720, M_SP_NA_1 ×720, C_SC_NA_1 ×2, 136 ×1; dangerous-operation matches: 722 (top sources: 10.80.20.2 ×721, 10.80.20.40 ×1); top conversations in lit-iec104.pcap: 10.80.20.2↔10.80.20.40 (2,896 pkts); flag-like strings found by `strings`: none in plain text (decode protocol fields) (basis: 1 of 1 capture file(s), first 300,000 packets each)

_Dataset credit: GoHacking (organiser); GitHub mirror by celoramalho (MIT repo) (2026) · License: None stated for the challenges — credit GoHacking._

</details>

## Dataset & credit

**GoHacking (organiser); GitHub mirror by celoramalho (MIT repo) (2026)** — license: None stated for the challenges — credit GoHacking

- [Dataset source — CTF Curupira 3.0 (GoHacking) 2026 — OT/SCADA track](https://github.com/celoramalho/CTF_Curupira_3.0)
- [MITRE ATT&amp;CK for ICS](https://attack.mitre.org/matrices/ics/)

<details><summary>Capture files (1)</summary>

- `data/ctf-curupira-3/lit-iec-104/lit-iec104.pcap`

</details>
