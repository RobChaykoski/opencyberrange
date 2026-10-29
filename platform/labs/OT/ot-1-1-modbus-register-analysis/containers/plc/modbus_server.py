#!/usr/bin/env python3
"""Modbus TCP server simulating a small industrial PLC.

The flag is stored as ASCII in holding registers 0..N (one character per
register). A handful of decoy registers and a coil bank make the device look
like a real controller. Students enumerate the register map with mbpoll or
pymodbus and decode the marker.
"""
import time

from pymodbus.server import StartTcpServer
from pymodbus.datastore import ModbusSequentialDataBlock, ModbusSlaveContext, ModbusServerContext
from pymodbus.device import ModbusDeviceIdentification

FLAG = "OCR{m0dbu5_r3g15t3r5_r3v34l3d}"

# Holding registers: flag chars (one per register) followed by decoy values.
hr_values = [ord(c) for c in FLAG] + [0x0000, 0x1234, 0xABCD, 0x00FF, 0x0F0F]
# Pad to a round 64 registers.
hr_values += [0x0000] * (64 - len(hr_values))

store = ModbusSlaveContext(
    di=ModbusSequentialDataBlock(0, [0] * 64),
    co=ModbusSequentialDataBlock(0, [False] * 64),
    hr=ModbusSequentialDataBlock(0, hr_values),
    ir=ModbusSequentialDataBlock(0, [0] * 64),
)
context = ModbusServerContext(slaves=store, single=True)

identity = ModbusDeviceIdentification()
identity.VendorName = "Halcyon Industrial Controls"
identity.ProductCode = "HIC-PLC-2400"
identity.VendorUrl = "https://halcyon-industrial.example"
identity.ProductName = "Process Controller"
identity.ModelName = "HIC-2400"
identity.MajorMinorRevision = "2.4.1"

if __name__ == "__main__":
    print("HIC-2400 PLC Modbus TCP server listening on 0.0.0.0:502", flush=True)
    StartTcpServer(context=context, identity=identity, address=("0.0.0.0", 502))