from collections import defaultdict
from itertools import groupby

def sentence_to_table(raw_sent):
    # CONLL09 (http://ufal.mff.cuni.cz/conll2009-st/task-description.html)
    #   0:ID 1:FORM 2:LEMMA 3:PLEMMA 4:POS 5:PPOS 6:FEAT 7:PFEAT 8:HEAD 9:PHEAD 10:DEPREL 11:PDEPREL 12:FILLPRED 13:PRED 14:APREDs
    columns = "ID FORM LEMMA PLEMMA POS PPOS FEAT PFEAT HEAD PHEAD DEPREL PDEPREL FILLPRED PRED".lower().split(" ")
    table = defaultdict(list)
    for line in raw_sent:
    #            apred_names = ('apred{}'.format(c) for c in count())
    #            row = dict(zip(line.split("\t"), chain(columns, apred_names)))
        # Leave apreds aside for now
        for name, value in zip(columns, line.split("\t")):
            table[name].append(value)

    return table

def sentences(conll_iter):
    current_sent = []
    for line in conll_iter:
        line = line.strip()
        if line == '':
            yield sentence_to_table(current_sent)
            current_sent = []
        else:
            current_sent.append(line)

    if len(current_sent) > 0:
        yield sentence_to_table(current_sent)