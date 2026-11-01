#!/usr/bin/env python3
"""Extract the OCRSTEG payload from a PNG's blue-channel LSBs.

Usage:
    python3 extract_lsb.py badge.png

The script uses only the Python standard library, so it runs on a stock Kali
container without Pillow, zsteg, or steghide. It expects an 8-bit RGB/RGBA,
non-interlaced PNG where the payload was written MSB-first into the least
significant bit of the blue channel, row by row.
"""
import struct
import sys
import zlib

MAGIC = b"OCRSTEG"


def read_png_pixels(path):
    with open(path, "rb") as handle:
        data = handle.read()
    if data[:8] != b"\x89PNG\r\n\x1a\n":
        raise ValueError("not a PNG file")

    pos = 8
    idat = bytearray()
    width = height = None
    color_type = None

    while pos + 12 <= len(data):
        length = struct.unpack(">I", data[pos:pos + 4])[0]
        chunk_type = data[pos + 4:pos + 8]
        chunk = data[pos + 8:pos + 8 + length]
        pos += 12 + length

        if chunk_type == b"IHDR":
            width, height, bit_depth, color_type, _, _, interlace = struct.unpack(
                ">IIBBBBB", chunk
            )
            if bit_depth != 8 or color_type not in (2, 6) or interlace != 0:
                raise ValueError(
                    "supported images are 8-bit RGB/RGBA, non-interlaced"
                )
        elif chunk_type == b"IDAT":
            idat.extend(chunk)
        elif chunk_type == b"IEND":
            break

    if width is None:
        raise ValueError("missing IHDR")

    channels = 3 if color_type == 2 else 4
    stride = width * channels
    raw = zlib.decompress(bytes(idat))
    pixels = bytearray()
    previous = bytearray(stride)
    offset = 0

    for _ in range(height):
        filter_type = raw[offset]
        offset += 1
        line = bytearray(raw[offset:offset + stride])
        offset += stride

        if filter_type == 1:  # Sub
            for i in range(channels, stride):
                line[i] = (line[i] + line[i - channels]) & 0xFF
        elif filter_type == 2:  # Up
            for i in range(stride):
                line[i] = (line[i] + previous[i]) & 0xFF
        elif filter_type == 3:  # Average
            for i in range(stride):
                left = line[i - channels] if i >= channels else 0
                line[i] = (line[i] + ((left + previous[i]) >> 1)) & 0xFF
        elif filter_type == 4:  # Paeth
            for i in range(stride):
                left = line[i - channels] if i >= channels else 0
                up = previous[i]
                up_left = previous[i - channels] if i >= channels else 0
                pa = abs(up - up_left)
                pb = abs(left - up_left)
                pc = abs(left + up - 2 * up_left)
                predictor = left if (pa <= pb and pa <= pc) else (up if pb <= pc else up_left)
                line[i] = (line[i] + predictor) & 0xFF
        elif filter_type != 0:
            raise ValueError(f"unknown PNG filter {filter_type}")

        pixels.extend(line)
        previous = line

    return width, height, channels, pixels


def extract(path):
    _width, _height, channels, pixels = read_png_pixels(path)
    bits = [pixels[i + 2] & 1 for i in range(0, len(pixels), channels)]

    decoded = bytearray()
    for i in range(0, len(bits) - 7, 8):
        value = 0
        for bit in bits[i:i + 8]:
            value = (value << 1) | bit
        decoded.append(value)

    marker = decoded.find(MAGIC)
    if marker == -1:
        raise SystemExit("no OCRSTEG payload found in the blue channel")

    length = int.from_bytes(decoded[marker + len(MAGIC):marker + len(MAGIC) + 4], "big")
    payload = decoded[marker + len(MAGIC) + 4:marker + len(MAGIC) + 4 + length]
    print(payload.decode("utf-8", errors="replace"))


if __name__ == "__main__":
    if len(sys.argv) != 2:
        raise SystemExit("usage: python3 extract_lsb.py badge.png")
    extract(sys.argv[1])
