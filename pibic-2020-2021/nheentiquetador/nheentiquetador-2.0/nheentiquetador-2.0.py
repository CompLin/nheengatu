#! /usr/bin/env python3
# -- coding: utf-8 --
# Copyright © 2021 Federal University of Ceará

# Authors: Dominick Maia Alexandre, Juliana Lopes Gurgel
# <domimaia@alu.ufc.br; julianalgurgel@alu.ufc.br>
# Date: 09/07/2021

import pandas as pd

yrl_glossary = 'sn-yrl-dict.txt'

with open('TEST-SET.txt', 'r', encoding='utf-8') as f:
    infile = f.readlines()

df = pd.read_csv(yrl_glossary, sep='\t', header=None, index_col=0)
glossary = df.to_dict()[1]

outlines = []

for line in infile:
    list_of_words = line.lower().split()

    new_line = ''

    for word in list_of_words:

        if word in glossary:
            new_line += word + '\\' + glossary[word] + ' '
        else:
            new_line += word + ' '

    outlines.append(new_line.strip() + '\n')

with open('TEST-SET-tagged.txt', 'w', encoding='utf-8') as f:
    f.writelines(outlines)
