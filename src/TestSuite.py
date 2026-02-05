#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Author: Leonel Figueiredo de Alencar
# Last update: February 4, 2026

import sys
import numpy as np
from Yauti import extractConlluSents, writeSentsConllu
from conllu import TokenList
from sklearn.model_selection import KFold


def divide_treebank(treebank_data):
	# Calculate the size of each part
	part_size = len(treebank_data) // 10

	# Divide the treebank into 10 parts
	treebank_parts = [treebank_data[i * part_size:(i + 1) * part_size] for i in range(10)]

	return treebank_parts

		
def mkTestTrain(dataset):
	dataset = np.array(dataset, dtype=object)
	kf = KFold(n_splits=10, shuffle=True, random_state=42)
	i=1
	for train_index, test_index in kf.split(dataset):
		# Split data into train and test sets
		train_data, test_data = dataset[train_index], dataset[test_index]
		writeSentsConllu(test_data,f"test-{i}.conllu")
		writeSentsConllu(train_data,f"train-{i}.conllu")
		i+=1
			

def main():
    # Check if a filename is provided as a command line argument
    if len(sys.argv) != 2:
        print("Usage: python TestSuite.py <treebank_filename>")
        sys.exit(1)

    # Read treebank data from the file
    treebank_filename = sys.argv[1]
    treebank_data = extractConlluSents(treebank_filename)
    
    # write test and train files
    mkTestTrain(treebank_data)

if __name__ == "__main__":
    main()
