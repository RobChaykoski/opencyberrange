# Exercise 2.1: S7comm Data Block Read

## Before You Begin

- [ ] Launched the exercise and opened the RangeBox desktop
- [ ] A terminal open inside the desktop
- [ ] The **PLC** address from the panel
- [ ] `nmap` and `python3` available (the tester and RangeBox ship `python-snap7`)

---

## Scenario

Halcyon Industrial Controls added a second process line with a Siemens-style
controller. The vendor left the engineering port open on the control network,
and the process data block holds more than setpoints.

S7comm has no built-in authentication. Anyone who can reach TCP 102 can
enumerate the controller and read its data blocks. Confirm the service, read
DB1, and recover the audit marker stored at byte offset 32.

---

## Your Objectives

- Identify an S7comm service on TCP 102
- Connect with a protocol client using rack 0 and slot 1
- Read DB1 and locate the marker at byte offset 32
- Explain the defensive control that removes this path

---

## Background: What a Data Block Is

A PLC stores process data in areas. Inputs and outputs are the physical
signals; flags and timers are internal state; data blocks are the structured
records an application defines. An engineering tool reads and writes those
blocks to commission a line.

S7comm carries those reads over TCP 102. The protocol was designed for a
trusted control network, so it has no user account, no password, and no
per-block authorization. Segmentation and a monitored boundary are the real
controls.

---

## Walkthrough

### Step 1: Confirm the service

!!! target "Probe TCP 102"
    ```bash
    nmap -sV -p 102 <plc_ip>
    ```

    A Siemens-style controller answers on `102/tcp` (`s7comm` or `iso-tsap`).
    If the port is filtered, stop and check the target address in the panel.

### Step 2: Connect with a client

The RangeBox and tester include `python-snap7`.

!!! target "Open an S7 connection"
    ```bash
    python3 -c "import snap7; c=snap7.client.Client(); c.connect('<plc_ip>', 0, 1); print('connected')"
    ```

    Rack 0, slot 1 is the common addressing for a compact controller. A
    connection confirms the controller accepted the session.

### Step 3: Read DB1

!!! target "Read the first 96 bytes of DB1"
    ```bash
    python3 -c "import snap7; c=snap7.client.Client(); c.connect('<plc_ip>', 0, 1); d=c.db_read(1, 0, 96); print(d[:16].hex(' ')); print(d[32:].split(bytes([0]))[0])"
    ```

    The first line shows the process image as hex. The second prints the ASCII
    marker that starts at offset 32 and ends at the first zero byte.

---

**Record Your Findings**

- Which port and service did you find?
- What does the first 16 bytes of DB1 look like in hex?
- What is the marker?
- Why does the controller answer without a password?

---

### Step 4: Explain the control

A student on the lab network reached a process data block with a five-line
client. In a real plant the same path is available to anyone who reaches TCP
102.

!!! target "Write the boundary rule"
    In your notes, state one network control and one monitoring control that
    would have blocked or detected this read. Then compare with the defensive
    takeaways below.

---

## Analysis Questions

**1. S7comm and Modbus both lack authentication. Why is segmentation more important than a strong password here?**

??? note "Reveal Answer"

    There is no account to password. The protocol trusts any client that can
    open a session, so the only enforceable control is reachability: put the
    controller on a control VLAN, block TCP 102 at the boundary, and require a
    broker or VPN for engineering access. A password on an engineering
    workstation does not stop a direct protocol connection.

**2. What makes a data-block read different from a register read in an incident review?**

??? note "Reveal Answer"

    A data block is application-defined, so the same byte range can mean
    setpoints, counters, or production recipes. A register read is easy to
    describe generically; a DB read needs the controller's project file to
    explain exactly what was exposed. That is why the DB number and offset are
    the important evidence to record.

**3. Which detection would you deploy first, and what would it alert on?**

??? note "Reveal Answer"

    Alert on new TCP 102 sessions from hosts outside the engineering subnet,
    then enrich with the source asset owner. Most plants have a very small set
    of legitimate engineering hosts, so a new source is high signal. A second
    rule can alert on DB reads outside a maintenance window.

## Key Takeaways

- S7comm exposes data blocks over TCP 102 with no authentication.
- Rack 0, slot 1 is the common compact-controller address; a successful
  connect is the first proof of exposure.
- Data blocks are application-defined, so record the DB number and offset.
- Segmentation, a monitored boundary, and an engineering-access broker are the
  controls that actually hold.
