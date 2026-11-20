# Medical-waste incinerator — command flooding attack

**Process control &amp; PLC testbeds** · **Hard** · 0.0 MB · 0 capture file(s)

> A command flooding attack was injected into a real plant's S7-1500 traffic. Find it.

> ⚠️ **Safety:** OT capture analysis is passive and safe. Never replay this traffic onto a real industrial network or send these commands to a real controller. Recorded at a real facility: device names, serial numbers and addresses are genuine. Treat them as sensitive and never use them to find or contact the site.

## Scenario

Researchers injected attacks into the real daily captures of a medical-waste incinerator's Siemens S7-1500 SCADA network (each attack capture is a normal day with the attack added). This challenge covers the **command flooding** attack.

Find the injected traffic, identify the attacker host, what it did to the PLC, and when.

## Objectives

- Find the injected traffic and the attacker host.
- Describe the attack technique from the S7comm/TCP evidence.
- Bound it in time.
- Write a detection that would fire on it but not on the normal days.

## 📥 Get the captures

The commands on this page read the captures from `data/`. Fetch the dataset first, from the repo root:

```bash
python3 scripts/fetch.py medical-waste-incinerator-s7-1500
```

- **[Medical-waste incinerator — real Siemens S7-1500 SCADA with injected attacks](../DATASETS.md#medical-waste-incinerator-s7-1500)** (`medical-waste-incinerator-s7-1500`), ~2.63 GB once fetched
  - **Mirror:** this repo's [`data-v1` release](https://github.com/SackOfHacks/ICS-PCAP-Challenges/releases/tag/data-v1), 1 part (0.71 GB compressed): [part000](https://github.com/SackOfHacks/ICS-PCAP-Challenges/releases/download/data-v1/medical-waste-incinerator-s7-1500.tar.part000) (0.71 GB)
  - **Original source:** [data.mendeley.com/datasets/vpcr4wpgfd/4](https://data.mendeley.com/datasets/vpcr4wpgfd/4) · [doi:10.17632/vpcr4wpgfd.4](https://doi.org/10.17632/vpcr4wpgfd.4)

Without `fetch.py`: download every part of the dataset, run `cat <dataset>.tar.part* | tar -x`, then `gunzip` the files listed in its `MIRROR-GZIPPED.txt`.

## Work it step by step

Two complete walkthroughs — pick your tool. Run every command from the repo root.

### With Pcapper

[Pcapper](https://github.com/SackOfHacks/pcapper) runs the OT protocol analyzers for you.

**1. Triage the capture**

Duration, endpoints and protocol mix before you dive in. Pcapper's overview auto-detects the OT protocols and runs the matching analyzers.

```bash
pcapper 'data/medical-waste-incinerator-s7-1500/traffic_with_command_flooding_attack06.pcap' --overview
```

**2. Deep-dive with Pcapper (--s7)**

Pcapper's protocol analyzer decodes the operations, flags anomalies, and --ot-commands normalizes every control/write across protocols.

```bash
pcapper 'data/medical-waste-incinerator-s7-1500/traffic_with_command_flooding_attack06.pcap' --s7 --ot-commands
```

**3. Map it to ATT&amp;CK for ICS**

Pcapper maps its detections to MITRE ATT&amp;CK (Enterprise + ICS) and draws the attack path.

```bash
pcapper 'data/medical-waste-incinerator-s7-1500/traffic_with_command_flooding_attack06.pcap' --mitre
```

### With tshark / Wireshark

The by-hand route: display filters, field extraction and statistics.

**1. Triage the capture**

Duration, endpoints and protocol mix before you dive in.

```bash
capinfos 'data/medical-waste-incinerator-s7-1500/traffic_with_command_flooding_attack06.pcap'
tshark -r 'data/medical-waste-incinerator-s7-1500/traffic_with_command_flooding_attack06.pcap' -q -z io,phs | head -40
```

**2. Map the S7comm-plus (S7-1200/1500) conversation**

Who polls whom? Masters/clients vs. outstations/servers, and the operation mix per pair.

```bash
tshark -r 'data/medical-waste-incinerator-s7-1500/traffic_with_command_flooding_attack06.pcap' -Y 'tcp.port == 102 && tcp.payload[0:2] == 03:00 && ((tcp.payload[4:3] == 02:f0:80 && tcp.payload[7] == 0x72 && tcp.payload[8] <= 3) || (tcp.payload[4] == 2 && tcp.payload[5] == 0x72 && tcp.payload[6] <= 3))' -T fields -e ip.src -e ip.dst -e tcp.len | sort | uniq -c | sort -rn | head -25
```

**3. Look for repeated and unusual messages**

S7comm-plus (0x72) from TIA Portal / HMIs to S7-1200/1500 PLCs; version 3 adds a 32-byte integrity digest and tshark has no built-in dissector, so read it structurally: who talks to the PLC, how often, message sizes, and payloads that repeat (a replay repeats its digest).

```bash
tshark -r 'data/medical-waste-incinerator-s7-1500/traffic_with_command_flooding_attack06.pcap' -Y 'tcp.port == 102 && tcp.payload[0:2] == 03:00 && ((tcp.payload[4:3] == 02:f0:80 && tcp.payload[7] == 0x72 && tcp.payload[8] <= 3) || (tcp.payload[4] == 2 && tcp.payload[5] == 0x72 && tcp.payload[6] <= 3))' -T fields -e ip.src -e tcp.payload | sort | uniq -c | sort -rn | head -15
```

**4. Diff against a normal day**

The attack capture is a normal day plus injected frames — subtract the baseline.

```bash
tshark -r 'data/medical-waste-incinerator-s7-1500/traffic_with_command_flooding_attack06.pcap' -q -z conv,tcp | head -20
```

**5. Message rate on TCP 102**

Floods and replays change the rate; compare with a normal day.

```bash
tshark -r 'data/medical-waste-incinerator-s7-1500/traffic_with_command_flooding_attack06.pcap' -q -z io,stat,10,'tcp.port == 102' | head -60
```

## Hints

<details><summary>Hint 1</summary>

Compare with the normal-day challenge: new hosts, new S7 functions, new rates.

</details>

<details><summary>Hint 2</summary>

The plant speaks S7comm-plus with an integrity digest: judge by source, rate, size and repeated payloads — Pcapper's --s7 decodes it.

</details>

## Solution

<details><summary>Reveal walkthrough / answer</summary>

The capture is a real plant day with an injected command flooding attack (the filename is the dataset's label). Expect: S7 requests at a rate far above the HMI's cycle.

**Computed evidence (auto-extracted with tshark — verify it yourself):** S7comm-plus (S7-1200/1500) packets (matched by the protocol filter used in the steps): 71,920; top conversations in traffic_with_command_flooding_attack06.pcap: 10.0.0.1↔10.0.0.2 (227,855 pkts), 10.0.0.2↔10.0.0.3 (25 pkts) (basis: 1 of 1 capture file(s), first 300,000 packets each)

_Dataset credit: Al-Duwairi, B., Shatnawi, A., Al-Hammouri, A., Ababneh, M. (Jordan University of Science and Technology) (2025) — doi:10.17632/vpcr4wpgfd.4 · License: CC BY 4.0._

</details>

## Dataset & credit

**Al-Duwairi, B., Shatnawi, A., Al-Hammouri, A., Ababneh, M. (Jordan University of Science and Technology) (2025) — doi:10.17632/vpcr4wpgfd.4** — license: CC BY 4.0

- [Dataset source — Medical-waste incinerator — real Siemens S7-1500 SCADA with ](https://data.mendeley.com/datasets/vpcr4wpgfd/4)
- [DOI 10.17632/vpcr4wpgfd.4](https://doi.org/10.17632/vpcr4wpgfd.4)
- [MITRE ATT&amp;CK for ICS](https://attack.mitre.org/matrices/ics/)

<details><summary>Capture files (1)</summary>

- `data/medical-waste-incinerator-s7-1500/traffic_with_command_flooding_attack06.pcap`

</details>
