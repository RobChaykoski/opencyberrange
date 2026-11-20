# Industroyer2 — the real malware's IEC-104 traffic

**ICS malware &amp; intrusions** · **Expert** · 0.0 MB · 3 capture file(s)

> In April 2022 Sandworm aimed Industroyer2 at Ukrainian substations. This is its traffic.

> ⚠️ **Safety:** Traffic of real ICS malware (sandboxed). Analyze offline only; never send these commands to a real RTU.

## Scenario

Industroyer2 is the IEC 60870-5-104 malware that Sandworm deployed against Ukrainian high-voltage substations in April 2022 — the successor to the 2016 CRASHOVERRIDE/Industroyer. Netresec ran the real sample in a sandbox against the three station addresses in its hard-coded configuration and published the captures.

Reconstruct exactly what the malware tells a substation RTU to do.

## Objectives

- Identify the targeted stations (IP, common/ASDU address).
- Reconstruct the IEC-104 session: STARTDT, interrogation, command sequence.
- List the information object addresses (IOAs) it commands and the command types and values.
- Write a detection for it.

## 📥 Get the captures

The commands on this page read the captures from `data/`. Fetch the dataset first, from the repo root:

```bash
python3 scripts/fetch.py netresec-industroyer2
```

- **[Industroyer2 — IEC-104 traffic of the real malware (Netresec)](../DATASETS.md#netresec-industroyer2)** (`netresec-industroyer2`), ~0.0 MB once fetched
  - **Mirror:** this repo's [`data-v1` release](https://github.com/SackOfHacks/ICS-PCAP-Challenges/releases/tag/data-v1), 1 part (0.0 MB compressed): [part000](https://github.com/SackOfHacks/ICS-PCAP-Challenges/releases/download/data-v1/netresec-industroyer2.tar.part000) (0.0 MB)
  - **Original source:** [netresec.com/?page=Blog&amp;month=2022-04&amp;post=Industroyer2-I…](https://www.netresec.com/?page=Blog&month=2022-04&post=Industroyer2-IEC-104-Analysis)

Without `fetch.py`: download every part of the dataset, run `cat <dataset>.tar.part* | tar -x`, then `gunzip` the files listed in its `MIRROR-GZIPPED.txt`.

## Work it step by step

Two complete walkthroughs — pick your tool. Run every command from the repo root.

### With Pcapper

[Pcapper](https://github.com/SackOfHacks/pcapper) runs the OT protocol analyzers for you.

**1. Triage the capture**

Duration, endpoints and protocol mix before you dive in. Pcapper's overview auto-detects the OT protocols and runs the matching analyzers.

```bash
pcapper 'data/netresec-industroyer2/Industroyer2-StationAddress1.pcap' --overview
```

**2. Deep-dive with Pcapper (--iec104)**

Pcapper's protocol analyzer decodes the operations, flags anomalies, and --ot-commands normalizes every control/write across protocols.

```bash
pcapper 'data/netresec-industroyer2/Industroyer2-StationAddress1.pcap' --iec104 --ot-commands
```

**3. Map it to ATT&amp;CK for ICS**

Pcapper maps its detections to MITRE ATT&amp;CK (Enterprise + ICS) and draws the attack path.

```bash
pcapper 'data/netresec-industroyer2/Industroyer2-StationAddress1.pcap' --mitre
```

### With tshark / Wireshark

The by-hand route: display filters, field extraction and statistics.

**1. Triage the capture**

Duration, endpoints and protocol mix before you dive in.

```bash
capinfos 'data/netresec-industroyer2/Industroyer2-StationAddress1.pcap'
tshark -r 'data/netresec-industroyer2/Industroyer2-StationAddress1.pcap' -q -z io,phs | head -40
```

**2. Map the IEC-104 conversation**

Who polls whom? Masters/clients vs. outstations/servers, and the operation mix per pair.

```bash
tshark -r 'data/netresec-industroyer2/Industroyer2-StationAddress1.pcap' -Y iec60870_asdu -T fields -e ip.src -e ip.dst -e iec60870_asdu.typeid -e iec60870_asdu.causetx | sort | uniq -c | sort -rn | head -25
```

**3. Hunt the dangerous operations**

Flag control commands (TypeID 45 single, 46 double, 47 regulating step, 48–50 set-points, 51 bitstring, 58–64 time-tagged variants), interrogations (100 general, 101 counter), read (102), clock sync (103) and reset process (105).

```bash
tshark -r 'data/netresec-industroyer2/Industroyer2-StationAddress1.pcap' -Y 'iec60870_asdu.typeid in {45, 46, 47, 48, 49, 50, 51, 58, 59, 60, 61, 62, 63, 64, 100, 101, 102, 103, 105}' -T fields -e frame.time -e ip.src -e ip.dst -e _ws.col.Info | head -40
```

## Hints

<details><summary>Hint 1</summary>

Each capture targets one station from the malware's configuration.

</details>

<details><summary>Hint 2</summary>

Read every I-format ASDU: TypeID, cause of transmission, IOA, value.

</details>

<details><summary>Hint 3</summary>

Netresec's write-up is the reference once you have your own answer.

</details>

## Solution

<details><summary>Reveal walkthrough / answer</summary>

Industroyer2 opens IEC-104 sessions to the RTUs in its config, activates data transfer (STARTDT), and then issues control commands (single/double commands) to specific information object addresses to switch them — in the real attack, to trip circuit breakers. Your IOA/TypeID/value table from the computed evidence and the packets is the answer; compare with Netresec's analysis.

**Computed evidence (auto-extracted with tshark — verify it yourself):** IEC-104 operations — C_DC_NA_1 ×80, C_SC_NA_1 ×56, C_IC_NA_1 ×9, 70 ×4, M_SP_NA_1 ×1; dangerous-operation matches: 145 (top sources: 10.82.40.105 ×91, 192.168.121.2 ×35, 192.168.122.2 ×19); top conversations in Industroyer2-StationAddress1.pcap: 192.168.121.2↔192.168.121.2 (140 pkts) (basis: 3 of 3 capture file(s), first 300,000 packets each)

_Dataset credit: Netresec (Erik Hjelmvik) (2022) · License: CC BY 4.0._

</details>

## Dataset & credit

**Netresec (Erik Hjelmvik) (2022)** — license: CC BY 4.0

- [Dataset source — Industroyer2 — IEC-104 traffic of the real malware (Netresec](https://www.netresec.com/?page=Blog&month=2022-04&post=Industroyer2-IEC-104-Analysis)
- [Netresec — Industroyer2 IEC-104 analysis](https://www.netresec.com/?page=Blog&month=2022-04&post=Industroyer2-IEC-104-Analysis)
- [MITRE ATT&amp;CK for ICS](https://attack.mitre.org/matrices/ics/)

<details><summary>Capture files (3)</summary>

- `data/netresec-industroyer2/Industroyer2-StationAddress1.pcap`
- `data/netresec-industroyer2/Industroyer2-StationAddress2.pcap`
- `data/netresec-industroyer2/Industroyer2-StationAddress3.pcap`

</details>
