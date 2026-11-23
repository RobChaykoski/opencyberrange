# Cyber-physical CTF pack

Status: **proposed challenge pack**, 100% virtual. No SDR, USB-CAN adapter,
physical PLC, drone, satellite dish, or radio transmission is required.

The pack uses the platform's normal per-session network and service names. Do
not hardcode a subnet such as `<session-subnet>`; the range allocates one `/24`
per session. Coordinates and identifiers below are synthetic.

## Scoring

| Challenge | Domain | Points |
|---|---|---:|
| Ghost Horizon | GNSS / navigation warfare | 300 |
| Blackout on the Grid | ICS / SCADA substation | 400 |
| Silent Orbit | Satellite telemetry / CCSDS | 300 |
| **Total** | | **1,000** |

Flags are `OCR{...}` in the platform lab and `<flag_n>` in the public CTF
template. The private flag store holds the real values.

## Challenge 1: Ghost Horizon (GNSS spoofing)

**Objective:** make a simulated UAV accept a false position and trigger its
geofence, without touching the signed command link.

**Hosted environment (default):**

```text
attacker (pymavlink / Python)
        |
        v  MAVLink UDP
uav-sim (flight state, EKF, geofence, telemetry)
```

The UAV signs its command link but accepts unsolicited `GPS_INPUT` or `HIL_GPS`
messages. Students:

1. Receive `HEARTBEAT`, `GLOBAL_POSITION_INT`, and `GPS_RAW_INT`.
2. Identify the GPS source and the EKF state.
3. Inject a false position at a controlled ramp, not a sudden teleport.
4. Observe the geofence/failsafe transition.
5. Read the flag from the `STATUSTEXT` diagnostic.

**Advanced option (still no hardware):** replace the MAVLink injection with a
GNU Radio + ZeroMQ loopback and `gps-sdr-sim` using a bundled synthetic
ephemeris. The "transmitter" and "receiver" are flowgraphs on the same host.
This is CPU-heavy and course-only; it is not required for the CTF.

**Do not:** transmit RF, use real GNSS data, target a real aircraft, or use real
coordinates. Use `10.0000, 20.0000` and `11.0000, 21.0000` as clearly
synthetic range points.

## Challenge 2: Blackout on the Grid (ICS/SCADA)

**Objective:** stop a simulated transformer overload by finding a rogue PLC
routine, tripping the safety breaker, and then fixing the logic.

**Hosted environment (default):**

```text
attacker (browser / curl / pymodbus)
        |
        v  Modbus/TCP
plc-sim (holding registers, coils, process model)
        |
        v
hmi (read-only dashboard + alarm panel)
```

Use the maintained pymodbus PLC simulator and a lightweight HMI. OpenPLC v4 was
evaluated and deferred because the runtime image exposes no Modbus registers
without an editor-generated program ZIP; OpenPLC v3 is archived. ScadaBR is a
legacy Java/Tomcat stack and is optional, pinned, and course-only, not a hosted
dependency.

Students:

1. Enumerate the Modbus unit and map holding registers and coils.
2. Read transformer temperature, load, and breaker state.
3. Identify the rogue write that keeps the cooling loop off.
4. Trip the safety breaker with the correct coil sequence.
5. Capture the flag from the HMI diagnostic and write the rollback/allowlist
   recommendation.

**Do not:** connect to a real PLC, write to a live process, or use real utility
names or coordinates. The process is a synthetic model.

## Challenge 3: Silent Orbit (satellite telemetry)

**Objective:** exploit a weak ground-station command path, recover the flag, and
then make the same command fail with signing and an allowlist.

**Hosted environment (default):**

```text
ground (command composer, telemetry view, audit)
        |
        v  virtual CCSDS link
flight-sim (command table, mode manager, telemetry, fault injection)
```

No SDR or live downlink is used. Students:

1. Decode CCSDS telemetry and identify the APID and command sequence.
2. Replay a legitimate command with a stale sequence number.
3. Abuse the missing command authentication to change the mode or dump a log.
4. Read the flag from the synthetic telemetry response.
5. Enable command signing and an allowlist; prove the replay is rejected.

**Do not:** transmit to a satellite, use live telemetry, or send a real command.

## Instructor key

| Challenge | Expected artifact | Flag |
|---|---|---|
| Ghost Horizon | `GPS_INPUT`/`HIL_GPS` injection followed by a geofence `STATUSTEXT` | `<flag_1>` |
| Blackout on the Grid | Modbus register/coil map, breaker trip, HMI diagnostic | `<flag_2>` |
| Silent Orbit | CCSDS APID/sequence map, replayed command, signed-command rejection | `<flag_3>` |

The public answer key contains no real flag values. Load the private values from
the flag store before a cohort runs.

## Safety and legal

- No RF transmission, no spectrum use, no SDR hardware.
- No real vehicle, drone, satellite, PLC, or utility.
- No real coordinates, facility names, or personal data.
- Rate-limit fuzzing and command injection.
- The labs are training simulations, not field procedures.

## Implementation order

1. **Ghost Horizon:** MAVLink simulator, telemetry/command API, GPS injection,
   geofence state, workbook, CTF template.
2. **Blackout on the Grid:** pymodbus process model, HMI, Modbus map, breaker
   sequence, evidence rubric.
3. **Silent Orbit:** CCSDS packet simulator, ground-station API, replay and
   signing controls.
4. Optional advanced: GNU Radio/ZeroMQ GNSS loopback; OpenPLC/ScadaBR pinned
   course-only target.

Every lab follows
[`PUBLICATION-METADATA-POLICY.md`](PUBLICATION-METADATA-POLICY.md): flags live
only in the lab definition/runtime, and public docs use placeholders.
