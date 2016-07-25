#!/usr/bin/env python

"""
Convert jet LUTs (human readable) into new programmable format
"""


import os
import sys
import argparse
from collections import OrderedDict
import xml.etree.ElementTree as XT
from xml.dom import minidom


SETTINGS = OrderedDict()  # is this necessary?
SETTINGS['jetSeedThreshold'] = 8  # IN HW PT NOT GeV
SETTINGS['jetMaxEta'] = 40  # WHICH ETA???
SETTINGS['HTMHT_maxJetEta'] = 28
SETTINGS['HT_jetThreshold'] = 60
SETTINGS['MHT_jetThreshold'] = 60


def pad_hex(h, length):
    """Ensure hex string is right length and case"""
    return '0x' + h.lstrip('0x').rjust(length, '0').upper()


def hexify_int(i):
    """Convert integer to hex string, with fixed length (not incl. 0x) & case"""
    return pad_hex(hex(i), length=5)


# Used to handle conversions
TYPE_DICT = {
    type(1): {
        "str": "uint",
        "conversion": hexify_int},
    type([1,2]): {
        "str": "vector:uint",
        "conversion": lambda x: (','.join(['\n' + 3*'  ' + hexify_int(i) for i in x])
                                 + '\n' + 2*'  ')}
}


def get_lut_contents(lut_file):
    """Read in human-readrable LUT, and convert values to list of ints"""
    with open(lut_file) as lut:
        lines = (line for line in lut if not line.startswith('#') and line != '')
        return [int(line.split()[1].strip()) for line in lines]


def do_lut_making(in_args=sys.argv[1:]):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("input", help="Input human readable LUT")
    parser.add_argument("xml", help="Output XML LUT filename")
    args = parser.parse_args(in_args)

    # add JEC lut
    SETTINGS['jetEnergyCalibLUT'] = get_lut_contents(args.input)

    # construct XML
    algo = XT.Element("algo", {"id": "calol2"})
    context = XT.SubElement(algo, 'context', {"id": "MainProcessor"})

    # add actual settings
    for k, v in SETTINGS.iteritems():
        type_str = TYPE_DICT[type(v)]['str']
        attrib_dict = {"id": k, "type": type_str}
        param = XT.SubElement(context, 'param', attrib_dict)
        convert_func = TYPE_DICT[type(v)]['conversion']
        param.text = convert_func(v)

    # write to file
    fcontents = minidom.parseString(XT.tostring(algo)).toprettyxml(indent=2*" ")
    fcontents = fcontents.replace('<?xml version="1.0" ?>\n', "")
    with open(args.xml, 'w') as f:
        f.write(fcontents)


if __name__ == "__main__":
    sys.exit(do_lut_making())
