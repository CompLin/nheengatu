#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Author: Leonel Figueiredo de Alencar
# Last update: August 26, 2025
# License: GNU General Public License v2

"""
CompareGoldTestFeats.py
========================

This script compares **gold-standard** and **automatically predicted**
morphosyntactic feature annotations of **Nheengatu** sentences, following
the guidelines of the **UD_Nheengatu-CompLin** treebank.

It is designed to work with the output of **Yauti**, a rule-based
morphosyntactic analyzer specialized for Nheengatu.
Yauti only performs morphosyntactic analysis of Nheengatu and does not
target other languages.

The script identifies tokens with special tags (marked with "/="),
extracts morphosyntactic features from gold and test analyses, and
produces a JSON file mapping sentence IDs to corresponding feature sets.

Special tags
------------
Tags prefixed with "=" enable Yauti to process words not found in its
lexicon or not handled by the tokenizer.
For example::

    xamanéu/=typo:c|xamunéu

allows Yauti to analyze the word *xamanéu*, which contains a typo,
mapping it to the correct form *xamunéu*. 
Yauti also assigns the token Typo=Yes, CorrectForm=xamanéu, and other features, following UD guidelines.

License
-------
This software is released under the **GNU General Public License v2**.

References
----------
- Leonel Figueiredo de Alencar. 2025.
  *Enhancing a Nheengatu Morphosyntactic Analyzer for Word Formation and
  Non-standard Language*. To appear in the Proceedings of the 16th Symposium
  in Information and Human Language Technology (STIL), Fortaleza,
  September 29 – October 02, 2025.

- Leonel Figueiredo de Alencar. 2023.
  *Yauti: A Tool for Morphosyntactic Analysis of Nheengatu within the
  Universal Dependencies Framework*. In Anais do XIV Simpósio Brasileiro
  de Tecnologia da Informação e da Linguagem Humana, pages 135–145.
  SBC, Porto Alegre, RS, Brasil.
  DOI: https://doi.org/10.5753/stil.2023.234131
  URL: https://sol.sbc.org.br/index.php/stil/article/view/25445

Usage example
-------------
From the command line:

    $ python CompareGoldTestFeats.py -t UD_Nheengatu-CompLin/*.conllu -o features.json

- The `-t` option specifies one or more input CoNLL-U files.
- The `-o` option specifies the output JSON file.
- If `-t` is omitted, the script defaults to the treebank defined in `TREEBANK_PATH`.

Output
------
- JSON file containing aligned gold vs. test feature annotations.
Example entries:
```json
	{
        "Avila2021:0:0:76@9": [
            {
                "Red": "Yes"
            },
            {
                "Red": "Yes"
            }
        ]
    },
	{
        "Magalhaes1876:10:4:239@8": [
            {
                "OrigLang": "pt"
            },
            {}
        ]
	},
	{
        "Rodrigues1890:1-1-7:4:4@15": [
            {
                "Style": "Rare",
                "VerbForm": "Inf",
                "StandardForm": "repiamu",
                "StandardMood": "Imp",
                "StandardNumber": "Sing",
                "StandardPerson": "2",
                "StandardVerbForm": "Fin"
            },
            {
                "Style": "Rare",
                "VerbForm": "Inf",
                "StandardForm": "repiamu",
                "StandardMood": "Imp,Ind",
                "StandardNumber": "Sing",
                "StandardPerson": "2",
                "StandardVerbForm": "Fin"
            }
        ]
    },
```

The resulting JSON file can then be used by `EvaluateFeatures.py` or
`EvaluateFeaturesSklearn.py` to compute precision, recall, F1-score,
and confusion matrices.

"""

import json
from Yauti import (
    extractConlluSents,
    mkConlluSentence,
    TREEBANK_PATH,
    tokenize,
    splitMultiWordTokens,
    process_token,
)
from collections import Counter

# ------------------------------------------------------------
# Core functions
# ------------------------------------------------------------

def mkGold(sents):
    """Return sentences that contain at least one special tag (/=)."""
    return [sent for sent in sents if "/=" in (sent.metadata.get("inputline") or "")]


def getTokensWithSpecialTags(tokens):
    """Return list of (token_id, token) for tokens containing '/='."""
    result = []
    i = 0
    while i < len(tokens):
        if "/=" in tokens[i]:
            result.append((i + 1, tokens[i]))
        i += 1
    return result


def extractFeatures(sent_id, gold_token, test_token):
    """
    Extract features (FEATS and MISC) from gold and test tokens.
    Returns a dict mapping sent_id to [gold_feats, test_feats].
    """
    feats = []
    for token in (gold_token, test_token):
        newfeats = {}
        token_feats = token.get("feats")
        if token_feats:
            newfeats = token_feats.copy()
        token_misc = token.get("misc")
        if token_misc:
            for k, v in token_misc.items():
                if k != "TokenRange":
                    newfeats[k] = v
        feats.append(newfeats)
    return {sent_id: feats}


def mkTestSet(treebank=TREEBANK_PATH):
    """
    Build the test set by comparing gold and Yauti analyses.

    Args:
        treebank (str or list): Path(s) to CoNLL-U file(s).

    Returns:
        list of dicts: Each dict maps sent_id to [gold_feats, test_feats].
    """
    sents = extractConlluSents(*treebank)
    tokenlists = mkGold(sents)
    test = []
    for tk in tokenlists:
        inputline = tk.metadata.get("inputline")
        sent_id = tk.metadata.get("sent_id")
        tokens = splitMultiWordTokens(tokenize(inputline))
        newtk = mkConlluSentence(tokens)
        if len(tk) == len(newtk):
            tokens_with_special_tags = getTokensWithSpecialTags(tokens)
            for token_id, token in tokens_with_special_tags:
                sent_id_token_id = f"{sent_id}@{token_id}"
                gold_token = tk.filter(id=token_id)[0]
                test_token = newtk.filter(id=token_id)[0]
                test.append(extractFeatures(sent_id_token_id, gold_token, test_token))
        else:
            print(sent_id, len(tk), len(newtk))
    return test


def save_to_json(data, filename="features.json"):
    """Save a Python data structure to a JSON file."""
    try:
        with open(filename, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=4)
        print(f"Data successfully saved to {filename}")
    except Exception as e:
        print(f"Error saving to {filename}: {e}")


# ------------------------------------------------------------
# Command-line entry point
# ------------------------------------------------------------
if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(
        description="Extract and compare morphosyntactic features from gold and Yauti analyses of Nheengatu."
    )
    parser.add_argument(
        "-t",
        "--treebanks",
        nargs="+",
        default=None,
        help="One or more input CoNLL-U files (default: TREEBANK_PATH).",
    )
    parser.add_argument(
        "-o",
        "--output",
        default="features.json",
        help="Output JSON filename (default: features.json).",
    )
    args = parser.parse_args()

    if args.treebanks:
        testset = mkTestSet(args.treebanks)
    else:
        testset = mkTestSet()

    save_to_json(testset, args.output)
