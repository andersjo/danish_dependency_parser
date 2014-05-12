#!/usr/bin/env python
import argparse
import codecs
import logging

parser = argparse.ArgumentParser(description="Remaps the POS tags of a CONLL file according to the given mapping")
parser.add_argument('input', help="Input file in CONLL format")
parser.add_argument('mapping', help="Skip training of the parser")
args = parser.parse_args()

logging.basicConfig(format='%(asctime)s : %(levelname)s : %(message)s', level=logging.INFO)

pos_map = dict(line.strip().split("\t") for line in codecs.open(args.mapping, encoding='utf-8'))

for line in codecs.open(args.input, encoding='utf-8'):
    line = line.strip()
    if line != '':
        parts = line.split("\t")
        cpos = parts[3]
        pos = parts[4]

        new_pos = pos_map.get(cpos, "*NONE*")
        parts[3] = new_pos
        parts[4] = new_pos

        print "\t".join(parts)

    else:
        print ''