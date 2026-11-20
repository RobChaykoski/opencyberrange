# APT Sandworm — attack chain against a wide-area measurement system

**ICS malware &amp; intrusions** · **Expert** · 0.0 MB · 0 capture file(s)

> An emulated Sandworm intrusion walks from a webshell to the phasor data concentrator. Rebuild the kill chain.

> ⚠️ **Safety:** Emulated APT traffic including webshell and lateral-movement payloads. Analyze offline only. This capture carries executable files (Windows PE / Linux ELF) inside the traffic, and some may be malware: work offline, hash anything you extract and never run it.

## Scenario

Researchers emulated a Sandworm-style APT against a wide-area measurement system (WAMS): PMUs stream IEEE C37.118 synchrophasors to an openPDC phasor data concentrator, with PTP time sync and PRP redundancy, alongside the IT services that manage it. The attacker plants a webshell, runs discovery and moves laterally (SMB/RDP/SSH) to the PDC and its database.

Rebuild the kill chain from the packets and map it to ATT&amp;CK.

## Objectives

- Find initial access (the webshell) and the attacker's IPs.
- Trace discovery and lateral movement to the PDC.
- Determine whether synchrophasor data or the PDC database were affected.
- Map each stage to ATT&amp;CK (Enterprise + ICS).

## 📥 Get the captures

The commands on this page read the captures from `data/`. Fetch the dataset first, from the repo root:

```bash
python3 scripts/fetch.py sandworm-apt-wams
```

- **[APT Sandworm emulation — wide-area measurement system (PMU/PDC)](../DATASETS.md#sandworm-apt-wams)** (`sandworm-apt-wams`), ~1.82 GB once fetched
  - **Mirror:** this repo's [`data-v1` release](https://github.com/SackOfHacks/ICS-PCAP-Challenges/releases/tag/data-v1), 1 part (1.65 GB compressed): [part000](https://github.com/SackOfHacks/ICS-PCAP-Challenges/releases/download/data-v1/sandworm-apt-wams.tar.part000) (1.65 GB)
  - **Original source:** [zenodo.org/records/16911636](https://zenodo.org/records/16911636) · [doi:10.5281/zenodo.16911636](https://doi.org/10.5281/zenodo.16911636)

Without `fetch.py`: download every part of the dataset, run `cat <dataset>.tar.part* | tar -x`, then `gunzip` the files listed in its `MIRROR-GZIPPED.txt`.

## Work it step by step

Two complete walkthroughs — pick your tool. Run every command from the repo root.

### With Pcapper

[Pcapper](https://github.com/SackOfHacks/pcapper) runs the OT protocol analyzers for you.

**1. Triage the capture**

Duration, endpoints and protocol mix before you dive in. Pcapper's overview auto-detects the OT protocols and runs the matching analyzers.

```bash
pcapper 'data/sandworm-apt-wams/SandwormAPT.pcap' --overview
```

**2. Deep-dive with Pcapper (--synchrophasor)**

Pcapper's protocol analyzer decodes the operations, flags anomalies, and --ot-commands normalizes every control/write across protocols.

```bash
pcapper 'data/sandworm-apt-wams/SandwormAPT.pcap' --synchrophasor --ot-commands
```

**3. Kill chain with Pcapper**

```bash
pcapper 'data/sandworm-apt-wams/SandwormAPT.pcap' --threats --mitre
pcapper 'data/sandworm-apt-wams/SandwormAPT.pcap' --timeline -ip <attacker_ip>
```

**4. Lateral movement**

```bash
pcapper 'data/sandworm-apt-wams/SandwormAPT.pcap' --smb --rdp --ssh --http
```

### With tshark / Wireshark

The by-hand route: display filters, field extraction and statistics.

**1. Triage the capture**

Duration, endpoints and protocol mix before you dive in.

```bash
capinfos 'data/sandworm-apt-wams/SandwormAPT.pcap'
tshark -r 'data/sandworm-apt-wams/SandwormAPT.pcap' -q -z io,phs | head -40
```

**2. Map the C37.118 synchrophasor conversation**

Who polls whom? Masters/clients vs. outstations/servers, and the operation mix per pair.

```bash
tshark -r 'data/sandworm-apt-wams/SandwormAPT.pcap' -Y synphasor -T fields -e ip.src -e ip.dst -e synphasor.frtype -e synphasor.idcode_stream_source | sort | uniq -c | sort -rn | head -25
```

**3. Hunt the dangerous operations**

Flag command frames (frame type 4) can turn PMU data transmission off or request configuration — normal from the PDC, suspicious from anywhere else.

```bash
tshark -r 'data/sandworm-apt-wams/SandwormAPT.pcap' -Y 'synphasor.frtype == 4' -T fields -e frame.time -e ip.src -e ip.dst -e _ws.col.Info | head -40
```

## Hints

<details><summary>Hint 1</summary>

Start with Pcapper --threats and --timeline on the attacker IP.

</details>

<details><summary>Hint 2</summary>

The flow-label CSV next to the capture is the answer key — use it to check, not to start.

</details>

## Solution

<details><summary>Reveal walkthrough / answer</summary>

The chain: webshell on an exposed web service → discovery → lateral movement over SMB/RDP/SSH → access to the openPDC host and its database, with the synchrophasor streams as the OT asset at stake. The labeled flow CSV shipped with the dataset marks each malicious flow.

**Computed evidence (auto-extracted with tshark — verify it yourself):** C37.118 synchrophasor operations — data ×111, command ×16, config-2 ×3; dangerous-operation matches: 16 (top sources: 192.168.21.230 ×12, 192.168.21.229 ×4); top conversations in SandwormAPT.pcap: 151.101.242.172↔192.168.21.229 (264,962 pkts), 192.168.21.229↔23.41.187.24 (12,610 pkts), 192.168.21.229↔23.41.187.33 (11,588 pkts) (basis: 1 of 1 capture file(s), first 300,000 packets each)

_Dataset credit: Iturbe, Dalamagkas, Radoglou-Grammatikis, Rios (Tecnalia, Univ. of Western Macedonia, PPC) (2025) — doi:10.5281/zenodo.16911636 · License: CC BY 4.0._

</details>

## Dataset & credit

**Iturbe, Dalamagkas, Radoglou-Grammatikis, Rios (Tecnalia, Univ. of Western Macedonia, PPC) (2025) — doi:10.5281/zenodo.16911636** — license: CC BY 4.0

- [Dataset source — APT Sandworm emulation — wide-area measurement system (PMU/P](https://zenodo.org/records/16911636)
- [DOI 10.5281/zenodo.16911636](https://doi.org/10.5281/zenodo.16911636)
- [MITRE ATT&amp;CK for ICS](https://attack.mitre.org/matrices/ics/)

<details><summary>Capture files (1)</summary>

- `data/sandworm-apt-wams/SandwormAPT.pcap`

</details>
