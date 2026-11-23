# Automotive and aerospace security pathways

Status: **proposed pathway design**. This page defines what the hosted range
can run safely and what belongs in an optional, isolated benchtop guide.

## Why these pathways

- **Automotive:** ISO/SAE 21434 and UN R155/R156 make vehicle cybersecurity a
  lifecycle and type-approval requirement. The skills gap is in CAN bus
  analysis, diagnostics, gateway segmentation, and evidence.
- **Aerospace:** NISTIR 8441, Space Policy Directive-5, and CCSDS practice make
  satellite command integrity, ground-station access, and telemetry provenance
  a growing requirement. The skills gap is in space protocols, flight-software
  command validation, and mission-control audit.

Both domains use the same teaching pattern: map the bus or link, replay a
legitimate message, abuse a trust boundary, then design and prove a control.

## Hosted-range constraint

Hosted labs are unprivileged containers. They do not receive host kernel
modules, USB devices, SDR hardware, or radio spectrum. The following are
therefore **benchtop-only**, not hosted labs:

- `vcan`, `can-utils`, ICSIM, and USB-to-CAN adapters;
- RTL-SDR, HackRF, Ubertooth, and live satellite downlinks;
- any transmission to a real vehicle, satellite, or ground station.

Hosted labs use deterministic userspace simulators instead. This is a safety
and reproducibility decision, not a limitation of the curriculum.

## Automotive pathway

| Module | Title | Level | Minutes | Focus |
|---|---|---|---|---|
| AUTO-01 | CAN Bus Fundamentals | beginner | 90 | arbitration, IDs, DLC, endianness, periodic frames |
| AUTO-02 | Replay and Arbitration Abuse | intermediate | 120 | capture, correlate, replay, door/status spoofing |
| AUTO-03 | UDS Diagnostics and Security Access | intermediate | 150 | sessions, read/write, seed/key, DTCs |
| AUTO-04 | Fuzzing, DTC, and Recovery | advanced | 150 | bounded fuzzing, ECU state, recovery, evidence |
| AUTO-05 | Gateway Segmentation and CAN IDS Capstone | advanced | 180 | gateway policy, allowlist IDS, attack proof, report |

### Hosted lab shape

```text
student browser / terminal
        |
        v
bench service (HTTP + CLI wrappers)
  candump, cansend, canplayer, uds, fuzz
        |
        v  TCP CAN broker (synthetic frames)
ecu-sim service
  engine, door, brake, infotainment, gateway
  UDS server, DTC store, rate limits
```

The simulator owns the vehicle state. Students never actuate a physical device.
The broker is deterministic and rate-limited, so a replay or fuzz run is
repeatable and safe.

### Hardware-optional benchtop

For an isolated bench, not a live vehicle:

```bash
sudo modprobe vcan
sudo ip link add dev vcan0 type vcan
sudo ip link set up vcan0
```

Use `can-utils` (`candump`, `cansend`, `canplayer`), ICSIM, Caring Caribou,
SavvyCAN, and Wireshark with SocketCAN. Use a USB-to-CAN adapter that supports
Linux SocketCAN (CANable, USB2CAN, PCAN-USB). Never fuzz a live vehicle, never
touch a safety-critical bus outside a bench, and isolate powertrain/braking
components.

## Aerospace pathway

| Module | Title | Level | Minutes | Focus |
|---|---|---|---|---|
| AERO-01 | CCSDS Telemetry and Telecommand | beginner | 90 | packet structure, APID, sequencing, checksums |
| AERO-02 | Ground-Station Command Injection and Replay | intermediate | 120 | command auth, replay window, telemetry provenance |
| AERO-03 | cFS Flight Software Command Validation | advanced | 180 | command table, bounds, failure detection, safe mode |
| AERO-04 | Yamcs Mission Control RBAC and Audit | intermediate | 120 | roles, command authorization, audit trail |
| AERO-05 | GNSS/Telemetry Integrity Capstone | advanced | 210 | spoof detection, zero-trust ground station, report |

### Hosted lab shape

```text
student browser / terminal
        |
        v
ground service (HTTP + CLI)
  telemetry view, command composer, replay, audit
        |
        v  virtual CCSDS link (synthetic packets)
flight-sim service
  cFS/NOS3 or lightweight CCSDS simulator
  command table, mode manager, telemetry, fault injection
```

No radio hardware is used. Students work with synthetic telemetry and command
packets, or offline IQ captures supplied as evidence. A real uplink is never in
scope.

### Hardware-optional benchtop

For receive-only study on an isolated bench:

- RTL-SDR or HackRF in receive-only mode;
- GNU Radio and GQRX for flowgraphs and spectrum viewing;
- SatDump and gr-satellites for offline decodes;
- Gpredict for pass planning and Doppler calculation.

Do not transmit, do not interfere with licensed spectrum, and do not send
commands to a real satellite or ground station. Use recorded IQ files and
public telemetry, not live operational links.

## Assessment

Every module requires a flag **and** an evidence artifact:

- automotive: bus map, arbitration notes, replay log, UDS transcript, DTC
  evidence, gateway policy, IDS rule, attack chain, mitigation;
- aerospace: packet map, command transcript, telemetry timeline, authorization
  evidence, fault-injection record, integrity rule, mitigation.

The capstones require a working control, not only an exploit. A student must
prove the attack is blocked or detected after the fix.

## Standards and frameworks

| Domain | Frameworks |
|---|---|
| Automotive | ISO/SAE 21434, UN R155/R156, NIST CSF 2.0, MITRE ATT&CK |
| Aerospace | NISTIR 8441, SPD-5, NIST SP 800-53, CCSDS, MITRE ATT&CK |

## Career mapping

- **Windsor-Essex / St. Clair College:** automotive and Automobility roles.
- **Ottawa:** Telesat Lightspeed, Canadian Space Agency, ground-station and
  mission-security roles.
- **Montreal:** aerospace manufacturing and avionics security.
- **Waterloo:** quantum-safe satellite research and secure communications.

## Implementation order

1. AUTO-01/02: userspace CAN broker, ECU simulator, bench API/CLI, replay
   exercise.
2. AERO-01/02: CCSDS packet simulator, ground-station command API, replay and
   provenance exercise.
3. AUTO-05 and AERO-05 capstones: gateway/IDS and command-authentication
   controls with proof.
4. Benchtop guides: Kali `vcan`/ICSIM and receive-only SDR, clearly separated
   from the hosted range.

## Publication rule

This page uses no real addresses, hostnames, lab flags, or credentials. Any
future lab follows [`PUBLICATION-METADATA-POLICY.md`](PUBLICATION-METADATA-POLICY.md):
flags live only in the lab definition/runtime, and public docs use placeholders.
