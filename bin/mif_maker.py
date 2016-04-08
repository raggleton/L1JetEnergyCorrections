#!/usr/bin/env python

"""
Convert human-readable LUT to machine-readable MIF format.

Adapted from code by Thomas Strebler/Olivier Davignon

Usage:
    python mif_maker.py <lut.txt> <output.mif> <nbits>
"""


import sys


def lut_to_mif(args=sys.argv[1:]):
    with open(args[0]) as lut, open(args[1], 'w') as mif:
        lines = (line for line in lut if not line.startswith('#') and line != '')
        ints = (int(line.split()[1].strip()) for line in lines)
        bins = [bin(x).replace('0b', '') for x in ints]
        nbits = int(args[2])
        for b in bins[:-1]:
            mif.write(b.zfill(nbits) + '\n')
        mif.write(bins[-1].zfill(nbits))  # no newline at end of file


if __name__ == "__main__":
    sys.exit(lut_to_mif())
