#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Author: Leonel Figueiredo de Alencar
# Last update: January 28, 2026

# TODO: see tasks list in ParseResults.py

import numpy as np

def my_compute_averages(results,task=0,subtask='f1'):
	tasks=['Tokenizer words','Tokenizer sentences','Tagging','Parsing']
	values=[]
	for r in results:
		d=r.get(tasks[task])
		v=d.get(subtask)
		values.append(float(v))
	print(sum(values)/len(values))

data_list = [{'Tokenizer words': {'system': '75', 'gold': '78', 'precision': '96.00', 'recall': '92.31', 'f1': '94.12'}, 'Tokenizer sentences': {'system': '11', 'gold': '13', 'precision': '81.82', 'recall': '69.23', 'f1': '75.00'}, 'Tagging': {'gold forms': '78', 'upostag': '84.97', 'xpostag': '84.97', 'feats': '81.05', 'alltags': '81.05', 'lemmas': '84.97'}, 'Parsing': {'gold forms': '78', 'UAS': '67.97', 'LAS': '60.13'}}, {'Tokenizer words': {'system': '62', 'gold': '65', 'precision': '95.16', 'recall': '90.77', 'f1': '92.91'}, 'Tokenizer sentences': {'system': '11', 'gold': '13', 'precision': '81.82', 'recall': '69.23', 'f1': '75.00'}, 'Tagging': {'gold forms': '65', 'upostag': '77.17', 'xpostag': '75.59', 'feats': '70.87', 'alltags': '69.29', 'lemmas': '85.04'}, 'Parsing': {'gold forms': '65', 'UAS': '50.39', 'LAS': '45.67'}}, {'Tokenizer words': {'system': '74', 'gold': '74', 'precision': '100.00', 'recall': '100.00', 'f1': '100.00'}, 'Tokenizer sentences': {'system': '12', 'gold': '12', 'precision': '100.00', 'recall': '100.00', 'f1': '100.00'}, 'Tagging': {'gold forms': '74', 'upostag': '90.54', 'xpostag': '83.78', 'feats': '82.43', 'alltags': '79.73', 'lemmas': '94.59'}, 'Parsing': {'gold forms': '74', 'UAS': '77.03', 'LAS': '70.27'}}, {'Tokenizer words': {'system': '84', 'gold': '86', 'precision': '98.81', 'recall': '96.51', 'f1': '97.65'}, 'Tokenizer sentences': {'system': '12', 'gold': '13', 'precision': '91.67', 'recall': '84.62', 'f1': '88.00'}, 'Tagging': {'gold forms': '86', 'upostag': '88.24', 'xpostag': '84.71', 'feats': '80.00', 'alltags': '78.82', 'lemmas': '92.94'}, 'Parsing': {'gold forms': '86', 'UAS': '54.12', 'LAS': '43.53'}}]

def compute_averages(data_list):

	# Initialize dictionaries to store cumulative values for averaging
	tokenizer_tokens_sum = {'f1': []}
	tokenizer_multiword_sum = {'f1': []}
	tokenizer_words_sum = {'f1': []}
	tokenizer_sentences_sum = {'f1': []}
	tagging_sum = {'upostag': [], 'xpostag': [], 'feats': [], 'lemmas': []}
	parsing_sum = {'UAS': [], 'LAS': []}

	# Iterate over each dictionary in the list
	for data_dict in data_list:
		# Accumulate values for 'Tokenizer words'
		tokenizer_tokens_sum['f1'].append(float(data_dict['Tokenizer tokens']['f1']))

		tokenizer_multiword_sum['f1'].append(float(data_dict['Tokenizer multiword tokens']['f1']))

		tokenizer_words_sum['f1'].append(float(data_dict['Tokenizer words']['f1']))

		# Accumulate values for 'Tokenizer sentences'
		tokenizer_sentences_sum['f1'].append(float(data_dict['Tokenizer sentences']['f1']))

		# Accumulate values for 'Tagging'
		tagging_sum['upostag'].append(float(data_dict['Tagging']['upostag']))
		tagging_sum['xpostag'].append(float(data_dict['Tagging']['xpostag']))
		tagging_sum['feats'].append(float(data_dict['Tagging']['feats']))
		tagging_sum['lemmas'].append(float(data_dict['Tagging']['lemmas']))

		# Accumulate values for 'Parsing'
		parsing_sum['UAS'].append(float(data_dict['Parsing']['UAS']))
		parsing_sum['LAS'].append(float(data_dict['Parsing']['LAS']))
		
	print(f"parsing_sum['UAS']{parsing_sum['UAS']}")
		
	print(f"parsing_sum['LAS']{parsing_sum['LAS']}")

	# Calculate averages

	# Calculate the mean (average)
	#mean_accuracy = np.mean(data_points)

	# Calculate the standard deviation
	#std_deviation_accuracy = np.std(data_points, ddof=1)  # Sample standard deviation

	num_datasets = len(data_list)

	tokenizer_tokens_avg = np.mean(tokenizer_tokens_sum['f1'])

	tokenizer_tokens_std = np.std(tokenizer_tokens_sum['f1'], ddof=1)

	tokenizer_multiword_avg = np.mean(tokenizer_multiword_sum['f1'])
	
	tokenizer_multiword_std = np.std(tokenizer_multiword_sum['f1'], ddof=1)
	tokenizer_words_avg = np.mean(tokenizer_words_sum['f1'])

	tokenizer_words_std = np.std(tokenizer_words_sum['f1'], ddof=1)

	tokenizer_sentences_avg = np.mean(tokenizer_sentences_sum['f1'])
	
	tokenizer_sentences_std = np.std(tokenizer_sentences_sum['f1'], ddof=1)
	
	tagging_avg = {key: np.mean(value) for key, value in tagging_sum.items()}
	tagging_std = {key: np.std(value, ddof=1) for key, value in tagging_sum.items()}
	parsing_avg = {key: np.mean(value) for key, value in parsing_sum.items()}
	parsing_std = {key: np.std(value, ddof=1) for key, value in parsing_sum.items()}

	# Construct the final dictionary
	averages_dict = {
		'Tokenizer tokens': {'f1': tokenizer_tokens_avg},
		'Tokenizer tokens std': {'f1_std': tokenizer_tokens_std},
		'Tokenizer multiword tokens': {'f1': tokenizer_multiword_avg},
		'Tokenizer multiword tokens std': {'f1_std': tokenizer_multiword_std},
		'Tokenizer words': {'f1': tokenizer_words_avg},
		'Tokenizer words std': {'f1_std': tokenizer_words_std},
		'Tokenizer sentences': {'f1': tokenizer_sentences_avg},
		'Tokenizer sentences std': {'f1_std': tokenizer_sentences_std},
		'Tagging': tagging_avg,
		'Parsing': parsing_avg
	}

	# Print the final dictionary
	print(averages_dict)
	print(f"\ntagging_std: {tagging_std}")
	print(f"\nparsing_std: {parsing_std}")
