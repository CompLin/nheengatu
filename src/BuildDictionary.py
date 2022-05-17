#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Author: Leonel Figueiredo de Alencar
# Date May 4, 2022

import re, sys
from Nheengatagger import extractLines

MAPPING={}
for l in """
adj.\tA
adj. 2ª cl.\tA2
adv.\tADV
adv. intensif.\tADVS
adv. interr.\tADVR
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
v.\tV
v. 2ª cl.\tV2
""".strip().split("\n"):
	k,v=l.split("\t")
	MAPPING[k]=v

REGEX=re.compile(r"""(\S+)\s+(\d\s+)? # groups 0 and 1: the lemma possibly followed by a numerical index
    (\([^)]+\)\s+)? # groups 2 and 3: forms with a relational prefix and/or
    (\(se\)\s+)? # 3rd person singular inactive prefix
    \((\w+\.[^)]*)\) # group 4: part of speech information
    \s+\-(.+$) # group 5: gloss""",re.VERBOSE)

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
    s=s[1:-1]
    return [f.strip() for f in s.split(",")]

def getpos(s):
	return " ".join(s.split())

def build(entries):
    dictlist=[]
    for entry in entries:
        dic={}
        dic["lemma"] = entry[0]
        dic["pos"] = getpos(entry[4])
        dic["gloss"] = entry[5]
        if entry[1]:
            dic["var"] = int(entry[1])
        if entry[2] and entry[3]:
            rel=getrel(entry[2])
            pron2=getpron2(entry[3])
            dic["rel"], dic["pron2"] = rel, pron2
        elif entry[2] and getpron2(entry[2]) == "se":
            dic["pron2"] = getpron2(entry[2])
        elif entry[2] and not getpron2(entry[2]) == "se":
            dic["rel"] = getrel(entry[2])
        dictlist.append(dic)
    return dictlist

def getwords(key,value,dictlist):
	return list(filter(lambda x: x.get(key) == value, dictlist))

def printWordTags(dic,outfile=sys.stdout):
		for entry in dic:
			" ".join(entry['pos'].split())
			print(f"{entry['lemma']}\t{entry['pos']}",file=outfile)

def makeNumber(forms):
	entries=[]
	for form,parse in forms:
		entries.append(f"{form}\t{parse}+SG")
		entries.append(f"{form}-itá\t{parse}+PL")
	return entries

def isImpersonal(gloss):
    return "(impess.)" in gloss # TODO: change 'gloss' to 'usage'

def conjugateVerb(lemma,pos):
	forms=[]
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
				forms.append(f"{pref}{lemma}\t{lemma}+{pos}+{tag}")
		forms.append(f"uri\t{lemma}+{pos}+3")
		return forms
	for pref,tag in dic.items():
		forms.append(f"{pref}{lemma}\t{lemma}+{pos}+{tag}")
	return forms

def WordParsePairs(dic):
    pairs=[]
    for n in dic:
        lemma=n.get('lemma')
        pos=n.get('pos') # TODO: change 'pos' to 'cat(egory) throughout the module'
        tags=[MAPPING.get(tag.strip()) for tag in pos.split("/")]
        rel=n.get('rel')
        forms=[]
        if rel:
            tag=tags[0]
            l=len(rel)
            if l == 2:
                forms.append((rel[0],f"{lemma}+{tag}+CONT"))
                forms.append((rel[1],f"{lemma}+{tag}+NCONT"))
                if tag == "N":
                    forms.append((lemma,f"{lemma}+{tag}+ABS"))
                    pairs.extend(makeNumber(forms))
                else:
                    pairs.extend(forms)
            elif l == 1:
                pairs.append(f"{lemma}\t{lemma}+{tag}+CONT")
                pairs.append(f"{rel[0]}\t{lemma}+{tag}+NCONT")
        else:
            for tag in tags:
                if tag == "N":
                    pairs.extend(makeNumber([(lemma,f"{lemma}+N")]))
                elif tag == "V" and not isImpersonal(n.get('gloss')):
                    pairs.extend(conjugateVerb(lemma,tag))
                else:
                    pairs.append(f"{lemma}\t{lemma}+{tag}")

    return pairs

def main(infile,outfile):
    entries=extractEntries(extractLines(infile))
    dictlist=build(entries)
    pairs=WordParsePairs(getwords("pos","s.",dictlist))
    with open(outfile, 'w') as f:
        print(*pairs,file=f)


if __name__ == "__main__":
        main(sys.argv[1])
