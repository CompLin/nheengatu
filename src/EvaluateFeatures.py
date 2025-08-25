#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Author: Leonel Figueiredo de Alencar
# Last update: August 11, 2025

"""
Evaluates morphosyntactic feature annotations using F1-score.
Includes per-feature metrics and confusion matrices with sentence IDs.

Usage:
    python evaluate_features.py

Requires:
    - mkTestSet(): returns a list of {sent_id: [gold_feats, test_feats]} dicts
"""

import json
from collections import defaultdict
from CompareGoldTestFeats import mkTestSet

INFILE="/home/leonel/Dropbox/publications/2025/STIL/features.edt.json"
INFILE="/home/leonel/Dropbox/publications/2025/STIL/test/data.json"

def compute_scores(tp,fp,fn):
    precision = tp / (tp + fp) if (tp + fp) else 0.0
    recall = tp / (tp + fn) if (tp + fn) else 0.0
    f1 = 2 * precision * recall / (precision + recall) if (precision + recall) else 0.0
    return precision, recall, f1

def compute_feature_f1(data):
    tp = fp = fn = 0

    feature_stats = defaultdict(lambda: {"tp": 0, "fp": 0, "fn": 0})
    confusion = defaultdict(lambda: defaultdict(list))  # feat → (gold_val, test_val) → [sent_ids]

    for item in data:
        for sent_id, (gold_feats, test_feats) in item.items():
            gold_dict = dict(gold_feats)
            test_dict = dict(test_feats)

            gold_keys = set(gold_dict)
            test_keys = set(test_dict)

            # Shared keys
            for feat in gold_keys & test_keys:
                gold_val = gold_dict[feat]
                test_val = test_dict[feat]
                if gold_val == test_val:
                    tp += 1
                    feature_stats[feat]["tp"] += 1
                else:
                    fn += 1
                    fp += 1
                    feature_stats[feat]["fn"] += 1
                    feature_stats[feat]["fp"] += 1
                    confusion[feat][(gold_val, test_val)].append(sent_id)

            # Missing in test
            for feat in gold_keys - test_keys:
                fn += 1
                feature_stats[feat]["fn"] += 1
                confusion[feat][(gold_dict[feat], "<MISSING>")].append(sent_id)

            # Extra in test
            for feat in test_keys - gold_keys:
                fp += 1
                feature_stats[feat]["fp"] += 1
                confusion[feat][("<MISSING>", test_dict[feat])].append(sent_id)

    # Overall scores
    precision, recall, f1=compute_scores(tp,fp,fn)

    return precision, recall, f1, feature_stats, confusion


def print_report(precision, recall, f1, feature_stats, confusion):
    print(f"Overall Precision: {precision:.3f}")
    print(f"Overall Recall:    {recall:.3f}")
    print(f"Overall F1-score:  {f1:.3f}")
    print("\nPer-feature scores:")
    print(f"{'Feature':<15} {'P':>6} {'R':>6} {'F1':>6} {'TP':>6} {'FP':>6} {'FN':>6}")
    for feat, stats in sorted(feature_stats.items()):
        tp = stats["tp"]
        fp = stats["fp"]
        fn = stats["fn"]
        '''p = tp / (tp + fp) if (tp + fp) else 0.0
        r = tp / (tp + fn) if (tp + fn) else 0.0
        f1_feat = 2 * p * r / (p + r) if (p + r) else 0.0'''
        p, r, f1_feat=compute_scores(tp,fp,fn)
        print(f"{feat:<15} {p:6.2f} {r:6.2f} {f1_feat:6.2f} {tp:6} {fp:6} {fn:6}")

    print("\nConfusion matrices (features with F1 < 1.0):")
    for feat, matrix in confusion.items():
        total_errors = sum(len(v) for v in matrix.values())
        if total_errors == 0:
            continue
        print(f"\nFeature: {feat}")
        for (gold_val, test_val), sent_ids in matrix.items():
            count = len(sent_ids)
            sent_list = ", ".join(sent_ids)
            print(f"  Gold: {gold_val:<15} → Test: {test_val:<15} ({count}x)")
            print(f"    Sentences: {sent_list}")


def main():
    #testset = mkTestSet()
    #Load your feature data
    with open(INFILE, "r", encoding="utf-8") as f:
        testset = json.load(f)
    print(f"Total tokens evaluated: {len(testset)}")
    precision, recall, f1, feature_stats, confusion = compute_feature_f1(testset)
    print_report(precision, recall, f1, feature_stats, confusion)


if __name__ == "__main__":
    main()

