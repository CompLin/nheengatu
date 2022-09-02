#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Author: Leonel Figueiredo de Alencar
# Last update: August 31, 2022

from Nheengatagger import getparselist
from conllu.models import Token,TokenList

UDTAGS={'PL': 'Plur', 'SG': 'Sing',
'V': 'VERB', 'N': 'NOUN', 'V2': 'VERB',
'A': 'ADJ', 'ADVR': 'ADV', 'ADVS': 'ADV',
'ADVL': 'ADV', 'A2': 'VERB', 'PUNCT' : 'PUNCT'}

def tokenrange(sentence):
    m=0
    for token in sentence.split():
        if not token.endswith("."):
            n=m+len(token)
            print(token,m,n)
            m=n+1
        else:
            token=token[:-1]
            n=m+len(token)
            print(token,m,n)
            print(".",n,n+1)

def mkConlluToken(word,entry,head=0, deprel='nsubj', start=0, ident=1, deps=None):
    end=start + len(word)
    feats={}
    token=Token()
    token['id']=ident
    token['form']=word
    token['lemma']=entry['lemma']
    pos=entry.get('pos')
    if pos:
        token['upos']=UDTAGS[pos]
        token['xpos']=pos
    person=entry.get('person')
    number=entry.get('number')
    rel=entry.get('rel')
    if person:
        feats['Person']=person
    if number:
        feats['Number']=UDTAGS[number]
    if rel:
        feats['Rel']=rel.title()
    token['feats']=feats
    token['head']=head
    token['deprel']=deprel
    token['deps']=deps
    token['misc']={'TokenRange': f'{start}:{end}'}
    return token

def handleSpaceAfter(tokenlist):
	s={'SpaceAfter' : 'No'}
	tokens=tokenlist.filter(upos='PUNCT')
	if tokens:
		for token in tokens:
			token['misc'].update(s)
			precedent=tokenlist.filter(id=token['id']-1)[0]
			precedent['misc'].update(s)

def mkConlluSentence(tokens):
    tokenlist=TokenList()
    ident=1
    start=0
    for token in tokens:
        parselist=getparselist(token.lower())
        entries=extract_feats(parselist)
        for entry in entries:
            if entry.get('pos') == 'PUNCT':
                start=start-1
            t=mkConlluToken(token,entry,start=start, ident=ident)
            tokenlist.append(t)
            start=start+len(token)+1
            ident+=1
    handleSpaceAfter(tokenlist)
    return tokenlist
