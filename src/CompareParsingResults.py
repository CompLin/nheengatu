#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Author: Leonel Figueiredo de Alencar
# Last update: February 5, 2026

"""
Compare LAS results from two parsing experiments (k-fold runs).

This script is intended for the evaluation pipeline of dependency parsing experiments
(e.g., UDPipe-based pipelines) where each experiment produces a text file containing a
line of the form:

    LAS Values: [85.57, 84.38, 84.05, ...]

Those LAS values typically correspond to the scores obtained on each fold of a
k-fold cross-validation run.

The script performs up to two tasks:

1) Statistical comparison
   - Performs a two-sided Mann–Whitney U test (a nonparametric test for independent
     samples) on the per-fold LAS values from experiment 1 vs. experiment 2.

2) Visualization (optional)
   - Plots LAS per fold for both experiments on the same line chart.
   - Plotting can be disabled via the --no-plot switch, which is useful when running
     the script on headless servers or in non-interactive environments.

Important note on test choice
-----------------------------
Mann–Whitney U assumes the two samples are *independent*. If your experimental design
is *paired* by fold (e.g., both experiments are evaluated on the exact same fold splits),
a paired test (e.g., Wilcoxon signed-rank) may be more appropriate.

This script currently uses Mann–Whitney U because it treats the fold-score samples as
independent. If you decide to switch to a paired test later, update both the code and
the documentation accordingly.

Dependencies
------------
- Python 3
- scipy
- matplotlib (only required if plotting is enabled)

Example usage
-------------
Compare two experiments whose ParseGoldTokResults.py outputs were saved as
gold-tok-tags-results.txt files:

    ./CompareParsingResults.py exp1/gold-tok-tags-results.txt exp2/gold-tok-tags-results.txt

Run without plotting (e.g., on a headless server):

    ./CompareParsingResults.py exp1/gold-tok-tags-results.txt \
                               exp2/gold-tok-tags-results.txt \
                               --no-plot

Expected output includes:
- Mann–Whitney U statistic
- Two-tailed p-value
- (Optionally) a matplotlib figure window showing fold-by-fold LAS for each experiment
"""


import argparse
import ast
import json
from pathlib import Path
from typing import List

import matplotlib.pyplot as plt
from scipy.stats import mannwhitneyu
from statistics import mean


def read_las_values(results_file: Path) -> List[float]:
    """
    Extract the list of LAS values from a results file.

    Parameters
    ----------
    results_file:
        Path to a text file that contains a line starting with "LAS Values:".

    Expected format
    ---------------
    A line in the file must begin with:

        LAS Values: [<float>, <float>, ...]

    For example:
        LAS Values: [83.23, 82.35, 80.16, 82.65, 81.72, 80.8, 81.52, 83.1, 81.49, 80.93]

    Returns
    -------
    List[float]
        The parsed LAS values as floats, in the order they appear in the list.

    Raises
    ------
    FileNotFoundError
        If results_file does not exist (raised by open()).
    ValueError
        If the file does not contain a "LAS Values:" line.
    SyntaxError / ValueError
        If the list after "LAS Values:" is not a valid Python literal list.
        (Parsing is done with ast.literal_eval for safety.)
    """
    with open(results_file, encoding="utf-8") as f:
        for line in f:
            if line.startswith("LAS Values:"):
                # Split only once: "LAS Values:" + rest-of-line
                _, values = line.split(":", 1)

                # Safe parsing of a Python literal list like "[1.0, 2.0]"
                parsed = ast.literal_eval(values.strip())

                # Ensure floats (ast may produce ints if present)
                return [float(x) for x in parsed]

    raise ValueError(f"No 'LAS Values:' line found in {results_file}")


def parse_args() -> argparse.Namespace:
    """
    Parse command-line arguments.

    Returns
    -------
    argparse.Namespace
        Parsed CLI arguments.
    """
    parser = argparse.ArgumentParser(
        description=(
            "Compare LAS values from two parsing experiments (k-fold results). "
            "Reads 'LAS Values: [...]' from each input file, runs a two-sided "
            "Mann–Whitney U test, plots fold-by-fold LAS, and optionally "
            "saves the results to a JSON file."
        )
    )

    parser.add_argument(
        "exp1",
        help=(
            "Path to the results file of experiment 1 (must contain a line "
            "starting with 'LAS Values:')."
        ),
    )
    parser.add_argument(
        "exp2",
        help=(
            "Path to the results file of experiment 2 (must contain a line "
            "starting with 'LAS Values:')."
        ),
    )

    parser.add_argument(
        "--json-out",
        choices=["yes", "no"],
        default="yes",
        help="Whether to save a JSON comparison report (default: yes).",
    )

    parser.add_argument(
        "--json-file",
        default=None,
        help=(
            "Optional path for the JSON output file. "
            "If omitted, a name is generated automatically."
        ),
    )

    parser.add_argument(
    "--no-plot",
    action="store_true",
    help="Do not display the matplotlib plot (useful on headless servers).",
    )

    return parser.parse_args()


def main() -> None:
    """
    Main entry point.

    Steps
    -----
    1) Read LAS value lists for exp1 and exp2.
    2) Validate that both have the same number of folds.
    3) Run two-sided Mann–Whitney U test.
    4) Plot fold-wise LAS curves for both experiments.
    """
    args = parse_args()

    exp1_path = Path(args.exp1)
    exp2_path = Path(args.exp2)

    exp1_las = read_las_values(exp1_path)
    exp2_las = read_las_values(exp2_path)

    if len(exp1_las) != len(exp2_las):
        raise ValueError(
            "Both experiments must have the same number of folds.\n"
            f"Found {len(exp1_las)} values in {exp1_path} and "
            f"{len(exp2_las)} values in {exp2_path}."
        )

    # Mann–Whitney U test (independent samples)
    statistic, p_value = mannwhitneyu(exp1_las, exp2_las, alternative="two-sided")
    print("Mann–Whitney U statistic:", statistic)
    print("Two-tailed p-value:", p_value)

    # ---- Optional JSON output ----
    if args.json_out == "yes":
        if args.json_file:
            json_path = Path(args.json_file)
        else:
            json_path = Path(
                f"comparison-{exp1_path.parent.name}-vs-"
                f"{exp2_path.parent.name}-LAS.json"
            )

        report = {
            "metric": "LAS",
            "test": "Mann–Whitney U (two-sided)",
            "folds": len(exp1_las),
            "exp1_file": str(exp1_path),
            "exp2_file": str(exp2_path),
            "exp1_values": exp1_las,
            "exp2_values": exp2_las,
            "mean_exp1": round(mean(exp1_las), 6),
            "mean_exp2": round(mean(exp2_las), 6),
            "U_statistic": float(statistic),
            "p_value": float(p_value),
        }

        json_path.write_text(
            json.dumps(report, indent=2, ensure_ascii=False) + "\n",
            encoding="utf-8",
        )

        print(f"\nJSON results saved to: {json_path}")
    # Plot fold-by-fold LAS (unless disabled)
    if not args.no_plot:
        folds = list(range(1, len(exp1_las) + 1))

        plt.figure(figsize=(8, 5))
        plt.plot(folds, exp1_las, marker="o", label=exp1_path.parent.name)
        plt.plot(folds, exp2_las, marker="o", label=exp2_path.parent.name)

        plt.xticks(folds)
        plt.xlabel("Fold")
        plt.ylabel("LAS (%)")
        plt.title("Parsing Experiment LAS Comparison")
        plt.legend()
        plt.tight_layout()
        plt.show()

if __name__ == "__main__":
    main()
