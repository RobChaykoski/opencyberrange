# IoT Security: Reference Map

!!! note "Reference map, not an assessed lab"
    This page collects public references and study questions. It has no platform
    flag. Use external tools only on devices you own or have written permission
    to test.

## Why IoT is different

IoT and embedded systems combine constraints that are less common in a normal
web application:

- long device lifetimes and irregular patch cycles;
- default or shared credentials;
- constrained CPU, memory, and power;
- firmware that is difficult to inspect or verify;
- exposed network services and weak discovery protocols;
- physical access and debug interfaces;
- privacy-sensitive sensors and telemetry;
- safety consequences when a device controls a physical process.

The security question is not only "can an attacker reach the service?" It is
also "what happens to the people and processes around the device when they do?"

## Topic map

| Topic | What to review | Public reference |
|---|---|---|
| Architecture and attack surface | Device, gateway, cloud, mobile app, and update path | [OWASP IoT Top 10](https://owasp.org/www-project-internet-of-things/), [ITSAP.00.012](https://www.cyber.gc.ca/en/guidance/internet-things-iot-security-itsap00012) |
| Default and weak credentials | Unique per-device credentials, first-boot rotation, no shared admin account | [OWASP IoT Top 10](https://owasp.org/www-project-internet-of-things/) |
| Network services | Unnecessary listeners, debug ports, discovery protocols, plaintext management | [NIST SP 800-213](https://csrc.nist.gov/publications/detail/sp/800-213/final) |
| Firmware analysis | Extract, identify components, check hard-coded secrets, verify update signatures | [Attify firmware-analysis-toolkit](https://github.com/attify/firmware-analysis-toolkit), [OWASP IoTGoat](https://github.com/OWASP/IoTGoat) |
| Update integrity | Signed updates, rollback protection, secure boot, key custody | [NIST SP 800-213](https://csrc.nist.gov/publications/detail/sp/800-213/final) |
| Privacy | Data minimisation, retention, consent, local versus cloud processing | [ENISA IoT guidelines](https://www.enisa.europa.eu/topics/iot-and-smart-infrastructure) |
| Incident response | Containment without breaking safety controls, evidence capture, recovery | [CISA ICS advisories](https://www.cisa.gov/ics-advisories) |

## Reference labs and tools

These are external projects. Check the licence, pin a reviewed version, and use
them only in an isolated environment.

- [OWASP IoTGoat](https://github.com/OWASP/IoTGoat) and its
  [challenge guide](https://github.com/OWASP/IoTGoat/wiki/IoTGoat-challenges) -
  deliberately vulnerable firmware for learning.
- [Attify firmware-analysis-toolkit](https://github.com/attify/firmware-analysis-toolkit) -
  firmware extraction and emulation helpers.
- [EXPLIOT](https://expliot.io/open-source-framework/) - IoT and embedded
  exploitation framework.
- [HomePWN](https://github.com/Telefonica/HomePWN) - IoT penetration-testing
  toolkit.
- [Hacking Printers wiki](http://hacking-printers.net/wiki/index.php?title=Main_Page) -
  printer and multifunction-device security reference.

Do not redistribute firmware, tool code, or challenge material without a
compatible licence. A repository with no licence is not usable. A link is not an
endorsement.

## Safe practice rules

1. Use a device you own or have written permission to test.
2. Keep the device on an isolated network with no route to production systems.
3. Do not test radio, Bluetooth, or printer features where they can affect
   other people or devices.
4. Capture evidence before changing firmware or configuration.
5. Keep credentials, device identifiers, and sensor data out of public notes.
6. Stop if a test could affect a safety function, a real user, or a device you
   do not control.

## Analysis questions

1. Why is a default credential more dangerous on an Internet-facing device than
   on a workstation behind a managed gateway?
2. What does a signed firmware update prove, and what does it not prove?
3. How would you review an IoT device's update path without breaking its
   rollback protection?
4. Which network services would you expect on a printer, and which are
   unnecessary?
5. Why does firmware emulation require caution even when the firmware is
   obtained lawfully?
6. What evidence would you preserve before replacing a device's firmware?
7. How does the Purdue model change incident response in an OT environment?

## Platform status

There is no dedicated IoT track or assessed IoT lab yet. This page is a
reference map for the OT, Forensics, and Web chapters. A future track should use
original targets and flags, a reviewed licence for any third-party firmware, and
a live harness run before it is published.
