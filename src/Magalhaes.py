#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Author: Leonel Figueiredo de Alencar
# Last update: June 27, 2023

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

	'â':{'char':'ậ','code':'U+1EAD','phonetic':'stressed close a','name':'LATIN SMALL LETTER A WITH CIRCUMFLEX AND DOT BELOW'},

	'ô':{'char':'ộ','code':'U+1ED9','phonetic':'stressed close o', 'name':'LATIN SMALL LETTER O WITH CIRCUMFLEX AND DOT BELOW'},

	'y':{'char':'ɨ','code':'U+0268', 'phonetic':'Close central unrounded vowel','name':'LATIN SMALL LETTER I WITH STROKE'},

	'å':{'char':'ẫ','code':'U+1EAB','phonetic':'stressed nasal a', 'name':'LATIN SMALL LETTER A WITH CIRCUMFLEX AND TILDE', 'compose':'oa'},

	'ā':{'char':'ẫ','variant': 'å', 'compose':'_a'},
	
	'ă': {'char':'ẫ','variant': 'å', 'compose':'ba'},
	
	'ŏ':{'char':'ṍ', 'code':'U+1ED7','phonetic':'stressed nasal o', 'name':'LATIN SMALL LETTER O WITH CIRCUMFLEX AND TILDE', 'compose':'bo'},

	'ø':{'char':'ô', 'phonetic':'possibly stressed close o', 'compose':'/o', 'example': '''"ipô" in "Paraná	oçuaxára:	— Ah,	iáutí,	inệ	ipø	rẹiúiútɨma	putári	mocộĩ	uê!" (p. 180, PDF 232), cf. "[...] ahé	ipộ	oçộ	rẹtệãna.(p. 179, PDF 231)"'''},
	
	'ò':{'char':'ô', 'variant': 'ø', 'compose':'`o'},
	
	'è':{'char':'ê', 'phonetic':'possibly stressed close e', 'compose':'`e', 'example': '''"uê", "wé" in Avila (2021), in "Paraná	oçuaxára:	— Ah,	iáutí,	inệ	ipø	rẹiúiútɨma	putári	mocộĩ	uê!" (p. 180, PDF 232)'''}
}


def mkTable(mapping=MAPPING):
	table=[]
	for k,d in MAPPING.items():
		table.append((k,d['char']))
	return table

TABLE=mkTable()

def main(string,table=TABLE):
	for old, new in table:
		string=string.replace(old,new)
	return string

