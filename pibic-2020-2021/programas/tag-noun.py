print("Esse programa gera uma tabela de nomes no modelo 'akaiú N' a partir de glossario-preprocessed.txt")

infilename = input('Infile name: ')
outfilename="%s-tagged.txt" % (infilename.split(".",1)[0])
infile = open(infilename, 'r', encoding='utf-8').read()
outfile = open(outfilename, 'w', encoding='utf-8')

for line in infile.splitlines():
    new_line = line.split()[0]
    new_line = new_line + " N"
    print(new_line, file=outfile)
