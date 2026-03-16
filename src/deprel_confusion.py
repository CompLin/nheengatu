#!/usr/bin/env python3
"""
Build a confusion matrix for dependency relations (DEPREL) by comparing
a gold CoNLL-U file with a system-output CoNLL-U file.

Usage:
    python deprel_confusion.py GOLD.conllu SYSTEM.conllu
    python deprel_confusion.py GOLD.conllu SYSTEM.conllu --heatmap
    python deprel_confusion.py GOLD.conllu SYSTEM.conllu --heatmap-offdiag
    python deprel_confusion.py GOLD.conllu SYSTEM.conllu --coarse --heatmap

Optional flags:
    --coarse           Collapse subtypes such as 'obl:tmod' to 'obl'
    --heatmap          Display and save a full row-normalized heatmap
    --heatmap-offdiag  Display and save a row-normalized heatmap with the
                       diagonal suppressed, highlighting actual confusions

Notes:
- Ignores comment lines.
- Ignores multiword token lines such as 3-4.
- Ignores empty nodes such as 5.1.
- Assumes both files contain the same tokenization and sentence order.
"""

import sys
from collections import Counter

import matplotlib.pyplot as plt
import pandas as pd


def read_deprels(conllu_path, use_coarse=False):
    """
    Read DEPREL labels from a CoNLL-U file.

    Parameters
    ----------
    conllu_path : str
        Path to the CoNLL-U file.
    use_coarse : bool
        If True, convert labels like 'obl:tmod' to 'obl'.

    Returns
    -------
    list of tuple
        A list of tuples:
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


def build_confusion(gold_file, pred_file, use_coarse=False):
    gold = read_deprels(gold_file, use_coarse=use_coarse)
    pred = read_deprels(pred_file, use_coarse=use_coarse)

    if len(gold) != len(pred):
        raise ValueError(
            f"Different numbers of comparable tokens: "
            f"gold={len(gold)} vs pred={len(pred)}"
        )

    gold_labels = []
    pred_labels = []
    mismatches = []

    for g, p in zip(gold, pred):
        g_sent_id, g_id, g_form, g_head, g_rel = g
        p_sent_id, p_id, p_form, p_head, p_rel = p

        # Basic alignment check
        if (g_id != p_id) or (g_form != p_form):
            raise ValueError(
                "Files are not aligned.\n"
                f"Gold: sent_id={g_sent_id}, id={g_id}, form={g_form}\n"
                f"Pred: sent_id={p_sent_id}, id={p_id}, form={p_form}"
            )

        gold_labels.append(g_rel)
        pred_labels.append(p_rel)

        if g_rel != p_rel:
            mismatches.append({
                "sent_id": g_sent_id,
                "token_id": g_id,
                "form": g_form,
                "gold_head": g_head,
                "pred_head": p_head,
                "gold_deprel": g_rel,
                "pred_deprel": p_rel,
            })

    # Confusion matrix as a pandas DataFrame
    cm = pd.crosstab(
        pd.Series(gold_labels, name="Gold"),
        pd.Series(pred_labels, name="Predicted"),
        dropna=False
    )

    # Sort relations alphabetically
    cm = cm.sort_index().sort_index(axis=1)

    return cm, mismatches, gold_labels, pred_labels


def normalize_rows(cm):
    """
    Row-normalize a confusion matrix so that each row sums to 1.

    Parameters
    ----------
    cm : pandas.DataFrame
        Confusion matrix with gold labels on rows and predicted labels on columns.

    Returns
    -------
    pandas.DataFrame
        Row-normalized confusion matrix.
    """
    row_sums = cm.sum(axis=1)
    return cm.div(row_sums.replace(0, 1), axis=0)


def plot_heatmap_full(cm, output_file="deprel_confusion_matrix_normalized.png"):
    cm_norm = normalize_rows(cm)

    matrix = cm_norm.values
    nrows, ncols = matrix.shape

    CELL_SIZE = 1.2

    fig_width = max(20, ncols * CELL_SIZE)
    fig_height = max(16, nrows * CELL_SIZE)

    fig, ax = plt.subplots(figsize=(fig_width, fig_height))

    im = ax.imshow(matrix, cmap="Blues", vmin=0, vmax=1)

    ax.set_xticks(range(ncols))
    ax.set_yticks(range(nrows))

    ax.set_xticklabels(cm_norm.columns, rotation=90, fontsize=16)
    ax.set_yticklabels(cm_norm.index, fontsize=16)

    ax.set_xlabel("Predicted DEPREL", fontsize=18)
    ax.set_ylabel("Gold DEPREL", fontsize=18)

    ax.set_title(
        "Dependency Relation Confusion Matrix (Row-Normalized)",
        fontsize=20,
        pad=30
    )

    threshold = 0.5

    for i in range(nrows):
        for j in range(ncols):
            val = matrix[i, j]

            if val > 0:
                color = "white" if val >= threshold else "black"

                ax.text(
                    j,
                    i,
                    f"{val:.2f}",
                    ha="center",
                    va="center",
                    fontsize=14,
                    color=color
                )

    cbar = fig.colorbar(im, ax=ax, fraction=0.03, pad=0.02)
    cbar.set_label("Proportion within gold relation", fontsize=16)

    fig.subplots_adjust(left=0.20, right=0.97, bottom=0.32, top=0.90)

    plt.savefig(output_file, dpi=300)
    print(f"Saved normalized heatmap to {output_file}")

    plt.show()


def plot_heatmap_offdiag(cm, output_file="deprel_confusion_matrix_normalized_offdiag.png"):
    """
    Plot and save a row-normalized heatmap with the diagonal suppressed,
    highlighting actual confusions.
    """
    cm_norm = normalize_rows(cm)

    # Copy for visualization only
    cm_vis = cm_norm.copy()

    common_labels = [label for label in cm_vis.index if label in cm_vis.columns]
    for label in common_labels:
        cm_vis.loc[label, label] = 0.0

    matrix = cm_vis.values
    nrows, ncols = matrix.shape

    fig_width = max(16, ncols * 0.85)
    fig_height = max(12, nrows * 0.85)

    fig, ax = plt.subplots(figsize=(fig_width, fig_height))

    offdiag_vals = matrix[matrix > 0]
    vmax = offdiag_vals.max() if offdiag_vals.size else 1.0

    im = ax.imshow(matrix, cmap="Blues", vmin=0, vmax=vmax)

    ax.set_xticks(range(ncols))
    ax.set_yticks(range(nrows))

    ax.set_xticklabels(cm_vis.columns, rotation=90, fontsize=13)
    ax.set_yticklabels(cm_vis.index, fontsize=13)

    ax.set_xlabel("Predicted DEPREL", fontsize=15)
    ax.set_ylabel("Gold DEPREL", fontsize=15)
    ax.set_title(
        "Dependency Relation Confusion Matrix (Row-Normalized, Diagonal Suppressed)",
        fontsize=17,
        pad=20
    )

    threshold = vmax * 0.5

    for i in range(nrows):
        for j in range(ncols):
            val = matrix[i, j]
            if val > 0:
                color = "white" if val >= threshold else "black"
                ax.text(
                    j,
                    i,
                    f"{val:.2f}",
                    ha="center",
                    va="center",
                    fontsize=12,
                    color=color
                )

    cbar = fig.colorbar(im, ax=ax, fraction=0.035, pad=0.02)
    cbar.set_label("Off-diagonal proportion within gold relation", fontsize=13)

    fig.subplots_adjust(left=0.18, right=0.97, bottom=0.28, top=0.90)

    plt.savefig(output_file, dpi=300)
    print(f"Saved normalized off-diagonal heatmap to {output_file}")
    plt.show()


def main():
    args = sys.argv[1:]

    if len(args) < 2:
        print(
            "Usage: python deprel_confusion.py GOLD.conllu SYSTEM.conllu "
            "[--coarse] [--heatmap] [--heatmap-offdiag]"
        )
        sys.exit(1)

    gold_file = args[0]
    pred_file = args[1]
    use_coarse = "--coarse" in args[2:]
    use_heatmap = "--heatmap" in args[2:]
    use_heatmap_offdiag = "--heatmap-offdiag" in args[2:]

    cm, mismatches, gold_labels, pred_labels = build_confusion(
        gold_file, pred_file, use_coarse=use_coarse
    )

    print("\n=== Confusion matrix for DEPREL ===\n")
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

    if mismatches:
        mismatch_df = pd.DataFrame(mismatches)
        mismatch_df.to_csv("deprel_mismatches.tsv", sep="\t", index=False)
        print("\nSaved mismatch list to deprel_mismatches.tsv")

    cm.to_csv("deprel_confusion_matrix.tsv", sep="\t")
    print("Saved confusion matrix to deprel_confusion_matrix.tsv")

    cm_norm = normalize_rows(cm)
    cm_norm.to_csv("deprel_confusion_matrix_normalized.tsv", sep="\t")
    print("Saved row-normalized confusion matrix to deprel_confusion_matrix_normalized.tsv")

    if use_heatmap:
        plot_heatmap_full(cm)

    if use_heatmap_offdiag:
        plot_heatmap_offdiag(cm)


if __name__ == "__main__":
    main()