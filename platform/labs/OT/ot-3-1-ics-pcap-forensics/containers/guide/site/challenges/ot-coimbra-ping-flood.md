# Coimbra Modbus SCADA — ICMP ping-flood DDoS

**Process control &amp; PLC testbeds** · **Easy** · 0.0 MB · 0 capture file(s)

> An ICMP flood against the SCADA network. How big, from where, and did the Modbus polling survive?

> ⚠️ **Safety:** OT capture analysis is passive and safe. Never replay this traffic onto a real industrial network or send these commands to a real controller.

## Scenario

The University of Coimbra built a Modbus/TCP SCADA testbed and captured clean operation plus a set of attacks for ICS intrusion-detection research (CRITIS 2018). Each challenge isolates one condition across the three capture sets.

An ICMP flood against the SCADA network. How big, from where, and did the Modbus polling survive?

## Objectives

- Characterize the traffic in this condition.
- Quantify the attack (rate, sources, targets) where present.
- Determine the effect on the Modbus process traffic.
- Write a detection for it.

## 📥 Get the captures

The commands on this page read the captures from `data/`. Fetch the dataset first, from the repo root:

```bash
python3 scripts/fetch.py coimbra-modbus-tcp-scada
```

- **[University of Coimbra — Modbus/TCP SCADA dataset #1 (CRITIS 2018)](../DATASETS.md#coimbra-modbus-tcp-scada)** (`coimbra-modbus-tcp-scada`), ~3.74 GB once fetched
  - **Mirror:** this repo's [`data-v1` release](https://github.com/SackOfHacks/ICS-PCAP-Challenges/releases/tag/data-v1), 1 part (0.91 GB compressed): [part000](https://github.com/SackOfHacks/ICS-PCAP-Challenges/releases/download/data-v1/coimbra-modbus-tcp-scada.tar.part000) (0.91 GB)
  - **Original source:** [github.com/tjcruz-dei/ICS_PCAPS](https://github.com/tjcruz-dei/ICS_PCAPS) · [doi:10.1007/978-3-030-05849-4_19](https://doi.org/10.1007/978-3-030-05849-4_19)

Without `fetch.py`: download every part of the dataset, run `cat <dataset>.tar.part* | tar -x`, then `gunzip` the files listed in its `MIRROR-GZIPPED.txt`.

## Work it step by step

Two complete walkthroughs — pick your tool. Run every command from the repo root.

### With Pcapper

[Pcapper](https://github.com/SackOfHacks/pcapper) runs the OT protocol analyzers for you.

**1. Inventory the captures**

Three capture sets with several runs each — pick one to start, compare the rest later.

```bash
ls -lh 'data/coimbra-modbus-tcp-scada/captures1_v2/pingFloodDDoS/eth2dump-pingFloodDDoS-15m-12h_1.pcap' 'data/coimbra-modbus-tcp-scada/captures1_v2/pingFloodDDoS/eth2dump-pingFloodDDoS-1m-12h_1.pcap' 'data/coimbra-modbus-tcp-scada/captures1_v2/pingFloodDDoS/eth2dump-pingFloodDDoS-30m-12h_1.pcap' 'data/coimbra-modbus-tcp-scada/captures1_v2/pingFloodDDoS/eth2dump-pingFloodDDoS-5m-12h_1.pcap' 'data/coimbra-modbus-tcp-scada/captures1_v2/pingFloodDDoS/eth2dump-pingFloodDDoS15m-0,5h_1.pcap' 'data/coimbra-modbus-tcp-scada/captures1_v2/pingFloodDDoS/eth2dump-pingFloodDDoS15m-1h_1.pcap' ...
```

**2. Triage with Pcapper**

```bash
pcapper 'data/coimbra-modbus-tcp-scada/captures1_v2/pingFloodDDoS/eth2dump-pingFloodDDoS-15m-12h_1.pcap' --overview
```

**3. Confirm with Pcapper**

```bash
pcapper 'data/coimbra-modbus-tcp-scada/captures1_v2/pingFloodDDoS/eth2dump-pingFloodDDoS-15m-12h_1.pcap' --modbus --protocols --scan
```

**4. Map it to ATT&amp;CK for ICS**

Pcapper maps its detections to MITRE ATT&amp;CK (Enterprise + ICS) and draws the attack path.

```bash
pcapper 'data/coimbra-modbus-tcp-scada/captures1_v2/pingFloodDDoS/eth2dump-pingFloodDDoS-15m-12h_1.pcap' --mitre
```

### With tshark / Wireshark

The by-hand route: display filters, field extraction and statistics.

**1. Triage the capture**

Duration, endpoints and protocol mix before you dive in.

```bash
capinfos 'data/coimbra-modbus-tcp-scada/captures1_v2/pingFloodDDoS/eth2dump-pingFloodDDoS-15m-12h_1.pcap'
tshark -r 'data/coimbra-modbus-tcp-scada/captures1_v2/pingFloodDDoS/eth2dump-pingFloodDDoS-15m-12h_1.pcap' -q -z io,phs | head -40
```

**2. Inventory the captures**

Three capture sets with several runs each — pick one to start, compare the rest later.

```bash
ls -lh 'data/coimbra-modbus-tcp-scada/captures1_v2/pingFloodDDoS/eth2dump-pingFloodDDoS-15m-12h_1.pcap' 'data/coimbra-modbus-tcp-scada/captures1_v2/pingFloodDDoS/eth2dump-pingFloodDDoS-1m-12h_1.pcap' 'data/coimbra-modbus-tcp-scada/captures1_v2/pingFloodDDoS/eth2dump-pingFloodDDoS-30m-12h_1.pcap' 'data/coimbra-modbus-tcp-scada/captures1_v2/pingFloodDDoS/eth2dump-pingFloodDDoS-5m-12h_1.pcap' 'data/coimbra-modbus-tcp-scada/captures1_v2/pingFloodDDoS/eth2dump-pingFloodDDoS15m-0,5h_1.pcap' 'data/coimbra-modbus-tcp-scada/captures1_v2/pingFloodDDoS/eth2dump-pingFloodDDoS15m-1h_1.pcap' ...
```

**3. Measure the flood**

Rate, sources and packet sizes.

```bash
tshark -r 'data/coimbra-modbus-tcp-scada/captures1_v2/pingFloodDDoS/eth2dump-pingFloodDDoS-15m-12h_1.pcap' -Y icmp -T fields -e ip.src -e ip.dst | sort | uniq -c | sort -rn | head
tshark -r 'data/coimbra-modbus-tcp-scada/captures1_v2/pingFloodDDoS/eth2dump-pingFloodDDoS-15m-12h_1.pcap' -q -z io,stat,1,icmp,mbtcp | head -30
```

## Hints

<details><summary>Hint 1</summary>

Compare against the clean baseline challenge — the delta is the attack.

</details>

<details><summary>Hint 2</summary>

io,stat with per-protocol columns shows the attack and the process traffic side by side.

</details>

## Solution

<details><summary>Reveal walkthrough / answer</summary>

A volumetric ICMP echo flood toward the SCADA hosts; quantify packets/s and sources, and check whether the Modbus polling rate degrades during the flood. The dataset's folder/file names are the ground-truth labels.

**Computed evidence (auto-extracted with tshark — verify it yourself):** Modbus/TCP operations — Write Single Register ×3105; dangerous-operation matches: 3105 (top sources: 172.27.224.250 ×3105); top conversations in eth2dump-pingFloodDDoS1m-0,5h_1.pcap: 172.27.224.250↔172.27.224.251 (15,528 pkts), 172.27.224.250↔253.193.25.212 (1 pkts), 172.27.224.250↔195.248.23.7 (1 pkts) (basis: 3 of 37 capture file(s), first 300,000 packets each, smallest files carrying Modbus/TCP chosen)

_Dataset credit: Frazão, I., Abreu, P. H., Cruz, T., Araújo, H., Simões, P. — University of Coimbra (ATENA H2020) (2018) — doi:10.1007/978-3-030-05849-4_19 · License: CC BY 3.0 (repository content)._

</details>

## Dataset & credit

**Frazão, I., Abreu, P. H., Cruz, T., Araújo, H., Simões, P. — University of Coimbra (ATENA H2020) (2018) — doi:10.1007/978-3-030-05849-4_19** — license: CC BY 3.0 (repository content)

- [Dataset source — University of Coimbra — Modbus/TCP SCADA dataset #1 (CRITIS ](https://github.com/tjcruz-dei/ICS_PCAPS)
- [DOI 10.1007/978-3-030-05849-4_19](https://doi.org/10.1007/978-3-030-05849-4_19)
- [MITRE ATT&amp;CK for ICS](https://attack.mitre.org/matrices/ics/)

<details><summary>Capture files (37)</summary>

- `data/coimbra-modbus-tcp-scada/captures1_v2/pingFloodDDoS/eth2dump-pingFloodDDoS-15m-12h_1.pcap`
- `data/coimbra-modbus-tcp-scada/captures1_v2/pingFloodDDoS/eth2dump-pingFloodDDoS-1m-12h_1.pcap`
- `data/coimbra-modbus-tcp-scada/captures1_v2/pingFloodDDoS/eth2dump-pingFloodDDoS-30m-12h_1.pcap`
- `data/coimbra-modbus-tcp-scada/captures1_v2/pingFloodDDoS/eth2dump-pingFloodDDoS-5m-12h_1.pcap`
- `data/coimbra-modbus-tcp-scada/captures1_v2/pingFloodDDoS/eth2dump-pingFloodDDoS15m-0,5h_1.pcap`
- `data/coimbra-modbus-tcp-scada/captures1_v2/pingFloodDDoS/eth2dump-pingFloodDDoS15m-1h_1.pcap`
- `data/coimbra-modbus-tcp-scada/captures1_v2/pingFloodDDoS/eth2dump-pingFloodDDoS15m-6h_1.pcap`
- `data/coimbra-modbus-tcp-scada/captures1_v2/pingFloodDDoS/eth2dump-pingFloodDDoS1m-0,5h_1.pcap`
- `data/coimbra-modbus-tcp-scada/captures1_v2/pingFloodDDoS/eth2dump-pingFloodDDoS1m-1h_1.pcap`
- `data/coimbra-modbus-tcp-scada/captures1_v2/pingFloodDDoS/eth2dump-pingFloodDDoS1m-6h_1.pcap`
- `data/coimbra-modbus-tcp-scada/captures1_v2/pingFloodDDoS/eth2dump-pingFloodDDoS30m-1h_1.pcap`
- `data/coimbra-modbus-tcp-scada/captures1_v2/pingFloodDDoS/eth2dump-pingFloodDDoS30m-6h_1.pcap`
- `data/coimbra-modbus-tcp-scada/captures1_v2/pingFloodDDoS/eth2dump-pingFloodDDoS5m-0,5h_1.pcap`
- `data/coimbra-modbus-tcp-scada/captures1_v2/pingFloodDDoS/eth2dump-pingFloodDDoS5m-1h_1.pcap`
- `data/coimbra-modbus-tcp-scada/captures1_v2/pingFloodDDoS/eth2dump-pingFloodDDoS5m-6h_1.pcap`
- `data/coimbra-modbus-tcp-scada/captures2/pingFloodDDoS/eth2dump-pingFloodDDoS15m-0,5h_1.pcap`
- `data/coimbra-modbus-tcp-scada/captures2/pingFloodDDoS/eth2dump-pingFloodDDoS15m-1h_1.pcap`
- `data/coimbra-modbus-tcp-scada/captures2/pingFloodDDoS/eth2dump-pingFloodDDoS15m-6h_1.pcap`
- `data/coimbra-modbus-tcp-scada/captures2/pingFloodDDoS/eth2dump-pingFloodDDoS1m-0,5h_1.pcap`
- `data/coimbra-modbus-tcp-scada/captures2/pingFloodDDoS/eth2dump-pingFloodDDoS1m-1h_1.pcap`
- `data/coimbra-modbus-tcp-scada/captures2/pingFloodDDoS/eth2dump-pingFloodDDoS1m-6h_1.pcap`
- `data/coimbra-modbus-tcp-scada/captures2/pingFloodDDoS/eth2dump-pingFloodDDoS30m-1h_1.pcap`
- `data/coimbra-modbus-tcp-scada/captures2/pingFloodDDoS/eth2dump-pingFloodDDoS30m-6h_1.pcap`
- `data/coimbra-modbus-tcp-scada/captures2/pingFloodDDoS/eth2dump-pingFloodDDoS5m-0,5h_1.pcap`
- `data/coimbra-modbus-tcp-scada/captures2/pingFloodDDoS/eth2dump-pingFloodDDoS5m-1h_1.pcap`
- `data/coimbra-modbus-tcp-scada/captures2/pingFloodDDoS/eth2dump-pingFloodDDoS5m-6h_1.pcap`
- `data/coimbra-modbus-tcp-scada/captures3/pingFloodDDoS/eth2dump-pingFloodDDoS15m-0,5h_1.pcap`
- `data/coimbra-modbus-tcp-scada/captures3/pingFloodDDoS/eth2dump-pingFloodDDoS15m-1h_1.pcap`
- `data/coimbra-modbus-tcp-scada/captures3/pingFloodDDoS/eth2dump-pingFloodDDoS15m-6h_1.pcap`
- `data/coimbra-modbus-tcp-scada/captures3/pingFloodDDoS/eth2dump-pingFloodDDoS1m-0,5h_1.pcap`
- `data/coimbra-modbus-tcp-scada/captures3/pingFloodDDoS/eth2dump-pingFloodDDoS1m-1h_1.pcap`
- `data/coimbra-modbus-tcp-scada/captures3/pingFloodDDoS/eth2dump-pingFloodDDoS1m-6h_1.pcap`
- `data/coimbra-modbus-tcp-scada/captures3/pingFloodDDoS/eth2dump-pingFloodDDoS30m-1h_1.pcap`
- `data/coimbra-modbus-tcp-scada/captures3/pingFloodDDoS/eth2dump-pingFloodDDoS30m-6h_1.pcap`
- `data/coimbra-modbus-tcp-scada/captures3/pingFloodDDoS/eth2dump-pingFloodDDoS5m-0,5h_1.pcap`
- `data/coimbra-modbus-tcp-scada/captures3/pingFloodDDoS/eth2dump-pingFloodDDoS5m-1h_1.pcap`
- `data/coimbra-modbus-tcp-scada/captures3/pingFloodDDoS/eth2dump-pingFloodDDoS5m-6h_1.pcap`

</details>
