# Protocol deep-dive — PROFINET (16 unique captures)

**Protocol library** · **Medium** · 0.8 MB · 3 capture file(s)

> A deduplicated library of 16 PROFINET captures from 5 public collections. Learn the protocol's grammar, then hunt its dangerous operations.

> ⚠️ **Safety:** OT capture analysis is passive and safe. Never replay this traffic onto a real industrial network or send these commands to a real controller.

## Scenario

Every public PROFINET sample in this range, deduplicated by SHA-256 across cisa-icsnpp-test-traces, ics-pcaps-haolipeng, inl-malcolm-ot-artifacts, iti-ics-security-tools-pcaps, s7comm-scenarios-jenilv07. Use it to learn what the protocol looks like on the wire — roles, operations, normal cadence — and to practice spotting the operations attackers abuse: DCP Set (service 4) renames a device or changes its IP — an attacker can knock an IO-device off its controller; DCP Identify (5) is discovery.

## Objectives

- Identify clients/masters and servers/outstations across the samples.
- Enumerate the PROFINET operations present.
- Flag every dangerous operation and its source.
- Map findings to ATT&amp;CK for ICS (T0846 Remote System Discovery · T0836 Modify Parameter · T0814 Denial of Service).

## 📥 Get the captures

The commands on this page read the captures from `data/`. Fetch its 5 datasets first, from the repo root:

```bash
python3 scripts/fetch.py cisa-icsnpp-test-traces ics-pcaps-haolipeng inl-malcolm-ot-artifacts iti-ics-security-tools-pcaps s7comm-scenarios-jenilv07
```

- **[CISA ICSNPP — Zeek ICS parser test traces](../DATASETS.md#cisa-icsnpp-test-traces)** (`cisa-icsnpp-test-traces`), ~14.8 MB once fetched
  - **Mirror:** this repo's [`data-v1` release](https://github.com/SackOfHacks/ICS-PCAP-Challenges/releases/tag/data-v1), 1 part (3.3 MB compressed): [part000](https://github.com/SackOfHacks/ICS-PCAP-Challenges/releases/download/data-v1/cisa-icsnpp-test-traces.tar.part000) (3.3 MB)
  - **Original source:** [github.com/cisagov/ICSNPP](https://github.com/cisagov/ICSNPP)
- **[ICS protocol sample captures (IEC-104, MMS and more)](../DATASETS.md#ics-pcaps-haolipeng)** (`ics-pcaps-haolipeng`), ~4.2 MB once fetched
  - **Not mirrored** (no licence that allows re-hosting): `fetch.py` downloads it from the original source
  - **Original source:** [github.com/haolipeng/ics-pcaps](https://github.com/haolipeng/ics-pcaps)
- **[INL Malcolm test artifacts — OT protocol samples](../DATASETS.md#inl-malcolm-ot-artifacts)** (`inl-malcolm-ot-artifacts`), ~99.2 MB once fetched
  - **Not mirrored** (no licence that allows re-hosting): `fetch.py` downloads it from the original source
  - **Original source:** [github.com/idaholab/Malcolm-Test-Artifacts](https://github.com/idaholab/Malcolm-Test-Artifacts)
- **[ITI ICS-Security-Tools — sample ICS protocol captures](../DATASETS.md#iti-ics-security-tools-pcaps)** (`iti-ics-security-tools-pcaps`), ~0.12 GB once fetched
  - **Not mirrored** (no licence that allows re-hosting): `fetch.py` downloads it from the original source
  - **Original source:** [github.com/ITI/ICS-Security-Tools/tree/master/pcaps](https://github.com/ITI/ICS-Security-Tools/tree/master/pcaps)
- **[ICS sample collection (jenilv-07) — S7comm scenarios, ControlLogix attack attempts, BACnet, Modbus, Omron, Tridium](../DATASETS.md#s7comm-scenarios-jenilv07)** (`s7comm-scenarios-jenilv07`), ~34.1 MB once fetched
  - **Not mirrored** (no licence that allows re-hosting): `fetch.py` downloads it from the original source
  - **Original source:** [github.com/jenilv-07/ICS-pcap-files](https://github.com/jenilv-07/ICS-pcap-files)

Without `fetch.py`: download every part of the dataset, run `cat <dataset>.tar.part* | tar -x`, then `gunzip` the files listed in its `MIRROR-GZIPPED.txt`.

## Work it step by step

Two complete walkthroughs — pick your tool. Run every command from the repo root.

### With Pcapper

[Pcapper](https://github.com/SackOfHacks/pcapper) runs the OT protocol analyzers for you.

**1. Triage the capture**

Duration, endpoints and protocol mix before you dive in. Pcapper's overview auto-detects the OT protocols and runs the matching analyzers.

```bash
pcapper 'data/cisa-icsnpp-test-traces/icsnpp-profinet-io-cm/profinet_io_cm.pcap' --overview
```

**2. Deep-dive with Pcapper (--profinet --lldp)**

Pcapper's protocol analyzer decodes the operations, flags anomalies, and --ot-commands normalizes every control/write across protocols.

```bash
pcapper 'data/cisa-icsnpp-test-traces/icsnpp-profinet-io-cm/profinet_io_cm.pcap' --profinet --lldp --ot-commands
```

**3. Sweep the whole library**

```bash
pcapper data/cisa-icsnpp-test-traces/ --profinet --lldp --ot-commands
```

**4. Map it to ATT&amp;CK for ICS**

Pcapper maps its detections to MITRE ATT&amp;CK (Enterprise + ICS) and draws the attack path.

```bash
pcapper 'data/cisa-icsnpp-test-traces/icsnpp-profinet-io-cm/profinet_io_cm.pcap' --mitre
```

### With tshark / Wireshark

The by-hand route: display filters, field extraction and statistics.

**1. Triage the capture**

Duration, endpoints and protocol mix before you dive in.

```bash
capinfos 'data/cisa-icsnpp-test-traces/icsnpp-profinet-io-cm/profinet_io_cm.pcap'
tshark -r 'data/cisa-icsnpp-test-traces/icsnpp-profinet-io-cm/profinet_io_cm.pcap' -q -z io,phs | head -40
```

**2. Map the PROFINET conversation**

Who polls whom? Masters/clients vs. outstations/servers, and the operation mix per pair.

```bash
tshark -r 'data/cisa-icsnpp-test-traces/icsnpp-profinet-io-cm/profinet_io_cm.pcap' -Y pn_dcp -T fields -e eth.src -e eth.dst -e pn_dcp.service_id -e pn_dcp.suboption_device_nameofstation | sort | uniq -c | sort -rn | head -25
```

**3. Hunt the dangerous operations**

Flag DCP Set (service 4) renames a device or changes its IP — an attacker can knock an IO-device off its controller; DCP Identify (5) is discovery.

```bash
tshark -r 'data/cisa-icsnpp-test-traces/icsnpp-profinet-io-cm/profinet_io_cm.pcap' -Y 'pn_dcp.service_id == 4' -T fields -e frame.time -e ip.src -e ip.dst -e _ws.col.Info | head -40
```

**4. Sweep the whole library**

```bash
for f in 'data/cisa-icsnpp-test-traces/icsnpp-profinet-io-cm/profinet_io_cm.pcap' 'data/cisa-icsnpp-test-traces/icsnpp-profinet-io-cm/profinet_io_cm_mixed_1.pcap' 'data/cisa-icsnpp-test-traces/icsnpp-profinet-io-cm/profinet_io_cm_mixed_2.pcapng' 'data/iti-ics-security-tools-pcaps/pcaps/Combined/Plant1.pcap' 'data/iti-ics-security-tools-pcaps/pcaps/profinet/profinet-wireshark-bug.pcap' 'data/iti-ics-security-tools-pcaps/pcaps/profinet/PROFINET-RT-DCP/PROFINET-RT.pcap' 'data/iti-ics-security-tools-pcaps/pcaps/profinet/PROFINET-RT-DCP/ChangeIPUsingDCP.pcap' 'data/iti-ics-security-tools-pcaps/pcaps/ModbusTCP/mb2.pcap' 'data/ics-pcaps-haolipeng/profinet_synthetic/synthetic-get-dcp.pcap' 'data/ics-pcaps-haolipeng/profinet_synthetic/synthetic-malformed-dcp.pcap'; do echo "== $f"; tshark -r "$f" -Y 'pn_dcp.service_id == 4' 2>/dev/null | head -3; done
```

## Hints

<details><summary>Hint 1</summary>

Wireshark display filter for the protocol: pn_dcp || pn_rt || pn_io || pn_ptcp

</details>

<details><summary>Hint 2</summary>

Dangerous-operation filter: pn_dcp.service_id == 4

</details>

<details><summary>Hint 3</summary>

Many library files are tiny protocol samples — read them packet by packet in Wireshark.

</details>

## Solution

<details><summary>Reveal walkthrough / answer</summary>

A library, not a single puzzle: the deliverable is a per-capture table of roles and operations, with the dangerous ones flagged (DCP Set (service 4) renames a device or changes its IP — an attacker can knock an IO-device off its controller; DCP Identify (5) is discovery). ATT&amp;CK for ICS: T0846 Remote System Discovery · T0836 Modify Parameter · T0814 Denial of Service. Sources are credited per collection in each folder's PROVENANCE.md.

**Computed evidence (auto-extracted with tshark — verify it yourself):** PROFINET operations — DCP Hello ×2, DCP Get ×2; dangerous-operation matches: 0 for the PROFINET filter (5 PROFINET packets present, so the zero is real) (basis: 3 of 16 capture file(s), first 300,000 packets each, smallest files carrying PROFINET chosen)

_Captures credited to: CISA ICSNPP — Zeek ICS parser test traces — CISA and Idaho National Laboratory (ICSNPP project) · ICS protocol sample captures (IEC-104, MMS and more) — haolipeng (GitHub) · INL Malcolm test artifacts — OT protocol samples — Idaho National Laboratory (Malcolm) · ITI ICS-Security-Tools — sample ICS protocol captures — Information Trust Institute (ITI), University of Illinois Urbana-Champaign · ICS sample collection (jenilv-07) — S7comm scenarios, ControlLogix attack attempts, BACnet, Modbus, Omron, Tridium — jenilv-07 (GitHub)._

</details>

## Dataset & credit

**CISA ICSNPP — Zeek ICS parser test traces — CISA and Idaho National Laboratory (ICSNPP project) · ICS protocol sample captures (IEC-104, MMS and more) — haolipeng (GitHub) · INL Malcolm test artifacts — OT protocol samples — Idaho National Laboratory (Malcolm) · ITI ICS-Security-Tools — sample ICS protocol captures — Information Trust Institute (ITI), University of Illinois Urbana-Champaign · ICS sample collection (jenilv-07) — S7comm scenarios, ControlLogix attack attempts, BACnet, Modbus, Omron, Tridium — jenilv-07 (GitHub)** — license: varies by collection — see each folder's PROVENANCE.md

- [Dataset source — CISA ICSNPP — Zeek ICS parser test traces](https://github.com/cisagov/ICSNPP)
- [Dataset source — ICS protocol sample captures (IEC-104, MMS and more)](https://github.com/haolipeng/ics-pcaps)
- [Dataset source — INL Malcolm test artifacts — OT protocol samples](https://github.com/idaholab/Malcolm-Test-Artifacts)
- [Dataset source — ITI ICS-Security-Tools — sample ICS protocol captures](https://github.com/ITI/ICS-Security-Tools/tree/master/pcaps)
- [Dataset source — ICS sample collection (jenilv-07) — S7comm scenarios, Contro](https://github.com/jenilv-07/ICS-pcap-files)
- [MITRE ATT&amp;CK for ICS](https://attack.mitre.org/matrices/ics/)

<details><summary>Capture files (3)</summary>

- `data/cisa-icsnpp-test-traces/icsnpp-profinet-io-cm/profinet_io_cm.pcap`
- `data/cisa-icsnpp-test-traces/icsnpp-profinet-io-cm/profinet_io_cm_mixed_1.pcap`
- `data/cisa-icsnpp-test-traces/icsnpp-profinet-io-cm/profinet_io_cm_mixed_2.pcapng`

</details>
