#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Author: Leonel Figueiredo de Alencar
# Last update: August 31, 2022

from Nheengatagger import getparselist, tokenize, DASHES
from BuildDictionary import MAPPING,extract_feats, loadGlossary
from conllu.models import Token,TokenList
from conllu import parse
from io import open
from conllu import parse_incr
import re

# Case of second class pronouns
CASE="Gen"

UDTAGS={'PL': 'Plur', 'SG': 'Sing',
'V': 'VERB', 'N': 'NOUN', 'V2': 'VERB',
'A': 'ADJ', 'ADVR': 'ADV', 'ADVS': 'ADV',
'ADVD': 'ADV', 'ADVL': 'ADV', 'A2': 'VERB',
'CONJ' : 'C|SCONJ', 'NFIN' : 'Inf', 'ART' : 'DET',
'AUXN' : 'VERB', 'AUXF' : 'AUX', 'CARD' : 'NUM',
'ORD' : 'ADJ', 'ELIP' : 'PUNCT'}

# TODO: extractDemonstratives()
DET =  {'DEM' : 'DET', 'QUANT' : 'DET',
'INT' : 'DET', 'ART' : 'DET', 'DEMX' : 'DET', 'DEMS' : 'DET',
'IND' : 'DET', 'TOT' : 'DET'}

DEIXIS={'DEMS' : 'Remt', 'DEMX' : 'Prox'}

def extractAuxiliaries(tag='aux.'):
    glossary=loadGlossary()
    auxiliaries=list(filter(lambda x: tag in x.get('pos'),glossary))
    return [auxiliary['lemma'] for auxiliary in auxiliaries]

AUX = extractAuxiliaries()

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
            ud='PRON'
            t=DET.get(v)
            if t:
                ud=t
            dic[v]=ud
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

def decrementRange(r='107:111',i=-1):
	m,n=[int(x) for x in r.split(':')]
	return f"{m-i}:{n-i}"

def decrementTokenRange(tokenlist,i=-1):
    for t in tokenlist:
        value=decrementRange(t['misc']['TokenRange'],i)
        t['misc']['TokenRange']=value

def getudtag(tag):
    udtag=UDTAGS.get(tag)
    if udtag:
        return udtag
    else:
        return tag.upper()

def RelAbbr(rel):
    if rel == 'NCONT':
        return 'NCont'
    return rel.title()

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
    else:
        token['upos']=None
        token['xpos']=None
    upos=token['upos']
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
        feats['Rel']=RelAbbr(rel)
        handleNcont(upos,feats)
    if feats:
        token['feats']=feats
    else:
        token['feats']=None
    token['head']=head
    if upos == 'VERB':
        token['deprel']='root'
    elif upos == 'PUNCT':
        token['deprel']='punct'
    else:
        token['deprel']=deprel
    token['deps']=deps
    token['misc']={'TokenRange': f'{start}:{end}'}
    return token

def spaceBefore(token):
    if token['xpos'] == 'ELIP' or token['lemma'] in DASHES:
        return True

def handleSpaceAfter(tokenlist):
    FinalPunct=('.','?','!')
    s={'SpaceAfter' : 'No'}
    tokens=tokenlist.filter(upos='PUNCT')
    if tokens:
        for token in tokens:
            if not spaceBefore(token):
                precedentlist=tokenlist.filter(id=token['id']-1)
                for precedent in precedentlist:
                    precedent['misc'].update(s)
                if token['lemma'] in FinalPunct:
                    token['misc'].update(s)

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

def TokensOfCatList(tokenlist,cat):
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
            token['deprel'] ='nmod:poss'
            token['head'] =nextToken['id']

def handleNounPron(token,nextToken, verbs,verbid):
    if nextToken['upos'] == 'ADP':
        token['deprel'] = 'obl'
        headid = previousVerb(token,verbs)
        token['head'] = headid
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
            token['deprel'] = 'nsubj'

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
    if nextToken['upos'] == 'NOUN': # TODO: possibly deprecated
        nextToken['deprel']='obj'
        nextToken['head']=token['id']
    elif nextToken['upos'] == 'SCONJ':
        token['deprel'] = 'advcl'
        headid = previousVerb(token,verbs)
        token['head'] = headid
    """else: # TODO:
        if len(verbs) > 1:
            if verbs[-1]['id'] == token['id']:
                token['head'] = verbs[0]['id']
                token['deprel'] = 'advcl'
                """

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

def handleDetNum(upos,token,tokenlist):
    deprel={'DET': 'det', 'NUM': 'nummod'}
    Pron='Pron'
    if upos == 'NUM':
        Pron='Num'
    token['deprel']=deprel.get(upos)
    nouns=TokensOfCatList(tokenlist,'NOUN')
    nounid=nextCat(token,nouns)
    tokenid=token['id']
    if nounid - tokenid > 2:
        token['head']=getNextWord(token,tokenlist)['id']
    else:
        token['head']=nounid
    xpos=token['xpos']
    value=xpos.title()
    deixis=DEIXIS.get(xpos)
    if deixis:
        updateFeats(token,'Deixis',deixis)
        value=value[:3]
    updateFeats(token,f'{Pron}Type',value)
    if token['feats'].get('PronType') == 'Art':
        updateFeats(token,'Definite','Ind')

def getNextToken(token, tokenlist):
    for t in tokenlist:
        if t['form'] != token['form']:
            return t

def getNextWord(token, tokenlist):
    start=tokenlist.index(token)
    i=start + 1
    while (i < len(tokenlist)):
        t=tokenlist[i]
        if t['upos'] != 'PUNCT' and t['form'] != token['form']:
            return t
        i+=1


def handleAux(tokenlist):
    verbs=VerbIdsList(tokenlist)
    c=len(verbs)
    if c == 1:
        if verbs[0]['lemma'] == 'ikú':
            verbs[0]['deprel'] = 'cop'
            # handleNonVerbalRoot()
    elif c > 1:
        for verb in verbs:
            lemma=verb['lemma']
            if lemma in ('sú','puderi','putari'):
                headid=nextVerb(verb,verbs)
                verb['upos'] = 'AUX'
                verb['deprel'] = 'aux'
                verb['head'] = headid
            elif lemma == 'ikú':
                headid=previousVerb(verb,verbs)
                verb['upos'] = 'AUX'
                verb['deprel'] = 'aux'
                verb['head'] = headid
            else:
                pass # TODO: ccomp, xcomp, advcl

def handleNcont(upos,feats):
    if feats['Rel'] == 'Ncont':
        if upos == 'VERB':
            feats.update({'Number':'Sing',
            'Person' : '3',
            'VerbForm' : 'Fin'})
        elif upos == 'NOUN':
            feats.update({'Number[psor]':'Sing',
            'Person[psor]' : '3'})

def AdjRoot(tokenlist):
    adjs=TokensOfCatList(tokenlist,'ADJ')
    if adjs:
        root=adjs[-1]
        root['head']=0
        root['deprel']='root'

def GenitiveConstruction(tokenlist):
    nouns=TokensOfCatList(tokenlist,'NOUN')
    #TODO

def handlePunct(token,nextToken, tokenlist,verbs):
    if nextToken['lemma'] == ",":
        nextToken['head'] = nextVerb(token,verbs)
    elif nextToken['xpos'] == 'ELIP':
         updateFeats(nextToken,'PunctType','Elip')
         nextToken['head'] = previousVerb(nextToken,verbs)
    else:
        nextToken['head']=FirstVerbId(tokenlist)

def addFeatures(tokenlist):
    i=0
    c=len(tokenlist) -1
    handleAux(tokenlist)
    verbid=FirstVerbId(tokenlist)
    verbs=VerbIdsList(tokenlist)
    if not verbs:
        AdjRoot(tokenlist)
    while(i < c) :
        token=tokenlist[i]
        upos=token['upos']
        #nextToken=tokenlist[i+1]
        nextToken=getNextToken(token, tokenlist[i+1:])
        if upos in ('NOUN','PRON','PROPN'):
            handleNounPron(token,nextToken, verbs,verbid)
            if upos == 'PRON':
                handlePron(token,nextToken)
                if token['xpos'] == 'REL':
                    token['deprel'] = 'nsubj'
                    j= i - 1
                    if j >= 0:
                        previous=tokenlist[j]
                        token['head'] = previous['id']
                        nouns=TokensOfCatList(tokenlist,'NOUN')
                        nounid=previousCat(token,nouns)
                        if nounid:
                            previous['head'] = nounid
                        previous['deprel'] = 'acl:relcl'
        elif upos == "PART":
            handlePart(token,verbs)
        elif upos == "VERB":
            handleVerb(token,nextToken,verbs)
        elif upos == "SCONJ":
            handleSconj(token,tokenlist,verbs)
        elif upos == "ADV":
            handleAdv(token,verbs)
        elif upos in ("DET","NUM"):
            handleDetNum(upos,token,tokenlist)
        if nextToken['upos'] == 'PUNCT': # TODO: sentences without final punctuation
            handlePunct(token,nextToken, tokenlist,verbs)
        i+=1

def mkConlluSentence(tokens):
    tokenlist=TokenList()
    ident=1
    start=0
    for token in tokens:
        tag=''
        if '/' in token:
            token,tag=token.split('/')
        parselist=getparselist(token.lower())
        if tag:
            parselist=list(filter(lambda x: x[1].startswith(tag.upper()),parselist))
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

def extractConlluSents(infile):
    sentences=[]
    data_file = open(infile, "r", encoding="utf-8")
    for tokenlist in parse_incr(data_file):
        sentences.append(tokenlist)
    return sentences

def insertSentId(sent,pref='MooreFP1994',textid=0,sentid=1):
    sent.metadata.update({'sent_id': f'{pref}:{textid}:{sentid}'})
    sent.metadata=sortDict(sent.metadata)

def extract_sents(line=None,lines=None):
    sents=[]
    if lines:
        for sent in text.split("\n"):
            sents.append(sent.strip())
    else:
        sents=[sent for sent in re.split(r"\s+-\s+|[)(]",line) if sent]
    return sents

def ppText(*sents):
    yrl,eng,por=sents[0],sents[1],sents[2]
    template=f"# text = {yrl}\n# text_eng = {eng}\n# text_por = {por}"
    dic={}
    if len(sents) > 3:
        for sent in sents[3:]:
            if sent.startswith('(') and sent.endswith(')'):
                dic['source']=sent[1:-1]
            else:
                dic['orig']=sent
    print(template)
    for k,v in dic.items():
        print(f"# text_{k} = {v}")

def mkText(text):
	ppText(extract_sents(lines=text))

def parseExample(text=None,template=None,sentid=None):
    if not text:
        text='''Aité kwá sera waá piranha yakunheseri
        aé i turususá i apuã waá rupí, asuí sanha
        saimbé yuíri. (Payema, 68, adap.)
        - Este que se chama piranha nós o conhecemos
        por seu formato oval e por seus dentes afiados.
        - This one called piranha we know for its oval shape
        and its sharp teeth.'''.replace('\n','')
        text=re.sub(r"\s+",' ',text)
    sents=extract_sents(text)
    yrl=re.sub(r"[/]\w+",'',sents[0])
    sents[1]=f"({sents[1]})"
    if template and sentid:
        print(f"# sent_id = {template}:{sentid}")
    if len(sents) == 5:
        ppText(yrl,sents[3],sents[2],sents[1],sents[4])
    else:
        ppText(yrl,sents[3],sents[2],sents[1])
    #mkText("\n".join((sents[0],sents[3],sents[2],f"({sents[1]})")))
    tokens=tokenize(sents[0])
    tk=mkConlluSentence(tokens)
    print(tk.serialize())

def writeConlluUD(sentences,outfile,pref='MooreFP1994',textid=0,sentid=1):
    i=0
    textid=textid
    sentid=sentid
    with open(outfile, 'w') as f:
        while(i < len(sentences)):
            sent=sentences[i]
            insertSentId(sent,pref,textid,sentid)
            i+=1
            sentid+=1
            print(sent.serialize(),end='',file=f)
