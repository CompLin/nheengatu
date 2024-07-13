#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Author: Leonel Figueiredo de Alencar
# Last update: February 16, 2024

import os, sys, string, json, datetime
from BuildDictionary import extract_feats, loadLexicon, guesser

USER=os.path.expanduser("~")
PATH=os.path.join(USER,"complin/nheengatu/data")
LEXICONFILE=os.path.join(PATH,"lexicon.json")
LEXICON=loadLexicon(LEXICONFILE)
DASHES=['‒', '–', '—','―']
PUNCTUATION='''.,;':?!“”"…()][}{'''
ELLIPSIS='[...]'
XXXX='xxxx'
ELIP='ELIP'
OPERATOR="Leonel Figueiredo de Alencar"
MESSAGE=f"""'''Automatically POS-tagged by Nheengatagger.
Operator: {OPERATOR}.
Date: {datetime.datetime.now().strftime("%c")}.
Metadata of the original corpus file reproduced below.'''
"""
NAMES=['antônio', 'barra', 'catarina', 'maria', 'miguel',
'paulo', 'pedro', 'rute', 'são', 'tefé', 'josé', 'joana',
'jesus', 'kristu', 'deus', 'kurukuí', 'augusto',
'iahuixa', 'buopé','rairú','isana','uauhi', 'uanskẽ',
'porominare', 'poronominare', 'karu', 'kukuí', 'pitiápo']

def propernames(namelist=NAMES):
    dic={}
    for name in namelist:
        dic[(name,)]={'PROPN'}
    return dic

def includePunctuation(punctuation=PUNCTUATION,ellipis=ELLIPSIS,elip=ELIP,dashes=DASHES):
    punctdict={}
    tagSet=set()
    tagSet.add("PUNCT")
    punctlist=list(punctuation)
    punctlist.extend(dashes)
    for punct in punctlist:
        punctdict[(punct,)]=tagSet
    elipSet=set()
    elipSet.add(elip)
    punctdict[(ellipis,)]=elipSet
    return punctdict

def extractWordTag(entry):
    word, parse = entry.split("\t")
    pos = parse.split("+")[1]
    return f"{word} {pos}"

def extractLines(infile="lexicon.txt"):
    return [extractWordTag(line.strip()) for line in open(infile,"r", encoding="utf-8").readlines() if line.strip() != ""]

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
        with open(infile, encoding="utf-8") as f:
            tagger = convertDictionary(json.load(f))
    else:
        tagger=makeDictionary(extractLines(infile))
    tagger.update(includePunctuation())
    tagger.update(propernames())
    return tagger

DICTIONARY=buildDictionary(LEXICONFILE)
MWE=extractMWEs(DICTIONARY)

def splitPunctuation(token,punctuation=PUNCTUATION):
    tokenlist=[]
    c= len(token)
    if c == 1:
        tokenlist.append(token)
    elif c == 2:
        tokenlist.append(token[:-1])
        tokenlist.append(token[-1])
    elif c > 2:
        tokenlist.append(token[-1])
        i=-2
        while(i >= -len(token)):
            char=token[i]
            if char in punctuation:
                tokenlist.append(char)
            else:
                t=token[:i+1]
                if t.startswith('"'):
                    tokenlist.append(t[1:])
                    tokenlist.append(t[0])
                else:
                    tokenlist.append(token[:i+1])
                break
            i=i-1
        tokenlist.reverse()
    return tokenlist

def tokenize(sentence,mwe=MWE,mwe_sep=" ", ellipis=ELLIPSIS, xxxx=XXXX):
    sentence=sentence.replace(ELLIPSIS,XXXX)
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
    restoreEllipsis(newList,ellipis,xxxx)
    return newList

def restoreEllipsis(newList,ellipis,xxxx):
    i=0
    while(i < len(newList)):
        if newList[i] == xxxx:
            newList[i] = ellipis
        i+=1

def tagWord(token,tagger=None):
    if not tagger:
        tagger=DICTIONARY
    tags=tagger.get(tuple(token.split()))
    if not tags:
        parselist=guesser(token,LEXICON)
        tags=set()
        if parselist:
            for parse in parselist:
                if parse:
                    tags.add(parse.get('pos'))
    return tags

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
        sortedlist=[e for e in sorted(tagSet) if e]
        if sortedlist:
            tagString="+".join(sortedlist)
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

def parseWord(word,lexicon=None,infile=LEXICONFILE):
    parselist=getparselist(word,lexicon,infile)
    if parselist:
        for lemma,tags in parselist:
            print(f"{word}\t{lemma}+{tags}")

def extendLexicon(lexicon):
    dictionary={}
    dictionary.update(includePunctuation())
    dictionary.update(propernames())
    for key,value in dictionary.items():
        new=key[0]
        lexicon[new]=[[new,list(value)[0]]]

def getparselist(word,lexicon=None,infile=LEXICONFILE):
    word=word.lower()
    if lexicon:
        lexicon=lexicon
    else:
        lexicon=loadLexicon(infile)
    extendLexicon(lexicon)
    parselist=lexicon.get(word)
    if parselist:
        return parselist
    return [[word,None]]

def main(infile):
    print(MESSAGE)
    lines=[]
    with open(infile, encoding="utf-8") as f:
        lines=f.readlines()
    tagText(lines)

if __name__ == "__main__":
        main(sys.argv[1])
