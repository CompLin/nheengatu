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
produces a JSON file mapping token IDs to corresponding feature sets.

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


def extractFeatures(token_id, gold_token, test_token):
    """
    Extract features (FEATS and MISC) from gold and test tokens.
    Returns a dict mapping token_id to [gold_feats, test_feats].
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
    return {token_id: feats}


def mkTestSet(treebank=TREEBANK_PATH):
    """
    Build the test set by comparing gold-standard and Yauti analyses.

    This function aligns tokens from gold-standard CoNLL-U annotations
    with their corresponding tokens produced by Yauti, focusing only on
    sentences that have an `# inputline` attribute and contain at least
    one token with a special tag ("/="). For each such token, it extracts
    and pairs morphosyntactic features from the gold and test tokens.

    Args:
        treebank (str or list): Path(s) to one or more CoNLL-U files.
            Defaults to the path defined in TREEBANK_PATH.

    Returns:
        list of dict:
            A list where each element is a dictionary of the form::

                {
                    token_id: [gold_feats, test_feats]
                }

            - ``gold_feats`` and ``test_feats`` are dictionaries of
              morphosyntactic features (from FEATS and MISC fields).
            - ``token_id`` is a unique identifier constructed as::

                  <sent_id>@<token_index>

              where:
              * ``sent_id`` is the sentence identifier from the
                `# sent_id` metadata field in the CoNLL-U file.
              * ``token_index`` is the integer ID of the token as it
                appears in the CoNLL-U token table (ID column).

            Example:
                If the sentence has ``sent_id = Avila2021:0:0:27`` and
                the token is at ID ``3`` in the CoNLL-U table, the
                resulting token_id is::

                    Avila2021:0:0:27@3

    Notes:
        - Only sentences with an `# inputline` metadata field containing
          at least one token marked with a special tag ("/=") are processed.
        - If the number of tokens in the gold and Yauti analyses does not
          match for a given sentence, the sentence ID and token counts are
          printed to stdout for debugging. These sentences are skipped and
          their tokens are **not** included in the test set.
        - At the end of execution, the function prints a summary of how
          many sentences were skipped due to mismatched token counts.
    """
    # Load sentences from CoNLL-U
    sents = extractConlluSents(*treebank)

    # Keep only sentences with "# inputline" and at least one "/=" token
    tokenlists = mkGold(sents)

    test = []
    mismatched_sentences = 0  # counter for skipped sentences

    for tk in tokenlists:
        # Original sentence text (with possible special tags)
        inputline = tk.metadata.get("inputline")

        # Sentence ID from CoNLL-U metadata
        sent_id = tk.metadata.get("sent_id")

        # Tokenize the inputline and split multiword tokens
        tokens = splitMultiWordTokens(tokenize(inputline))

        # Rebuild sentence as Yauti would analyze it
        newtk = mkConlluSentence(tokens)

        # Proceed only if token counts match (sanity check)
        if len(tk) == len(newtk):
            # Identify tokens that contain special tags ("/=")
            tokens_with_special_tags = getTokensWithSpecialTags(tokens)

            for token_id, token in tokens_with_special_tags:
                # Build unique token ID: <sent_id>@<token_index>
                sent_id_token_id = f"{sent_id}@{token_id}"

                # Retrieve corresponding gold and test tokens
                gold_token = tk.filter(id=token_id)[0]
                test_token = newtk.filter(id=token_id)[0]

                # Extract and store features
                test.append(extractFeatures(sent_id_token_id, gold_token, test_token))
        else:
            # Debugging output when gold/test tokenization lengths mismatch
            print(f"⚠️ Mismatch in {sent_id}: gold={len(tk)}, yauti={len(newtk)}")
            mismatched_sentences += 1

    # Print summary of skipped sentences
    if mismatched_sentences > 0:
        print(f"\nSummary: {mismatched_sentences} sentence(s) skipped due to mismatched token counts.")

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
