#!/bin/bash

# Iterate over file pairs
for i in {1..10}; do
    test_file="test-${i}.conllu"
    model="model-${i}.output"
    results="results-${i}.txt"
    gold="gold-tok-tags-${i}.txt"

    # Execute your command on each pair
    #udpipe --tokenize --tokenizer=ranges --accuracy --tag --parse  ${model} ${test_file} > ${results}
    udpipe --accuracy --parse  ${model} ${test_file} > ${gold}
done
