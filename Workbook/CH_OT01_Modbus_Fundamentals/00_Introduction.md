# OT01: Modbus Fundamentals

<!-- BEGIN GENERATED CHAPTER POSITION -->
!!! note "Curriculum position"
    **Chapter:** `OT01` — Modbus Fundamentals
    **Prerequisites:** `NET00` — Network Foundations
    **Recommended next:** `OT02` — S7comm and PLC Data Blocks
<!-- END GENERATED CHAPTER POSITION -->

## Industrial Protocols and the Analyst

Operational technology (OT) networks run the physical world: water, power,
manufacturing. They use protocols designed decades ago for reliability, not
security. Modbus TCP is the most common: no authentication, no encryption,
and a 16-bit register model that anyone on the network can read or write.

This chapter starts with the protocol itself, then moves to the write path and
the gateways that try to control it. You will enumerate a simulated process
controller, read its registers, change a setpoint, and bypass a write filter
that checks only one function code.

---

## What You Will Learn

- Discover a Modbus TCP service and identify the device
- Read holding registers and coils with mbpoll and raw Python
- Decode ASCII stored in consecutive registers
- Write a register and observe the process change
- Explain why a gateway must inspect every write function code
- Record the device identity and register layout

---

## Connection Details

| Exercise | Evidence | What you pull |
|----------|----------|---------------|
| 1.1 | PLC (offset 60) | Modbus TCP on port 502, read-only |
| 1.2 | PLC (offset 60) | Setpoint write and interlock marker |
| 1.3 | Gateway (offset 60) | Gateway allow-list bypass and marker |

---

## Safety Note

Modbus has no authentication. Treat every register read as potentially
sensitive and every write as potentially dangerous. The writes in this chapter
target a simulated controller only. Never write to a real controller.

## Scanning a Real OT Network

A PLC or RTU is not a server. Before you scan anything outside this lab:

1. Get written authorization for the range, ports, window, and stop condition.
2. Discover with an ARP sweep first: `nmap -sn -PR <subnet>`.
3. Slow it down: `--scan-delay 5s --max-parallelism 1`.
4. Scan only the protocol port you need: 502 Modbus, 102 S7, 44818 EtherNet/IP,
   20000 DNP3.
5. Identify with `modbus-discover`, `s7-info`, `enip-info`, or `dnp3-info`; do
   not run exploit or write probes during discovery.

The full procedure, including stop conditions, is in
[OT/ICS scanning safety](https://github.com/RobChaykoski/opencyberrange/blob/main/docs/OT-SCANNING-SAFETY.md).
