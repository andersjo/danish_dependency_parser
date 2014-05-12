#!/usr/bin/python
# -*- coding: utf-8 -*-
__author__ = 'alonso'


class ParsedToken:
    def __init__(self, index, form, lemma, POS,FULLPOS, featdict, head, label):
        self.index = index
        self.form = form
        self.lemma = lemma
        self.POS = POS
        self.FULLPOS = FULLPOS
        self.featdict = featdict
        self.head = head
        self.label = label



    def __str__( self ):
        return "\t".join([self.index, self.form, self.POS,self.FULLPOS, self.head, self.label])
    def isHeadword(self):
        return self.form.endswith("**") and self.form.startswith("**")

class ParsedSentence():

    def __init__(self):
        self.tokens = []
        self.sentenceid = ""
        self.headword = ""
        self.lang = ""

    def addToken(self,index, form, lemma, POS,FULLPOS,featdict, head, label):
        self.tokens.append(ParsedToken(index, form, lemma, POS,FULLPOS,featdict, head, label))

    def headwordIndex(self):
        for i in range(len(self.tokens)):
            if self.tokens[i].isHeadword():
                return i
        return -1
    def headwordToken(self):
        return self.tokens[self.headwordIndex()]


    def forms(self):
        return [t.form for t in self.tokens]

    def lemmas(self):
        return [t.lemma for t in self.tokens]

    def postags(self):
        return [t.POS for t in self.tokens]

    def feats(self):
        return ["-".join(t.featdict.keys()) for t in self.tokens]


    def getHead(self,tokenindex): #not the index on the tokens() array, but the index attribute of the Token class
        tok = ""
        for t in self.tokens:
            if t.index == tokenindex:
                tok = t
                break
        for t in self.tokens:
            if t.index == tok.head:
                return t
        return ParsedToken( 0,"","","","","",0,"root")

    def getChildren(self,tokenindex): #not the index on the tokens() array, but the index attribute of the Token class
        children = []
        for t in self.tokens:
            if t.head == tokenindex:
                children.append(t)
        return children

    def getPathToRoot(self,index):
        pathtoroot = []
        while self.getHead(index).label != "root":
            index = self.getHead(index).index
            pathtoroot.append(index)
        return pathtoroot



    def convertDanishToNormal(self):
        #this function changes the dependency tree of the sentence wtr to headness of articles
        #in the original Danish treebank, nouns are headed by article and the article bears the noun's role (Sb, Obj)
        #1) input example before conversion
        #1 paa 0
        #2 det 1
        #3 danske 2
        #4 hold 2
        #2) desired output
        #1 paa 0
        #2 det 4
        #3 danske 3
        #4 hold 2
        for t in self.tokens:
            if t.POS.lower().startswith("n") and (self.getHead(t.index).POS in ["PO","PD","AC","PI"] or self.getHead(t.index).POS=="AN" and self.getHead(t.index).lemma.lower() in ["sådan","hel","al"]): #a noun headed by a determiner or a predeterminer
                article = self.getHead(t.index)
                noun = t
                #reassign head of the noun's siblings to the noun, false positives will occur but it is better than the previous thing
                for s in self.getChildren(noun.head) :
                    s.head = noun.index
                noun.head = article.head
                noun.label = article.label
                #reassing NP-headedness to the noun by swapping head and label with article
                article.head = noun.index
                article.label = noun.label


    def __str__(self):
        return self.sentenceid+":"+self.lemmas()

