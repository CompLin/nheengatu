The contents of the `glossary.txt` file of this folder were first copied and pasted as raw text from the glossary on pages 103-111 of the following book:

Navarro, Eduardo de Almeida. (2016). *Curso de Língua Geral (nheengatu ou tupi moderno): a língua das origens da civilização amazônica* (2nd ed.). Centro Angel Rama da Faculdade de Filosofia, Letras e Ciências Humanas da Universidade de São Paulo.

Copyright of this book belongs to its author, Professor Eduardo de Almeida Navarro of the University of São Paulo. The version of the glossary in this repository is made available here solely to promote research, teaching, and learning of the Nheengatu language. Therefore, this material and all derived data shouldn't be used for any commercial purposes.

Minor formatting and orthographic inconsistencies in the glossary were corrected. Besides, some entries were changed to make the lexical information more explicit for computational processing. All changes can be tracked with the help of the commit history. Most of the changes, if not all, have been documented in the issues.   

We also acknowledge the use of Avila (2021)'s dictionary, which provided invaluable lexical, grammatical, and semantic information for the construction of the morphological analyzer and related treebank annotation tools:

Avila, Marcel Twardowsky.(2021). *Proposta de dicionário nheengatu-português* [Doctoral dissertation, University of São Paulo]. doi:[10.11606/T.8.2021.tde-10012022-201925](https://doi.org/10.11606/T.8.2021.tde-10012022-201925).

Dozens of new entries of the glossary or corrections on existing entries were based on this work. These additions, however, represent simplifications of the original entries. The scope and format of the glossary entries are tailored to the automatic annotation tools, meaning explanations often limit themselves to the readings manifest in the corpus examples. Therefore, usage of the glossary in other contexts, e.g., translation or language learning and teaching, should be done with caution. The use of Avila's dictionary should be preferred in these situations.      

The glossary feeds a couple of bash and Python scripts to extract the relevant information for the computational processing of Nheengatu, mostly for tagging and lemmatization. The extracted lexical information is encoded in different data structures stored in the other files of this folder.

If you detect any errors in the data, please submit an issue.
