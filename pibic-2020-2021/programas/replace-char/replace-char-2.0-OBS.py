#! /usr/bin/env python3 #para poder rodar em qualquer lugar
# -*- coding: utf-8 -*-

# Author: 
# email@server
# Date: 

""" Usage:

replace_char_new.py INPUT_FILE

Example:

replace_char_new.py test.txt

"""
# a biblioteca sys relacionada ao sistema
import sys
'This program corrects some characters in a given file'

# def é 'definição de função'. serve para definir uma função
# e reaproveitar a função, fazendo uma abertura no fluxo de leitura
# : serve para dizer que a partir daí começa as instruções
# 'pass' pro interpretador passar para a próxima linha
# toda função que é declarada ela precisa ser retornada
# para retornar precisa retornar a função
def replace_char(infile,outfile):
    for i in infile:
        char = i.replace("a:", "â").replace("e:", "ê").replace("o:", "ô").replace("`a", "à").replace("\:", ":").replace("c,", "ç").replace("a'", "á").replace("e'", "é").replace("i'", "í").replace("o'", "ó").replace("u'", "ú").replace("a~", "ã").replace("e~", "ẽ").replace("i~", "ĩ").replace("o~", "õ").replace("u~", "ũ")
        print(char, end="", file=outfile)

    infile.close()
    outfile.close()

# a função replace_char(infile,outfile) está dentro da função main()
def main():
    infilename=sys.argv[1]
    outfilename="%s.edt.txt" % (infilename.split(".",1)[0])
    infile = open(infilename, 'r', encoding='utf-8')
    outfile = open(outfilename, 'w', encoding='utf-8')
    replace_char(infile,outfile)
    print('Output has been written to', outfilename)

if __name__ == '__main__':
	main()
