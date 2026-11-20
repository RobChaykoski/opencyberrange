# CIC Modbus 2023 — the substation's normal day

**Power grid &amp; substations** · **Medium** · 0.0 MB · 0 capture file(s)

> Baseline a simulated substation: a SCADA HMI polling three IEDs over Modbus/TCP, captured per device and network-wide.

> ⚠️ **Safety:** OT capture analysis is passive and safe. Never replay this traffic onto a real industrial network or send these commands to a real controller.

## Scenario

The CIC Modbus 2023 dataset (Canadian Institute for Cybersecurity) simulates a substation whose SCADA HMI polls intelligent electronic devices over Modbus/TCP. Attack techniques include reconnaissance, query flooding, payload loading, delay response, length change, false-data injection, frame stacking, brute-force write and replay, launched from three vantage points.

Benign traffic only: the SCADA HMI and a central agent poll IEDs ied1a, ied1b and ied4c over Modbus/TCP. Learn each device's normal function codes, registers and cadence — the reference for the three attack challenges.

## Objectives

- Identify the HMI, the IEDs and any attacker host.
- Profile normal Modbus operations per device pair.
- Find each malicious technique and its time window.
- Write detections that work even when the attacker uses the master's address.

## 📥 Get the captures

The commands on this page read the captures from `data/`. Fetch the dataset first, from the repo root:

```bash
python3 scripts/fetch.py cic-modbus-2023
```

- **[CIC Modbus Dataset 2023 — substation Modbus attacks](../DATASETS.md#cic-modbus-2023)** (`cic-modbus-2023`), ~15.76 GB once fetched
  - **Mirror:** this repo's [`data-v1` release](https://github.com/SackOfHacks/ICS-PCAP-Challenges/releases/tag/data-v1), 3 parts (3.91 GB compressed): [part000](https://github.com/SackOfHacks/ICS-PCAP-Challenges/releases/download/data-v1/cic-modbus-2023.tar.part000) (1.90 GB) · [part001](https://github.com/SackOfHacks/ICS-PCAP-Challenges/releases/download/data-v1/cic-modbus-2023.tar.part001) (1.90 GB) · [part002](https://github.com/SackOfHacks/ICS-PCAP-Challenges/releases/download/data-v1/cic-modbus-2023.tar.part002) (0.11 GB)
  - **Original source:** [unb.ca/cic/datasets/modbus-2023.html](https://www.unb.ca/cic/datasets/modbus-2023.html)

Without `fetch.py`: download every part of the dataset, run `cat <dataset>.tar.part* | tar -x`, then `gunzip` the files listed in its `MIRROR-GZIPPED.txt`.

## Work it step by step

Two complete walkthroughs — pick your tool. Run every command from the repo root.

### With Pcapper

[Pcapper](https://github.com/SackOfHacks/pcapper) runs the OT protocol analyzers for you.

**1. Triage the capture**

Duration, endpoints and protocol mix before you dive in. Pcapper's overview auto-detects the OT protocols and runs the matching analyzers.

```bash
pcapper 'data/cic-modbus-2023/Modbus Dataset/benign/network-wide-pcap-capture/network-wide/network-wide-normal-14.pcap' --overview
```

**2. Deep-dive with Pcapper (--modbus)**

Pcapper's protocol analyzer decodes the operations, flags anomalies, and --ot-commands normalizes every control/write across protocols.

```bash
pcapper 'data/cic-modbus-2023/Modbus Dataset/benign/network-wide-pcap-capture/network-wide/network-wide-normal-14.pcap' --modbus --ot-commands
```

**3. Compare per-device views**

Each device folder is a capture from that device's port — the same event looks different from each vantage point.

```bash
ls 'data/cic-modbus-2023/Modbus Dataset/benign'
pcapper 'data/cic-modbus-2023/Modbus Dataset/benign/' --modbus --ot-commands
```

**4. Map it to ATT&amp;CK for ICS**

Pcapper maps its detections to MITRE ATT&amp;CK (Enterprise + ICS) and draws the attack path.

```bash
pcapper 'data/cic-modbus-2023/Modbus Dataset/benign/network-wide-pcap-capture/network-wide/network-wide-normal-14.pcap' --mitre
```

### With tshark / Wireshark

The by-hand route: display filters, field extraction and statistics.

**1. Triage the capture**

Duration, endpoints and protocol mix before you dive in.

```bash
capinfos 'data/cic-modbus-2023/Modbus Dataset/benign/network-wide-pcap-capture/network-wide/network-wide-normal-14.pcap'
tshark -r 'data/cic-modbus-2023/Modbus Dataset/benign/network-wide-pcap-capture/network-wide/network-wide-normal-14.pcap' -q -z io,phs | head -40
```

**2. Map the Modbus/TCP conversation**

Who polls whom? Masters/clients vs. outstations/servers, and the operation mix per pair.

```bash
tshark -r 'data/cic-modbus-2023/Modbus Dataset/benign/network-wide-pcap-capture/network-wide/network-wide-normal-14.pcap' -Y mbtcp -T fields -e ip.src -e ip.dst -e mbtcp.unit_id -e modbus.func_code | sort | uniq -c | sort -rn | head -25
```

**3. Hunt the dangerous operations**

Flag writes (FC 5/6/15/16/22/23), diagnostics (FC 8 — restart / force-listen-only), device identification (FC 43/14, recon) and Schneider UMAS (FC 90, engineering).

```bash
tshark -r 'data/cic-modbus-2023/Modbus Dataset/benign/network-wide-pcap-capture/network-wide/network-wide-normal-14.pcap' -Y 'modbus.func_code in {5, 6, 15, 16, 22, 23, 8, 43, 90}' -T fields -e frame.time -e ip.src -e ip.dst -e _ws.col.Info | head -40
```

## Hints

<details><summary>Hint 1</summary>

Start from the network-/substation-wide capture, then confirm on the per-device captures.

</details>

<details><summary>Hint 2</summary>

Frame stacking and length change break the MBAP length field — look for length mismatches and malformed PDUs.

</details>

<details><summary>Hint 3</summary>

From a compromised master, look at the values and timing, not the source IP.

</details>

## Solution

<details><summary>Reveal walkthrough / answer</summary>

Labeled by vantage point (the folder). The compromised-IED set ships dated attack logs as ground truth; the CIC paper documents each technique. Score yourself on the technique ↔ window ↔ target table.

**Computed evidence (auto-extracted with tshark — verify it yourself):** Modbus/TCP operations — Read Coils ×40070, Read Holding Registers ×20063, Read Discrete Inputs ×20036, Read Input Registers ×20032, Write Single Coil ×108, Write Single Register ×88; dangerous-operation matches: 196 (top sources: 185.175.0.3 ×98, 185.175.0.4 ×52, 185.175.0.8 ×40); top conversations in vethd9e14c0-normal-10.pcap: 185.175.0.3↔185.175.0.5 (34,482 pkts), 185.175.0.1↔224.0.0.251 (4 pkts), 185.175.0.6↔224.0.0.22 (2 pkts) (basis: 3 of 62 capture file(s), first 300,000 packets each, smallest files carrying Modbus/TCP chosen)

_Dataset credit: Boakye-Boateng, K., Ghorbani, A. A., Lashkari, A. H. — Canadian Institute for Cybersecurity (UNB); Kaggle mirror by 'kiminya' (2023) · License: CIC dataset terms (free for research with citation); mirrored on Kaggle._

</details>

## Dataset & credit

**Boakye-Boateng, K., Ghorbani, A. A., Lashkari, A. H. — Canadian Institute for Cybersecurity (UNB); Kaggle mirror by 'kiminya' (2023)** — license: CIC dataset terms (free for research with citation); mirrored on Kaggle

- [Dataset source — CIC Modbus Dataset 2023 — substation Modbus attacks](https://www.unb.ca/cic/datasets/modbus-2023.html)
- [CIC Modbus Dataset 2023 (UNB)](https://www.unb.ca/cic/datasets/modbus-2023.html)
- [MITRE ATT&amp;CK for ICS](https://attack.mitre.org/matrices/ics/)

<details><summary>Capture files (62)</summary>

- `data/cic-modbus-2023/Modbus Dataset/benign/central-agent/central-agent-network-capture/veth460b141-normal.pcap`
- `data/cic-modbus-2023/Modbus Dataset/benign/ied1a/ied1a-network-capture/veth4edc015-normal-10.pcap`
- `data/cic-modbus-2023/Modbus Dataset/benign/ied1a/ied1a-network-capture/veth4edc015-normal-11.pcap`
- `data/cic-modbus-2023/Modbus Dataset/benign/ied1a/ied1a-network-capture/veth4edc015-normal-4.pcap`
- `data/cic-modbus-2023/Modbus Dataset/benign/ied1a/ied1a-network-capture/veth4edc015-normal-5.pcap`
- `data/cic-modbus-2023/Modbus Dataset/benign/ied1a/ied1a-network-capture/veth4edc015-normal-6.pcap`
- `data/cic-modbus-2023/Modbus Dataset/benign/ied1a/ied1a-network-capture/veth4edc015-normal-7.pcap`
- `data/cic-modbus-2023/Modbus Dataset/benign/ied1a/ied1a-network-capture/veth4edc015-normal-8.pcap`
- `data/cic-modbus-2023/Modbus Dataset/benign/ied1a/ied1a-network-capture/veth4edc015-normal-9.pcap`
- `data/cic-modbus-2023/Modbus Dataset/benign/ied1b/ied1b-network-capture/vethd9e14c0-normal-10.pcap`
- `data/cic-modbus-2023/Modbus Dataset/benign/ied1b/ied1b-network-capture/vethd9e14c0-normal-4.pcap`
- `data/cic-modbus-2023/Modbus Dataset/benign/ied1b/ied1b-network-capture/vethd9e14c0-normal-5.pcap`
- `data/cic-modbus-2023/Modbus Dataset/benign/ied1b/ied1b-network-capture/vethd9e14c0-normal-6.pcap`
- `data/cic-modbus-2023/Modbus Dataset/benign/ied1b/ied1b-network-capture/vethd9e14c0-normal-7.pcap`
- `data/cic-modbus-2023/Modbus Dataset/benign/ied1b/ied1b-network-capture/vethd9e14c0-normal-8.pcap`
- `data/cic-modbus-2023/Modbus Dataset/benign/ied1b/ied1b-network-capture/vethd9e14c0-normal-9.pcap`
- `data/cic-modbus-2023/Modbus Dataset/benign/ied4c/ied4c-network-capture/veth8bc3408-normal-10.pcap`
- `data/cic-modbus-2023/Modbus Dataset/benign/ied4c/ied4c-network-capture/veth8bc3408-normal-11.pcap`
- `data/cic-modbus-2023/Modbus Dataset/benign/ied4c/ied4c-network-capture/veth8bc3408-normal-4.pcap`
- `data/cic-modbus-2023/Modbus Dataset/benign/ied4c/ied4c-network-capture/veth8bc3408-normal-5.pcap`
- `data/cic-modbus-2023/Modbus Dataset/benign/ied4c/ied4c-network-capture/veth8bc3408-normal-6.pcap`
- `data/cic-modbus-2023/Modbus Dataset/benign/ied4c/ied4c-network-capture/veth8bc3408-normal-7.pcap`
- `data/cic-modbus-2023/Modbus Dataset/benign/ied4c/ied4c-network-capture/veth8bc3408-normal-8.pcap`
- `data/cic-modbus-2023/Modbus Dataset/benign/ied4c/ied4c-network-capture/veth8bc3408-normal-9.pcap`
- `data/cic-modbus-2023/Modbus Dataset/benign/network-wide-pcap-capture/network-wide/network-wide-normal-14.pcap`
- `data/cic-modbus-2023/Modbus Dataset/benign/network-wide-pcap-capture/network-wide/network-wide-normal-15.pcap`
- `data/cic-modbus-2023/Modbus Dataset/benign/network-wide-pcap-capture/network-wide/network-wide-normal-16.pcap`
- `data/cic-modbus-2023/Modbus Dataset/benign/network-wide-pcap-capture/network-wide/network-wide-normal-17.pcap`
- `data/cic-modbus-2023/Modbus Dataset/benign/network-wide-pcap-capture/network-wide/network-wide-normal-18.pcap`
- `data/cic-modbus-2023/Modbus Dataset/benign/network-wide-pcap-capture/network-wide/network-wide-normal-19.pcap`
- `data/cic-modbus-2023/Modbus Dataset/benign/network-wide-pcap-capture/network-wide/network-wide-normal-20.pcap`
- `data/cic-modbus-2023/Modbus Dataset/benign/network-wide-pcap-capture/network-wide/network-wide-normal-21.pcap`
- `data/cic-modbus-2023/Modbus Dataset/benign/network-wide-pcap-capture/network-wide/network-wide-normal-22.pcap`
- `data/cic-modbus-2023/Modbus Dataset/benign/network-wide-pcap-capture/network-wide/network-wide-normal-23.pcap`
- `data/cic-modbus-2023/Modbus Dataset/benign/network-wide-pcap-capture/network-wide/network-wide-normal-24.pcap`
- `data/cic-modbus-2023/Modbus Dataset/benign/network-wide-pcap-capture/network-wide/network-wide-normal-25.pcap`
- `data/cic-modbus-2023/Modbus Dataset/benign/network-wide-pcap-capture/network-wide/network-wide-normal-26.pcap`
- `data/cic-modbus-2023/Modbus Dataset/benign/network-wide-pcap-capture/network-wide/network-wide-normal-27.pcap`
- `data/cic-modbus-2023/Modbus Dataset/benign/network-wide-pcap-capture/network-wide/network-wide-normal-28.pcap`
- `data/cic-modbus-2023/Modbus Dataset/benign/network-wide-pcap-capture/network-wide/network-wide-normal-29.pcap`
- `data/cic-modbus-2023/Modbus Dataset/benign/network-wide-pcap-capture/network-wide/network-wide-normal-30.pcap`
- `data/cic-modbus-2023/Modbus Dataset/benign/network-wide-pcap-capture/network-wide/network-wide-normal-31.pcap`
- `data/cic-modbus-2023/Modbus Dataset/benign/network-wide-pcap-capture/network-wide/network-wide-normal-32.pcap`
- `data/cic-modbus-2023/Modbus Dataset/benign/scada-hmi/scada-hmi-network-capture/veth5bbeaa2-normal-13.pcap`
- `data/cic-modbus-2023/Modbus Dataset/benign/scada-hmi/scada-hmi-network-capture/veth5bbeaa2-normal-14.pcap`
- `data/cic-modbus-2023/Modbus Dataset/benign/scada-hmi/scada-hmi-network-capture/veth5bbeaa2-normal-15.pcap`
- `data/cic-modbus-2023/Modbus Dataset/benign/scada-hmi/scada-hmi-network-capture/veth5bbeaa2-normal-16.pcap`
- `data/cic-modbus-2023/Modbus Dataset/benign/scada-hmi/scada-hmi-network-capture/veth5bbeaa2-normal-17.pcap`
- `data/cic-modbus-2023/Modbus Dataset/benign/scada-hmi/scada-hmi-network-capture/veth5bbeaa2-normal-18.pcap`
- `data/cic-modbus-2023/Modbus Dataset/benign/scada-hmi/scada-hmi-network-capture/veth5bbeaa2-normal-19.pcap`
- `data/cic-modbus-2023/Modbus Dataset/benign/scada-hmi/scada-hmi-network-capture/veth5bbeaa2-normal-20.pcap`
- `data/cic-modbus-2023/Modbus Dataset/benign/scada-hmi/scada-hmi-network-capture/veth5bbeaa2-normal-21.pcap`
- `data/cic-modbus-2023/Modbus Dataset/benign/scada-hmi/scada-hmi-network-capture/veth5bbeaa2-normal-22.pcap`
- `data/cic-modbus-2023/Modbus Dataset/benign/scada-hmi/scada-hmi-network-capture/veth5bbeaa2-normal-23.pcap`
- `data/cic-modbus-2023/Modbus Dataset/benign/scada-hmi/scada-hmi-network-capture/veth5bbeaa2-normal-24.pcap`
- `data/cic-modbus-2023/Modbus Dataset/benign/scada-hmi/scada-hmi-network-capture/veth5bbeaa2-normal-25.pcap`
- `data/cic-modbus-2023/Modbus Dataset/benign/scada-hmi/scada-hmi-network-capture/veth5bbeaa2-normal-26.pcap`
- `data/cic-modbus-2023/Modbus Dataset/benign/scada-hmi/scada-hmi-network-capture/veth5bbeaa2-normal-27.pcap`
- `data/cic-modbus-2023/Modbus Dataset/benign/scada-hmi/scada-hmi-network-capture/veth5bbeaa2-normal-28.pcap`
- `data/cic-modbus-2023/Modbus Dataset/benign/scada-hmi/scada-hmi-network-capture/veth5bbeaa2-normal-29.pcap`
- `data/cic-modbus-2023/Modbus Dataset/benign/scada-hmi/scada-hmi-network-capture/veth5bbeaa2-normal-30.pcap`
- `data/cic-modbus-2023/Modbus Dataset/benign/scada-hmi/scada-hmi-network-capture/veth5bbeaa2-normal-31.pcap`

</details>
