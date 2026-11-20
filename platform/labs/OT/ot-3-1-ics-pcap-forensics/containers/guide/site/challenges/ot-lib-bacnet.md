# Protocol deep-dive — BACnet (204 unique captures)

**Protocol library** · **Medium** · 0.9 MB · 5 capture file(s)

> A deduplicated library of 204 BACnet captures from 6 public collections. Learn the protocol's grammar, then hunt its dangerous operations.

> ⚠️ **Safety:** OT capture analysis is passive and safe. Never replay this traffic onto a real industrial network or send these commands to a real controller.

## Scenario

Every public BACnet sample in this range, deduplicated by SHA-256 across automayt-ics-pcap, cisa-icsnpp-test-traces, emreekin-ics-pcaps, inl-malcolm-ot-artifacts, iti-ics-security-tools-pcaps, kargs-bacnet-captures. Use it to learn what the protocol looks like on the wire — roles, operations, normal cadence — and to practice spotting the operations attackers abuse: atomicWriteFile (7), createObject/deleteObject (10/11), writeProperty/writePropertyMultiple (15/16), deviceCommunicationControl (17 — silence a device) and reinitializeDevice (20); Who-Is (unconfirmed 8) is the discovery sweep.

## Objectives

- Identify clients/masters and servers/outstations across the samples.
- Enumerate the BACnet operations present.
- Flag every dangerous operation and its source.
- Map findings to ATT&amp;CK for ICS (T0836 Modify Parameter · T0816 Device Restart/Shutdown · T0846 Remote System Discovery).

## 📥 Get the captures

The commands on this page read the captures from `data/`. Fetch its 5 datasets first, from the repo root:

```bash
python3 scripts/fetch.py automayt-ics-pcap cisa-icsnpp-test-traces emreekin-ics-pcaps iti-ics-security-tools-pcaps kargs-bacnet-captures
```

- **[ICS-pcap collection (automayt / Jason Smith)](../DATASETS.md#automayt-ics-pcap)** (`automayt-ics-pcap`), ~0.42 GB once fetched
  - **Not mirrored** (no licence that allows re-hosting): `fetch.py` downloads it from the original source
  - **Original source:** [github.com/automayt/ICS-pcap](https://github.com/automayt/ICS-pcap)
- **[CISA ICSNPP — Zeek ICS parser test traces](../DATASETS.md#cisa-icsnpp-test-traces)** (`cisa-icsnpp-test-traces`), ~14.8 MB once fetched
  - **Mirror:** this repo's [`data-v1` release](https://github.com/SackOfHacks/ICS-PCAP-Challenges/releases/tag/data-v1), 1 part (3.3 MB compressed): [part000](https://github.com/SackOfHacks/ICS-PCAP-Challenges/releases/download/data-v1/cisa-icsnpp-test-traces.tar.part000) (3.3 MB)
  - **Original source:** [github.com/cisagov/ICSNPP](https://github.com/cisagov/ICSNPP)
- **[ICS-Pcaps (Emre Ekin / ICS Defense) — OT protocol subset](../DATASETS.md#emreekin-ics-pcaps)** (`emreekin-ics-pcaps`), ~0.26 GB once fetched
  - **Not mirrored** (no licence that allows re-hosting): `fetch.py` downloads it from the original source
  - **Original source:** [github.com/EmreEkin/ICS-Pcaps](https://github.com/EmreEkin/ICS-Pcaps)
- **[ITI ICS-Security-Tools — sample ICS protocol captures](../DATASETS.md#iti-ics-security-tools-pcaps)** (`iti-ics-security-tools-pcaps`), ~0.12 GB once fetched
  - **Not mirrored** (no licence that allows re-hosting): `fetch.py` downloads it from the original source
  - **Original source:** [github.com/ITI/ICS-Security-Tools/tree/master/pcaps](https://github.com/ITI/ICS-Security-Tools/tree/master/pcaps)
- **[BACnet capture library (kargs.net)](../DATASETS.md#kargs-bacnet-captures)** (`kargs-bacnet-captures`), ~42.1 MB once fetched
  - **Not mirrored** (no licence that allows re-hosting): `fetch.py` downloads it from the original source
  - **Original source:** [kargs.net/captures](https://kargs.net/captures/)

Without `fetch.py`: download every part of the dataset, run `cat <dataset>.tar.part* | tar -x`, then `gunzip` the files listed in its `MIRROR-GZIPPED.txt`.

## Work it step by step

Two complete walkthroughs — pick your tool. Run every command from the repo root.

### With Pcapper

[Pcapper](https://github.com/SackOfHacks/pcapper) runs the OT protocol analyzers for you.

**1. Triage the capture**

Duration, endpoints and protocol mix before you dive in. Pcapper's overview auto-detects the OT protocols and runs the matching analyzers.

```bash
pcapper 'data/cisa-icsnpp-test-traces/icsnpp-bacnet/bacnet_malformed_service_tags.pcap' --overview
```

**2. Deep-dive with Pcapper (--bacnet)**

Pcapper's protocol analyzer decodes the operations, flags anomalies, and --ot-commands normalizes every control/write across protocols.

```bash
pcapper 'data/cisa-icsnpp-test-traces/icsnpp-bacnet/bacnet_malformed_service_tags.pcap' --bacnet --ot-commands
```

**3. Sweep the whole library**

```bash
pcapper data/automayt-ics-pcap/ --bacnet --ot-commands
```

**4. Map it to ATT&amp;CK for ICS**

Pcapper maps its detections to MITRE ATT&amp;CK (Enterprise + ICS) and draws the attack path.

```bash
pcapper 'data/cisa-icsnpp-test-traces/icsnpp-bacnet/bacnet_malformed_service_tags.pcap' --mitre
```

### With tshark / Wireshark

The by-hand route: display filters, field extraction and statistics.

**1. Triage the capture**

Duration, endpoints and protocol mix before you dive in.

```bash
capinfos 'data/cisa-icsnpp-test-traces/icsnpp-bacnet/bacnet_malformed_service_tags.pcap'
tshark -r 'data/cisa-icsnpp-test-traces/icsnpp-bacnet/bacnet_malformed_service_tags.pcap' -q -z io,phs | head -40
```

**2. Map the BACnet conversation**

Who polls whom? Masters/clients vs. outstations/servers, and the operation mix per pair.

```bash
tshark -r 'data/cisa-icsnpp-test-traces/icsnpp-bacnet/bacnet_malformed_service_tags.pcap' -Y bacapp -T fields -e ip.src -e ip.dst -e bacapp.confirmed_service -e bacapp.unconfirmed_service | sort | uniq -c | sort -rn | head -25
```

**3. Hunt the dangerous operations**

Flag atomicWriteFile (7), createObject/deleteObject (10/11), writeProperty/writePropertyMultiple (15/16), deviceCommunicationControl (17 — silence a device) and reinitializeDevice (20); Who-Is (unconfirmed 8) is the discovery sweep.

```bash
tshark -r 'data/cisa-icsnpp-test-traces/icsnpp-bacnet/bacnet_malformed_service_tags.pcap' -Y 'bacapp.confirmed_service in {7, 10, 11, 15, 16, 17, 20}' -T fields -e frame.time -e ip.src -e ip.dst -e _ws.col.Info | head -40
```

**4. Sweep the whole library**

```bash
for f in 'data/cisa-icsnpp-test-traces/icsnpp-bacnet/bacnet_malformed_service_tags.pcap' 'data/cisa-icsnpp-test-traces/icsnpp-bacnet/bacnet_services.pcap' 'data/cisa-icsnpp-test-traces/icsnpp-bacnet/bacnet_error_reject_abort.pcap' 'data/cisa-icsnpp-test-traces/icsnpp-bacnet/bacnet_example.pcap' 'data/cisa-icsnpp-test-traces/icsnpp-bacnet/bacnet_segmented_data.pcap' 'data/iti-ics-security-tools-pcaps/pcaps/BACnet/bacnet_test.pcap' 'data/automayt-ics-pcap/TRIDIUM/plugfest-tridium-2/plugfest-tridium-2.pcap' 'data/automayt-ics-pcap/TRIDIUM/plugfest-tridium-1/plugfest-tridium-1.pcap' 'data/automayt-ics-pcap/TRIDIUM/tridium-jace2/tridium-jace2.pcap' 'data/automayt-ics-pcap/BACNET/BACnet-BBMD-on-same-subnet/BACnet-BBMD-on-same-subnet.pcap'; do echo "== $f"; tshark -r "$f" -Y 'bacapp.confirmed_service in {7, 10, 11, 15, 16, 17, 20}' 2>/dev/null | head -3; done
```

## Hints

<details><summary>Hint 1</summary>

Wireshark display filter for the protocol: bacnet || bacapp || bvlc

</details>

<details><summary>Hint 2</summary>

Dangerous-operation filter: bacapp.confirmed_service in {7, 10, 11, 15, 16, 17, 20}

</details>

<details><summary>Hint 3</summary>

Many library files are tiny protocol samples — read them packet by packet in Wireshark.

</details>

## Solution

<details><summary>Reveal walkthrough / answer</summary>

A library, not a single puzzle: the deliverable is a per-capture table of roles and operations, with the dangerous ones flagged (atomicWriteFile (7), createObject/deleteObject (10/11), writeProperty/writePropertyMultiple (15/16), deviceCommunicationControl (17 — silence a device) and reinitializeDevice (20); Who-Is (unconfirmed 8) is the discovery sweep). ATT&amp;CK for ICS: T0836 Modify Parameter · T0816 Device Restart/Shutdown · T0846 Remote System Discovery. Sources are credited per collection in each folder's PROVENANCE.md.

**Computed evidence (auto-extracted with tshark — verify it yourself):** BACnet operations — atomicReadFile ×2, readProperty ×2, 18 ×1; dangerous-operation matches: 0 for the BACnet filter (5 BACnet packets present, so the zero is real); top conversations in PrivateTransferError.cap: 192.168.2.1↔192.168.2.122 (1 pkts) (basis: 3 of 80 capture file(s), first 300,000 packets each, smallest files carrying BACnet chosen)

_Captures credited to: ICS-pcap collection (automayt / Jason Smith) — Jason Smith (automayt) · CISA ICSNPP — Zeek ICS parser test traces — CISA and Idaho National Laboratory (ICSNPP project) · ICS-Pcaps (Emre Ekin / ICS Defense) — OT protocol subset — Emre Ekin (ICS Defense, icsdefense.net) · INL Malcolm test artifacts — OT protocol samples — Idaho National Laboratory (Malcolm) · ITI ICS-Security-Tools — sample ICS protocol captures — Information Trust Institute (ITI), University of Illinois Urbana-Champaign · BACnet capture library (kargs.net) — Steve Karg (BACnet Stack author)._

</details>

## Dataset & credit

**ICS-pcap collection (automayt / Jason Smith) — Jason Smith (automayt) · CISA ICSNPP — Zeek ICS parser test traces — CISA and Idaho National Laboratory (ICSNPP project) · ICS-Pcaps (Emre Ekin / ICS Defense) — OT protocol subset — Emre Ekin (ICS Defense, icsdefense.net) · INL Malcolm test artifacts — OT protocol samples — Idaho National Laboratory (Malcolm) · ITI ICS-Security-Tools — sample ICS protocol captures — Information Trust Institute (ITI), University of Illinois Urbana-Champaign · BACnet capture library (kargs.net) — Steve Karg (BACnet Stack author)** — license: varies by collection — see each folder's PROVENANCE.md

- [Dataset source — ICS-pcap collection (automayt / Jason Smith)](https://github.com/automayt/ICS-pcap)
- [Dataset source — CISA ICSNPP — Zeek ICS parser test traces](https://github.com/cisagov/ICSNPP)
- [Dataset source — ICS-Pcaps (Emre Ekin / ICS Defense) — OT protocol subset](https://github.com/EmreEkin/ICS-Pcaps)
- [Dataset source — INL Malcolm test artifacts — OT protocol samples](https://github.com/idaholab/Malcolm-Test-Artifacts)
- [Dataset source — ITI ICS-Security-Tools — sample ICS protocol captures](https://github.com/ITI/ICS-Security-Tools/tree/master/pcaps)
- [Dataset source — BACnet capture library (kargs.net)](https://kargs.net/captures/)
- [MITRE ATT&amp;CK for ICS](https://attack.mitre.org/matrices/ics/)

<details><summary>Capture files (5)</summary>

- `data/cisa-icsnpp-test-traces/icsnpp-bacnet/bacnet_malformed_service_tags.pcap`
- `data/cisa-icsnpp-test-traces/icsnpp-bacnet/bacnet_services.pcap`
- `data/cisa-icsnpp-test-traces/icsnpp-bacnet/bacnet_error_reject_abort.pcap`
- `data/cisa-icsnpp-test-traces/icsnpp-bacnet/bacnet_example.pcap`
- `data/cisa-icsnpp-test-traces/icsnpp-bacnet/bacnet_segmented_data.pcap`

</details>
