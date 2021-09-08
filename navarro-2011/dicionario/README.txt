# Este documento descreve as etapas da compilação do 'sn-yrl-dict.txt', um dicionário de palavras que ocorrem no SN do nheengatu e suas respectivas etiquetas morfossintáticas
# Autora: Juliana Lopes Gurgel
# <julianalgurgel@alu.ufc.br>
# Última atualização: 06/09/2021

>>> Parte 1: revisão

a) Revisar classes dos verbetes.
b) Fazer lista de variantes e de formas irregulares (ver documento 'variantes-e-formas-irregulares.txt' na pasta 'metodologia').
c) Fazer lista de palavras ambíguas (ver documento 'verbetes-para-revisao.txt').
d) Fazer lista de verbetes sem classificação ou cuja classificação deve ser modificada (ver documento 'classificacao.txt' na pasta 'metodologia').

>>> Parte 2: pré-processamento para extração

a) Corrigir caracteres acentuados utilizando o programa 'replace-char-1.0.py'. Ex.: "e~" por "ẽ", gerando o arquivo 'glossario_corrigido.txt'.
b) Modificar classe de alguns verbetes e classificar verbetes sem classe no arquivo 'glossario_corrigido.txt' (ver documento 'classificacao.txt' na pasta 'metodologia').
c) Inventariar os padrões de abreviaturas das classes conforme aparecem no glossário para fazer a extração utilizando expressões regulares (ver documento 'abreviaturas-das-classes.txt' na pasta 'metodologia').
d) Revisar as variantes e as formas irregulares no 'glossario_corrigido.txt' (ver documento 'variantes-e-formas-irregulares.txt' na pasta 'metodologia').
e) Para evitar a inclusão indevida ou a exclusão indevida de verbetes no momento da extração (ver documento 'variantes-e-formas-irregulares.txt' na pasta 'metodologia'):
	(i) padronizar as entradas do tipo variante para "var. de" e do tipo irregular para "ver";
	(ii) adicionar classes das variantes e das formas irregulares de acordo com a classe do verbete de origem.
f) Usando o Sed, retirar do 'glossario_corrigido.txt' as interrogações (?1, ?2) de entradas lexicais como: maã?1 (pron. interr.) - 1. que? o que? 2. qual?  (ver documento 'linux-command-list.txt' na pasta 'metodologia')
g) Usando o Sed, retirar do 'glossario_corrigido.txt' os números (1, 2, 3, 4) de verbetes como: akaiú1 (s.) - caju; akaiú2 (s.) - ano. (ver documento 'linux-command-list.txt' na pasta 'metodologia')
h) Guardar cópias do glossário de cada passo da Etapa 2 e criar cópia 'glossario-preprocessed.txt' para Etapa 3.

>>> Parte 3: extração e finalização

a) Extrair do 'glossario-preprocessed.txt' os verbetes que pertencem às classes que ocorrem no SN, gerando arquivos como n.txt; adj1.txt; adj2.txt; etc. (ver documento 'abreviaturas-das-classes.txt' na pasta 'metodologia' para conferir os padrões de busca)
b) Revisar todos os arquivos gerados, para conferir se a extração foi feita corretamente (comparando o total de linhas do OUTFILE e o total de ocorrências no 'glossario-preprocessed.txt', ex.: total de 381 ocorrências para "(s.)" e "(s. / adj.)" e 381 linhas no 'n.txt')
c) Retirar a definição dos verbetes, utilizando o programa 'del-definition.py', de forma que cada arquivo de saída seja uma lista apenas com os verbetes.
d) Para verbetes com uma etiqueta, gerar tabelas com duas colunas, no modelo 'akaiú N' utilizando o programa 'tag-noun.py' (ver documento 'linux-command-list.txt' na pasta 'metodologia').
e) Juntar todas as tabelas em um só arquivo.
f) Extrair verbetes repetidos, para gerar tabela de palavras de duas ou mais classes à parte.
g) Para verbetes com duas ou mais etiquetas, manualmente gerar tabelas com duas colunas, no modelo 'pirasua [N, ADJ1]'.
h) Juntar todas as tabelas em um só arquivo e organizar os itens por ordem alfabética, gerando 'sn-yrl-dict.txt'.
