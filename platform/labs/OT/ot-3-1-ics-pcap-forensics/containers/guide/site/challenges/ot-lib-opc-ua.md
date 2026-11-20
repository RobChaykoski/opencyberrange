# Protocol deep-dive — OPC UA (29 unique captures)

**Protocol library** · **Medium** · 1.1 MB · 27 capture file(s)

> A deduplicated library of 29 OPC UA captures from 3 public collections. Learn the protocol's grammar, then hunt its dangerous operations.

> ⚠️ **Safety:** OT capture analysis is passive and safe. Never replay this traffic onto a real industrial network or send these commands to a real controller.

## Scenario

Every public OPC UA sample in this range, deduplicated by SHA-256 across cisa-icsnpp-test-traces, emreekin-ics-pcaps, inl-malcolm-ot-artifacts. Use it to learn what the protocol looks like on the wire — roles, operations, normal cadence — and to practice spotting the operations attackers abuse: Write (node 673) and Call (712, method execution); Browse (527) maps the address space; check OpenSecureChannel/CreateSession for SecurityMode None and anonymous ActivateSession.

## Objectives

- Identify clients/masters and servers/outstations across the samples.
- Enumerate the OPC UA operations present.
- Flag every dangerous operation and its source.
- Map findings to ATT&amp;CK for ICS (T0836 Modify Parameter · T0871 Execution through API · T0861 Point &amp; Tag Identification).

## 📥 Get the captures

The commands on this page read the captures from `data/`. Fetch its 3 datasets first, from the repo root:

```bash
python3 scripts/fetch.py cisa-icsnpp-test-traces emreekin-ics-pcaps inl-malcolm-ot-artifacts
```

- **[CISA ICSNPP — Zeek ICS parser test traces](../DATASETS.md#cisa-icsnpp-test-traces)** (`cisa-icsnpp-test-traces`), ~14.8 MB once fetched
  - **Mirror:** this repo's [`data-v1` release](https://github.com/SackOfHacks/ICS-PCAP-Challenges/releases/tag/data-v1), 1 part (3.3 MB compressed): [part000](https://github.com/SackOfHacks/ICS-PCAP-Challenges/releases/download/data-v1/cisa-icsnpp-test-traces.tar.part000) (3.3 MB)
  - **Original source:** [github.com/cisagov/ICSNPP](https://github.com/cisagov/ICSNPP)
- **[ICS-Pcaps (Emre Ekin / ICS Defense) — OT protocol subset](../DATASETS.md#emreekin-ics-pcaps)** (`emreekin-ics-pcaps`), ~0.26 GB once fetched
  - **Not mirrored** (no licence that allows re-hosting): `fetch.py` downloads it from the original source
  - **Original source:** [github.com/EmreEkin/ICS-Pcaps](https://github.com/EmreEkin/ICS-Pcaps)
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
pcapper 'data/cisa-icsnpp-test-traces/icsnpp-opcua-binary/open62541_discover_getendpoints_discover_urls.pcap' --overview
```

**2. Deep-dive with Pcapper (--opc)**

Pcapper's protocol analyzer decodes the operations, flags anomalies, and --ot-commands normalizes every control/write across protocols.

```bash
pcapper 'data/cisa-icsnpp-test-traces/icsnpp-opcua-binary/open62541_discover_getendpoints_discover_urls.pcap' --opc --ot-commands
```

**3. Sweep the whole library**

```bash
pcapper data/cisa-icsnpp-test-traces/ --opc --ot-commands
```

**4. Map it to ATT&amp;CK for ICS**

Pcapper maps its detections to MITRE ATT&amp;CK (Enterprise + ICS) and draws the attack path.

```bash
pcapper 'data/cisa-icsnpp-test-traces/icsnpp-opcua-binary/open62541_discover_getendpoints_discover_urls.pcap' --mitre
```

### With tshark / Wireshark

The by-hand route: display filters, field extraction and statistics.

**1. Triage the capture**

Duration, endpoints and protocol mix before you dive in.

```bash
capinfos 'data/cisa-icsnpp-test-traces/icsnpp-opcua-binary/open62541_discover_getendpoints_discover_urls.pcap'
tshark -r 'data/cisa-icsnpp-test-traces/icsnpp-opcua-binary/open62541_discover_getendpoints_discover_urls.pcap' -q -z io,phs | head -40
```

**2. Map the OPC UA conversation**

Who polls whom? Masters/clients vs. outstations/servers, and the operation mix per pair.

```bash
tshark -r 'data/cisa-icsnpp-test-traces/icsnpp-opcua-binary/open62541_discover_getendpoints_discover_urls.pcap' -Y opcua -T fields -e ip.src -e ip.dst -e opcua.transport.type -e opcua.servicenodeid.numeric | sort | uniq -c | sort -rn | head -25
```

**3. Hunt the dangerous operations**

Flag Write (node 673) and Call (712, method execution); Browse (527) maps the address space; check OpenSecureChannel/CreateSession for SecurityMode None and anonymous ActivateSession.

```bash
tshark -r 'data/cisa-icsnpp-test-traces/icsnpp-opcua-binary/open62541_discover_getendpoints_discover_urls.pcap' -Y 'opcua.servicenodeid.numeric in {673, 712}' -T fields -e frame.time -e ip.src -e ip.dst -e _ws.col.Info | head -40
```

**4. Sweep the whole library**

```bash
for f in 'data/cisa-icsnpp-test-traces/icsnpp-opcua-binary/open62541_discover_getendpoints_discover_urls.pcap' 'data/cisa-icsnpp-test-traces/icsnpp-opcua-binary/python_opcua-client-server_minimal.pcap' 'data/cisa-icsnpp-test-traces/icsnpp-opcua-binary/open62541_create_monitored_items.pcap' 'data/cisa-icsnpp-test-traces/icsnpp-opcua-binary/open62541_client-server_mainloop-ActivateSession-diagInfo.pcap' 'data/cisa-icsnpp-test-traces/icsnpp-opcua-binary/open62541_client-server_encrypted.pcap' 'data/cisa-icsnpp-test-traces/icsnpp-opcua-binary/pending_overflow.pcap' 'data/cisa-icsnpp-test-traces/icsnpp-opcua-binary/opcua_with-gap_with-handshake.pcap' 'data/cisa-icsnpp-test-traces/icsnpp-opcua-binary/python_opcua-client-server_minimal-2.pcap' 'data/cisa-icsnpp-test-traces/icsnpp-opcua-binary/open62541_client-server_mainloop-hasInnerDiagInfo.pcap' 'data/cisa-icsnpp-test-traces/icsnpp-opcua-binary/opcua_with_nested_diagInfo.pcap'; do echo "== $f"; tshark -r "$f" -Y 'opcua.servicenodeid.numeric in {673, 712}' 2>/dev/null | head -3; done
```

## Hints

<details><summary>Hint 1</summary>

Wireshark display filter for the protocol: opcua

</details>

<details><summary>Hint 2</summary>

Dangerous-operation filter: opcua.servicenodeid.numeric in {673, 712}

</details>

<details><summary>Hint 3</summary>

Many library files are tiny protocol samples — read them packet by packet in Wireshark.

</details>

## Solution

<details><summary>Reveal walkthrough / answer</summary>

A library, not a single puzzle: the deliverable is a per-capture table of roles and operations, with the dangerous ones flagged (Write (node 673) and Call (712, method execution); Browse (527) maps the address space; check OpenSecureChannel/CreateSession for SecurityMode None and anonymous ActivateSession). ATT&amp;CK for ICS: T0836 Modify Parameter · T0871 Execution through API · T0861 Point &amp; Tag Identification. Sources are credited per collection in each folder's PROVENANCE.md.

**Computed evidence (auto-extracted with tshark — verify it yourself):** OPC UA operations — OpenSecureChannel ×3, 449 ×3, 452 ×3, GetEndpoints ×2, 554 ×2, 557 ×2, 431 ×1, CreateSession ×1; dangerous-operation matches: 0 for the OPC UA filter (30 OPC UA packets present, so the zero is real); top conversations in opycua_share.pcap: 192.168.1.101↔192.168.1.106 (7 pkts) (basis: 3 of 29 capture file(s), first 300,000 packets each, smallest files carrying OPC UA chosen)

_Captures credited to: CISA ICSNPP — Zeek ICS parser test traces — CISA and Idaho National Laboratory (ICSNPP project) · ICS-Pcaps (Emre Ekin / ICS Defense) — OT protocol subset — Emre Ekin (ICS Defense, icsdefense.net) · INL Malcolm test artifacts — OT protocol samples — Idaho National Laboratory (Malcolm)._

</details>

## Dataset & credit

**CISA ICSNPP — Zeek ICS parser test traces — CISA and Idaho National Laboratory (ICSNPP project) · ICS-Pcaps (Emre Ekin / ICS Defense) — OT protocol subset — Emre Ekin (ICS Defense, icsdefense.net) · INL Malcolm test artifacts — OT protocol samples — Idaho National Laboratory (Malcolm)** — license: varies by collection — see each folder's PROVENANCE.md

- [Dataset source — CISA ICSNPP — Zeek ICS parser test traces](https://github.com/cisagov/ICSNPP)
- [Dataset source — ICS-Pcaps (Emre Ekin / ICS Defense) — OT protocol subset](https://github.com/EmreEkin/ICS-Pcaps)
- [Dataset source — INL Malcolm test artifacts — OT protocol samples](https://github.com/idaholab/Malcolm-Test-Artifacts)
- [MITRE ATT&amp;CK for ICS](https://attack.mitre.org/matrices/ics/)

<details><summary>Capture files (27)</summary>

- `data/cisa-icsnpp-test-traces/icsnpp-opcua-binary/open62541_discover_getendpoints_discover_urls.pcap`
- `data/cisa-icsnpp-test-traces/icsnpp-opcua-binary/python_opcua-client-server_minimal.pcap`
- `data/cisa-icsnpp-test-traces/icsnpp-opcua-binary/open62541_create_monitored_items.pcap`
- `data/cisa-icsnpp-test-traces/icsnpp-opcua-binary/open62541_client-server_mainloop-ActivateSession-diagInfo.pcap`
- `data/cisa-icsnpp-test-traces/icsnpp-opcua-binary/open62541_client-server_encrypted.pcap`
- `data/cisa-icsnpp-test-traces/icsnpp-opcua-binary/pending_overflow.pcap`
- `data/cisa-icsnpp-test-traces/icsnpp-opcua-binary/opcua_with-gap_with-handshake.pcap`
- `data/cisa-icsnpp-test-traces/icsnpp-opcua-binary/python_opcua-client-server_minimal-2.pcap`
- `data/cisa-icsnpp-test-traces/icsnpp-opcua-binary/open62541_client-server_mainloop-hasInnerDiagInfo.pcap`
- `data/cisa-icsnpp-test-traces/icsnpp-opcua-binary/opcua_with_nested_diagInfo.pcap`
- `data/cisa-icsnpp-test-traces/icsnpp-opcua-binary/open62541_client-server_mainloop-not-localhost.pcap`
- `data/cisa-icsnpp-test-traces/icsnpp-opcua-binary/open62541_read_service_test_data_with_history.pcap`
- `data/cisa-icsnpp-test-traces/icsnpp-opcua-binary/open62541_browse_with_diagnostic_info.pcap`
- `data/cisa-icsnpp-test-traces/icsnpp-opcua-binary/open62541_browse_request_with_results.pcap`
- `data/cisa-icsnpp-test-traces/icsnpp-opcua-binary/open62541_client-server_mainloop-withStringTable.pcap`
- `data/cisa-icsnpp-test-traces/icsnpp-opcua-binary/open62541_browse_has_server_idx.pcap`
- `data/cisa-icsnpp-test-traces/icsnpp-opcua-binary/opcua_with-gap.pcap`
- `data/cisa-icsnpp-test-traces/icsnpp-opcua-binary/open62541_browse_next.pcap`
- `data/cisa-icsnpp-test-traces/icsnpp-opcua-binary/open62541_client-server_mainloop-4-InnerDiagInfo.pcap`
- `data/cisa-icsnpp-test-traces/icsnpp-opcua-binary/open62541_client-server_mainloop-hasInnerStatusCode.pcap`
- `data/cisa-icsnpp-test-traces/icsnpp-opcua-binary/open62541_client-server_mainloop-hasInnerDiagInfohasAddlInfo.pcap`
- `data/cisa-icsnpp-test-traces/icsnpp-opcua-binary/open62541_client-server_mainloop.pcap`
- `data/cisa-icsnpp-test-traces/icsnpp-opcua-binary/open62541_read_service_test_data.pcap`
- `data/cisa-icsnpp-test-traces/icsnpp-opcua-binary/open62541_client-server_mainloop-no-handshake.pcap`
- `data/cisa-icsnpp-test-traces/icsnpp-opcua-binary/open62541_client-server_minimal.pcap`
- `data/cisa-icsnpp-test-traces/icsnpp-opcua-binary/python_opcua-client-server_encrypted.pcap`
- `data/cisa-icsnpp-test-traces/icsnpp-opcua-binary/open62541_client-server-getEndpoints.pcap`

</details>
