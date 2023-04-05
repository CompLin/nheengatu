#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Author: Leonel Figueiredo de Alencar
# Last update: April 4, 2023

from Nheengatagger import getparselist, tokenize, DASHES
from BuildDictionary import DIR,MAPPING, extract_feats, loadGlossary, loadLexicon, extractTags, isAux, accent, guessVerb
from conllu.models import Token,TokenList
from conllu import parse
from io import open
from conllu import parse_incr
import re, os

# default annotator's name abbreviation
ANNOTATOR = 'LFdeA'

# Characters to be removed from input sentence
REMOVE=r"/=?\w*([:=|]\w+)*@?"

# Separators of multiword tokens
HYPHEN='-'
UNDERSCORE='_'

# Multiword token
MULTIWORDTOKENS={}

# Case of second class pronouns
CASE="Gen"

# Enclitic postpositions
# TODO: extract fom glossary
# hyphenated
CLITICS=['pe']

# non-hyphenated
# clitic alomorph of postposition 'upé'
ME='me'

# clitic adverb "-ntu"
NTU='ntu'

# clitic question particle "-ta"
TA='taá'

NONHYPHEN=[NTU,ME]

ROOT=[]

GLOSSARY=loadGlossary(jsonformat=os.path.join(DIR,"glossary.json"))
LEXICON=loadLexicon()

UDTAGS={'PL': 'Plur', 'SG': 'Sing',
'V': 'VERB', 'N': 'NOUN', 'V2': 'VERB', 'V3': 'VERB',
'A': 'ADJ', 'A2': 'VERB',
'CONJ' : 'C|SCONJ', 'NFIN' : 'Inf', 'ART' : 'DET',
'COP' : 'AUX', 'PREP' : 'ADP', 'SCONJR': 'SCONJ',
'AUXN' : 'AUX', 'AUXFR' : 'AUX', 'AUXFS' : 'AUX',
'CARD' : 'NUM', 'ORD' : 'ADJ', 'ELIP' : 'PUNCT',
'COL':'Coll', 'PRV': 'Priv'}

# TODO: extractDemonstratives()
DET =  {'DEM' : 'DET', 'INDQ' : 'DET',
'INT' : 'DET', 'ART' : 'DET', 'DEMX' : 'DET', 'DEMS' : 'DET',
'DEMSN' : 'DET', 'IND' : 'DET', 'TOT' : 'DET'}

DEIXIS={'DEMS' : 'Remt', 'DEMSN' : 'Remt','DEMX' : 'Prox', 'I': 'Remt', 'X': 'Prox'}

ADVTYPE={'ADVO':'Loc','ADVD':'Loc', 'ADVS':'Deg', 'ADVJ':'Cau', 'ADVG':'Deg'}

WH_ADVTYPE={'ADVC':'Loc', 'ADVA':'Man',
'ADVT':'Tim', 'ADVM':'Mod', 'ADVU': 'Cau'}

WH_ADV={'ADVR': 'Int', 'ADVL':'Rel'}
DEM_ADV={'ADVD': 'Dem'}
ADVPRONTYPE={}
ADVPRONTYPE.update(WH_ADV)
ADVPRONTYPE.update(DEM_ADV)

ADVTYPE.update(WH_ADVTYPE)

def extractAuxiliaries(tag='aux.'):
    glossary=loadGlossary()
    auxiliaries=list(filter(lambda x: tag in x.get('pos'),glossary))
    for auxiliary in auxiliaries:
        pos=auxiliary['pos']
        auxiliary['pos']=extractTags(pos,isAux)[0]
    return auxiliaries

AUX = extractAuxiliaries()

def extractAuxEntry(lemma):
    entry=dict()
    entries=list(filter(lambda x: lemma == x.get('lemma'), AUX))
    if entries:
        entry.update(entries[0])
    return entry

def AdverbTags():
    adv='adv.'
    upos='ADV'
    dic={}
    for pos,xpos in MAPPING.items():
        if pos.startswith(adv):
            dic[xpos]=upos
    return dic

def extractAdverbs():
    advs={}
    for lemma,entries in LEXICON.items():
        for entry in entries:
            if entry[1].startswith('ADV'):
                if advs.get(lemma):
                    advs[lemma].append(entry[1])
                else:
                    advs[lemma]=[entry[1]]
    return advs

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
UDTAGS.update(AdverbTags())

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
    degree=entry.get('degree')
    derivation=entry.get('derivation')
    aspect=entry.get('aspect')
    tense=entry.get('tense')
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
    if degree:
        feats['Degree']=f"{degree.title()}"
    if aspect:
        feats['Aspect']=f"{aspect.title()}"
    if tense:
        feats['Tense']=f"{tense.title()}"
    if derivation:
        feats['Derivation']=UDTAGS.get(derivation)
    if feats:
        token['feats']=feats
    else:
        token['feats']=None
    if token['xpos'] == 'REL':
        updateFeats(token,'PronType','Rel')
    #elif token['xpos'] == 'ADVR':
    #    updateFeats(token,'PronType','Int')
    #elif token['xpos'] == 'ADVL':
    #    updateFeats(token,'PronType','Rel')
    elif token['xpos'] in ('ORD','ADVO'):
        updateFeats(token,'NumType','Ord')
    includeAdvType(token)
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
    GenitiveConstruction(nouns)

def handlePospCompl(token,nextToken):
    nextToken['deprel']='case'
    nextToken['head'] =token['id']

def handleAdpCompl(token,verbs,nextToken):
    token['deprel'] = 'obl'
    verb=previousVerb(token,verbs)
    if not verb:
        verb=nextVerb(token,verbs)
    if verb:
        token['head'] = verb
    posp=nextToken['xpos'] == 'ADP'
    if posp:
        handlePospCompl(token,nextToken)

def setAttribute(token,attribute,value,overwrite=False):
    if overwrite:
        token[attribute] = value
    else:
        if not token[attribute]:
            token[attribute] = value

def handleNounPron(token,nextToken,verbs):
    upos=''
    if nextToken:
        upos=nextToken['upos']
    if upos == 'ADP':
        handleAdpCompl(token,verbs,nextToken)
    elif upos == 'ADJ':
        if token['upos'] == 'NOUN':
            #nextToken['deprel']='amod'
            #nextToken['head'] =token['id']
            setAttribute(nextToken,'deprel','amod')
            if nextToken['deprel']=='amod':
                nextToken['head'] =token['id']
    elif upos == 'VERB':
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
    i=len(verbs)-1
    while(i >=0):
        verb=verbs[i]
        verbid=verb['id']
        if verbid < tokid:
            token['head']=verbid
            break
        else:
            headPartNextVerb(token,verbs)
        i=i-1

def handleIntj(token,verbs):
    token['deprel'] = 'discourse'
    headPartNextVerb(token,verbs)

def PreviousContentWord(token,tokenlist):
    funct=['ADP','AUX','CONJ','SCONJ']
    return getPreviousToken(token,tokenlist,funct)


def handlePart(token,tokenlist,verbs):
    mapping= {
    'PQ': {'PartType': 'Int','QestType':'Polar'},
    'CQ': {'PartType': 'Int','QestType':'Content'},
    'NEG': {'PartType': 'Neg','Polarity':'Neg'},
    'CONS': {'PartType': 'Mod','Polarity':'Pos'},
    'NEGI': {'PartType': 'Neg','Polarity':'Neg','Mood': 'Imp'},
    'RPRT': {'PartType': 'Mod','Evident':'Nfh'},
    # 'RPRT': {'PartType': 'Tam','Evident':'Nfh'},
    'PFV': {'PartType': 'Tam','Aspect':'Perf'},
    'FRUST': {'PartType': 'Tam','Aspect':'Frus'},
    'FUT': {'PartType': 'Tam','Tense':'Fut'},
    'PRET': {'PartType': 'Tam','Tense':'Past'},
    'EXST': {'PartType': 'Exs'},
    'CERT': {'PartType': 'Mod'},
    'ASSUM': {'PartType': 'Mod'},
    'PROTST': {'PartType': 'Mod'},
    'TOTAL': {'PartType': 'Quant'},
    'COND': {'PartType': 'Mod', 'Mood': 'Cnd'},
    'NEC': {'PartType': 'Mod', 'Mood': 'Nec'},
    'FOC': {'PartType': 'Emp', 'Foc': 'Yes'}
    }
    token['deprel'] = 'advmod'
    xpos=token['xpos']
    if xpos.startswith('NEG'): #TODO: use the dictionary instead
        updateFeats(token,'Polarity', 'Neg')
        updateFeats(token,'PartType', 'Neg')
        if xpos == 'NEGI':
            updateFeats(token,'Mood', 'Imp')
        headPartNextVerb(token,verbs)
    elif xpos == 'RPRT':
        updateFeats(token,'Evident','Nfh')
        updateFeats(token,'PartType', 'Mod')
        headPartPreviousVerb(token,verbs)
    elif xpos == 'CERT' or xpos == 'ASSUM':
        updateFeats(token,'PartType', 'Mod')
        token['head']=getAdvHead(token,tokenlist,verbs)
        # headPartPreviousVerb(token,verbs)
    elif xpos == 'NEC':
        updateFeats(token,'PartType', 'Mod')
        headPartNextVerb(token,verbs)
    elif xpos == 'PFV':
        #headPartPreviousVerb(token,verbs)
        token['head']=getAdvHead(token,tokenlist,verbs)
        updateFeats(token,'Aspect','Perf')
    elif xpos == 'FRUST':
        headPartPreviousVerb(token,verbs)
        updateFeats(token,'Aspect','Frus')
    elif xpos == 'PROTST':
        headPartPreviousVerb(token,verbs)
        updateFeats(token,'PartType', 'Mod')
    elif xpos == 'FUT':
        #headPartPreviousVerb(token,verbs)
        token['head']=getAdvHead(token,tokenlist,verbs)
        updateFeats(token,'Tense','Fut')
    elif xpos == 'PRET':
        headPartPreviousVerb(token,verbs)
        updateFeats(token,'Tense','Past')
    elif xpos == 'CQ':
        headPartNextVerb(token,verbs)
        updateFeats(token,'PartType', 'Int')
    elif xpos == 'COND':
        headPartPreviousVerb(token,verbs)
        updateFeats(token,'PartType', 'Mod')
        updateFeats(token,'Mood', 'Cnd')
    elif xpos == 'PQ':
        headPartPreviousVerb(token,verbs)
        updateFeats(token,'PartType', 'Int')
    elif xpos == 'TOTAL':
        headPartPreviousVerb(token,verbs)
        # updateFeats(token,'PartType': 'Quant')
    elif xpos == 'CONS':
        headPartPreviousVerb(token,verbs)
        for feat,val in mapping['CONS'].items():
            updateFeats(token,feat, val)
    elif xpos == 'FOC':
        previous=PreviousContentWord(token,tokenlist)
        token['head']=previous['id']
        updateFeats(token,'PartType', 'Emp')
        updateFeats(token,'Foc', 'Yes')
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

def previousPunct(token,tokenlist):
    puncts=TokensOfCatList(tokenlist,'PUNCT')
    return previousCat(token,puncts)

def getAdvHead(token,tokenlist,verbs):
    punctid=previousPunct(token,tokenlist)
    headid=previousVerb(token,verbs)
    tokenid=token['id']
    if not inInterval(headid,punctid,tokenid):
        headid=nextVerb(token,verbs)
    return headid

def AdvPronType(lastchar):
    for adv,prontype in ADVPRONTYPE.items():
        if adv.endswith(lastchar):
            return prontype
    return None

def WhAdvType(lastchar):
    for adv,advtype in WH_ADVTYPE.items():
        if adv.endswith(lastchar):
            return advtype
    return None

def RelativeInterrogativeAdv(tag):
    feats={}
    #feats['xpos']=tag
    prontype=None
    advtype=None
    if tag and tag.startswith('ADV') and len(tag) > 3:
        i=-1
        if len(tag) == 5:
            i=-2
            advtype=WhAdvType(tag[-1])
            if not advtype:
                advtype=ADVTYPE.get(tag[:-1])
                if tag.startswith('ADVD'):
                    lastchar=tag[-1]
                    feats['Deixis']=DEIXIS.get(lastchar)
        #xpos=f"{tag[0:3]}{tag[i]}"
        #feats['xpos']=xpos
        prontype=AdvPronType(tag[i])
    #if not prontype:
    #    prontype=
    feats['PronType']=prontype
    if not advtype:
        advtype=ADVTYPE.get(tag)
    feats['AdvType']=advtype
    return feats

def includeAdvType(token):
    xpos=token['xpos']
    dic=RelativeInterrogativeAdv(xpos)
    #key=dic['xpos']
    prontype=dic.get('PronType')
    advtype=dic.get('AdvType')
    deixis=dic.get('Deixis')
    if advtype:
        updateFeats(token,'AdvType',advtype)
    if prontype:
        updateFeats(token,'PronType',prontype)
    if deixis:
        updateFeats(token,'Deixis',deixis)

def handleAdv(token,nextToken, tokenlist,verbs):
    token['deprel']='advmod'
    previous=getPreviousToken(token,tokenlist,skip=['PUNCT'])
    xpos=token['xpos']
    #includeAdvType(token)
    feats=token.get('feats')
    prontype=None
    advtype=None
    if feats:
        prontype=feats.get('PronType')
        advtype=feats.get('AdvType')
    if prontype =='Rel':
        #updateFeats(token,'PronType', 'Rel')
        nouns=TokensOfCatList(tokenlist,'NOUN')
        nounid=previousCat(token,nouns)
        headid=nextVerb(token,verbs)
        token['head']=headid
        headlist=tokenlist.filter(id=headid)
        if headlist:
            head=headlist[0]
            head['deprel']='acl:relcl'
            if previous:
                head['head']=previous['id']
    elif prontype =='Deg':
        token['head']=previous['id']
        #updateFeats(token,'AdvType','Deg')
        feats=nextToken.get('feats')
        if feats and feats.get('PronType') == 'Rel':
            updateFeats(token,'Degree','Sup')
        else:
            updateFeats(token,'Degree','Cmp')
    elif prontype =='Int':
        token['head']=nextVerb(token,verbs)
        #updateFeats(token,'PronType', 'Int')
    else:
        token['head']=getAdvHead(token,tokenlist,verbs)
        #if xpos=='ADVD':
        #    updateFeats(token,'PronType', 'Dem')
        #    updateFeats(token,'AdvType', 'Loc')
    #includeAdvType(token)

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
    # token['deprel'] = 'mark'
    xpos=token['xpos']
    if xpos == 'SCONJR':
        token['head']=nextVerb(token,verbs)
    else:
        handleSconjS(token,tokenlist,verbs)
    headSconj(token,verbs)

def handleSconjS(token,tokenlist,verbs):
    '''TODO:
    1. adapt function to handle non-verbal clauses
    '''
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
    headSconj(token,verbs)

def headSconj(token,verbs):
    headid=token['head']
    headlist=verbs.filter(id=headid)
    if headlist:
        head=headlist[0]
        head['deprel']='advcl'
        head['head']=getHeadVerb(head,verbs)

def handlePosp(token,tokenlist,nouns):
    previous=getPreviousToken(token,tokenlist)
    if previous and previous['upos'] not in ('NOUN','PRON','PROPN'):
        nounid=previousCat(token,nouns)
        token['head']=nounid
        nounHead(nounid,nouns,tokenlist)

def nounHead(nounid,nouns,tokenlist):
    for noun in nouns:
        if noun['id'] == nounid:
            noun['deprel'] = 'obl'
            headlist=tokenlist.filter(deprel='root')
            head=previousCat(noun,headlist)
            noun['head'] = head
            break

def handlePrep(token,tokenlist,nouns):
    i=tokenlist.index(token)
    next=getNextToken(token,tokenlist[i+1:])
    nounid=0
    if next:
        upos=next['upos']
        if upos in ('NOUN','PRON','PROPN'):
            nounid=next['id']
            token['head']=nounid
        else:
            nounid=nextCat(token,nouns)
            token['head']=nounid
    nounHead(nounid,nouns,tokenlist)

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
        if token['xpos'] == 'PREP':
            handlePrep(token,tokenlist,nouns)
        else:
            handlePosp(token,tokenlist,nouns)

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

def skipToken(upos,skip):
    return upos not in skip

def getPreviousToken(token,tokenlist,skip=[]):
    index=tokenlist.index(token)
    c=len(tokenlist[:index])
    if c > 1:
        i=c-1
        while(i >= 0):
            previous=tokenlist[i]
            if previous['form'] != token['form'] and skipToken(previous['upos'],skip):
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

def inInterval(num,begin,end):
    return begin < num < end

def sameClause(headid,previous,next):
    return inInterval(headid,previous,next)

def handleSameClause(verb,pos,headid,previous,next):
    if sameClause(headid,previous,next):
        headAux(verb,headid)
        setUposXpos(verb,pos)

def handleAux(tokenlist):
    verbs=VerbIdsList(tokenlist)
    puncts=TokensOfCatList(tokenlist,'PUNCT')
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
            entry=extractAuxEntry(lemma)
            pos=entry.get('pos')
            previous=previousCat(verb,puncts)
            next=nextCat(verb,puncts)
            headid=0
            if pos == 'AUXFR':
                i=verbs.index(verb)
                if i+1 < len(verbs):
                    nextverb=verbs[i+1]
                    feats=nextverb.get('feats')
                    if feats and feats.get('Compound'):
                        pass
                    else:
                        headid=nextVerb(verb,verbs)
                        handleSameClause(verb,pos,headid,previous,next)
            elif pos == 'AUXFS' or pos == 'AUXN':
                headid=previousVerb(verb,verbs)
                handleSameClause(verb,pos,headid,previous,next)
            else:
                pass # TODO: ccomp, xcomp, advcl
    for verb in verbs:
        if verb['upos'] == 'AUX':
            if verb['lemma'] == 'yuíri':
                updateFeats(verb,'Aspect','Iter')

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

def assignHead(tokenlist,rootid):
    for token in tokenlist:
        if token['head'] == 0 and token['deprel'] != 'root':
            token['head'] = rootid

def AdjOrNounRoot(tokenlist):
    adjs=TokensOfCatList(tokenlist,'ADJ')
    nouns=TokensOfCatList(tokenlist,'NOUN')
    nouns.extend(TokensOfCatList(tokenlist,'PRON'))
    nouns.extend(TokensOfCatList(tokenlist,'PROPN'))
    cop=tokenlist.filter(deprel='cop')
    rootid=0
    if adjs:
        root=adjs[-1]
        setAttribute(root,'deprel','root')
        rootid=root['id']
        if nouns:
            i=-1
            while(i>=-len(nouns)):
                noun=nouns[i]
                if noun['id'] < rootid:
                    setAttribute(noun,'deprel','nsubj')
                    noun['head']=rootid
                    break
                i=i-1
    if cop:
        cop[0]['head'] = rootid
    assignHead(tokenlist,rootid)

def GenitiveConstruction(nouns):
    i=0
    c=len(nouns)-1
    while(i<c):
        this=nouns[i]
        if not this['deprel']:
            j=i+1
            if j <=c:
                this['deprel']='nmod:poss'
                next=nouns[j]
                this['head']=next['id']
        i+=1

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
            handlePart(token,tokenlist,verbs)
        elif upos == "INTJ":
            handleIntj(token,verbs)
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
            handleAdv(token,nextToken,tokenlist,verbs)
        elif upos in ("DET","NUM"):
            handleDetNum(upos,token,nextToken,tokenlist,verbs)
        if nextToken and nextToken['upos'] == 'PUNCT': # TODO: sentences without final punctuation
            handlePunct(token,nextToken, tokenlist,verbs)
        i+=1
    handleVerbs(verbs)
    handleNmodPoss(tokenlist)

def getTag(parse):
	tag=parse[1]
	if tag:
		return tag.split('+')[0]
	return ''

def filterparselist(tag,parselist):
    return list(filter(lambda x: getTag(x) == tag.upper(),parselist))

def handleCompoundAux(token):
    updateFeats(token,'Compound','Yes')

def handleClitic(token):
    updateFeats(token,'Clitic','Yes')

def handleHyphenSepToken(token):
    upos=token['upos']
    if upos == 'VERB':
        handleCompoundAux(token)
    else:
        handleClitic(token)

def getStartEnd(token):
    dic={}
    misc=token.get('misc')
    if misc:
        tokenrange=''
        if misc.get('TokenRange'):
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

def insertMultitokenWord(tokenlist):
    newlist=TokenList()
    sep='-'
    for token in tokenlist:
        feats=token.get('feats')
        if feats:
            if feats.get('Compound') == 'Yes'or feats.get('Clitic') == 'Yes':
                index=tokenlist.index(token)
                previous=tokenlist[index-1]
                startend=getStartEnd(previous)
                start=startend.get('start')
                if start:
                    spaceafter=getSpaceAfter(token)
                    end=getStartEnd(token)['end']
                    alomorph=''
                    misc=previous['misc']
                    if misc:
                        alomorph=misc.get('Alomorph')
                    first=previous['form']
                    if alomorph:
                        first=alomorph
                    #if token['upos'] == 'ADV' or token['form'] == ME:
                    #    sep=''
                    mwt=MULTIWORDTOKENS.get(first)
                    if mwt:
                        form=mwt
                    else:
                        form=f"{first}{sep}{token['form']}"
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
        if form[1:] in CLITICS:
            dic['lemma']='upé'
            dic['xpos']='ADP'
        dic['hyphen']=True
    elif form.endswith(HYPHEN):
        dic['host']=True
        dic['form']=form[:-1]
    elif form.startswith(UNDERSCORE):
        mkSuff(form,dic)
    return dic

def mkNTU(dic): # TODO: remove if deprecated
    dic['form']=form[1:]
    dic['lemma']='ntu'
    dic['upos']='ADV'
    dic['underscore']=True

def mkSuff(form,dic):
    form=form[1:]
    ntu={'xpos':'ADV','lemma':'ntu','clitic': NTU}
    me={'xpos':'ADP','lemma':'upé','clitic':ME}
    ta={'xpos': 'CQ','lemma':'taá','clitic':TA}
    suffs=[ntu,me,ta]
    for suff in suffs:
        clitic=suff.get('clitic')
        if clitic == form:
            dic['form']=form
            dic['upos']=UDTAGS[suff['xpos']]
            dic['xpos']=suff['xpos']
            dic['lemma']=suff['lemma']
            dic['underscore']=True
            break


def mkPropn(form):
    return [[form.lower(), 'PROPN']]

def mkAdv(form):
    return [[form.lower(), 'ADV']]

def mkVerb(form,derivation='',orig=None, orig_form=None):
    new={}
    feats=['V']
    if derivation:
        feats.append(derivation)
    if orig:
        new['OrigLang']=orig
    if orig_form:
        new['Orig']=orig_form
    entry=guessVerb(form)
    feats.append(entry['person'])
    number=entry.get('number')
    if number:
        feats.append(number)
    tags='+'.join(feats)
    lemma=entry['lemma']
    new['parselist']=[[lemma, tags]]
    return new

def handleAccent(base,nasal=False,force=False):
    parselist=getparselist(base)
    tags=list(filter(lambda x: x[1],parselist))
    if tags and not force:
        return base
    return accent(base,nasal)

def endswith(form,suff):
    if form.endswith(suff):
        return form[:-len(suff)]
    return ''

def mkHab(form):
    suff='tiwa'
    if form.endswith(suff):
        base=form[:-len(suff)]
        form=handleAccent(base)
        return mkVerb(form,derivation='HAB')

def mkHabSconj(form):
    suff='tiwa'
    new={}
    if form.endswith(suff):
        base=form[:-len(suff)]
        lemma=handleAccent(base)
        new['parselist']=[[lemma, 'SCONJ+HAB']]
        return new

def parseWord(form,lenght):
    base=form[:-lenght].lower()
    suff=form[-lenght:]
    return base,suff

def getval(key,dic):
    for k,v in dic.items():
        if k.startswith(key):
            return v
    return None

def mkHabXpos(form,xpos='', lenght=0, accent=False, guess=False, force=False):
    if not lenght:
        lenght=4
    suffs={'wara':{'Aspect':'FREQ', 'Tense': 'PRES'},
    'tiwa': {'Aspect':'HAB'},
    'wera': {'Aspect':'FREQ', 'Tense': 'PAST'}}
    base, suff=parseWord(form,lenght)
    tag=suffs[suff]['Aspect']
    feats=[]
    feats.append(tag)
    tense=suffs[suff].get('Tense')
    if tense:
        feats.append(tense)
    new={}
    if accent:
        base=handleAccent(base,force=force)
    if not xpos:
        xpos='V'
    if not guess:
        parselist=getparselist(base)
        parse=filterparselist(xpos,parselist)[0]
        parse[1]=f"{parse[1]}+{'+'.join(feats)}"
        new['parselist']=[parse]
        return new
    if xpos == 'V':
        new=mkVerb(base,derivation=tag)
    elif xpos == 'N':
        pass
    else:
        new['parselist']=[[base, f"{xpos}+{tag}"]]
    return new

def mkNoun(form,orig=None,dic={},orig_form=''):
    feats=[]
    new={}
    if orig:
        new['OrigLang']=orig
    if orig_form:
        new['Orig']=orig_form
    number=dic.get('number')
    degree=dic.get('degree')
    derivation=dic.get('derivation')
    if degree:
        feats.append(degree)
    if derivation:
        feats.append(derivation)
    if not number:
        number=getNumber(form)['number']
    feats.append(number)
    new['parselist']=[[form.lower(), f"N+{'+'.join(feats)}"]]
    return new

def mkAdj(form,orig='pt',dic={}):
    feats=[]
    new={}
    if orig:
        new['OrigLang']=orig
    degree=dic.get('degree')
    derivation=dic.get('derivation')
    if degree:
        feats.append(degree)
    if derivation:
        feats.append(derivation)
    new['parselist']=[[form.lower(), f"A+{'+'.join(feats)}"]]
    return new


def getNumber(form):
    dic={}
    dic['number']='SG'
    if form.endswith('-itá'):
        dic['number']='PL'
    return dic

def mkAug(form,force=False):
    i=-4
    dic=getNumber(form)
    dic['degree']='AUG'
    number=dic.get('number')
    if number == 'PL':
        i=-8
    lemma=handleAccent(form[:i],force=force)
    return mkNoun(lemma,None,dic)

def mkCol(form):
    suff='tiwa'
    i=-len(suff)
    dic=getNumber(form)
    dic['derivation']='COL'
    number=dic.get('number')
    if number == 'PL':
        i-=-4
    lemma=handleAccent(form[:i])
    return mkNoun(lemma,None,dic)

def mkPrv(form):
    i=-4
    dic={}
    dic['derivation']='PRV'
    lemma=form[:i]
    return mkAdj(lemma,None,dic)

def mkClitic(lemma,upos):
    return [[lemma, upos]]

def mkUpos(lemma,upos):
    return [[lemma, upos]]

def mkIntj(lemma):
    return mkUpos(lemma,'INTJ')

def handleRedup(token):
    redup={}
    parts=token.split('-')
    if len(parts) == 2 and parts[1]:
        if parts[0].endswith(parts[1]):
            redup['form'],redup['lemma']=parts[0],parts[1]
    return redup

def handleAlomorph(form):
    return form.replace('ií','iwa')

def mkRoot(index):
    ROOT.append(index)

def handleRoot(tokenlist):
    rootid=0
    if ROOT:
        rootid=ROOT.pop()+1
        token=tokenlist.filter(id=rootid)[0]
        token['deprel']='root'
        token['head']=0
        for t in tokenlist:
            if t['id'] != rootid and t['head'] == 0:
                t['head']=rootid
                if not t['deprel']:
                    if isNominal(t['upos']) and t['id'] < rootid:
                        t['deprel']='nsubj'

def isNominal(upos):
    return upos in ['NOUN','PROPN','PRON']

def parseArgs(string):
    dic={}
    #oper='='
    #index=string.index(oper)
    #parts=string[index+1:].split(':')
    parts=string.split(':')
    dic['func'] = parts[0]
    for part in parts[1:]:
        arg,val=part.split('|')
        dic[arg]=val
    return dic

def parseTag(tag):
    values={'t': True, 'f': 'False'}
    sep=':'
    dic={}
    if sep in tag:
        args=parseArgs(tag)
        for k,v in args.items():
            value = values.get(v)
            if value:
                args[k]=values[v]
            else:
                if k == 'l':
                    args[k]=int(v)
        dic.update(args)
    else:
        dic['func']=tag
    return dic

def mkConlluSentence(tokens):
    ROOT.clear()
    tokenlist=TokenList()
    ident=1
    start=0
    for token in tokens:
        old=token
        tag=MULTIWORDTOKENS.get('xpos')
        root=False
        if '/' in token:
            token,tag=token.split('/')
            if '@' in tag:
                root=True
                tag=tag[:-1]
        dic=handleHyphen(token)
        new={}
        form=dic.get('form')
        redup=handleRedup(token)
        parselist=[]
        lemma=dic.get('lemma')
        upos=dic.get('upos') # TODO: problably not used
        xpos=dic.get('xpos')
        host=dic.get('host')
        alomorph=form.lower()
        if redup:
            parselist=getparselist(redup['form'])
        else:
            if lemma:
                parselist=mkClitic(lemma,xpos)
            else:
                if host:
                    alomorph=handleAlomorph(form.lower())
                    parselist=getparselist(alomorph)
                else:
                    parselist=getparselist(form.lower())
        if tag:
            tagparse=parseTag(tag)
            t=tagparse.get('func')
            if t:
                tag=t
            orig=tagparse.get('o')
            orig_form=tagparse.get('s')
            force=tagparse.get('f')
            newparselist=[]
            if tag == '=p':
                newparselist=mkPropn(token)
            elif tag == '=adv':
                newparselist=mkAdv(token)
            elif tag == '=n':
                new=mkNoun(form,orig=orig,orig_form=orig_form)
                newparselist=new['parselist']
            elif tag == '=a':
                new=mkAdj(form,orig=orig)
                newparselist=new['parselist']
            elif tag == '=v':
                new=mkVerb(form,orig=orig,orig_form=orig_form)
                newparselist=new['parselist']
            elif tag == '=hab':
                new=mkHab(form)
                newparselist=new['parselist']
            elif tag == '=col':
                new=mkCol(form)
                newparselist=new['parselist']
            elif tag == '=hab=sconj':
                new=mkHabSconj(form)
                newparselist=new['parselist']
            elif tag == '=mkhab':
                xpos=tagparse.get('x')
                if xpos:
                    xpos=xpos.upper()
                new=mkHabXpos(  form,
                                xpos=tagparse.get('x'),
                                lenght=tagparse.get('l'),
                                accent=tagparse.get('a'),
                                guess=tagparse.get('g'),
                                force=force
                                )
                newparselist=new['parselist']
            elif tag == '=aug':
                new=mkAug(form,force)
                newparselist=new['parselist']
            elif tag == '=prv':
                new=mkPrv(form)
                newparselist=new['parselist']
            elif tag == '=intj':
                newparselist=mkIntj(form)
            #elif tag == '=r':
            #    mkRoot(tokens.index(old))
            else:
                newparselist=filterparselist(tag,parselist)
            if newparselist:
                parselist=newparselist
        if root:
            mkRoot(tokens.index(old))
        entries=extract_feats(parselist)
        for entry in entries:
            if entry.get('pos') == 'PUNCT':
                start=start-1
            t=mkConlluToken(form,entry,start=start, ident=ident)
            if dic.get('hyphen') or dic.get('underscore'):
                handleHyphenSepToken(t)
            if new:
                orig=new.get('OrigLang')
                orig_form=new.get('Orig')
                if orig:
                    t['misc'].update({'OrigLang': orig})
                if orig_form:
                    t['misc'].update({'Orig': orig_form})
            if host and form.lower() != alomorph:
                t['misc'].update({'Alomorph': form})
            tokenlist.append(t)
        start=start+len(token)+1
        ident+=1
    handleSpaceAfter(tokenlist)
    addFeatures(tokenlist)
    insertMultitokenWord(tokenlist)
    handleRoot(tokenlist)
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

def insertAnnotator(sentences,annotator):
    for sent in sentences:
        sent.metadata.update({'text_annotator':annotator})

def extract_sents(line=None,lines=None):
    sents=[]
    if lines:
        for sent in lines.split("\n"):
            sents.append(sent.strip())
    else:
        sents=[sent for sent in re.split(r"\s+-\s+|[)(]",line) if sent]
    return sents

def ppText(sents,pref='',textid=0,index=0,sentid=0):
    output=[]
    if pref:
        output.append(f"# sent_id = {pref}:{textid}:{index}:{sentid}")
    yrl,eng,por=sents[0],sents[1],sents[2]
    template=f"# text = {yrl}\n# text_eng = {eng}\n# text_por = {por}"
    dic={}
    if len(sents) > 3:
        for sent in sents[3:]:
            if sent.startswith('(') and sent.endswith(')'):
                dic['source']=sent[1:-1]
            else:
                dic['orig']=sent
    output.append(template)
    for k,v in dic.items():
        output.append(f"# text_{k} = {v}")
    return '\n'.join(output)

def mkText(text):
	print(ppText(extract_sents(lines=text)))

def extractYrl(sent):
    return re.sub(REMOVE,'',sent)

def handleSents(sents,pref,textid,index,sentid,annotator):
    yrl=extractYrl(sents[0])
    sents[1]=f"({sents[1]})"
    output=[]
    if len(sents) == 5:
        output.append(ppText([yrl,sents[3],
        sents[2],
        sents[1],
        sents[4]],
        pref,textid,index,sentid))
    else:
        output.append(ppText([yrl,
        sents[3],
        sents[2],
        sents[1]],
        pref,textid,index,sentid))
    tk=parseSentence(sents[0])
    includeAnnotator(output,annotator)
    output.append(tk.serialize())
    return output

def includeAnnotator(output,annotator):
    output.append(f"# text_annotator = {annotator}")

def handleParse(output,copyboard=True):
    outstring='\n'.join(output)
    if copyboard:
        import pyperclip
        pyperclip.copy(outstring)
    print(outstring)

def TreebankSentence(text='',pref='',textid=0,index=0,sentid=0,copyboard=True,annotator='LFdeA'):
    if not text:
        text='''Aité kwá sera waá piranha yakunheseri
        aé i turususá i apuã waá rupí, asuí sanha
        saimbé yuíri. (Payema, 68, adap.)
        - Este que se chama piranha nós o conhecemos
        por seu formato oval e por seus dentes afiados.
        - This one called piranha we know for its oval shape
        and its sharp teeth.'''.replace('\n','') # Avila (2021, p. 256)
        text=re.sub(r"\s+",' ',text)
    sents=extract_sents(text)
    handleParse(handleSents(sents, pref,textid,index,sentid,annotator),copyboard=copyboard)

def includeTranslation(example):
    from deep_translator import GoogleTranslator
    parts=extract_sents(example)
    text_por=parts[-1]
    text_eng=GoogleTranslator(source='pt', target='en').translate(text_por)
    parts.append(text_eng)
    return parts

def parseExample(example,pref,textid,index,sentid,copyboard=True,annotator=ANNOTATOR):
	sents=includeTranslation(example)
	handleParse(handleSents(sents, pref,textid,index,sentid,annotator),copyboard=copyboard)

def endswithNTU(word):
    return word.endswith(NTU)

def extractNTU(glossary):
    return [entry['lemma'] for entry in filter(lambda x: endswithNTU(x['lemma']),glossary)]

def endswithSuff(suff,word):
    return word.endswith(suff)

def extractSuff(suff,glossary):
    return [entry['lemma'] for entry in filter(lambda x: endswithSuff(suff,x['lemma']),glossary)]

def inGlossary(word):
    wordlist=extractNTU(GLOSSARY)
    if word in wordlist:
        return True
    return False

def withSuff(suff,word):
    wordlist=extractSuff(suff,GLOSSARY)
    if word.lower() in wordlist:
        return True
    return False

def hasCliticAdv(token): # TODO: possibly deprecated
    if endswithNTU(token) and not inGlossary(token):
        return handleAccent(token[:-len(NTU)])
    return ''

def startswithNasal(suff):
    return suff != NTU and suff[0] in 'mn'

def hasClitic(suff,token):
    if endswithSuff(suff,token) and not withSuff(suff,token):
            nasal=startswithNasal(suff)
            return handleAccent(token[:-len(suff)],nasal)
    return ''

def mkHost(host,clitic,token,xpos=''):
    dic={}
    dic['host']=host
    dic['suff']=clitic
    if xpos:
        dic['xpos']=xpos
    dic['multiwordtoken']=token
    return dic

def extractHost(token):
    dic={}
    if token.lower() == 'maita':
        return mkHost('mayé',TA,token,'ADVRA')
    for clitic in NONHYPHEN:
        host=hasClitic(clitic,token)
        if host:
            return mkHost(host,clitic,token)
    return dic

def splitMultiWordTokens(tokens):
    MULTIWORDTOKENS.clear()
    sep=[d['lemma'] for d in AUX]
    sep.extend(CLITICS)
    newlist=[]
    for t in tokens:
        dic=extractHost(t)
        if HYPHEN in t:
            index=t.index(HYPHEN)
            first=t[:index]
            second=t[index:]
            if second[1:] in sep:
                if second[1:] in CLITICS:
                    first=f"{first}-"
                newlist.extend([first,second])
            else: #TODO: has hyphen and clitic "-ntu"
                newlist.append(t)
        elif dic: # TODO: if dic ...?
            host=dic['host']
            suff=dic['suff']
            mwt=dic['multiwordtoken']
            xpos=dic.get('xpos')
            if xpos:
                MULTIWORDTOKENS['xpos']=xpos
            MULTIWORDTOKENS[host]=mwt
            newlist.extend([host,f"{UNDERSCORE}{suff}"])
        else:
            newlist.append(t)
    return newlist

def parseSentence(sent):
    tokens=splitMultiWordTokens(tokenize(sent))
    tk=mkConlluSentence(tokens)
    return tk

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

def TreebankSentences(text,pref='MooreFP1994',textid=0,index=0,sentid=1,copyboard=True, annotator=ANNOTATOR):
    output=[]
    dic=mkDict(text)
    i=0
    sentid=sentid
    index=index
    source=dic.get('source')
    yrl,eng,por=dic['yrl'],dic['eng'],dic['por']
    while(i < len(yrl)):
        output.append(
        ppText(
        [extractYrl(yrl[i]),eng[i],por[i]],
        pref,textid,index,sentid)
        )
        if source:
            output.append(f"# text_source = {source}")
        tk=parseSentence(yrl[i])
        includeAnnotator(output,annotator)
        output.append(tk.serialize())
        sentid+=1
        index+=1
        i+=1
    handleParse(output,copyboard=copyboard)

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

def writeSentsConllu(sentences,outfile):
    with open(outfile, 'w') as f:
        for sent in sentences:
            print(sent.serialize(),end='',file=f)

def insertAnnotatorInSents(infile,outfile,annotator):
    sents=extractConlluSents(infile)
    insertAnnotator(sents,annotator)
    writeSentsConllu(sents,outfile)
