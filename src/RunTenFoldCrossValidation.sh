#!/bin/bash
# Author: Leonel Figueiredo de Alencar
# Last update: January 26, 2026

# Check for correct number of arguments (expecting 1 argument)
if [ "$#" -ne 1 ]; then
  echo "Usage: $0 <treebank_file>"
  exit 1
fi

echo "Creating 'log.txt' file."
touch log.txt
echo "File 'log.txt' written to disk."
echo "Split $1 treebank file in ten folds, each fold consisting of a test and a train set." >> log.txt
TestSuite.py $1

echo "Create 10 different models, one for each fold. This may take up several hours." >> log.txt
CreateModels.sh

echo "Parse and test 10 times using each time a different model and test file." >> log.txt
TenFoldCrossVal.sh

echo "Process the results of parsing with gold tokenization and gold tags." >> log.txt
ParseGoldTokResults.py > gold-tok-tags-results.txt
echo "File 'gold-tok-tags-results.txt' written to disk."
