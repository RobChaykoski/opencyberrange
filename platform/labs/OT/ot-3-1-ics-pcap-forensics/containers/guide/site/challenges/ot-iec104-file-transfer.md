# IEC-104 file transfer (FreyrSCADA)

**Power grid &amp; substations** · **Medium** · 0.0 MB · 0 capture file(s)

> The rarely seen file-service side of IEC-104. What was transferred?

> ⚠️ **Safety:** OT capture analysis is passive and safe. Never replay this traffic onto a real industrial network or send these commands to a real controller.

## Scenario

The rarely seen file-service side of IEC-104. What was transferred?

IEC 60870-5-104 file-transfer traffic between FreyrSCADA simulators — the rarely seen file-service side of IEC-104.

## Objectives

- Identify devices and protocol roles.
- Characterize the traffic.
- Find and explain any attack or unusual operation.

## 📥 Get the captures

The commands on this page read the captures from `data/`. Fetch the dataset first, from the repo root:

```bash
python3 scripts/fetch.py netresec-iec104-file-transfer
```

- **[IEC-104 file transfer between FreyrSCADA simulators (Netresec)](../DATASETS.md#netresec-iec104-file-transfer)** (`netresec-iec104-file-transfer`), ~0.2 MB once fetched
  - **Not mirrored** (no licence that allows re-hosting): `fetch.py` downloads it from the original source
  - **Original source:** [netresec.com](https://www.netresec.com/)

## Work it step by step

Two complete walkthroughs — pick your tool. Run every command from the repo root.

### With Pcapper

[Pcapper](https://github.com/SackOfHacks/pcapper) runs the OT protocol analyzers for you.

**1. Triage the capture**

Duration, endpoints and protocol mix before you dive in. Pcapper's overview auto-detects the OT protocols and runs the matching analyzers.

```bash
pcapper 'data/netresec-iec104-file-transfer/NM_2022-12-13T14-16-00.pcap' --overview
```

**2. Deep-dive with Pcapper (--iec104)**

Pcapper's protocol analyzer decodes the operations, flags anomalies, and --ot-commands normalizes every control/write across protocols.

```bash
pcapper 'data/netresec-iec104-file-transfer/NM_2022-12-13T14-16-00.pcap' --iec104 --ot-commands
```

**3. Map it to ATT&amp;CK for ICS**

Pcapper maps its detections to MITRE ATT&amp;CK (Enterprise + ICS) and draws the attack path.

```bash
pcapper 'data/netresec-iec104-file-transfer/NM_2022-12-13T14-16-00.pcap' --mitre
```

### With tshark / Wireshark

The by-hand route: display filters, field extraction and statistics.

**1. Triage the capture**

Duration, endpoints and protocol mix before you dive in.

```bash
capinfos 'data/netresec-iec104-file-transfer/NM_2022-12-13T14-16-00.pcap'
tshark -r 'data/netresec-iec104-file-transfer/NM_2022-12-13T14-16-00.pcap' -q -z io,phs | head -40
```

**2. Map the IEC-104 conversation**

Who polls whom? Masters/clients vs. outstations/servers, and the operation mix per pair.

```bash
tshark -r 'data/netresec-iec104-file-transfer/NM_2022-12-13T14-16-00.pcap' -Y iec60870_asdu -T fields -e ip.src -e ip.dst -e iec60870_asdu.typeid -e iec60870_asdu.causetx | sort | uniq -c | sort -rn | head -25
```

**3. Hunt the dangerous operations**

Flag control commands (TypeID 45 single, 46 double, 47 regulating step, 48–50 set-points, 51 bitstring, 58–64 time-tagged variants), interrogations (100 general, 101 counter), read (102), clock sync (103) and reset process (105).

```bash
tshark -r 'data/netresec-iec104-file-transfer/NM_2022-12-13T14-16-00.pcap' -Y 'iec60870_asdu.typeid in {45, 46, 47, 48, 49, 50, 51, 58, 59, 60, 61, 62, 63, 64, 100, 101, 102, 103, 105}' -T fields -e frame.time -e ip.src -e ip.dst -e _ws.col.Info | head -40
```

## Hints

<details><summary>Hint 1</summary>

Pcapper --overview first, then the protocol analyzer.

</details>

## Solution

<details><summary>Reveal walkthrough / answer</summary>

See the computed evidence and the dataset documentation.

**Computed evidence (auto-extracted with tshark — verify it yourself):** IEC-104 operations — 125 ×384, 122 ×22, 123 ×21, 124 ×21, 121 ×19, C_IC_NA_1 ×3, C_CI_NA_1 ×3, C_CS_NA_1 ×2; dangerous-operation matches: 8 (top sources: 127.0.0.1 ×8); top conversations in NM_2022-12-13T14-16-00.pcap: 127.0.0.1↔127.0.0.1 (1,857 pkts) (basis: 1 of 1 capture file(s), first 300,000 packets each)

_Dataset credit: Netresec (2022) · License: Not stated — credit Netresec._

</details>

## Dataset & credit

**Netresec (2022)** — license: Not stated — credit Netresec

- [Dataset source — IEC-104 file transfer between FreyrSCADA simulators (Netrese](https://www.netresec.com/)
- [MITRE ATT&amp;CK for ICS](https://attack.mitre.org/matrices/ics/)

<details><summary>Capture files (1)</summary>

- `data/netresec-iec104-file-transfer/NM_2022-12-13T14-16-00.pcap`

</details>
