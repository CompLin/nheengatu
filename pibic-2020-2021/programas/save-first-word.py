# Programa idealizado para extrair os verbetes e suas respectivas classes do vocabulário de Navarro (2011).
# Não foi utilizado por conta dos diferentes padrões das entradas lexicais presentes no vocabulário.
# A extração dos verbetes foi feita no terminal do Unix por meio de expressões regulares.

# Reading from file
text = open('text.txt', 'r').read()

# Sample text: It is the same in 'text.txt'
text = '''palavra (n) - (1) bla bla
outra-palavra (v.) - bla bla-bla'''

# Ideia: 
# 1) ler cada linha
# 2) dividir cada linha em um lista palavras (strings)
# 3) localizar onde se encontra "-"
# 4) salvar todas as palavras do começo da frase até "-" em uma nova lista
# 5) transformar a nova lista em uma string de novo 
for line in text.splitlines():                  # 1)
    list_of_words = line.split()                # 2)
    index_of_hifen = list_of_words.index("-")   # 3)
    new_line = line.split()[0:index_of_hifen]   # 4)
    new_line = " ".join(new_line)               # 5)
    print(new_line)
