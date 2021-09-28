print('This program corrects some characters in a given file')

infilename = input('Infile name ')
outfilename = "%s_output.txt" % (infilename.split(".",1)[0])

infile = open(infilename, 'r', encoding='utf-8')
outfile = open(outfilename, 'w+', encoding='utf-8')

for i in infile:
    char = i.replace("a:", "â").replace("e:", "ê").replace("o:", "ô").replace("`a", "à").replace("\:", ":").replace("c,", "ç").replace("a'", "á").replace("e'", "é").replace("i'", "í").replace("o'", "ó").replace("u'", "ú").replace("a~", "ã").replace("e~", "ẽ").replace("i~", "ĩ").replace("o~", "õ").replace("u~", "ũ")
    print(char, end="", file=outfile)

infile.close()
outfile.close()

print('O nome do novo arquivo é', outfilename)
