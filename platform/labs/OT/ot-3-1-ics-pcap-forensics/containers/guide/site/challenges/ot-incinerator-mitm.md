# Medical-waste incinerator — man-in-the-middle attack

**Process control &amp; PLC testbeds** · **Hard** · 0.0 MB · 0 capture file(s)

> A man-in-the-middle attack was injected into a real plant's S7-1500 traffic. Find it.

> ⚠️ **Safety:** OT capture analysis is passive and safe. Never replay this traffic onto a real industrial network or send these commands to a real controller. Recorded at a real facility: device names, serial numbers and addresses are genuine. Treat them as sensitive and never use them to find or contact the site.

## Scenario

Researchers injected attacks into the real daily captures of a medical-waste incinerator's Siemens S7-1500 SCADA network (each attack capture is a normal day with the attack added). This challenge covers the **man-in-the-middle** attack.

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
pcapper 'data/medical-waste-incinerator-s7-1500/traffic_with_mitm_attack03.pcap' --overview
```

**2. Deep-dive with Pcapper (--s7)**

Pcapper's protocol analyzer decodes the operations, flags anomalies, and --ot-commands normalizes every control/write across protocols.

```bash
pcapper 'data/medical-waste-incinerator-s7-1500/traffic_with_mitm_attack03.pcap' --s7 --ot-commands
```

**3. Map it to ATT&amp;CK for ICS**

Pcapper maps its detections to MITRE ATT&amp;CK (Enterprise + ICS) and draws the attack path.

```bash
pcapper 'data/medical-waste-incinerator-s7-1500/traffic_with_mitm_attack03.pcap' --mitre
```

### With tshark / Wireshark

The by-hand route: display filters, field extraction and statistics.

**1. Triage the capture**

Duration, endpoints and protocol mix before you dive in.

```bash
capinfos 'data/medical-waste-incinerator-s7-1500/traffic_with_mitm_attack03.pcap'
tshark -r 'data/medical-waste-incinerator-s7-1500/traffic_with_mitm_attack03.pcap' -q -z io,phs | head -40
```

**2. Map the S7comm conversation**

Who polls whom? Masters/clients vs. outstations/servers, and the operation mix per pair.

```bash
tshark -r 'data/medical-waste-incinerator-s7-1500/traffic_with_mitm_attack03.pcap' -Y s7comm -T fields -e ip.src -e ip.dst -e s7comm.header.rosctr -e s7comm.param.func -e s7comm.param.userdata.funcgroup -e s7comm.param.userdata.subfunc | sort | uniq -c | sort -rn | head -25
```

**3. Hunt the dangerous operations**

Flag write variable (0x05), program download (0x1A–0x1C), program upload (0x1D–0x1F — logic theft), PI-service (0x28 — start/restart/compress), PLC STOP (0x29) and security/password userdata (function group 5); SZL reads (function group 4) are device recon.

```bash
tshark -r 'data/medical-waste-incinerator-s7-1500/traffic_with_mitm_attack03.pcap' -Y 's7comm.param.func in {0x05, 0x1a, 0x1b, 0x1c, 0x1d, 0x1e, 0x1f, 0x28, 0x29} || s7comm.param.userdata.funcgroup == 5' -T fields -e frame.time -e ip.src -e ip.dst -e _ws.col.Info | head -40
```

**4. Diff against a normal day**

The attack capture is a normal day plus injected frames — subtract the baseline.

```bash
tshark -r 'data/medical-waste-incinerator-s7-1500/traffic_with_mitm_attack03.pcap' -q -z conv,tcp | head -20
```

## Hints

<details><summary>Hint 1</summary>

Compare with the normal-day challenge: new hosts, new S7 functions, new rates.

</details>

<details><summary>Hint 2</summary>

The injected traffic is classic S7comm: PLC STOP is function 0x29, writes are 0x05, downloads 0x1A–0x1C.

</details>

## Solution

<details><summary>Reveal walkthrough / answer</summary>

The capture is a real plant day with an injected man-in-the-middle attack (the filename is the dataset's label). Expect: ARP-spoofed interception between HMI and PLC with altered S7 values.

**Computed evidence (auto-extracted with tshark — verify it yourself):** S7comm operations — Read Var ×1; dangerous-operation matches: 0 for the S7comm filter (1 S7comm packets present, so the zero is real); top conversations in traffic_with_mitm_attack03.pcap: 192.168.3.10↔192.168.3.20 (226,095 pkts), 192.168.3.20↔192.168.3.255 (32 pkts) (basis: 1 of 1 capture file(s), first 300,000 packets each)

_Dataset credit: Al-Duwairi, B., Shatnawi, A., Al-Hammouri, A., Ababneh, M. (Jordan University of Science and Technology) (2025) — doi:10.17632/vpcr4wpgfd.4 · License: CC BY 4.0._

</details>

## Dataset & credit

**Al-Duwairi, B., Shatnawi, A., Al-Hammouri, A., Ababneh, M. (Jordan University of Science and Technology) (2025) — doi:10.17632/vpcr4wpgfd.4** — license: CC BY 4.0

- [Dataset source — Medical-waste incinerator — real Siemens S7-1500 SCADA with ](https://data.mendeley.com/datasets/vpcr4wpgfd/4)
- [DOI 10.17632/vpcr4wpgfd.4](https://doi.org/10.17632/vpcr4wpgfd.4)
- [MITRE ATT&amp;CK for ICS](https://attack.mitre.org/matrices/ics/)

<details><summary>Capture files (1)</summary>

- `data/medical-waste-incinerator-s7-1500/traffic_with_mitm_attack03.pcap`

</details>
