# R-GOOSE and tunnelled GOOSE

**Power grid &amp; substations** · **Medium** · 0.0 MB · 0 capture file(s)

> Routable GOOSE, GOOSE over VXLAN and GOOSE in Simplemux — substation events once they leave the bay.

> ⚠️ **Safety:** OT capture analysis is passive and safe. Never replay this traffic onto a real industrial network or send these commands to a real controller.

## Scenario

Routable GOOSE, GOOSE over VXLAN and GOOSE in Simplemux — substation events once they leave the bay.

Routable GOOSE (R-GOOSE), GOOSE over VXLAN and GOOSE multiplexed with Simplemux — how substation L2 events look once they leave the bay.

## Objectives

- Identify devices and protocol roles.
- Find and characterize the malicious activity.
- Use the dataset's labels/companion files to check yourself.

## 📥 Get the captures

The commands on this page read the captures from `data/`. Fetch the dataset first, from the repo root:

```bash
python3 scripts/fetch.py r-goose-tunnelled-goose
```

- **[R-GOOSE and tunnelled GOOSE traffic](../DATASETS.md#r-goose-tunnelled-goose)** (`r-goose-tunnelled-goose`), ~1.9 MB once fetched
  - **Mirror:** this repo's [`data-v1` release](https://github.com/SackOfHacks/ICS-PCAP-Challenges/releases/tag/data-v1), 1 part (0.6 MB compressed): [part000](https://github.com/SackOfHacks/ICS-PCAP-Challenges/releases/download/data-v1/r-goose-tunnelled-goose.tar.part000) (0.6 MB)
  - **Original source:** [zenodo.org/records/22047499](https://zenodo.org/records/22047499) · [doi:10.5281/zenodo.22047499](https://doi.org/10.5281/zenodo.22047499)

Without `fetch.py`: download every part of the dataset, run `cat <dataset>.tar.part* | tar -x`, then `gunzip` the files listed in its `MIRROR-GZIPPED.txt`.

## Work it step by step

Two complete walkthroughs — pick your tool. Run every command from the repo root.

### With Pcapper

[Pcapper](https://github.com/SackOfHacks/pcapper) runs the OT protocol analyzers for you.

**1. Triage the capture**

Duration, endpoints and protocol mix before you dive in. Pcapper's overview auto-detects the OT protocols and runs the matching analyzers.

```bash
pcapper 'data/r-goose-tunnelled-goose/Traffic of R-GOOSE and tunnelled GOOSE/GOOSE inside Simplemux Blast/rasp2_eth1_simplemuxBlast_5ms-55558.pcap' --overview
```

**2. Deep-dive with Pcapper (--goose)**

Pcapper's protocol analyzer decodes the operations, flags anomalies, and --ot-commands normalizes every control/write across protocols.

```bash
pcapper 'data/r-goose-tunnelled-goose/Traffic of R-GOOSE and tunnelled GOOSE/GOOSE inside Simplemux Blast/rasp2_eth1_simplemuxBlast_5ms-55558.pcap' --goose --ot-commands
```

**3. Map it to ATT&amp;CK for ICS**

Pcapper maps its detections to MITRE ATT&amp;CK (Enterprise + ICS) and draws the attack path.

```bash
pcapper 'data/r-goose-tunnelled-goose/Traffic of R-GOOSE and tunnelled GOOSE/GOOSE inside Simplemux Blast/rasp2_eth1_simplemuxBlast_5ms-55558.pcap' --mitre
```

### With tshark / Wireshark

The by-hand route: display filters, field extraction and statistics.

**1. Triage the capture**

Duration, endpoints and protocol mix before you dive in.

```bash
capinfos 'data/r-goose-tunnelled-goose/Traffic of R-GOOSE and tunnelled GOOSE/GOOSE inside Simplemux Blast/rasp2_eth1_simplemuxBlast_5ms-55558.pcap'
tshark -r 'data/r-goose-tunnelled-goose/Traffic of R-GOOSE and tunnelled GOOSE/GOOSE inside Simplemux Blast/rasp2_eth1_simplemuxBlast_5ms-55558.pcap' -q -z io,phs | head -40
```

**2. Map the IEC 61850 GOOSE conversation**

Who polls whom? Masters/clients vs. outstations/servers, and the operation mix per pair.

```bash
tshark -r 'data/r-goose-tunnelled-goose/Traffic of R-GOOSE and tunnelled GOOSE/GOOSE inside Simplemux Blast/rasp2_eth1_simplemuxBlast_5ms-55558.pcap' -Y goose -T fields -e eth.src -e goose.gocbRef -e goose.stNum -e goose.sqNum -e goose.timeAllowedtoLive | head -40
```

**3. Hunt the dangerous operations**

Flag GOOSE has no confirmed 'write' — the attack surface is the event stream itself: stNum jumping without a real state change, sqNum resets, bursts far above the retransmission curve, the test/simulation flag, or an unexpected source MAC publishing a known gocbRef.

```bash
tshark -r 'data/r-goose-tunnelled-goose/Traffic of R-GOOSE and tunnelled GOOSE/GOOSE inside Simplemux Blast/rasp2_eth1_simplemuxBlast_5ms-55558.pcap' -Y 'goose' -T fields -e frame.time -e ip.src -e ip.dst -e _ws.col.Info | head -40
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

**Computed evidence (auto-extracted with tshark — verify it yourself):** IEC 61850 GOOSE packets matching `goose`: 8; GOOSE streams — GEDeviceF650/LLN0$GO$gcb01 from 80:6d:97:07:2c:3a,00:a0:f4:08:2f:77: 8 frames, 1 distinct stNum, 1 sqNum resets; top conversations in GOOSE_over_VXLAN.pcap: 192.168.3.171↔192.168.3.172 (8 pkts) (basis: 1 of 10 capture file(s), first 300,000 packets each)

_Dataset credit: Saldana, Jose (2026) — doi:10.5281/zenodo.22047499 · License: CC BY 4.0._

</details>

## Dataset & credit

**Saldana, Jose (2026) — doi:10.5281/zenodo.22047499** — license: CC BY 4.0

- [Dataset source — R-GOOSE and tunnelled GOOSE traffic](https://zenodo.org/records/22047499)
- [DOI 10.5281/zenodo.22047499](https://doi.org/10.5281/zenodo.22047499)
- [MITRE ATT&amp;CK for ICS](https://attack.mitre.org/matrices/ics/)

<details><summary>Capture files (10)</summary>

- `data/r-goose-tunnelled-goose/Traffic of R-GOOSE and tunnelled GOOSE/GOOSE inside Simplemux Blast/rasp2_eth1_simplemuxBlast_5ms-55558.pcap`
- `data/r-goose-tunnelled-goose/Traffic of R-GOOSE and tunnelled GOOSE/GOOSE inside VXLAN/GOOSE_over_VXLAN.pcap`
- `data/r-goose-tunnelled-goose/Traffic of R-GOOSE and tunnelled GOOSE/R-GOOSE converted to unicast with a gateway/R-GOOSE.pcap`
- `data/r-goose-tunnelled-goose/Traffic of R-GOOSE and tunnelled GOOSE/R-GOOSE converted to unicast with a gateway/ns_sub1.pcap`
- `data/r-goose-tunnelled-goose/Traffic of R-GOOSE and tunnelled GOOSE/R-GOOSE converted to unicast with a gateway/ns_sub2.pcap`
- `data/r-goose-tunnelled-goose/Traffic of R-GOOSE and tunnelled GOOSE/R-GOOSE inside GRE/R-GOOSE.pcap`
- `data/r-goose-tunnelled-goose/Traffic of R-GOOSE and tunnelled GOOSE/R-GOOSE inside GRE/results_rgoose_gre_20260616_094957/01_ns1_ingress.pcap`
- `data/r-goose-tunnelled-goose/Traffic of R-GOOSE and tunnelled GOOSE/R-GOOSE inside GRE/results_rgoose_gre_20260616_094957/02_ns1_underlay_gre.pcap`
- `data/r-goose-tunnelled-goose/Traffic of R-GOOSE and tunnelled GOOSE/R-GOOSE inside GRE/results_rgoose_gre_20260616_094957/03_ns2_egress.pcap`
- `data/r-goose-tunnelled-goose/Traffic of R-GOOSE and tunnelled GOOSE/R-GOOSE native/R-GOOSE.pcap`

</details>
