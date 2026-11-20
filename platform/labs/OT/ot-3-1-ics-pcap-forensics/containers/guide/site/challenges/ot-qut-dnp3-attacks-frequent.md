# QUT DNP3 — Triage: all attack classes (frequent set)

**Process control &amp; PLC testbeds** · **Hard** · 0.0 MB · 0 capture file(s)

> About 65 attacks hidden in hours of normal DNP3. Triage them all.

> ⚠️ **Safety:** OT capture analysis is passive and safe. Never replay this traffic onto a real industrial network or send these commands to a real controller.

## Scenario

QUT built a DNP3 testbed — a master polling an outstation over DNP3/TCP — and used a Scapy-based attack framework to run each attack many times, capturing every run from three vantage points: the **master**, the **outstation** ("slave") and the **attacker**. Every packet of the master and outstation captures is labelled in the matching CSV (frame number, summary, label).

This is a **mixed** capture: every attack class mixed together, scheduled frequently inside normal polling — 65 scheduled runs. Triage: classify every attack you find.

## Objectives

- Baseline the normal master↔outstation polling.
- Find every attack window.
- Classify each attack (flooding, injection, MITM, masquerading, replay, recon).
- Score yourself against config.txt and the labels.

## 📥 Get the captures

The commands on this page read the captures from `data/`. Fetch the dataset first, from the repo root:

```bash
python3 scripts/fetch.py qut-dnp3-2017
```

- **[QUT 2017 DNP3 — replay, MITM, injection, flooding, masquerading](../DATASETS.md#qut-dnp3-2017)** (`qut-dnp3-2017`), ~3.25 GB once fetched
  - **Not mirrored** (no licence that allows re-hosting): `fetch.py` downloads it from the original source
  - **Original source:** [github.com/qut-infosec/2017QUT_DNP3](https://github.com/qut-infosec/2017QUT_DNP3)

## Work it step by step

Two complete walkthroughs — pick your tool. Run every command from the repo root.

### With Pcapper

[Pcapper](https://github.com/SackOfHacks/pcapper) runs the OT protocol analyzers for you.

**1. Triage the master's view**

Duration, endpoints and protocol mix before you dive in. Pcapper's overview auto-detects the OT protocols and runs the matching analyzers.

```bash
pcapper 'data/qut-dnp3-2017/2017QUT_DNP3-master/Attacks/attacks/testing/frequent/20161021142316/20161021142316/20161021142316.master.pcap' --overview
```

**2. Deep-dive with Pcapper (--dnp3)**

Pcapper's protocol analyzer decodes the operations, flags anomalies, and --ot-commands normalizes every control/write across protocols.

```bash
pcapper 'data/qut-dnp3-2017/2017QUT_DNP3-master/Attacks/attacks/testing/frequent/20161021142316/20161021142316/20161021142316.master.pcap' --dnp3 --ot-commands
```

**3. Map it to ATT&amp;CK for ICS**

Pcapper maps its detections to MITRE ATT&amp;CK (Enterprise + ICS) and draws the attack path.

```bash
pcapper 'data/qut-dnp3-2017/2017QUT_DNP3-master/Attacks/attacks/testing/frequent/20161021142316/20161021142316/20161021142316.master.pcap' --mitre
```

**4. Check yourself against the schedule**

config.txt lists every attack run (timestamp.attack) in this capture; the CSVs label every frame.

```bash
cat 'data/qut-dnp3-2017/2017QUT_DNP3-master/Attacks/attacks/testing/frequent/20161021142316/20161021142316/20161021142316.config.txt'
awk -F, '{print $NF}' 'data/qut-dnp3-2017/2017QUT_DNP3-master/Attacks/attacks/testing/frequent/20161021142316/20161021142316/20161021142316.master.csv' | sort | uniq -c | sort -rn
```

### With tshark / Wireshark

The by-hand route: display filters, field extraction and statistics.

**1. Triage the master's view**

Duration, endpoints and protocol mix before you dive in.

```bash
capinfos 'data/qut-dnp3-2017/2017QUT_DNP3-master/Attacks/attacks/testing/frequent/20161021142316/20161021142316/20161021142316.master.pcap'
tshark -r 'data/qut-dnp3-2017/2017QUT_DNP3-master/Attacks/attacks/testing/frequent/20161021142316/20161021142316/20161021142316.master.pcap' -q -z io,phs | head -40
```

**2. Map the DNP3 conversation**

Who polls whom? Masters/clients vs. outstations/servers, and the operation mix per pair.

```bash
tshark -r 'data/qut-dnp3-2017/2017QUT_DNP3-master/Attacks/attacks/testing/frequent/20161021142316/20161021142316/20161021142316.master.pcap' -Y dnp3 -T fields -e ip.src -e ip.dst -e dnp3.src -e dnp3.dst -e dnp3.al.func | sort | uniq -c | sort -rn | head -25
```

**3. Hunt the dangerous operations**

Flag WRITE (2), SELECT/OPERATE (3/4), DIRECT_OPERATE (5/6), COLD/WARM_RESTART (13/14), INITIALIZE_DATA/APPL (15/16), START/STOP_APPL (17/18), DISABLE_UNSOLICITED (21), OPEN/DELETE_FILE (25/27), ACTIVATE_CONFIG (31).

```bash
tshark -r 'data/qut-dnp3-2017/2017QUT_DNP3-master/Attacks/attacks/testing/frequent/20161021142316/20161021142316/20161021142316.master.pcap' -Y 'dnp3.al.func in {2, 3, 4, 5, 6, 13, 14, 15, 16, 17, 18, 21, 25, 27, 31}' -T fields -e frame.time -e ip.src -e ip.dst -e _ws.col.Info | head -40
```

**4. Find every attack window**

Bucket DNP3 traffic per second and per source/MAC; attacks are bursts or new speakers.

```bash
tshark -r 'data/qut-dnp3-2017/2017QUT_DNP3-master/Attacks/attacks/testing/frequent/20161021142316/20161021142316/20161021142316.master.pcap' -q -z io,stat,10,dnp3,arp | head -80
tshark -r 'data/qut-dnp3-2017/2017QUT_DNP3-master/Attacks/attacks/testing/frequent/20161021142316/20161021142316/20161021142316.master.pcap' -Y dnp3 -T fields -e eth.src -e ip.src -e dnp3.al.func | sort | uniq -c | sort -rn | head -20
```

**5. Check yourself against the schedule**

config.txt lists every attack run (timestamp.attack) in this capture; the CSVs label every frame.

```bash
cat 'data/qut-dnp3-2017/2017QUT_DNP3-master/Attacks/attacks/testing/frequent/20161021142316/20161021142316/20161021142316.config.txt'
awk -F, '{print $NF}' 'data/qut-dnp3-2017/2017QUT_DNP3-master/Attacks/attacks/testing/frequent/20161021142316/20161021142316/20161021142316.master.csv' | sort | uniq -c | sort -rn
```

## Hints

<details><summary>Hint 1</summary>

Attack runs are separated by normal traffic — look for state changes in rate, speakers and function codes.

</details>

<details><summary>Hint 2</summary>

ARP is part of the story for MITM and masquerading.

</details>

## Solution

<details><summary>Reveal walkthrough / answer</summary>

65 scheduled attack runs; config.txt is the schedule and the CSV labels every frame. Score: attacks found / attacks scheduled, and correct classifications.

**Computed evidence (auto-extracted with tshark — verify it yourself):** DNP3 operations — WRITE ×23873, RESPONSE ×14021, READ ×10363, CONFIRM ×4680, UNSOLICITED_RESPONSE ×3874, RECORD_CURRENT_TIME ×35, ENABLE_UNSOLICITED ×33, 7 ×21; dangerous-operation matches: 4464 (top sources: 192.168.10.66 ×4431, 192.168.10.221 ×33); top conversations in 20161021142316.attacker.pcap: 192.168.10.20↔255.255.255.255 (10,087 pkts), 192.168.10.222↔192.168.10.66 (9,974 pkts), 192.168.10.221↔192.168.10.222 (9,034 pkts) (basis: 3 of 3 capture file(s), first 300,000 packets each)

_Dataset credit: Rodofile, N. R., Radke, K., Foo, E. (Queensland University of Technology) (2017) · License: No license stated — credit the authors._

</details>

## Dataset & credit

**Rodofile, N. R., Radke, K., Foo, E. (Queensland University of Technology) (2017)** — license: No license stated — credit the authors

- [Dataset source — QUT 2017 DNP3 — replay, MITM, injection, flooding, masquerad](https://github.com/qut-infosec/2017QUT_DNP3)
- [MITRE ATT&amp;CK for ICS](https://attack.mitre.org/matrices/ics/)

<details><summary>Capture files (3)</summary>

- `data/qut-dnp3-2017/2017QUT_DNP3-master/Attacks/attacks/testing/frequent/20161021142316/20161021142316/20161021142316.attacker.pcap`
- `data/qut-dnp3-2017/2017QUT_DNP3-master/Attacks/attacks/testing/frequent/20161021142316/20161021142316/20161021142316.master.pcap`
- `data/qut-dnp3-2017/2017QUT_DNP3-master/Attacks/attacks/testing/frequent/20161021142316/20161021142316/20161021142316.slave.pcap`

</details>
