#!/usr/bin/env python3
"""S7comm PLC simulator for the S7comm data-block lab.

The marker sits in DB1 at byte offset 32. The rest of the block looks like a
small process image so the read returns plausible controller data, not a single
obvious string.
"""
import ctypes
import time

from snap7.server import Server
from snap7.types import srvAreaDB

FLAG = "OCR{s7c0mm_db_r34d_3xp0s3d}"

db1 = bytearray(256)

# A small process image: setpoints, status words, and counters.
db1[0:8] = (72.5).hex().encode().ljust(8, b"\x00")[:8]
db1[8:10] = (1450).to_bytes(2, "big")
db1[10:12] = (0x0001).to_bytes(2, "big")

# Analyst marker at the documented offset.
marker = FLAG.encode("ascii")
db1[32:32 + len(marker)] = marker

server = Server()
# python-snap7 expects a ctypes buffer; a plain bytearray has no ctypes size.
db1_buffer = (ctypes.c_char * len(db1)).from_buffer_copy(db1)
server.register_area(srvAreaDB, 1, db1_buffer)
server.start(102)

print("HIC-S7 PLC S7comm server listening on 0.0.0.0:102", flush=True)

while True:
    time.sleep(3600)
