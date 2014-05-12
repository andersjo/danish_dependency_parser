import argparse
import codecs

parser = argparse.ArgumentParser(description="Convert from CONLL06 to CONLL09 format")
parser.add_argument('input', help="Input file in CONLL06 format")
args = parser.parse_args()

for line in codecs.open(args.input, encoding='utf-8'):
    line = line.strip()
    if line != '':
        (index, form, lemma, cpos, pos, feat, head, deprel, extra1, extra2) = line.split("\t")
        row = ['_'] * 13
        row[0] = index
        row[1] = form
        row[2] = lemma
        row[3] = lemma
        row[4] = cpos
        row[5] = cpos
        row[6] = "pos=" + pos.replace("=", "_")
        row[7] = "pos=" + pos.replace("=", "_")
        row[8] = head
        row[9] = head
        row[10] = deprel
        row[11] = deprel

        print "\t".join(row)

    else:
        print ""
