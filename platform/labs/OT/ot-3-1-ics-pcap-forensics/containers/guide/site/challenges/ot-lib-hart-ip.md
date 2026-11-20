# Protocol deep-dive — HART-IP (5 unique captures)

**Protocol library** · **Easy** · 0.5 MB · 4 capture file(s)

> A deduplicated library of 5 HART-IP captures from 2 public collections. Learn the protocol's grammar, then hunt its dangerous operations.

> ⚠️ **Safety:** OT capture analysis is passive and safe. Never replay this traffic onto a real industrial network or send these commands to a real controller.

## Scenario

Every public HART-IP sample in this range, deduplicated by SHA-256 across cisa-icsnpp-test-traces, inl-malcolm-ot-artifacts. Use it to learn what the protocol looks like on the wire — roles, operations, normal cadence — and to practice spotting the operations attackers abuse: HART-IP tunnels HART commands to field instruments — command 0 (read unique ID) is recon; write commands change instrument configuration.

## Objectives

- Identify clients/masters and servers/outstations across the samples.
- Enumerate the HART-IP operations present.
- Flag every dangerous operation and its source.
- Map findings to ATT&amp;CK for ICS (T0888 Remote System Information Discovery · T0836 Modify Parameter).

## 📥 Get the captures

The commands on this page read the captures from `data/`. Fetch its 2 datasets first, from the repo root:

```bash
python3 scripts/fetch.py cisa-icsnpp-test-traces inl-malcolm-ot-artifacts
```

- **[CISA ICSNPP — Zeek ICS parser test traces](../DATASETS.md#cisa-icsnpp-test-traces)** (`cisa-icsnpp-test-traces`), ~14.8 MB once fetched
  - **Mirror:** this repo's [`data-v1` release](https://github.com/SackOfHacks/ICS-PCAP-Challenges/releases/tag/data-v1), 1 part (3.3 MB compressed): [part000](https://github.com/SackOfHacks/ICS-PCAP-Challenges/releases/download/data-v1/cisa-icsnpp-test-traces.tar.part000) (3.3 MB)
  - **Original source:** [github.com/cisagov/ICSNPP](https://github.com/cisagov/ICSNPP)
- **[INL Malcolm test artifacts — OT protocol samples](../DATASETS.md#inl-malcolm-ot-artifacts)** (`inl-malcolm-ot-artifacts`), ~99.2 MB once fetched
  - **Not mirrored** (no licence that allows re-hosting): `fetch.py` downloads it from the original source
  - **Original source:** [github.com/idaholab/Malcolm-Test-Artifacts](https://github.com/idaholab/Malcolm-Test-Artifacts)

Without `fetch.py`: download every part of the dataset, run `cat <dataset>.tar.part* | tar -x`, then `gunzip` the files listed in its `MIRROR-GZIPPED.txt`.

## Work it step by step

Two complete walkthroughs — pick your tool. Run every command from the repo root.

### With Pcapper

[Pcapper](https://github.com/SackOfHacks/pcapper) runs the OT protocol analyzers for you.

**1. Triage the capture**

Duration, endpoints and protocol mix before you dive in. Pcapper's overview auto-detects the OT protocols and runs the matching analyzers.

```bash
pcapper 'data/cisa-icsnpp-test-traces/icsnpp-hart-ip/hart-ip_all_types_and_commands_sent.pcapng' --overview
```

**2. Deep-dive with Pcapper (--hart)**

Pcapper's protocol analyzer decodes the operations, flags anomalies, and --ot-commands normalizes every control/write across protocols.

```bash
pcapper 'data/cisa-icsnpp-test-traces/icsnpp-hart-ip/hart-ip_all_types_and_commands_sent.pcapng' --hart --ot-commands
```

**3. Sweep the whole library**

```bash
pcapper data/cisa-icsnpp-test-traces/ --hart --ot-commands
```

**4. Map it to ATT&amp;CK for ICS**

Pcapper maps its detections to MITRE ATT&amp;CK (Enterprise + ICS) and draws the attack path.

```bash
pcapper 'data/cisa-icsnpp-test-traces/icsnpp-hart-ip/hart-ip_all_types_and_commands_sent.pcapng' --mitre
```

### With tshark / Wireshark

The by-hand route: display filters, field extraction and statistics.

**1. Triage the capture**

Duration, endpoints and protocol mix before you dive in.

```bash
capinfos 'data/cisa-icsnpp-test-traces/icsnpp-hart-ip/hart-ip_all_types_and_commands_sent.pcapng'
tshark -r 'data/cisa-icsnpp-test-traces/icsnpp-hart-ip/hart-ip_all_types_and_commands_sent.pcapng' -q -z io,phs | head -40
```

**2. Map the HART-IP conversation**

Who polls whom? Masters/clients vs. outstations/servers, and the operation mix per pair.

```bash
tshark -r 'data/cisa-icsnpp-test-traces/icsnpp-hart-ip/hart-ip_all_types_and_commands_sent.pcapng' -Y hart_ip -T fields -e ip.src -e ip.dst -e hart_ip.message_id | sort | uniq -c | sort -rn | head -25
```

**3. Hunt the dangerous operations**

Flag HART-IP tunnels HART commands to field instruments — command 0 (read unique ID) is recon; write commands change instrument configuration.

```bash
tshark -r 'data/cisa-icsnpp-test-traces/icsnpp-hart-ip/hart-ip_all_types_and_commands_sent.pcapng' -Y 'hart_ip' -T fields -e frame.time -e ip.src -e ip.dst -e _ws.col.Info | head -40
```

**4. Sweep the whole library**

```bash
for f in 'data/cisa-icsnpp-test-traces/icsnpp-hart-ip/hart-ip_all_types_and_commands_sent.pcapng' 'data/cisa-icsnpp-test-traces/icsnpp-hart-ip/hart-ip_all_messageIDs.pcapng' 'data/cisa-icsnpp-test-traces/icsnpp-hart-ip/hart-ip.pcap' 'data/cisa-icsnpp-test-traces/icsnpp-hart-ip/hart-ip_publish_and_keepAlive.pcapng' 'data/inl-malcolm-ot-artifacts/Malcolm-Test-Artifacts-main/pcap/protocols/HARTIP.pcap'; do echo "== $f"; tshark -r "$f" -Y 'hart_ip' 2>/dev/null | head -3; done
```

## Hints

<details><summary>Hint 1</summary>

Wireshark display filter for the protocol: hart_ip

</details>

<details><summary>Hint 2</summary>

Dangerous-operation filter: hart_ip

</details>

<details><summary>Hint 3</summary>

Many library files are tiny protocol samples — read them packet by packet in Wireshark.

</details>

## Solution

<details><summary>Reveal walkthrough / answer</summary>

A library, not a single puzzle: the deliverable is a per-capture table of roles and operations, with the dangerous ones flagged (HART-IP tunnels HART commands to field instruments — command 0 (read unique ID) is recon; write commands change instrument configuration). ATT&amp;CK for ICS: T0888 Remote System Information Discovery · T0836 Modify Parameter. Sources are credited per collection in each folder's PROVENANCE.md.

**Computed evidence (auto-extracted with tshark — verify it yourself):** HART-IP packets matching `hart_ip`: 131; top conversations in hart-ip_all_messageIDs.pcapng: 10.9.0.117↔192.168.122.197 (19 pkts) (basis: 3 of 5 capture file(s), first 300,000 packets each, smallest files carrying HART-IP chosen)

_Captures credited to: CISA ICSNPP — Zeek ICS parser test traces — CISA and Idaho National Laboratory (ICSNPP project) · INL Malcolm test artifacts — OT protocol samples — Idaho National Laboratory (Malcolm)._

</details>

## Dataset & credit

**CISA ICSNPP — Zeek ICS parser test traces — CISA and Idaho National Laboratory (ICSNPP project) · INL Malcolm test artifacts — OT protocol samples — Idaho National Laboratory (Malcolm)** — license: varies by collection — see each folder's PROVENANCE.md

- [Dataset source — CISA ICSNPP — Zeek ICS parser test traces](https://github.com/cisagov/ICSNPP)
- [Dataset source — INL Malcolm test artifacts — OT protocol samples](https://github.com/idaholab/Malcolm-Test-Artifacts)
- [MITRE ATT&amp;CK for ICS](https://attack.mitre.org/matrices/ics/)

<details><summary>Capture files (4)</summary>

- `data/cisa-icsnpp-test-traces/icsnpp-hart-ip/hart-ip_all_types_and_commands_sent.pcapng`
- `data/cisa-icsnpp-test-traces/icsnpp-hart-ip/hart-ip_all_messageIDs.pcapng`
- `data/cisa-icsnpp-test-traces/icsnpp-hart-ip/hart-ip.pcap`
- `data/cisa-icsnpp-test-traces/icsnpp-hart-ip/hart-ip_publish_and_keepAlive.pcapng`

</details>
