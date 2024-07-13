#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Author: Leonel Figueiredo de Alencar
# Last update: July 13, 2024

PEOPLE = {
'gab' : "Gabriela Lourenço Fernandes",
'sus': 'Susan Gabriela Huallpa Huanacuni',
'hel': 'Hélio Leonam Barroso Silva',
'leo': 'Leonel Figueiredo de Alencar',
'dom': 'Dominick Maia Alexandre',
'lev': 'Antônio Levy Melo Nogueira',
'jul': 'Juliana Lopes Gurgel',
'mar': 'Marcel Twardowsky Avila'
}

INSTITUTIONS = {'min' : 'Biblioteca Brasiliana Guita e José Mindlin'}

ROLES=[ {'scr' : 'transcriber'},
{'an' : 'annotator', 'optional' : False,
'description' : '''This the person who performs the annotation, running Yauti on the
 sentence, checking the output for correction, and correcting any detected errors.
 The annotator is also responsible for checking text transcription, modernization, and translation.'''},
{'nsl' : 'translator', 'optional' : True,},
{'mod' : 'modernizer', 'optional' : True},
{'rev' : 'reviewer', 'optional' : True}
]

def getRole(abbreviation='an'):
	role=''
	for dic in ROLES:
		role=dic.get(abbreviation)
		if role:
			break
	return role

def mkRole(person='leo', text='text', abbreviation='an'):
	dic={}
	role=getRole(abbreviation)
	dic[f"{'_'.join([text,role])}"]=PEOPLE[person]
	return dic

def mkTextModernizer(person='hel',text='text_por'):
	return mkRole(person, text, 'mod')

def mkAnnotator(person='dom',text='text'):
	return mkRole(person, text, 'an')

def mkReviewer(person='jul', number=1):
	return {f"{getRole('rev')}{number}" : PEOPLE[person]}

def mkTranscriber(person='gab',text='text_orig',modernizer=True, translation='por'):
	dic=mkRole(person=person, text=text, abbreviation='scr')
	if modernizer:
		dic.update(mkTextModernizer(person,f"text_{translation}"))
	return dic

def Mindlin(person='gab',institution='min',modernizer=True):
	person=PEOPLE[person]
	institution=INSTITUTIONS[institution]
	person=f"{person}, {institution}"
	transcriber=mkTranscriber(person, modernizer=True)
	return transcriber
