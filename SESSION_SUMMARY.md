# OT/IoT Lab Prompts - OpenCyberRange

## Modbus Fundamentals (CH_OT01)

### Lab 1.1: Modbus Register Analysis — Prompt Questions

**1. Service Discovery**
- What command would you use to discover Modbus TCP services on the network?
- What nmap flags are essential for identifying Modbus-capable devices?
- How does the Modbus Protocol ID field (set to 0) help distinguish Modbus TCP from other protocols?

**2. Register Reading**
- Function code 0x03 (Read Holding Registers) returns data in what format?
- If a register contains the value 0x0041, what single ASCII character does it represent?
- Why might two different registers need to be combined to form a 32-bit integer or IEEE 754 floating-point value?

**3. ASCII Decoding**
- In the walkthrough Python script, how are register values converted to ASCII characters?
- What condition must a register value satisfy to be considered a valid ASCII printable character?
- Why might the flag be split across multiple registers, and how would you reconstruct the full text?

**4. Security Implications**
- Why is Modbus considered "insecure by design"?
- What are the risks of exposing Modbus port 502 to untrusted networks?
- How could an attacker use Modbus register reads to gather intelligence about a industrial control system?
- What defensive controls would you recommend for a Modbus deployment?

**5. Troubleshooting**
- Connection refused: What are the three most likely causes?
- Gibberish output: How does byte-order (endianness) affect register interpretation?
- mbpoll not found: What alternative Python libraries or raw socket methods can read Modbus registers?

### Lab 1.2: (Planned) Modbus Write single register

**Prompt:** A malicious insider attempts to write to a holding register to disrupt the process line. 
- Function code 0x06 writes a single register. What ethical concerns surround unauthorized writes?
- If you could monitor all register writes in real-time, what anomaly detection rules would you implement?
- How would you respond if a write changed a safety-critical setpoint without authorization?

### Lab 1.3: (Planned) Modbus Industrial Gateway

**Prompt:** Your organization has a Modbus TCP-to-SNMP gateway. 
- What additional attack surface does the gateway introduce?
- How would you validate that the gateway properly filters/modifies Modbus data?
- What logging and alerting would you configure for gateway-mediated register reads?

### Lab 1.4: (Planned) Modbus TCP Encapsulation

**Prompt:** A capture file shows Modbus TCP frames with unexpected Unit IDs.
- What is the purpose of the Unit ID field in a Modbus TCP MBAP header?
- How would you investigate a Modbus session where Unit IDs jump between 1, 10, and 255?
- What might mismatched Unit IDs indicate about network segmentation or proxy interference?

### Lab 1.5: (Planned) Modbus Anomaly Detection

**Prompt:** You are building an anomaly detection system for Modbus traffic.
- What baseline metrics would you track (e.g., register access frequency, unusual function codes, time-of-day patterns)?
- How would you distinguish between legitimate operational changes (e.g., a scheduled setpoint change) and malicious reconnaissance?
- What threshold levels would trigger alerts for your environment?

---

## OT Security Concepts — Quick Reference

| Topic | Key Point |
|-------|-----------|
| **Modbus Authentication** | None. Any client can read/write any registered address. |
| **Modbus Encryption** | None. Traffic is cleartext. Use TLS/DTLS gateways if needed. |
| **Common Function Codes** | 0x01 Coils, 0x02 Discrete Inputs, 0x03 Holding Registers, 0x04 Input Registers, 0x05/0x06 Single Write |
| **Register Addressing** | 0-based or 1-dependent depending on implementation; always verify the device's mapping |
| **Broadcast Writes** | Function code 0xFF (or 0x05/0x06 with unit ID 0) writes to all devices on the network — use with extreme caution |
| **Typical Attack Vectors** | — Register read for reconnaissance (motor status, tank levels, PID values) — Register write to disrupt process (over-speed motor, open/close valve) — DMA/chaos attacks via broadcast writes — PLC firmware extraction via crafted PDUs |
| **Defensive Controls** | — Network segmentation (OT VLAN, separate switch) — Firewall rules restricting port 502 to known SCADA IPs — IDS/IPS signatures for Modbus function codes — Unidirectional gateways for critical data flows — Read-only gateways for monitoring only — Network traffic normalization and anomaly detection |

---

## OT/IoT Lab Design Principles

### 1. Safety First
- All OT labs use **simulated** devices (Python Modbus servers, RangeBox PLC emulators, Inetsim)
- **Never** write to real controller registers unless explicitly authorized and supervised
- Labs are designed for **read-only** analysis unless the exercise explicitly calls for write operations

### 2. Reproducibility
- Each lab has a deterministic flag hidden in register values or device responses
- Flag format: `OCR{...}` — same format across all labs
- Lab environments can be rebuilt from container definitions

### 3. Progressive Complexity
- **CH_OT01 L1**: Modbus discovery, register reading, ASCII decode
- **CH_OT01 L2**: (Planned) Write handling, anomaly detection, gateway analysis
- **CH_OT01 L3**: (Planned) Multi-protocol industrial networks, Modbus+TCP+DNP3+ICMP correlation
- **CH_OT01 L4**: (Planned) Real-time monitoring, IDS alerts, incident response scenario
- **CH_OT01 L5**: (Planned) Comprehensive assessment — multi-vector OT incident

### 4. Learn-by-Doing
- Each lab includes **hands-on commands** (mbpoll, python3 socket, nmap -sV)
- **Analysis questions** require critical thinking about security implications
- **Defensive takeaways** translate to real-world OT security practice

### 5. Measurable Outcomes
- Student can discover a Modbus TCP service via network scanning
- Student can read holding registers using command-line or Python tools
- Student can decode ASCII or structured data stored across registers
- Student can articulate at least three security risks of unprotected Modbus
- Student can recommend at least two defensive controls for OT network segmentation

---

## Prompt File Structure (Recommended)

If you want to store lab prompts as separate files, the following structure is recommended:

```
Workbook/CH_OT01_Modbus_Fundamentals/prompts/
    01_register_analysis.txt    # Prompt questions for Lab 1.1
    02_write_single.txt         # Prompt questions for Lab 1.2 (if enabled)
    03_gateway_analysis.txt     # Prompt questions for Lab 1.3
    04_encapsulation.txt        # Prompt questions for Lab 1.4
    05_anomaly_detection.txt    # Prompt questions for Lab 1.5
    quick_reference.md          # OT security quick reference table
    troubleshooting_guide.md    # Common issues and fixes
```

**Example prompt file content** (`01_register_analysis.txt`):

```
# OT01-L1: Modbus Register Analysis — Prompt Questions

## Discovery
1. What nmap command discovers Modbus TCP services? What does the `-sV` flag do?
2. Why is Protocol ID = 0 significant in a Modbus TCP MBAP header?

## Reading Registers
1. Function code 0x03 returns data in big-endian format. Explain how you would read register 40001 to get the value at memory address 0.
2. If register values are [0x0041, 0x0042], what ASCII string do they form? What if the order is reversed?

## Security Analysis
1. List three types of information an attacker could gather by reading Modbus registers.
2. Why is "security by obscurity" particularly dangerous in OT environments?
3. What legal/ethical considerations apply when scanning industrial networks you don't own?

## Defensive Takeaways
1. Recommend two network architecture controls for isolating Modbus devices.
2. Describe how a read-only gateway would function in front of a Modbus PLC.
3. What monitoring alerts would you configure for after-hours register writes?
```

---

## Integration with Existing Workbook

The prompts above can be:
- **Placed as separate `.txt` files** in the lab directory alongside `01_Modbus_Register_Analysis.md`
- **Included as annexes** at the end of the markdown chapter
- **Used as instructor-led discussion questions** during live workshop sessions
- **Exportable to LMS** as quiz questions or assignment prompts

Would you like me to:
1. Create the `prompts/` directory with the prompt files listed above?
2. Add the prompt questions as annexes at the end of the existing `01_Modbus_Register_Analysis.md`?
3. Create a different set of prompts focused on a specific OT/IoT topic (DNP3, IEC 60870-5, OPC UA, etc.)?
4. Create a troubleshooting guide for common Modbus lab issues?