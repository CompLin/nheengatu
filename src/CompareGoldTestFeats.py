#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Author: Leonel Figueiredo de Alencar
# Last update: August 25, 2025

import json
import argparse
from Yauti import extractConlluSents, mkConlluSentence, TREEBANK_PATH, tokenize, splitMultiWordTokens, process_token
from collections import Counter


def mkGold(sents):
    return [sent for sent in sents if "/=" in (sent.metadata.get("inputline") or "")]


def getTokensWithSpecialTags(tokens):
    result = []
    i = 0
    while i < len(tokens):
        if "/=" in tokens[i]:
            result.append((i + 1, tokens[i]))
        i += 1
    return result


def extractFeatures(sent_id, gold_token, test_token):
    feats = []
    for token in gold_token, test_token:
        newfeats = {}
        token_feats = token.get('feats')
        if token_feats:
            newfeats = token_feats.copy()
        token_misc = token.get('misc')
        if token_misc:
            for k, v in token_misc.items():
                if k != 'TokenRange':
                    newfeats[k] = v
        feats.append(newfeats)
    return {sent_id: feats}


def extractTags(tokenlists):
    tags = []
    for tk in tokenlists:
        inputline = tk.metadata.get('inputline')
        tokens = splitMultiWordTokens(tokenize(inputline))
        for token in tokens:
            token_data = process_token(token)
            parsed = token_data.get('parsed')
            if parsed:
                func = parsed.get('func')
                if func:
                    tags.append(token_data['raw_tag'])
    return tags


def extractFeatureFreqDist(data, feat):
    results = []
    for dic in data:
        for sent_id, diclist in dic.items():
            gold = diclist[0]
            test = diclist[1]
            goldfeat = gold.get(feat)
            testfeat = test.get(feat)
            if goldfeat or testfeat:
                results.append((goldfeat, testfeat))
    return Counter(results).most_common()


def mkTestSet(treebank=TREEBANK_PATH):
    sents = extractConlluSents(*treebank)
    tokenlists = mkGold(sents)
    test = []
    for tk in tokenlists:
        inputline = tk.metadata.get('inputline')
        sent_id = tk.metadata.get('sent_id')
        tokens = splitMultiWordTokens(tokenize(inputline))
        newtk = mkConlluSentence(tokens)
        len_tk = len(tk)
        len_newtk = len(newtk)
        if len_tk == len_newtk:
            tokens_with_special_tags = getTokensWithSpecialTags(tokens)
            for token_id, token in tokens_with_special_tags:
                sent_id_token_id = f"{sent_id}@{token_id}"
                gold_token = tk.filter(id=token_id)[0]
                test_token = newtk.filter(id=token_id)[0]
                test.append(extractFeatures(sent_id_token_id, gold_token, test_token))
        else:
            print(sent_id, len_tk, len_newtk)
    return test


def save_to_json(data, filename='features.json'):
    """
    Saves a Python data structure to a JSON file.
    """
    try:
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=4)
        print(f"Data successfully saved to {filename}")
    except Exception as e:
        print(f"Error saving to {filename}: {e}")


def main():
    parser = argparse.ArgumentParser(
        description="Generate a test set of features and save to JSON."
    )
    parser.add_argument(
        "-t", "--treebank", nargs="+",
        help="Input CoNLL-U files. If omitted, defaults to TREEBANK_PATH."
    )
    parser.add_argument(
        "-o", "--output", required=True,
        help="Output JSON file name."
    )
    args = parser.parse_args()

    if args.treebank:
        print(f"Processing treebank files: {args.treebank}")
        testset = mkTestSet(treebank=args.treebank)
    else:
        print(f"No -t specified. Using default TREEBANK_PATH: {TREEBANK_PATH}")
        testset = mkTestSet()

    save_to_json(testset, args.output)


if __name__ == "__main__":
    main()
