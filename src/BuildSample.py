#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Author: Leonel Figueiredo de Alencar
# Last update: November 4, 2024
import random

# Your dictionary of sentences with ambiguity counts
sentence_ambiguities = {'MooreFP1994:0:0:6': 1, 'MooreFP1994:0:0:24': 2, 'Alencar2021:0:0:53': 1, 'Navarro2016:0:0:38': 1, 'Navarro2016:0:0:40': 1, 'Navarro2016:0:0:126': 1, 'Navarro2016:0:0:129': 1, 'Navarro2016:0:0:135': 1, 'Navarro2016:0:0:136': 1, 'Navarro2016:0:0:139': 1, 'Navarro2016:0:0:148': 1, 'Avila2021:0:0:27': 5, 'Avila2021:0:0:35': 2, 'Avila2021:0:0:66': 1, 'Avila2021:0:0:102': 1, 'Avila2021:0:0:124': 2, 'Avila2021:0:0:127': 1, 'Avila2021:0:0:134': 2, 'Avila2021:0:0:155': 1, 'Avila2021:0:0:180': 1, 'Avila2021:0:0:183': 1, 'Avila2021:0:0:186': 1, 'Avila2021:0:0:202': 2, 'Avila2021:0:0:273': 1, 'Avila2021:0:0:311': 1, 'Avila2021:28:2:325': 1, 'Avila2021:28:3:326': 1, 'Avila2021:0:0:330': 1, 'Avila2021:0:0:353': 2, 'Avila2021:0:0:368': 1, 'Avila2021:0:0:372': 2, 'Avila2021:0:0:384': 1, 'Avila2021:0:0:387': 2, 'Avila2021:0:0:397': 1, 'Avila2021:0:0:434': 1, 'Avila2021:35:2:438': 1, 'Avila2021:0:0:448': 1, 'Avila2021:37:1:465': 1, 'Avila2021:38:1:472': 1, 'Avila2021:39:1:477': 1, 'Avila2021:0:0:519': 1, 'Avila2021:0:0:531': 1, 'Avila2021:0:0:548': 1, 'Avila2021:0:0:562': 1, 'Avila2021:0:0:568': 1, 'Avila2021:0:0:569': 1, 'Avila2021:0:0:593': 1, 'Avila2021:0:0:594': 1, 'Avila2021:0:0:606': 1, 'Avila2021:0:0:628': 1, 'Avila2021:0:0:642': 1, 'Avila2021:0:0:644': 2, 'Avila2021:0:0:646': 1, 'Avila2021:0:0:652': 1, 'Avila2021:0:0:678': 1, 'Avila2021:0:0:694': 1, 'Avila2021:0:0:718': 1, 'NTLN2019:1:1:8': 3, 'NTLN2019:1:2:9': 1, 'NTLN2019:2:4:15': 1, 'NTLN2019:8:1:47': 2, 'NTLN2019:8:2:48': 1, 'NTLN2019:0:0:49': 2, 'Cruz2011:0:0:19': 2, 'Cruz2011:0:0:43': 1, 'Cruz2011:0:0:50': 1, 'Cruz2011:0:0:73': 1, 'Cruz2011:0:0:82': 1, 'Cruz2011:0:0:101': 1, 'Cruz2011:0:0:114': 2, 'Cruz2011:0:0:116': 2, 'Cruz2011:0:0:117': 1, 'Casasnovas2006:5:10:58': 1, 'Casasnovas2006:6:8:67': 2, 'Casasnovas2006:8:6:74': 1, 'Casasnovas2006:9:3:87': 2, 'Casasnovas2006:10:8:127': 1, 'Casasnovas2006:10:12:131': 1, 'Casasnovas2006:11:19:150': 1, 'Casasnovas2006:11:21:152': 2, 'Casasnovas2006:11:27:158': 2, 'Casasnovas2006:11:34:165': 3, 'Rodrigues1890:1-2-2:120:120': 1, 'Rodrigues1890:2-5:4:104': 1, 'Magalhaes1876:1-1-1:0:71': 2, 'Magalhaes1876:1:6:6': 1, 'Magalhaes1876:1:12:12': 1, 'Magalhaes1876:1:15:15': 1, 'Magalhaes1876:1:21:21': 1, 'Magalhaes1876:1:42:42': 1, 'Magalhaes1876:1:43:43': 1, 'Magalhaes1876:2:5:48': 1, 'Magalhaes1876:2:6:49': 1, 'Magalhaes1876:2:8:51': 1, 'Amorim1928:19:51:51': 1, 'Amorim1928:21:41:41': 1, 'Amorim1928:21:61:61': 1, 'Amorim1928:21:113:113': 1, 'Amorim1928:6:378:378': 1, 'Amorim1928:2:101:5500': 1, 'Amorim1928:2:500:6000': 1, 'Amorim1928:12:50:50': 1, 'Amorim1928:18:25:25': 1, 'Amorim1928:18:26:26': 1, 'Hartt1938:0:0:9': 1, 'Hartt1938:0:0:25': 1, 'Costa1909:0:0:1001': 1, 'Aguiar1898:21-6:7:547': 5, 'Studart1926:0:0:2810': 2, 'Studart1926:0:0:36103': 1}

# Calculate the total number of ambiguities
total_ambiguities = sum(sentence_ambiguities.values())

# Set targets for each sample
target_ambiguities_10 = round(total_ambiguities * 0.1)
target_ambiguities_30 = round(total_ambiguities * 0.3)

# Shuffle sentences
sentences = list(sentence_ambiguities.items())
random.shuffle(sentences)

# Function to generate a sample with a specified target ambiguity count from a list of sentences
def generate_sample(sentences, target_ambiguities):
    sample = []
    cumulative_ambiguities = 0
    remaining_sentences = []

    for sentence_id, ambiguities in sentences:
        if cumulative_ambiguities >= target_ambiguities:
            remaining_sentences.append((sentence_id, ambiguities))
        else:
            sample.append((sentence_id, ambiguities))
            cumulative_ambiguities += ambiguities

    return sample, cumulative_ambiguities, remaining_sentences

# Generate sample_10
sample_10, cumulative_ambiguities_10, remaining_sentences = generate_sample(sentences, target_ambiguities_10)

# Generate sample_30 from remaining sentences
sample_30, cumulative_ambiguities_30, _ = generate_sample(remaining_sentences, target_ambiguities_30)

# Display results
print("Sample 10%:")
for sentence_id, ambiguities in sample_10:
    print(f"Sentence: {sentence_id}, Ambiguities: {ambiguities}")
print(f"\nTotal Ambiguities in Sample 10%: {cumulative_ambiguities_10} (Target: {target_ambiguities_10})\n")

print("Sample 30%:")
for sentence_id, ambiguities in sample_30:
    print(f"Sentence: {sentence_id}, Ambiguities: {ambiguities}")
print(f"\nTotal Ambiguities in Sample 30%: {cumulative_ambiguities_30} (Target: {target_ambiguities_30})")

