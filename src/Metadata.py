#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Author: Leonel Figueiredo de Alencar
# Last update: June 23, 2024

PEOPLE = {
'gab' : "Gabriela Lourenço Fernandes",
'sus': 'Susan Gabriela Huallpa Huanacuni'
}

INSTITUTIONS = {'min' : 'Biblioteca Brasiliana Guita e José Mindlin'}

def Mindlin(person=PEOPLE['gab'],institution=INSTITUTIONS['min'],modernizer=True):
	person=f"{person}, {institution}"
	transcriber={'text_orig_transcriber': person}
	if modernizer:
		transcriber.update({'text_por_modernizer': person})
	return transcriber
