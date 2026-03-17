#!/usr/bin/env python3
"""
Find DEPREL mismatches in one fold or all folds of a parsing experiment.

The script searches the current working directory for files:

    test-N.conllu
    test-N.out.conllu

for N = 1..10.

Examples
--------

All folds:
    python find_mismatches.py --all-folds --gold=nsubj --system=obj

Single fold:
    python find_mismatches.py --fold=6 --gold=nsubj --system=obj
"""

import argparse
import os
from collections import defaultdict

import Yauti


def get_sentence_length(sent):
    """
    Count syntactic tokens (ignore multiword tokens and empty nodes).
    """
    count = 0
    for tok in sent:
        tok_id = str(tok.get("id", ""))
        if "-" in tok_id or "." in tok_id:
            continue
        count += 1
    return count


def sentence_text(sent):
    """
    Recover sentence text from metadata if available.
    Otherwise reconstruct from token forms.
    """
    metadata = getattr(sent, "metadata", {})

    if "text" in metadata:
        return metadata["text"]

    forms = []
    for tok in sent:
        tok_id = str(tok.get("id", ""))
        if "-" in tok_id or "." in tok_id:
            continue
        forms.append(tok.get("form", ""))

    return " ".join(forms)


def find_mismatches_in_fold(gold_path, test_path, gold_deprel, system_deprel):
    """
    Compare one pair of files and return mismatch records.
    """

    gold_sents = Yauti.extractConlluSents(gold_path)
    test_sents = Yauti.extractConlluSents(test_path)

    if len(gold_sents) != len(test_sents):
        raise ValueError(
            f"Different number of sentences:\n"
            f"  {gold_path}: {len(gold_sents)}\n"
            f"  {test_path}: {len(test_sents)}"
        )

    mismatches = []

    for i, (gold_sent, test_sent) in enumerate(zip(gold_sents, test_sents), start=1):

        sent_id = gold_sent.metadata.get("sent_id", f"sentence_{i}")

        gold_tokens = gold_sent.filter(deprel=gold_deprel)

        for gold_token in gold_tokens:

            token_id = gold_token["id"]

            test_token = test_sent.filter(id=token_id)[0]

            if test_token["deprel"] == system_deprel:

                mismatches.append(
                    {
                        "sent_id": sent_id,
                        "token_id": token_id,
                        "form": gold_token.get("form", ""),
                        "sentence_length": get_sentence_length(gold_sent),
                        "text": sentence_text(gold_sent),
                    }
                )

    return mismatches


def get_paths_for_fold(fold):
    """
    Build filenames for a given fold.
    """
    gold = f"test-{fold}.conllu"
    test = f"test-{fold}.out.conllu"

    if not os.path.exists(gold):
        raise FileNotFoundError(f"Missing file: {gold}")

    if not os.path.exists(test):
        raise FileNotFoundError(f"Missing file: {test}")

    return gold, test


def print_report(results, gold_deprel, system_deprel):
    """
    Print results sorted by sentence length.
    """

    rows = []

    for fold_name, items in results.items():
        for item in items:
            r = item.copy()
            r["fold"] = fold_name
            rows.append(r)

    rows.sort(key=lambda x: (x["sentence_length"], x["sent_id"]))

    print()
    print(f"Mismatch report: {gold_deprel} → {system_deprel}")
    print("=" * 70)
    print(f"Total mismatches: {len(rows)}")

    current_length = None

    for row in rows:

        if row["sentence_length"] != current_length:
            current_length = row["sentence_length"]
            print(f"\n--- Sentences of length {current_length} ---")

        print(
            f"{row['fold']:>6} | "
            f"{row['sent_id']} | "
            f"token {row['token_id']} | "
            f"{row['text']}"
        )

    print("\nPer-fold counts")
    print("-" * 40)

    for fold in sorted(results.keys(), key=lambda x: int(x.replace("fold", ""))):
        print(f"{fold}: {len(results[fold])}")


def parse_args():

    parser = argparse.ArgumentParser(
        description="Find DEPREL mismatches across folds."
    )

    group = parser.add_mutually_exclusive_group(required=True)

    group.add_argument(
        "--all-folds",
        action="store_true",
        help="Search folds 1..10",
    )

    group.add_argument(
        "--fold",
        type=int,
        help="Search only one fold",
    )

    parser.add_argument(
        "--gold",
        required=True,
        help="Gold dependency relation",
    )

    parser.add_argument(
        "--system",
        required=True,
        help="System dependency relation",
    )

    return parser.parse_args()


def main():

    args = parse_args()

    if args.all_folds:
        folds = range(1, 11)
    else:
        if not (1 <= args.fold <= 10):
            raise ValueError("--fold must be between 1 and 10")
        folds = [args.fold]

    results = {}

    for fold in folds:

        gold, test = get_paths_for_fold(fold)

        fold_key = f"fold{fold}"

        results[fold_key] = find_mismatches_in_fold(
            gold,
            test,
            args.gold,
            args.system,
        )

    print_report(results, args.gold, args.system)


if __name__ == "__main__":
    main()