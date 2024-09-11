#!/bin/bash
# Author: Leonel Figueiredo de Alencar
# Last update: September 10, 2024

echo "Split $1 treebank file in ten folds." > log.txt
TestSuite.py $1

echo "Create 10 different models. This may take up several hours." >> log.txt
CreateModels.sh

echo "Parse and test 10 times using each time a different model and test file." >> log.txt
TenFoldCrossVal.sh

echo "Process the results of parsing with gold tokenization and gold tags." >> log.txt
ParseGoldTokResults.py > results.txt

