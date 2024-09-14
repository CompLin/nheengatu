#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Author: Leonel Figueiredo de Alencar
# Last update: September 13, 2024

from Nheengatagger import getparselist, tokenize, DASHES, ELLIPSIS
from BuildDictionary import DIR,MAPPING, extract_feats, loadGlossary, loadLexicon, extractTags, isAux, accent, guessVerb, PRONOUNS, extractArchaicLemmas, IMPIND
from Metadata import Mindlin, PEOPLE, mkReviewer
from conllu.models import Token,TokenList
from conllu import parse
from io import open
from conllu import parse_incr
import re, os

# default annotator's name abbreviation
ANNOTATOR = PEOPLE['leo']

# metadata attributes
ANNOTATOR_ATT = 'text_annotator' #TODO: this is deprecated as of the new version of Metadata

# path to treebank file
TREEBANK_FILE='yrl_complin-ud-test.conllu'
TREEBANK_DIR='corpus/universal-dependencies'
TREEBANK_PATH=os.path.join(DIR,TREEBANK_DIR, TREEBANK_FILE)

# set with lexicalized reduplications
LEXREDUP=set()

# reduplication tag
REDUP='RED'

# tag for the middle, passive, reflexive or reciprocal voice
MEDPASS='MID' # mediopassive voice

# prefix for the middle, passive, reflexive or reciprocal voice
YU = 'yu'

VOICE={'MID' : 'Mid,Pass', 'ACT' : 'Act'}

# set with all treebank sentences
TREEBANK_SENTS=[]

# single and double quotes
DOUBQUOMARK='"'
QUOTES='''"''"'''

# punctuation introducing a dependent clause
# TODO: the comma needs a special treatment when introducing non-clausal dependents
COMMA=','
COLON=':'
SEMICOLON=';'
DEPPUNCT=[COMMA,COLON,SEMICOLON]
DEPPUNCT.extend(DASHES)

# locative form
LOCATIVE=re.compile(r"forma locativa de (\w+)")

# characters to be removed from input sentence
REMOVE=re.compile(r"/=?[\w\+]*([:=|]\w+)*@?")

# regex defining pattern to parse examples
PARTS=re.compile(r"\s+-\s+|[)(]")

PARTS1=re.compile(r"[)(]")

PARTS2=re.compile(r"\s*-\s+")

# regex for squeezing white space
SQUEEZE=re.compile(r"\s{2,}")

# regex matching tags like 'N+ABS', 'N+NCONT', 'ABS', 'NCONT', etc.
TAGSEQ=re.compile(r'(^\w+\+)?(\w+)\b')

# separators of multiword tokens
HYPHEN='-'
UNDERSCORE='_'

# sentence terminators
SENTTERM=('.','?','!')

# Multiword token TODO: reimplement as list of dictionaries (see below)
MULTIWORDTOKENS={}

# Case of second class pronouns
CASE="Gen"

# Enclitic items
# TODO: extract from glossary
# hyphenated postposition
PE='pe'
# content question particle
TACL='ta'

CLITICENTRIES={
PE : {'lemma':'upé','xpos':'ADP'},
TACL : {'lemma':'taá','xpos':'CQ'}
}
#CLITICS=[list(dic.keys())[0] for dic in CLITICENTRIES]
CLITICS=list(CLITICENTRIES.keys())

# non-hyphenated clitics
# clitic alomorphs of postposition 'upé'
ME='me'
PI='pi'

# clitic particle
WERA='wera'

# clitic adpositions
WARA='wara'
# normalized lemmatization of alomorph 'pi'
UPE='upé'
PI=UPE

# clitic adverb "-ntu"
NTU='ntu'

# clitic question particle "-ta"
TA='taá'

NONHYPHEN=[NTU,ME,WARA,WERA]

ROOT=[]

GLOSSARY=loadGlossary(jsonformat=os.path.join(DIR,"glossary.json"))
LEXICON=loadLexicon()

# archaic lemmas
ARCHAIC_LEMMAS=extractArchaicLemmas(GLOSSARY)

UDTAGS={'PL': 'Plur', 'SG': 'Sing',
'V': 'VERB', 'N': 'NOUN', 'LOC' : 'N', 'V2': 'VERB', 'V3': 'VERB',
'VSUFF': 'VERB',
'A': 'ADJ', 'CONJ' : 'C|SCONJ', 'NFIN' : 'Inf', 'FIN' : 'Fin', 'ART' : 'DET',
'COP' : 'AUX', 'PREP' : 'ADP', 'SCONJR': 'SCONJ',
'AUXN' : 'AUX', 'AUXFR' : 'AUX', 'AUXFS' : 'AUX',
'CARD' : 'NUM', 'ORD' : 'ADJ', 'ELIP' : 'PUNCT',
'COL':'Coll', 'PRV': 'Priv', 'RELF' : 'PRON', 'RED': 'Red', 'PROND': 'PRON'}

# TODO: extractDemonstratives()
# TODO: implement function mapping these keys to 'DET'
DET =  {'DEM' : 'DET', 'INDQ' : 'DET',
'INT' : 'DET', 'ART' : 'DET', 'DEMX' : 'DET', 'DEMS' : 'DET',
'DEMSN' : 'DET', 'IND' : 'DET', 'TOT' : 'DET'}

# list of part-of-speech tags in determiner position
DETERMINERS=("DET","NUM")

DEIXIS={'DEMS' : 'Remt', 'DEMSN' : 'Remt','DEMX' : 'Prox', 'I': 'Remt', 'X': 'Prox'}

ADVTYPE={'ADVO':'Tim','ADVD':'Loc', 'ADVS':'Deg', 'ADVJ':'Cau', 'ADVG':'Deg', 'ADVP':'Con'}

WH_ADVTYPE={'ADVC':'Loc', 'ADVA':'Man',
'ADVT':'Tim', 'ADVM':'Mod', 'ADVU': 'Cau'}

WH_ADV={'ADVR': 'Int', 'ADVL':'Rel', 'ADVN': 'Ind'}
DEM_ADV={'ADVD': 'Dem'}
ADVPRONTYPE={}
ADVPRONTYPE.update(WH_ADV)
ADVPRONTYPE.update(DEM_ADV)

ADVTYPE.update(WH_ADVTYPE)

def extract_redup(glossary=GLOSSARY):
    lexredup=set()
    entries=list(filter(lambda x: HYPHEN in x['lemma'], glossary))
    for entry in entries:
        lemma=entry['lemma']
        parts=lemma.split(HYPHEN)
        if len(parts) == 2 and parts[0] == parts[1]:
            lexredup.add(lemma)
    return lexredup

def getRelPrefix(token):
    pref=''
    firstchar=token[0]
    if firstchar.lower() in ('r','s','t'):
        pref=firstchar
    return pref

def extractLocativeNouns(glossary=GLOSSARY):
    locatives=list(filter(lambda x: 's. loc.' == x.get('pos'), glossary))
    for entry in locatives:
        gloss=entry['gloss']
        entry['base']=LOCATIVE.search(gloss).groups()[0]
        entry['prefix']=getRelPrefix(entry['base'])
    return locatives

LOCATIVES=extractLocativeNouns()

LEXREDUP=extract_redup()

def getLocEntry(form):
    def handleRelForm(entry,form):
        rel=entry.get('rel')
        if not rel:
            rel=''
        return form in rel
    entries=list(filter(lambda entry: entry.get('lemma') == form or handleRelForm(entry,form),LOCATIVES))
    if entries:
        return entries[0]
    else:
        return {}

def extractTreebankSents(infile=TREEBANK_PATH):
    sents=extractConlluSents(infile)
    for sent in sents:
        text=sent.metadata.get('text_orig')
        if not text:
            text=sent.metadata.get('text')
        TREEBANK_SENTS.append(text)

def checkSentence(sent):
    if not TREEBANK_SENTS:
        extractTreebankSents()
    sents=list(filter(lambda x:x == sent, TREEBANK_SENTS))
    if sents:
        return True
    return False

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
        misc=t.get('misc')
        if misc:
            value=incrementRange(misc['TokenRange'],i)
            misc['TokenRange']=value

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

def WordsOfLength(length,pos):
    glossary=loadGlossary()
    return list(filter(lambda x:  len(x['lemma']) == length and x['pos'] == pos,glossary))

def includeAdpType(token):
    mapping={'ADP' : 'Post', 'PREP' : 'Prep'}
    adptype=mapping.get(token['upos'])
    if adptype:
        updateFeats(token,'AdpType',adptype)
        token['feats']=sortDict(token['feats'])

def mkConlluToken(word,entry,head=0, deprel=None, start=0, ident=1, deps=None):
    mapping={'ADP' : 'case', 'SCONJ':'mark',
    'VERB':'root',
    'PUNCT':'punct'}
    modernform={}
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
    case=entry.get('case')
    degree=entry.get('degree')
    derivation=entry.get('derivation')
    voice=entry.get('voice')
    redup=entry.get('redup')
    aspect=entry.get('aspect')
    tense=entry.get('tense')
    vform=entry.get('vform')
    mood=entry.get('mood')
    rel=entry.get('rel')
    style=entry.get('style')
    if person:
        feats['Person']=person
        #if token['upos']=='VERB': # TODO makes the verification below of vform redundant (include AUX)
            #feats['VerbForm']='Fin'
    if vform: # TODO problably redundant
        feats['VerbForm']=getudtag(vform)
    if number:
        feats['Number']=getudtag(number)
    if rel:
        feats['Rel']=RelAbbr(rel)
        handleNCont(upos,feats)
    if degree:
        feats['Degree']=f"{degree.title()}"
    if aspect:
        feats['Aspect']=f"{aspect.title()}"
    if voice:
        feats['Voice']=VOICE[voice]
    if mood:
        value=f"{mood.title()}"
        if mood == IMPIND:
            value='Imp,Ind'
        feats['Mood']=value
    if tense:
        feats['Tense']=f"{tense.title()}"
    if derivation:
        feats['Derivation']=UDTAGS.get(derivation)
    if redup:
        feats['Red']='Yes'
    if case:
        feats['Case']=case.title()
    if style:
        feats['Style']=style.title()
        entries=list(filter(lambda entry: word.lower() == entry['ancient'] ,ARCHAIC_LEMMAS))
        if entries:
            modern=entries[0]['modern']
            modernform['ModernLemma']=modern
            if word.istitle():
                modern=modern.title()
            modernform['ModernForm']=modern
        else:
            entries=list(filter(lambda entry: entry['xpos'] == 'PREF' and word.lower().startswith(entry['ancient'].strip(HYPHEN)),ARCHAIC_LEMMAS))
            if entries:
                modern=entries[0]['modern'].strip(HYPHEN)
                ancient=entries[0]['ancient'].strip(HYPHEN)
                if word.istitle():
                    modern=modern.title()
                modernform['ModernForm']=f"{modern}{word[len(ancient):]}"
    if feats:
        token['feats']=feats
    else:
        token['feats']=None
    if token['xpos'] in ('REL', 'RELF'):
        updateFeats(token,'PronType','Rel')
    #elif token['xpos'] == 'ADVR':
    #    updateFeats(token,'PronType','Int')
    #elif token['xpos'] == 'ADVL':
    #    updateFeats(token,'PronType','Rel')
    elif token['xpos'] in ('ORD','ADVO'):
        updateFeats(token,'NumType','Ord')
    includeAdvType(token)
    includeAdpType(token)
    token['head']=head
    dprl=mapping.get(upos)
    if not dprl:
        feats=token.get('feats')
        if feats and feats.get('Case') == 'Dat':
            dprl = 'iobj'
        else:
            dprl=deprel
    token['deprel']=dprl
    token['deps']=deps
    token['misc']={'TokenRange': f'{start}:{end}'}
    if modernform:
        token['misc'].update(modernform)
    return token

def spaceBefore(token):
    if token['xpos'] == 'ELIP' or token['lemma'] in DEPPUNCT:
        return True

def insertNoSpaceAfter(token):
    if not spaceBefore(token):
        token['misc'].update({'SpaceAfter' : 'No'})

def handleSpaceAfter(tokenlist):
    i=0
    while(i<len(tokenlist)-1):
        token=tokenlist[i]
        nexttoken=tokenlist[i+1]
        if token['lemma'] == ',':
            misc=token.get('misc')
            if misc.get('SpaceAfter'):
                misc.pop('SpaceAfter')
        elif token['lemma'] == ELLIPSIS and nexttoken['lemma'] in SENTTERM+(',',):
            token['misc'].update({'SpaceAfter' : 'No'})
        i+=1
    tokens=tokenlist.filter(upos='PUNCT')
    quotes=[token for token in tokenlist if token['form'] in QUOTES]
    if tokens:
        previousHasSpaceAfter=False
        i=0
        c=len(tokenlist)
        while(i<len(tokens)):
            precedentlist=tokenlist.filter(id=tokens[i]['id']-1)
            if tokens[i] in quotes:
                if previousHasSpaceAfter:
                    handlePrecedent(precedentlist)
                    quotid=previousCat(tokens[i],quotes)
                    quote=tokens.filter(id=quotid)[0]
                    tokens[i]['head']=quote['head']
                    previousHasSpaceAfter=False
                else:
                    insertNoSpaceAfter(tokens[i])
                    tokenid=tokens[i]['id']
                    head=tokenlist.filter(id=tokenid+1)[0]
                    tokens[i]['head']=head['id']
                    previousHasSpaceAfter=True
            else:
                handlePrecedent(precedentlist)
            if tokens[i]['lemma'] in SENTTERM:
                insertNoSpaceAfter(tokens[i])
            i+=1

def handlePrecedent(precedentlist):
    for precedent in precedentlist:
        insertNoSpaceAfter(precedent)

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
    'return True if token is a verb or an existential or presentative particle'
    if token.get('upos') == 'VERB' or token.get('xpos') in ('EXST', 'PRSV'):
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
    if xpos not in PRONOUNS:
        prontype=xpos.title()
        if len(prontype) > 3 and prontype not in ('Card',):
            prontype=prontype[:3]
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
    start=0
    while(i < len(nouns)-1):
        token=nouns[i]
        j=i+1
        nexttoken=nouns[j]
        feats=nexttoken.get('feats')
        rel=''
        if feats:
            rel=feats.get('Rel')
        if hasNext(token,nexttoken):
            if rel == 'Cont' or (sameHead(token,nexttoken) and sameDeprel(token,nexttoken)):
                start=j
                token['deprel']='nmod:poss'
                token['head']=nexttoken['id']
        i+=1
    GenitiveConstruction(nouns,tokenlist)
    return start

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
    'PRSV': {'PartType': 'Prs'},
    'CERT': {'PartType': 'Mod'},
    'PREC': {'PartType': 'Mod'},
    'ASSUM': {'PartType': 'Mod'},
    'PROTST': {'PartType': 'Mod'},
    'MOD': {'PartType': 'Mod'},
    'TOTAL': {'PartType': 'Quant', 'Aspect':'Compl'},
    'COND': {'PartType': 'Mod', 'Mood': 'Cnd'},
    'NEC': {'PartType': 'Mod', 'Mood': 'Nec'},
    'FOC': {'PartType': 'Emp', 'Foc': 'Yes'},
    'FREQ': {'Aspect':'Freq', 'Tense' : 'Past'},
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
    elif xpos == 'FREQ':
        for k,v in mapping[xpos].items():
            updateFeats(token,k, v)
        headPartPreviousVerb(token,verbs)
    elif xpos == 'CERT' or xpos == 'ASSUM':
        updateFeats(token,'PartType', 'Mod')
        token['head']=getAdvHead(token,tokenlist,verbs)
        # headPartPreviousVerb(token,verbs)
    elif xpos == 'NEC':
        updateFeats(token,'PartType', 'Mod')
        headPartNextVerb(token,verbs)
    elif xpos == 'PREC':
        updateFeats(token,'PartType', 'Mod')
        headPartNextVerb(token,verbs)
    elif xpos == 'MOD':
        updateFeats(token,'PartType', 'Mod')
        headPartPreviousVerb(token,verbs)
    elif xpos == 'PFV':
        #headPartPreviousVerb(token,verbs)
        token['head']=getAdvHead(token,tokenlist,verbs)
        updateFeats(token,'Aspect','Perf')
    elif xpos == 'TOTAL':
        #headPartPreviousVerb(token,verbs)
        token['head']=getAdvHead(token,tokenlist,verbs)
        updateFeats(token,'Aspect','Compl')
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
        if previous:
            token['head']=previous['id']
        updateFeats(token,'PartType', 'Emp')
        updateFeats(token,'Foc', 'Yes')
    elif xpos == 'EXST' or xpos == 'PRSV':
        if len(verbs) > 0:
            headPartNextVerb(token,verbs)
        else:
            token['head']=0
            token['deprel']='root'
            verbs.append(token)
        value=mapping[xpos]['PartType']
        updateFeats(token,'PartType', value)

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
    headSconj(token,verbs) # TODO: redundant? See below.

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
    headSconj(token,verbs) # TODO: redundant? See above.

def headSconj(token,verbs):
    headid=token['head']
    headlist=verbs.filter(id=headid)
    if headlist:
        head=headlist[0]
        head['deprel']='advcl'
        head['head']=getHeadVerb(head,verbs)

def handlePosp(token,tokenlist,nouns):
    previous=getPreviousToken(token,tokenlist)
    if previous:
        if previous['upos'] == 'ADV':
            token['head']=previous['id']
            previous['deprel']='obl'
        elif previous['upos'] not in ('NOUN','PRON','PROPN'):
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
    if token['xpos'] not in ('CARD',):
        verbid=nextVerb(token,verbs)
        tokenid=token['id']
        if verbid:
            if nounid > verbid or not nounid:
                token['upos']='PRON'
                setDeprel(token,verbid,'nsubj')
        elif not nounid:
            token['upos']='PRON'
            headid=previousVerb(token,verbs)
            setDeprel(token,headid,'obj')

def handlePronSeq(tokenlist):
    c=len(tokenlist)
    i=0
    while(i < c-1):
        token=tokenlist[i]
        if token['upos']=='PRON':
            next=tokenlist[i+1]
            if next['upos']=='PRON':
                if token['deprel'] == next['deprel']:
                    token['deprel']='det'
                    token['head']=next['id']
        i+=1

def handleDetNum(upos,token,nextToken,tokenlist,verbs):
    Pron='Pron'
    if upos == 'NUM':
        Pron='Num'
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
    feats=nextToken.get('feats')
    if feats:
        rel=feats.get('Rel')
        if rel == 'Cont':
            token['upos']='PRON'
            token['head']=nextToken['id']
            token['deprel']='nmod:poss'
    deprel={'DET': 'det', 'NUM': 'nummod'}
    delta=2
    nouns=TokensOfCatList(tokenlist,'NOUN')
    nounid=nextCat(token,nouns)
    if not nounid:
        nounid=previousCat(token,nouns)
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

def isCop(token):
    return token['lemma'] == 'ikú'

def mkCop(token):
    #token['deprel'] = 'cop' 070723
    token['xpos'] = 'COP'
    #token['upos'] = 'AUX' 070723

def AdjAdvorOblRoot(root,cop,overwrite=True):
    rootid=root['id']
    setDeprel(cop,rootid,'cop',overwrite)
    cop['upos']='AUX'
    root['deprel']='root'
    root['head']=0

def getAdjAdvRoot(tokenlist,cop,deps,overwrite):
    rootid=None
    for upos in ['ADJ','ADV']:
        rootid=getUposRoot(tokenlist,upos,cop,deps,overwrite)
        if rootid != None:
            return rootid

def getUposRoot(tokenlist,upos,cop,deps,overwrite):
    for token in tokenlist:
        if token['upos'] == upos:
            AdjAdvorOblRoot(token,cop,overwrite)
            rootid=token['id']
            if token in deps:
                deps.remove(token)
            return rootid

def handleCopClause(tokenlist,copulas):
    cop=copulas[0]
    copid=cop['id']
    rootid=copid
    deps=tokenlist.filter(head=copid)
    obls=deps.filter(deprel='obl')
    for obl in obls:
        if obl['id'] > copid:
            AdjAdvorOblRoot(obl,cop)
            rootid=obl['id']
            deps.remove(obl)
            break
    if rootid == copid:
        advmods=deps.filter(deprel='advmod')
        for advmod in advmods:
            if advmod['id'] > copid:
                AdjAdvorOblRoot(advmod,cop)
                rootid=advmod['id']
                deps.remove(advmod)
                break
    if rootid == copid:
        tokenid=getAdjAdvRoot(tokenlist,cop,deps,True)
        if tokenid:
            rootid=tokenid
    for dep in deps:
        dep['head']=rootid

def isAdvCl(verb,tokenlist,delta=1):
    verbid=verb['id']
    sconjs=verbid+delta
    return tokenlist.filter(id=sconjs)

def handleAux(tokenlist):
    verbs=VerbIdsList(tokenlist)
    puncts=TokensOfCatList(tokenlist,'PUNCT')
    c=len(verbs)
    if c == 1:
        if isCop(verbs[0]):
            mkCop(verbs[0])
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
                        handleSconjList(tokenlist,verbs)
                        advcl=tokenlist.filter(head=headid,deprel='mark')
                        #if not isAdvCl(verb,tokenlist):
                        if not advcl:
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

def isNounModifier(token):
    return token['upos'] in ('DET','PRON')

def assignSubj(rootid,nouns):
    i=-1
    while(i>=-len(nouns)):
        noun=nouns[i]
        if noun['id'] < rootid:
            setAttribute(noun,'deprel','nsubj')
            setAttribute(noun,'head',rootid)
            break
        i=i-1

def handleOblRoot(tokenlist):
    copulas=tokenlist.filter(xpos='COP')
    if copulas:
        handleCopClause(tokenlist,copulas)
    else:
        verbs=tokenlist.filter(upos='VERB')
        if not verbs:
            handleOblRootNoCop(tokenlist)

def handleOblRootNoCop(tokenlist):
    obls=tokenlist.filter(deprel='obl')
    puncts=tokenlist.filter(deprel='punct')
    if obls:
        nouns=extractNominals(tokenlist)
        root=obls[-1]
        root['deprel']='root'
        root['head']=0
        rootid=root['id']
        if puncts:
            puncts[-1]['head']=rootid
        assignSubj(rootid,nouns)

def extractNominals(tokenlist):
    nouns=TokensOfCatList(tokenlist,'NOUN')
    nouns.extend(TokensOfCatList(tokenlist,'PRON'))
    nouns.extend(TokensOfCatList(tokenlist,'PROPN'))
    return nouns

def AdjOrNounRoot(tokenlist):
    adjs=TokensOfCatList(tokenlist,'ADJ')
    nouns=extractNominals(tokenlist)
    #cop=tokenlist.filter(deprel='cop') 070723
    cop=tokenlist.filter(xpos='COP')
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
                    setAttribute(noun,'head',rootid)
                    break
                i=i-1
    if cop:
        cop[0]['head'] = rootid
    assignHead(tokenlist,rootid)

def GenitiveConstruction(nouns,tokenlist):
    i=0
    c=len(nouns)-1
    while(i<c):
        this=nouns[i]
        if not this['deprel']:
            for token in tokenlist[this['id']:]:
                if token['upos'] in ('AUX','VERB','ADV'):
                    return
            j=i+1
            if j <=c:
                this['deprel']='nmod:poss'
                next=nouns[j]
                this['head']=next['id']
        i+=1

def handleExpletive0(tokenlist): # TODO: handle non-adjacent subject
    i=1
    while(i<len(tokenlist)):
        this=tokenlist[i]
        previous=tokenlist[i-1]
        if this['xpos'] == 'PRON2' and this['deprel'] == 'nsubj':
            if previous['deprel'] == 'nsubj':
                this['deprel'] = 'expl'
        i+=1

def handleExpletive(tokenlist): # TODO: handle non-adjacent subject
    i=1
    while(i<len(tokenlist)):
        this=tokenlist[i]
        if this['xpos'] == 'PRON2' and this['deprel'] == 'nsubj':
            headid=this['head']
            for token in tokenlist[:i]:
                if token['head'] == headid and token['deprel'] == 'nsubj':
                    this['deprel'] = 'expl'
                    break
        i+=1

def handlePunct(token,nextToken,tokenlist,verbs):
    if nextToken['lemma'] in DEPPUNCT:
        nextToken['head'] = nextVerb(token,verbs)
    elif nextToken['xpos'] == 'ELIP':
         updateFeats(nextToken,'PunctType','Elip')
         if token['upos'] == 'PUNCT':
             rootlist=tokenlist.filter(deprel='root')
             if rootlist:
                 token['head']=rootlist[0]['id']
                 nextToken['head'] = token['head']
         else:
            nextToken['head'] = previousVerb(nextToken,verbs)
    elif nextToken['lemma'] not in QUOTES:
        headlist=tokenlist.filter(deprel='root')
        head=1
        if headlist:
            head=headlist[0]['id']
        nextToken['head']=head

def handleComma(token,tokenlist):
    verbs=VerbsList(tokenlist)
    token['head'] = nextVerb(token,verbs)

def handleStartPunct(tokenlist):
    first=tokenlist[0]
    if first['upos'] == 'PUNCT' and first['lemma'] in DASHES:
        root=tokenlist.filter(deprel='root')
        if root:
            first['head']=root[0]['id']

def mkPunctToken(punct,start,ident):
    parselist=getparselist(punct)
    entries=extract_feats(parselist)
    return mkConlluToken(punct,entries[0],start=start,ident=ident)

def insertPunct(punct,tokenid,tokenlist):
    position=tokenid-1
    previous=tokenlist.filter(id=position)[0]
    insertNoSpaceAfter(previous)
    start=int(getStartEnd(previous,False)['end'])
    token=mkPunctToken(punct,start,tokenid)
    incrementSentId(tokenlist,tokenid)
    tokenlist.insert(position,token)
    comma=tokenlist.filter(id=tokenid)[0]
    handleComma(comma,tokenlist) # TODO: adapt this to hanlde other punctuation
    incrementTokenRange(tokenlist[tokenid+1:])
    
def separateClitic(data,token=None,hostid=29,tokenlist=None):
    '''Separate a clitic attached to a host with token id 29, e.g., 'uikuwera',placing the clitic on the next position, thereby incrementing the ids of the following tokens. See issue #518.
    '''
    tokenlist=parse(data)[0]
    tokenid=hostid+1
    incrementSentId(tokenlist,tokenid)
    base=tokenlist[hostid-1]
    tk=parseSentence(base['form'])
    mwt,head,token=tk
    token['head']=base['id']
    base['misc'].pop('TokenRange')
    sp=base['misc'].get('SpaceAfter')
    if not base.get('misc'):
        base['misc']=None
    lemma=base['lemma']
    last=lemma[-1]
    if last in ('á','í','ú'):
        base['form']=f"{head['form'][:-1]}{last}"
    else:
        base['form']=head['form']
    token['id']=tokenid
    token['deprel']='advmod'
    for att in 'Aspect','Tense':
        token['feats'].update({att : base['feats'].pop(att)})
    tokenlist.insert(hostid,token)
    mwt['id']=(base['id'],'-',token['id'])
    if sp:
        base['misc'].pop('SpaceAfter')
        misc=mwt.get('misc')
        if misc:
            mwt['misc'].update({'SpaceAfter' : sp})
        else:
            mwt['misc']=sp
    tokenlist.insert(hostid-1,mwt)
    incrementTokenRange(tokenlist[tokenid+1:])
    sortTokens(tokenlist)
    print(tokenlist.serialize())

def issue365(sents,lemma='pitérupi',display=False):
	i=0
	edited=[]
	for sent in sents:
		tk=sent.filter(lemma=lemma, upos='ADP')
		if tk:
			separateAdp(tokenlist=sent,lemma=lemma,display=display)
			edited.append(sent.metadata['sent_id'])
			i+=1
	print(f"Total edited sentences: {i}")

def separateAdp(data='',token=None,hostid=0,tokenlist=None,outfile='',lemma='pitérupi',display=False):
    '''Separate the clitic alomorph of the postposition "upé" attached to a noun such as "pitera" in "pitérupi" with hostid id. See issue #365.
    '''
    base=None
    if data:
        tokenlist=parse(data)[0]
    if not hostid:
        base=tokenlist.filter(lemma=lemma)[0]
        hostid=base['id']
    tokenid=hostid+1
    incrementSentId(tokenlist,tokenid)
    previous=tokenlist[hostid-2]
    if not base:
        base=tokenlist[hostid-1]
    tk=parseSentence(base['form'])
    mwt,head,token=tk
    token['head']=base['id']
    base['misc'].pop('TokenRange')
    sp=base['misc'].get('SpaceAfter')
    for att in ('form','lemma','upos','xpos','feats'):
        base[att]=head[att]
    for att in ('head','deprel'):
        base[att]=previous[att]
    token['id']=tokenid
    previous['head']=base['id']
    previous['deprel']='nmod:poss'
    dependents=tokenlist.filter(head=previous['id'])
    for dep in dependents:
        if dep['deprel'] in ('case','advmod'):
            dep['head']=hostid
    tokenlist.insert(hostid,token)
    mwt['id']=(base['id'],'-',token['id'])
    if sp:
        base['misc'].pop('SpaceAfter')
        misc=mwt.get('misc')
        if misc:
            mwt['misc'].update({'SpaceAfter' : sp})
        else:
            mwt['misc']=sp
    if not base.get('misc'):
        base['misc']=None
    tokenlist.insert(hostid-1,mwt)
    incrementTokenRange(tokenlist[tokenid+1:])
    sortTokens(tokenlist)
    if outfile:
        f=open(outfile,'w')
        print(tokenlist.serialize(),file=f)
        f.close()
    elif display:
        print(tokenlist.serialize())
    return tokenlist
    
def incrementSentId(tokenlist,startid):
	for token in tokenlist:
		tokenid=token['id']
		if isinstance(tokenid,int):
			if token['id'] >= startid:
				token['id']+=1
		elif isinstance(tokenid,tuple):
			token['id']=(tokenid[0]+1,'-',tokenid[2]+1)
		head=token['head']
		if head and head >= startid:
			token['head']+=1

def handleRel(token,tokenlist):
    token['deprel'] = 'nsubj'
    i=len(tokenlist)
    previous=getPreviousToken(token,tokenlist)
    if previous['id'] > 1 and previous['upos'] == 'PART':
        previous=getPreviousToken(previous,tokenlist)
    token['head'] = previous['id']
    nouns=TokensOfCatList(tokenlist,'NOUN')
    prons=TokensOfCatList(tokenlist,'PRON')
    for pron in prons:
        if pron['xpos'] == 'PRON2':
            prons.remove(pron)
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

def handleSconjList(tokenlist,verbs):
    for token in tokenlist:
        if token['upos'] == 'SCONJ':
            handleSconj(token,tokenlist,verbs)

def addFeatures(tokenlist):
    start=0
    i=0
    c=len(tokenlist) -1
    handleAux(tokenlist)
    verbid=FirstVerbId(tokenlist)
    verbs=VerbIdsList(tokenlist)
    if not verbs:
        start=handleNmodPoss(tokenlist)
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
        elif upos == 'PART':
            handlePart(token,tokenlist,verbs)
        elif upos == 'X':
            token['deprel']='goeswith'
            previous=tokenlist[i-1]
            token['head']=previous['id']
        elif upos == "INTJ":
            handleIntj(token,verbs)
        elif upos == "VERB":
            pass
            # TODO: handleVerb(token,nextToken,verbs)
        elif upos == "ADP":
            handleAdp(token,tokenlist,verbs)
        elif upos == "SCONJ": # TODO: iterate over tokenlist annotating all SCONJs
            handleSconj(token,tokenlist,verbs)
        elif upos == "CCONJ":
            handleCconj(token,verbs)
        elif upos == "ADV":
            handleAdv(token,nextToken,tokenlist,verbs)
        elif upos in DETERMINERS:
            handleDetNum(upos,token,nextToken,tokenlist,verbs)
        if nextToken and nextToken['upos'] == 'PUNCT': # TODO: sentences without final punctuation
            handlePunct(token,nextToken, tokenlist,verbs)
        i+=1
    handleVerbs(verbs)
    handleNmodPoss(tokenlist[start:])

def mkVocative(token,punct):
    if punct['lemma'] == COMMA:
        token['deprel'] = 'vocative'
        punct['head'] = token['id']

def handleVocative(tokenlist):
    for token in tokenlist:
        if token['deprel'] in ('nsubj','obj'):
            i=tokenlist.index(token)
            next=getNextToken(token,tokenlist[i+1:])
            previous=getPreviousToken(token,tokenlist)
            if next and next['upos'] == 'PUNCT':
                if previous:
                    if previous['upos'] == 'PUNCT':
                        mkVocative(token,previous)
                        break
                    elif previous['deprel'] == 'nmod:poss':
                        beforeprevious=getPreviousToken(previous,tokenlist)
                        if beforeprevious:
                            if beforeprevious['upos'] == 'PUNCT':
                                mkVocative(token,beforeprevious)
                                break
                        else:
                            mkVocative(token,next)
                            break
                else:
                    mkVocative(token,next)
                    break

def getXpos(parse):
	tags=parse[1]
	if tags:
		return tags.split('+')[0]
	return ''

def getTags(parse):
    tags=''
    m=None
    if parse[1]:
        m=TAGSEQ.search(parse[1])
    if m:
        x,y=m.groups()
        if x:
            tags=f"{x}{y}"
        else:
            tags=y
    return tags

def hasTag(tags1,tags2):
    if re.search(rf"\b{re.escape(tags2)}\b",tags1):
        return True
    return False

def filterparselist(tags,parselist):
    if tags:
        return list(filter(lambda x: hasTag(getTags(x),tags.upper()),parselist))
    else:
        return parselist

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

def getStartEnd(token,remove=True):
    dic={}
    misc=token.get('misc')
    if misc:
        tokenrange=''
        if misc.get('TokenRange'):
            if remove:
                tokenrange=misc.pop('TokenRange')
            else:
                tokenrange=misc.get('TokenRange')
        if not misc:
            token['misc']=None
        if tokenrange:
            start,end=tokenrange.split(':')
            dic['start']=start
            dic['end']=end
    return dic

def correctTokenRanges(tokenlist):
    start=0
    end=0
    i=0
    previous=Token()
    previd=0
    c=len(tokenlist)
    while(i<c):
        token=tokenlist[i]
        tokenid=token['id']
        misc=token.get('misc')
        if misc:
            tokenrange=misc.get('TokenRange')
            spaceafter=misc.get('SpaceAfter')
            if tokenrange:
                if i > 0:
                    previous=tokenlist[i-1]
                if previous:
                    previd=previous['id']
                if tokenid != previd:
                    end=start+len(token['form'])
                    startend=f"{start}:{end}"
                    token['misc']['TokenRange']=startend
                    increment=1
                    if spaceafter:
                        increment=0
                    start=end+increment
        i+=1

def getSpaceAfter(token):
    misc=token.get('misc')
    if misc:
        if misc.get('SpaceAfter'):
            return misc.pop('SpaceAfter')

def insertMultitokenWord(tokenlist):
    sep='-'
    compound=Token()
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
    if compound:
        correctTokenRanges(tokenlist) # TODO: verify whether this function suffices to correctly set TokenRange values

def insertMultitokenWord1(tokenlist):
    sep='-'
    compound=Token()
    for token in tokenlist:
        feats=token.get('feats')
        if feats:
            if feats.get('Compound') == 'Yes'or feats.get('Clitic') == 'Yes':
                index=tokenlist.index(token)
                previous=tokenlist[index-1]
                spaceafter=getSpaceAfter(token)
                alomorph=''
                misc=previous['misc']
                if misc:
                    alomorph=misc.get('Alomorph')
                first=previous['form']
                if alomorph:
                    first=alomorph
                mwt=MULTIWORDTOKENS.get(first)
                if mwt:
                    form=mwt
                else:
                    form=f"{first}{sep}{token['form']}"
                tokenid=token['id']
                ident=f'{tokenid-1}-{tokenid}'
                compound=mkMultiWordToken(ident,form,spaceafter=spaceafter)
                tokenlist.insert(index-1,compound)
    if compound:
        correctTokenRanges(tokenlist)

def extractCliticEntry(clitic):
    entries=list(filter(lambda dic: list(dic.keys())[0] ==clitic, CLITICENTRIES))
    if entries:
        return entries[0]

def handleHyphen(form):
    dic={}
    dic['form']=form
    dic['hyphen']=False
    if form.startswith(HYPHEN):
        dic['form']=form[1:]
        entry=CLITICENTRIES.get(form[1:])
        if entry:
            dic.update(entry)
            #dic['lemma']=CLITICENTRIES[form[1:]]['lemma']
            #dic['xpos']=CLITICENTRIES[form[1:]]['xpos']
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
	wara={'xpos':'ADP','lemma':'wara','clitic':WARA}
	wera={'xpos':'FREQ','lemma':'wera','clitic':WERA}
	pi={'xpos':'ADP','lemma':'upé','clitic':PI}
	ta={'xpos': 'CQ','lemma':'taá','clitic':TA}
	suffs=[ntu,me,pi,ta,wara,wera]
	for suff in suffs:
		clitic=suff.get('clitic')
		if clitic == form:
			dic['form']=form
			dic['upos']=getudtag(suff['xpos'])
			dic['xpos']=suff['xpos']
			dic['lemma']=suff['lemma']
			dic['underscore']=True
			break

def mkPropn(token,orig=None,orig_form=None):
    new={}
    feats=['PROPN']
    tags='+'.join(feats)
    lemma=token.lower()
    if orig:
        new['OrigLang']=orig
    if orig_form:
        new['Orig']=orig_form
    new['parselist']=[[lemma, tags]]
    return new

def mkAdv(form):
    return [[form.lower(), 'ADV']]

def mkX(form):
    return [[None, 'X']]

def isInLexicon(lemma,orig):
    # If orig is None, check if lemma is in the lexicon
    if orig is None:
        _isInLexicon(lemma)

def _isInLexicon(lemma='',parselist=[]):
	if lemma:
		parselist=getparselist(lemma)
	else:
		lemma=parselist[0][0]
	if len(parselist) == 1 and parselist[0][1] is None:
		raise Exception(f"Lemma '{lemma}' not found in the lexicon")

def handleOrig(new,lemma,orig, orig_form):
    if orig_form:
        new['Orig']=orig_form
        if not orig:
                raise Exception(f"Original form '{orig_form}' without original language")
    if orig:
        new['OrigLang']=orig
        if not orig_form:
            pass # TODO: apply Portuguese spell checker on the lemma 
    else:
        _isInLexicon(lemma)

def mkVerb(form,derivation='',orig=None, orig_form=None):
    new={}
    feats=['V']
    entry=guessVerb(form)
    lemma=entry['lemma']
    handleOrig(new,lemma,orig, orig_form)
    if derivation:
        feats.append(derivation)
    feats.append(entry['person'])
    number=entry.get('number')
    mood=entry.get('mood')
    if number:
        feats.append(number)
    if mood:
        feats.append(mood)
    tags='+'.join(feats)
    new['parselist']=[[lemma, tags]]
    return new

def handleMiddlePassive(form):
	new={}
	entry=guessVerb(form)
	if entry['lemma'].startswith(YU):
		entry['voice']=MEDPASS
		entry['lemma']=entry['lemma'][len(YU):]
	parselist=getparselist(f"{entry['pref']}{entry['lemma']}")
	tags=serializeEntry(entry)
	_isInLexicon(lemma='',parselist=parselist)
	new['parselist']=[[entry['lemma'],tags]]
	return new
	
def serializeEntry(entry):
	keys=['pos','derivation','voice','style','mood','person','number'] # TODO: create function to serialize dictionary entry 
	feats=[]
	for k in keys:
		value=entry.get(k)
		if value:
			feats.append(value)
	tags='+'.join(feats)
	return tags

def handlePartialRedup(form,length,xpos='V',orig=None, orig_form=''): # TODO: reduplication of adjectives
    new={}
    entry=guessVerb(form)
    lemma=entry['lemma'][length:] # TODO: check if lemma exists in the lexicon
    handleOrig(new,lemma,orig, orig_form)
    entry['derivation']=REDUP
    keys=['pos','derivation','style','mood','person','number'] # TODO: create function to serialize dictionary entry 
    feats=[]
    for k in keys:
        value=entry.get(k)
        if value:
            feats.append(value)
    tags='+'.join(feats)
    new['parselist']=[[lemma,tags]]
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

def mkHab(form): # TODO: this seems deprecated (see mkHabXpos)
    suff='tiwa'
    if form.endswith(suff):
        base=form[:-len(suff)]
        form=handleAccent(base)
        return mkVerb(form,derivation='HAB')

def mkHabSconj(form): # TODO: this seems deprecated (see mkHabXpos)
    suff='tiwa'
    new={}
    if form.endswith(suff):
        base=form[:-len(suff)]
        lemma=handleAccent(base)
        new['parselist']=[[lemma, 'SCONJ+HAB']]
        return new

def parseWord(form,length):
    base=form[:-length].lower()
    suff=form[-length:]
    return base,suff

def getval(key,dic):
    for k,v in dic.items():
        if k.startswith(key):
            return v
    return None

def mkHabXpos(form,xpos='', length=0, accent=False, guess=False, force=False):
    '''TODO: Possibly deprecated. Morphem "wera" is no longer analysed as a suffix, but as a particle, see issue #512.  
    '''
    if not length:
        length=4
    suffs={'wara':{'Aspect':'FREQ', 'Tense': 'PRES'},
    'tiwa': {'Aspect':'HAB'},
    'wera': {'Aspect':'FREQ', 'Tense': 'PAST'}}
    base, suff=parseWord(form,length)
    tag=suffs[suff]['Aspect']
    feats=[]
    feats.append(tag)
    tense=suffs[suff].get('Tense')
    if tense:
        feats.append(tense)
    new={}
    if accent:
        base=handleAccent(base,force=force) # TODO: accent handling based on the lexicon?
    if not xpos:
        xpos='V'
    if not guess:
        parselist=getparselist(base)
        parses=filterparselist(xpos,parselist)
        if parses:
            parse=parses[0]
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
    lemma=form.lower()
    handleOrig(new,lemma,orig, orig_form)
    number=dic.get('number')
    degree=dic.get('degree')
    derivation=dic.get('derivation')
    if degree:
        feats.append(degree)
    if derivation:
        feats.append(derivation)
    if not number:
        d=getNumber(lemma)
        number=d['number']
        lemma=d.get('lemma')
    feats.append(number)
    new['parselist']=[[lemma, f"N+{'+'.join(feats)}"]]
    return new

def mkAdj(form,orig='pt',dic={},orig_form='',xpos='a'): # TODO: use broader name
    form=form.lower()
    feats=[]
    new={}
    handleOrig(new,lemma,orig, orig_form)
    degree=dic.get('degree')
    derivation=dic.get('derivation')
    if degree:
        feats.append(degree)
    if derivation:
        feats.append(derivation)
    new['parselist']=[[form, f"{xpos.upper()}+{'+'.join(feats)}"]]
    return new

def getNumber(form):
    dic={}
    dic['number']='SG'
    if form.endswith('-itá') or form.endswith('-etá'):
        dic['number']='PL'
        dic['lemma']=form[:-4]
    else:
        dic['lemma']=form
    return dic

def mkAug(form,force=False): # TODO: superseded by mkEval
    form=form.lower()
    i=-4
    dic=getNumber(form)
    dic['degree']='AUG'
    number=dic.get('number')
    if number == 'PL':
        i=-8
    lemma=handleAccent(form[:i],force=force)
    return mkNoun(lemma,None,dic)

def mkEval(form,xpos='N',force=False,orig=None,orig_form='',accent=True):
    suffixes={'wasú': 'AUG', 'mirĩ': 'DIM', 'í': 'DIM','íra': 'DIM'}
    xpos=xpos
    dic={}
    dic['lemma']=form.lower()
    if xpos=='N':
        dic.update(getNumber(dic['lemma']))
    for suff,feat in suffixes.items():
         if dic['lemma'].endswith(suff):
             dic['degree']=feat
             dic['lemma']=dic['lemma'][:-len(suff)]
             break
    lemma=dic['lemma']
    if accent:
        lemma=handleAccent(lemma,force=force)
    if dic.get('number'):
        return mkNoun(lemma,dic=dic,orig=orig,orig_form=orig_form)
    return mkAdj(lemma,None,dic,xpos=xpos)

def mkCol(form):
    form=form.lower()
    suff='tiwa'
    i=-len(suff)
    dic=getNumber(form)
    dic['derivation']='COL'
    number=dic.get('number')
    if number == 'PL':
        i-=-4
    lemma=handleAccent(form[:i])
    return mkNoun(lemma,None,dic)

def mkPrv(form, xpos='A'):
    form=form.lower()
    i=-3
    dic={}
    tag='PRV'
    dic['derivation']=tag
    form=form[:i]
    if form.endswith('-'):
        form=form[:-1]
    lemma=handleAccent(form)
    new={}
    if xpos == 'A':
        new=mkAdj(lemma,None,dic)
    else:
        new['parselist']=[[lemma, f"{xpos}+{tag}"]]
    return new

def mkClitic(lemma,upos):
    return [[lemma, upos]]

def mkUpos(lemma,upos):
    return [[lemma.lower(), upos]]

def checkXposTag(pos_tag):
    """
    Process a part-of-speech tag from the XPOS set, raising an error if the tag is not in the valid tagset.

    Args:
        pos_tag (str): The part-of-speech tag to process.
    
    Returns:
        str: The uppercase version of the part-of-speech tag.

    Raises:
        ValueError: If the pos_tag is not in the predefined tagset.
    """
    pos_tag=pos_tag.upper()
    if pos_tag not in MAPPING.values():
        raise ValueError(f"Invalid part-of-speech tag: '{pos_tag}'. Expected one of the XPOS tagset.")
    
    return pos_tag

def get_iso_3_letter_code(language_code):
    from iso639 import languages
    """
    Converts a valid 2-letter or 3-letter ISO language code to a 3-letter ISO language code.

    Args:
        language_code (str): A valid 2-letter or 3-letter ISO language code.
    
    Returns:
        str: The corresponding 3-letter ISO language code.
    
    Raises:
        ValueError: If the input string does not represent a valid ISO language code.
    # Example usage
        print(get_iso_3_letter_code('pt'))  # Output: 'por'
        print(get_iso_3_letter_code('eng'))  # Output: 'eng'
        print(get_iso_3_letter_code('xyzw'))  # Raises ValueError
        print(get_iso_3_letter_code('xyz'))  # Raises ValueError
    """
    # Normalize to lowercase
    language_code = language_code.lower()
    language=languages.part1.get(language_code) or languages.part3.get(language_code)
    if language is None:
        raise ValueError(f"Invalid language code: {language_code}")
    
    return language.part3

def _mkUpos(form,xpos,orig=None,orig_form=''):
    new={}
    lemma=form.lower()
    if orig:
        new['OrigLang']=orig
    if orig_form:
        new['Orig']=orig_form
    new['parselist']=[[lemma, f"{xpos}"]]
    return new

def mkIntj(lemma):
    return mkUpos(lemma,'INTJ')

def _mkIntj(form,orig=None,orig_form=''):
    return _mkUpos(form,'INTJ',orig,orig_form)

def mkCard(lemma,orig=None,orig_form=''):
    return _mkUpos(lemma,'CARD',orig,orig_form)

def handleRedup(token):
    redup={}
    if HYPHEN in token and not token in LEXREDUP:
        parts=token.split('-')
        if len(parts) == 2 and parts[1]:
            if parts[0].endswith(parts[1]):
                redup['form'],redup['lemma']=parts[0],parts[1]
    return redup

def handleAlomorph(form):
    return form.replace('ií','iwa')

def mkRoot(index):
    ROOT.append(index)

def isMultitokenWord(tokenid):
	return (type(tokenid) is tuple and len(tokenid) == 3) or (type(tokenid) is str and len(tokenid.split('-')) == 2)

def setRoot(tokenlist):
    rootlist=tokenlist.filter(deprel='root')
    if rootlist:
        root=rootlist[0]
        rootid=root['id']
        for token in tokenlist:
            tokenid=token['id']
            if not isMultitokenWord(tokenid) and tokenid != rootid:
                if not token['head']:
                    token['head'] = rootid

def handleRoot(tokenlist):
    rootid=0
    if ROOT:
        rootlist=tokenlist.filter(deprel='root')
        rootid=ROOT.pop()+1
        token=tokenlist.filter(id=rootid)[0]
        token['deprel']='root'
        token['head']=0
        for t in rootlist:
            headid=t['id']
            deps=tokenlist.filter(head=headid)
            for dep in deps:
                depid=dep['id']
                punctid=previousPunct(dep,tokenlist)
                if punctid < headid < depid:
                    pass
                elif dep['lemma'] in DEPPUNCT:
                    pass
                else:
                    dep['head']=rootid
            t['deprel']='parataxis'
            t['head']=rootid
        feats=token.get('feats')
        isIntPron=False
        if feats:
            if feats.get('PronType') == 'Int':
                isIntPron=True
        for t in tokenlist:
            if t['id'] != rootid:
                if t['head'] == 0:
                    t['head']=rootid
                    if isCop(t):
                        mkCop(t)
                if not t['deprel']:
                    if isNominal(t['upos']):
                        if t['id'] < rootid or isIntPron:
                            setAttribute(t,'deprel','nsubj')
        last=tokenlist[-1]
        if last['deprel'] == 'punct' and last['head'] != rootid:
            last['head'] = rootid

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
    sep=':'
    dic={}
    if sep in tag:
        args=parseArgs(tag)
        for k,v in args.items():
            if k == 'a':
                if v == 'f':
                    args[k]=False
                elif v == 't':
                    args[k]=True
            elif k == 'l':
                args[k]=int(v)
        dic.update(args)
    else:
        dic['func']=tag
    return dic

def insertRedup(parselist):
    for parse in parselist:
        lemma,tags=parse[0],parse[1]
        if tags:
            taglist=tags.split('+')
            c=len(taglist)
            if c > 1:
                taglist.insert(1,REDUP)
            elif c == 1:
                taglist.append(REDUP)
            parse[1]="+".join(taglist)

def extractTag(token):
    if '/' in token:
        return token.split('/')

def mkTypo(correct,typo):
    dic={}
    dic['CorrectForm']=correct
    dic['Typo']=typo
    return dic

def mkModernForm(modern,attribute):
    dic={}
    dic[attribute]=modern
    return dic

def formatModernFeats(feats,register):
    new={}
    for k,v in feats.items():
        if k in ('lemma'):
            modern_value=v
        elif k == 'NCONT':
            modern_value='NCont'
        else:
            modern_value=v.title()
        new[f"{register}{k.title()}"]=modern_value
    return new

def diffFeats(modern_token,arch_token):
    '''Return lemma and features in modern_token that are not in arch_token.
    '''
    newdic={}
    arch_feats=arch_token.get('feats')
    if arch_feats:
        arch_lemma=arch_token['lemma']
        modern_feats=modern_token.get('feats')
        modern_lemma=modern_token['lemma']
        if arch_lemma != modern_lemma:
            newdic['lemma']=modern_lemma
        for k,v in modern_feats.items():
            m=arch_feats.get(k)
            if m != v:
                newdic.update({k : v})
    return newdic

def getStyle(attribute):
    mapping={'ModernForm' : 'Arch', 'StandardForm' : 'Rare'}
    return mapping.get(attribute)

def mkConlluSentence(tokens):
    register='Modern'
    field='Form'
    attribute=f"{register}{field}"
    ROOT.clear()
    tokenlist=TokenList()
    ident=1
    start=0
    for token in tokens:
        old=token
        tag=MULTIWORDTOKENS.get('xpos')
        root=False
        parts=extractTag(token)
        if parts:
            token,tag=parts
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
            insertRedup(parselist)
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
            if orig:
                orig=get_iso_3_letter_code(orig)
            accent=tagparse.get('a')
            length=tagparse.get('l')
            typo=tagparse.get('t')
            correct=tagparse.get('c')
            modern=tagparse.get('m')
            newregister=tagparse.get('r')
            if newregister:
                register=newregister
                attribute=f"{newregister.title()}{field}"
            archpos=tagparse.get('h')
            orig_form=tagparse.get('s')
            force=tagparse.get('f')
            xpos=tagparse.get('x')
            if xpos:
                xpos=checkXposTag(xpos)
            newparselist=[]
            if tag == '=p':
                new=mkPropn(token,orig=orig,orig_form=orig_form)
                newparselist=new['parselist']
            elif tag == '=typo':
                dic.update(mkTypo(correct,form))
                if xpos == 'X':
                    newparselist=mkX(correct)
                else:
                    newparselist=getparselist(correct.lower())
            elif tag == '=mf':
                dic.update(mkModernForm(modern,attribute))
                newparselist=getparselist(form.lower())
                modernparselist=getparselist(modern.lower())
                if xpos:
                    modernparselist=filterparselist(xpos,modernparselist)
                if archpos:
                    newparselist=filterparselist(archpos,newparselist)
            elif tag == '=adv': # TODO: possibly deprecated (see mkUpos)
                newparselist=mkAdv(token)
            elif tag == '=x':
                newparselist=mkX(token)
            elif tag == '=n':
                new=mkNoun(form,orig=orig,orig_form=orig_form)
                newparselist=new['parselist']
            elif tag == '=a':
                new=mkAdj(form,orig=orig,orig_form=orig_form)
                newparselist=new['parselist']
            elif tag == '=v':
                new=mkVerb(form,orig=orig,orig_form=orig_form)
                newparselist=new['parselist']
            elif tag == '=hab': # TODO deprecated
                new=mkHab(form)
                newparselist=new['parselist']
            elif tag == '=col':
                new=mkCol(form)
                newparselist=new['parselist']
            elif tag == '=hab=sconj': # TODO deprecated
                new=mkHabSconj(form)
                newparselist=new['parselist']
            elif tag == '=mkhab': # TODO change "mkhab" to "hab" (possibly deprecated, see issue #516
                new=mkHabXpos(  form,
                                xpos,
                                length=length,
                                accent=accent,
                                guess=tagparse.get('g'),
                                force=force
                                )
                newparselist=new['parselist']
            elif tag == '=aug': # TODO possibly deprecated (see =ev)
                new=mkAug(form,force)
                newparselist=new['parselist']
            elif tag == '=ev': # TODO: handle accent argument
                new=mkEval(form,xpos,force,orig,orig_form,accent)
                newparselist=new['parselist']
            elif tag == '=prv':
                new=mkPrv(form,xpos)
                newparselist=new['parselist']
            elif tag == '=intj':
                new=_mkIntj(form,orig,orig_form)
                newparselist=new['parselist']
            elif tag == '=card':
                new=mkCard(form, orig,orig_form) # TODO see mkIntj
                newparselist=new['parselist']
            elif tag == '=upos':
                new=_mkUpos(form,xpos, orig,orig_form)
                newparselist=new['parselist']
            elif tag == '=red':
                new=handlePartialRedup(form,length)
                newparselist=new['parselist']
            elif tag == '=mid':
                new=handleMiddlePassive(form)
                newparselist=new['parselist']
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
            if dic.get('underscore'):
                start=start-1
            t=mkConlluToken(form,entry,start=start, ident=ident)
            if dic.get('hyphen') or dic.get('underscore'):
                handleHyphenSepToken(t)
            correct_form=dic.get('CorrectForm')
            typo=dic.get('Typo')
            if correct_form and typo:
                t['misc'].update({'CorrectForm': correct_form})
                if xpos != 'X':
                    t['feats'].update({'Typo': 'Yes'})
                t['form']=typo
            modern_form=dic.get(attribute)
            if modern_form:
                t['misc'].update({attribute: modern_form})
                modern_entries=extract_feats(modernparselist)
                modern_token=mkConlluToken(modern_form,modern_entries[0])
                diff=formatModernFeats(diffFeats(modern_token,t),register)
                t['misc'].update(diff)
                updateFeats(t,'Style',getStyle(attribute))
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
    handleOblRoot(tokenlist)
    handleRoot(tokenlist)
    handleExpletive(tokenlist)
    handleVocative(tokenlist)
    handleStartPunct(tokenlist)
    setRoot(tokenlist)
    handlePronSeq(tokenlist)
    handleV2(tokenlist)
    sortTokens(tokenlist)
    return tokenlist

def handleV2(tokenlist):
	HandleMoodPerson(tokenlist)

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
        for sent in SqueezeWhiteSpace(lines).split("\n"):
            sents.append(sent.strip())
    else:
        parts1=[part.strip() for part in PARTS1.split(SqueezeWhiteSpace(line),2)]
        parts2=[sent.strip() for sent in PARTS2.split(parts1[-1]) if sent]
        sents.extend(parts1[:2])
        sents.extend(parts2)
    return sents

def SqueezeWhiteSpace(s):
    return SQUEEZE.sub(" ",s)

def mkSentId(pref='',textid=0,index=0,sentid=0):
	return f"{pref}:{textid}:{index}:{sentid}"

def _ppText(sents,pref='',textid=0,index=0,sentid=0):
	sentid=mkSentId(pref,textid,index,sentid)
	metadata={}
	if pref:
		metadata['sent_id'] = sentid
	yrl,eng,por=[sent.strip() for sent in sents[:3]]
	template=f"# text = {yrl}\n# text_eng = {eng}\n# text_por = {por}"
	metadata.update(dict(zip(["text", "text_eng", "text_por"], [yrl,eng,por])))
	if len(sents) > 3:
		for sent in sents[3:]:
			if sent.startswith('(') and sent.endswith(')'):
				metadata['source']=sent[1:-1]
			else:
				metadata['orig']=sent
	return metadata

def ppText(sents,pref='',textid=0,index=0,sentid=0):
    output=[]
    if pref:
        output.append(f"# sent_id = {pref}:{textid}:{index}:{sentid}")
    yrl,eng,por=[sent.strip() for sent in sents[:3]]
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
    return REMOVE.sub('',sent)

def handleSents(sents,pref,textid,index,sentid,annotator,metadata):
    yrl=extractYrl(sents[0])
    sents[1]=f"({sents[1]})"
    output=[] # TODO: update TokenList's  metadata instead
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
    if metadata:
        tk.metadata.update(metadata)
    includeAnnotator(output,annotator) # TODO: update the TokenList's metadata
    output.append(tk.serialize())
    return output

def _handleSents(sents,annotator,metadata):
	text=sents['text']
	sents['text']=extractYrl(text)
	tokenlist=parseSentence(text)
	tokenlist.metadata.update(sents)
	if metadata:
		tokenlist.metadata.update(metadata)
	_includeAnnotator(tokenlist,annotator)
	return tokenlist

def includeAnnotator(output,annotator):
    output.append(f"# {ANNOTATOR_ATT} = {annotator}")

def _includeAnnotator(tokenlist,annotator):
    if annotator:
        tokenlist.metadata[ANNOTATOR_ATT]=annotator

def formatList(output):
    return '\n'.join(output)

def handleParse(outstring,copyboard=True):
    if copyboard:
        import pyperclip
        pyperclip.copy(outstring)
    print(outstring)

def getFileNameParts(pref,textid,index,sentid):
    return {'pref':pref, 'textid':str(textid),
    'index':str(index),'sentid':str(sentid)}

def TreebankSentence(text='',pref='',textid=0,index=0,sentid=0,copyboard=True,annotator='LFdeA',outfile=False,overwrite=False):
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
    output=handleSents(sents, pref,textid,index,sentid,annotator)
    outstring=formatList(output)
    if outfile:
        metadata=getFileNameParts(pref,textid,index,sentid)
        saveParseToFile(includeText(text,outstring),metadata,overwrite)
    handleParse(outstring,copyboard=copyboard)

def saveParseToFile(outstring,metadata,overwrite):
    values=list(metadata.values())
    filename=f"{'-'.join(values)}.conllu"
    if os.path.exists(filename) and not overwrite:
        print(f"{filename} already exists.")
    else:
        outfile=open(filename,'w', encoding="utf-8")
        print(outstring,file=outfile)
        outfile.close()

def formatTextEng(s):
    s=s.strip()
    c=s[0]
    chars='-—'
    if c in chars:
        s=s.replace(c,'').strip()
        return f'"{s.strip(chars).strip()}"'
    return s

def mkTranslation(text_por):
    from deep_translator import GoogleTranslator
    text_eng=GoogleTranslator(source='pt', target='en').translate(text_por)
    return formatTextEng(text_eng)

def includeTranslation(parts,translate=True):
    i=-1
    if len(parts) == 4:
        i=-2
    text_por=parts[i]
    text_eng= 'TODO'
    if translate:
        text_eng=mkTranslation(text_por)
    if len(parts) == 4:
        parts.insert(-1,text_eng)
    else:
        parts.append(text_eng)

def _includeTranslation(text_por,translate=True):
	text_eng= 'TODO'
	if translate:
		from deep_translator import GoogleTranslator
		text_eng=GoogleTranslator(source='pt', target='en').translate(text_por)
		text_eng=formatTextEng(text_eng)
	return text_eng

def _parseExample(sents,copyboard=True,annotator=ANNOTATOR,check=True, outfile=False, overwrite=False,metadata={}, translate=True,inputline=True):
	yrl=sents['text']
	por=sents['text_por']
	if check:
		if checkSentence(yrl): # TODO: extractYrl before checking sentence!
			print(f"Sentence '{yrl}' already is in the treebank.")
			return
	sents['text_eng'] = _includeTranslation(por,translate)
	metadata=metadata
	if inputline:
		metadata.update({'inputline': yrl})
	tokenlist=_handleSents(sents,annotator,metadata)
	outstring=tokenlist.serialize()
	#if outfile: TODO
	#    metadata=getFileNameParts(pref,textid,index,sentid)
	#    saveParseToFile(includeText(example,outstring),metadata, overwrite)
	handleParse(outstring,copyboard=copyboard)

def parseExample(example,pref,textid,index,sentid,copyboard=True,annotator=ANNOTATOR,check=True, outfile=False, overwrite=False,metadata={},translate=True, inputline=True):
    sents=extract_sents(example)
    yrl=sents[0]
    metadata=metadata
    if inputline:
        metadata.update({'inputline': yrl})
    if check:
        if checkSentence(yrl):
            print(f"Sentence '{yrl}' already is in the treebank.")
            return
    includeTranslation(sents,translate)
    output=handleSents(sents,pref,textid,index,sentid,annotator,metadata)
    outstring=formatList(output)
    if outfile:
        metadata=getFileNameParts(pref,textid,index,sentid)
        saveParseToFile(includeText(example,outstring),metadata, overwrite)
    handleParse(outstring,copyboard=copyboard)

def includeText(text,outstring):
    return f"# textinput = {text}\n{outstring}"

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
    form=token.lower()
    pair=extractTag(token)
    tag=''
    if pair:
        token,tag=pair
    if form == 'maita':
        return mkHost('mayé',TA,token,'ADVRA')
    else:
        entry=getLocEntry(form)
        if entry:
            base_pref=entry['prefix']
            form_prefix=getRelPrefix(form)
            base=entry['base']
            if form_prefix and base_pref:
                base=f"{form_prefix.lower()}{base[1:]}"
            elif form_prefix:
                base=f"{form_prefix.lower()}{base}"
            return mkHost(base,PI,token,'N')
    for clitic in NONHYPHEN:
        host=hasClitic(clitic,token)
        if host:
            return mkHost(host,clitic,token,tag)
    return dic

def hasLinkingHyphen(token):
    parts=token.split("|")
    c=len(parts)
    if c == 1:
        return HYPHEN in token
    else:
        return HYPHEN in parts[0]
    return False

def splitMultiWordTokens(tokens):
    MULTIWORDTOKENS.clear()
    sep=[d['lemma'] for d in AUX]
    sep.extend(CLITICS)
    newlist=[]
    for t in tokens:
        dic=extractHost(t)
        if hasLinkingHyphen(t):
            tag=''
            parts=extractTag(t)
            if parts:
                t,tag=parts
            index=t.index(HYPHEN)
            first=t[:index]
            second=t[index:]
            if second[1:] in sep:
                if second[1:] in CLITICS:
                    first=f"{first}-"
                if tag:
                    first=f"{first}/{tag}"
                newlist.extend([first,second])
            else: #TODO: has hyphen and clitic "-ntu"
                newlist.append(f"{t}/{tag}")
        elif dic: # TODO: if dic ...?
            host=dic['host']
            suff=dic['suff']
            mwt=dic['multiwordtoken']
            xpos=dic.get('xpos')
            if xpos:
                MULTIWORDTOKENS['xpos']=xpos # TODO 23/08/2024: MULTIWORDTOKENS as list of dictionaries (a sentence can have more than one MWT)
            MULTIWORDTOKENS[host]=mwt
            newlist.extend([host,f"{UNDERSCORE}{suff}"])
        else:
            newlist.append(t)
    return newlist

def handleRightQuotationMark(tokens):
	indexes=[]
	j=0
	quote=DOUBQUOMARK # TODO: handling of other quote types
	while(j < len(tokens)):
		if "/" in tokens[j]:
			word,tags=tokens[j].split("/")
			if word.endswith(quote):
				tokens[j]=f"{word[:-1]}/{tags}"
				indexes.append(j)
		j+=1
	for i in indexes:
		if i == (len(tokens) -1):
			tokens.append(quote)
		else:
			tokens.insert(i+1,quote)

def parseSentence(sent):
    tokens=splitMultiWordTokens(tokenize(sent))
    handleRightQuotationMark(tokens)
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
    outstring=formatList(output)
    handleParse(outstring,copyboard=copyboard)

def writeConlluUD(sentences,outfile,pref='MooreFP1994',textid=0,sentid=1):
    i=0
    textid=textid
    sentid=sentid
    with open(outfile, 'w', encoding="utf-8") as f:
        while(i < len(sentences)):
            sent=sentences[i]
            insertSentId(sent,pref,textid,sentid)
            i+=1
            sentid+=1
            print(sent.serialize(),end='',file=f)

def writeSentsConllu(sentences,outfile):
    with open(outfile, 'w', encoding="utf-8") as f:
        for sent in sentences:
            print(sent.serialize(),end='',file=f)

def insertAnnotatorInSents(infile,outfile,annotator):
    sents=extractConlluSents(infile)
    insertAnnotator(sents,annotator)
    writeSentsConllu(sents,outfile)

def extractWordTagPairs(tokenlist):
	i=0
	triples=[]
	mapping={'ADV': '=adv', 'NOUN': '=n', 'ADJ': '=a',
		 'PROPN': '=p', 'VERB': '=v', 'INTJ': '=intj'}
	while(i<len(tokenlist)):
		func=''
		token=tokenlist[i]
		tokenid=token['id']
		form=token['form']
		xpos=token['xpos']
		tag=None
		if xpos:
			xpos=xpos.lower()
			tag=xpos
		upos=token['upos']
		if upos in ('INTJ','PROPN'):
			func=mapping[upos]
		feats=token['feats']
		if feats:
			rel=feats.get('Rel')
			if rel:
				tag=f"{xpos}+{rel.lower()}"
			aug=feats.get('Degree')
			if aug == 'Aug':
				func='=aug'
			aspect=feats.get('Aspect')
			if aspect in ('Freq','Hab'):
				func=f"=mkhab:x|{tag}:a|t"
			derivation=feats.get('Derivation')
			if derivation:
				if derivation == 'Priv':
					func=f"=prv:x|{xpos}"
				elif derivation == 'Coll':
					func='=col'
		misc=token['misc']
		if misc:
			spaceafter=misc.get('SpaceAfter')
			origlang=misc.get('OrigLang')
			if not func:
				if origlang:
					func=mapping.get(upos)
		if isMultitokenWord(tokenid):
			if HYPHEN in form:
				tag=tokenlist[i+1]['xpos'].lower()
			i+=2
		if func:
			tag=func
		triples.append((form,tag,spaceafter))
		i+=1
	return triples

def mkSent(triples):
	sent=""
	for form,tag,spaceafter in triples:
		sep=' '
		if spaceafter:
			sep=''
		word=f"{form}"
		if tag and tag not in ('punct','elip'):
			word=f"{form}/{tag}"
		sent=f"{sent}{word}{sep}"
	return sent

def removeLemmaAmbiguity(tk):
	i=0
	while(i<len(tk)):
		doubles=tk.filter(id=i)
		if len(doubles) == 2:
			t1=doubles[0]
			t2=doubles[1]
			form1=t1['form']
			form2=t2['form']
			if form1 == form2:
				feats1=t1.get('feats')
				feats2=t2.get('feats')
				if feats1 and feats2:
					rel1=feats1.get('Rel')
					rel2=feats2.get('Rel')
					vform1=feats1.get('VerbForm')
					vform2=feats2.get('VerbForm')
					if rel1 and rel2:
						if rel1=='Abs':
							index=tk.index(t1)
							tk.pop(index)
						elif rel2=='Abs':
							index=tk.index(t2)
							tk.pop(index)
					if vform1 and vform2:
						if vform1=='Inf':
							index=tk.index(t1)
							tk.pop(index)
						elif vform2=='Inf':
							index=tk.index(t2)
							tk.pop(index)
		i+=1

def mkTestSet(sents):
    test_sents=[]
    i=0
    while(i<len(sents)):
        tk=sents[i]
        triples=extractWordTagPairs(tk)
        sent=mkSent(triples)
        newtk=parseSentence(sent)
        removeLemmaAmbiguity(newtk)
        text=extractYrl(sent)
        newtk.metadata['sent_id']=f"{i}"
        newtk.metadata['text']=text
        newtk.metadata['sent']=sent
        test_sents.append(newtk)
        i+=1
    return test_sents

def mkSecText(yrl=None,yrl_source=None,por=None, por_sec=False,por_source=None):
    sep=''
    if por_sec:
        por_sec='sec'
        sep='_'
    else:
        por_sec=''
    dic={}
    if yrl:
        dic['text_sec']=yrl
    if por:
        text_por=f"{sep.join(['text_por',por_sec])}"
        dic[text_por]=por
    if yrl_source:
        dic[f'text_sec_source']=yrl_source
        if por_source:
            dic[f'{text_por}_source']=por_source
        else:
            dic[f'{text_por}_source']=yrl_source
    return dic

def mkSecTextAvila(example,por_sec=True):
    sents=extract_sents(example)
    return mkSecText(yrl=sents[0],yrl_source='Avila (2021)',por_sec=por_sec,por=sents[2])

def ppMetadata(metadata):
	for k,v in metadata.items():
		print(f"# {k} = {v}")

def ModernForm(form='remunhã',feats='Number=Sing|Person=2|VerbForm=Fin',register='Modern'):
    featlist=[feat.split('=') for feat in feats.split('|')]
    field='Form'
    misc=[f"{register}{field}={form}"]
    for feat in featlist:
        misc.append(f"{register}{feat[0]}={feat[1]}")
    return "|".join(misc)

def ExtractSentsMaslova(text):
    pat=re.compile(r"\s+[—–]\s+-\s+")
    lines=text.split("\n")
    parsedLines=[pat.split(line) for line in lines]
    dic={}
    languages=('yrl','por','rus')
    dic['number']=parsedLines[0][0]
    dic.update(zip(languages,[line[1] for line in parsedLines]))
    return dic

def formatExampleMaslova(dic,orig_page,sec_page):
    outdic={}
    outdic['inputline']=f"{dic['yrl']} (p. {orig_page}, No. {dic['number']}) {dic['por']} - {dic['yrl']}"
    outdic['text_transcriber'] = 'Maslova (2018:{sec_page})'
    return outdic

def setSentReviewers(sent,namelist):
	i=0
	dic={}
	while(i < len(namelist)):
		dic[f"reviewer{i+1}"]=namelist[i]
		i+=1
	sent.metadata.update(dic)

def includeReviewers(sents,sentids,namelist=['JLG','DMA']):
    for sent in sents:
        for sentid in sentids:
            if sent.metadata['sent_id'] == sentid:
                includeReviewers(sent,['JLG','DMA'])
                sentids.remove(sentid)

def pp(s):
    print(parseSentence(s).serialize())

def getSentsWithSentId(sentid,sents):
	return list(filter(lambda sent: sentid in sent.metadata['sent_id'],sents))

def getLastSentWithSentId(sentid,sents):
	r=list(filter(lambda sent: sentid in sent.metadata['sent_id'],sents))
	if r:
		return r[-1].metadata['sent_id']

def mkNextSentWithSentId(sentid,sents):
    parts=[]
    def incr_number(numbers):
        i=0
        while(i<len(numbers)):
            if numbers[i] > 0:
                numbers[i]= numbers[i]+1
            i+=1
    elements = getLastSentWithSentId(sentid,sents).split(":")
    parts.append(elements[0])
    numbers=[int(nr) for nr in elements[1:]]
    incr_number(numbers)
    parts.extend(numbers)
    return parts

def extractSourcesAvila(sents):
	sources=[]
	avila_sents=getSentsWithSentId("Avila2021",sents)
	return [sent.metadata['text_source'].split(",")[0].strip("(2021)").strip() for sent in avila_sents]

def capitalizeFirstLetter(sentence):
    return f"{sentence[0].upper()}{sentence[1:]}"

def handleSentsHartt(example):
    """
    Parse a string containing an example from Hartt (1938) into a dictionary.

    The input string should be in a format where each line contains a different version of a Nheengatu sentence and/or its translation into Portuguese. The first line contains the number and, if available, the letter of the example followed by the original text. The following lines contain different versions and translations thereof.

    Parameters:
    example (str): A string with multiple lines, each containing a version of a Nheengatu sentence and/or its translation into Portuguese, formatted as follows:
                   53 - omú oeín okaú resé yapenúna suí.
                   53 - Amú uweena ukaú resé igapenú suí.
                   53 - Amú-itá uweena ukaú resé gapenú suí. (Hartt, 387, adap.) Alguns vomitaram porque ficaram enjoados devido ao banzeiro.
                   53 - alguns lançaram (vomitaram) estando enjoados pelo movimento das maresias.


     Returns:
    dict: A dictionary with the parsed key-value pairs:
          - 'index': a tuple where the first element is an integer representing the sentence number, and the second element is a string representing the letter if available, or an empty string if not (tuple (int, str))
          - 'text_orig': Hartt's (1938) original Nheengatu sentence (str)
          - 'text': the first variant of the Nheengatu sentence, with the spelling adapted to the one proposed by Avila (2021) (str)
          - 'avila': Avila's (2021) example with citation or NA if non-available (str)
          - 'text_por': Hartt's (1938) Portuguese translation in modernide orthography (str)

    Examples:
    >>> input_string = '''
    53 - omú oeín okaú resé yapenúna suí.
    53 - Amú uweena ukaú resé igapenú suí.
    53 - Amú-itá uweena ukaú resé gapenú suí. (Hartt, 387, adap.) Alguns vomitaram porque ficaram enjoados devido ao banzeiro.
    53 - alguns lançaram (vomitaram) estando enjoados pelo movimento das maresias.
    '''
>>> handleSentsHartt(input_string)
    {'index': (53, ''),
    'text_orig': 'omú oeín okaú resé yapenúna suí.',
    'text': 'Amú uweena ukaú resé igapenú suí.',
    'avila': 'Amú-itá uweena ukaú resé gapenú suí. (Hartt, 387, adap.) Alguns vomitaram porque ficaram enjoados devido ao banzeiro.',
    'text_por': 'Alguns lançaram (vomitaram) estando enjoados pelo movimento das maresias.'}

    Raises:
    ValueError: If the input string does not contain the expected number of lines.
    """
    lines=[line.strip().split(' - ',1) for line in example.split('\n') if line.strip() != '']

    if len(lines) != 4:
        raise ValueError("Input string must contain exactly four non-empty lines.")

    result = {}
    # Extract the number and optionally the letter from the first line
    number_letter = lines[0][0].split(" ")
    if len(number_letter) == 2:
        number, letter = number_letter
        number = int(number)
    else:
        number = int(number_letter[0])
        letter = ''
    result['index']=(number,letter)
    keys=('text_orig','text','avila','text_por')
    i=0
    while(i < len(lines)):
       result[keys[i]]=lines[i][1]
       i+=1
    # Capitalize the first letter of the Portuguese translation
    result['text_por']=capitalizeFirstLetter(result['text_por'])
    return result

AVILA_SENTS=[]
def parseSingleLineExample(example,text_nr=2, prefix="Amorim1928", translate=True, transcriber=Mindlin, person='gab'):
	"""
	Parse a Nheengatu sentence example from Amorim (1928) or an analogous publication and print the respective analysis in the CoNNL-U format, copying it to the clipboard.

	Parameters:
	example (str): A string with a Nheengatu sentence in modernized orthography, page
		and example number, its translation into Portuguese, and the text in the original orthography,
		possibly followed by Avila's (2021) corresponding example, formatted as in the examples below.
	text_nr (int, optional): Text number or identifier. Default is 2.
	prefix (str, optional): Prefix for the output format. Default is "Amorim1928".
	translate (bool, optional): Whether to translate the sentence. Default is True.
	transcriber (function, optional): A function that creates a dictionary with information about the transcribers of the sentence. Default is Mindlin.

	Examples:
	>>> example = '''Musapiri yasí riré/adp, paá, nhaã intí waá upitá i/pron2 puruã aé/pron uyupúi muxiwa umukirá arama/sconj aintá/pron. (p. 312, No. 76) Três luas depois, contam, àquelas que não tinham ficado cheias ele começou dando muxiba para engordar. - Musapyre iasy riré, paa, nhaa nty uaá opytá ipuruan aé oiupe muxiua omukyrá arama aetá.'''

	>>> example='''Buopé paá intí usuaxara, umundú yeperesé uyapí kaziwera/=typo:c|kaxiwera pupé nhaã kunhã-etá pirá rimbiú arama/sconj. (p. 24, No. 15) Buopé, contam, não respondeu, mandou imediatamente jogar essas mulheres na cachoeira para comida de peixe. - Buopé paa nti osuaixara, omundu iepéresé oiapi kaziuera pýpé nhaa kunhãetá pirá rembiú arama. § Buopé paá ti usuaxara, umundú yeperesé uyapí kaxiwera pupé nhaã kunhã-itá pirá rimbiú arama. (Amorim, 26, adap.) Buopé, contam, não respondeu, mandou imediatamente jogar essas mulheres na cachoeira para serem comida de peixe.'''

	"""
	global AVILA_SENTS
	pat=re.compile(r"No. (\d+)(\-(\d+))?")
	section="§"
	sep=re.compile(rf"\s*{section}\s*")
	sent_nr=0
	match=pat.search(example)
	if match:
		groups=match.groups()
		sent_nr=int(groups[0])
	amorim,avila = '',''
	metadata={}
	if section in example:
		amorim,avila=sep.split(example)
		metadata=mkSecTextAvila(avila)
		if not AVILA_SENTS:
			sents=extractConlluSents(TREEBANK_PATH)
			AVILA_SENTS=getSentsWithSentId('Avila2021',sents)
		result=list(filter(lambda sent: sent.metadata['text'] == metadata['text_sec'],AVILA_SENTS))
		if result:
			metadata['cross_reference']=result[0].metadata['sent_id']
	else:
		amorim=example
	metadata.update(transcriber(person))
	parseExample(amorim,prefix,text_nr,sent_nr,sent_nr,metadata=metadata,translate=translate)

def getPortugueseTextProducer(sent):
    source=sent.metadata.get('text_por_source')
    if source:
        return source
    translator=sent.metadata.get('text_por_translator')
    if translator:
        return translator
    orig=sent.metadata.get('text_por_orig')
    if orig:
        return sent.metadata.get('text_annotator')
    return sent.metadata['sent_id'].split(':')[0]

def formatPages(start_page,end_page):
	if start_page and end_page:
		if start_page == end_page:
			pages=start_page
		else:
			pages=f"{start_page}-{end_page}"
	else:
		if start_page:
			pages=start_page
		else:
			pages=''
	if pages:
		pages=f"p. {pages}, "
	return pages

def parseExampleAmorim(example,text_nr=0,start_page=0,end_page=0, copyboard=True,annotator=ANNOTATOR,check=True, outfile=False, overwrite=False,metadata={}, translate=False,inputline=True):
	"""
	>>> example='''18: (Nheengatú) Aru (S. Gabriel) 297-299.
29-30\tAé/pron unheẽ: — Remaã ne tuwí/=mf:m|ruwí kwera/n mayawé/advra uyumuaíwa, kuíri aé/=mf:m|i:x|pron2:h|pron irumu/adp tenhẽ/foc kurí xasú xapusanú indé, puranga/adva ne mira, umaã indé arama/sconj.
29-30\tEla disse: — Vê teu sangue cuera como se estragou, agora com ele mesmo eu te curarei para tua gente olhar bonito para ti.
29-30\tAé onheen: — Remaan ne tuuy kuera maaiaué oiumuayua, kuyre aé irumo tenhé kuri xasu xapusanu ndé, puranga ne mira, omaan ndé arama.'''
	>>> AnnotateConllu.parseExampleAmorim(example)
	"""
	metadata.update(Mindlin())
	sents={}
	title=''
	lines=[line.strip() for line in example.split("\n") if line.strip() != '']
	if len(lines) == 4:
		i=1
		pat=r"(\d+):(\D+)(\d+-\d+)"
		regex=re.compile(pat)
		m=regex.search(lines[0])
		if m:
			groups=m.groups()
			if groups:
				number,lang_title_place,start_end=[part.strip() for part in groups]
				start_page,end_page=start_end.split('-')
				text_nr=int(number)
				parts=[part.strip() for part in re.split(r"[\)\(]",lang_title_place) if part.strip() !='']
				if parts:
					if len(parts) == 2:
						lang=parts[0]
						title=parts[1]
						if lang == "Nheengatú":
							title=title.upper()
					elif len(parts) == 3:
						place=parts[2]
						metadata.update({'place' : place})
	elif len(lines) == 3:
		i=0
	sent_num,text=lines[i].split("\t")
	#sent_num=int(sent_num)
	text,por,orig=[line.split("\t")[1] for line in lines[i:]]
	prefix="Amorim1928"
	sents['sent_id']=mkSentId(prefix,text_nr,sent_num,sent_num)
	sents['text']=text
	sents['text_por']=por
	sents['text_source']=f"{formatPages(start_page,end_page)}No. {sent_num}"
	sents['text_orig']=orig
	if title:
		sents['title_orig']=title
	return _parseExample(sents,copyboard=copyboard,annotator=annotator,check=check, outfile=outfile, overwrite=overwrite,metadata=metadata, translate=translate,inputline=inputline)

def eliminateDependentToken(tokenlist,tokenid):
	tokenlist.pop(tokenid-1)
	for token in tokenlist:
		if isinstance(token['id'],int):
			if token['id'] > tokenid:
				token['id'] = token['id'] -1
			if token['head'] > tokenid:
				token['head'] = token['head'] -1
		elif isinstance(token['id'],tuple):
				start,hyphen,end = token['id']
				if int(start) > tokenid:
					token['id'] = (f"{int(start)-1}",hyphen,f"{int(end)-1}")

def mergePronoun3PP(tokenlist,tokenid,form):
	updateFeats(tokenlist[tokenid],'Number','Plur')
	tokenlist[tokenid]['form'] = form
	eliminateDependentToken(tokenlist,tokenid)
	sortTokens(tokenlist)

def mkVariants(form):
	variants=set()
	variants.add(form.replace('é','ẽ'))
	variants.add(form.replace('ẽ','é'))
	return variants
	
def _mergePronoun3PP(tokenlist):
	edited=False
	text_orig=tokenlist.metadata.get('text_orig')
	if not text_orig:
		return edited
	pron3PP=tokenlist.filter(lemma='ta',xpos='PRON',feats__Number="Plur", feats__Person="3", feats__PronType="Prs")
	print('pron3PP', pron3PP)
	for token in pron3PP:
		tokenid=token['id']
		headid=token['head']
		print('tokenid,token,headid: ',tokenid,token,headid)
		if headid - tokenid != 1:
			return edited
		headlist=tokenlist.filter(upos='VERB',id=headid)
		head=None
		if headlist:
			head=headlist[0]
		else:
			return edited
		pronform=token['form']
		headform=head['form']
		headlemma=head['lemma']
		variants=mkVariants(headlemma)
		print(f"head: {head},pronform: {pronform},headform: {headform}, headlemma: {headlemma}")
		text=tokenlist.metadata['text']
		regex=rf"({pronform})(u?)({'|'.join(variants)})"
		print(regex)
		match=re.search(regex,text_orig)
		if not match:
			text_orig=text_orig.replace('bwé','bué')
			match=re.search(regex,text_orig)
		print('match',match)
		if match:
			u=match.groups()[1]
			form=f"{pronform}{u}{headlemma}"
			newtext=text.replace(f"{pronform} {headform}",form,1)
			print(f"form, newtext {form, newtext}")
			tokenlist.metadata['text']=text.replace(f"{pronform} {headform}",form)
			print(f"replaced text: {tokenlist.metadata['text']}")
			mergePronoun3PP(tokenlist,tokenid,form)
			edited=True
			break
	return edited

def testFunction(sentid):
	sents=extractConlluSents(TREEBANK_PATH)
	tokenlist=getSentsWithSentId(sentid,sents)[0]
	edited=_mergePronoun3PP(tokenlist)
	return edited,tokenlist

def issue480(sents=[]):
	if not sents:
		sents=extractConlluSents(TREEBANK_PATH)
	edt=[]
	for tokenlist in sents:
		edited = _mergePronoun3PP(tokenlist)
		if isinstance(edited,str):
			return edited
		if edited:
			edt.append(tokenlist.metadata['sent_id'])
			addReviewer(tokenlist)
	return edt

def insertFeat(token,newfeat,value):
	def condition(feat,feats):
		if feat == 'Mood':
			# return feats.get('VerbForm') == 'Fin'
			return feats.get('VerbForm') != 'Inf'
		return feat == 'VerbForm'
	dic={newfeat:value}
	feats=token.get('feats')
	if feats:
		oldfeat=feats.get(newfeat)
		if not oldfeat:
			if condition(newfeat,feats):
				token['feats'].update(dic)
	else:
		token['feats']=dic

def InsertIndDepClause(sent):
	tokenlist=sent.filter(upos='VERB', deprel='advcl')
	tokenlist.extend(sent.filter(upos='VERB', deprel='xcomp'))
	#tokenlist.extend(sent.filter(upos='VERB', deprel='ccomp')) # this is incorrect (issue #503)
	tokenlist.extend(sent.filter(upos='VERB', deprel='acl:relcl'))
	tokenlist.extend(sent.filter(upos='VERB', deprel='advcl:relcl'))
	for token in tokenlist:
		insertFeat(token,'Mood','Ind')

def InsertMoodNegClause(sent):
	tokenlist=sent.filter(xpos='NEGI')
	tokenlist.extend(sent.filter(xpos='NEG'))
	tokenlist.extend(sent.filter(xpos='COND'))
	mapping={'NEGI' : 'Imp', 'NEG' : 'Ind', 'COND' : 'Ind'} # TODO: include FUT?
	for token in tokenlist:
		headid = token['head']
		headlist=sent.filter(id=headid)
		if headlist:
			head=headlist[0]
			if head['upos'] == 'VERB':
				xpos=token['xpos']
				insertFeat(head,'Mood',mapping[xpos])

def InsertMoodInterClause(sent):
	tokenlist=sent.filter(feats__PartType="Int")
	tokenlist.extend(sent.filter(upos='PUNCT', lemma='?'))
	tokenlist.extend(sent.filter(feats__PronType="Rel"))
	for token in tokenlist:
		headid = token['head']
		headlist=sent.filter(id=headid)
		if headlist:
			head=headlist[0]
			if head['upos'] == 'VERB':
				insertFeat(head,'Mood','Ind')

def CopyMoodFromHeadVerb(sent):
	tokenlist=sent.filter(upos='AUX')
	tokenlist.extend(sent.filter(upos='VERB', deprel='conj'))
	tokenlist.extend(sent.filter(upos='VERB', deprel='parataxis'))
	for token in tokenlist:
		headid = token['head']
		headlist=sent.filter(id=headid)
		if headlist:
			head=headlist[0]
			if head['upos'] == 'VERB':
				feats=head.get('feats')
				if feats:
					mood=feats.get('Mood')
					if mood:
						insertFeat(token,'Mood',mood)
			else:
				insertFeat(token,'Mood','Ind')

def HandleMoodPerson(sent):
	for token in sent:
			if token['upos'] in ('AUX','VERB'):
				insertFeat(token,'VerbForm','Fin')
				feats=token.get('feats')
				if feats:
					person=feats.get('Person')
					if person == '2':
						insertFeat(token,'Mood','Imp,Ind')
					elif person in ('1','3'):
						insertFeat(token,'Mood','Ind')
					else:
						insertFeat(token,'Mood','Ind')

def insertMoodVerbForm(sents):
	for sent in sents:
		InsertIndDepClause(sent)
		InsertMoodNegClause(sent)
		InsertMoodInterClause(sent)
		CopyMoodFromHeadVerb(sent)
		HandleMoodPerson(sent)
		sortTokens(sent)

def ExtractCcompImp2Person(sents):
	"""Extract sentences from the treebank according to issue #503.
	"""
	newsents=[]
	for sent in sents:
		tokenlist=sent.filter(upos='VERB', feats__Person='2',feats__Mood="Ind",deprel='ccomp')
	if tokenlist:
		newsents.append(sent)
	return newsents

def mkDictRevisedSents(ccomp):
	"""Create a dictionary from the sentences returned by ExtractCcompImp2Person (issue #503)
	"""
	dic={}
	for sent in ccomp:
		sentid=sent.metadata['sent_id']
		dic[sentid]=sent
	return dic

def correctSents(sents,dic):
	"""Update the treebank with the manually corrected sentences (issue #503).
	"""
	i=0
	newsents=[]
	for sent in sents:
		sentid=sent.metadata['sent_id']
		newsent=dic.get(sentid)
		if newsent:
			newsents.append(newsent)
			i+=1
		else:
			newsents.append(sent)
	print(f"Total revised sentences: {i}")
	return newsents

def changeAdjToNoun(sent, lemma='kwera'):
	'''This function implements the analysis of "kwera" by Cruz (2011) ,referred to in issue #294. It transforms adjetives with lemma "kwera" attached to a head noun via the amod dependency relation into a noun the former one is attached to via the nmod:poss relation. 
	'''
	adjectives=sent.filter(lemma='kwera',upos='ADJ',deprel='amod')
	for adj in adjectives:
		head=sent.filter(upos='NOUN',id=adj['head'])
		if head:
			headnoun=head[0]
			adj['deprel']=headnoun['deprel']
			adj['head']=headnoun['head']
			adj['upos']='NOUN'
			adj['xpos']='N'
			updateFeats(adj,'Number','Sing')
			adpositions=sent.filter(head=headnoun['id'],upos='ADP',deprel='case')
			if adpositions:
				for adp in adpositions:
					adp['head']=adj['id']
			headnoun['head']=adj['id']
			headnoun['deprel']='nmod:poss'
			return True
		
def checkPron2(sents=[]):
	'''Detect sentences with PRON2 in an atypical configuration. See issue #536.
	'''
	if not sents:
		sents=extractConlluSents(TREEBANK_PATH)
	pron2=[]
	for sent in sents:
		results=sent.filter(xpos='PRON2')
		for r in results:
			headid=r['head']
			headlist=sent.filter(id=headid)
			if headlist and headlist[0]['xpos'] == 'V':
				case=sent.filter(deprel='case',head=r['id'])
				if not case:
					style=r.get('feats').get('Style')
					if not style:
						pron2.append(sent.metadata['sent_id'])
	return pron2

def checkPron(sents=[]):
	'''Detect sentences with the XPOS tag PRON in an atypical configuration. See issue #536.
	'''
	if not sents:
		sents=extractConlluSents(TREEBANK_PATH)
	pron=[]
	for sent in sents:
		results=sent.filter(xpos='PRON',feats__Person='3')
		for r in results:
			case=sent.filter(deprel='case',head=r['id'])
			if case:
				style=r.get('feats').get('Style')
				if not style:
					pron.append(sent.metadata['sent_id'])
	return pron

def addReviewer(sent):
	reviewers=[]
	d={}
	for k,v in sent.metadata.items():
		if k.startswith('reviewer'):
			reviewers.append(v)
	c=len(reviewers)
	if 'LFdeA' in reviewers or 'Leonel Figueiredo de Alencar' in reviewers:
		pass
	else:
		d=mkReviewer('leo',c+1)
	d['review_status']='ongoing'
	sent.metadata.update(d)
	
def issue536(sents):
	def repl(t):
		return t.replace("rũmu","rumu")
	for sent in sents:
		error='irũmu'
		correct='irumu'
		irumu=sent.filter(lemma=error) or sent.filter(form=error) or sent.filter(form=error.title())
		if irumu:
			text_orig = sent.metadata['text']
			sent.metadata['text']=repl(text_orig)
			if sent.metadata.get('text_orig'):
				print(sent.metadata['sent_id'])
			else:
				sent.metadata['text_orig']= text_orig
			for token in sent:
				if token['lemma']==error:
					token['lemma']=correct
				if token['form'].upper()==error.upper():
					token['form']=f"{error[0]}{correct[1:]}"
					token['lemma'] = correct

