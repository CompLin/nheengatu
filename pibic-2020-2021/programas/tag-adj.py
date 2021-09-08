print("Esse programa gera uma tabela de adjetivos no modelo 'apara A2' a partir de glossario-preprocessed.txt")

#infile1 = open('a1.txt', 'r').read()
infile2 = open('a2.txt', 'r').read()
#outfile1 = open('a1-tagged.txt', 'w', encoding='utf-8')
outfile2 = open('a2-tagged.txt', 'w', encoding='utf-8')

#for line in infile1.splitlines():
#    new_line = line.split()[0]
#    new_line = new_line + " A1"
#    print(new_line, file=outfile1)
    	
for line in infile2.splitlines():  	
    new_line = line.split()[0]
    new_line = new_line + " A2"
    print(new_line, file=outfile2)
    	

    	



