#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Author: Leonel Figueiredo de Alencar
# Last update: January 26, 2026

import re, sys

from ComputeAveragesSD import compute_averages as cs

# Read the content of the file
infile='/home/leonel/nheengatu/compostela/test3/results-1b.txt'

def parse_line(line):
    # Define a regex pattern to extract key-value pairs
    pattern = re.compile(r'(?P<key>[\w\s]+):\s*(?P<value>[\d.]+)')

    # Use re.finditer to find all key-value pairs in the line
    matches = re.finditer(pattern, line)

    # Store the key-value pairs in a dictionary
    data = {match.group('key').strip(): match.group('value').strip() for match in matches}

    return data

def parseFile(infile):
	results=[]
	tasks=['Tokenizer tokens','Tokenizer multiword tokens','Tokenizer words','Tokenizer sentences','Tagging','Parsing']
	# Read the content of the file
	with open(infile, 'r') as file:
		file_content = file.read()

	# Split the content into lines and process each line
	lines = file_content.split('\n')
	for line in lines:
		# Skip irrelevant lines
		if not line.startswith("Tokenizer") and not line.startswith("Tagging") and not line.startswith("Parsing"):
			continue

		# Parse the line and print the result
		parsed_data = parse_line(line)
		results.append(parsed_data)
	return dict(zip(tasks,results))

def main():
	# Check if one or more filenames are provided as a command line argument
	if len(sys.argv) < 2:
		print("Usage: python script.py <treebank_filename>")
		sys.exit(1)
	results=[]
	for f in sys.argv[1:]:
		results.append(parseFile(f))
	#compute_averages(results)
	cs(results)

if __name__ == "__main__":
	main()
