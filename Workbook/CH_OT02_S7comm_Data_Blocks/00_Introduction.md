# OT02: S7comm and PLC Data Blocks

<!-- BEGIN GENERATED CHAPTER POSITION -->
!!! note "Curriculum position"
    **Chapter:** `OT02` — S7comm and PLC Data Blocks
    **Prerequisites:** `OT01` — Modbus Fundamentals
    **Recommended next:** `AI01` — AI Security Foundations
<!-- END GENERATED CHAPTER POSITION -->

## From Registers to Data Blocks

Modbus exposes a flat register map. Siemens-style controllers use S7comm, a
binary protocol built around data blocks (DBs). A DB is a named block of bytes
inside the controller: setpoints, counters, status words, and often data that
was never meant to leave the process network.

S7comm has the same core weakness as Modbus: the protocol has no
authentication. If TCP 102 is reachable, a client can connect and read the
data blocks the controller exposes.

This chapter moves from register reads to a data-block read. You will confirm
the service, connect with a protocol client, and recover a marker stored at a
documented byte offset.

---

## What You Will Learn

- Identify an S7comm service on TCP 102
- Connect to a controller with rack 0 and slot 1
- Read a data block and interpret its byte layout
- Explain why engineering ports must be segmented and monitored

---

## Connection Details

| Exercise | Evidence | What you pull |
|----------|----------|---------------|
| 2.1 | PLC (offset 61) | S7comm on port 102 |

---

## Safety Note

This controller is simulated and isolated. Reading a data block is passive, but
on a real process network an unexpected connection to TCP 102 is an incident
signal. Never probe a live controller without written authorization and a
maintenance window.
