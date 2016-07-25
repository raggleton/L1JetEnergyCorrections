#!/usr/bin/env python

"""
Convert human-readable LUT to machine-readable MIF format.

Adapted from code by Thomas Strebler/Olivier Davignon

Usage:
    python mif_maker.py <lut.txt> <output.mif>
"""


import sys


def lut_to_mif(args=sys.argv[1:]):
    with open(args[0]) as lut, open(args[1], 'w') as mif:
        lines = (line for line in lut if not line.startswith('#') and line != '')
        ints = (int(line.split()[1].strip()) for line in lines)
        hexs = (hex(x).lstrip('0x').upper() for x in ints)
        for h in hexs:
            mif.write('0x' + h.rjust(5, '0') + '\n')  # ensure 5 chars long


if __name__ == "__main__":
    sys.exit(lut_to_mif())
