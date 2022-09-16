#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Author: Leonel Figueiredo de Alencar
# Last update: August 31, 2022

from Nheengatagger import getparselist
from BuildDictionary import MAPPING,extract_feats
from conllu.models import Token,TokenList

# Case of second class pronouns
CASE="Gen"

UDTAGS={'PL': 'Plur', 'SG': 'Sing',
'V': 'VERB', 'N': 'NOUN', 'V2': 'VERB',
'A': 'ADJ', 'ADVR': 'ADV', 'ADVS': 'ADV',
'ADVD': 'ADV', 'ADVL': 'ADV', 'A2': 'VERB',
'CONJ' : 'C|SCONJ', 'NFIN' : 'Inf', 'ART' : 'DET',
'AUXN' : 'VERB', 'AUXF' : 'AUX'}

def extractParticles(mapping):
	dic={}
	for k,v in mapping.items():
		if 'part.' in k:
			dic[v]='PART'
	return dic

def extractPronouns(mapping):
	dic={}
	for k,v in mapping.items():
		if 'pron.' in k:
			dic[v]='PRON'
	return dic

UDTAGS.update(extractParticles(MAPPING))
UDTAGS.update(extractPronouns(MAPPING))

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

def VerbIdsList(tokenlist): # TODO: VerbsList
    return tokenlist.filter(upos="VERB")

def TokensofCatList(tokenlist,cat):
    return tokenlist.filter(upos=cat)

def FirstVerbId(tokenlist):
    verbs=VerbIdsList(tokenlist)
    if verbs:
        return verbs[0]['id']
    return 0

def getprontype(xpos):
    prontype='Prs'
    if xpos not in ('PRON', 'PRON2'):
        prontype=xpos.title()
    return prontype

def handlePron(token,nextToken):
    xpos=token['xpos']
    prontype=getprontype(xpos)
    if not token.get('feats'):
        token['feats']={}
    token['feats'].update({'PronType': prontype})
    if xpos == 'PRON2':
        token['feats'].update({'Case': CASE})
        if nextToken['upos'] == 'NOUN':
            token['feats'].update({'Poss': 'Yes'})
            token['deprel'] ='nmod'
            token['head'] =nextToken['id']

def handleNounPron(token,nextToken, verbid):
    if nextToken['upos'] == 'ADP':
        token['deprel'] = 'obl'
        token['head'] = verbid
        nextToken['deprel']='case'
        nextToken['head'] =token['id']
    elif nextToken['upos'] == 'ADJ' and token['upos'] == 'NOUN':
        nextToken['deprel']='amod'
        nextToken['head'] =token['id']
    elif nextToken['upos'] == 'VERB' and not token['deprel']:
        token['deprel'] = 'nsubj'
        token['head'] =nextToken['id']
    if not token['xpos'] == 'PRON2' and not token['deprel']:
        tokenid=token['id']
        token['head'] = verbid
        if verbid < tokenid:
            token['deprel'] = 'obj'
        else:
            token['deprel'] = 'subj'

def updateFeats(token,feature,value):
    if not token['feats']:
        token['feats']={}
    token['feats'].update({feature : value})

def handlePart(token,verbs):
    #token['feats']={}
    token['deprel'] = 'advmod'
    xpos=token['xpos']
    tokid=token['id']
    if xpos == 'NEG':
        updateFeats(token,'Polarity', 'Neg')
        #token['feats'].update({'Polarity': 'Neg'})
        for verb in verbs:
            verbid=verb['id']
            if verbid > tokid:
                token['head']=verbid
                break
    elif xpos == 'RPRT':
        updateFeats(token,'Evident','Nfh')
        #token['feats'].update({'Evident': 'Nfh'})
        if verbs:
            token['head']=verbs[0]['id']

def handleVerb(token,nextToken,verbs):
    if nextToken['upos'] == 'VERB':
        nextToken['upos']= 'AUX'
        nextToken['deprel']='aux'
        nextToken['head']=token['id']
    elif nextToken['upos'] == 'NOUN':
        nextToken['deprel']='obj'
        nextToken['head']=token['id']
    else: # TODO:
        if len(verbs) > 1:
            if verbs[-1]['id'] == token['id']:
                token['head'] = verbs[0]['id']
                token['deprel'] = 'advcl'

def handleSconj(token,tokenlist,verbs):
    token['deprel'] = 'mark'
    tokid=token['id']
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

def handleAdv(token,verbs):
    token['deprel']='advmod'
    if token['xpos']=='ADVD':
        token['feats']={}
        token['feats'].update({'PronType': 'Dem'})
    token['head']=getHeadVerb(token,verbs)
       
def handleAdv0(token,verbs):
    token['deprel']='advmod'
    if token['xpos']=='ADVD':
        token['feats']={}
        token['feats'].update({'PronType': 'Dem'})
    tokenid=token['id']
    i=-1
    c=-len(verbs)
    while(i >= c):
        verbid=verbs[i]['id']
        if verbid < tokenid:
            token['head']=verbid
            break
        i=i-1

def getHeadVerb(token,verbs):
    headid=previousVerb(token,verbs)
    if headid:
        return headid
    return nextVerb(token,verbs)

def previousVerb(token,verbs):
    tokenid=token['id']
    i=-1
    c=-len(verbs)
    while(i >= c):
        verbid=verbs[i]['id']
        if verbid < tokenid:
            return verbid
        i=i-1
    return 0

def nextVerb(token,verbs):
    tokenid=token['id']
    for verb in verbs:
        verbid=verb['id']
        if verbid > tokenid:
            return verbid
    return 0

def nextCat(token,cats):
    tokenid=token['id']
    for cat in cats:
        catid=cat['id']
        if catid > tokenid:
            return catid
    return 0

def previousCat(token,cats):
    tokenid=token['id']
    i=-1
    c=-len(cats)
    while(i >= c):
        catid=cats[i]['id']
        if catid < tokenid:
            return catid
        i=i-1
    return 0

def handleDem(token,tokenlist):
    token['feats'].update({'PronType': 'Dem'})
    token['deprel']='det'
    nouns=TokensofCatList(tokenlist,'NOUN')
    nounid=nextCat(token,nouns)
    token['head']=nounid

def getNextToken(token, tokenlist):
    for t in tokenlist:
        if t['form'] != token['form']:
            return t

def handleAux(tokenlist):
    verbs=VerbIdsList(tokenlist)
    c=len(verbs)
    if c == 1:
        if verbs[0]['lemma'] == 'ikú':
            verbs[0]['deprel'] = 'cop'
    elif c > 1:
        for verb in verbs:
            lemma=verb['lemma']
            if lemma == 'sú':
                headid=nextVerb(verb,verbs)
                verb['upos'] = 'AUX'
                verb['deprel'] = 'aux'
                verb['head'] = headid
            elif lemma == 'ikú':
                headid=previousVerb(verb,verbs)
                verb['upos'] = 'AUX'
                verb['deprel'] = 'aux'
                verb['head'] = headid

def addFeatures(tokenlist):
    i=0
    c=len(tokenlist) -1
    handleAux(tokenlist)
    verbid=FirstVerbId(tokenlist)
    verbs=VerbIdsList(tokenlist)
    while(i < c) :
        token=tokenlist[i]
        upos=token['upos']
        #nextToken=tokenlist[i+1]
        nextToken=getNextToken(token, tokenlist[i+1:])
        if upos in ('NOUN','PRON'):
            handleNounPron(token,nextToken, verbid)
            if upos == 'PRON':
                handlePron(token,nextToken)
        elif upos == "PART":
            handlePart(token,verbs)
        elif upos == "VERB":
            handleVerb(token,nextToken,verbs)
        elif upos == "SCONJ":
            handleSconj(token,tokenlist,verbs)
        elif upos == "ADV":
            handleAdv(token,verbs)
        elif upos == "DEM":
            handleDem(token,tokenlist)
        if nextToken['upos'] == 'PUNCT':
            if nextToken['lemma'] == ",":
                nextToken['head'] = nextVerb(token,verbs)
            else:
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
