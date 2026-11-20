# IEEE 24-bus SDN lab — R-GOOSE on primary/backup paths

**Power grid &amp; substations** · **Medium** · 0.0 MB · 0 capture file(s)

> R-GOOSE traffic from an ONOS-controlled SDN substation lab on primary and backup paths.

> ⚠️ **Safety:** OT capture analysis is passive and safe. Never replay this traffic onto a real industrial network or send these commands to a real controller.

## Scenario

R-GOOSE traffic from an ONOS-controlled SDN substation lab on primary and backup paths.

Captures from an ONOS-controlled SDN lab of the IEEE 24-bus system carrying routable IEC 61850 GOOSE (R-GOOSE) on primary/backup paths.

## Objectives

- Identify devices and protocol roles.
- Find and characterize the malicious activity.
- Use the dataset's labels/companion files to check yourself.

## 📥 Get the captures

The commands on this page read the captures from `data/`. Fetch the dataset first, from the repo root:

```bash
python3 scripts/fetch.py iec61850-rgoose-sdn-lab
```

- **[IEEE 24-bus SDN substation lab — IEC 61850 R-GOOSE](../DATASETS.md#iec61850-rgoose-sdn-lab)** (`iec61850-rgoose-sdn-lab`), ~0.0 MB once fetched
  - **Not mirrored** (no licence that allows re-hosting): `fetch.py` downloads it from the original source
  - **Original source:** [github.com/jaafaris/ieee24-onos-sdn-lab-v2-](https://github.com/jaafaris/ieee24-onos-sdn-lab-v2-)

## Work it step by step

Two complete walkthroughs — pick your tool. Run every command from the repo root.

### With Pcapper

[Pcapper](https://github.com/SackOfHacks/pcapper) runs the OT protocol analyzers for you.

**1. Triage the capture**

Duration, endpoints and protocol mix before you dive in. Pcapper's overview auto-detects the OT protocols and runs the matching analyzers.

```bash
pcapper 'data/iec61850-rgoose-sdn-lab/output/pcaps/f4_bak_3_to_9.pcap' --overview
```

**2. Deep-dive with Pcapper (--overview)**

Pcapper's protocol analyzer decodes the operations, flags anomalies, and --ot-commands normalizes every control/write across protocols.

```bash
pcapper 'data/iec61850-rgoose-sdn-lab/output/pcaps/f4_bak_3_to_9.pcap' --overview --ot-commands
```

**3. Every control and write, normalized**

--ot-commands lists every OT control/write command across protocols; --threats consolidates Pcapper's detections.

```bash
pcapper 'data/iec61850-rgoose-sdn-lab/output/pcaps/f4_bak_3_to_9.pcap' --ot-commands --threats
```

**4. Map it to ATT&amp;CK for ICS**

Pcapper maps its detections to MITRE ATT&amp;CK (Enterprise + ICS) and draws the attack path.

```bash
pcapper 'data/iec61850-rgoose-sdn-lab/output/pcaps/f4_bak_3_to_9.pcap' --mitre
```

### With tshark / Wireshark

The by-hand route: display filters, field extraction and statistics.

**1. Triage the capture**

Duration, endpoints and protocol mix before you dive in.

```bash
capinfos 'data/iec61850-rgoose-sdn-lab/output/pcaps/f4_bak_3_to_9.pcap'
tshark -r 'data/iec61850-rgoose-sdn-lab/output/pcaps/f4_bak_3_to_9.pcap' -q -z io,phs | head -40
```

**2. Map the IEC 61850 R-GOOSE conversation**

Who polls whom? Masters/clients vs. outstations/servers, and the operation mix per pair.

```bash
tshark -r 'data/iec61850-rgoose-sdn-lab/output/pcaps/f4_bak_3_to_9.pcap' -Y r-goose -T fields -e ip.src -e ip.dst -e udp.dstport -e rgoose.spdu_num -e goose.gocbRef -e goose.stNum -e goose.sqNum | head -40
```

**3. Hunt the dangerous operations**

Flag routable GOOSE carries protection trips and interlocks across IP networks; forged or replayed messages (stNum/sqNum out of order, unexpected source) can trip breakers remotely.

```bash
tshark -r 'data/iec61850-rgoose-sdn-lab/output/pcaps/f4_bak_3_to_9.pcap' -Y 'r-goose' -T fields -e frame.time -e ip.src -e ip.dst -e _ws.col.Info | head -40
```

## Hints

<details><summary>Hint 1</summary>

Look for label files (CSV/JSON/logs) next to the captures — they are the answer key.

</details>

<details><summary>Hint 2</summary>

Compare attack captures against the clean/normal ones.

</details>

## Solution

<details><summary>Reveal walkthrough / answer</summary>

The dataset's bundled labels and companion files are the authoritative answer key; the computed evidence below summarizes what the packets show.

**Computed evidence (auto-extracted with tshark — verify it yourself):** IEC 61850 R-GOOSE packets matching `r-goose`: 128; top conversations in f4_pri_3_to_9.pcap: 10.100.3.30↔232.0.1.3 (42 pkts) (basis: 3 of 4 capture file(s), first 300,000 packets each, smallest files carrying IEC 61850 R-GOOSE chosen)

_Dataset credit: jaafaris (GitHub) · License: No license stated in repo — credit the author._

</details>

## Dataset & credit

**jaafaris (GitHub)** — license: No license stated in repo — credit the author

- [Dataset source — IEEE 24-bus SDN substation lab — IEC 61850 R-GOOSE](https://github.com/jaafaris/ieee24-onos-sdn-lab-v2-)
- [MITRE ATT&amp;CK for ICS](https://attack.mitre.org/matrices/ics/)

<details><summary>Capture files (4)</summary>

- `data/iec61850-rgoose-sdn-lab/output/pcaps/f4_bak_3_to_9.pcap`
- `data/iec61850-rgoose-sdn-lab/output/pcaps/f4_bak_9_to_8.pcap`
- `data/iec61850-rgoose-sdn-lab/output/pcaps/f4_pri_3_to_9.pcap`
- `data/iec61850-rgoose-sdn-lab/output/pcaps/f4_pri_9_to_8.pcap`

</details>
