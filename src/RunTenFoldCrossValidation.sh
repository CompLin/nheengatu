#!/bin/bash
# Author: Leonel Figueiredo de Alencar
# Last update: September 10, 2024

# split treebank file in ten folds
TestSuite.py sample.conllu

# create 10 different models (this may take up several hours)
CreateModels.sh

# Parse and test 10 times using each time a different model and test file
TenFoldCrossVal.sh

# Process the results of parsing with gold tokenization and gold tags
ParseGoldTokResults.py

