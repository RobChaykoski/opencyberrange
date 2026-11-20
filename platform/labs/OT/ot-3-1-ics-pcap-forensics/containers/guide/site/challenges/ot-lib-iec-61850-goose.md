# Protocol deep-dive — IEC 61850 GOOSE (16 unique captures)

**Protocol library** · **Medium** · 0.0 MB · 0 capture file(s)

> A deduplicated library of 16 IEC 61850 GOOSE captures from 3 public collections. Learn the protocol's grammar, then hunt its dangerous operations.

> ⚠️ **Safety:** OT capture analysis is passive and safe. Never replay this traffic onto a real industrial network or send these commands to a real controller.

## Scenario

Every public IEC 61850 GOOSE sample in this range, deduplicated by SHA-256 across emreekin-ics-pcaps, ics-pcaps-haolipeng, iti-ics-security-tools-pcaps. Use it to learn what the protocol looks like on the wire — roles, operations, normal cadence — and to practice spotting the operations attackers abuse: GOOSE has no confirmed 'write' — the attack surface is the event stream itself: stNum jumping without a real state change, sqNum resets, bursts far above the retransmission curve, the test/simulation flag, or an unexpected source MAC publishing a known gocbRef.

## Objectives

- Identify clients/masters and servers/outstations across the samples.
- Enumerate the IEC 61850 GOOSE operations present.
- Flag every dangerous operation and its source.
- Map findings to ATT&amp;CK for ICS (T0855 Unauthorized Command Message · T0856 Spoof Reporting Message · T0831 Manipulation of Control · T0814 Denial of Service).

## 📥 Get the captures

The commands on this page read the captures from `data/`. Fetch its 3 datasets first, from the repo root:

```bash
python3 scripts/fetch.py emreekin-ics-pcaps ics-pcaps-haolipeng iti-ics-security-tools-pcaps
```

- **[ICS-Pcaps (Emre Ekin / ICS Defense) — OT protocol subset](../DATASETS.md#emreekin-ics-pcaps)** (`emreekin-ics-pcaps`), ~0.26 GB once fetched
  - **Not mirrored** (no licence that allows re-hosting): `fetch.py` downloads it from the original source
  - **Original source:** [github.com/EmreEkin/ICS-Pcaps](https://github.com/EmreEkin/ICS-Pcaps)
- **[ICS protocol sample captures (IEC-104, MMS and more)](../DATASETS.md#ics-pcaps-haolipeng)** (`ics-pcaps-haolipeng`), ~4.2 MB once fetched
  - **Not mirrored** (no licence that allows re-hosting): `fetch.py` downloads it from the original source
  - **Original source:** [github.com/haolipeng/ics-pcaps](https://github.com/haolipeng/ics-pcaps)
- **[ITI ICS-Security-Tools — sample ICS protocol captures](../DATASETS.md#iti-ics-security-tools-pcaps)** (`iti-ics-security-tools-pcaps`), ~0.12 GB once fetched
  - **Not mirrored** (no licence that allows re-hosting): `fetch.py` downloads it from the original source
  - **Original source:** [github.com/ITI/ICS-Security-Tools/tree/master/pcaps](https://github.com/ITI/ICS-Security-Tools/tree/master/pcaps)

## Work it step by step

Two complete walkthroughs — pick your tool. Run every command from the repo root.

### With Pcapper

[Pcapper](https://github.com/SackOfHacks/pcapper) runs the OT protocol analyzers for you.

**1. Triage the capture**

Duration, endpoints and protocol mix before you dive in. Pcapper's overview auto-detects the OT protocols and runs the matching analyzers.

```bash
pcapper 'data/iti-ics-security-tools-pcaps/pcaps/IEC61850/Sample_File_MMS_and_GOOSE.pcap' --overview
```

**2. Deep-dive with Pcapper (--goose)**

Pcapper's protocol analyzer decodes the operations, flags anomalies, and --ot-commands normalizes every control/write across protocols.

```bash
pcapper 'data/iti-ics-security-tools-pcaps/pcaps/IEC61850/Sample_File_MMS_and_GOOSE.pcap' --goose --ot-commands
```

**3. Sweep the whole library**

```bash
pcapper data/emreekin-ics-pcaps/ --goose --ot-commands
```

**4. Map it to ATT&amp;CK for ICS**

Pcapper maps its detections to MITRE ATT&amp;CK (Enterprise + ICS) and draws the attack path.

```bash
pcapper 'data/iti-ics-security-tools-pcaps/pcaps/IEC61850/Sample_File_MMS_and_GOOSE.pcap' --mitre
```

### With tshark / Wireshark

The by-hand route: display filters, field extraction and statistics.

**1. Triage the capture**

Duration, endpoints and protocol mix before you dive in.

```bash
capinfos 'data/iti-ics-security-tools-pcaps/pcaps/IEC61850/Sample_File_MMS_and_GOOSE.pcap'
tshark -r 'data/iti-ics-security-tools-pcaps/pcaps/IEC61850/Sample_File_MMS_and_GOOSE.pcap' -q -z io,phs | head -40
```

**2. Map the IEC 61850 GOOSE conversation**

Who polls whom? Masters/clients vs. outstations/servers, and the operation mix per pair.

```bash
tshark -r 'data/iti-ics-security-tools-pcaps/pcaps/IEC61850/Sample_File_MMS_and_GOOSE.pcap' -Y goose -T fields -e eth.src -e goose.gocbRef -e goose.stNum -e goose.sqNum -e goose.timeAllowedtoLive | head -40
```

**3. Hunt the dangerous operations**

Flag GOOSE has no confirmed 'write' — the attack surface is the event stream itself: stNum jumping without a real state change, sqNum resets, bursts far above the retransmission curve, the test/simulation flag, or an unexpected source MAC publishing a known gocbRef.

```bash
tshark -r 'data/iti-ics-security-tools-pcaps/pcaps/IEC61850/Sample_File_MMS_and_GOOSE.pcap' -Y 'goose' -T fields -e frame.time -e ip.src -e ip.dst -e _ws.col.Info | head -40
```

**4. Sweep the whole library**

```bash
for f in 'data/iti-ics-security-tools-pcaps/pcaps/IEC61850/Sample_File_MMS_and_GOOSE.pcap' 'data/iti-ics-security-tools-pcaps/pcaps/IEC61850/GOOSE/GOOSE.pcap' 'data/iti-ics-security-tools-pcaps/pcaps/IEC61850/GOOSE/GOOSE_DEMO.pcap' 'data/iti-ics-security-tools-pcaps/pcaps/IEC61850/GOOSE/Sample_File_GOOSE.pcap' 'data/emreekin-ics-pcaps/IEC61850/gooseind1_7.pcap' 'data/emreekin-ics-pcaps/IEC61850/iedscout.pcap' 'data/emreekin-ics-pcaps/IEC61850/mmsy1.pcap' 'data/emreekin-ics-pcaps/IEC61850/pres.pcap' 'data/emreekin-ics-pcaps/IEC61850/mmsy.pcap' 'data/emreekin-ics-pcaps/IEC61850/pres1.pcap'; do echo "== $f"; tshark -r "$f" -Y 'goose' 2>/dev/null | head -3; done
```

## Hints

<details><summary>Hint 1</summary>

Wireshark display filter for the protocol: goose

</details>

<details><summary>Hint 2</summary>

Dangerous-operation filter: goose

</details>

<details><summary>Hint 3</summary>

Many library files are tiny protocol samples — read them packet by packet in Wireshark.

</details>

## Solution

<details><summary>Reveal walkthrough / answer</summary>

A library, not a single puzzle: the deliverable is a per-capture table of roles and operations, with the dangerous ones flagged (GOOSE has no confirmed 'write' — the attack surface is the event stream itself: stNum jumping without a real state change, sqNum resets, bursts far above the retransmission curve, the test/simulation flag, or an unexpected source MAC publishing a known gocbRef). ATT&amp;CK for ICS: T0855 Unauthorized Command Message · T0856 Spoof Reporting Message · T0831 Manipulation of Control · T0814 Denial of Service. Sources are credited per collection in each folder's PROVENANCE.md.

**Computed evidence (auto-extracted with tshark — verify it yourself):** IEC 61850 GOOSE packets matching `goose`: 3; GOOSE streams — GEDeviceF650/LLN0$GO$gcb01 from 00:a0:f4:08:2f:77: 2 frames, 1 distinct stNum, 0 sqNum resets; 111 from 00:17:a4:dd:98:1e: 1 frames, 1 distinct stNum, 0 sqNum resets (basis: 3 of 16 capture file(s), first 300,000 packets each, smallest files carrying IEC 61850 GOOSE chosen)

_Captures credited to: ICS-Pcaps (Emre Ekin / ICS Defense) — OT protocol subset — Emre Ekin (ICS Defense, icsdefense.net) · ICS protocol sample captures (IEC-104, MMS and more) — haolipeng (GitHub) · ITI ICS-Security-Tools — sample ICS protocol captures — Information Trust Institute (ITI), University of Illinois Urbana-Champaign._

</details>

## Dataset & credit

**ICS-Pcaps (Emre Ekin / ICS Defense) — OT protocol subset — Emre Ekin (ICS Defense, icsdefense.net) · ICS protocol sample captures (IEC-104, MMS and more) — haolipeng (GitHub) · ITI ICS-Security-Tools — sample ICS protocol captures — Information Trust Institute (ITI), University of Illinois Urbana-Champaign** — license: varies by collection — see each folder's PROVENANCE.md

- [Dataset source — ICS-Pcaps (Emre Ekin / ICS Defense) — OT protocol subset](https://github.com/EmreEkin/ICS-Pcaps)
- [Dataset source — ICS protocol sample captures (IEC-104, MMS and more)](https://github.com/haolipeng/ics-pcaps)
- [Dataset source — ITI ICS-Security-Tools — sample ICS protocol captures](https://github.com/ITI/ICS-Security-Tools/tree/master/pcaps)
- [MITRE ATT&amp;CK for ICS](https://attack.mitre.org/matrices/ics/)

<details><summary>Capture files (16)</summary>

- `data/iti-ics-security-tools-pcaps/pcaps/IEC61850/Sample_File_MMS_and_GOOSE.pcap`
- `data/iti-ics-security-tools-pcaps/pcaps/IEC61850/GOOSE/GOOSE.pcap`
- `data/iti-ics-security-tools-pcaps/pcaps/IEC61850/GOOSE/GOOSE_DEMO.pcap`
- `data/iti-ics-security-tools-pcaps/pcaps/IEC61850/GOOSE/Sample_File_GOOSE.pcap`
- `data/emreekin-ics-pcaps/IEC61850/gooseind1_7.pcap`
- `data/emreekin-ics-pcaps/IEC61850/iedscout.pcap`
- `data/emreekin-ics-pcaps/IEC61850/mmsy1.pcap`
- `data/emreekin-ics-pcaps/IEC61850/pres.pcap`
- `data/emreekin-ics-pcaps/IEC61850/mmsy.pcap`
- `data/emreekin-ics-pcaps/IEC61850/pres1.pcap`
- `data/ics-pcaps-haolipeng/iec61850-goose/GOOSE_t_binary_time.pcap`
- `data/ics-pcaps-haolipeng/iec61850-goose/GOOSE_t_unsupported_time.pcap`
- `data/ics-pcaps-haolipeng/iec61850-goose/GOOSE_array_structure.pcap`
- `data/ics-pcaps-haolipeng/iec61850-goose/GOOSE_array_depth_truncated_10nest.pcap`
- `data/ics-pcaps-haolipeng/iec61850-goose/GOOSE_all_data_primitives_fallbacks.pcap`
- `data/ics-pcaps-haolipeng/iec61850-goose/GOOSE_array_truncated.pcap`

</details>
