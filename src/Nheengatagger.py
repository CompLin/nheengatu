#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Author: Leonel Figueiredo de Alencar
# Date May 4, 2022

import os, sys, string

USER=os.path.expanduser("~")
PATH=os.path.join(USER,"complin/nheengatu/pibic-2020-2021/nheentiquetador/nheentiquetador-2.0")
INFILE=os.path.join(PATH,"sn-yrl-dict.txt")


def extractLines(infile):
    return [line.strip() for line in open(infile,"r").readlines() if line.strip() != ""]

def makeDictionary(lines):
	dictionary=dict()
	for line in lines:
		stringlist=line.split()
		token=tuple(stringlist[:-1])
		tag=stringlist[-1]
		if dictionary.get(token):
			dictionary[token].append(tag)
		else:
			dictionary[token]=[tag]
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
                lastchar=""
                if nextToken[-1] in string.punctuation:
                    lastchar=nextToken[-1]
                for word in wordList:
                    if nextToken == word:
                        newList.append(f"{thisToken}{mwe_sep}{nextToken}")
                        break
                    elif nextToken[:-1] == word and lastchar:
                        newList.append(f"{thisToken}{mwe_sep}{nextToken[:-1]}")
                        newList.append(lastchar)
                        tokenList.pop(i+1)
                        if i == len(tokenList)-1:
                            includeLast=False
                        break
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
        tagList=tagWord(token)
        tagString="???"
        if tagList:
            tagString="+".join(tagList)
        print(f"{token}{tagsep}{tagString}",end=tokensep)

def main(infile):
    for line in extractLines(infile):
        if line.startswith("#"):
            print(line,"\n")
        else:
            tagSentence(line.lower())
            print()

if __name__ == "__main__":
        main(sys.argv[1])
