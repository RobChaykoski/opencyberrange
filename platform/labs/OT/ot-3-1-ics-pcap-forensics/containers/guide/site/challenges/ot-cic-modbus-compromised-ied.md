# CIC Modbus 2023 — attacks from a compromised IED

**Power grid &amp; substations** · **Expert** · 0.0 MB · 0 capture file(s)

> A field device has been turned against the substation. Dated attack logs are your answer key.

> ⚠️ **Safety:** OT capture analysis is passive and safe. Never replay this traffic onto a real industrial network or send these commands to a real controller.

## Scenario

The CIC Modbus 2023 dataset (Canadian Institute for Cybersecurity) simulates a substation whose SCADA HMI polls intelligent electronic devices over Modbus/TCP. Attack techniques include reconnaissance, query flooding, payload loading, delay response, length change, false-data injection, frame stacking, brute-force write and replay, launched from three vantage points.

An IED is compromised and used as the attack platform, including against the trust/agent system. The dataset ships dated attack logs alongside the per-device captures — use them only to check your timeline.

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
pcapper 'data/cic-modbus-2023/Modbus Dataset/attack/compromised-ied/central-agent/central-agent-network-captures/vethffb308b-0.pcap' --overview
```

**2. Deep-dive with Pcapper (--modbus)**

Pcapper's protocol analyzer decodes the operations, flags anomalies, and --ot-commands normalizes every control/write across protocols.

```bash
pcapper 'data/cic-modbus-2023/Modbus Dataset/attack/compromised-ied/central-agent/central-agent-network-captures/vethffb308b-0.pcap' --modbus --ot-commands
```

**3. Compare per-device views**

Each device folder is a capture from that device's port — the same event looks different from each vantage point.

```bash
ls 'data/cic-modbus-2023/Modbus Dataset/attack/compromised-ied'
pcapper 'data/cic-modbus-2023/Modbus Dataset/attack/compromised-ied/' --modbus --ot-commands
```

**4. Map it to ATT&amp;CK for ICS**

Pcapper maps its detections to MITRE ATT&amp;CK (Enterprise + ICS) and draws the attack path.

```bash
pcapper 'data/cic-modbus-2023/Modbus Dataset/attack/compromised-ied/central-agent/central-agent-network-captures/vethffb308b-0.pcap' --mitre
```

### With tshark / Wireshark

The by-hand route: display filters, field extraction and statistics.

**1. Triage the capture**

Duration, endpoints and protocol mix before you dive in.

```bash
capinfos 'data/cic-modbus-2023/Modbus Dataset/attack/compromised-ied/central-agent/central-agent-network-captures/vethffb308b-0.pcap'
tshark -r 'data/cic-modbus-2023/Modbus Dataset/attack/compromised-ied/central-agent/central-agent-network-captures/vethffb308b-0.pcap' -q -z io,phs | head -40
```

**2. Map the Modbus/TCP conversation**

Who polls whom? Masters/clients vs. outstations/servers, and the operation mix per pair.

```bash
tshark -r 'data/cic-modbus-2023/Modbus Dataset/attack/compromised-ied/central-agent/central-agent-network-captures/vethffb308b-0.pcap' -Y mbtcp -T fields -e ip.src -e ip.dst -e mbtcp.unit_id -e modbus.func_code | sort | uniq -c | sort -rn | head -25
```

**3. Hunt the dangerous operations**

Flag writes (FC 5/6/15/16/22/23), diagnostics (FC 8 — restart / force-listen-only), device identification (FC 43/14, recon) and Schneider UMAS (FC 90, engineering).

```bash
tshark -r 'data/cic-modbus-2023/Modbus Dataset/attack/compromised-ied/central-agent/central-agent-network-captures/vethffb308b-0.pcap' -Y 'modbus.func_code in {5, 6, 15, 16, 22, 23, 8, 43, 90}' -T fields -e frame.time -e ip.src -e ip.dst -e _ws.col.Info | head -40
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

**Computed evidence (auto-extracted with tshark — verify it yourself):** Modbus/TCP operations — Read Coils ×59475, Read Discrete Inputs ×29690, Read Input Registers ×29682, Read Holding Registers ×29677, Write Single Register ×256, Write Single Coil ×140; dangerous-operation matches: 396 (top sources: 185.175.0.2 ×198, 185.175.0.8 ×111, 185.175.0.4 ×45); top conversations in vethc76bd3f-5.pcap: 185.175.0.2↔185.175.0.5 (235,073 pkts), 185.175.0.1↔224.0.0.251 (19 pkts) (basis: 3 of 43 capture file(s), first 300,000 packets each, smallest files carrying Modbus/TCP chosen)

_Dataset credit: Boakye-Boateng, K., Ghorbani, A. A., Lashkari, A. H. — Canadian Institute for Cybersecurity (UNB); Kaggle mirror by 'kiminya' (2023) · License: CIC dataset terms (free for research with citation); mirrored on Kaggle._

</details>

## Dataset & credit

**Boakye-Boateng, K., Ghorbani, A. A., Lashkari, A. H. — Canadian Institute for Cybersecurity (UNB); Kaggle mirror by 'kiminya' (2023)** — license: CIC dataset terms (free for research with citation); mirrored on Kaggle

- [Dataset source — CIC Modbus Dataset 2023 — substation Modbus attacks](https://www.unb.ca/cic/datasets/modbus-2023.html)
- [CIC Modbus Dataset 2023 (UNB)](https://www.unb.ca/cic/datasets/modbus-2023.html)
- [MITRE ATT&amp;CK for ICS](https://attack.mitre.org/matrices/ics/)

<details><summary>Capture files (43)</summary>

- `data/cic-modbus-2023/Modbus Dataset/attack/compromised-ied/central-agent/central-agent-network-captures/vethffb308b-0.pcap`
- `data/cic-modbus-2023/Modbus Dataset/attack/compromised-ied/central-agent/central-agent-network-captures/vethffb308b-1.pcap`
- `data/cic-modbus-2023/Modbus Dataset/attack/compromised-ied/central-agent/central-agent-network-captures/vethffb308b-2.pcap`
- `data/cic-modbus-2023/Modbus Dataset/attack/compromised-ied/central-agent/central-agent-network-captures/vethffb308b-3.pcap`
- `data/cic-modbus-2023/Modbus Dataset/attack/compromised-ied/central-agent/central-agent-network-captures/vethffb308b-4.pcap`
- `data/cic-modbus-2023/Modbus Dataset/attack/compromised-ied/ied1a/ied1a-network-captures/veth3614724-0.pcap`
- `data/cic-modbus-2023/Modbus Dataset/attack/compromised-ied/ied1a/ied1a-network-captures/veth3614724-1.pcap`
- `data/cic-modbus-2023/Modbus Dataset/attack/compromised-ied/ied1a/ied1a-network-captures/veth3614724-2.pcap`
- `data/cic-modbus-2023/Modbus Dataset/attack/compromised-ied/ied1a/ied1a-network-captures/veth3614724-3.pcap`
- `data/cic-modbus-2023/Modbus Dataset/attack/compromised-ied/ied1a/ied1a-network-captures/veth3614724-4.pcap`
- `data/cic-modbus-2023/Modbus Dataset/attack/compromised-ied/ied1a/ied1a-network-captures/veth3614724-5.pcap`
- `data/cic-modbus-2023/Modbus Dataset/attack/compromised-ied/ied1b/ied1b-network-captures/vethc76bd3f-0.pcap`
- `data/cic-modbus-2023/Modbus Dataset/attack/compromised-ied/ied1b/ied1b-network-captures/vethc76bd3f-1.pcap`
- `data/cic-modbus-2023/Modbus Dataset/attack/compromised-ied/ied1b/ied1b-network-captures/vethc76bd3f-2.pcap`
- `data/cic-modbus-2023/Modbus Dataset/attack/compromised-ied/ied1b/ied1b-network-captures/vethc76bd3f-3.pcap`
- `data/cic-modbus-2023/Modbus Dataset/attack/compromised-ied/ied1b/ied1b-network-captures/vethc76bd3f-4.pcap`
- `data/cic-modbus-2023/Modbus Dataset/attack/compromised-ied/ied1b/ied1b-network-captures/vethc76bd3f-5.pcap`
- `data/cic-modbus-2023/Modbus Dataset/attack/compromised-ied/ied4c/ied4c-network-captures/vethe685ac9-0.pcap`
- `data/cic-modbus-2023/Modbus Dataset/attack/compromised-ied/ied4c/ied4c-network-captures/vethe685ac9-1.pcap`
- `data/cic-modbus-2023/Modbus Dataset/attack/compromised-ied/ied4c/ied4c-network-captures/vethe685ac9-2.pcap`
- `data/cic-modbus-2023/Modbus Dataset/attack/compromised-ied/ied4c/ied4c-network-captures/vethe685ac9-3.pcap`
- `data/cic-modbus-2023/Modbus Dataset/attack/compromised-ied/ied4c/ied4c-network-captures/vethe685ac9-4.pcap`
- `data/cic-modbus-2023/Modbus Dataset/attack/compromised-ied/ied4c/ied4c-network-captures/vethe685ac9-5.pcap`
- `data/cic-modbus-2023/Modbus Dataset/attack/compromised-ied/trust-scada-hmi/trust-scada-network-captures/veth3efd353-0.pcap`
- `data/cic-modbus-2023/Modbus Dataset/attack/compromised-ied/trust-scada-hmi/trust-scada-network-captures/veth3efd353-1.pcap`
- `data/cic-modbus-2023/Modbus Dataset/attack/compromised-ied/trust-scada-hmi/trust-scada-network-captures/veth3efd353-10.pcap`
- `data/cic-modbus-2023/Modbus Dataset/attack/compromised-ied/trust-scada-hmi/trust-scada-network-captures/veth3efd353-11.pcap`
- `data/cic-modbus-2023/Modbus Dataset/attack/compromised-ied/trust-scada-hmi/trust-scada-network-captures/veth3efd353-12.pcap`
- `data/cic-modbus-2023/Modbus Dataset/attack/compromised-ied/trust-scada-hmi/trust-scada-network-captures/veth3efd353-13.pcap`
- `data/cic-modbus-2023/Modbus Dataset/attack/compromised-ied/trust-scada-hmi/trust-scada-network-captures/veth3efd353-14.pcap`
- `data/cic-modbus-2023/Modbus Dataset/attack/compromised-ied/trust-scada-hmi/trust-scada-network-captures/veth3efd353-15.pcap`
- `data/cic-modbus-2023/Modbus Dataset/attack/compromised-ied/trust-scada-hmi/trust-scada-network-captures/veth3efd353-16.pcap`
- `data/cic-modbus-2023/Modbus Dataset/attack/compromised-ied/trust-scada-hmi/trust-scada-network-captures/veth3efd353-17.pcap`
- `data/cic-modbus-2023/Modbus Dataset/attack/compromised-ied/trust-scada-hmi/trust-scada-network-captures/veth3efd353-18.pcap`
- `data/cic-modbus-2023/Modbus Dataset/attack/compromised-ied/trust-scada-hmi/trust-scada-network-captures/veth3efd353-19.pcap`
- `data/cic-modbus-2023/Modbus Dataset/attack/compromised-ied/trust-scada-hmi/trust-scada-network-captures/veth3efd353-2.pcap`
- `data/cic-modbus-2023/Modbus Dataset/attack/compromised-ied/trust-scada-hmi/trust-scada-network-captures/veth3efd353-3.pcap`
- `data/cic-modbus-2023/Modbus Dataset/attack/compromised-ied/trust-scada-hmi/trust-scada-network-captures/veth3efd353-4.pcap`
- `data/cic-modbus-2023/Modbus Dataset/attack/compromised-ied/trust-scada-hmi/trust-scada-network-captures/veth3efd353-5.pcap`
- `data/cic-modbus-2023/Modbus Dataset/attack/compromised-ied/trust-scada-hmi/trust-scada-network-captures/veth3efd353-6.pcap`
- `data/cic-modbus-2023/Modbus Dataset/attack/compromised-ied/trust-scada-hmi/trust-scada-network-captures/veth3efd353-7.pcap`
- `data/cic-modbus-2023/Modbus Dataset/attack/compromised-ied/trust-scada-hmi/trust-scada-network-captures/veth3efd353-8.pcap`
- `data/cic-modbus-2023/Modbus Dataset/attack/compromised-ied/trust-scada-hmi/trust-scada-network-captures/veth3efd353-9.pcap`

</details>
