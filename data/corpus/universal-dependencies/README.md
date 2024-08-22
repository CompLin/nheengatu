# Summary

The [UD_Nheengatu-CompLin](https://aclanthology.org/2024.propor-2.8) is a treebank of [Nheengatu](https://glottolog.org/resource/languoid/id/nhen1239) or Nhengatu (ISO-639: `yrl`), also known, inter alia, as Modern Tupi and *Língua Geral Amazônica*. It comprises sentences from diverse published sources, e.g., spontaneous speech, grammatical descriptions, fables, myths, coursebooks, and dictionaries.


# Introduction

To our knowledge, this is the first treebank of Nheengatu. It is a work in progress. The initial release only contained a couple hundred sentences. This new release encompasses more than seven times that number. We plan to continually expand the resource in the next months.

The treebank comprises sentences from diverse published sources freely available on the Internet, e.g., grammatical descriptions, fables, coursebooks, and dictionaries. The sentences were either extracted from PDF text files, transcribed from non-searchable (image-only) PDF files, or manually converted to orthography from phonetic transcriptions. Throughout the treebank, we use the spelling system proposed by Avila (2021). The annotation was performed semi-automatically, i.e., we first applied the Yauti morphosyntactic analyzer (de Alencar 2023) to each sentence and then manually revised the output.

The development of this treebank and related tools and resources is part of the research activities of the Research Group on Computation and Natural Language (*Computação e Linguagem Natural* — CompLin) at the Humanities Center of the Federal University of Ceará in Brazil. The main contributor to this effort is Leonel Figueiredo de Alencar, coordinator of the CompLin group. Additional annotators include Dominick Maia Alexandre and Juliana Lopes Gurgel, scholarship holder with the [DACILAT](https://bv.fapesp.br/57063) project, funded by the São Paulo State Research Support Foundation (*Fundação de Amparo à Pesquisa do Estado de São Paulo* — FAPESP) under Process No. 22/09158-5.

The following repository contains the most update development version of the treebank as well as related tools and resources:

https://github.com/CompLin/nheengatu

So far, the treebank includes examples from Seixas (1853), Magalhães (1876), Sympson (1877), Rogrigues (1890), Aguiar (1898), Costa (1909), Studart (1926), Amorim (1928), Hartt (1938), Moore, Facundes, and Pires (1994), Casasnovas (2006), Cruz (2011), Comunidade de Terra Preta (2013), Stradelli (1929/2014), Navarro (2016), Muller et al. (2019), Alencar (2021), Avila (2021), and Melgueiro (2022) as well as from the New Testament (*Novo Testamento na língua Nyengatu*, 1973/2019).

# How to cite
If use any of the tools and resources of this repository, please cite the following papers accordingly:

## ACM reference format:

Leonel Figueiredo de Alencar. 2024. [A Universal Dependencies Treebank for Nheengatu](https://aclanthology.org/2024.propor-2.8). In Proceedings of the 16th International Conference on Computational Processing of Portuguese - Vol. 2, pages 37–54, Santiago de Compostela, Galicia/Spain. Association for Computational Lingustics.

Leonel Figueiredo de Alencar. 2024. Aspectos da construção de um corpus sintaticamente anotado do nheengatu no modelo Dependências Universais. _Texto Livre_. 17, (ago. 2024), e52653. DOI:https://doi.org/10.1590/1983-3652.2024.52653.

Leonel Figueiredo de Alencar. 2023. [Yauti: A Tool for Morphosyntactic Analysis of Nheengatu within the Universal Dependencies Framework](https://doi.org/10.5753/stil.2023.234131). In *Anais do XIV Simpósio Brasileiro de Tecnologia da Informação e da Linguagem Humana*, setembro 25, 2023, Belo Horizonte/MG, Brasil. SBC, Porto Alegre, Brasil, 135-145. DOI: https://doi.org/10.5753/stil.2023.234131.

## APA reference format:
de Alencar, L. F. (2024). A Universal Dependencies Treebank for Nheengatu. In P. Gamallo, D. Claro, A. J. S. Teixeira, L. Real, M. García, H. G. Oliveira, & R. Amaro (Eds.), _Proceedings of the 16th International Conference on Computational Processing of Portuguese, PROPOR 2024, Santiago de Compostela, Galicia/Spain, 12-15 March, 2024_ (Vol. 2, pp. 37-54). Association for Computational Linguistics. https://aclanthology.org/2024.propor-2.8

de Alencar, L. F. (2024). Aspectos da construção de um corpus sintaticamente anotado do nheengatu no modelo Dependências Universais. _Texto Livre_, 17, e52653. https://doi.org/10.1590/1983-3652.2024.52653

de Alencar, L. F. (2023). Yauti: A Tool for Morphosyntactic Analysis of Nheengatu within the Universal Dependencies Framework. In _Anais do XIV Simpósio Brasileiro de Tecnologia da Informação e da Linguagem Humana_, (pp. 135-145). Porto Alegre: SBC. doi:10.5753/stil.2023.234131

## ABNT reference format:

ALENCAR, Leonel Figueiredo de. A Universal Dependencies Treebank for Nheengatu. In: GAMALLO, Pablo; CLARO, Daniela; TEIXEIRA, António J. S.; REAL, Livy; GARCÍA, Marcos; OLIVEIRA, Hugo Gonçalo; AMARO, Raquel (Eds.). *Proceedings of the 16th International Conference on Computational Processing of Portuguese, PROPOR 2024, Santiago de Compostela, Galicia/Spain, 12-15 March, 2024.* Stroudsburg, PA, USA: Association for Computational Linguistics, 2024. v. 2, p. 37-54. Available at: https://aclanthology.org/2024.propor-2.8.

ALENCAR, Leonel Figueiredo de. Aspectos da construção de um corpus sintaticamente anotado do nheengatu no modelo Dependências Universais. *Texto Livre*, Belo Horizonte-MG, v. 17, p. e52653, 2024. DOI: 10.1590/1983-3652.2024.52653. Disponível em: https://periodicos.ufmg.br/index.php/textolivre/article/view/52653. Acesso em: 22 ago. 2024.

ALENCAR, Leonel Figueiredo de. Yauti: A Tool for Morphosyntactic Analysis of Nheengatu within the Universal Dependencies Framework. In: SIMPÓSIO BRASILEIRO DE TECNOLOGIA DA INFORMAÇÃO E DA LINGUAGEM HUMANA (STIL), 14., 2023, Belo Horizonte/MG. **Anais** [...]. Porto Alegre: Sociedade Brasileira de Computação, 2023. p. 135-145. DOI: https://doi.org/10.5753/stil.2023.234131.

## BibTex reference format:

```bibtex
@inproceedings{DeAlencar2024a,
  author = "de Alencar, Leonel Figueiredo",
  editor  = {Pablo Gamallo and
            Daniela Claro and
            Ant{\'{o}}nio J. S. Teixeira and
            Livy Real and
            Marcos Garc{\'{\i}}a and
            Hugo Gon{\c{c}}alo Oliveira and
            Raquel Amaro},
  title = "A {U}niversal {D}ependencies Treebank for {N}heengatu",
  booktitle = {Proceedings of the 16th International Conference on Computational Processing of Portuguese, {PROPOR} 2024, Santiago de Compostela, Galicia/Spain, 12-15 March, 2024},
  pages = "37--54",
  volume = {2},
  publisher = {Association for Computational Linguistics},
  year = {2024},
  month = {3},
  url = "https://aclanthology.org/2024.propor-2.8",
  address = {Stroudsburg, PA, USA},
  abstract="We present UD_Nheengatu-CompLin, the inaugural treebank for Nheengatu, an endangered Indigenous language of Brazil with limited digital resources. This treebank stands as the largest among Indigenous American languages in version 2.13 of the Universal Dependencies collection. The developmental version comprises 1,336 trees, encompassing 13,246 tokens and 13,374 words. In a 10-fold cross-validation experiment using UDPipe 1.2, parsing with gold tokenization and gold tags achieved a labeled attachment score (LAS) of 81.17 ± 1.02, outperforming Yauti, the rule-based analyzer employed for sentence annotation.",
  isbn = {979-8-89176-062-2,
  doi = "10.5281/zenodo.11372209"}
}
```

```bibtext
@article{DeAlencar2024b,
  journal={Texto Livre},
  author={Alencar, Leonel Figueiredo de},
  place={Belo Horizonte-MG},
  title={Aspectos da construção de um corpus sintaticamente anotado do nheengatu no modelo Dependências Universais},
  volume={17},
  url={https://periodicos.ufmg.br/index.php/textolivre/article/view/52653},
  DOI={10.1590/1983-3652.2024.52653},
  abstract={The alienation of natural language technologies adds up to the weakening of minority languages coexisting with majority languages. Especially younger speakers, who function as links in language transmission, tend to migrate to the language favored by these resources. Nheengatu, an endangered Brazilian indigenous language, has a digital support score of just 0.07 on the Digital Language Support (DLS) scale. This is significantly lower than the 0.97 score for Portuguese, to which Nheengatu has been continually losing speakers. The Nheengatu treebank of the Universal Dependencies collection aims to reduce this deficit by feeding the training of a neural parser. Initially released on 11/15/2023 with 196 sentences and 2,146 words, the latest version, as of 05/15/2024, comprises 1,470 sentences and 15,036 words from twenty publications spanning different historical phases of Nheengatu. This makes it the largest treebank for an Amerindian language in the collection. The use of an automatic analyzer facilitated the rapid expansion of the corpus, while human annotators reviewed each annotation to ensure a 100% validation rate, achieving a two-star rating, the highest for Amerindian language treebanks in the Universal Dependencies collection. The ongoing expansion and revision aim to include all public domain texts and achieve state-of-the-art parsing results.},
  year={2024},
  month={8},
  pages={e52653}
}
```

```bibtex
@inproceedings{DeAlencar2023,
 author = {Leonel Figueiredo de Alencar},
 title = {Yauti: A Tool for Morphosyntactic Analysis of Nheengatu within the Universal Dependencies Framework},
 booktitle = {Anais do XIV Simpósio Brasileiro de Tecnologia da Informação e da Linguagem Humana},
 location = {Belo Horizonte/MG},
 year = {2023},
 pages = {135--145},
 publisher = {SBC},
 address = {Porto Alegre, RS, Brasil},
 doi = {10.5753/stil.2023.234131},
 url = {https://sol.sbc.org.br/index.php/stil/article/view/25445}
}

```

# Acknowledgments

We thank Eduardo de Almeida Navarro (University of São Paulo) for kindly allowing us to use examples and texts from his coursebook (Navarro 2016), whose glossary was the first basis for the morphological analyzer we implemented to annotate the UD_Nheengatu-CompLin treebank.

We owe much to Avila (2021)'s dictionary, from which numerous treebank sentences stem. This dictionary also provided invaluable lexical, grammatical, and semantic information for the further development of the morphological analyzer and related treebank annotation tools. We are much obliged to its author, Marcel Twardowsky Avila, for making the XML version of the dictionary available to us and clarifying many questions about the dictionary entries.

We gratefully acknowledge the scholarships provided to annotators by both the São Paulo State Research Support Foundation (FAPESP) through the [DACILAT](https://bv.fapesp.br/57063) project under Process No. 22/09158-5 and the Foundation for the Support and Development of Research in the State of Ceará (FUNCAP).

We are indebted to Gabriela Lourenço Fernandes and Susan Gabriela Huallpa Huanacuni, internees of the [Biblioteca Brasiliana Guita e José Mindlin](https://www.bbm.usp.br/pt-br/) of the University of São Paulo (USP), as well as to its research specialist and curator João Marcos Cardoso, for transcriptions of stories from Amorim (1928) and Rodrigues (1890).

Thanks are also due to the Federal University of Amazonas Press (*Editora da Universidade Federal do Amazonas* — UFAM), particularly to its director, Sérgio Freire, for granting permission to incorporate texts from Casasnovas (2006) into the treebank.

## License

Copyright of the treebank sentences and their translations belongs to their respective authors. This data is made available here solely to promote research, teaching, and learning of the Nheengatu language. Therefore, it shouldn't be used for any commercial purposes. For more information, see LICENSE.txt.

## References

* Aguiar, Costa. (1898). *Doutrina christã destinada aos naturaes do amazonas em nhihingatu' com traducção portugueza em face*. Pap. e Tip. Pacheco, Silva & C.
* Avila, Marcel Twardowsky.(2021). *Proposta de dicionário nheengatu-português* [Doctoral dissertation, University of São Paulo]. doi:10.11606/T.8.2021.tde-10012022-201925
* Casasnovas, Afonso. (2016). *Noções de língua geral ou nheengatú: Gramática, lendas e vocabulário* (2nd ed.). Editora da Universidade Federal do Amazonas; Faculdade Salesiana Dom Bosco.
* Comunidade de Terra Preta. (2013). *Fábulas de Terra Preta: Uma coletânea bilingüe*.
* Costa, D. Frederico. (1909). *Carta pastoral de D. Frederico Costa bispo do Amazonas a seus amados diocesanos*. Typ. Minerva.
* Cruz, Aline da. (2011). *Fonologia e gramática do nheengatú: A língua falada pelos povos Baré, Warekena e Baniwa*. Netherlands National Graduate School of Linguistics.
* de Alencar, Leonel Figueiredo. (2021). Uma gramática computacional de um fragmento do nheengatu / A computational grammar for a fragment of Nheengatu. _Revista de Estudos da Linguagem, 29_(3), 1717-1777. doi:http://dx.doi.org/10.17851/2237-2083.29.3.1717-1777
* de Amorim, Antonio Brandão. (1928). Lendas em nheêngatú e em portuguez. *Revista do Instituto Historico e Geographico Brasileiro, 154*(100), 9-475.
* de Magalhães, J. V. C. (1876). *O selvagem*. Typographia da Reforma.
* Maslova, Irina. (2018). *Tradução Comentada de Mitos e Lendas Amazônicas do Nheengatu para o Russo*. [Master's thesis, University of São Paulo]. doi:10.11606/D.8.2019.tde-22022019-175350
* Melgueiro, Edilson Martins. (2022). *O Nheengatu de Stradelli aos dias atuais: uma contribuição aos estudos lexicais de línguas Tupí-Guaraní em perspectiva diacrônica*. [Doctoral dissertation, University of Brasília]. http://repositorio2.unb.br/jspui/handle/10482/44655
* Moore, Denny, Facundes, Sidney, & Pires, Nádia. (1994). *Nheengatu (Língua Geral Amazônica), its History, and the Effects of Language Contact*. UC Berkeley: Department of Linguistics. Retrieved from https://escholarship.org/uc/item/7tb981s1
* Muller, Jean-Claude, Dietrich, Wolf, Monserrat, Ruth, Barros, Cândida, Arenz, Karl-Heinz, & Prudente, Gabriel. (Eds.). (2019). *Dicionário De Língua Geral Amazônica*. Universitätsverlag Potsdam; Museu Paraense Emilio Goeldi.
* Navarro, Eduardo de Almeida. (2016). *Curso de Língua Geral (nheengatu ou tupi moderno): A língua das origens da civilização amazônica* (2nd ed.). Centro Angel Rama da Faculdade de Filosofia, Letras e Ciências Humanas da Universidade de São Paulo.
* *Novo Testamento na língua Nyengatu* (2nd ed.). (2019). Missão Novas Tribos do Brasil. (Original work published 1973)
* Rodrigues, João Barbosa. (1890).  *Poranduba amazonense ou kochiyma-uara porandub, 1872-1887.* Typ. de G. Leuzinger & Filhos.
* Seixas, Manoel Justiniano de. (1853). *Vocabulario da lingua indigena geral para o uso do Seminario Episcopal do Pará*. Typ. de Mattos e Compª.
* Stradelli, Ermanno. (2014). *Vocabulário português-nheengatu, nheengatu-português*. Ateliê Editorial.(Original work published 1929)
Here is the BibTeX entry formatted according to APA style:
* Studart, Jorge. (1926). Ligeiras noções de língua geral. *Revista do Instituto do Ceará, 40*, 26–38.
* Sympson, Pedro Luiz. *Grammatica da lingua brazilica geral, fallada pelos aborigines das provincias do Pará e Amazonas*. Typographia do Commercio do Amazonas, 1877.

# Changelog

* 2022-11-15 v2.11
  * Initial release in Universal Dependencies.


<pre>
=== Machine-readable metadata (DO NOT REMOVE!) ================================
Data available since: UD v2.11
License: CC BY-NC-SA 4.0
Includes text: yes
Genre: spoken bible fiction nonfiction grammar-examples
Lemmas: manual native
UPOS: manual native
XPOS: manual native
Features: manual native
Relations: manual native
Contributors: de Alencar, Leonel Figueiredo
Contributing: elsewhere
Contact: leonel.de.alencar@ufc.br
===============================================================================
</pre>
