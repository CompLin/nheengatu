#!/usr/bin/env python3
"""
Build a confusion matrix for dependency relations (DEPREL) by comparing
a gold CoNLL-U file with a system-output CoNLL-U file.

This script can operate in two modes:

1. Single-pair mode
   Compare one gold file against one predicted file.

   Usage:
       python deprel_confusion.py GOLD.conllu SYSTEM.conllu
       python deprel_confusion.py GOLD.conllu SYSTEM.conllu --heatmap
       python deprel_confusion.py GOLD.conllu SYSTEM.conllu --heatmap-offdiag

2. Aggregated 10-fold mode
   Compare all pairs test-N.conllu vs. test-N.out.conllu for N = 1..10,
   merge all discrepancies into one overall analysis, and generate the same
   TSV/PNG outputs from the combined results.

   Usage:
       python deprel_confusion.py --all-folds
       python deprel_confusion.py --all-folds --heatmap
       python deprel_confusion.py --all-folds --heatmap-offdiag
       python deprel_confusion.py --all-folds --coarse --max-mismatches 20

Optional flags:
    --coarse             Collapse subtypes such as 'obl:tmod' to 'obl'
    --heatmap            Display and save a full row-normalized heatmap
    --heatmap-offdiag    Display and save a row-normalized heatmap with the
                         diagonal suppressed, highlighting actual confusions
    --all-folds          Aggregate test-N.conllu vs. test-N.out.conllu for
                         N = 1..10
    --max-mismatches K   Limit plots to labels involved in the top K off-
                         diagonal confusion pairs. This affects only plots,
                         not TSV exports.

Notes:
- Ignores comment lines.
- Ignores multiword token lines such as 3-4.
- Ignores empty nodes such as 5.1.
- Assumes corresponding files contain the same tokenization and sentence order.
"""

import argparse
import os
import re
import sys
from collections import Counter

import matplotlib.pyplot as plt
import pandas as pd


def parse_args():
    parser = argparse.ArgumentParser(
        description="Build confusion matrices for DEPREL predictions."
    )
    parser.add_argument("gold_file", nargs="?", help="Gold CoNLL-U file")
    parser.add_argument("pred_file", nargs="?", help="Predicted CoNLL-U file")
    parser.add_argument(
        "--coarse",
        action="store_true",
        help="Collapse subtypes such as 'obl:tmod' to 'obl'",
    )
    parser.add_argument(
        "--heatmap",
        action="store_true",
        help="Display and save a full row-normalized heatmap",
    )
    parser.add_argument(
        "--heatmap-offdiag",
        action="store_true",
        help="Display and save a row-normalized heatmap with the diagonal suppressed",
    )
    parser.add_argument(
        "--all-folds",
        action="store_true",
        help="Aggregate test-N.conllu vs. test-N.out.conllu for N = 1..10",
    )
    parser.add_argument(
        "--max-mismatches",
        type=int,
        default=None,
        metavar="K",
        help=(
            "Limit plots to labels involved in the top K off-diagonal confusion "
            "pairs; affects only plots, not TSV exports"
        ),
    )
    return parser.parse_args()


def infer_run_label(args):
    """
    Infer a label to be inserted into output filenames.

    Returns:
        - 'all-folds' for aggregated mode
        - 'fold-N' if gold_file matches test-N.conllu
        - 'single' otherwise
    """
    if args.all_folds:
        return "all-folds"

    if args.gold_file:
        match = re.search(r"test-(\d+)\.conllu$", os.path.basename(args.gold_file))
        if match:
            return f"fold-{match.group(1)}"

    return "single"


def read_deprels(conllu_path, use_coarse=False):
    """
    Read DEPREL labels from a CoNLL-U file.

    Returns a list of tuples:
        (sent_id, token_id, form, head, deprel)
    """
    rows = []
    sent_id = None

    with open(conllu_path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.rstrip("\n")

            if not line:
                continue

            if line.startswith("#"):
                if line.startswith("# sent_id ="):
                    sent_id = line.split("=", 1)[1].strip()
                continue

            cols = line.split("\t")
            if len(cols) != 10:
                continue

            token_id = cols[0]

            # Ignore multiword tokens (e.g. 3-4) and empty nodes (e.g. 5.1)
            if "-" in token_id or "." in token_id:
                continue

            form = cols[1]
            head = cols[6]
            deprel = cols[7]

            if use_coarse:
                deprel = deprel.split(":", 1)[0]

            rows.append((sent_id, token_id, form, head, deprel))

    return rows


def compare_pair(gold_file, pred_file, use_coarse=False, pair_label=None):
    """
    Compare one gold/predicted file pair and return labels and mismatches.
    """
    gold = read_deprels(gold_file, use_coarse=use_coarse)
    pred = read_deprels(pred_file, use_coarse=use_coarse)

    if len(gold) != len(pred):
        raise ValueError(
            f"Different numbers of comparable tokens in pair "
            f"{gold_file} vs {pred_file}: gold={len(gold)} vs pred={len(pred)}"
        )

    gold_labels = []
    pred_labels = []
    mismatches = []

    for g, p in zip(gold, pred):
        g_sent_id, g_id, g_form, g_head, g_rel = g
        p_sent_id, p_id, p_form, p_head, p_rel = p

        if (g_id != p_id) or (g_form != p_form):
            raise ValueError(
                "Files are not aligned.\n"
                f"Gold: file={gold_file}, sent_id={g_sent_id}, id={g_id}, form={g_form}\n"
                f"Pred: file={pred_file}, sent_id={p_sent_id}, id={p_id}, form={p_form}"
            )

        gold_labels.append(g_rel)
        pred_labels.append(p_rel)

        if g_rel != p_rel:
            mismatches.append({
                "pair": pair_label if pair_label is not None else f"{gold_file} vs {pred_file}",
                "gold_file": gold_file,
                "pred_file": pred_file,
                "sent_id": g_sent_id,
                "token_id": g_id,
                "form": g_form,
                "gold_head": g_head,
                "pred_head": p_head,
                "gold_deprel": g_rel,
                "pred_deprel": p_rel,
            })

    return gold_labels, pred_labels, mismatches


def build_confusion_from_pairs(file_pairs, use_coarse=False):
    """
    Build one overall confusion matrix from one or more file pairs.
    """
    all_gold_labels = []
    all_pred_labels = []
    all_mismatches = []

    for pair_label, gold_file, pred_file in file_pairs:
        gold_labels, pred_labels, mismatches = compare_pair(
            gold_file,
            pred_file,
            use_coarse=use_coarse,
            pair_label=pair_label,
        )
        all_gold_labels.extend(gold_labels)
        all_pred_labels.extend(pred_labels)
        all_mismatches.extend(mismatches)

    cm = pd.crosstab(
        pd.Series(all_gold_labels, name="Gold"),
        pd.Series(all_pred_labels, name="Predicted"),
        dropna=False,
    )

    labels = sorted(set(all_gold_labels) | set(all_pred_labels))
    cm = cm.reindex(index=labels, columns=labels, fill_value=0)

    return cm, all_mismatches, all_gold_labels, all_pred_labels


def collect_all_fold_pairs(start=1, end=10):
    """
    Return the list of available file pairs:
        test-N.conllu vs test-N.out.conllu
    for N in [start, end].

    Missing files raise an error, since this mode is intended for a complete
    10-fold pipeline.
    """
    pairs = []

    for n in range(start, end + 1):
        gold_file = f"test-{n}.conllu"
        pred_file = f"test-{n}.out.conllu"

        if not os.path.exists(gold_file):
            raise FileNotFoundError(f"Missing gold file: {gold_file}")
        if not os.path.exists(pred_file):
            raise FileNotFoundError(f"Missing predicted file: {pred_file}")

        pairs.append((f"fold-{n}", gold_file, pred_file))

    return pairs


def normalize_rows(cm):
    """
    Row-normalize a confusion matrix so that each row sums to 1.
    """
    row_sums = cm.sum(axis=1)
    return cm.div(row_sums.replace(0, 1), axis=0)


def restrict_confusion_for_plot(cm, max_mismatches=None):
    """
    Restrict the confusion matrix used in plots to labels involved in the top
    K off-diagonal confusion pairs.

    This does not affect exported TSV files, only the plotted matrix.

    If max_mismatches is None, return the original matrix.
    """
    if max_mismatches is None:
        return cm

    if max_mismatches <= 0:
        raise ValueError("--max-mismatches must be a positive integer")

    offdiag = []
    for gold_label in cm.index:
        for pred_label in cm.columns:
            if gold_label == pred_label:
                continue
            count = cm.loc[gold_label, pred_label]
            if count > 0:
                offdiag.append((gold_label, pred_label, count))

    offdiag.sort(key=lambda x: x[2], reverse=True)
    top_pairs = offdiag[:max_mismatches]

    if not top_pairs:
        return cm

    selected_labels = sorted(
        set(g for g, _, _ in top_pairs) | set(p for _, p, _ in top_pairs)
    )
    return cm.loc[selected_labels, selected_labels]


def plot_heatmap_full(
    cm,
    output_file="deprel_confusion_matrix_normalized.png",
    max_mismatches=None,
):
    """
    Plot and save a full row-normalized heatmap.
    Uses bounded figure size to avoid excessive memory use.
    """
    cm_plot = restrict_confusion_for_plot(cm, max_mismatches=max_mismatches)
    cm_norm = normalize_rows(cm_plot)

    matrix = cm_norm.values
    nrows, ncols = matrix.shape

    cell_size = 0.55
    fig_width = min(max(12, ncols * cell_size + 3), 24)
    fig_height = min(max(10, nrows * cell_size + 3), 20)

    fig, ax = plt.subplots(figsize=(fig_width, fig_height))
    im = ax.imshow(matrix, cmap="Blues", vmin=0, vmax=1, aspect="auto")

    max_dim = max(nrows, ncols)
    tick_fs = max(7, min(12, int(220 / max_dim)))
    ann_fs = max(6, min(10, int(180 / max_dim)))
    label_fs = max(11, tick_fs + 2)
    title_fs = max(13, tick_fs + 3)

    ax.set_xticks(range(ncols))
    ax.set_yticks(range(nrows))
    ax.set_xticklabels(cm_norm.columns, rotation=90, fontsize=tick_fs)
    ax.set_yticklabels(cm_norm.index, fontsize=tick_fs)

    title = "Dependency Relation Confusion Matrix (Row-Normalized)"
    if max_mismatches is not None:
        title += f"\nTop {max_mismatches} mismatch pairs only"
    ax.set_xlabel("Predicted DEPREL", fontsize=label_fs)
    ax.set_ylabel("Gold DEPREL", fontsize=label_fs)
    ax.set_title(title, fontsize=title_fs)

    threshold = 0.5

    for i in range(nrows):
        for j in range(ncols):
            val = matrix[i, j]
            if val >= 0.01:
                color = "white" if val >= threshold else "black"
                ax.text(
                    j,
                    i,
                    f"{val:.2f}",
                    ha="center",
                    va="center",
                    fontsize=ann_fs,
                    color=color,
                )

    cbar = fig.colorbar(im, ax=ax, fraction=0.046, pad=0.04)
    cbar.set_label("Proportion within gold relation", fontsize=label_fs)
    cbar.ax.tick_params(labelsize=tick_fs)

    fig.tight_layout()
    plt.savefig(output_file, dpi=180, bbox_inches="tight")
    print(f"Saved normalized heatmap to {output_file}")
    plt.show()


def plot_heatmap_offdiag(
    cm,
    output_file="deprel_confusion_matrix_normalized_offdiag.png",
    max_mismatches=None,
):
    """
    Plot and save a row-normalized heatmap with the diagonal suppressed,
    highlighting actual confusions.
    Uses bounded figure size to avoid excessive memory use.
    """
    cm_plot = restrict_confusion_for_plot(cm, max_mismatches=max_mismatches)
    cm_norm = normalize_rows(cm_plot)
    cm_vis = cm_norm.copy()

    common_labels = [label for label in cm_vis.index if label in cm_vis.columns]
    for label in common_labels:
        cm_vis.loc[label, label] = 0.0

    matrix = cm_vis.values
    nrows, ncols = matrix.shape

    cell_size = 0.55
    fig_width = min(max(12, ncols * cell_size + 3), 24)
    fig_height = min(max(10, nrows * cell_size + 3), 20)

    fig, ax = plt.subplots(figsize=(fig_width, fig_height))

    offdiag_vals = matrix[matrix > 0]
    vmax = offdiag_vals.max() if offdiag_vals.size else 1.0

    im = ax.imshow(matrix, cmap="Blues", vmin=0, vmax=vmax, aspect="auto")

    max_dim = max(nrows, ncols)
    tick_fs = max(7, min(12, int(220 / max_dim)))
    ann_fs = max(6, min(10, int(180 / max_dim)))
    label_fs = max(11, tick_fs + 2)
    title_fs = max(13, tick_fs + 3)

    ax.set_xticks(range(ncols))
    ax.set_yticks(range(nrows))
    ax.set_xticklabels(cm_vis.columns, rotation=90, fontsize=tick_fs)
    ax.set_yticklabels(cm_vis.index, fontsize=tick_fs)

    title = "Dependency Relation Confusion Matrix (Row-Normalized, Diagonal Suppressed)"
    if max_mismatches is not None:
        title += f"\nTop {max_mismatches} mismatch pairs only"
    ax.set_xlabel("Predicted DEPREL", fontsize=label_fs)
    ax.set_ylabel("Gold DEPREL", fontsize=label_fs)
    ax.set_title(title, fontsize=title_fs)

    threshold = vmax * 0.5 if vmax > 0 else 0.5

    for i in range(nrows):
        for j in range(ncols):
            val = matrix[i, j]
            if val >= 0.01:
                color = "white" if val >= threshold else "black"
                ax.text(
                    j,
                    i,
                    f"{val:.2f}",
                    ha="center",
                    va="center",
                    fontsize=ann_fs,
                    color=color,
                )

    cbar = fig.colorbar(im, ax=ax, fraction=0.046, pad=0.04)
    cbar.set_label("Off-diagonal proportion within gold relation", fontsize=label_fs)
    cbar.ax.tick_params(labelsize=tick_fs)

    fig.tight_layout()
    plt.savefig(output_file, dpi=180, bbox_inches="tight")
    print(f"Saved normalized off-diagonal heatmap to {output_file}")
    plt.show()


def main():
    args = parse_args()
    run_label = infer_run_label(args)

    if args.all_folds:
        if args.gold_file or args.pred_file:
            print("Do not provide GOLD/PRED files together with --all-folds.", file=sys.stderr)
            sys.exit(1)
        file_pairs = collect_all_fold_pairs(1, 10)
        mode_label = "overall 10-fold aggregate"
    else:
        if not args.gold_file or not args.pred_file:
            print(
                "Usage:\n"
                "  python deprel_confusion.py GOLD.conllu SYSTEM.conllu "
                "[--coarse] [--heatmap] [--heatmap-offdiag] [--max-mismatches K]\n"
                "  python deprel_confusion.py --all-folds "
                "[--coarse] [--heatmap] [--heatmap-offdiag] [--max-mismatches K]",
                file=sys.stderr,
            )
            sys.exit(1)
        file_pairs = [("single", args.gold_file, args.pred_file)]
        mode_label = f"{args.gold_file} vs {args.pred_file}"

    cm, mismatches, gold_labels, pred_labels = build_confusion_from_pairs(
        file_pairs,
        use_coarse=args.coarse,
    )

    print(f"\n=== Confusion matrix for DEPREL ({mode_label}) ===\n")
    print(cm)

    print("\n=== Most frequent confusions (gold -> predicted) ===\n")
    pair_counts = Counter(
        (m["gold_deprel"], m["pred_deprel"])
        for m in mismatches
    )
    for (gold_rel, pred_rel), count in pair_counts.most_common(20):
        print(f"{gold_rel:15s} -> {pred_rel:15s} : {count}")

    print(f"\nTotal comparable tokens: {len(gold_labels)}")
    print(f"Correct DEPREL labels:   {sum(g == p for g, p in zip(gold_labels, pred_labels))}")
    print(f"Incorrect DEPREL labels: {len(mismatches)}")

    mismatch_file = f"deprel_mismatches_{run_label}.tsv"
    confusion_file = f"deprel_confusion_matrix_{run_label}.tsv"
    norm_file = f"deprel_confusion_matrix_normalized_{run_label}.tsv"
    heatmap_file = f"deprel_confusion_matrix_normalized_{run_label}.png"
    offdiag_file = f"deprel_confusion_matrix_normalized_offdiag_{run_label}.png"

    if mismatches:
        mismatch_df = pd.DataFrame(mismatches)
        mismatch_df.to_csv(mismatch_file, sep="\t", index=False)
        print(f"\nSaved mismatch list to {mismatch_file}")

    cm.to_csv(confusion_file, sep="\t")
    print(f"Saved confusion matrix to {confusion_file}")

    cm_norm = normalize_rows(cm)
    cm_norm.to_csv(norm_file, sep="\t")
    print(f"Saved row-normalized confusion matrix to {norm_file}")

    if args.heatmap:
        plot_heatmap_full(
            cm,
            output_file=heatmap_file,
            max_mismatches=args.max_mismatches,
        )

    if args.heatmap_offdiag:
        plot_heatmap_offdiag(
            cm,
            output_file=offdiag_file,
            max_mismatches=args.max_mismatches,
        )


if __name__ == "__main__":
    main()