# CIC Modbus 2023 — attacks from a compromised SCADA HMI

**Power grid &amp; substations** · **Expert** · 0.0 MB · 0 capture file(s)

> The HMI itself is compromised — the attacker speaks with the master's voice.

> ⚠️ **Safety:** OT capture analysis is passive and safe. Never replay this traffic onto a real industrial network or send these commands to a real controller.

## Scenario

The CIC Modbus 2023 dataset (Canadian Institute for Cybersecurity) simulates a substation whose SCADA HMI polls intelligent electronic devices over Modbus/TCP. Attack techniques include reconnaissance, query flooding, payload loading, delay response, length change, false-data injection, frame stacking, brute-force write and replay, launched from three vantage points.

The SCADA HMI is compromised and used to attack the IEDs. Because the malicious requests come from the legitimate master, you must find them by behaviour — function code, register, value, timing — not by source address.

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
pcapper 'data/cic-modbus-2023/Modbus Dataset/attack/compromised-scada/substation-wide-capture/substation-0.pcap' --overview
```

**2. Deep-dive with Pcapper (--modbus)**

Pcapper's protocol analyzer decodes the operations, flags anomalies, and --ot-commands normalizes every control/write across protocols.

```bash
pcapper 'data/cic-modbus-2023/Modbus Dataset/attack/compromised-scada/substation-wide-capture/substation-0.pcap' --modbus --ot-commands
```

**3. Compare per-device views**

Each device folder is a capture from that device's port — the same event looks different from each vantage point.

```bash
ls 'data/cic-modbus-2023/Modbus Dataset/attack/compromised-scada'
pcapper 'data/cic-modbus-2023/Modbus Dataset/attack/compromised-scada/' --modbus --ot-commands
```

**4. Map it to ATT&amp;CK for ICS**

Pcapper maps its detections to MITRE ATT&amp;CK (Enterprise + ICS) and draws the attack path.

```bash
pcapper 'data/cic-modbus-2023/Modbus Dataset/attack/compromised-scada/substation-wide-capture/substation-0.pcap' --mitre
```

### With tshark / Wireshark

The by-hand route: display filters, field extraction and statistics.

**1. Triage the capture**

Duration, endpoints and protocol mix before you dive in.

```bash
capinfos 'data/cic-modbus-2023/Modbus Dataset/attack/compromised-scada/substation-wide-capture/substation-0.pcap'
tshark -r 'data/cic-modbus-2023/Modbus Dataset/attack/compromised-scada/substation-wide-capture/substation-0.pcap' -q -z io,phs | head -40
```

**2. Map the Modbus/TCP conversation**

Who polls whom? Masters/clients vs. outstations/servers, and the operation mix per pair.

```bash
tshark -r 'data/cic-modbus-2023/Modbus Dataset/attack/compromised-scada/substation-wide-capture/substation-0.pcap' -Y mbtcp -T fields -e ip.src -e ip.dst -e mbtcp.unit_id -e modbus.func_code | sort | uniq -c | sort -rn | head -25
```

**3. Hunt the dangerous operations**

Flag writes (FC 5/6/15/16/22/23), diagnostics (FC 8 — restart / force-listen-only), device identification (FC 43/14, recon) and Schneider UMAS (FC 90, engineering).

```bash
tshark -r 'data/cic-modbus-2023/Modbus Dataset/attack/compromised-scada/substation-wide-capture/substation-0.pcap' -Y 'modbus.func_code in {5, 6, 15, 16, 22, 23, 8, 43, 90}' -T fields -e frame.time -e ip.src -e ip.dst -e _ws.col.Info | head -40
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

**Computed evidence (auto-extracted with tshark — verify it yourself):** Modbus/TCP operations — Read Coils ×49015, Read Holding Registers ×24526, Read Input Registers ×24526, Read Discrete Inputs ×24509, Write Single Coil ×8374, Write Single Register ×92; dangerous-operation matches: 8466 (top sources: 185.175.0.3 ×4233, 185.175.0.5 ×4153, 185.175.0.8 ×44); top conversations in vethc76bd3f-7.pcap: 185.175.0.3↔185.175.0.5 (155,691 pkts), 185.175.0.1↔224.0.0.251 (11 pkts), 185.175.0.6↔224.0.0.22 (2 pkts) (basis: 3 of 57 capture file(s), first 300,000 packets each, smallest files carrying Modbus/TCP chosen)

_Dataset credit: Boakye-Boateng, K., Ghorbani, A. A., Lashkari, A. H. — Canadian Institute for Cybersecurity (UNB); Kaggle mirror by 'kiminya' (2023) · License: CIC dataset terms (free for research with citation); mirrored on Kaggle._

</details>

## Dataset & credit

**Boakye-Boateng, K., Ghorbani, A. A., Lashkari, A. H. — Canadian Institute for Cybersecurity (UNB); Kaggle mirror by 'kiminya' (2023)** — license: CIC dataset terms (free for research with citation); mirrored on Kaggle

- [Dataset source — CIC Modbus Dataset 2023 — substation Modbus attacks](https://www.unb.ca/cic/datasets/modbus-2023.html)
- [CIC Modbus Dataset 2023 (UNB)](https://www.unb.ca/cic/datasets/modbus-2023.html)
- [MITRE ATT&amp;CK for ICS](https://attack.mitre.org/matrices/ics/)

<details><summary>Capture files (57)</summary>

- `data/cic-modbus-2023/Modbus Dataset/attack/compromised-scada/central-agent/central-agent-network-captures/vethffb308b-0.pcap`
- `data/cic-modbus-2023/Modbus Dataset/attack/compromised-scada/central-agent/central-agent-network-captures/vethffb308b-1.pcap`
- `data/cic-modbus-2023/Modbus Dataset/attack/compromised-scada/ied1a/ied1a-network-captures/veth3614724-0.pcap`
- `data/cic-modbus-2023/Modbus Dataset/attack/compromised-scada/ied1a/ied1a-network-captures/veth3614724-1.pcap`
- `data/cic-modbus-2023/Modbus Dataset/attack/compromised-scada/ied1a/ied1a-network-captures/veth3614724-2.pcap`
- `data/cic-modbus-2023/Modbus Dataset/attack/compromised-scada/ied1a/ied1a-network-captures/veth3614724-3.pcap`
- `data/cic-modbus-2023/Modbus Dataset/attack/compromised-scada/ied1a/ied1a-network-captures/veth3614724-4.pcap`
- `data/cic-modbus-2023/Modbus Dataset/attack/compromised-scada/ied1a/ied1a-network-captures/veth3614724-5.pcap`
- `data/cic-modbus-2023/Modbus Dataset/attack/compromised-scada/ied1b/ied1b-network-captures/vethc76bd3f-0.pcap`
- `data/cic-modbus-2023/Modbus Dataset/attack/compromised-scada/ied1b/ied1b-network-captures/vethc76bd3f-1.pcap`
- `data/cic-modbus-2023/Modbus Dataset/attack/compromised-scada/ied1b/ied1b-network-captures/vethc76bd3f-2.pcap`
- `data/cic-modbus-2023/Modbus Dataset/attack/compromised-scada/ied1b/ied1b-network-captures/vethc76bd3f-3.pcap`
- `data/cic-modbus-2023/Modbus Dataset/attack/compromised-scada/ied1b/ied1b-network-captures/vethc76bd3f-4.pcap`
- `data/cic-modbus-2023/Modbus Dataset/attack/compromised-scada/ied1b/ied1b-network-captures/vethc76bd3f-5.pcap`
- `data/cic-modbus-2023/Modbus Dataset/attack/compromised-scada/ied1b/ied1b-network-captures/vethc76bd3f-6.pcap`
- `data/cic-modbus-2023/Modbus Dataset/attack/compromised-scada/ied1b/ied1b-network-captures/vethc76bd3f-7.pcap`
- `data/cic-modbus-2023/Modbus Dataset/attack/compromised-scada/ied4c/ied4c-network-captures/vethe685ac9-0.pcap`
- `data/cic-modbus-2023/Modbus Dataset/attack/compromised-scada/ied4c/ied4c-network-captures/vethe685ac9-1.pcap`
- `data/cic-modbus-2023/Modbus Dataset/attack/compromised-scada/ied4c/ied4c-network-captures/vethe685ac9-2.pcap`
- `data/cic-modbus-2023/Modbus Dataset/attack/compromised-scada/ied4c/ied4c-network-captures/vethe685ac9-3.pcap`
- `data/cic-modbus-2023/Modbus Dataset/attack/compromised-scada/ied4c/ied4c-network-captures/vethe685ac9-4.pcap`
- `data/cic-modbus-2023/Modbus Dataset/attack/compromised-scada/ied4c/ied4c-network-captures/vethe685ac9-5.pcap`
- `data/cic-modbus-2023/Modbus Dataset/attack/compromised-scada/scada-hmi/scada-hmi-network-capture/veth291ab9a-0.pcap`
- `data/cic-modbus-2023/Modbus Dataset/attack/compromised-scada/scada-hmi/scada-hmi-network-capture/veth291ab9a-1.pcap`
- `data/cic-modbus-2023/Modbus Dataset/attack/compromised-scada/scada-hmi/scada-hmi-network-capture/veth291ab9a-10.pcap`
- `data/cic-modbus-2023/Modbus Dataset/attack/compromised-scada/scada-hmi/scada-hmi-network-capture/veth291ab9a-11.pcap`
- `data/cic-modbus-2023/Modbus Dataset/attack/compromised-scada/scada-hmi/scada-hmi-network-capture/veth291ab9a-12.pcap`
- `data/cic-modbus-2023/Modbus Dataset/attack/compromised-scada/scada-hmi/scada-hmi-network-capture/veth291ab9a-13.pcap`
- `data/cic-modbus-2023/Modbus Dataset/attack/compromised-scada/scada-hmi/scada-hmi-network-capture/veth291ab9a-14.pcap`
- `data/cic-modbus-2023/Modbus Dataset/attack/compromised-scada/scada-hmi/scada-hmi-network-capture/veth291ab9a-15.pcap`
- `data/cic-modbus-2023/Modbus Dataset/attack/compromised-scada/scada-hmi/scada-hmi-network-capture/veth291ab9a-16.pcap`
- `data/cic-modbus-2023/Modbus Dataset/attack/compromised-scada/scada-hmi/scada-hmi-network-capture/veth291ab9a-2.pcap`
- `data/cic-modbus-2023/Modbus Dataset/attack/compromised-scada/scada-hmi/scada-hmi-network-capture/veth291ab9a-3.pcap`
- `data/cic-modbus-2023/Modbus Dataset/attack/compromised-scada/scada-hmi/scada-hmi-network-capture/veth291ab9a-4.pcap`
- `data/cic-modbus-2023/Modbus Dataset/attack/compromised-scada/scada-hmi/scada-hmi-network-capture/veth291ab9a-5.pcap`
- `data/cic-modbus-2023/Modbus Dataset/attack/compromised-scada/scada-hmi/scada-hmi-network-capture/veth291ab9a-6.pcap`
- `data/cic-modbus-2023/Modbus Dataset/attack/compromised-scada/scada-hmi/scada-hmi-network-capture/veth291ab9a-7.pcap`
- `data/cic-modbus-2023/Modbus Dataset/attack/compromised-scada/scada-hmi/scada-hmi-network-capture/veth291ab9a-8.pcap`
- `data/cic-modbus-2023/Modbus Dataset/attack/compromised-scada/scada-hmi/scada-hmi-network-capture/veth291ab9a-9.pcap`
- `data/cic-modbus-2023/Modbus Dataset/attack/compromised-scada/substation-wide-capture/substation-0.pcap`
- `data/cic-modbus-2023/Modbus Dataset/attack/compromised-scada/substation-wide-capture/substation-1.pcap`
- `data/cic-modbus-2023/Modbus Dataset/attack/compromised-scada/substation-wide-capture/substation-10.pcap`
- `data/cic-modbus-2023/Modbus Dataset/attack/compromised-scada/substation-wide-capture/substation-11.pcap`
- `data/cic-modbus-2023/Modbus Dataset/attack/compromised-scada/substation-wide-capture/substation-12.pcap`
- `data/cic-modbus-2023/Modbus Dataset/attack/compromised-scada/substation-wide-capture/substation-13.pcap`
- `data/cic-modbus-2023/Modbus Dataset/attack/compromised-scada/substation-wide-capture/substation-14.pcap`
- `data/cic-modbus-2023/Modbus Dataset/attack/compromised-scada/substation-wide-capture/substation-15.pcap`
- `data/cic-modbus-2023/Modbus Dataset/attack/compromised-scada/substation-wide-capture/substation-16.pcap`
- `data/cic-modbus-2023/Modbus Dataset/attack/compromised-scada/substation-wide-capture/substation-17.pcap`
- `data/cic-modbus-2023/Modbus Dataset/attack/compromised-scada/substation-wide-capture/substation-2.pcap`
- `data/cic-modbus-2023/Modbus Dataset/attack/compromised-scada/substation-wide-capture/substation-3.pcap`
- `data/cic-modbus-2023/Modbus Dataset/attack/compromised-scada/substation-wide-capture/substation-4.pcap`
- `data/cic-modbus-2023/Modbus Dataset/attack/compromised-scada/substation-wide-capture/substation-5.pcap`
- `data/cic-modbus-2023/Modbus Dataset/attack/compromised-scada/substation-wide-capture/substation-6.pcap`
- `data/cic-modbus-2023/Modbus Dataset/attack/compromised-scada/substation-wide-capture/substation-7.pcap`
- `data/cic-modbus-2023/Modbus Dataset/attack/compromised-scada/substation-wide-capture/substation-8.pcap`
- `data/cic-modbus-2023/Modbus Dataset/attack/compromised-scada/substation-wide-capture/substation-9.pcap`

</details>
