#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Author: Leonel Figueiredo de Alencar
# Last update: October 10, 2022

from Nheengatagger import tagSentence

# immediate left context of a noun (tags provided by Juliana Gurgel)
CONTEXT={'A','ART','DEMX','DEMS','IND','NUM','PRON','PROPN'}

def disambiguate(sent):
    tagged=[('#BEGIN','@BG')]
    tagged.extend(tagSentence(sent))
    tagged.append(('#END','@END'))
    i=1
    while(i < len(tagged)-1):
        previous=set(tagged[i-1][1].split('+'))
        next=set(tagged[i+1][1].split('+'))
        word=tagged[i][0]
        tags=set(tagged[i][1].split('+'))
        if len(tags) > 1:
            if 'N' in tags:
                if previous.issubset(CONTEXT):
                    tagged[i]=(word,'N')
            if 'A' in tags:
                if 'N' in previous or 'N' in next:
                    tagged[i]=(word,'A')
                # if ... TODO: context
            if 'ADV' in tags:
                pass # TODO: if-rule
            if 'ART' in tags:
                if next.issubset({'N'}):
                    tagged[i]=(word,'ART')
                else:
                    tagged[i]=(word,'FRUST')
        i+=1
    return tagged[1:-1]

def test():
    sent='Nhaã apigawa uwasemu yepé sumuara kunhã.'
    print(tagSentence(sent))
    print(disambiguate(sent))
