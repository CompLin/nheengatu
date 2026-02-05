#!/bin/bash
# Author: Leonel Figueiredo de Alencar
# Last update: February 4, 2026
# CreateModels.sh
#
# Purpose
#   Train 10 UDPipe models (one per fold) for a 10-fold cross-validation setup.
#
# Context in the pipeline
#   This script is intended to be run AFTER the Python script that creates the
#   fold-specific training files:
#       TestSuite.py  --> writes: train-1.conllu ... train-10.conllu
#   Then this script trains:
#       model-1.output ... model-10.output
#
# Requirements
#   - Bash
#   - UDPipe available on PATH (command: udpipe)
#   - Files train-1.conllu ... train-10.conllu present in the current directory
#
# Output
#   - model-${i}.output for i = 1..10 (UDPipe trained models)
#
# Notes
#   - If any train-*.conllu file is missing, udpipe will fail for that fold.
#   - By default, the script overwrites existing model-*.output files.
#


# Optional safety settings:
#   -e : exit immediately if a command fails (recommended for pipelines)
#   -u : treat unset variables as an error
#   -o pipefail : catch failures in pipelines
set -euo pipefail

# Train one model per fold (1..10).
# Each fold uses the corresponding training file generated earlier.
for i in {1..10}; do
    # Input training data for fold i (produced by TestSuite.py).
    train_file="train-${i}.conllu"

    # Output model file for fold i.
    model="model-${i}.output"

    # Sanity check: fail early with a clear error message if the input is missing.
    if [[ ! -f "$train_file" ]]; then
        echo "ERROR: Missing training file: $train_file" >&2
        echo "Run TestSuite.py first (it should generate train-1.conllu ... train-10.conllu)." >&2
        exit 1
    fi

    # Train the UDPipe model for this fold.
    # Syntax: udpipe --train <model_output_file> <training_conllu_file>
    #
    # This produces a trained model in $model, which can later be used for tagging/parsing.
    udpipe --train "$model" "$train_file"
done
