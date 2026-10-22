"""Decoder for the practice save format, written from REA/Ghidra evidence only."""
import struct, sys

def fnv1a(b):
    h = 0x811C9DC5
    for x in b:
        h = ((h ^ x) * 0x01000193) & 0xFFFFFFFF
    return h

def unscramble(b, key=0x5A):
    out = bytearray()
    for x in b:
        out.append(x ^ key)
        key = (key * 5 + 3) & 0xFF
    return bytes(out)

def decode(data):
    magic, version, length = struct.unpack_from("<IHH", data, 0)
    assert magic == 0x5356574B, hex(magic)
    body = unscramble(data[8:8 + length])
    (crc,) = struct.unpack_from("<I", data, 8 + length)
    assert fnv1a(body) == crc, "checksum mismatch"
    hunger, thirst, health, day = struct.unpack_from("<fffi", body, 0)
    n = body[16]; name = body[17:17 + n].decode()
    p = 17 + n; count = body[p]; p += 1
    slots = [struct.unpack_from("<HH", body, p + 4 * i) for i in range(count)]
    return dict(version=version, hunger=hunger, thirst=thirst, health=health, day=day, name=name, slots=slots)

for path in sys.argv[1:]:
    print(path, decode(open(path, "rb").read()))
