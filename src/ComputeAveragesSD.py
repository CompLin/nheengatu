#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Author: Leonel Figueiredo de Alencar
# Last update: February 5, 2026

import numpy as np


def compute_averages(data_list):

    # Initialize dictionaries to store cumulative values for averaging
    tokenizer_tokens_sum = {"f1": []}
    tokenizer_multiword_sum = {"f1": []}
    tokenizer_words_sum = {"f1": []}
    tokenizer_sentences_sum = {"f1": []}
    tagging_sum = {
        "upostag": [],
        "xpostag": [],
        "feats": [],
        "alltags": [],
        "lemmas": [],
    }
    parsing_sum = {"UAS": [], "LAS": []}

    # Iterate over each dictionary in the list
    for data_dict in data_list:
        # Accumulate values for 'Tokenizer words'
        tokenizer_tokens_sum["f1"].append(float(data_dict["Tokenizer tokens"]["f1"]))

        tokenizer_multiword_sum["f1"].append(
            float(data_dict["Tokenizer multiword tokens"]["f1"])
        )

        tokenizer_words_sum["f1"].append(float(data_dict["Tokenizer words"]["f1"]))

        # Accumulate values for 'Tokenizer sentences'
        tokenizer_sentences_sum["f1"].append(
            float(data_dict["Tokenizer sentences"]["f1"])
        )

        # Accumulate values for 'Tagging'
        tagging_sum["upostag"].append(float(data_dict["Tagging"]["upostag"]))
        tagging_sum["xpostag"].append(float(data_dict["Tagging"]["xpostag"]))
        tagging_sum["feats"].append(float(data_dict["Tagging"]["feats"]))
        tagging_sum["alltags"].append(float(data_dict["Tagging"]["alltags"]))
        tagging_sum["lemmas"].append(float(data_dict["Tagging"]["lemmas"]))

        # Accumulate values for 'Parsing'
        parsing_sum["UAS"].append(float(data_dict["Parsing"]["UAS"]))
        parsing_sum["LAS"].append(float(data_dict["Parsing"]["LAS"]))

    # Calculate averages

    # Calculate the mean (average)
    # mean_accuracy = np.mean(data_points)

    # Calculate the standard deviation
    # std_deviation_accuracy = np.std(data_points, ddof=1)  # Sample standard deviation

    num_datasets = len(data_list)

    tokenizer_tokens_avg = np.mean(tokenizer_tokens_sum["f1"])

    tokenizer_tokens_std = np.std(tokenizer_tokens_sum["f1"], ddof=1)

    tokenizer_multiword_avg = np.mean(tokenizer_multiword_sum["f1"])

    tokenizer_multiword_std = np.std(tokenizer_multiword_sum["f1"], ddof=1)
    tokenizer_words_avg = np.mean(tokenizer_words_sum["f1"])

    tokenizer_words_std = np.std(tokenizer_words_sum["f1"], ddof=1)

    tokenizer_sentences_avg = np.mean(tokenizer_sentences_sum["f1"])

    tokenizer_sentences_std = np.std(tokenizer_sentences_sum["f1"], ddof=1)

    tagging_avg = {key: np.mean(value) for key, value in tagging_sum.items()}
    tagging_std = {key: np.std(value, ddof=1) for key, value in tagging_sum.items()}
    parsing_avg = {key: np.mean(value) for key, value in parsing_sum.items()}
    parsing_std = {key: np.std(value, ddof=1) for key, value in parsing_sum.items()}

    # Construct the final dictionary
    averages_dict = {
        "Parsing sum": parsing_sum,
        "Parsing average": parsing_avg,
        "Parsing std": parsing_std,
        "Tokenizer tokens sum": tokenizer_tokens_sum,
        "Tokenizer tokens average f1": tokenizer_tokens_avg,
        "Tokenizer tokens std": tokenizer_tokens_std,
        "Tokenizer multiword sum": tokenizer_multiword_sum,
        "Tokenizer multiword tokens average f1": tokenizer_multiword_avg,
        "Tokenizer multiword tokens std": tokenizer_multiword_std,
        "Tokenizer words sum": tokenizer_words_sum,
        "Tokenizer words average f1": tokenizer_words_avg,
        "Tokenizer words std": tokenizer_words_std,
        "Tokenizer sentences sum": tokenizer_sentences_sum,
        "Tokenizer sentences average f1": tokenizer_sentences_avg,
        "Tokenizer sentences std": tokenizer_sentences_std,
        "Tagging sum": tagging_sum,
        "Tagging average f1": tagging_avg,
        "Tagging std": tagging_std,
    }

    # Print the final dictionary
    print(averages_dict)

    return averages_dict
