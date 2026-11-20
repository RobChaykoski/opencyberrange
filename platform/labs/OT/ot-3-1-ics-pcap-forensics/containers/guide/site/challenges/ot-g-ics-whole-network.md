# G-ICS — one capture, four OT protocols under load

**Power grid &amp; substations** · **Medium** · 0.0 MB · 0 capture file(s)

> A loaded lab network carrying IEC 61850 Sampled Values, GOOSE, Modbus and PROFINET at once. Baseline it.

> ⚠️ **Safety:** OT capture analysis is passive and safe. Never replay this traffic onto a real industrial network or send these commands to a real controller.

## Scenario

A loaded lab network carrying IEC 61850 Sampled Values, GOOSE, Modbus and PROFINET at once. Baseline it.

A full-network capture of the G-ICS lab under 80 Mbps of background load with nine IEC 61850 Sampled-Value streams, plus GOOSE, Modbus and PROFINET — normal operation only.

## Objectives

- Identify devices and protocol roles.
- Characterize the traffic.
- Find and explain any attack or unusual operation.

## 📥 Get the captures

The commands on this page read the captures from `data/`. Fetch the dataset first, from the repo root:

```bash
python3 scripts/fetch.py g-ics-grenoble-whole-network
```

- **[G-ICS — whole-network capture (IEC 61850 SV/GOOSE, Modbus, PROFINET)](../DATASETS.md#g-ics-grenoble-whole-network)** (`g-ics-grenoble-whole-network`), ~1.53 GB once fetched
  - **Mirror:** this repo's [`data-v1` release](https://github.com/SackOfHacks/ICS-PCAP-Challenges/releases/tag/data-v1), 1 part (80.5 MB compressed): [part000](https://github.com/SackOfHacks/ICS-PCAP-Challenges/releases/download/data-v1/g-ics-grenoble-whole-network.tar.part000) (80.5 MB)
  - **Original source:** [data.mendeley.com/datasets/8cjkkw79z2/1](https://data.mendeley.com/datasets/8cjkkw79z2/1) · [doi:10.17632/8cjkkw79z2.1](https://doi.org/10.17632/8cjkkw79z2.1)

Without `fetch.py`: download every part of the dataset, run `cat <dataset>.tar.part* | tar -x`, then `gunzip` the files listed in its `MIRROR-GZIPPED.txt`.

## Work it step by step

Two complete walkthroughs — pick your tool. Run every command from the repo root.

### With Pcapper

[Pcapper](https://github.com/SackOfHacks/pcapper) runs the OT protocol analyzers for you.

**1. Triage the capture**

Duration, endpoints and protocol mix before you dive in. Pcapper's overview auto-detects the OT protocols and runs the matching analyzers.

```bash
pcapper 'data/g-ics-grenoble-whole-network/80mbps9SVwholenetwork.pcapng' --overview
```

**2. Deep-dive with Pcapper (--sv)**

Pcapper's protocol analyzer decodes the operations, flags anomalies, and --ot-commands normalizes every control/write across protocols.

```bash
pcapper 'data/g-ics-grenoble-whole-network/80mbps9SVwholenetwork.pcapng' --sv --ot-commands
```

**3. Map it to ATT&amp;CK for ICS**

Pcapper maps its detections to MITRE ATT&amp;CK (Enterprise + ICS) and draws the attack path.

```bash
pcapper 'data/g-ics-grenoble-whole-network/80mbps9SVwholenetwork.pcapng' --mitre
```

### With tshark / Wireshark

The by-hand route: display filters, field extraction and statistics.

**1. Triage the capture**

Duration, endpoints and protocol mix before you dive in.

```bash
capinfos 'data/g-ics-grenoble-whole-network/80mbps9SVwholenetwork.pcapng'
tshark -r 'data/g-ics-grenoble-whole-network/80mbps9SVwholenetwork.pcapng' -q -z io,phs | head -40
```

**2. Map the IEC 61850 SV conversation**

Who polls whom? Masters/clients vs. outstations/servers, and the operation mix per pair.

```bash
tshark -r 'data/g-ics-grenoble-whole-network/80mbps9SVwholenetwork.pcapng' -Y sv -T fields -e eth.src -e sv.svID -e sv.smpCnt | head -40
```

**3. Hunt the dangerous operations**

Flag sampled-value streams feed protection relays — look for smpCnt discontinuities, duplicate svIDs from new sources and floods.

```bash
tshark -r 'data/g-ics-grenoble-whole-network/80mbps9SVwholenetwork.pcapng' -Y 'sv' -T fields -e frame.time -e ip.src -e ip.dst -e _ws.col.Info | head -40
```

## Hints

<details><summary>Hint 1</summary>

Pcapper --overview first, then the protocol analyzer.

</details>

## Solution

<details><summary>Reveal walkthrough / answer</summary>

See the computed evidence and the dataset documentation.

**Computed evidence (auto-extracted with tshark — verify it yourself):** IEC 61850 SV packets matching `sv`: 230,170; top conversations in 80mbps9SVwholenetwork.pcapng: 192.168.105.1↔192.168.105.5 (195 pkts), 10.10.5.2↔10.10.5.4 (98 pkts), 10.10.4.2↔10.10.4.6 (19 pkts) (basis: 1 of 1 capture file(s), first 300,000 packets each)

_Dataset credit: Altaher, Thiriet, Mocanu (Univ. Grenoble Alpes) (2020) — doi:10.17632/8cjkkw79z2.1 · License: CC BY 4.0._

</details>

## Dataset & credit

**Altaher, Thiriet, Mocanu (Univ. Grenoble Alpes) (2020) — doi:10.17632/8cjkkw79z2.1** — license: CC BY 4.0

- [Dataset source — G-ICS — whole-network capture (IEC 61850 SV/GOOSE, Modbus, P](https://data.mendeley.com/datasets/8cjkkw79z2/1)
- [DOI 10.17632/8cjkkw79z2.1](https://doi.org/10.17632/8cjkkw79z2.1)
- [MITRE ATT&amp;CK for ICS](https://attack.mitre.org/matrices/ics/)

<details><summary>Capture files (1)</summary>

- `data/g-ics-grenoble-whole-network/80mbps9SVwholenetwork.pcapng`

</details>
