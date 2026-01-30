#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Author: Leonel Figueiredo de Alencar
# Last update: January 29, 2026

import re
import sys
import json

from ComputeAveragesSD import compute_averages as cs


def parse_line(line):
    """
    Parse a line containing key-value pairs like:
      'Parsing ... UAS: 89.12%, LAS: 85.51%'

    Returns:
        dict[str, str]: mapping from key to value (as strings).
    """
    pattern = re.compile(r'(?P<key>[\w\s]+):\s*(?P<value>[\d.]+)')
    matches = re.finditer(pattern, line)
    return {m.group('key').strip(): m.group('value').strip() for m in matches}


def parseFile(infile):
    """
    Parse one results file and return a dict with fixed task keys:
      Tokenizer tokens, Tokenizer multiword tokens, Tokenizer words,
      Tokenizer sentences, Tagging, Parsing
    """
    results = []
    tasks = [
        'Tokenizer tokens',
        'Tokenizer multiword tokens',
        'Tokenizer words',
        'Tokenizer sentences',
        'Tagging',
        'Parsing'
    ]

    with open(infile, 'r', encoding="utf-8") as file:
        file_content = file.read()

    for line in file_content.split('\n'):
        if not (line.startswith("Tokenizer") or line.startswith("Tagging") or line.startswith("Parsing")):
            continue
        results.append(parse_line(line))

    return dict(zip(tasks, results))


def main():
    """
    Usage:
        ParseResults.py <file1> [file2 ...]
    Example:
        ParseResults.py raw-text-results-*.txt

    Besides printing results to stdout (via ComputeAveragesSD.compute_averages),
    this script also saves the returned summary dictionary to 'raw-text-results.json'.
    """
    if len(sys.argv) < 2:
        print("Usage: ParseResults.py <results_file1> [results_file2 ...]")
        sys.exit(1)

    results = [parseFile(f) for f in sys.argv[1:]]

    # ComputeAveragesSD now returns a dictionary (and can still print, if it does).
    summary = cs(results)

    # Save summary to JSON
    outname = "raw-text-results.json"
    with open(outname, "w", encoding="utf-8") as out:
        json.dump(summary, out, indent=2, ensure_ascii=False)

    print(f"\nSaved JSON summary to: {outname}")


if __name__ == "__main__":
    main()
