#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Author: Leonel Figueiredo de Alencar
# Last update: January 26, 2026

"""
Parse parsing-evaluation result files and compute descriptive statistics
(mean and sample standard deviation) for a selected metric (default: LAS).

Typical input line in each file:
    Parsing from gold tokenization with gold tags - forms: 2078, UAS: 89.12%, LAS: 85.51%

Key features
-----------
1) Directory selection:
   - If a directory is given as a positional argument, files are searched there.
   - Otherwise, files are searched in the current working directory.

2) --pattern:
   - A glob pattern to select input files (relative to the chosen directory).

3) Sanity check:
   - By default, requires exactly 10 folds/files (configurable with --folds).

4) --metric:
   - Extracts a percentage for a metric label like "LAS" or "UAS".
   - Works for any metric that appears as: "<METRIC>: <number>%"
"""

import argparse
import glob
import os
import re
import sys
import numpy as np


def fold_index_from_filename(path):
    """
    Extract the fold index from a filename by reading the last integer before '.txt'.

    Expected examples:
        gold-tok-tags-results-1.txt  -> 1
        gold-tok-tags-results-10.txt -> 10

    Raises:
        ValueError: if no fold index can be extracted.
    """
    name = os.path.basename(path)
    m = re.search(r'-(\d+)\.txt$', name)
    if not m:
        raise ValueError(f"Cannot extract fold index from filename: {name}")
    return int(m.group(1))


def find_input_files(directory, pattern):
    """
    Find input files matching a glob pattern within a directory, and return them sorted
    by fold index.

    Args:
        directory (str): Directory to search.
        pattern (str): Glob pattern (e.g., 'gold-tok-tags-results-*.txt').

    Returns:
        list[str]: Sorted list of file paths.

    Raises:
        FileNotFoundError: If no files match the pattern.
    """
    full_pattern = os.path.join(directory, pattern)
    files = glob.glob(full_pattern)

    if not files:
        raise FileNotFoundError(
            f"No files matching pattern '{pattern}' found in: {directory}"
        )

    files.sort(key=fold_index_from_filename)
    return files


def extract_metric_values(text, metric):
    """
    Extract percentage values for a given metric from a text block.

    The function expects patterns like:
        'UAS: 89.12%'
        'LAS: 85.51%'

    Args:
        text (str): File contents.
        metric (str): Metric label (e.g., 'LAS', 'UAS').

    Returns:
        list[float]: Extracted metric values as floats.
    """
    # Allow optional spaces, and accept numbers like 85 or 85.51
    # We escape metric in case a user passes something with regex chars.
    metric_escaped = re.escape(metric)
    regex = rf'\b{metric_escaped}:\s*([\d]+(?:\.[\d]+)?)%'

    matches = re.findall(regex, text)
    return [float(m) for m in matches]


def calculate_statistics(values):
    """
    Compute mean and sample standard deviation (ddof=1).

    Args:
        values (list[float]): Numerical values.

    Returns:
        tuple[float, float]: (mean, std_dev) rounded to 2 decimals.
    """
    mean = float(np.mean(values))
    std = float(np.std(values, ddof=1))  # sample std dev
    return round(mean, 2), round(std, 2)


def parse_args(argv):
    """
    Parse command-line arguments.
    """
    parser = argparse.ArgumentParser(
        description="Compute mean/std-dev of a chosen metric from parsing result files."
    )

    # Optional positional directory; if omitted, default is current working directory.
    parser.add_argument(
        "directory",
        nargs="?",
        default=None,
        help="Directory containing result files (default: current working directory).",
    )

    parser.add_argument(
        "--pattern",
        default="gold-tok-tags-results-*.txt",
        help="Glob pattern for input files (default: gold-tok-tags-results-*.txt).",
    )

    parser.add_argument(
        "--folds",
        type=int,
        default=10,
        help="Expected number of folds/files (default: 10).",
    )

    parser.add_argument(
        "--metric",
        default="LAS",
        help="Metric label to extract (default: LAS). Examples: LAS, UAS.",
    )

    return parser.parse_args(argv)


def main(argv=None):
    """
    Main entry point.

    Raises:
        NotADirectoryError: if the provided directory does not exist.
        FileNotFoundError: if no matching files are found.
        ValueError: if the fold count is wrong or metric values are missing.
    """
    args = parse_args(sys.argv[1:] if argv is None else argv)

    results_dir = args.directory if args.directory is not None else os.getcwd()
    if not os.path.isdir(results_dir):
        raise NotADirectoryError(f"Not a directory: {results_dir}")

    files = find_input_files(results_dir, args.pattern)

    # Sanity check: expected number of folds/files
    if len(files) != args.folds:
        raise ValueError(
            f"Expected exactly {args.folds} fold files, but found {len(files)}.\n"
            f"Directory: {results_dir}\nPattern: {args.pattern}\n"
            f"Files: {', '.join(os.path.basename(f) for f in files)}"
        )

    metric = args.metric.strip()
    all_values = []

    for path in files:
        print(f"Processing file: {path}")
        with open(path, encoding="utf-8") as f:
            values = extract_metric_values(f.read(), metric)
            all_values.extend(values)

    if not all_values:
        raise ValueError(
            f"No values found for metric '{metric}'. "
            f"Check that your files contain entries like '{metric}: 85.51%'."
        )

    mean, std = calculate_statistics(all_values)

    print(f"\n{metric} Values: {all_values}")
    print(f"Mean {metric}: {mean}%")
    print(f"Standard Deviation of {metric}: {std}%")


if __name__ == "__main__":
    main()
