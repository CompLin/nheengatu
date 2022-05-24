#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Author: Leonel Figueiredo de Alencar
# Last update: May 19, 2022

import os, sys, string

USER=os.path.expanduser("~")
PATH=os.path.join(USER,"complin/nheengatu/data")
INFILE=os.path.join(PATH,"lexicon.txt")
PUNCTUATION=".,;:?!—"
MESSAGE="""'''Automatically POS-tagged by Nheengatagger.
Metadata of the original corpus file reproduced below.'''
"""

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

def extractLines(infile):
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

DICTIONARY=makeDictionary(extractLines(INFILE))
DICTIONARY.update(includePunctuation())
MWE=extractMWEs(DICTIONARY)

def tokenize(sentence,mwe=MWE,mwe_sep=" "):
    tokenList=sentence.split()
    includeLast=True
    newList=[]
    i=0
    while(i < len(tokenList)-1):
        thisToken=tokenList[i]
        lastchar=thisToken[-1]
        if lastchar in string.punctuation:
            newList.append(thisToken[:-1])
            newList.append(lastchar)
        else:
            wordList=mwe.get(thisToken)
            if wordList:
                nextToken=tokenList[i+1]
                if nextToken in wordList:
                    newList.append(f"{thisToken}{mwe_sep}{nextToken}")
                    tokenList.pop(i+1)
                else:
                    if nextToken[-1] in string.punctuation and nextToken[:-1] in wordList:
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
        if lastchar in string.punctuation:
            newList.append(lastToken[:-1])
            newList.append(lastchar)
        else:
            newList.append(lastToken)
    return newList

def tagWord(token,tagger=DICTIONARY):
    return tagger.get(tuple(token.split()))

def tagSentence(sentence,tagger=DICTIONARY, tagsep="/", tokensep=" "):
    for token in tokenize(sentence):
        tagSet=tagWord(token.lower())
        tagString="PROPN"
        if tagSet:
            tagString="+".join(tagSet)
        print(f"{token}{tagsep}{tagString}",end=tokensep)

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
						tagSentence(line)
						print()
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
