#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Author: Leonel Figueiredo de Alencar (adapted by ChatGPT)
# Last update: February 1, 2026

"""
CompareRawTextParsing.py

Compare fold-level evaluation results stored in two JSON files produced by
your UDPipe 1.4 evaluation pipeline (10-fold CV).

The JSON schema is expected to include top-level keys containing the word 'sum'
whose values are dictionaries mapping metric dimensions to lists of 10 fold results,
e.g.:

  "Parsing sum": {"UAS": [...10...], "LAS": [...10...] }
  "Tagging sum": {"upostag": [...10...], "xpostag": [...], ...}
  "Tokenizer words sum": {"f1": [...10...]}

This script:
  1) extracts ONLY those fold-level lists (ignores averages/std scalars),
  2) compares EXP1 vs EXP2 for each dimension using Mann–Whitney U (two-sided),
  3) prints a report with three parts:
       PART 1: EXP1 significantly outperforms EXP2
       PART 2: EXP2 significantly outperforms EXP1
       PART 3: no statistically significant difference

It can also save the comparison report to JSON (default: yes):
  --json-out yes|no

Usage:
  CompareRawTextParsing.py exp1/raw-text-results.json exp2/raw-text-results.json
"""

import re
import argparse
import json
import math
from pathlib import Path
from statistics import mean
from scipy.stats import mannwhitneyu


DEFAULT_ALPHA = 0.05
EXPECTED_FOLDS = 10


def load_json(path: Path) -> dict:
    """Load a JSON file as a Python dict."""
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def is_number(x) -> bool:
    """Return True if x is int/float and not NaN."""
    return isinstance(x, (int, float)) and not (isinstance(x, float) and math.isnan(x))


def extract_sum_lists(obj: dict, expected_len: int = EXPECTED_FOLDS) -> dict:
    """
    Extract fold-level lists from top-level keys that contain 'sum' (case-insensitive).

    Returns:
      dict[str, list[float]] mapping metric_id -> fold_values

    metric_id format:
      "<top_key> / <dimension>"

    Raises ValueError if:
      - no fold-level lists are found
      - a fold list is not length expected_len
      - fold list contains non-numeric values
    """
    extracted = {}

    for top_key, top_val in obj.items():
        # Only consider keys that contain 'sum' and whose value is a dict of dimensions.
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
    """Pretty-print one comparison line."""
    return f"- {metric_id}: mean1={m1:.3f}, mean2={m2:.3f}, U={u_stat:.3f}, p={p:.6f}"


def row_to_dict(metric_id, u_stat, p, m1, m2):
    """Convert a comparison result to a JSON-friendly dict."""
    return {
        "metric": metric_id,
        "mean_exp1": round(m1, 6),
        "mean_exp2": round(m2, 6),
        "U": round(u_stat, 6),
        "p": round(p, 6),
    }


def main():
    parser = argparse.ArgumentParser(
        description=(
            "Compare EXP1 vs EXP2 fold-level metrics from two JSON result files using "
            "Mann–Whitney U (two-sided)."
        )
    )
    parser.add_argument("exp1_json", help="Path to EXP1 JSON (e.g., exp1/raw-text-results.json)")
    parser.add_argument("exp2_json", help="Path to EXP2 JSON (e.g., exp2/raw-text-results.json)")
    parser.add_argument("--alpha", type=float, default=DEFAULT_ALPHA,
                        help="Significance level (default: 0.05)")
    parser.add_argument("--folds", type=int, default=EXPECTED_FOLDS,
                        help="Expected number of folds (default: 10)")
    parser.add_argument("--json-out", choices=["yes", "no"], default="yes",
                        help="Save comparison report to JSON (default: yes)")
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
        row = row_to_dict(metric_id, u_stat, p, m1, m2)

        if p < args.alpha:
            if m1 > m2:
                part1.append(row)
            elif m2 > m1:
                part2.append(row)
            else:
                # Equal means: avoid directional claim
                part3.append(row)
        else:
            part3.append(row)

    # ---- Print report ----
    print(f"Comparing:\n  EXP1: {p1}\n  EXP2: {p2}")
    print(f"Test: Mann–Whitney U (two-sided), alpha={args.alpha}, folds={args.folds}")
    print()

    print("PART 1 — EXP1 significantly outperforms EXP2")
    if part1:
        for row in sorted(part1, key=lambda r: r["p"]):
            print(format_line(row["metric"], row["U"], row["p"], row["mean_exp1"], row["mean_exp2"]))
    else:
        print("- (none)")
    print()

    print("PART 2 — EXP2 significantly outperforms EXP1")
    if part2:
        for row in sorted(part2, key=lambda r: r["p"]):
            print(format_line(row["metric"], row["U"], row["p"], row["mean_exp1"], row["mean_exp2"]))
    else:
        print("- (none)")
    print()

    print("PART 3 — No statistically significant difference")
    if part3:
        for row in sorted(part3, key=lambda r: (r["p"], r["metric"])):
            print(format_line(row["metric"], row["U"], row["p"], row["mean_exp1"], row["mean_exp2"]))
    else:
        print("- (none)")

    # ---- Optional JSON output ----
    if args.json_out == "yes":
        exp1_name = p1.parent.name or "exp1"
        exp2_name = p2.parent.name or "exp2"
        outname = f"comparison-{exp1_name}-vs-{exp2_name}.json"

        out = {
            "alpha": args.alpha,
            "test": "Mann–Whitney U (two-sided)",
            "folds": args.folds,
            "exp1_file": str(p1),
            "exp2_file": str(p2),
            "PART1_EXP1_better": part1,
            "PART2_EXP2_better": part2,
            "PART3_no_significant_difference": part3,
        }

        with open(outname, "w", encoding="utf-8") as f:
            json.dump(out, f, indent=2, ensure_ascii=False)

        print(f"\nJSON comparison report saved to: {outname}")


if __name__ == "__main__":
    main()
