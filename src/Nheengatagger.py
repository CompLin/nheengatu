#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Author: Leonel Figueiredo de Alencar
# Last update: May 30, 2022

import os, sys, string, json, datetime

USER=os.path.expanduser("~")
PATH=os.path.join(USER,"complin/nheengatu/data")
LEXICON=os.path.join(PATH,"lexicon.json")
PUNCTUATION='''.,;':?!—“”"…()][}{'''
OPERATOR="Leonel Figueiredo de Alencar"
MESSAGE=f"""'''Automatically POS-tagged by Nheengatagger.
Operator: {OPERATOR}.
Date: {datetime.datetime.now().strftime("%c")}.
Metadata of the original corpus file reproduced below.'''
"""
NAMES=['antônio', 'barra', 'catarina', 'maria', 'miguel',
'paulo', 'pedro', 'rute', 'são', 'tefé', 'josé', 'joana']

def propernames(namelist=NAMES):
    dic={}
    for name in namelist:
        dic[(name,)]={'PROPN'}
    return dic

def includePunctuation(punctuation=PUNCTUATION):
    punctdict={}
    tagSet=set()
    tagSet.add("PUNCT")
    punctlist=list(punctuation)
    for punct in punctlist:
        punctdict[(punct,)]=tagSet
    return punctdict

def extractWordTag(entry):
    word, parse = entry.split("\t")
    pos = parse.split("+")[1]
    return f"{word} {pos}"

def extractLines(infile="lexicon.txt"):
    return [extractWordTag(line.strip()) for line in open(infile,"r").readlines() if line.strip() != ""]

def makeDictionary(lines):
    dictionary=dict()
    for line in lines:
        stringlist=line.split()
        token=tuple(stringlist[:-1])
        tag=stringlist[-1]
        tags=set()
        if dictionary.get(token):
            dictionary[token].add(tag)
        else:
            tags.add(tag)
            dictionary[token]=tags
    return dictionary

def extractMWEs(dictionary):
    mwe = dict()
    for k in dictionary.keys():
        if len(k) == 2:
            first=k[0]
            second=k[1]
            if mwe.get(first):
                mwe[first].append(second)
            else:
                mwe[first]=[second]
    return mwe

def convertDictionary(dic):
    tagger={}
    for word,parses in dic.items():
        tags=set()
        for parse in parses:
            pos=parse[1].split('+',1)[0]
            tags.add(pos)
        tagger[tuple(word.split())]=tags
    return tagger

def buildDictionary(infile="lexicon.json"):
    tagger={}
    if infile.endswith("json"):
        with open(infile) as f:
            tagger = convertDictionary(json.load(f))
    else:
        tagger=makeDictionary(extractLines(infile))
    tagger.update(includePunctuation())
    tagger.update(propernames())
    return tagger

DICTIONARY=buildDictionary(LEXICON)
MWE=extractMWEs(DICTIONARY)

def splitPunctuation(token,punctuation=PUNCTUATION):
    tokenlist=[]
    tokenlist.append(token[-1])
    i=-2
    while(i > -len(token)):
        char=token[i]
        if char in punctuation:
            tokenlist.append(char)
        else:
            tokenlist.append(token[:i+1])
            break
        i=i-1
    tokenlist.reverse()
    return tokenlist

def tokenize(sentence,mwe=MWE,mwe_sep=" "):
    tokenList=sentence.split()
    includeLast=True
    newList=[]
    i=0
    while(i < len(tokenList)-1):
        thisToken=tokenList[i]
        lastchar=thisToken[-1]
        firstchar=thisToken[0]
        if firstchar in PUNCTUATION:
            newList.append(firstchar)
            thisToken=thisToken[1:]
        if lastchar in PUNCTUATION:
            newList.extend(splitPunctuation(thisToken))
        else:
            wordList=mwe.get(thisToken)
            if wordList:
                nextToken=tokenList[i+1]
                if nextToken in wordList:
                    newList.append(f"{thisToken}{mwe_sep}{nextToken}")
                    tokenList.pop(i+1)
                else:
                    if nextToken[-1] in PUNCTUATION and nextToken[:-1] in wordList:
                        newList.append(f"{thisToken}{mwe_sep}{nextToken[:-1]}")
                        newList.append(nextToken[-1])
                        tokenList.pop(i+1)
                        if i == len(tokenList)-1:
                            includeLast=False
                    else:
                        newList.append(thisToken)
            else:
                newList.append(thisToken)
        i+=1
    if includeLast:
        lastToken=tokenList[-1]
        lastchar=lastToken[-1]
        if lastchar in PUNCTUATION:
            newList.extend(splitPunctuation(lastToken))
        else:
            newList.append(lastToken)
    return newList

def tagWord(token,tagger=DICTIONARY):
    return tagger.get(tuple(token.split()))

def pprint(tagged, tagsep="/", tokensep=" "):
    for token,tag in tagged:
        print(f"{token}{tagsep}{tag}",end=tokensep)
    print()

def tagSentence(sentence,tagger=DICTIONARY, unknown="???"):
    tagged=[]
    tokens=tokenize(sentence)
    for token in tokens:
        tagString=unknown
        tagSet=tagWord(token.lower())
        if tagSet:
            tagString="+".join(sorted(tagSet))
        else:
            if tokens.index(token) > 0 and token.istitle():
                tagString="PROPN"
        tagged.append((token,tagString))
    return tagged

def tagText(lines):
    include=True
    for line in lines:
        line=line.strip()
        if line.startswith("'''"):
            include=False
            print(line)
        elif line.endswith("'''"):
            include=True
            print(line)
        else:
            if include:
                if line.startswith("#"):
                    print(line)
                else:
                    if line:
                        pprint(tagSentence(line))
                    else:
                        print()
            else:
                print(line)


def main(infile):
    print(MESSAGE)
    lines=[]
    with open(infile) as f:
        lines=f.readlines()
    tagText(lines)

if __name__ == "__main__":
        main(sys.argv[1])
