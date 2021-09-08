#! /usr/bin/env python3
# -*- coding: utf-8 -*-

# Authors: Juliana Lopes Gurgel; Leonel Figueiredo de Alencar Araripe
# <julianalgurgel@alu.ufc.br; leonel.de.alencar@ufc.br>
# Date: 03/22/2021

""" Usage:

replace_char_new.py INPUT_FILE

Example:

replace_char_new.py test.txt

"""
import sys
'This program corrects some characters in a given file'

def replace_char(infile,outfile):
    for i in infile:
        char = i.replace("a:", "â").replace("e:", "ê").replace("o:", "ô").replace("`a", "à").replace("\:", ":").replace("c,", "ç").replace("a'", "á").replace("e'", "é").replace("i'", "í").replace("o'", "ó").replace("u'", "ú").replace("a~", "ã").replace("e~", "ẽ").replace("i~", "ĩ").replace("o~", "õ").replace("u~", "ũ")
        print(char, end="", file=outfile)

    infile.close()
    outfile.close()


def main():
    infilename=sys.argv[1]
    outfilename="%s.edt.txt" % (infilename.split(".",1)[0])
    infile = open(infilename, 'r', encoding='utf-8')
    outfile = open(outfilename, 'w', encoding='utf-8')
    replace_char(infile,outfile)
    print('Output has been written to', outfilename)

if __name__ == '__main__':
	main()
