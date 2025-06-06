#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Author: Leonel Figueiredo de Alencar
# Last update: February 13, 2025

import re

PAT=re.compile(r"^\w+$")

INSTITUTIONS = {'min' : 'Biblioteca Brasiliana Guita e José Mindlin',
                'dac' : '''DACILAT Project, FAPESP's Process No. 2022/09158-5'''
                }

PEOPLE = {
'gab' : 'Gabriela Lourenço Fernandes',
'sus': 'Susan Gabriela Huallpa Huanacuni',
'hel': 'Hélio Leonam Barroso Silva',
'leo': 'Leonel Figueiredo de Alencar',
'dom': 'Dominick Maia Alexandre',
'lev': 'Antônio Levy Melo Nogueira',
'jul': 'Juliana Lopes Gurgel',
'mar': 'Marcel Twardowsky Avila',
'viv': 'Vivianne Anselmo Nascimento',
'let': 'Letícia Farias Nunes',
'dav': 'Davi Sampaio Santos',
'ano': 'anonymized'
}

ROLES=[     {'scr' : 'transcriber', 'description' : 'This the person who … TODO','optional' : True, 'requires' : 'text_prim'},
       
            {'an' : 'annotator', 'optional' : False,'description' : '''This the person who performs the annotation, running Yauti on the sentence, checking the output for correction, and fixing any detected errors. The annotator is also responsible for checking text transcription, modernization, and translation, if these attributes are available.''', 'requires' : 'text'},
            
            {'nsl' : 'translator', 'description' : 'This the person who … TODO', 'optional' : True},
            {'mod' : 'modernizer', 'description' : 'This the person who … TODO','optional' : True},
            {'rev' : 'reviewer', 'description' : 'This the person who … TODO', 'optional' : True, 'requires' : 'text_annotator'}
]

TEXT= [ {'attribute_name': 'text', 'description': '''This the annotated text in adapted spelling if the original text does not conform to Avila's (2021) orthography.''', 'optional' : False},
       
       {'attribute_name': 'text_orig', 'description': '''This the original text of the publication referred to in the sentence identity attribute it this text does not conform to Avila's (2021) orthography.''', 'optional' : True, 'requires': 'text'},
       
       {'attribute_name': 'text_prim', 'description': '''This the primary text the publication referred to in the sentence identity attribute cites in the text_source attribute.''', 'optional' : True, 'requires': 'text'},
       
       {'attribute_name': 'text_sec', 'description': '''This a version of the original text steming from a secondary source.''', 'optional' : True, 'requires': 'text_orig'},
       
        {'attribute_name': 'text_por_sec', 'description': '''This a version of the original text steming from a secondary source.''', 'optional' : True, 'requires': 'text_por'},
       
    ]

SOURCE= [ {'attribute_name': 'text_source', 'description': '''TODO ….''', 'optional' : False},
         
         {'attribute_name': 'text_sec_source', 'description': '''TODO ….''', 'optional' : True, 'requires': 'text_sec'},
          
        {'attribute_name': 'text_por_sec_source', 'description': '''TODO ….''', 'optional' : True, 'requires': 'text_por_sec'},
    ]
def getRole(abbreviation='an'):
	role=''
	for dic in ROLES:
		role=dic.get(abbreviation)
		if role:
			break
	return role

def handleAbbreviation(abbreviation):
    name = PEOPLE.get(abbreviation)
    if not name:
        if PAT.search(abbreviation):
            raise ValueError("Non-registered abbreviation")
        else:
            name = abbreviation
    return name

def mkRole(person='leo', text='text', abbreviation='an', institution=''):
    dic = {}
    name = handleAbbreviation(person)  # Let the error propagate if it occurs
    role = getRole(abbreviation)
    if institution:
        name = f"{', '.join([name, INSTITUTIONS[institution]])}"
    dic[f"{'_'.join([text, role])}"] = name
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

def Dacilat(person='dom',modernizer=True):
	transcriber=mkTranscriber(person, modernizer=True,institution='dac')
	return transcriber

def mkTextGloss(gloss,lang='por'):
    metadata={}
    metadata[f"text_{lang}_gloss"]=gloss
    return metadata
