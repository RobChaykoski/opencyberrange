# Bundled challenges

The guide at `http://guide.lab` contains 17 challenges that match the captures
on this workstation. Work them in this order:

## Incident captures

| Challenge | Capture(s) |
|---|---|
| `ot-triton-tristation` — TRITON/TRISIS TriStation traffic | `data/nozomi-triton-tristation/malware_exec.pcap` |
| `ot-industroyer2` — Industroyer2 IEC-104 traffic | `data/netresec-industroyer2/Industroyer2-StationAddress1.pcap` (+2, +3) |
| `ot-goose-fdi` — GOOSE false-data injection | `data/goose-false-data-injection/FDI/Attack/FDI_Attack_traffic.pcapng` and `FDI/Clean/clean.pcapng` |

## Protocol library

| Challenge | Protocol |
|---|---|
| `ot-lib-modbus-tcp` | Modbus/TCP |
| `ot-lib-s7comm` | S7comm |
| `ot-lib-s7comm-plus-s7-1200-1500` | S7comm-plus |
| `ot-lib-dnp3` | DNP3 |
| `ot-lib-iec-104` (within the Industroyer2 set) | IEC-104 |
| `ot-lib-bacnet` | BACnet |
| `ot-lib-ethernet-ip-cip` | EtherNet/IP and CIP |
| `ot-lib-profinet` | PROFINET |
| `ot-lib-opc-ua` | OPC UA |
| `ot-lib-hart-ip` | HART-IP |
| `ot-lib-ethercat` | EtherCAT |
| `ot-lib-omni` / `ot-lib-ansi-c12-22` / `ot-lib-c37-118-synchrophasor` / `ot-lib-omron-fins` / `ot-lib-roc-plus` | Additional OT protocols bundled from the CISA ICSNPP traces |

## Suggested workflow

```bash
cd /home/analyst
ls -lh data/*/
tshark -r data/nozomi-triton-tristation/malware_exec.pcap -q -z io,phs
tshark -r data/nozomi-triton-tristation/malware_exec.pcap -q -z conv,udp
tshark -r data/netresec-industroyer2/Industroyer2-StationAddress1.pcap -q -z conv,tcp
tshark -r data/goose-false-data-injection/FDI/Attack/FDI_Attack_traffic.pcapng -Y goose | head
```

Read the guide's **tshark / Wireshark** track for the exact filters and expected
evidence. The computed evidence on each page is the self-check, not a substitute
for running the commands.

## Credits

- Guide and challenge authoring: SackOfHacks/ICS-PCAP-Challenges (MIT).
- TRITON/TRISIS capture: Nozomi Networks Labs (BSD-3-Clause).
- Industroyer2 captures: Netresec / Erik Hjelmvik (CC BY 4.0).
- GOOSE FDI captures: Enache, Stan, Barbulescu (CC BY 4.0).
- CISA ICSNPP test traces and the credited upstream collections (see each
  dataset's `PROVENANCE.md` and `LICENSE-NOTICE.md`).
