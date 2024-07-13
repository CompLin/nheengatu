#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Author: Leonel Figueiredo de Alencar
# Last update: Janaury 17, 2024

# https://en.wikipedia.org/wiki/Compose_key
# https://math.dartmouth.edu/~sarunas/Linux_Compose_Key_Sequences.html
# https://en.wiktionary.org/wiki/Appendix:Unicode/Latin_Extended_Additional
# Magalhães (1876: 1-3): explanation about the phonetic transcription system of Nheengatu (PDF 53-56)
# MAGALHÃES, Couto de. O selvagem: curso da língua geral segundo Ollendorf; origens, costumes, região selvagem. Rio de Janeiro: Tipografia da Reforma, 1876.
# https://www.literaturabrasileira.ufsc.br/documentos/?id=135896
'''
Mapping from k to {'char':v,'code':p,'phonetic':f, 'name':n, 'compose':c}, where

k is an alternativa character that can be directly typed in or using a compose-key sequence;

v is the Unicode character the present script will substitute for k;

p is the Unicode code point of v;

f is the phonetic value;

n is the name of p;

c is the compose key sequence of k;

'''

MAPPING={
	'ë':{'char':'ẹ', 'code':'U+1EB9','phonetic':'close e', 'name':'LATIN SMALL LETTER E WITH DOT BELOW'},
	'ö':{'char':'ọ','code':'U+1ECD','phonetic':'close o', 'name':'LATIN SMALL LETTER O WITH DOT BELOW'},

	'ä':{'char':'ạ','code':'U+1EA1','phonetic':'close a','name':'LATIN SMALL LETTER A WITH DOT BELOW'},

	'ê':{'char':'ệ','code':'U+1EC7','phonetic':'stressed close e', 'name':'LATIN SMALL LETTER E WITH CIRCUMFLEX AND DOT BELOW'},

	'ĕ': {'char':'ệ','variant': 'ê', 'compose':'be'},

	'ē': {'char':'ệ','variant': 'ê', 'compose':'_e'},

	'â':{'char':'ậ','code':'U+1EAD','phonetic':'stressed close a','name':'LATIN SMALL LETTER A WITH CIRCUMFLEX AND DOT BELOW'},

	'ô':{'char':'ộ','code':'U+1ED9','phonetic':'stressed close o', 'name':'LATIN SMALL LETTER O WITH CIRCUMFLEX AND DOT BELOW'},

	'œ': {'char':'ộ','variant': 'ô', 'compose':'oe'},

	#'y':{'char':'ɨ','code':'U+0268', 'phonetic':'Close central unrounded vowel','name':'LATIN SMALL LETTER I WITH STROKE'},

	'ý':{'char':'ɨ','variant': 'y', 'compose':"'y"},

	'å':{'char':'ẫ','code':'U+1EAB','phonetic':'stressed nasal a', 'name':'LATIN SMALL LETTER A WITH CIRCUMFLEX AND TILDE', 'compose':'oa'},

	'ā':{'char':'ẫ','variant': 'å', 'compose':'_a'},

	'ă': {'char':'ẫ','variant': 'å', 'compose':'ba'},

	'ŏ':{'char':'ṍ', 'code':'U+1E4D','phonetic':'stressed nasal o', 'name':'LATIN SMALL LETTER O WITH TILDE AND ACUTE', 'compose':'bo'},

	'ō':{'char':'ṍ','variant': 'ŏ', 'compose':'_o'},

	'ø':{'char':'ô', 'phonetic':'possibly stressed close o', 'compose':'/o', 'example': '''"ipô" in "Paraná	oçuaxára:	— Ah,	iáutí,	inệ	ipø	rẹiúiútɨma	putári	mocộĩ	uê!" (p. 180, PDF 232), cf. "[...] ahé	ipộ	oçộ	rẹtệãna.(p. 179, PDF 231)"'''},

	'ò':{'char':'ô', 'variant': 'ø', 'compose':'`o'},

	'è':{'char':'ê', 'phonetic':'possibly stressed close e', 'compose':'`e', 'example': '''"uê", "wé" in Avila (2021), in "Paraná	oçuaxára:	— Ah,	iáutí,	inệ	ipø	rẹiúiútɨma	putári	mocộĩ	uê!" (p. 180, PDF 232)'''}
}


def mkTable(mapping=MAPPING):
	table=[]
	for k,d in MAPPING.items():
		table.append((k,d['char']))
	return table

def mkDictionary(mapping=MAPPING):
	dic={}
	for k,v in mapping.items():
		dic[k]=v['char']
	return dic

TABLE=mkTable()
DICTIONARY=mkDictionary()

def translate(string,dic=DICTIONARY):
	table=str.maketrans(dic)
	return string.translate(table)

def replace(string,table=TABLE):
	for old, new in table:
		string=string.replace(old,new)
	return string

def parseText(infile):
	text=open(infile, encoding="utf-8").read().strip()
	pairs=text.split("\n\n")
	sents=[]
	i=0
	c=len(pairs)
	while(i<c):
		pair=pairs[i]
		parts=pair.strip().split("\n")
		if len(parts) == 2:
			yrl,por = parts
			dic={}
			dic['yrl']=yrl.split("\t")
			dic['por']=por.split("\t")
			dic['sent_num']=i+1
			sents.append(dic)
		else:
			print(i,pair)
		i+=1
	return sents

def checkAlignment(sents):
	errors=[]
	for sent in sents:
		yrl,por=sent['yrl'],sent['por']
		if len(yrl) != len(por):
			errors.append(sent)
	return errors

def pprint(sents):
	msg="Sentence number: "
	sep=f"{(len(msg)+4)*'-'}"
	for sent in sents:
		yrl,por=sent['yrl'],sent['por']
		c=min(len(yrl),len(por))
		i=0
		print(f"{sep}\n{msg}{sent['sent_num']}.\n{sep}")
		while(i<c):
			print(yrl[i],por[i],sep="\n",end="\n\n")
			i+=1

def printAlignmentErrors(infile):
	sents=parseText(infile)
	errors=checkAlignment(sents)
	er=len(errors)
	sn=len(sents)
	if len(errors):
		pprint(errors)
		print(f"\n{er} out of {sn} sentences ({er/sn*100:.2f}%) has alignment problems.")
