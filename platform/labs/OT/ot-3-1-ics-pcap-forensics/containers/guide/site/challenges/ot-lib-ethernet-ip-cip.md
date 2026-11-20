# Protocol deep-dive — EtherNet/IP &amp; CIP (84 unique captures)

**Protocol library** · **Medium** · 0.2 MB · 6 capture file(s)

> A deduplicated library of 84 EtherNet/IP &amp; CIP captures from 8 public collections. Learn the protocol's grammar, then hunt its dangerous operations.

> ⚠️ **Safety:** OT capture analysis is passive and safe. Never replay this traffic onto a real industrial network or send these commands to a real controller.

## Scenario

Every public EtherNet/IP &amp; CIP sample in this range, deduplicated by SHA-256 across automayt-ics-pcap, cisa-icsnpp-test-traces, emreekin-ics-pcaps, inl-malcolm-ot-artifacts, iti-ics-security-tools-pcaps, kargs-bacnet-captures, s7comm-scenarios-jenilv07, suricata-verify-ics-tests. Use it to learn what the protocol looks like on the wire — roles, operations, normal cadence — and to practice spotting the operations attackers abuse: CIP Reset (0x05), Start (0x06), Stop (0x07), Set Attribute Single (0x10), Execute PCCC (0x4B), Write Tag (0x4D), Write Tag Fragmented (0x53); ENIP ListIdentity (0x63) is the classic discovery broadcast.

## Objectives

- Identify clients/masters and servers/outstations across the samples.
- Enumerate the EtherNet/IP &amp; CIP operations present.
- Flag every dangerous operation and its source.
- Map findings to ATT&amp;CK for ICS (T0858 Change Operating Mode · T0836 Modify Parameter · T0816 Device Restart/Shutdown · T0846 Remote System Discovery).

## 📥 Get the captures

The commands on this page read the captures from `data/`. Fetch its 7 datasets first, from the repo root:

```bash
python3 scripts/fetch.py automayt-ics-pcap cisa-icsnpp-test-traces emreekin-ics-pcaps iti-ics-security-tools-pcaps kargs-bacnet-captures s7comm-scenarios-jenilv07 suricata-verify-ics-tests
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
- **[ICS sample collection (jenilv-07) — S7comm scenarios, ControlLogix attack attempts, BACnet, Modbus, Omron, Tridium](../DATASETS.md#s7comm-scenarios-jenilv07)** (`s7comm-scenarios-jenilv07`), ~34.1 MB once fetched
  - **Not mirrored** (no licence that allows re-hosting): `fetch.py` downloads it from the original source
  - **Original source:** [github.com/jenilv-07/ICS-pcap-files](https://github.com/jenilv-07/ICS-pcap-files)
- **[Suricata-verify — ICS protocol test captures](../DATASETS.md#suricata-verify-ics-tests)** (`suricata-verify-ics-tests`), ~0.1 MB once fetched
  - **Mirror:** this repo's [`data-v1` release](https://github.com/SackOfHacks/ICS-PCAP-Challenges/releases/tag/data-v1), 1 part (0.0 MB compressed): [part000](https://github.com/SackOfHacks/ICS-PCAP-Challenges/releases/download/data-v1/suricata-verify-ics-tests.tar.part000) (0.0 MB)
  - **Original source:** [github.com/OISF/suricata-verify](https://github.com/OISF/suricata-verify)

Without `fetch.py`: download every part of the dataset, run `cat <dataset>.tar.part* | tar -x`, then `gunzip` the files listed in its `MIRROR-GZIPPED.txt`.

## Work it step by step

Two complete walkthroughs — pick your tool. Run every command from the repo root.

### With Pcapper

[Pcapper](https://github.com/SackOfHacks/pcapper) runs the OT protocol analyzers for you.

**1. Triage the capture**

Duration, endpoints and protocol mix before you dive in. Pcapper's overview auto-detects the OT protocols and runs the matching analyzers.

```bash
pcapper 'data/cisa-icsnpp-test-traces/icsnpp-enip/set_attribute_single_service_cip.pcapng' --overview
```

**2. Deep-dive with Pcapper (--enip --cip --pccc)**

Pcapper's protocol analyzer decodes the operations, flags anomalies, and --ot-commands normalizes every control/write across protocols.

```bash
pcapper 'data/cisa-icsnpp-test-traces/icsnpp-enip/set_attribute_single_service_cip.pcapng' --enip --cip --pccc --ot-commands
```

**3. Sweep the whole library**

```bash
pcapper data/automayt-ics-pcap/ --enip --cip --pccc --ot-commands
```

**4. Map it to ATT&amp;CK for ICS**

Pcapper maps its detections to MITRE ATT&amp;CK (Enterprise + ICS) and draws the attack path.

```bash
pcapper 'data/cisa-icsnpp-test-traces/icsnpp-enip/set_attribute_single_service_cip.pcapng' --mitre
```

### With tshark / Wireshark

The by-hand route: display filters, field extraction and statistics.

**1. Triage the capture**

Duration, endpoints and protocol mix before you dive in.

```bash
capinfos 'data/cisa-icsnpp-test-traces/icsnpp-enip/set_attribute_single_service_cip.pcapng'
tshark -r 'data/cisa-icsnpp-test-traces/icsnpp-enip/set_attribute_single_service_cip.pcapng' -q -z io,phs | head -40
```

**2. Map the EtherNet/IP &amp; CIP conversation**

Who polls whom? Masters/clients vs. outstations/servers, and the operation mix per pair.

```bash
tshark -r 'data/cisa-icsnpp-test-traces/icsnpp-enip/set_attribute_single_service_cip.pcapng' -Y enip -T fields -e ip.src -e ip.dst -e enip.command -e cip.sc | sort | uniq -c | sort -rn | head -25
```

**3. Hunt the dangerous operations**

Flag CIP Reset (0x05), Start (0x06), Stop (0x07), Set Attribute Single (0x10), Execute PCCC (0x4B), Write Tag (0x4D), Write Tag Fragmented (0x53); ENIP ListIdentity (0x63) is the classic discovery broadcast.

```bash
tshark -r 'data/cisa-icsnpp-test-traces/icsnpp-enip/set_attribute_single_service_cip.pcapng' -Y 'cip.sc in {0x05, 0x06, 0x07, 0x10, 0x4b, 0x4d, 0x53} || enip.command == 0x63' -T fields -e frame.time -e ip.src -e ip.dst -e _ws.col.Info | head -40
```

**4. Sweep the whole library**

```bash
for f in 'data/cisa-icsnpp-test-traces/icsnpp-enip/set_attribute_single_service_cip.pcapng' 'data/cisa-icsnpp-test-traces/icsnpp-enip/set_attribute_single_service_cip.pcapng' 'data/cisa-icsnpp-test-traces/icsnpp-enip/multiple_service_packet_cip.pcapng' 'data/cisa-icsnpp-test-traces/icsnpp-enip/multiple_service_packet_cip.pcapng' 'data/cisa-icsnpp-test-traces/icsnpp-enip/enip_cip_example.pcap' 'data/cisa-icsnpp-test-traces/icsnpp-enip/enip_cip_example.pcap' 'data/iti-ics-security-tools-pcaps/pcaps/EthernetIP/EthernetIP-CIP.pcap' 'data/iti-ics-security-tools-pcaps/pcaps/EthernetIP/EthernetIP-CIP.pcap' 'data/iti-ics-security-tools-pcaps/pcaps/EthernetIP/enip_test.pcap' 'data/iti-ics-security-tools-pcaps/pcaps/EthernetIP/cip-eth-set-2.pcap'; do echo "== $f"; tshark -r "$f" -Y 'cip.sc in {0x05, 0x06, 0x07, 0x10, 0x4b, 0x4d, 0x53} || enip.command == 0x63' 2>/dev/null | head -3; done
```

## Hints

<details><summary>Hint 1</summary>

Wireshark display filter for the protocol: enip

</details>

<details><summary>Hint 2</summary>

Dangerous-operation filter: cip.sc in {0x05, 0x06, 0x07, 0x10, 0x4b, 0x4d, 0x53} || enip.command == 0x63

</details>

<details><summary>Hint 3</summary>

Many library files are tiny protocol samples — read them packet by packet in Wireshark.

</details>

## Solution

<details><summary>Reveal walkthrough / answer</summary>

A library, not a single puzzle: the deliverable is a per-capture table of roles and operations, with the dangerous ones flagged (CIP Reset (0x05), Start (0x06), Stop (0x07), Set Attribute Single (0x10), Execute PCCC (0x4B), Write Tag (0x4D), Write Tag Fragmented (0x53); ENIP ListIdentity (0x63) is the classic discovery broadcast). ATT&amp;CK for ICS: T0858 Change Operating Mode · T0836 Modify Parameter · T0816 Device Restart/Shutdown · T0846 Remote System Discovery. Sources are credited per collection in each folder's PROVENANCE.md.

**Computed evidence (auto-extracted with tshark — verify it yourself):** EtherNet/IP &amp; CIP operations — Set Attribute Single ×2, Start ×1; dangerous-operation matches: 3 (top sources: 192.168.10.121 ×2, 192.168.1.69 ×1); top conversations in cip-eth-set-2.pcap: 192.168.10.105↔192.168.10.121 (1 pkts) (basis: 3 of 80 capture file(s), first 300,000 packets each, smallest files carrying EtherNet/IP &amp; CIP chosen)

_Captures credited to: ICS-pcap collection (automayt / Jason Smith) — Jason Smith (automayt) · CISA ICSNPP — Zeek ICS parser test traces — CISA and Idaho National Laboratory (ICSNPP project) · ICS-Pcaps (Emre Ekin / ICS Defense) — OT protocol subset — Emre Ekin (ICS Defense, icsdefense.net) · INL Malcolm test artifacts — OT protocol samples — Idaho National Laboratory (Malcolm) · ITI ICS-Security-Tools — sample ICS protocol captures — Information Trust Institute (ITI), University of Illinois Urbana-Champaign · BACnet capture library (kargs.net) — Steve Karg (BACnet Stack author) · ICS sample collection (jenilv-07) — S7comm scenarios, ControlLogix attack attempts, BACnet, Modbus, Omron, Tridium — jenilv-07 (GitHub) · Suricata-verify — ICS protocol test captures — OISF (Open Information Security Foundation)._

</details>

## Dataset & credit

**ICS-pcap collection (automayt / Jason Smith) — Jason Smith (automayt) · CISA ICSNPP — Zeek ICS parser test traces — CISA and Idaho National Laboratory (ICSNPP project) · ICS-Pcaps (Emre Ekin / ICS Defense) — OT protocol subset — Emre Ekin (ICS Defense, icsdefense.net) · INL Malcolm test artifacts — OT protocol samples — Idaho National Laboratory (Malcolm) · ITI ICS-Security-Tools — sample ICS protocol captures — Information Trust Institute (ITI), University of Illinois Urbana-Champaign · BACnet capture library (kargs.net) — Steve Karg (BACnet Stack author) · ICS sample collection (jenilv-07) — S7comm scenarios, ControlLogix attack attempts, BACnet, Modbus, Omron, Tridium — jenilv-07 (GitHub) · Suricata-verify — ICS protocol test captures — OISF (Open Information Security Foundation)** — license: varies by collection — see each folder's PROVENANCE.md

- [Dataset source — ICS-pcap collection (automayt / Jason Smith)](https://github.com/automayt/ICS-pcap)
- [Dataset source — CISA ICSNPP — Zeek ICS parser test traces](https://github.com/cisagov/ICSNPP)
- [Dataset source — ICS-Pcaps (Emre Ekin / ICS Defense) — OT protocol subset](https://github.com/EmreEkin/ICS-Pcaps)
- [Dataset source — INL Malcolm test artifacts — OT protocol samples](https://github.com/idaholab/Malcolm-Test-Artifacts)
- [Dataset source — ITI ICS-Security-Tools — sample ICS protocol captures](https://github.com/ITI/ICS-Security-Tools/tree/master/pcaps)
- [Dataset source — BACnet capture library (kargs.net)](https://kargs.net/captures/)
- [Dataset source — ICS sample collection (jenilv-07) — S7comm scenarios, Contro](https://github.com/jenilv-07/ICS-pcap-files)
- [Dataset source — Suricata-verify — ICS protocol test captures](https://github.com/OISF/suricata-verify)
- [MITRE ATT&amp;CK for ICS](https://attack.mitre.org/matrices/ics/)

<details><summary>Capture files (6)</summary>

- `data/cisa-icsnpp-test-traces/icsnpp-enip/set_attribute_single_service_cip.pcapng`
- `data/cisa-icsnpp-test-traces/icsnpp-enip/set_attribute_single_service_cip.pcapng`
- `data/cisa-icsnpp-test-traces/icsnpp-enip/multiple_service_packet_cip.pcapng`
- `data/cisa-icsnpp-test-traces/icsnpp-enip/multiple_service_packet_cip.pcapng`
- `data/cisa-icsnpp-test-traces/icsnpp-enip/enip_cip_example.pcap`
- `data/cisa-icsnpp-test-traces/icsnpp-enip/enip_cip_example.pcap`

</details>
