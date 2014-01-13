#!/usr/bin/env python
import argparse
import codecs
import logging
import os
from os.path import join
import re
import subprocess
from tempfile import TemporaryFile, NamedTemporaryFile
import sys
import conll09
from common import MATE_DIR, DATA_DIR, OPENNLP_BIN, POS_TAG_MODEL, PARSE_MODEL, OPENNLP_TOOL_JAR
from nltk import wordpunct_tokenize
from subprocess import Popen, PIPE, STDOUT

def tag_sentences(tokenized_sentences):
    tagger_in_file = NamedTemporaryFile(delete=False)
    tagger_out_file = NamedTemporaryFile(delete=False)
    tagger_out_file.close()

    glued_sentences = [u" ".join(sent) for sent in tokenized_sentences]
    tagger_input = u"\n".join(glued_sentences).lower().encode('utf-8')

    # logging.info("Tagging {} sentences".format(len(tokenized_sentences)))
    # p = Popen([OPENNLP_BIN, 'POSTagger', POS_TAG_MODEL],
    #           stdout=PIPE, stdin=PIPE) # , stderr=STDOUT

    tagger_in_file.write(u"\n".join(glued_sentences).lower().encode('utf-8'))
    tagger_in_file.close()

    java_cmd = "java -Dfile.encoding=UTF8 -Xmx1024m -jar {}".format(OPENNLP_TOOL_JAR)

    cmd = "{java_cmd} POSTagger {model} < {in_file} > {out_file}".format(
        java_cmd=java_cmd, model=POS_TAG_MODEL, in_file=tagger_in_file.name, out_file=tagger_out_file.name
    )
    logging.info("Tagging with {}".format(cmd))
    subprocess.check_call(cmd, shell=True)

    with codecs.open(tagger_out_file.name, encoding='utf-8') as tagger_out_file2:
        tagged_lines = [l.strip() for l in tagger_out_file2]
        for tokens, tag_pairs in zip(tokenized_sentences, tagged_lines):
            tags = [pair.split("_")[-1] for pair in tag_pairs.split(" ")]
            yield zip(tokens, tags)

    os.remove(tagger_in_file.name)
    os.remove(tagger_out_file.name)

parser = argparse.ArgumentParser(description="Parses Danish sentence-delimited text")
parser.add_argument('in_file', help="File in one-sentence-per-line format")
parser.add_argument('out_file', help="Parsed output in CONLL09 format")
args = parser.parse_args()

logging.basicConfig(format='%(asctime)s : %(levelname)s : %(message)s', level=logging.INFO)

tokenized_sentences = []
for line in codecs.open(args.in_file, encoding='utf-8'):
    tokens = wordpunct_tokenize(line)
    # tokens = map(unicode.lower, tokens)
    tokenized_sentences.append(tokens)

parser_input_fname = args.in_file + '.conll'
with codecs.open(parser_input_fname, 'w', encoding='utf-8') as parser_input_file:
    for sent_i, tagged_tokens in enumerate(tag_sentences(tokenized_sentences)):
        if sent_i > 0:
            print >>parser_input_file, ""
        for token_i, (token, tag) in enumerate(tagged_tokens, 1):
            # 0:ID 1:FORM 2:LEMMA 3:PLEMMA 4:POS 5:PPOS 6:FEAT 7:PFEAT 8:HEAD 9:PHEAD 10:DEPREL
            # 11:PDEPREL 12:FILLPRED 13:PRED 14:APREDs
            conll_columns = [u'_'] * 14
            conll_columns[0] = unicode(token_i)
            conll_columns[1] = token
            conll_columns[5] = tag
            print >>parser_input_file, u"\t".join(conll_columns)

logging.info("Parsing {}".format(parser_input_fname))

# ~/code/esict_parse/model/ddt-universal.pos < /var/folders/px/dbxzlfxd1rj4ftscc1sp7lph0000gp/T/tmplFtjqC

subprocess.check_call(['java', '-Xmx6G',
                       '-cp', join(MATE_DIR, 'anna-3.3.jar'),
                       'is2.parser.Parser',
                       '-model', PARSE_MODEL,
                       '-test', parser_input_fname,
                       '-out', args.out_file])

print "Cleaning up"
os.remove(parser_input_fname)