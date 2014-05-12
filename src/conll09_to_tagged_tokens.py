import argparse
import codecs

parser = argparse.ArgumentParser(description="Converts a CONLL06 file to one-sentence-per-line format where tokens have their part of speech as a postfix.")
parser.add_argument('input')
args = parser.parse_args()


tokens = []
for line in codecs.open(args.input, encoding='utf-8'):
    line = line.strip()

    if line != '':
        parts = line.split("\t")
        tokens.append(u"{}_{}".format(parts[1].lower(), parts[4]))
    else:
        print " ".join(tokens)
        tokens = []

if tokens:
    print " ".join(tokens)