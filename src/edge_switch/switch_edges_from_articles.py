# coding: utf-8
# Author: Hector Alonso Martinez
import argparse
import parsedsentence


class SentenceReader:
    def __init__(self, inputfile):
        self.inputready = inputfile

    def sentences(self):
        stack = parsedsentence.ParsedSentence()
        #for line in codecs.open(self.inputready,"r","utf-8").readlines():
        for line in open(self.inputready).readlines():
            if len(line) < 2:
                stack.convertDanishToNormal()
                yield stack
                stack = parsedsentence.ParsedSentence()
            else:
                (index, form, lemma, POS, FULLPOS, feats, head, label, phead, plabel) = line.strip().split("\t")
                #print form,lemma,POS,feats,head,label
                featsdict = {}
                if feats.find("|") != -1:
                    for feature in feats.split("|"):
                        if feature.find("=") == -1:
                            pass
                        else:
                            (attr, value) = feature.split("=")
                            if attr == "sentenceid":
                                stack.sentenceid = value
                            elif attr == "headword":
                                stack.headword = value
                            else:
                                featsdict[attr] = value
                stack.addToken(index, form, lemma, POS, FULLPOS, featsdict, head, label)


parser = argparse.ArgumentParser(description="""""")
parser.add_argument('infile')
args = parser.parse_args()

reader = SentenceReader(args.infile)
for sentence in reader.sentences():
    for i, t in enumerate(sentence.tokens, 1):
        l = "\t".join([str(i), t.form, t.lemma, t.POS, t.FULLPOS, "_", t.head, t.label, "_", "_"])
        print l
    print
