# IEC-104 testbed traffic (QUB)

**Power grid &amp; substations** · **Medium** · 0.0 MB · 0 capture file(s)

> IEC 60870-5-104 from a research testbed — read the protocol's grammar, then look for abuse.

> ⚠️ **Safety:** OT capture analysis is passive and safe. Never replay this traffic onto a real industrial network or send these commands to a real controller.

## Scenario

IEC 60870-5-104 from a research testbed — read the protocol's grammar, then look for abuse.

IEC 60870-5-104 traffic from a testbed used in research on IEC-104 attacks. Fetched from Figshare's static download host (ndownloader.figstatic.com); the figshare.com host serves a JavaScript challenge.

## Objectives

- Identify devices and protocol roles.
- Characterize the traffic.
- Find and explain any attack or unusual operation.

## 📥 Get the captures

The commands on this page read the captures from `data/`. Fetch the dataset first, from the repo root:

```bash
python3 scripts/fetch.py maynard-iec104-testbed
```

- **[IEC 60870-5-104 testbed traffic (Maynard, QUB)](../DATASETS.md#maynard-iec104-testbed)** (`maynard-iec104-testbed`), ~38.3 MB once fetched
  - **Mirror:** this repo's [`data-v1` release](https://github.com/SackOfHacks/ICS-PCAP-Challenges/releases/tag/data-v1), 1 part (22.8 MB compressed): [part000](https://github.com/SackOfHacks/ICS-PCAP-Challenges/releases/download/data-v1/maynard-iec104-testbed.tar.part000) (22.8 MB)
  - **Original source:** [doi.org/10.6084/m9.figshare.6133457.v1](https://doi.org/10.6084/m9.figshare.6133457.v1) · [doi:10.6084/m9.figshare.6133457.v1](https://doi.org/10.6084/m9.figshare.6133457.v1)

Without `fetch.py`: download every part of the dataset, run `cat <dataset>.tar.part* | tar -x`, then `gunzip` the files listed in its `MIRROR-GZIPPED.txt`.

## Work it step by step

Two complete walkthroughs — pick your tool. Run every command from the repo root.

### With Pcapper

[Pcapper](https://github.com/SackOfHacks/pcapper) runs the OT protocol analyzers for you.

**1. Triage the capture**

Duration, endpoints and protocol mix before you dive in. Pcapper's overview auto-detects the OT protocols and runs the matching analyzers.

```bash
pcapper 'data/maynard-iec104-testbed/dataset-v1.pcap' --overview
```

**2. Deep-dive with Pcapper (--iec104)**

Pcapper's protocol analyzer decodes the operations, flags anomalies, and --ot-commands normalizes every control/write across protocols.

```bash
pcapper 'data/maynard-iec104-testbed/dataset-v1.pcap' --iec104 --ot-commands
```

**3. Map it to ATT&amp;CK for ICS**

Pcapper maps its detections to MITRE ATT&amp;CK (Enterprise + ICS) and draws the attack path.

```bash
pcapper 'data/maynard-iec104-testbed/dataset-v1.pcap' --mitre
```

### With tshark / Wireshark

The by-hand route: display filters, field extraction and statistics.

**1. Triage the capture**

Duration, endpoints and protocol mix before you dive in.

```bash
capinfos 'data/maynard-iec104-testbed/dataset-v1.pcap'
tshark -r 'data/maynard-iec104-testbed/dataset-v1.pcap' -q -z io,phs | head -40
```

**2. Map the IEC-104 conversation**

Who polls whom? Masters/clients vs. outstations/servers, and the operation mix per pair.

```bash
tshark -r 'data/maynard-iec104-testbed/dataset-v1.pcap' -Y iec60870_asdu -T fields -e ip.src -e ip.dst -e iec60870_asdu.typeid -e iec60870_asdu.causetx | sort | uniq -c | sort -rn | head -25
```

**3. Hunt the dangerous operations**

Flag control commands (TypeID 45 single, 46 double, 47 regulating step, 48–50 set-points, 51 bitstring, 58–64 time-tagged variants), interrogations (100 general, 101 counter), read (102), clock sync (103) and reset process (105).

```bash
tshark -r 'data/maynard-iec104-testbed/dataset-v1.pcap' -Y 'iec60870_asdu.typeid in {45, 46, 47, 48, 49, 50, 51, 58, 59, 60, 61, 62, 63, 64, 100, 101, 102, 103, 105}' -T fields -e frame.time -e ip.src -e ip.dst -e _ws.col.Info | head -40
```

## Hints

<details><summary>Hint 1</summary>

Pcapper --overview first, then the protocol analyzer.

</details>

## Solution

<details><summary>Reveal walkthrough / answer</summary>

See the computed evidence and the dataset documentation.

**Computed evidence (auto-extracted with tshark — verify it yourself):** IEC-104 operations — C_IC_NA_1 ×17640, C_CS_NA_1 ×17620, M_ME_NB_1 ×8820; dangerous-operation matches: 35260 (top sources: 10.50.50.150 ×17625, 10.50.50.101 ×3526, 10.50.50.104 ×3526); top conversations in dataset-v1.pcap: 10.50.50.2↔10.50.50.3 (34,323 pkts), 10.50.50.105↔10.50.50.150 (16,832 pkts), 10.50.50.102↔10.50.50.150 (16,822 pkts) (basis: 1 of 1 capture file(s), first 300,000 packets each)

_Dataset credit: Peter Maynard (Queen's University Belfast) (2018) — doi:10.6084/m9.figshare.6133457.v1 · License: CC BY 4.0._

</details>

## Dataset & credit

**Peter Maynard (Queen's University Belfast) (2018) — doi:10.6084/m9.figshare.6133457.v1** — license: CC BY 4.0

- [Dataset source — IEC 60870-5-104 testbed traffic (Maynard, QUB)](https://doi.org/10.6084/m9.figshare.6133457.v1)
- [DOI 10.6084/m9.figshare.6133457.v1](https://doi.org/10.6084/m9.figshare.6133457.v1)
- [MITRE ATT&amp;CK for ICS](https://attack.mitre.org/matrices/ics/)

<details><summary>Capture files (1)</summary>

- `data/maynard-iec104-testbed/dataset-v1.pcap`

</details>
