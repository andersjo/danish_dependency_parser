# coding: utf-8
import argparse
import codecs
from collections import defaultdict
import json
import logging
import os
from os.path import join
from tempfile import NamedTemporaryFile
import subprocess

from common import MATE_DIR, OPENNLP_TOOL_JAR, MODEL_DIR
from tokenize import DanishTokenizer, read_abbrevations


def tag_sentences(tokenized_sentences, model):
    tagger_in_file = NamedTemporaryFile(delete=False)
    tagger_out_file = NamedTemporaryFile(delete=False)
    tagger_out_file.close()

    glued_sentences = [u" ".join(sent) for sent in tokenized_sentences]

    tagger_in_file.write(u"\n".join(glued_sentences).lower().encode('utf-8'))
    tagger_in_file.close()

    java_cmd = "java -Dfile.encoding=UTF8 -Xmx1024m -jar {}".format(OPENNLP_TOOL_JAR)

    cmd = "{java_cmd} POSTagger {model} < {in_file} > {out_file}".format(
        java_cmd=java_cmd, model=join(MODEL_DIR, "{}.pos".format(model)),
        in_file=tagger_in_file.name, out_file=tagger_out_file.name
    )
    logging.info("Tagging with {}".format(cmd))
    subprocess.check_call(cmd, shell=True)

    tagged_sentences = []
    with codecs.open(tagger_out_file.name, encoding='utf-8') as tagger_out_file2:
        tagged_lines = [l.strip() for l in tagger_out_file2]
        for tokens, tag_pairs in zip(tokenized_sentences, tagged_lines):
            tags = [pair.split("_")[-1] for pair in tag_pairs.split(" ")]

            tagged_sentences.append(zip(tokens, tags))

    os.remove(tagger_in_file.name)
    os.remove(tagger_out_file.name)

    assert len(tagged_sentences) == len(tokenized_sentences)
    return tagged_sentences

def parse_sentences(tagged_sentences, model):
    parser_in_file = NamedTemporaryFile(delete=False)
    parser_in_file.close()
    parser_out_file = NamedTemporaryFile(delete=False)
    parser_out_file.close()

    with codecs.open(parser_in_file.name, 'w', encoding='utf-8') as parser_in_utf8:
        # Writing input file
        for sent_i, tagged_tokens in enumerate(tagged_sentences):
            if sent_i > 0:
                print >>parser_in_utf8, ""
            for token_i, (token, tag) in enumerate(tagged_tokens, 1):
                # 0:ID 1:FORM 2:LEMMA 3:PLEMMA 4:POS 5:PPOS 6:FEAT 7:PFEAT 8:HEAD 9:PHEAD 10:DEPREL
                # 11:PDEPREL 12:FILLPRED 13:PRED 14:APREDs
                conll_columns = [u'_'] * 14
                conll_columns[0] = unicode(token_i)
                conll_columns[1] = token
                conll_columns[5] = tag
                print >>parser_in_utf8, u"\t".join(conll_columns)

    # Calling parser
    logging.info("Parsing {}".format(parser_in_file.name))
    subprocess.check_call(['java', '-Xmx6G',
               '-cp', join(MATE_DIR, 'anna-3.3.jar'),
               'is2.parser.Parser',
               '-model', join(MODEL_DIR, "{}.parse".format(model)),
               '-test', parser_in_file.name,
               '-out', parser_out_file.name])

    # Reading output file
    parsed_sentences = []
    with codecs.open(parser_out_file.name, encoding='utf-8') as parser_out_utf8:
        parsed_sentence = defaultdict(list)
        for line in parser_out_utf8:
            line = line.strip()
            if line:
                parts = line.split("\t")
                parsed_sentence['form'].append(parts[1])
                parsed_sentence['pos'].append(parts[5])
                parsed_sentence['head'].append(int(parts[9]))
                parsed_sentence['deprel'].append(parts[11])
            else:
                parsed_sentences.append(dict(parsed_sentence))
                parsed_sentence = defaultdict(list)

        if len(parsed_sentence):
            parsed_sentences.append(parsed_sentence)

    # Cleaning up
    os.remove(parser_in_file.name)
    os.remove(parser_out_file.name)

    assert len(parsed_sentences) == len(tagged_sentences)
    return parsed_sentences


parser = argparse.ArgumentParser(description="Parses Danish sentence-delimited text")
parser.add_argument('in_file', help="Input text. By default the format is plain text, one document per line.")

parser.add_argument('--input-format', help="Format of input text. Default: json", choices=('json',), default='json')
parser.add_argument('--id-field', help="Name of JSON id field. Default: _id", default='_id')
parser.add_argument('--model', help="Prefix of model (in /model subdirectory). Default: ddt-uni", default='ddt-uni')
parser.add_argument('--text-fields', help="Name of JSON text field. Default is: body ", nargs='*', default=['body'])
parser.add_argument('--output-format', help="Format of parsed text. Default: json", choices=('json',), default='json')
parser.add_argument('out_file', help="Parsed output")
args = parser.parse_args()

logging.basicConfig(format='%(asctime)s : %(levelname)s : %(message)s', level=logging.INFO)

tokenizer = DanishTokenizer(read_abbrevations("data/da-abbr.txt"))

all_sentence_ids = []
all_sentences = []
if args.input_format == 'json':
    with codecs.open(args.in_file, encoding='utf-8') as in_file:
        for line in in_file:
            doc = json.loads(line)
            for text_field in args.text_fields:
                text = doc.get(text_field)
                if text:
                    if isinstance(text, list):
                        text = "\n".join(text)
                    sentences = tokenizer.sent_tokenize(text)
                    all_sentences += sentences
                    all_sentence_ids += [(doc.get(args.id_field), text_field)]*len(sentences)


tagged_sentences = tag_sentences(all_sentences, args.model)
parsed_sentences = parse_sentences(tagged_sentences, args.model)
assert len(parsed_sentences) == len(all_sentence_ids)

# Output
with codecs.open(args.out_file, 'w', encoding='utf-8') as out:
    last_doc_id = None

    for sent, sent_id in zip(parsed_sentences, all_sentence_ids):
        doc_id, field = sent_id

        if last_doc_id != doc_id:
            if last_doc_id is not None:
                print >>out, json.dumps(dict(current_doc))
            last_doc_id = doc_id
            current_doc = defaultdict(list)
            current_doc[args.id_field] = doc_id

        parsed_field = "{}_parsed".format(field)
        current_doc[parsed_field].append(sent)

    if len(current_doc):
        print >>out, json.dumps(dict(doc))