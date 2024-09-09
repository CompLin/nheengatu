#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Author: Leonel Figueiredo de Alencar
# Last update: September 9, 2024

INSTITUTIONS = {'min' : 'Biblioteca Brasiliana Guita e José Mindlin'}

PEOPLE = {
'gab' : 'Gabriela Lourenço Fernandes',
'sus': 'Susan Gabriela Huallpa Huanacuni',
'hel': 'Hélio Leonam Barroso Silva',
'leo': 'Leonel Figueiredo de Alencar',
'dom': 'Dominick Maia Alexandre',
'lev': 'Antônio Levy Melo Nogueira',
'jul': 'Juliana Lopes Gurgel',
'mar': 'Marcel Twardowsky Avila',
'viv': 'Vivianne Anselmo Nascimento'
}

ROLES=[ {'scr' : 'transcriber'},
{'an' : 'annotator', 'optional' : False,
'description' : '''This the person who performs the annotation, running Yauti on the
 sentence, checking the output for correction, and fixing any detected errors.
 The annotator is also responsible for checking text transcription, modernization, and translation,
 if these attributes are available.'''},
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

def mkRole(person='leo', text='text', abbreviation='an',institution=''):
	dic={}
	role=getRole(abbreviation)
	person=PEOPLE[person]
	if institution:
		person=f"{', '.join([person,INSTITUTIONS[institution]])}"
	dic[f"{'_'.join([text,role])}"]=person
	return dic

def mkTextModernizer(person='hel',text='text_por',institution=''):
	return mkRole(person, text, 'mod',institution)

def mkAnnotator(person='dom',text='text',institution=''):
	return mkRole(person, text, 'an',institution)

def mkReviewer(person='jul', number=1):
	return {f"{getRole('rev')}{number}" : PEOPLE[person]}

def mkTranscriber(person='gab',text='text_orig',modernizer=True, translation='por',institution=''):
	dic=mkRole(person=person, text=text, abbreviation='scr',institution=institution)
	if modernizer:
		dic.update(mkTextModernizer(person,f"text_{translation}",institution))
	return dic

def Mindlin(person='gab',modernizer=True):
	transcriber=mkTranscriber(person, modernizer=True,institution='min')
	return transcriber
