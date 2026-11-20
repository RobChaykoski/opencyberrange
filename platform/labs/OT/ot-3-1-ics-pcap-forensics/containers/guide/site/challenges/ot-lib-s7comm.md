# Protocol deep-dive — S7comm (52 unique captures)

**Protocol library** · **Medium** · 0.1 MB · 4 capture file(s)

> A deduplicated library of 52 S7comm captures from 7 public collections. Learn the protocol's grammar, then hunt its dangerous operations.

> ⚠️ **Safety:** OT capture analysis is passive and safe. Never replay this traffic onto a real industrial network or send these commands to a real controller.

## Scenario

Every public S7comm sample in this range, deduplicated by SHA-256 across automayt-ics-pcap, cisa-icsnpp-test-traces, emreekin-ics-pcaps, ics-pcaps-haolipeng, inl-malcolm-ot-artifacts, iti-ics-security-tools-pcaps, s7comm-scenarios-jenilv07. Use it to learn what the protocol looks like on the wire — roles, operations, normal cadence — and to practice spotting the operations attackers abuse: write variable (0x05), program download (0x1A–0x1C), program upload (0x1D–0x1F — logic theft), PI-service (0x28 — start/restart/compress), PLC STOP (0x29) and security/password userdata (function group 5); SZL reads (function group 4) are device recon.

## Objectives

- Identify clients/masters and servers/outstations across the samples.
- Enumerate the S7comm operations present.
- Flag every dangerous operation and its source.
- Map findings to ATT&amp;CK for ICS (T0843 Program Download · T0845 Program Upload · T0858 Change Operating Mode · T0836 Modify Parameter · T0888 Remote System Information Discovery).

## 📥 Get the captures

The commands on this page read the captures from `data/`. Fetch its 7 datasets first, from the repo root:

```bash
python3 scripts/fetch.py automayt-ics-pcap cisa-icsnpp-test-traces emreekin-ics-pcaps ics-pcaps-haolipeng inl-malcolm-ot-artifacts iti-ics-security-tools-pcaps s7comm-scenarios-jenilv07
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
pcapper 'data/cisa-icsnpp-test-traces/icsnpp-s7comm/s7comm_plus_port_change.pcap' --overview
```

**2. Pcapper reports TCP/5678 as an unknown service**

Pcapper recognises OT protocols on their standard ports, so it lists TCP/5678 without decoding it. Identify the protocol with tshark's decode-as (see the tshark / Wireshark track), then continue here.

```bash
pcapper 'data/cisa-icsnpp-test-traces/icsnpp-s7comm/s7comm_plus_port_change.pcap' --services
```

**3. Deep-dive with Pcapper (--s7)**

Pcapper's protocol analyzer decodes the operations, flags anomalies, and --ot-commands normalizes every control/write across protocols.

```bash
pcapper 'data/cisa-icsnpp-test-traces/icsnpp-s7comm/s7comm_plus_port_change.pcap' --s7 --ot-commands
```

**4. Sweep the whole library**

```bash
pcapper data/automayt-ics-pcap/ --s7 --ot-commands
```

**5. Map it to ATT&amp;CK for ICS**

Pcapper maps its detections to MITRE ATT&amp;CK (Enterprise + ICS) and draws the attack path.

```bash
pcapper 'data/cisa-icsnpp-test-traces/icsnpp-s7comm/s7comm_plus_port_change.pcap' --mitre
```

### With tshark / Wireshark

The by-hand route: display filters, field extraction and statistics.

**1. Triage the capture**

Duration, endpoints and protocol mix before you dive in.

```bash
capinfos 'data/cisa-icsnpp-test-traces/icsnpp-s7comm/s7comm_plus_port_change.pcap'
tshark -r 'data/cisa-icsnpp-test-traces/icsnpp-s7comm/s7comm_plus_port_change.pcap' -q -z io,phs | head -40
```

**2. Map the S7comm conversation**

Who polls whom? Masters/clients vs. outstations/servers, and the operation mix per pair.

```bash
tshark -r 'data/cisa-icsnpp-test-traces/icsnpp-s7comm/s7comm_plus_port_change.pcap' -d tcp.port==5678,tpkt -Y s7comm -T fields -e ip.src -e ip.dst -e s7comm.header.rosctr -e s7comm.param.func -e s7comm.param.userdata.funcgroup -e s7comm.param.userdata.subfunc | sort | uniq -c | sort -rn | head -25
```

**3. Hunt the dangerous operations**

Flag write variable (0x05), program download (0x1A–0x1C), program upload (0x1D–0x1F — logic theft), PI-service (0x28 — start/restart/compress), PLC STOP (0x29) and security/password userdata (function group 5); SZL reads (function group 4) are device recon.

```bash
tshark -r 'data/cisa-icsnpp-test-traces/icsnpp-s7comm/s7comm_plus_port_change.pcap' -d tcp.port==5678,tpkt -Y 's7comm.param.func in {0x05, 0x1a, 0x1b, 0x1c, 0x1d, 0x1e, 0x1f, 0x28, 0x29} || s7comm.param.userdata.funcgroup == 5' -T fields -e frame.time -e ip.src -e ip.dst -e _ws.col.Info | head -40
```

**4. Sweep the whole library**

```bash
for f in 'data/cisa-icsnpp-test-traces/icsnpp-s7comm/s7comm_plus_port_change.pcap' 'data/cisa-icsnpp-test-traces/icsnpp-s7comm/s7comm_plus.pcap' 'data/cisa-icsnpp-test-traces/icsnpp-s7comm/snap7.pcap' 'data/cisa-icsnpp-test-traces/icsnpp-s7comm/s7ident.pcap' 'data/iti-ics-security-tools-pcaps/pcaps/Combined/Plant1.pcap' 'data/iti-ics-security-tools-pcaps/pcaps/ModbusTCP/mb2.pcap' 'data/iti-ics-security-tools-pcaps/pcaps/s7/step7_s300_download.pcapng' 'data/iti-ics-security-tools-pcaps/pcaps/s7/s7comm_varservice_libnodavedemo_bench.pcap' 'data/iti-ics-security-tools-pcaps/pcaps/s7/snap7_s300_stop.pcapng' 'data/iti-ics-security-tools-pcaps/pcaps/s7/step7_s300_readVarTab.pcapng'; do echo "== $f"; tshark -r "$f" -Y 's7comm.param.func in {0x05, 0x1a, 0x1b, 0x1c, 0x1d, 0x1e, 0x1f, 0x28, 0x29} || s7comm.param.userdata.funcgroup == 5' 2>/dev/null | head -3; done
```

## Hints

<details><summary>Hint 1</summary>

Wireshark display filter for the protocol: s7comm

</details>

<details><summary>Hint 2</summary>

Dangerous-operation filter: s7comm.param.func in {0x05, 0x1a, 0x1b, 0x1c, 0x1d, 0x1e, 0x1f, 0x28, 0x29} || s7comm.param.userdata.funcgroup == 5

</details>

<details><summary>Hint 3</summary>

Many library files are tiny protocol samples — read them packet by packet in Wireshark.

</details>

## Solution

<details><summary>Reveal walkthrough / answer</summary>

A library, not a single puzzle: the deliverable is a per-capture table of roles and operations, with the dangerous ones flagged (write variable (0x05), program download (0x1A–0x1C), program upload (0x1D–0x1F — logic theft), PI-service (0x28 — start/restart/compress), PLC STOP (0x29) and security/password userdata (function group 5); SZL reads (function group 4) are device recon). ATT&amp;CK for ICS: T0843 Program Download · T0845 Program Upload · T0858 Change Operating Mode · T0836 Modify Parameter · T0888 Remote System Information Discovery. Sources are credited per collection in each folder's PROVENANCE.md.

**Computed evidence (auto-extracted with tshark — verify it yourself):** S7comm operations — Setup Communication ×3, PLC Stop ×2; dangerous-operation matches: 2 (top sources: 134.249.62.206 ×1, 134.249.61.163 ×1); top conversations in pro2.pcap: 10.10.10.10↔10.10.10.70 (2 pkts) (basis: 3 of 52 capture file(s), first 300,000 packets each, smallest files carrying S7comm chosen)

_Captures credited to: ICS-pcap collection (automayt / Jason Smith) — Jason Smith (automayt) · CISA ICSNPP — Zeek ICS parser test traces — CISA and Idaho National Laboratory (ICSNPP project) · ICS-Pcaps (Emre Ekin / ICS Defense) — OT protocol subset — Emre Ekin (ICS Defense, icsdefense.net) · ICS protocol sample captures (IEC-104, MMS and more) — haolipeng (GitHub) · INL Malcolm test artifacts — OT protocol samples — Idaho National Laboratory (Malcolm) · ITI ICS-Security-Tools — sample ICS protocol captures — Information Trust Institute (ITI), University of Illinois Urbana-Champaign · ICS sample collection (jenilv-07) — S7comm scenarios, ControlLogix attack attempts, BACnet, Modbus, Omron, Tridium — jenilv-07 (GitHub)._

</details>

## Dataset & credit

**ICS-pcap collection (automayt / Jason Smith) — Jason Smith (automayt) · CISA ICSNPP — Zeek ICS parser test traces — CISA and Idaho National Laboratory (ICSNPP project) · ICS-Pcaps (Emre Ekin / ICS Defense) — OT protocol subset — Emre Ekin (ICS Defense, icsdefense.net) · ICS protocol sample captures (IEC-104, MMS and more) — haolipeng (GitHub) · INL Malcolm test artifacts — OT protocol samples — Idaho National Laboratory (Malcolm) · ITI ICS-Security-Tools — sample ICS protocol captures — Information Trust Institute (ITI), University of Illinois Urbana-Champaign · ICS sample collection (jenilv-07) — S7comm scenarios, ControlLogix attack attempts, BACnet, Modbus, Omron, Tridium — jenilv-07 (GitHub)** — license: varies by collection — see each folder's PROVENANCE.md

- [Dataset source — ICS-pcap collection (automayt / Jason Smith)](https://github.com/automayt/ICS-pcap)
- [Dataset source — CISA ICSNPP — Zeek ICS parser test traces](https://github.com/cisagov/ICSNPP)
- [Dataset source — ICS-Pcaps (Emre Ekin / ICS Defense) — OT protocol subset](https://github.com/EmreEkin/ICS-Pcaps)
- [Dataset source — ICS protocol sample captures (IEC-104, MMS and more)](https://github.com/haolipeng/ics-pcaps)
- [Dataset source — INL Malcolm test artifacts — OT protocol samples](https://github.com/idaholab/Malcolm-Test-Artifacts)
- [Dataset source — ITI ICS-Security-Tools — sample ICS protocol captures](https://github.com/ITI/ICS-Security-Tools/tree/master/pcaps)
- [Dataset source — ICS sample collection (jenilv-07) — S7comm scenarios, Contro](https://github.com/jenilv-07/ICS-pcap-files)
- [MITRE ATT&amp;CK for ICS](https://attack.mitre.org/matrices/ics/)

<details><summary>Capture files (4)</summary>

- `data/cisa-icsnpp-test-traces/icsnpp-s7comm/s7comm_plus_port_change.pcap`
- `data/cisa-icsnpp-test-traces/icsnpp-s7comm/s7comm_plus.pcap`
- `data/cisa-icsnpp-test-traces/icsnpp-s7comm/snap7.pcap`
- `data/cisa-icsnpp-test-traces/icsnpp-s7comm/s7ident.pcap`

</details>
