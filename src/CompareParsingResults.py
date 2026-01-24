#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Author: Leonel Figueiredo de Alencar
# Last update: January 23, 2026

import argparse
import ast
import matplotlib.pyplot as plt
from scipy.stats import mannwhitneyu
from pathlib import Path


def read_las_values(results_file):
    """
    Extract LAS values from a results.txt file.

    Expected line format:
    LAS Values: [85.57, 84.38, 84.05, ...]
    """
    with open(results_file, encoding="utf-8") as f:
        for line in f:
            if line.startswith("LAS Values:"):
                _, values = line.split(":", 1)
                return ast.literal_eval(values.strip())

    raise ValueError(f"No 'LAS Values:' line found in {results_file}")


def main():
    parser = argparse.ArgumentParser(
        description="Compare LAS results from two parsing experiments using Wilcoxon signed-rank test."
    )
    parser.add_argument("exp1", help="Path to results.txt of experiment 1")
    parser.add_argument("exp2", help="Path to results.txt of experiment 2")

    args = parser.parse_args()

    exp1_path = Path(args.exp1)
    exp2_path = Path(args.exp2)

    exp1 = read_las_values(exp1_path)
    exp2 = read_las_values(exp2_path)

    if len(exp1) != len(exp2):
        raise ValueError("Both experiments must have the same number of folds.")

    # Mann–Whitney U test (independent samples)
    statistic, p_value = mannwhitneyu(
    exp1,
    exp2,
    alternative="two-sided"
)
    print("Mann–Whitney U statistic:", statistic)
    print("Two-tailed p-value:", p_value)

    # Plot
    folds = list(range(1, len(exp1) + 1))

    plt.figure(figsize=(8, 5))
    plt.plot(folds, exp1, marker='o', label=exp1_path.parent.name)
    plt.plot(folds, exp2, marker='o', label=exp2_path.parent.name)

    plt.xticks(folds)
    plt.xlabel('Fold')
    plt.ylabel('LAS (%)')
    plt.title('Parsing Experiment LAS Comparison')
    plt.legend()
    plt.tight_layout()
    plt.show()


if __name__ == "__main__":
    main()
