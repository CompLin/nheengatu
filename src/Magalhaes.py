#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Author: Leonel Figueiredo de Alencar
# Last update: June 27, 2023

# https://en.wikipedia.org/wiki/Compose_key
# https://math.dartmouth.edu/~sarunas/Linux_Compose_Key_Sequences.html
# https://en.wiktionary.org/wiki/Appendix:Unicode/Latin_Extended_Additional
# Magalhães (1876: 1-3): explanation about the phonetic transcription system of Nheengatu
'''
Mapping from k to v, where k is an alternativa character
that can be typed using a compose-key sequence,
which will be replaced by the
Latin Extended Additional Unicode character v
by means of the present script.'''

MAPPING={'ë':'ẹ',
'ö':'ọ',
'ä':'ạ',
'ê':'ệ',
'â':'ậ',
'ô':'ộ',
'y':'ɨ',
'å':'ẫ',
'ā': 'ẫ',
'ă': 'ẫ',
'ŏ':'ṍ',
'ø':'ô'
}
