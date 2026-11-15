# OT/ICS scanning safety

Industrial devices are not servers. A modern IT host barely notices a port
scan; an old PLC or RTU with a small network stack can stall, drop its
communication task, or fault a process. Treat every scan of a real OT network
as a change to a production system.

The lab targets in this platform are simulated, but use the same procedure so
the habit carries into authorised field work.

## Before you scan

1. **Get written authorization.** Cover the exact address range, the ports and
   scripts allowed, the maintenance window, the on-site contact, and the
   rollback/stop condition. Verbal approval is not enough.
2. **Discover with ARP first.** On the local segment, an ARP sweep is the
   gentlest way to find live devices:
   ```bash
   nmap -sn -PR 10.100.3.0/24
   ```
   ARP does not cross routers. If the devices are not on your segment, ask for
   the asset list instead of sweeping a routed range.
3. **Slow the scan down.** Use a delay between probes and one probe at a time:
   ```bash
   nmap -sT -Pn -p 502 --scan-delay 5s --max-parallelism 1 10.100.3.60
   ```
   Do not use `-T4`, `-A`, `--script vuln`, or full-port sweeps on OT.
4. **Scan only the ports you need.** Common industrial ports:
   | Port | Protocol |
   | --- | --- |
   | 502/tcp | Modbus TCP |
   | 102/tcp | S7comm (Siemens) |
   | 44818/tcp | EtherNet/IP (Allen-Bradley, Omron) |
   | 20000/tcp | DNP3 |
5. **Use the protocol scripts for identification, not exploitation.**
   ```bash
   nmap -sT -Pn -p 502,102,44818,20000 \
     --scan-delay 5s --max-parallelism 1 \
     --script modbus-discover,s7-info,enip-info,dnp3-info \
     10.100.3.60
   ```

## Stop conditions

Abort and tell the on-site contact if any of these happen:

- a controller faults, reboots, or drops its process network;
- a PLC or RTU stops answering after a probe;
- the scan produces communication alarms in the control room;
- you lose the maintenance-window contact.

Do not "finish the range" after a device misbehaves.

## What not to do

- No unauthenticated scanning outside the written scope.
- No `-A`, `-T4`, `-T5`, or default full-port scans.
- No exploit scripts, write probes, or firmware queries during discovery.
- No scanning from a corporate IT network into a control network. Use the
  authorised jump host or the lab network.
- No screenshots or exports that contain live setpoints, credentials, or
  customer identifiers.

## In the labs

The OT exercises run on simulated controllers. The workbooks still ask you to
use ARP discovery, a delay, and a single port, because the point is the
procedure. If a lab instruction gives a faster command, the safe form is the
one to use in the field.

The platform also ships an **OT Scan** tool (Tools in the sidebar, or the button
in a running exercise). It builds the command from a validated address, a fixed
protocol list, and the delay you choose, and keeps the authorisation checklist
in view. It runs offline and does not send a scan.
