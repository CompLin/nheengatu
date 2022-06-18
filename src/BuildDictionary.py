#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Author: Leonel Figueiredo de Alencar
# Date May 30, 2022

import re, sys, os, json

DIR=os.path.join(os.path.expanduser("~"),"complin/nheengatu/data")

NFIN="NFIN"
MAPPING={}
for l in """
adj.\tA
adj. 2ª cl.\tA2
adv.\tADV
adv. intensif.\tADVS
adv. interr.\tADVR
adv. rel.\tADVL
art. indef.\tART
conj.\tCONJ
dem.\tDEM
num.\tNUM
interj.\tINTJ
s.\tN
part.\tPART
posp.\tADP
pron.\tPRON
pron. 2ª cl.\tPRON2
pron. indef.\tINDF
pron. interr.\tINT
pron. quant.\tQUANT
pron. relativo\tREL
suf.\tSUFF
pref.\tPREF
v.\tV
v. 2ª cl.\tV2
""".strip().split("\n"):
    k,v=l.split("\t")
    MAPPING[k]=v

REGEX=re.compile(
    r"""(\S+(\s+[^\d\W]+)?) # groups 0 and 1: lemma and optional 2nd token of lemma
    \s+(\d\s+)? # group 2: optional numerical index
    (\([^)]+\)\s+)? # groups 3 and 4: forms with a relational prefix and/or
    (\(se\)\s+)? # 3rd person singular inactive prefix
    \((\w+\.[^)]*)\) # group 5: part of speech information
    \s+\-(.+$) # group 6: gloss""",re.VERBOSE)

def extractLines(infile):
    return [line.strip() for line in open(infile,"r").readlines() if line.strip() != ""]

def extractEntries(lines):
    entries=[]
    for line in lines:
        m=REGEX.match(line)
        if m:
            entries.append(m.groups())
    return entries

def getpron2(s):
    return s.strip()[1:-1]

def getrel(s):
    s=s.strip()[1:-1]
    return [f.strip() for f in s.split(",")]

def getpos(s):
    return " ".join(s.split())

def buildGlossary(entries): #TODO: rename function
    glossary=[]
    for entry in entries:
        dic={}
        dic["lemma"] = entry[0]
        dic["pos"] = getpos(entry[5])
        dic["gloss"] = entry[6].strip()
        if entry[2]:
            var=entry[2].strip()
            dic["var"] = int(var)
        if entry[3] and entry[4]:
            rel=getrel(entry[3])
            pron2=getpron2(entry[4])
            dic["rel"], dic["pron2"] = rel, pron2
        elif entry[3] and getpron2(entry[3]) == "se":
            dic["pron2"] = getpron2(entry[3])
        elif entry[3] and not getpron2(entry[3]) == "se":
            rel=getrel(entry[3])
            dic["rel"] = rel
        glossary.append(dic)
    return glossary

def printWordTags(dic,outfile=sys.stdout):
        for entry in dic:
            " ".join(entry['pos'].split())
            print(f"{entry['lemma']}\t{entry['pos']}",file=outfile)

def makeNumber(forms):
    entries=set()
    for form,parse in forms:
        entries.add(f"{form}\t{parse}+SG")
        entries.add(f"{form}-itá\t{parse}+PL")
    return entries

def isImpersonal(gloss):
    return "(impess.)" in gloss # TODO: change 'gloss' to 'usage'

def conjugateVerb(lemma,pos):
    forms=set()
    dic={
    'a': '1+SG',
    're': '2+SG',
    'u': '3',
    'ya': '1+PL',
    'pe': '2+PL',
    'ta': '3+PL',
    'tau': '3+PL'
    }
    if lemma == "yuri":
        for pref,tag in dic.items():
            if not '3' in tag:
                forms.add(f"{pref}{lemma}\t{lemma}+{pos}+{tag}")
        forms.add(f"uri\t{lemma}+{pos}+3")
        return forms
    for pref,tag in dic.items():
        forms.add(f"{pref}{lemma}\t{lemma}+{pos}+{tag}")
    forms.add(f"{lemma}\t{lemma}+{pos}+{NFIN}")
    return forms

def WordParsePairs(glossary):
    pairs=set()
    for n in glossary:
        lemma=n.get('lemma')
        pos=n.get('pos') # TODO: change 'pos' to 'cat(egory) throughout the module'
        tags=[MAPPING.get(tag.strip()) for tag in pos.split("/")]
        rel=n.get('rel')
        forms=set()
        if rel:
            tag=tags[0]
            l=len(rel)
            if l == 2:
                forms.add((rel[0],f"{lemma}+{tag}+CONT"))
                ncont=rel[1].split("/")
                for form in ncont:
                    forms.add((form,f"{lemma}+{tag}+NCONT"))
                if tag == "N":
                    forms.add((lemma,f"{lemma}+{tag}+ABS"))
                    pairs.update(makeNumber(forms))
                else:
                    pairs.update(forms)
            elif l == 1:
                pairs.add(f"{lemma}\t{lemma}+{tag}+CONT")
                pairs.add(f"{rel[0]}\t{lemma}+{tag}+NCONT")
        else:
            for tag in tags:
                if tag in ('N','DEM','REL') or lemma in ('amú',):
                    pairs.update(makeNumber([(lemma,f"{lemma}+{tag}")]))
                elif tag == "V" and not isImpersonal(n.get('gloss')):
                    pairs.update(conjugateVerb(lemma,tag))
                else:
                    pairs.add(f"{lemma}\t{lemma}+{tag}")

    return pairs

def extractHomonyms(glossary):
    newdict=dict()
    for dic in glossary:
        lemma=dic.pop('lemma')
        if newdict.get(lemma):
            newdict[lemma].append(dic)
        else:
            newdict[lemma]=[dic]
    return newdict

def WordParseDict(pairs):
    dic={}
    for pair in pairs:
        word,parse = pair.split("\t")
        lemma,features = parse.split("+",1)
        if dic.get(word):
            dic[word].append((lemma,features))
        else:
            dic[word]=[(lemma,features)]
    return dic

def sort(s):
    i=s.index("\t")
    return s[i+1:]

def loadGlossary(glossary=None, infile="glossary.json"):
    if glossary:
        glossary=glossary
    else:
        with open(infile) as f:
            glossary = json.load(f)
    return glossary

def loadLexicon(infile="lexicon.json"):
    with open(infile) as f:
        lexicon = json.load(f)
    return lexicon

def getwords(key,value,glossary=None, infile="glossary.json"):
    glossary=loadGlossary(glossary,infile)
    return list(filter(lambda x: x.get(key) == value, glossary))

def inGloss(string,glossary=None, infile="glossary.json"):
    glossary=loadGlossary(glossary,infile)
    return list(filter(lambda x: string in x.get('gloss'),glossary))

def saveJSON(glossary, outfile="glossary.json"):
    with open(outfile, "w") as write_file:
        json.dump(glossary, write_file, indent=4, ensure_ascii=False)

def saveGlossary(infile="glossary.txt",outfile="glossary.json"):
    entries=extractEntries(extractLines(infile))
    glossary=buildGlossary(entries)
    saveJSON(glossary, outfile)

def endswith(token,suff):
    pat=rf"(^.+)({suff})(-itá)?$"
    match=re.match(pat,token)
    if match:
        return match.groups()

def insertA(word):
    if not endswith(word,'[aeiou]'):
        return f"{word}a"
    return accent(word)

def accent(word):
    mapping={'a': 'á', 'e': 'é', 'o': 'ó', 'u': 'ú', 'i': 'í'}
    for k,v in mapping.items():
        if word.endswith(k):
            return f"{word[:-1]}{v}"
    return word

def extract_pos(parses):
    poslist=[]
    for parse in parses:
        poslist.append(parse[1].split('+')[0])
    return poslist

featsdic={}
def extract_feats(parses):
    global featsdic
    featsdic={'[123]': 'person','SG|PL': 'number','ABS|NCONT|CONT' : 'rel'}
    entries=[]
    for lemma,feats in parses:
        new={}
        new['lemma']=lemma
        featslist=feats.split('+')
        new['pos']=featslist[0]
        for f in featslist[1:]:
            for k,v in featsdic.items():
                if f in k:
                    new[v]=f
        entries.append(new)
    return entries

def insertSingularNumber(entry):
    pos=entry.get('pos')
    if pos and pos == 'N':
        if not entry.get('number'):
            entry['number']='SG'

def removeNumber(entry,number,feats):
    if entry.get(number) == 'PL':
        #print('number removed')
        if number in feats:
            feats.remove(number)
    pos=entry.get('pos')
    if pos and pos != 'N':
        #print('number removed')
        if number in feats:
            feats.remove(number)

def isNoun(entry):
    return entry.get('pos') == 'N'

def copy_feats(entry1,entry2,number='number'):
    feats=['pos','suff']
    feats.extend(list(featsdic.values()))
    if entry1.get('default'):
        entry2['pos']=entry1['default']
    if entry2.get('pos'):
        feats.remove('pos')
    #print(f"entry 2 in copy_feats: {entry2}")
    removeNumber(entry2,number,feats)
    # or entry2.get('pos') != 'N'
    #print(feats)
    #print(feats)
    for feat in feats:
        value=entry1.get(feat)
        if value:
            entry2[feat]=value

def guesser(token,lexicon):
    plural={"pos": "N", "number": "PL"}
    mapping={
    "wasú": {"default": "N", "suff": "AUG", "function": accent},
    "mirĩ": {"default": "N", "suff": "DIM", "function": accent},
    "í|ĩ": {"default": "N", "suff": "DIM", "function": insertA},
    "wera": {"default": "V", "suff": "HAB", "function": accent},
    "rana": {"default": "N", "suff": "APPR","function": accent},
    "-kunhã": {"pos": "N",'suff' : 'F'},
    "-apigawa": {"pos": "N", 'suff' : 'M'},
    "sawa|tawa|pawa": {"pos": "N", "suff": "NMZ", "function": accent},
    "sara": {"pos": "N", "suff": "AGN", "function": accent},
    "tiwa": {"pos": "N", "suff": "COL", "function": accent},
    "íma": {"pos": "A", "suff": "PRIV", "function": accent},
    "wara|pura": {"pos": "A|N", "suff": "ORIG", "function": accent}
    }
    newentries=[]
    for suff,entry in mapping.items():
         groups=endswith(token,suff)
         if groups:
             lemmas=set()
             base=groups[0]
             lemmas.add(base)
             function=entry.get('function')
             if function:
                 base=function(base)
                 lemmas.add(base)
             #print(lemmas)
             for lemma in lemmas:
                parses=lexicon.get(lemma)
                if parses:
                    entries=extract_feats(parses)
                    for ent in entries:
                        new={}
                        new['lemma']=lemma
                        if entry.get('pos'):
                            new['pos']=entry['pos']
                        if groups[2] == '-itá':
                            new.update(plural)
                            #print(f"new: {new}")
                        copy_feats(ent,new)
                        new['suff']=entry['suff']
                        insertSingularNumber(new)
                        newentries.append(new)
             if not newentries:
                new={}
                if groups[2] == '-itá':
                    new.update(plural)
                new['lemma']=base
                copy_feats(entry,new)
                insertSingularNumber(new)
                newentries.append(new)
             break
    return newentries

def parse(word,lexicon=None,infile="lexicon.json"):
    if lexicon:
        lexicon=lexicon
    else:
        lexicon=loadLexicon(infile)
    parselist=lexicon.get(word)
    if parselist:
        for lemma,tags in parselist:
            print(f"{word}\t{lemma}+{tags}")

def words():
    return [ 'purangamirĩ', 'mirawasú', 'miraíma', 'miratiwa',
    'yurarawasú-itá', 'tatuí-itá', 'yuraraí-itá','miramirĩ-itá',
    'yuraraí', 'yawaretewasú', 'yurarawasú', 'tatuí', 'itaí',
    'takwarĩ', 'wiramirĩ', 'miramirĩ','yawareté-kunhã',
    'yurará-apigawa', 'yurará-kunhã', 'yurará-apigawa-itá',
    'yurará-kunhã-itá','yawareté-apigawa', 'yawareté-apigawa-itá',
    'sakurana', 'kawĩrana', 'umundawera',
    'kaapura', 'iwakapura', 'kaawara', 'iwakawara', 'pakuatiwa',
    'mbauíma', 'seẽíma', 'watasara', 'mbuesara', 'kamundusara',
    'kitikasara', 'surisawa', 'katusawa', 'yuraraíma']

def test(outfile='outfile.txt', words=words()):
    lexicon=loadLexicon()
    output={}
    for word in words:
        output[word]=guesser(word,lexicon)
    with open(outfile, 'w') as f:
        if outfile.endswith(".json"):
            json.dump(output,
            f,
            indent=4,
            ensure_ascii=False)
        else:
            for word,entries in output.items():
                print(word, end='\t', file=f)
                for entry in entries:
                    print(entry, end=" ",file=f)
            print(file=f)

def main(infile="glossary.txt",outfile="lexicon.json",path=None):
    if path:
        infile=os.path.join(path,infile)
        outfile=os.path.join(path,outfile)
    entries=extractEntries(extractLines(infile))
    glossary=buildGlossary(entries)
    pairs=list(WordParsePairs(glossary))
    pairs.sort(key= sort)
    with open(outfile, 'w') as f:
        if outfile.endswith(".json"):
            json.dump(WordParseDict(pairs),
            f,
            indent=4,
            ensure_ascii=False)
        else:
            print(*pairs,sep="\n",file=f)

if __name__ == "__main__":
    if len(sys.argv) > 0:
        main(*sys.argv[1:])
    else:
        main()
