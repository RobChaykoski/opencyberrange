# OT01: Modbus Fundamentals

<!-- BEGIN GENERATED CHAPTER POSITION -->
!!! note "Curriculum position"
    **Chapter:** `OT01` - Modbus Fundamentals
    **Prerequisites:** `NET00` - Network Foundations
    **Recommended next:** `OT02` - S7comm and PLC Data Blocks
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
