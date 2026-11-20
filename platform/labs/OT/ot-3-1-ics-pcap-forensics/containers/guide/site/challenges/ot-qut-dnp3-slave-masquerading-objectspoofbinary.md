# QUT DNP3 — Outstation masquerading — spoofed binary inputs

**Process control &amp; PLC testbeds** · **Expert** · 0.0 MB · 0 capture file(s)

> DNP3 attack, one run, three vantage points: a fake outstation feeds the master forged binary-input values.

> ⚠️ **Safety:** OT capture analysis is passive and safe. Never replay this traffic onto a real industrial network or send these commands to a real controller.

## Scenario

QUT built a DNP3 testbed — a master polling an outstation over DNP3/TCP — and used a Scapy-based attack framework to run each attack many times, capturing every run from three vantage points: the **master**, the **outstation** ("slave") and the **attacker**. Every packet of the master and outstation captures is labelled in the matching CSV (frame number, summary, label).

This challenge is one run of **Outstation masquerading — spoofed binary inputs**: a fake outstation feeds the master forged binary-input values. The dataset contains 24 runs of this attack type in total — once you have solved this one, the others are practice.

## Objectives

- Identify master, outstation and attacker (IP **and** MAC).
- Find the attack window and every attack packet.
- Explain what the attack does to the DNP3 session and the process data.
- Write a detection that survives the other runs.

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
pcapper 'data/qut-dnp3-2017/2017QUT_DNP3-master/Masqurading/masquerading/testing/frequent/20161021132643/20161021132643/20160828190718.slave_masquerading_ObjectSpoofBinary/20160828190718.slave_masquerading_ObjectSpoofBinary.master.pcap' --overview
```

**2. Deep-dive with Pcapper (--dnp3)**

Pcapper's protocol analyzer decodes the operations, flags anomalies, and --ot-commands normalizes every control/write across protocols.

```bash
pcapper 'data/qut-dnp3-2017/2017QUT_DNP3-master/Masqurading/masquerading/testing/frequent/20161021132643/20161021132643/20160828190718.slave_masquerading_ObjectSpoofBinary/20160828190718.slave_masquerading_ObjectSpoofBinary.master.pcap' --dnp3 --ot-commands
```

**3. Compare with the attacker's own capture**

The attacker-side capture shows exactly what the attacker sent — the cleanest way to confirm your reading.

```bash
pcapper 'data/qut-dnp3-2017/2017QUT_DNP3-master/Masqurading/masquerading/testing/frequent/20161021132643/20161021132643/20160828190718.slave_masquerading_ObjectSpoofBinary/20160828190718.slave_masquerading_ObjectSpoofBinary.attacker.pcap' --dnp3 --ot-commands
```

**4. Map it to ATT&amp;CK for ICS**

Pcapper maps its detections to MITRE ATT&amp;CK (Enterprise + ICS) and draws the attack path.

```bash
pcapper 'data/qut-dnp3-2017/2017QUT_DNP3-master/Masqurading/masquerading/testing/frequent/20161021132643/20161021132643/20160828190718.slave_masquerading_ObjectSpoofBinary/20160828190718.slave_masquerading_ObjectSpoofBinary.master.pcap' --mitre
```

**5. Check yourself against the per-packet labels**

Column 3 of each CSV is the label for that frame number.

```bash
awk -F, '{print $NF}' 'data/qut-dnp3-2017/2017QUT_DNP3-master/Masqurading/masquerading/testing/frequent/20161021132643/20161021132643/20160828190718.slave_masquerading_ObjectSpoofBinary/20160828190718.slave_masquerading_ObjectSpoofBinary.master.csv' | sort | uniq -c | sort -rn
awk -F, '{print $NF}' 'data/qut-dnp3-2017/2017QUT_DNP3-master/Masqurading/masquerading/testing/frequent/20161021132643/20161021132643/20160828190718.slave_masquerading_ObjectSpoofBinary/20160828190718.slave_masquerading_ObjectSpoofBinary.slave.csv' | sort | uniq -c | sort -rn
```

### With tshark / Wireshark

The by-hand route: display filters, field extraction and statistics.

**1. Triage the master's view**

Duration, endpoints and protocol mix before you dive in.

```bash
capinfos 'data/qut-dnp3-2017/2017QUT_DNP3-master/Masqurading/masquerading/testing/frequent/20161021132643/20161021132643/20160828190718.slave_masquerading_ObjectSpoofBinary/20160828190718.slave_masquerading_ObjectSpoofBinary.master.pcap'
tshark -r 'data/qut-dnp3-2017/2017QUT_DNP3-master/Masqurading/masquerading/testing/frequent/20161021132643/20161021132643/20160828190718.slave_masquerading_ObjectSpoofBinary/20160828190718.slave_masquerading_ObjectSpoofBinary.master.pcap' -q -z io,phs | head -40
```

**2. Map the DNP3 conversation**

Who polls whom? Masters/clients vs. outstations/servers, and the operation mix per pair.

```bash
tshark -r 'data/qut-dnp3-2017/2017QUT_DNP3-master/Masqurading/masquerading/testing/frequent/20161021132643/20161021132643/20160828190718.slave_masquerading_ObjectSpoofBinary/20160828190718.slave_masquerading_ObjectSpoofBinary.master.pcap' -Y dnp3 -T fields -e ip.src -e ip.dst -e dnp3.src -e dnp3.dst -e dnp3.al.func | sort | uniq -c | sort -rn | head -25
```

**3. Hunt the dangerous operations**

Flag WRITE (2), SELECT/OPERATE (3/4), DIRECT_OPERATE (5/6), COLD/WARM_RESTART (13/14), INITIALIZE_DATA/APPL (15/16), START/STOP_APPL (17/18), DISABLE_UNSOLICITED (21), OPEN/DELETE_FILE (25/27), ACTIVATE_CONFIG (31).

```bash
tshark -r 'data/qut-dnp3-2017/2017QUT_DNP3-master/Masqurading/masquerading/testing/frequent/20161021132643/20161021132643/20160828190718.slave_masquerading_ObjectSpoofBinary/20160828190718.slave_masquerading_ObjectSpoofBinary.master.pcap' -Y 'dnp3.al.func in {2, 3, 4, 5, 6, 13, 14, 15, 16, 17, 18, 21, 25, 27, 31}' -T fields -e frame.time -e ip.src -e ip.dst -e _ws.col.Info | head -40
```

**4. Who is really speaking?**

Masquerading shows up as the right IP with the wrong MAC, a second source for one DNP3 address, or responses nobody asked for.

```bash
tshark -r 'data/qut-dnp3-2017/2017QUT_DNP3-master/Masqurading/masquerading/testing/frequent/20161021132643/20161021132643/20160828190718.slave_masquerading_ObjectSpoofBinary/20160828190718.slave_masquerading_ObjectSpoofBinary.master.pcap' -Y dnp3 -T fields -e eth.src -e ip.src -e dnp3.src -e dnp3.dst | sort | uniq -c | sort -rn
```

**5. Compare with the attacker's own capture**

The attacker-side capture shows exactly what the attacker sent — the cleanest way to confirm your reading.

```bash
tshark -r 'data/qut-dnp3-2017/2017QUT_DNP3-master/Masqurading/masquerading/testing/frequent/20161021132643/20161021132643/20160828190718.slave_masquerading_ObjectSpoofBinary/20160828190718.slave_masquerading_ObjectSpoofBinary.attacker.pcap' -Y 'dnp3 || arp' | head -40
```

**6. Check yourself against the per-packet labels**

Column 3 of each CSV is the label for that frame number.

```bash
awk -F, '{print $NF}' 'data/qut-dnp3-2017/2017QUT_DNP3-master/Masqurading/masquerading/testing/frequent/20161021132643/20161021132643/20160828190718.slave_masquerading_ObjectSpoofBinary/20160828190718.slave_masquerading_ObjectSpoofBinary.master.csv' | sort | uniq -c | sort -rn
awk -F, '{print $NF}' 'data/qut-dnp3-2017/2017QUT_DNP3-master/Masqurading/masquerading/testing/frequent/20161021132643/20161021132643/20160828190718.slave_masquerading_ObjectSpoofBinary/20160828190718.slave_masquerading_ObjectSpoofBinary.slave.csv' | sort | uniq -c | sort -rn
```

## Hints

<details><summary>Hint 1</summary>

Read the master's and the outstation's captures side by side — what one sends and the other receives should match.

</details>

<details><summary>Hint 2</summary>

MACs do not lie as easily as IPs on a switched LAN.

</details>

## Solution

<details><summary>Reveal walkthrough / answer</summary>

Labelled run of **slave_masquerading_ObjectSpoofBinary**. The per-packet CSV labels are the exact answer key; the attacker capture shows the attacker's actions. Expected answer: attacker IP/MAC, window, the frames that implement the attack, and how they differ from normal master↔outstation traffic.

**Computed evidence (auto-extracted with tshark — verify it yourself):** DNP3 operations — RESPONSE ×16, UNSOLICITED_RESPONSE ×14, READ ×12, CONFIRM ×10, RECORD_CURRENT_TIME ×4, WRITE ×4, ENABLE_UNSOLICITED ×2; dangerous-operation matches: 4 (top sources: 192.168.10.221 ×4); top conversations in 20160828190718.slave_masquerading_ObjectSpoofBinary.attacker.pcap: 192.168.10.221↔192.168.10.222 (41 pkts), 192.168.10.222↔224.0.0.251 (9 pkts), 192.168.10.1↔192.168.10.222 (4 pkts) (basis: 3 of 3 capture file(s), first 300,000 packets each)

_Dataset credit: Rodofile, N. R., Radke, K., Foo, E. (Queensland University of Technology) (2017) · License: No license stated — credit the authors._

</details>

## Dataset & credit

**Rodofile, N. R., Radke, K., Foo, E. (Queensland University of Technology) (2017)** — license: No license stated — credit the authors

- [Dataset source — QUT 2017 DNP3 — replay, MITM, injection, flooding, masquerad](https://github.com/qut-infosec/2017QUT_DNP3)
- [MITRE ATT&amp;CK for ICS](https://attack.mitre.org/matrices/ics/)

<details><summary>Capture files (3)</summary>

- `data/qut-dnp3-2017/2017QUT_DNP3-master/Masqurading/masquerading/testing/frequent/20161021132643/20161021132643/20160828190718.slave_masquerading_ObjectSpoofBinary/20160828190718.slave_masquerading_ObjectSpoofBinary.attacker.pcap`
- `data/qut-dnp3-2017/2017QUT_DNP3-master/Masqurading/masquerading/testing/frequent/20161021132643/20161021132643/20160828190718.slave_masquerading_ObjectSpoofBinary/20160828190718.slave_masquerading_ObjectSpoofBinary.master.pcap`
- `data/qut-dnp3-2017/2017QUT_DNP3-master/Masqurading/masquerading/testing/frequent/20161021132643/20161021132643/20160828190718.slave_masquerading_ObjectSpoofBinary/20160828190718.slave_masquerading_ObjectSpoofBinary.slave.pcap`

</details>
