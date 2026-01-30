#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Author: Leonel Figueiredo de Alencar (adapted by ChatGPT)
# Last update: 2026-01-30

"""
CompareRawTextParsing.py

Compare fold-level evaluation results stored in two JSON files produced by
your UDPipe 1.4 evaluation pipeline (10-fold CV).

The JSON schema is expected to include keys containing the word 'sum',
whose values are dictionaries mapping metric dimensions to lists of
10 fold results, e.g.:

  "Parsing sum": {"UAS": [...10...], "LAS": [...10...] }
  "Tagging sum": {"upostag": [...10...], "xpostag": [...], ...}
  "Tokenizer words sum": {"f1": [...10...]}

This script extracts *only* those fold-level lists and compares EXP1 vs EXP2
for each dimension using Mann–Whitney U (two-sided), printing a report with:

  PART 1: EXP1 significantly outperforms EXP2
  PART 2: EXP2 significantly outperforms EXP1
  PART 3: no statistically significant difference

Example:
  CompareRawTextParsing.py exp1/raw-text-results.json exp2/raw-text-results.json
"""

import argparse
import json
import math
from pathlib import Path
from statistics import mean
from scipy.stats import mannwhitneyu


DEFAULT_ALPHA = 0.05
EXPECTED_FOLDS = 10


def load_json(path: Path) -> dict:
    """Load JSON file as a Python dict."""
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def is_number(x) -> bool:
    """Return True if x is an int/float and not NaN."""
    return isinstance(x, (int, float)) and not (isinstance(x, float) and math.isnan(x))


def extract_sum_lists(obj: dict, expected_len: int = EXPECTED_FOLDS) -> dict:
    """
    Extract fold-level lists from keys that contain 'sum'.

    Returns a dict mapping:
      metric_id -> list[float]

    where metric_id is formatted as:
      "<top_key> / <dimension>"

    Example metric_id:
      "Parsing sum / LAS"
      "Tokenizer words sum / f1"
      "Tagging sum / upostag"

    Raises ValueError on schema problems (missing, wrong length, non-numeric).
    """
    extracted = {}

    for top_key, top_val in obj.items():
        # We only consider entries whose key contains 'sum' and whose value is a dict.
        if "sum" not in top_key.lower():
            continue
        if not isinstance(top_val, dict):
            continue

        for dim, values in top_val.items():
            if not isinstance(values, list):
                continue

            metric_id = f"{top_key} / {dim}"

            if len(values) != expected_len:
                raise ValueError(
                    f"{metric_id}: expected {expected_len} fold values, found {len(values)}"
                )
            if not all(is_number(v) for v in values):
                raise ValueError(f"{metric_id}: non-numeric fold value(s) found")

            extracted[metric_id] = [float(v) for v in values]

    if not extracted:
        raise ValueError("No fold-level lists found under keys containing 'sum'.")

    return extracted


def compare_lists(x, y):
    """
    Compare two fold lists using two-sided Mann–Whitney U.

    Returns:
      (u_stat, p_value, mean_x, mean_y)
    """
    u_stat, p_value = mannwhitneyu(x, y, alternative="two-sided")
    return float(u_stat), float(p_value), float(mean(x)), float(mean(y))


def format_line(metric_id, u_stat, p, m1, m2):
    return f"- {metric_id}: mean1={m1:.3f}, mean2={m2:.3f}, U={u_stat:.3f}, p={p:.6f}"


def main():
    parser = argparse.ArgumentParser(
        description="Compare EXP1 vs EXP2 fold-level metrics from two JSON result files using Mann–Whitney U (two-sided)."
    )
    parser.add_argument("exp1_json", help="Path to EXP1 JSON (e.g., exp1/raw-text-results.json)")
    parser.add_argument("exp2_json", help="Path to EXP2 JSON (e.g., exp2/raw-text-results.json)")
    parser.add_argument("--alpha", type=float, default=DEFAULT_ALPHA, help="Significance level (default: 0.05)")
    parser.add_argument("--folds", type=int, default=EXPECTED_FOLDS, help="Expected number of folds (default: 10)")
    args = parser.parse_args()

    p1 = Path(args.exp1_json)
    p2 = Path(args.exp2_json)

    d1 = load_json(p1)
    d2 = load_json(p2)

    exp1_metrics = extract_sum_lists(d1, expected_len=args.folds)
    exp2_metrics = extract_sum_lists(d2, expected_len=args.folds)

    # Compare only metrics present in both JSON files
    common = sorted(set(exp1_metrics.keys()) & set(exp2_metrics.keys()))
    if not common:
        raise ValueError("No common 'sum' metrics found between EXP1 and EXP2 JSON files.")

    part1 = []  # EXP1 significantly better
    part2 = []  # EXP2 significantly better
    part3 = []  # not significant

    for metric_id in common:
        x = exp1_metrics[metric_id]
        y = exp2_metrics[metric_id]

        u_stat, p, m1, m2 = compare_lists(x, y)

        if p < args.alpha:
            if m1 > m2:
                part1.append((metric_id, u_stat, p, m1, m2))
            elif m2 > m1:
                part2.append((metric_id, u_stat, p, m1, m2))
            else:
                # Same mean but significant is rare; keep it in PART 3 to avoid directional claim.
                part3.append((metric_id, u_stat, p, m1, m2))
        else:
            part3.append((metric_id, u_stat, p, m1, m2))

    print(f"Comparing:\n  EXP1: {p1}\n  EXP2: {p2}")
    print(f"Test: Mann–Whitney U (two-sided), alpha={args.alpha}, folds={args.folds}")
    print()

    print("PART 1 — EXP1 significantly outperforms EXP2")
    if part1:
        for row in sorted(part1, key=lambda r: r[2]):  # sort by p-value
            print(format_line(*row))
    else:
        print("- (none)")
    print()

    print("PART 2 — EXP2 significantly outperforms EXP1")
    if part2:
        for row in sorted(part2, key=lambda r: r[2]):
            print(format_line(*row))
    else:
        print("- (none)")
    print()

    print("PART 3 — No statistically significant difference")
    if part3:
        for row in sorted(part3, key=lambda r: (r[2], r[0])):  # p then name
            print(format_line(*row))
    else:
        print("- (none)")


if __name__ == "__main__":
    main()
