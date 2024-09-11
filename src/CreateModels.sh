#!/bin/bash

# Iterate over file pairs
for i in {1..10}; do
    train_file="train-${i}.conllu"
    model="model-${i}.output"

    # Execute your command on each pair
    udpipe --train ${model} ${train_file}

done
