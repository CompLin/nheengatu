#!/bin/bash
# --------------------------------------------------------------------
# Script: TenFoldCrossVal.sh
# Author: Leonel Figueiredo de Alencar
# Last update: January 26, 2026
#
# Description:
#     Performs ten-fold cross-validation parsing using pre-trained
#     UDPipe models. For each fold i = 1..10, the script loads:
#         - test-i.conllu       : test set for fold i
#         - model-i.output      : corresponding UDPipe model
#
#     The script can operate in two modes:
#
#     (1) Default mode (no -t):
#         Parses using **gold tokenisation and gold tags**.
#         Output file:
#             gold-tok-tags-results-i.txt
#
#     (2) Tokenize+Tag+Parse mode (-t):
#         Performs tokenisation + tagging + parsing.
#         Output file:
#             raw-text-results-i.txt
#
# Usage:
#     ./TenFoldCrossVal.sh       # parse only (gold tokenisation + gold tags)
#     ./TenFoldCrossVal.sh -t    # tokenize + tag + parse
#
# Option:
#     -t     Enables tokenisation and tagging before parsing.
# --------------------------------------------------------------------

# Parse options
tt_flag=false
while getopts ":t" opt; do
  case ${opt} in
    t )
      tt_flag=true
      ;;
    \? )
      echo "Usage: $0 [-t]"
      exit 1
      ;;
  esac
done

# Display mode information
if [ "$tt_flag" = true ]; then
    echo "Mode: Tokenisation + Tagging + Parsing (UDPipe will ignore gold tokens and gold tags)"
else
    echo "Mode: Parsing with GOLD tokenisation and GOLD tags"
fi
echo "------------------------------------------------------------"

# Loop over the 10 folds
for i in {1..10}; do
    test_file="test-${i}.conllu"
    model="model-${i}.output"

    results="raw-text-results-${i}.txt"
    gold="gold-tok-tags-results-${i}.txt"

    echo "Processing fold ${i}..."
    echo "  Model: ${model}"
    echo "  Test:  ${test_file}"

    if [ "$tt_flag" = true ]; then
        echo "  → Running UDPipe with tokenisation, tagging and parsing"
        echo "  → Output: ${results}"
        udpipe --tokenize --tokenizer=ranges --accuracy --tag --parse \
               "${model}" "${test_file}" > "${results}"
    else
        echo "  → Running UDPipe with gold tokenisation and gold tags"
        echo "  → Output: ${gold}"
        udpipe --accuracy --parse \
               "${model}" "${test_file}" > "${gold}"
    fi

    echo "  ✔ Fold ${i} completed."
    echo "------------------------------------------------------------"
done

echo "All 10 folds processed successfully."
echo "Results are saved in 'raw-text-results-1.txt' to 'raw-text-results-10.txt' (if -t option was used) or 'gold-tok-tags-results-1.txt' to 'gold-tok-tags-results-10.txt' (if no -t option)."