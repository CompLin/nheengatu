#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Author: Leonel Figueiredo de Alencar
# Last update: August 24, 2025

import json
from Yauti import extractConlluSents, mkConlluSentence, TREEBANK_PATH, tokenize, splitMultiWordTokens, process_token
from collections import Counter

def mkGold(sents):
    return [sent for sent in sents if "/=" in (sent.metadata.get("inputline") or "")]

data=[
	{'Avila2021:0:0:27': [
		{'Number': 'Plur', 'Person': '2', 'VerbForm': 'Vnoun'}, 
		{'Number': 'Plur', 'Person': '2', 'VerbForm': 'Vnoun', 'SpaceAfter': 'No'}]}, 
	{'Avila2021:0:0:76': [
		{'Red': 'Yes'}, {'Red': 'Yes'}]}, 
	{'Avila2021:0:0:275': [
		{'Red': 'Yes'}, {'Red': 'False'}]}, 
	{'Avila2021:0:0:300': [
		{'Derivation': 'Priv'}, 
		{'Derivation': 'Priv', 'SpaceAfter': 'No'}]}, 
	{'Avila2021:0:0:317': [
		{'Mood': 'Ind', 'Person': '3', 'Red': 'Yes', 'VerbForm': 'Fin'}, 
		{'Mood': 'Ind', 'Person': '3', 'Red': 'Yes', 'VerbForm': 'Fin'}]}, 
	{'Avila2021:32:2:375': [
		{'Red': 'Yes', 'SpaceAfter': 'No'}, {'SpaceAfter': 'No'}]}, 
	{'Avila2021:0:0:378': [
		{'Derivation': 'Priv', 'SpaceAfter': 'No'}, {'SpaceAfter': 'No'}]}, 
	{'Avila2021:0:0:726': [
		{'SpaceAfter': 'No'}, {'SpaceAfter': 'No'}]}, 
	{'NTLN2019:1:2:9': [
		{'VerbForm': 'Vnoun'}, {'Person': '3', 'VerbForm': 'Vnoun'}]}, 
	{'NTLN2019:0:0:34': [
		{'Mood': 'Ind', 'Person': '3', 'VerbForm': 'Fin', 'Orig': 'vender', 'OrigLang': 'pt'}, 
		{'VerbForm': 'Fin', 'VerbType': 'Act','Orig': 'vende', 'OrigLang': 'por'}]}]

def getTokensWithSpecialTags(tokens):
	result=[]
	i=0
	while(i<len(tokens)):
		if "/=" in tokens[i]:
			result.append((i+1,tokens[i]))
		i+=1
	return result

def extractFeatures(sent_id,gold_token,test_token):
	feats=[]
	for token in gold_token,test_token:
		newfeats={}
		token_feats=token.get('feats')
		if token_feats:
			newfeats=token_feats.copy()
		token_misc=token.get('misc')
		if token_misc:
			for k,v in token_misc.items():
				if k != 'TokenRange':
					newfeats[k]=v
		feats.append(newfeats)
	return {sent_id : feats}

def extractTags(tokenlists):
	tags=[]
	for tk in tokenlists:
		inputline=tk.metadata.get('inputline')
		tokens=splitMultiWordTokens(tokenize(inputline))
		for token in tokens:
			token_data=process_token(token)
			parsed=token_data.get('parsed')
			if parsed:
				func=parsed.get('func')
				if func:
					tags.append(token_data['raw_tag'])
	return tags

def extractFeatureFreqDist(data,feat):
	results=[]
	for dic in data:
		for sent_id, diclist in dic.items():
			gold=diclist[0]
			test=diclist[1]
			goldfeat=gold.get(feat)
			testfeat=test.get(feat)
			if goldfeat or testfeat:
				results.append((goldfeat,testfeat))
	return Counter(results).most_common()

def mkTestSet(treebank=TREEBANK_PATH):
	sents = extractConlluSents(*treebank)
	tokenlists = mkGold(sents)
	test=[]
	#counts=[]
	for tk in tokenlists:
		inputline=tk.metadata.get('inputline')
		sent_id=tk.metadata.get('sent_id')
		tokens=splitMultiWordTokens(tokenize(inputline))
		newtk=mkConlluSentence(tokens)
		len_tk=len(tk)
		len_newtk=len(newtk)
		if len_tk == len_newtk:
			tokens_with_special_tags=getTokensWithSpecialTags(tokens)
			for token_id,token in tokens_with_special_tags:
				sent_id_token_id=f"{sent_id}@{token_id}"
				gold_token=tk.filter(id=token_id)[0]
				test_token=newtk.filter(id=token_id)[0]
				test.append(extractFeatures(sent_id_token_id,gold_token,test_token))
		else:
			print(sent_id,len_tk,len_newtk)
	return test

def save_to_json(data, filename='features.json'):
    """
    Saves a Python data structure to a JSON file.

    Parameters:
    - data: The Python object (dict, list, etc.) to save.
    - filename: The path to the JSON file where the data should be saved.
    """
    try:
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=4)
        print(f"Data successfully saved to {filename}")
    except Exception as e:
        print(f"Error saving to {filename}: {e}")

def compute_feature_f1(data): # TODO: redundant; see evaluate_features.py
    """
    Compute precision, recall, and F1-score for feature prediction.
    
    Args:
        data (list of dict): Each dict maps a sent_id to a list of two dicts: [gold_feats, test_feats].
        
    Returns:
        tuple: (precision, recall, f1_score) as floats
    """
    true_positives = 0
    false_positives = 0
    false_negatives = 0

    for item in data:
        for sent_id, (gold_feats, test_feats) in item.items():
            gold_items = set(gold_feats.items())
            test_items = set(test_feats.items())

            true_positives += len(gold_items & test_items)
            false_positives += len(test_items - gold_items)
            false_negatives += len(gold_items - test_items)

    precision = true_positives / (true_positives + false_positives) if (true_positives + false_positives) else 0.0
    recall = true_positives / (true_positives + false_negatives) if (true_positives + false_negatives) else 0.0
    f1 = 2 * precision * recall / (precision + recall) if (precision + recall) else 0.0

    return precision, recall, f1

def main():
    # compile feature data
    #testset = mkTestSet()  # This returns a list of {sent_id: [gold, test]} dicts
    # or load feature data
    with open("/home/leonel/Dropbox/publications/2025/STIL/features.edt.json", "r", encoding="utf-8") as f:
        testset = json.load(f)
    precision, recall, f1 = compute_feature_f1(testset)
    print(f"Total tokens: {len(testset)}")
    print(f"Precision: {precision:.3f}")
    print(f"Recall:    {recall:.3f}")
    print(f"F1-score:  {f1:.3f}")

if __name__ == "__main__":
    main()

