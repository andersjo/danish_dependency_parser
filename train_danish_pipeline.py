#!/usr/bin/env python
import argparse
import codecs
import logging
import os
from os.path import join
import subprocess
import conll09

parser = argparse.ArgumentParser(description="Trains a Danish pipeline for tokenizing, lemmatizing, tagging, and parsing")
parser.add_argument('--no-pos', help="Skip training of the POS tagger", action='store_true')
parser.add_argument('--no-parse', help="Skip training of the parser", action='store_true')
args = parser.parse_args()

logging.basicConfig(format='%(asctime)s : %(levelname)s : %(message)s', level=logging.INFO)

def write_opennlp_tag_file(conll09_fname, tag_fname):
    with codecs.open(conll09_fname, encoding='utf-8') as conll09_file:
        with codecs.open(tag_fname, 'w', encoding='utf-8') as tag_file:
            # opennlp_pos_train_file = codecs.open(join(data_dir, 'opennlp_pos_train.txt'))
            for sentence in conll09.sentences(conll09_file):
                toks = [u"{}_{}".format(form.replace("_", '+').lower(), pos)
                        for form, pos in zip(sentence['form'], sentence['pos'])]
                # print sentence
                # print u" ".join(toks)
                print >>tag_file, u" ".join(toks)

# Setup paths
software_dir = join(os.path.dirname(__file__), 'software')
data_dir = join(os.path.dirname(__file__), 'data')
model_dir = join(os.path.dirname(__file__), 'model')

mate_dir = join(software_dir, 'mate')
opennlp_dir = join(software_dir, 'apache-opennlp-1.5.2')
opennlp_bin = reduce(join, [opennlp_dir, 'bin', 'opennlp'])

pos_tag_model = join(model_dir, 'ddt-universal.pos')
parse_model = join(model_dir, 'ddt-universal.parse')

treebank_train = join(data_dir, 'danish_ddt_train+anna.universal.conll9')
treebank_test = join(data_dir, 'danish_ddt_test.universal.conll9')

tagger_train = join(data_dir, 'danish_ddt_train.universal.tagged')
tagger_test = join(data_dir, 'danish_ddt_test.universal.tagged')

if not args.no_pos:
    write_opennlp_tag_file(treebank_train, tagger_train)
    write_opennlp_tag_file(treebank_test, tagger_test)

    print "Training POS tagger"
    subprocess.check_call([opennlp_bin, 'POSTaggerTrainer',
                           '-dict', join(data_dir, 'opennlp_pos_ambiguity.xml'),
                           '-data', tagger_train,
                           '-lang', 'danish',
                           '-type', 'maxent',
                           '-model', pos_tag_model])

    print "Evaluating POS tagger"
    subprocess.check_call([opennlp_bin, 'POSTaggerEvaluator',
                           '-data', tagger_test,
                           '-model', pos_tag_model])

if not args.no_parse:
    subprocess.check_call(['java', '-Xmx32G',
                           '-cp', join(mate_dir, 'anna-3.3.jar'),
                           'is2.parser.Parser',
                           '-model', parse_model,
                           '-train', treebank_train,
                           '-test', treebank_test,
                           '-eval', treebank_test
                           ])