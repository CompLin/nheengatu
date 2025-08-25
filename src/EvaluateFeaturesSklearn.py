#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Author: Leonel Figueiredo de Alencar
# Last update: August 25, 2025
"""
Flattens morphosyntactic feature data into y_true and y_pred labels,
computes evaluation metrics, and prints results.

Usage:
    python FlattenFeatureData.py input.json

Arguments:
    input.json: Path to JSON file containing feature data
"""

import json
import sys
from sklearn.metrics import classification_report, confusion_matrix, precision_score, recall_score, f1_score
from collections import defaultdict, Counter

def flatten_feature_data(data):
    """
    Flatten gold and predicted feature data into lists of labels for evaluation.

    Args:
        data (list): List of dicts with sent_id mapping to [gold_feats, pred_feats].

    Returns:
        tuple: (y_true, y_pred, per_feature_data)
    """
    y_true = []
    y_pred = []
    per_feature = defaultdict(lambda: {'y_true': [], 'y_pred': []})

    for item in data:
        for sent_id, (gold_feats, pred_feats) in item.items():
            all_feats = set(gold_feats.keys()) | set(pred_feats.keys())

            for feat in all_feats:
                gold_val = gold_feats.get(feat)
                pred_val = pred_feats.get(feat)

                true_label = f"{feat}={gold_val}" if gold_val is not None else "∅"
                pred_label = f"{feat}={pred_val}" if pred_val is not None else "∅"

                y_true.append(true_label)
                y_pred.append(pred_label)

                per_feature[feat]['y_true'].append(true_label)
                per_feature[feat]['y_pred'].append(pred_label)

    return y_true, y_pred, per_feature

def generate_confusion_matrices(per_feature_data):
    """
    Generate confusion matrices for each feature.

    Args:
        per_feature_data (dict): Mapping from feature name to gold/pred lists.

    Returns:
        dict: Confusion matrices for each feature.
    """
    matrices = {}
    for feat, values in per_feature_data.items():
        labels = sorted(set(values['y_true']) | set(values['y_pred']))
        cm = confusion_matrix(values['y_true'], values['y_pred'], labels=labels)
        matrices[feat] = {
            "labels": labels,
            "matrix": cm.tolist()
        }
    return matrices

def CompareGroundTruthPrediction(attribute, y_true, y_pred):
    """
    Compare ground truth and predictions for a given attribute.

    Args:
        attribute (str): The attribute name.
        y_true (list): Gold labels.
        y_pred (list): Predicted labels.

    Returns:
        list: Most common mismatches for the attribute.
    """
    res = []
    for g, p in zip(y_true, y_pred):
        if attribute in g or attribute in p:
            res.append((g, p))
    return Counter(res).most_common()

def main():
    if len(sys.argv) < 2:
        print("Usage: python EvaluateFeaturesSklearn.py input.json")
        sys.exit(1)

    infile = sys.argv[1]
    with open(infile, "r", encoding="utf-8") as f:
        data = json.load(f)

    # Flatten data
    y_true, y_pred, per_feature_data = flatten_feature_data(data)

    # Print global classification report
    print(classification_report(y_true, y_pred, digits=3, zero_division=0))

    # Compute micro/macro/weighted metrics
    metrics = {
        "Micro Precision": precision_score(y_true, y_pred, average='micro', zero_division=0),
        "Micro Recall": recall_score(y_true, y_pred, average='micro', zero_division=0),
        "Micro F1": f1_score(y_true, y_pred, average='micro', zero_division=0),
        "Macro Precision": precision_score(y_true, y_pred, average='macro', zero_division=0),
        "Macro Recall": recall_score(y_true, y_pred, average='macro', zero_division=0),
        "Macro F1": f1_score(y_true, y_pred, average='macro', zero_division=0),
        "Weighted Precision": precision_score(y_true, y_pred, average='weighted', zero_division=0),
        "Weighted Recall": recall_score(y_true, y_pred, average='weighted', zero_division=0),
        "Weighted F1": f1_score(y_true, y_pred, average='weighted', zero_division=0)
    }

    for name, value in metrics.items():
        print(f"{name}: {value:.3f}")

if __name__ == "__main__":
    main()


