# coding: utf-8
import codecs
from collections import defaultdict
import os
from xml.sax.saxutils import escape

from common import DATA_DIR


map_filename = os.path.join(DATA_DIR, 'da-sto.map')
map_pairs = [line.strip().split("\t") for line in codecs.open(map_filename, encoding='utf-8')]
STO_UNIVERSAL_MAP = dict(map_pairs)

ambiguity_map = defaultdict(set)
for line in codecs.open(os.path.join(DATA_DIR, 'sto/orig/STOposUTF8'), encoding='utf-8'):
    form, lemma, pos = line.strip().split("\t")
    universal_pos = STO_UNIVERSAL_MAP[pos]
    if universal_pos in ('ADJ', 'ADP', 'ADV', 'CONJ', 'NOUN', 'PRON', 'VERB', 'X'):
        ambiguity_map[form].add(universal_pos)

def clean_token(token):
    # Weird character that ends up in the file
    token = token.replace(u'\x1b', '')
    token = token.lower()
    return escape(token)

print u"""<?xml version="1.0" encoding="UTF-8"?>
<dictionary case_sensitive="false">"""

for form, tags in ambiguity_map.items():
    print u"""
    <entry tags="{tags}">
        <token>{token}</token>
    </entry>""".format(token=clean_token(form), tags=" ".join(tags))
print u"</dictionary>"