print("Esse programa gera uma tabela de adjetivos no modelo 'ixé PRON1' a partir de glossario-preprocessed.txt")

infile1 = open('pron1.txt', 'r').read()
#infile2 = open('pron2.txt', 'r').read()
outfile1 = open('pron1-tagged.txt', 'w', encoding='utf-8')
#outfile2 = open('pron2-tagged.txt', 'w', encoding='utf-8')

for line in infile1.splitlines():
	new_line = line.split()[0]
	new_line = new_line + " PRON1"
	print(new_line, file=outfile1)

#for line in infile2.splitlines():
#	new_line = line.split()[0]
#	new_line = new_line + " PRON2"
#	print(new_line, file=outfile2)	
	



    	

    
    	

    	



