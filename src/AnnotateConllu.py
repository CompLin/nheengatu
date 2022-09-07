#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Author: Leonel Figueiredo de Alencar
# Last update: August 31, 2022

from Nheengatagger import getparselist
from BuildDictionary import extract_feats
from conllu.models import Token,TokenList

# Case of second class pronouns
CASE="Gen"

UDTAGS={'PL': 'Plur', 'SG': 'Sing',
'V': 'VERB', 'N': 'NOUN', 'V2': 'VERB',
'A': 'ADJ', 'ADVR': 'ADV', 'ADVS': 'ADV',
'ADVL': 'ADV', 'A2': 'VERB', 'PUNCT' : 'PUNCT',
'ADP' : 'ADP', 'CONJ' : 'C|SCONJ', 'PRON2' : 'PRON',
'REL' : 'PRON', 'NFIN' : 'Inf'}

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

def getudtag(tag):
    udtag=UDTAGS.get(tag)
    if udtag:
        return udtag
    else:
        return tag.upper()

def mkConlluToken(word,entry,head=0, deprel=None, start=0, ident=1, deps=None):
    end=start + len(word)
    feats={}
    token=Token()
    token['id']=ident
    token['form']=word
    token['lemma']=entry['lemma']
    pos=entry.get('pos')
    if pos:
        token['upos']=getudtag(pos)
        token['xpos']=pos
    person=entry.get('person')
    number=entry.get('number')
    vform=entry.get('vform')
    rel=entry.get('rel')
    if person:
        feats['Person']=person
        if token['upos']=='VERB':
            feats['VerbForm']='Fin'
    if number:
        feats['Number']=getudtag(number)
    if vform:
        feats['VerbForm']=getudtag(vform)
    if rel:
        feats['Rel']=rel.title()
    if feats:
        token['feats']=feats
    else:
        token['feats']=None
    token['head']=head
    upos=token['upos']
    if upos == 'VERB':
        token['deprel']='root'
    elif upos == 'PUNCT':
        token['deprel']='punct'
    else:
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

def sortDict(d):
    l=list(d.items())
    l.sort()
    return dict(l)

def sortTokens(tokenlist):
    for token in tokenlist:
        for k,v in token.items():
            if isinstance(v, dict) and len(v) > 1:
                token[k]=sortDict(v)

def VerbIdsList(tokenlist):
    return tokenlist.filter(upos="VERB")

def FirstVerbId(tokenlist):
    verbs=VerbIdsList(tokenlist)
    if verbs:
        return verbs[0]['id']
    return 0

def addFeatures(tokenlist):
    i=0
    c=len(tokenlist) -1
    while(i < c) :
        token=tokenlist[i]
        nextToken=tokenlist[i+1]
        upos=token['upos']
        if upos == 'PRON':
            if token['xpos'] == 'REL':
                token['feats'].update({'PronType': 'Rel'})
            else:
                token['feats'].update({'PronType': 'Prs'})
            if token['xpos'] == 'PRON2':
                token['feats'].update({'Case': CASE})
                if nextToken['upos'] == 'NOUN':
                    token['feats'].update({'Poss': 'Yes'})
                    token['deprel'] ='nmod'
                    token['head'] =nextToken['id']
        if upos in ('NOUN','PRON'):
            if nextToken['upos'] == 'ADP':
                token['deprel'] = 'obl'
                token['head'] = FirstVerbId(tokenlist)
                nextToken['deprel']='case'
                nextToken['head'] =token['id']
            elif nextToken['upos'] == 'ADJ' and upos == 'NOUN':
                nextToken['deprel']='amod'
                nextToken['head'] =token['id']
            elif nextToken['upos'] == 'VERB' and not token['deprel']:
                token['deprel'] = 'nsubj'
                token['head'] =nextToken['id']
            else:
                if not token['xpos'] == 'PRON2' and not token['deprel']:
                    verbid=FirstVerbId(tokenlist)
                    tokenid=token['id']
                    if verbid < tokenid:
                        token['deprel'] = 'obj'
                        token['head'] = verbid
        elif upos == "VERB":
            if nextToken['upos'] == 'VERB':
                nextToken['upos']= 'AUX'
                nextToken['deprel']='aux'
                nextToken['head']=token['id']
            elif nextToken['upos'] == 'NOUN':
                nextToken['deprel']='obj'
                nextToken['head']=token['id']
            else:
                verbs=VerbIdsList(tokenlist)
                if len(verbs) > 1:
                    if verbs[-1]['id'] == token['id']:
                        token['head'] = verbs[0]['id']
                        token['deprel'] = 'advcl'
        elif upos == "SCONJ":
            token['deprel'] = 'mark'
            tokid=token['id']
            verbs=VerbIdsList(tokenlist)
            if tokid > 0:
                if tokenlist[tokid-1]['lemma'] == 'ti':
                    for verb in verbs:
                        verbid=verb['id']
                        if verbid > tokid:
                            token['head']=verbid
                            break
                else:
                    j=-1
                    while(j >= -len(verbs)) :
                        verbid=verbs[j]['id']
                        if verbid < token['id']:
                            token['head']= verbid
                            break
                        j=j-1
        if nextToken['upos'] == 'PUNCT':
            nextToken['head']=FirstVerbId(tokenlist)
        i+=1

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
    addFeatures(tokenlist)
    sortTokens(tokenlist)
    return tokenlist
