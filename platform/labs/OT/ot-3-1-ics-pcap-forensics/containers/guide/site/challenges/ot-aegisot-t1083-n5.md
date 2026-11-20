# AegisOT — File and Directory Discovery (T1083)

**Process control &amp; PLC testbeds** · **Medium** · 0.0 MB · 0 capture file(s)

> One ATT&amp;CK for ICS technique, executed against a Modbus plant: File and Directory Discovery (T1083). Find it, time it, attribute it.

> ⚠️ **Safety:** OT capture analysis is passive and safe. Never replay this traffic onto a real industrial network or send these commands to a real controller.

## Scenario

AegisOT is a containerised OT testbed — HMIs and PLCs speaking Modbus/TCP over a simulated physical process. Each attack capture executes exactly one ATT&amp;CK technique; this one is **File and Directory Discovery (T1083)**, a network-level attack.

Find the attacker host, the attack window and every packet that implements the technique, and explain the process impact.

## Objectives

- Identify the attacker host and the attack window.
- Show the packets that implement T1083.
- Explain the impact on the process (or what the attacker learned).
- Write a detection that would not fire on the normal sets.

## 📥 Get the captures

The commands on this page read the captures from `data/`. Fetch the dataset first, from the repo root:

```bash
python3 scripts/fetch.py aegisot-ics-attacks
```

- **[AegisOT — Modbus OT testbed with 11 ATT&amp;CK-for-ICS techniques](../DATASETS.md#aegisot-ics-attacks)** (`aegisot-ics-attacks`), ~3.13 GB once fetched
  - **Mirror:** this repo's [`data-v1` release](https://github.com/SackOfHacks/ICS-PCAP-Challenges/releases/tag/data-v1), 1 part (0.56 GB compressed): [part000](https://github.com/SackOfHacks/ICS-PCAP-Challenges/releases/download/data-v1/aegisot-ics-attacks.tar.part000) (0.56 GB)
  - **Original source:** [kaggle.com/datasets/khadijadrira/industrial-cybersecurity…](https://www.kaggle.com/datasets/khadijadrira/industrial-cybersecurity-repository)

Without `fetch.py`: download every part of the dataset, run `cat <dataset>.tar.part* | tar -x`, then `gunzip` the files listed in its `MIRROR-GZIPPED.txt`.

## Work it step by step

Two complete walkthroughs — pick your tool. Run every command from the repo root.

### With Pcapper

[Pcapper](https://github.com/SackOfHacks/pcapper) runs the OT protocol analyzers for you.

**1. Triage the capture**

Duration, endpoints and protocol mix before you dive in. Pcapper's overview auto-detects the OT protocols and runs the matching analyzers.

```bash
pcapper 'data/aegisot-ics-attacks/ICS_Dataset/Attack_Data/Network_Level_Attacks/File_and_Directory_Discovery_T1083/Network_Level/Merged_Packet/output_attack_n5.pcap' --overview
```

**2. Deep-dive with Pcapper (--modbus)**

Pcapper's protocol analyzer decodes the operations, flags anomalies, and --ot-commands normalizes every control/write across protocols.

```bash
pcapper 'data/aegisot-ics-attacks/ICS_Dataset/Attack_Data/Network_Level_Attacks/File_and_Directory_Discovery_T1083/Network_Level/Merged_Packet/output_attack_n5.pcap' --modbus --ot-commands
```

**3. Find the attacker and the technique on the wire**

Network-level techniques show up as new conversations: scans, remote-service sessions and file access that the baseline does not have.

```bash
pcapper 'data/aegisot-ics-attacks/ICS_Dataset/Attack_Data/Network_Level_Attacks/File_and_Directory_Discovery_T1083/Network_Level/Merged_Packet/output_attack_n5.pcap' --scan --services --threats
```

**4. Map it to ATT&amp;CK for ICS**

Pcapper maps its detections to MITRE ATT&amp;CK (Enterprise + ICS) and draws the attack path.

```bash
pcapper 'data/aegisot-ics-attacks/ICS_Dataset/Attack_Data/Network_Level_Attacks/File_and_Directory_Discovery_T1083/Network_Level/Merged_Packet/output_attack_n5.pcap' --mitre
```

**5. Check yourself against the ground truth**

The attack-script log and the labelled flows ship with the dataset — open them only after you have your own answer.

```bash
head -40 'data/aegisot-ics-attacks/ICS_Dataset/Attack_Data/Network_Level_Attacks/File_and_Directory_Discovery_T1083/Network_Level/Flow/Attack_Summary_n5.txt'
head -1 'data/aegisot-ics-attacks/ICS_Dataset/Attack_Data/Network_Level_Attacks/File_and_Directory_Discovery_T1083/Network_Level/Flow/File_and_Directory_Discovery_Labeled.csv' | tr ',' '\n' | tail -6   # label columns
```

### With tshark / Wireshark

The by-hand route: display filters, field extraction and statistics.

**1. Triage the capture**

Duration, endpoints and protocol mix before you dive in.

```bash
capinfos 'data/aegisot-ics-attacks/ICS_Dataset/Attack_Data/Network_Level_Attacks/File_and_Directory_Discovery_T1083/Network_Level/Merged_Packet/output_attack_n5.pcap'
tshark -r 'data/aegisot-ics-attacks/ICS_Dataset/Attack_Data/Network_Level_Attacks/File_and_Directory_Discovery_T1083/Network_Level/Merged_Packet/output_attack_n5.pcap' -q -z io,phs | head -40
```

**2. Map the Modbus/TCP conversation**

Who polls whom? Masters/clients vs. outstations/servers, and the operation mix per pair.

```bash
tshark -r 'data/aegisot-ics-attacks/ICS_Dataset/Attack_Data/Network_Level_Attacks/File_and_Directory_Discovery_T1083/Network_Level/Merged_Packet/output_attack_n5.pcap' -Y mbtcp -T fields -e ip.src -e ip.dst -e mbtcp.unit_id -e modbus.func_code | sort | uniq -c | sort -rn | head -25
```

**3. Hunt the dangerous operations**

Flag writes (FC 5/6/15/16/22/23), diagnostics (FC 8 — restart / force-listen-only), device identification (FC 43/14, recon) and Schneider UMAS (FC 90, engineering).

```bash
tshark -r 'data/aegisot-ics-attacks/ICS_Dataset/Attack_Data/Network_Level_Attacks/File_and_Directory_Discovery_T1083/Network_Level/Merged_Packet/output_attack_n5.pcap' -Y 'modbus.func_code in {5, 6, 15, 16, 22, 23, 8, 43, 90}' -T fields -e frame.time -e ip.src -e ip.dst -e _ws.col.Info | head -40
```

**4. Find the attacker and the technique on the wire**

Network-level techniques show up as new conversations: scans, remote-service sessions and file access that the baseline does not have.

```bash
tshark -r 'data/aegisot-ics-attacks/ICS_Dataset/Attack_Data/Network_Level_Attacks/File_and_Directory_Discovery_T1083/Network_Level/Merged_Packet/output_attack_n5.pcap' -q -z conv,tcp | head -30
```

**5. Check yourself against the ground truth**

The attack-script log and the labelled flows ship with the dataset — open them only after you have your own answer.

```bash
head -40 'data/aegisot-ics-attacks/ICS_Dataset/Attack_Data/Network_Level_Attacks/File_and_Directory_Discovery_T1083/Network_Level/Flow/Attack_Summary_n5.txt'
head -1 'data/aegisot-ics-attacks/ICS_Dataset/Attack_Data/Network_Level_Attacks/File_and_Directory_Discovery_T1083/Network_Level/Flow/File_and_Directory_Discovery_Labeled.csv' | tr ',' '\n' | tail -6   # label columns
```

## Hints

<details><summary>Hint 1</summary>

Diff against the AegisOT normal-operations captures.

</details>

<details><summary>Hint 2</summary>

Read the ATT&amp;CK page for T1083 — the procedure examples tell you what to look for.

</details>

## Solution

<details><summary>Reveal walkthrough / answer</summary>

Labelled as File and Directory Discovery (T1083). The dataset's attack-script log names the start time and actions; the labelled flow CSV marks every malicious flow. Your answer: attacker IP, window, and the packets (with function codes / registers / services) that implement the technique.

**Computed evidence (auto-extracted with tshark — verify it yourself):** Modbus/TCP operations — Write Single Register ×46821, Read Input Registers ×19165, Read Coils ×14368, Read Holding Registers ×9618, Write Single Coil ×136; dangerous-operation matches: 46957 (top sources: 192.168.0.21 ×35185, 192.168.0.22 ×11768, 192.168.0.32 ×4); top conversations in output_attack_n5.pcap: 192.168.0.100↔192.168.0.200 (70,858 pkts), 192.168.0.21↔192.168.0.22 (70,556 pkts), 192.168.0.21↔192.168.0.31 (53,177 pkts) (basis: 1 of 1 capture file(s), first 300,000 packets each)

_Dataset credit: Kaggle user 'khadijadrira' (2026) · License: CC BY-NC-SA 4.0._

</details>

## Dataset & credit

**Kaggle user 'khadijadrira' (2026)** — license: CC BY-NC-SA 4.0

- [Dataset source — AegisOT — Modbus OT testbed with 11 ATT&amp;CK-for-ICS technique](https://www.kaggle.com/datasets/khadijadrira/industrial-cybersecurity-repository)
- [ATT&amp;CK T1083 — File and Directory Discovery](https://attack.mitre.org/techniques/T1083/)
- [MITRE ATT&amp;CK for ICS](https://attack.mitre.org/matrices/ics/)

<details><summary>Capture files (1)</summary>

- `data/aegisot-ics-attacks/ICS_Dataset/Attack_Data/Network_Level_Attacks/File_and_Directory_Discovery_T1083/Network_Level/Merged_Packet/output_attack_n5.pcap`

</details>
