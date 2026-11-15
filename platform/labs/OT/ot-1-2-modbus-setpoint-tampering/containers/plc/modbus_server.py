#!/usr/bin/env python3
"""Modbus TCP server simulating a process controller with a writable setpoint.

Register map (holding registers, function code 0x03/0x06):

    10  temperature setpoint (starts at 20)
    11  measured temperature (updated by the simulation loop)
    12  alarm threshold (200)
    13  pump speed percentage
    40  maintenance marker (empty until the safety interlock trips)

Coils:

    0   pump run command
    1   alarm

Writing a setpoint of 250 or more trips the safety interlock: the pump stops,
the alarm raises, the measured temperature reports a fault, and the controller
writes a maintenance marker into registers 40 and up. The point of the
exercise is that the write needs no authentication.
"""
import threading
import time

from pymodbus.datastore import (
    ModbusSequentialDataBlock,
    ModbusServerContext,
    ModbusSlaveContext,
)
from pymodbus.device import ModbusDeviceIdentification
from pymodbus.server import StartTcpServer

FLAG = "OCR{m0dbu5_wr1t3_c0ntr0l}"
TRIP_SETPOINT = 250
ALARM_THRESHOLD = 200

HOLDING_COUNT = 128
COIL_COUNT = 64

SETPOINT = 10
MEASURED = 11
ALARM = 12
PUMP_SPEED = 13
MARKER = 40

LOCK = threading.Lock()


def initial_holding_registers():
    values = [0] * HOLDING_COUNT
    values[SETPOINT] = 20
    values[MEASURED] = 20
    values[ALARM] = ALARM_THRESHOLD
    values[PUMP_SPEED] = 60
    # Decoys: a plausible block of config/counter values above the marker.
    decoys = {
        20: 0x0001,
        21: 0x00C8,
        22: 0x1234,
        30: 0x00FA,
        31: 0x0F0F,
        32: 0xABCD,
    }
    for address, value in decoys.items():
        values[address] = value
    return values


store = ModbusSlaveContext(
    di=ModbusSequentialDataBlock(0, [0] * HOLDING_COUNT),
    co=ModbusSequentialDataBlock(0, [False] * COIL_COUNT),
    hr=ModbusSequentialDataBlock(0, initial_holding_registers()),
    ir=ModbusSequentialDataBlock(0, [0] * HOLDING_COUNT),
)
context = ModbusServerContext(slaves=store, single=True)


def read_holding(address, count=1):
    return store.getValues(3, address, count)


def write_holding(address, values):
    store.setValues(3, address, values)


def write_coil(address, values):
    store.setValues(1, address, values)


def process_loop():
    """Simulate the process and trip the interlock on an unsafe setpoint."""
    state = {"tripped": False, "tick": 0}
    while True:
        time.sleep(1)
        state["tick"] += 1
        with LOCK:
            setpoint = read_holding(SETPOINT)[0]
            if setpoint >= TRIP_SETPOINT and not state["tripped"]:
                state["tripped"] = True
                write_coil(0, [False])
                write_coil(1, [True])
                write_holding(MEASURED, [999])
                write_holding(PUMP_SPEED, [0])
                write_holding(MARKER, [ord(char) for char in FLAG])
                print(
                    "Safety interlock tripped: setpoint "
                    f"{setpoint} outside safe range",
                    flush=True,
                )
                continue
            if state["tripped"]:
                continue
            # Settle the measured value toward the setpoint with a small
            # oscillation so a write has a visible effect on the process.
            drift = (state["tick"] % 5) - 2
            measured = max(0, min(998, setpoint + drift))
            write_holding(MEASURED, [measured])
            write_coil(0, [setpoint < TRIP_SETPOINT])
            write_coil(1, [setpoint >= ALARM_THRESHOLD])


identity = ModbusDeviceIdentification()
identity.VendorName = "Halcyon Industrial Controls"
identity.ProductCode = "HIC-PLC-2400"
identity.VendorUrl = "https://halcyon-industrial.example"
identity.ProductName = "Process Controller"
identity.ModelName = "HIC-2400"
identity.MajorMinorRevision = "2.4.1"


if __name__ == "__main__":
    threading.Thread(target=process_loop, daemon=True).start()
    print("HIC-2400 PLC Modbus TCP server listening on 0.0.0.0:502", flush=True)
    StartTcpServer(context=context, identity=identity, address=("0.0.0.0", 502))
