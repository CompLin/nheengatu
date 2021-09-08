#! /usr/bin/env python3
# -- coding: utf-8 --
# Copyright © 2021 Federal University of Ceará

# Authors: Leidiana Iza Andrade Freitas, Dominick Maia Alexandre, Juliana Lopes Gurgel
# <izafreitas@alu.ufc.br; domimaia@alu.ufc.br; julianalgurgel@alu.ufc.br>
# Date: 29/05/2021

import pandas as pd

yrl_glossary = 'dic_test.txt'

infilename = input('Infile name: ')
outfilename="%s_output.txt" % (infilename.split(".",1)[0])

with open(infilename, 'r', encoding='utf-8') as f:
    infile = f.readlines()

# defining function to tag words
def tag_word(line, glossary):
    tagged_word = line.lower()

# tagging words
    for word, tag in glossary.items():
        tagged_word = tagged_word.replace(word.lower(), word.lower() + '\\' + tag)

# tagging nouns inflected in the plural
        if '\\N-itá' in tagged_word:
            tagged_word = tagged_word.replace('\\N-itá', '-itá')
            tagged_word = tagged_word.replace(word.lower(), word.lower() + '\\' + tag)

# printing proper names with capital letters
        if 'N-PRO' in tag:
            tagged_word = tagged_word.replace(word.lower(), word.capitalize())
# printing uppercase tags
    for tag in glossary.values():
            tagged_word = tagged_word.replace(tag, tag.upper())

    return tagged_word[0].upper() + tagged_word[1:]

df = pd.read_csv(yrl_glossary, sep='\t', header=None, index_col=0)
glossary = df.to_dict()[1]

# infile will contain a list where each item is a line
# e.g. infile[0] = line 1.
with open(infilename) as file:
    lines = file.readlines()
lines = [word.strip() for word in lines if word != '\n']

# tagging words in each line of the infile with tag_word function
tagged_words = [tag_word(word, glossary) for word in lines]

# saving tagged outfile
with open(outfilename, 'w+', encoding='utf-8') as outfile:
    for tagged_word in tagged_words:
        outfile.write(f'{tagged_word}\n\n')
