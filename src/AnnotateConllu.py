#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Author: Leonel Figueiredo de Alencar
# Last update: October 25, 2022

from Nheengatagger import getparselist, tokenize, DASHES
from BuildDictionary import MAPPING, extract_feats, loadGlossary, extractTags, isAux
from conllu.models import Token,TokenList
from conllu import parse
from io import open
from conllu import parse_incr
import re

# Separator of multiword tokens
HYPHEN='-'
# Case of second class pronouns
CASE="Gen"

UDTAGS={'PL': 'Plur', 'SG': 'Sing',
'V': 'VERB', 'N': 'NOUN', 'V2': 'VERB',
'A': 'ADJ', 'ADVR': 'ADV', 'ADVS': 'ADV',
'ADVJ': 'ADV', 'ADVD': 'ADV',
'ADVL': 'ADV', 'A2': 'VERB',
'CONJ' : 'C|SCONJ', 'NFIN' : 'Inf', 'ART' : 'DET',
'COP' : 'AUX',
'AUXN' : 'AUX', 'AUXFR' : 'AUX', 'AUXFS' : 'AUX',
'CARD' : 'NUM', 'ORD' : 'ADJ', 'ELIP' : 'PUNCT'}

# TODO: extractDemonstratives()
DET =  {'DEM' : 'DET', 'INDQ' : 'DET',
'INT' : 'DET', 'ART' : 'DET', 'DEMX' : 'DET', 'DEMS' : 'DET',
'IND' : 'DET', 'TOT' : 'DET'}

DEIXIS={'DEMS' : 'Remt', 'DEMX' : 'Prox'}

def extractAuxiliaries(tag='aux.'):
    glossary=loadGlossary()
    auxiliaries=list(filter(lambda x: tag in x.get('pos'),glossary))
    for auxiliary in auxiliaries:
        pos=auxiliary['pos']
        auxiliary['pos']=extractTags(pos,isAux)[0]
    return auxiliaries

AUX = extractAuxiliaries()

def extractAuxEntry(lemma):
    return list(filter(lambda x: lemma == x.get('lemma'), AUX))

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

def incrementRange(r='107:111',i=1):
	m,n=[int(x) for x in r.split(':')]
	return f"{m+i}:{n+i}"

def incrementTokenRange(tokenlist,i=1):
    for t in tokenlist:
        value=incrementRange(t['misc']['TokenRange'],i)
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

def mkTokenRange(token, start, end):
    token['misc']={'TokenRange': f'{start}:{end}'}

def mkMultiWordToken(ident,form,start=0,end=0,spaceafter=None):
    token=Token()
    token['id']=ident
    token['form']=form
    for field in ('lemma','upos','xpos','feats','head','deprel','deps'):
        token[field] = None
    mkTokenRange(token,start,end)
    if spaceafter:
        token['misc'].update({'SpaceAfter':'No'})
    return token

def WordsOfLenghth(lenght,pos):
    glossary=loadGlossary()
    return list(filter(lambda x:  len(x['lemma']) == lenght and x['pos'] == pos,glossary))

def mkConlluToken(word,entry,head=0, deprel=None, start=0, ident=1, deps=None):
    mapping={'ADP' : 'case', 'SCONJ':'mark',
    'VERB':'root',
    'PUNCT':'punct'}
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
        handleNCont(upos,feats)
    if feats:
        token['feats']=feats
    else:
        token['feats']=None
    token['head']=head
    dprl=mapping.get(upos)
    if not dprl:
        dprl=deprel
    token['deprel']=dprl
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

def VerbIdsList(tokenlist):
    return tokenlist.filter(upos="VERB")

def VerbIdsList1(tokenlist):
    return VerbsList(tokenlist)

def isVerb(token):
    'return True if token is a verb or an existential particle'
    if token.get('upos') == 'VERB' or token.get('xpos') == 'EXST':
        return True
    return False

def VerbsList(tokenlist):
    verblist=list(filter(lambda x: isVerb(x), tokenlist))
    tk=TokenList()
    tk.extend(verblist)
    return tk

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
        if len(prontype) > 3 and prontype not in ('Card',):
            prontype=prontype[:3]
    return prontype

def handlePron(token,nextToken):
    xpos=token['xpos']
    prontype=getprontype(xpos)
    #print(xpos,prontype)
    if not token.get('feats'):
        token['feats']={}
    token['feats'].update({'PronType': prontype})
    if xpos == 'PRON2':
        token['feats'].update({'Case': CASE})
        if nextToken['upos'] == 'NOUN':
            token['feats'].update({'Poss': 'Yes'})
            token['deprel'] ='nmod:poss'
            token['head'] =nextToken['id']

def setDeprel(token, headid,deprel='nsubj',overwrite=False):
    if overwrite:
        token['deprel'] = deprel
        token['head'] =  headid
    else:
        if not token['deprel']:
            token['deprel'] = deprel
            token['head'] =  headid

def SubjOrObj(token,verbs):
    previousverb = previousVerb(token,verbs)
    nextverb = nextVerb(token,verbs)
    if previousverb:
        headlist=verbs.filter(id=previousverb)
        if headlist:
            head=headlist[0]
            upos=head['upos']
            if upos == 'VERB':
                setDeprel(token,previousverb,'obj')
            else:
                setDeprel(token,previousverb,'nsubj')
    elif nextverb:
        setDeprel(token,nextverb,'nsubj')

def hasNext(token,nexttoken):
    return token['id'] == nexttoken['id'] - 1

def sameHead(token,nexttoken):
    return token['head']==nexttoken['head']

def sameDeprel(token,nexttoken):
    dep1=token['deprel']
    dep2=nexttoken['deprel']
    return dep1==dep2

def ListOfCats(tokenlist,cats):
    newlist=TokenList()
    for token in tokenlist:
        if token.get('upos') in cats:
            newlist.append(token)
    return newlist

def handleNmodPoss(tokenlist):
    nouns=ListOfCats(tokenlist,('NOUN','PROPN'))
    i=0
    while(i < len(nouns)-1):
        token=nouns[i]
        nexttoken=nouns[i+1]
        if hasNext(token,nexttoken):
            if sameHead(token,nexttoken) and sameDeprel(token,nexttoken):
                token['deprel']='nmod:poss'
                token['head']=nexttoken['id']
        i+=1

def handleAdpCompl(token,verbs,nextToken):
    token['deprel'] = 'obl'
    headid=previousVerb(token,verbs)
    if not headid:
        headid=nextVerb(token,verbs)
    token['head'] = headid
    nextToken['deprel']='case'
    nextToken['head'] =token['id']

def handleNounPron(token,nextToken,verbs):
    if nextToken['upos'] == 'ADP':
        handleAdpCompl(token,verbs,nextToken)
    elif nextToken['upos'] == 'ADJ':
        if token['upos'] == 'NOUN':
            nextToken['deprel']='amod'
            nextToken['head'] =token['id']
    elif nextToken['upos'] == 'VERB':
        token['deprel'] = 'nsubj'
        token['head'] =nextToken['id']
    if  token['xpos'] != 'PRON2':
        SubjOrObj(token,verbs)

def updateFeats(token,feature,value):
    if not token['feats']:
        token['feats']={}
    token['feats'].update({feature : value})

def headPartNextVerb(token,verbs):
    tokid=token['id']
    for verb in verbs:
        verbid=verb['id']
        if verbid > tokid:
            token['head']=verbid
            break

def headPartPreviousVerb(token,verbs):
    tokid=token['id']
    for verb in verbs:
        verbid=verb['id']
        if verbid < tokid:
            token['head']=verbid
            break
        else:
            headPartNextVerb(token,verbs)

def handlePart(token,verbs):
    mapping= {
    'PQ': {'PartType': 'Int','QestType':'Polar'},
    'CQ': {'PartType': 'Int','QestType':'Content'},
    'NEG': {'PartType': 'Neg','Polarity':'Neg'},
    'RPRT': {'PartType': 'Mod','Evident':'Nfh'},
    # 'RPRT': {'PartType': 'Tam','Evident':'Nfh'},
    'PFV': {'PartType': 'Tam','Aspect':'Perf'},
    'FRUST': {'PartType': 'Tam','Aspect':'Frus'},
    'FUT': {'PartType': 'Tam','Tense':'Fut'},
    'PRET': {'PartType': 'Tam','Tense':'Past'},
    'EXST': {'PartType': 'Exs'},
    }
    token['deprel'] = 'advmod'
    xpos=token['xpos']
    if xpos == 'NEG': #TODO: use the dictionary instead
        updateFeats(token,'Polarity', 'Neg')
        updateFeats(token,'PartType', 'Neg')
        headPartNextVerb(token,verbs)
    elif xpos == 'RPRT':
        updateFeats(token,'Evident','Nfh')
        updateFeats(token,'PartType', 'Mod')
        headPartPreviousVerb(token,verbs)
    elif xpos == 'PFV':
        headPartPreviousVerb(token,verbs)
        updateFeats(token,'Aspect','Perf')
    elif xpos == 'FRUST':
        headPartPreviousVerb(token,verbs)
        updateFeats(token,'Aspect','Frus')
    elif xpos == 'FUT':
        headPartPreviousVerb(token,verbs)
        updateFeats(token,'Tense','Fut')
    elif xpos == 'PRET':
        headPartPreviousVerb(token,verbs)
        updateFeats(token,'Tense','Past')
    elif xpos == 'CQ':
        headPartNextVerb(token,verbs)
        updateFeats(token,'PartType', 'Int')
    elif xpos == 'PQ':
        headPartPreviousVerb(token,verbs)
        updateFeats(token,'PartType', 'Int')
    elif xpos == 'EXST':
        if len(verbs) > 0:
            headPartNextVerb(token,verbs)
        else:
            token['head']=0
            token['deprel']='root'
            verbs.append(token)
        updateFeats(token,'PartType', 'Exs')

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

def handleSconj0(token,tokenlist,verbs):
    token['deprel'] = 'mark'
    tokid=token['id']
    if tokid > 0:
        if tokenlist[tokid-1]['lemma'] == 'ti':
            for verb in verbs:
                verbid=verb['id']
                if verbid > tokid:
                    token['head']=verbid
                    #verb['deprel'] = 'advcl'
                    break
        else:
            j=-1
            while(j >= -len(verbs)) :
                verbid=verbs[j]['id']
                if verbid < token['id']:
                    token['head']= verbid
                    #verbs[j]['deprel'] = 'advcl'
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

def handleCconj(token,verbs):
    headid=nextVerb(token,verbs)
    token['deprel']='cc'
    token['head']=headid
    if headid:
        for verb in verbs:
            if verb['id'] == headid:
                verb['deprel']='conj'
                verb['head']=previousVerb(verb,verbs)
                break

def handleSconj(token,tokenlist,verbs):
    '''TODO:
    1. adapt function to handle non-verbal clauses
    '''
    token['deprel'] = 'mark'
    previous=getPreviousToken(token,tokenlist)
    if previous:
        if previous['xpos'] == 'NEG':
            token['head']=nextVerb(token,verbs)
        else:
            if previous['upos'] == 'PUNCT':
                token['head']=nextVerb(token,verbs)
            else:
                token['head']=previousVerb(token,verbs)
    else:
        token['head']=nextVerb(token,verbs)
    headid=token['head']
    headlist=verbs.filter(id=headid)
    if headlist:
        head=headlist[0]
        head['deprel']='advcl'
        head['head']=getHeadVerb(head,verbs)

def handleAdp(token,tokenlist,verbs):
    '''TODO:
    1. implement a function analogous to handleSconj and handleCconj
    2. change ADP treatment in the functions dealing with precedent categories
    3. does handleAdpCompl perform a similar job?
    '''
    feats=token.get('feats')
    if feats and feats.get('Rel') == 'NCont':
        token['deprel'] = 'obl'
        token['head'] = getHeadVerb(token,verbs)
    else:
        token['deprel'] = 'case'
        nouns=TokensOfCatList(tokenlist,'NOUN')
        previous=getPreviousToken(token,tokenlist)
        if previous['upos'] not in ('NOUN','PRON','PROPN'):
            nounid=previousCat(token,nouns)
            token['head']=nounid
            for noun in nouns:
                if noun['id'] == nounid:
                    noun['deprel'] = 'obl'
                    headlist=tokenlist.filter(deprel='root')
                    head=previousCat(noun,headlist)
                    noun['head'] = head

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

def getNextToken(token,tokenlist):
    for t in tokenlist:
        if t['form'] != token['form']:
            return t

def getPreviousToken(token,tokenlist):
    index=tokenlist.index(token)
    c=len(tokenlist[:index])
    if c > 1:
        i=c-1
        while(i >= 0):
            previous=tokenlist[i]
            if previous['form'] != token['form']:
                return previous
            i=i-1
    elif c == 1:
        return tokenlist[:index][0]

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

def pronOrDet(token,nounid,verbs):
    verbid=nextVerb(token,verbs)
    tokenid=token['id']
    if verbid:
        if nounid > verbid or not nounid:
            token['upos']='PRON'
            setDeprel(token,verbid,'nsubj')
    elif not nounid:
        token['upos']='PRON'
        setDeprel(token,verbid,'obj')

def handleDetNum(upos,token,nextToken,tokenlist,verbs):
    deprel={'DET': 'det', 'NUM': 'nummod'}
    delta=2
    Pron='Pron'
    if upos == 'NUM':
        Pron='Num'
    nouns=TokensOfCatList(tokenlist,'NOUN')
    nounid=nextCat(token,nouns)
    pronOrDet(token,nounid,verbs)
    deprel=deprel.get(token['upos'])
    if deprel:
        token['deprel']=deprel
        tokenid=token['id']
        if nounid - tokenid > delta:
            token['head']=getNextWord(token,tokenlist)['id']
        else:
            token['head']=nounid
    else:
        if nextToken['upos'] == 'ADP':
            handleAdpCompl(token,verbs,nextToken)
    xpos=token['xpos']
    value=getprontype(xpos)
    #value=xpos.title()
    deixis=DEIXIS.get(xpos)
    if deixis:
        updateFeats(token,'Deixis',deixis)
        #value=value[:3]
    updateFeats(token,f'{Pron}Type',value)
    if token['feats'].get('PronType') == 'Art':
        updateFeats(token,'Definite','Ind')

def getNextWord(token, tokenlist):
    start=tokenlist.index(token)
    i=start + 1
    while (i < len(tokenlist)):
        t=tokenlist[i]
        if t['upos'] != 'PUNCT' and t['form'] != token['form']:
            return t
        i+=1

def headAux(verb,headid):
    if headid:
        verb['upos'] = 'AUX'
        verb['deprel'] = 'aux'
        verb['head'] = headid

def setUposXpos(verb,pos):
    verb['xpos'] = pos
    verb['upos'] = UDTAGS[pos]

def sameClause(headid,punctid):
    return headid > punctid

def handleAux(tokenlist):
    verbs=VerbIdsList(tokenlist)
    puncts=nouns=TokensOfCatList(tokenlist,'PUNCT')
    c=len(verbs)
    if c == 1:
        if verbs[0]['lemma'] == 'ikú':
            verbs[0]['deprel'] = 'cop'
            verbs[0]['xpos'] = 'COP'
            verbs[0]['upos'] = 'AUX'
            # handleNonVerbalRoot()
    elif c > 1:
        for verb in verbs:
            verbid=verb['id']
            lemma=verb['lemma']
            entries=extractAuxEntry(lemma)
            pos=''
            if entries:
                pos=entries[0]['pos']
            if pos == 'AUXFR':
                headid=nextVerb(verb,verbs)
                headAux(verb,headid)
                setUposXpos(verb,pos)
            elif pos == 'AUXFS' or pos == 'AUXN':
                # TODO: get id previous PUNCT, headid > punctid
                punctid=previousCat(verb,puncts)
                headid=previousVerb(verb,verbs)
                if sameClause(headid,punctid):
                    headAux(verb,headid)
                    setUposXpos(verb,pos)
            else:
                pass # TODO: ccomp, xcomp, advcl

def handleNCont(upos,feats):
    if feats['Rel'] == 'NCont':
        if upos == 'VERB':
            feats.update({'Number':'Sing',
            'Person' : '3',
            'VerbForm' : 'Fin'})
        elif upos == 'NOUN':
            feats.update({'Number[psor]':'Sing',
            'Person[psor]' : '3'})
        elif upos == 'ADP':
            feats.update({'Number[grnd]':'Sing',
            'Person[grnd]' : '3'})

def extractClauses(tokenlist):
    clauses=[]
    for token in tokenlist:
        if token['form'] == ',':
            first=TokenList()
            index=tokenlist.index(token)
            first.extend(tokenlist[:index])
            clauses.append(first)
            last=TokenList()
            last.extend(tokenlist[index:])
            clauses.append(last)
            break
    return clauses

def AdjOrNounRoot(tokenlist):
    adjs=TokensOfCatList(tokenlist,'ADJ')
    nouns=TokensOfCatList(tokenlist,'NOUN')
    rootid=0
    nsubjid=0
    if adjs:
        rootid=adjs[-1]['id']
    elif nouns:
        if len(nouns) > 1:
            nsubjid=nouns[0]['id']
            rootid=nouns[1]['id']
    if rootid:
        for token in tokenlist:
            if token['id']==rootid:
                token['head']=0
                token['deprel']='root'
                break
    if nsubjid:
        for token in tokenlist:
            if token['id']==nsubjid:
                token['head']=rootid
                token['deprel']='nsubj'
                break

def GenitiveConstruction(tokenlist):
    nouns=TokensOfCatList(tokenlist,'NOUN')
    #TODO

def handlePunct(token,nextToken,tokenlist,verbs):
    if nextToken['lemma'] == ",":
        nextToken['head'] = nextVerb(token,verbs)
    elif nextToken['xpos'] == 'ELIP':
         updateFeats(nextToken,'PunctType','Elip')
         nextToken['head'] = previousVerb(nextToken,verbs)
    else:
        headlist=tokenlist.filter(deprel='root')
        head=1
        if headlist:
            head=headlist[0]['id']
        nextToken['head']=head

def handleRel(token,tokenlist):
    token['deprel'] = 'nsubj'
    i=len(tokenlist)
    previous=getPreviousToken(token,tokenlist)
    token['head'] = previous['id']
    nouns=TokensOfCatList(tokenlist,'NOUN')
    prons=TokensOfCatList(tokenlist,'PRON')
    tokenid=token['id']
    headids=[tokenid]
    nounid=previousCat(token,nouns)
    headids.append(nounid)
    pronid=previousCat(token,prons)
    headids.append(pronid)
    headids.sort()
    j=headids.index(tokenid)
    headid=nounid
    if headids.index(tokenid) > 0:
        headid=headids[j-1]
    previous['head'] = headid
    previous['deprel'] = 'acl:relcl'

def handleVerbs(verbs):
    rootlist=verbs.filter(deprel='root')
    if len(rootlist) > 1:
        for verb in rootlist[1:]:
            headid = previousVerb(verb,verbs)
            setDeprel(verb, headid,deprel='parataxis',overwrite=True)

def addFeatures(tokenlist):
    i=0
    c=len(tokenlist) -1
    handleAux(tokenlist)
    verbid=FirstVerbId(tokenlist)
    verbs=VerbIdsList(tokenlist)
    if not verbs:
        AdjOrNounRoot(tokenlist)
    while(i < c) :
        token=tokenlist[i]
        upos=token['upos']
        nextToken=getNextToken(token, tokenlist[i+1:])
        if upos in ('NOUN','PRON','PROPN'):
            if token['xpos'] == 'REL':
                handleRel(token,tokenlist)
            else:
                handleNounPron(token,nextToken,verbs)
                if upos == 'PRON':
                    handlePron(token,nextToken)
        elif upos == "PART":
            handlePart(token,verbs)
        elif upos == "VERB":
            pass
            # TODO: handleVerb(token,nextToken,verbs)
        elif upos == "ADP":
            handleAdp(token,tokenlist,verbs)
        elif upos == "SCONJ":
            handleSconj(token,tokenlist,verbs)
        elif upos == "CCONJ":
            handleCconj(token,verbs)
        elif upos == "ADV":
            handleAdv(token,verbs)
        elif upos in ("DET","NUM"):
            handleDetNum(upos,token,nextToken,tokenlist,verbs)
        if nextToken['upos'] == 'PUNCT': # TODO: sentences without final punctuation
            handlePunct(token,nextToken, tokenlist,verbs)
        i+=1
    handleVerbs(verbs)
    handleNmodPoss(tokenlist)

def filterparselist(tag,parselist):
    return list(filter(lambda x: x[1].split('+')[0] == tag.upper(),parselist))

def handleCompoundAux(token):
    updateFeats(token,'Compound','Yes')

def getStartEnd(token):
    dic={}
    misc=token.get('misc')
    if misc:
        tokenrange=misc.pop('TokenRange')
        if not misc:
            token['misc']=None
        if tokenrange:
            start,end=tokenrange.split(':')
            dic['start']=start
            dic['end']=end
    return dic

def getSpaceAfter(token):
    misc=token.get('misc')
    if misc.get('SpaceAfter'):
        return misc.pop('SpaceAfter')

def insertCompoundAux(tokenlist):
    newlist=TokenList()
    for token in tokenlist:
        feats=token.get('feats')
        if feats:
            if feats.get('Compound') == 'Yes':
                index=tokenlist.index(token)
                previous=tokenlist[index-1]
                #print(previous)
                #start=getStartEnd(previous)['start']
                startend=getStartEnd(previous)
                start=startend.get('start')
                if start:
                    spaceafter=getSpaceAfter(token)
                    end=getStartEnd(token)['end']
                    form=f"{previous['form']}-{token['form']}"
                    tokenid=token['id']
                    ident=f'{tokenid-1}-{tokenid}'
                    compound=mkMultiWordToken(ident,form,start,end,spaceafter)
                    tokenlist.insert(index-1,compound)
                #break

def handleHyphen(form):
    dic={}
    dic['form']=form
    dic['hyphen']=False
    if form.startswith(HYPHEN):
        dic['form']=form[1:]
        dic['hyphen']=True
    return dic

def mkConlluSentence(tokens):
    tokenlist=TokenList()
    ident=1
    start=0
    for token in tokens:
        tag=''
        if '/' in token:
            token,tag=token.split('/')
        dic=handleHyphen(token)
        form=dic.get('form')
        parselist=getparselist(form.lower())
        if tag:
            newparselist=filterparselist(tag,parselist)
            if newparselist:
                parselist=newparselist
        entries=extract_feats(parselist)
        for entry in entries:
            if entry.get('pos') == 'PUNCT':
                start=start-1
            t=mkConlluToken(form,entry,start=start, ident=ident)
            if dic.get('hyphen'):
                handleCompoundAux(t)
            tokenlist.append(t)
        start=start+len(token)+1
        ident+=1
    handleSpaceAfter(tokenlist)
    addFeatures(tokenlist)
    insertCompoundAux(tokenlist)
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

def ppText(sents,pref='',textid=0,index=0,sentid=0):
    if pref:
        print(f"# sent_id = {pref}:{textid}:{index}:{sentid}")
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

def extractYrl(sent):
    return re.sub(r"[/]\w+",'',sent)

def TreebankSentence(text='',pref='',textid=0,index=0,sentid=0):
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
    yrl=extractYrl(sents[0])
    sents[1]=f"({sents[1]})"
    if len(sents) == 5:
        ppText([yrl,sents[3],sents[2],sents[1],sents[4]],pref,textid,index,sentid)
    else:
        ppText([yrl,sents[3],sents[2],sents[1]],pref,textid,index,sentid)
    #mkText("\n".join((sents[0],sents[3],sents[2],f"({sents[1]})")))
    parseSentence(sents[0])

def splitMultiWordTokens(tokens):
    aux=[d['lemma'] for d in AUX]
    newlist=[]
    for t in tokens:
        if HYPHEN in t:
            index=t.index(HYPHEN)
            second=t[index:]
            if second[1:] in aux:
                newlist.extend([t[:index],second])
            else:
                newlist.append(t)
        else:
            newlist.append(t)
    return newlist

def parseSentence(sent):
    tokens=splitMultiWordTokens(tokenize(sent))
    tk=mkConlluSentence(tokens)
    print(tk.serialize())

def mkDict(text,pref='MooreFP1994',textid=0,sentid=1):
	groups=text.split('|')
	dic={}
	dic['yrl']=[]
	dic['yrl'].append(groups[0].strip())
	parts=[re.sub(r"\s-\s",'',part).strip() for part in re.split(r"[)(]",groups[1])]
	dic['source']=parts[1]
	dic['yrl'].append(parts[0])
	dic['por']=[]
	dic['por'].append(parts[2])
	por,eng=[s.strip() for s in re.split(r"\s-\s",groups[2])]
	dic['por'].append(por)
	dic['eng']=[]
	dic['eng'].append(eng)
	dic['eng'].append(groups[3])
	return dic

def TreebankSentences(text,pref='MooreFP1994',textid=0,index=0,sentid=1):
    dic=mkDict(text)
    i=0
    sentid=sentid
    index=index
    source=dic.get('source')
    yrl,eng,por=dic['yrl'],dic['eng'],dic['por']
    while(i < len(yrl)):
        ppText([extractYrl(yrl[i]),eng[i],por[i]],pref,textid,index,sentid)
        if source:
            print(f"# text_source = {source}")
        parseSentence(yrl[i])
        sentid+=1
        index+=1
        i+=1

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
