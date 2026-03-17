#!/usr/bin/env python3
"""
Analyze parser errors in CoNLL-U files.

This script compares gold CoNLL-U files with system-output CoNLL-U files
and produces a compact diagnostic report that helps identify weaknesses in
both the parser and the annotation scheme.

It reports:

1. Global metrics:
   - UAS  (unlabeled attachment accuracy)
   - label accuracy (DEPREL only)
   - LAS  (labeled attachment accuracy)

2. Error taxonomy:
   - attachment-only errors
   - label-only errors
   - errors affecting both head and label

3. Per-relation diagnostics:
   - support
   - head accuracy
   - label accuracy
   - LAS

4. Label-wise precision / recall / F1

5. Frequent label confusions

6. Error breakdown by UPOS

7. Attachment-distance diagnostics:
   - how far the predicted head is from the gold head

It supports two modes:

1. Single-pair mode
   Compare one gold file with one predicted file.

   Usage:
       python parser_diagnostics.py GOLD.conllu SYSTEM.conllu
       python parser_diagnostics.py GOLD.conllu SYSTEM.conllu --coarse

2. Aggregated 10-fold mode
   Compare all pairs test-N.conllu vs. test-N.out.conllu for N = 1..10,
   merge all results into one overall analysis, and generate the same
   summary/TSV outputs from the combined data.

   Usage:
       python parser_diagnostics.py --all-folds
       python parser_diagnostics.py --all-folds --coarse

Outputs:
- parser_error_summary_<label>.txt
- parser_error_tokens_<label>.tsv
- parser_error_by_relation_<label>.tsv
- parser_label_prf_<label>.tsv
- parser_confusions_<label>.tsv
- parser_error_by_upos_<label>.tsv
- parser_head_distance_errors_<label>.tsv

where <label> is:
- all-folds   in aggregated mode
- fold-N      when the gold file is test-N.conllu
- single      otherwise
"""

import argparse
import os
import re
import sys

import pandas as pd


def parse_args():
    parser = argparse.ArgumentParser(
        description="Analyze parser errors in CoNLL-U files."
    )
    parser.add_argument("gold_file", nargs="?", help="Gold CoNLL-U file")
    parser.add_argument("pred_file", nargs="?", help="Predicted CoNLL-U file")
    parser.add_argument(
        "--coarse",
        action="store_true",
        help="Collapse subtypes such as 'obl:tmod' to 'obl'",
    )
    parser.add_argument(
        "--all-folds",
        action="store_true",
        help="Aggregate test-N.conllu vs. test-N.out.conllu for N = 1..10",
    )
    return parser.parse_args()


def infer_run_label(args):
    if args.all_folds:
        return "all-folds"

    if args.gold_file:
        match = re.search(r"test-(\d+)\.conllu$", os.path.basename(args.gold_file))
        if match:
            return f"fold-{match.group(1)}"

    return "single"


def collect_all_fold_pairs(start=1, end=10):
    """
    Return the list of file pairs:
        test-N.conllu vs test-N.out.conllu
    for N in [start, end], searching in the current working directory.
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


def read_conllu(path, use_coarse=False):
    """
    Read token-level information from a CoNLL-U file.

    Ignores:
    - comments
    - multiword tokens
    - empty nodes
    """
    rows = []
    sent_id = None

    with open(path, "r", encoding="utf-8") as f:
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

            if "-" in token_id or "." in token_id:
                continue

            form = cols[1]
            lemma = cols[2]
            upos = cols[3]
            xpos = cols[4]
            feats = cols[5]
            head = cols[6]
            deprel = cols[7]
            deps = cols[8]
            misc = cols[9]

            if use_coarse:
                deprel = deprel.split(":", 1)[0]

            rows.append({
                "sent_id": sent_id,
                "id": token_id,
                "form": form,
                "lemma": lemma,
                "upos": upos,
                "xpos": xpos,
                "feats": feats,
                "head": head,
                "deprel": deprel,
                "deps": deps,
                "misc": misc,
            })

    return rows


def safe_int(x):
    try:
        return int(x)
    except ValueError:
        return None


def compare_tokens(gold_rows, pred_rows, pair_label=None, gold_file=None, pred_file=None):
    """
    Align token-by-token and compute diagnostics for one pair of files.
    """
    if len(gold_rows) != len(pred_rows):
        raise ValueError(
            f"Different numbers of comparable tokens: "
            f"gold={len(gold_rows)} vs pred={len(pred_rows)}"
        )

    records = []

    for g, p in zip(gold_rows, pred_rows):
        if g["id"] != p["id"] or g["form"] != p["form"]:
            raise ValueError(
                "Files are not aligned.\n"
                f"Gold: sent_id={g['sent_id']}, id={g['id']}, form={g['form']}\n"
                f"Pred: sent_id={p['sent_id']}, id={p['id']}, form={p['form']}"
            )

        head_ok = g["head"] == p["head"]
        rel_ok = g["deprel"] == p["deprel"]
        las_ok = head_ok and rel_ok

        gold_id = safe_int(g["id"])
        gold_head = safe_int(g["head"])
        pred_head = safe_int(p["head"])

        gold_head_dist = None
        pred_head_dist = None
        head_distance_delta = None

        if gold_id is not None and gold_head is not None:
            gold_head_dist = abs(gold_id - gold_head)
        if gold_id is not None and pred_head is not None:
            pred_head_dist = abs(gold_id - pred_head)
        if gold_head is not None and pred_head is not None:
            head_distance_delta = pred_head - gold_head

        records.append({
            "pair": pair_label,
            "gold_file": gold_file,
            "pred_file": pred_file,
            "sent_id": g["sent_id"],
            "id": g["id"],
            "form": g["form"],
            "lemma": g["lemma"],
            "upos": g["upos"],
            "gold_head": g["head"],
            "pred_head": p["head"],
            "gold_deprel": g["deprel"],
            "pred_deprel": p["deprel"],
            "head_ok": head_ok,
            "rel_ok": rel_ok,
            "las_ok": las_ok,
            "attachment_only_error": (not head_ok) and rel_ok,
            "label_only_error": head_ok and (not rel_ok),
            "both_error": (not head_ok) and (not rel_ok),
            "gold_head_dist": gold_head_dist,
            "pred_head_dist": pred_head_dist,
            "head_distance_delta": head_distance_delta,
        })

    return pd.DataFrame(records)


def build_dataframe_from_pairs(file_pairs, use_coarse=False):
    """
    Build one combined dataframe from one or more gold/predicted file pairs.
    """
    frames = []

    for pair_label, gold_file, pred_file in file_pairs:
        gold_rows = read_conllu(gold_file, use_coarse=use_coarse)
        pred_rows = read_conllu(pred_file, use_coarse=use_coarse)

        df_pair = compare_tokens(
            gold_rows,
            pred_rows,
            pair_label=pair_label,
            gold_file=gold_file,
            pred_file=pred_file,
        )
        frames.append(df_pair)

    if not frames:
        return pd.DataFrame()

    return pd.concat(frames, ignore_index=True)


def compute_label_prf(df):
    """
    Compute precision / recall / F1 for DEPREL labels only.
    """
    labels = sorted(set(df["gold_deprel"]) | set(df["pred_deprel"]))
    rows = []

    for label in labels:
        tp = ((df["gold_deprel"] == label) & (df["pred_deprel"] == label)).sum()
        fp = ((df["gold_deprel"] != label) & (df["pred_deprel"] == label)).sum()
        fn = ((df["gold_deprel"] == label) & (df["pred_deprel"] != label)).sum()

        precision = tp / (tp + fp) if tp + fp else 0.0
        recall = tp / (tp + fn) if tp + fn else 0.0
        f1 = 2 * precision * recall / (precision + recall) if precision + recall else 0.0

        rows.append({
            "label": label,
            "tp": tp,
            "gold_support": tp + fn,
            "pred_support": tp + fp,
            "precision": precision,
            "recall": recall,
            "f1": f1,
        })

    return pd.DataFrame(rows).sort_values(
        ["gold_support", "f1"], ascending=[False, False]
    )


def compute_relation_summary(df):
    """
    Per-gold-relation summary.
    """
    rel = (
        df.groupby("gold_deprel")
        .agg(
            support=("gold_deprel", "size"),
            head_accuracy=("head_ok", "mean"),
            label_accuracy=("rel_ok", "mean"),
            las=("las_ok", "mean"),
            attachment_only_errors=("attachment_only_error", "sum"),
            label_only_errors=("label_only_error", "sum"),
            both_errors=("both_error", "sum"),
        )
        .reset_index()
        .rename(columns={"gold_deprel": "relation"})
        .sort_values(["support", "las"], ascending=[False, True])
    )
    return rel


def compute_confusions(df, min_count=1):
    """
    Frequent label confusions, excluding correct predictions.
    """
    bad = df[df["rel_ok"] == False]
    conf = (
        bad.groupby(["gold_deprel", "pred_deprel"])
        .size()
        .reset_index(name="count")
        .sort_values("count", ascending=False)
    )
    return conf[conf["count"] >= min_count]


def compute_upos_summary(df):
    """
    Error breakdown by UPOS.
    """
    up = (
        df.groupby("upos")
        .agg(
            support=("upos", "size"),
            head_accuracy=("head_ok", "mean"),
            label_accuracy=("rel_ok", "mean"),
            las=("las_ok", "mean"),
            attachment_only_errors=("attachment_only_error", "sum"),
            label_only_errors=("label_only_error", "sum"),
            both_errors=("both_error", "sum"),
        )
        .reset_index()
        .sort_values(["support", "las"], ascending=[False, True])
    )
    return up


def compute_head_distance_errors(df):
    """
    Summarize how wrong predicted heads differ from gold heads.
    """
    bad = df[df["head_ok"] == False].copy()

    if bad.empty:
        return pd.DataFrame(columns=["measure", "value"])

    rows = []

    rows.append({
        "measure": "mean_gold_head_distance",
        "value": bad["gold_head_dist"].dropna().mean()
    })
    rows.append({
        "measure": "mean_pred_head_distance",
        "value": bad["pred_head_dist"].dropna().mean()
    })
    rows.append({
        "measure": "mean_head_distance_delta",
        "value": bad["head_distance_delta"].dropna().mean()
    })
    rows.append({
        "measure": "median_gold_head_distance",
        "value": bad["gold_head_dist"].dropna().median()
    })
    rows.append({
        "measure": "median_pred_head_distance",
        "value": bad["pred_head_dist"].dropna().median()
    })
    rows.append({
        "measure": "median_head_distance_delta",
        "value": bad["head_distance_delta"].dropna().median()
    })

    return pd.DataFrame(rows)


def format_pct(x):
    return f"{100 * x:.2f}%"


def write_summary(
    outfile,
    df,
    relation_summary,
    label_prf,
    confusions,
    upos_summary,
    head_distance_summary
):
    total = len(df)
    head_correct = int(df["head_ok"].sum())
    rel_correct = int(df["rel_ok"].sum())
    las_correct = int(df["las_ok"].sum())

    attach_only = int(df["attachment_only_error"].sum())
    label_only = int(df["label_only_error"].sum())
    both_error = int(df["both_error"].sum())

    with open(outfile, "w", encoding="utf-8") as f:
        f.write("PARSER DIAGNOSTIC SUMMARY\n")
        f.write("=========================\n\n")

        if "pair" in df.columns and df["pair"].notna().any():
            pair_counts = df.groupby("pair").size().sort_index()
            f.write("PAIRS INCLUDED\n")
            f.write("--------------\n")
            for pair_name, count in pair_counts.items():
                f.write(f"{pair_name}: {count} tokens\n")
            f.write("\n")

        f.write("GLOBAL METRICS\n")
        f.write("--------------\n")
        f.write(f"Tokens compared: {total}\n")
        f.write(f"UAS: {format_pct(head_correct / total)} ({head_correct}/{total})\n")
        f.write(f"Label accuracy: {format_pct(rel_correct / total)} ({rel_correct}/{total})\n")
        f.write(f"LAS: {format_pct(las_correct / total)} ({las_correct}/{total})\n\n")

        f.write("ERROR TAXONOMY\n")
        f.write("--------------\n")
        f.write(f"Attachment-only errors: {attach_only}\n")
        f.write(f"Label-only errors:      {label_only}\n")
        f.write(f"Both head+label wrong:  {both_error}\n\n")

        f.write("TOP LABEL CONFUSIONS\n")
        f.write("--------------------\n")
        for _, row in confusions.head(20).iterrows():
            f.write(
                f"{row['gold_deprel']:15s} -> {row['pred_deprel']:15s} : {int(row['count'])}\n"
            )
        f.write("\n")

        f.write("HARDEST GOLD RELATIONS BY LAS (support >= 10)\n")
        f.write("---------------------------------------------\n")
        hard = relation_summary[relation_summary["support"] >= 10].sort_values(
            ["las", "support"], ascending=[True, False]
        )
        for _, row in hard.head(15).iterrows():
            f.write(
                f"{row['relation']:15s} "
                f"support={int(row['support']):4d} "
                f"head={format_pct(row['head_accuracy']):>8s} "
                f"label={format_pct(row['label_accuracy']):>8s} "
                f"LAS={format_pct(row['las']):>8s}\n"
            )
        f.write("\n")

        f.write("LABELS WITH LOWEST PRECISION (pred support >= 10)\n")
        f.write("-----------------------------------------------\n")
        low_prec = label_prf[label_prf["pred_support"] >= 10].sort_values(
            ["precision", "pred_support"], ascending=[True, False]
        )
        for _, row in low_prec.head(15).iterrows():
            f.write(
                f"{row['label']:15s} "
                f"pred={int(row['pred_support']):4d} "
                f"gold={int(row['gold_support']):4d} "
                f"P={format_pct(row['precision']):>8s} "
                f"R={format_pct(row['recall']):>8s} "
                f"F1={format_pct(row['f1']):>8s}\n"
            )
        f.write("\n")

        f.write("LABELS WITH LOWEST RECALL (gold support >= 10)\n")
        f.write("---------------------------------------------\n")
        low_rec = label_prf[label_prf["gold_support"] >= 10].sort_values(
            ["recall", "gold_support"], ascending=[True, False]
        )
        for _, row in low_rec.head(15).iterrows():
            f.write(
                f"{row['label']:15s} "
                f"gold={int(row['gold_support']):4d} "
                f"pred={int(row['pred_support']):4d} "
                f"P={format_pct(row['precision']):>8s} "
                f"R={format_pct(row['recall']):>8s} "
                f"F1={format_pct(row['f1']):>8s}\n"
            )
        f.write("\n")

        f.write("UPOS CATEGORIES WITH LOWEST LAS (support >= 10)\n")
        f.write("-----------------------------------------------\n")
        bad_upos = upos_summary[upos_summary["support"] >= 10].sort_values(
            ["las", "support"], ascending=[True, False]
        )
        for _, row in bad_upos.head(15).iterrows():
            f.write(
                f"{row['upos']:8s} "
                f"support={int(row['support']):4d} "
                f"head={format_pct(row['head_accuracy']):>8s} "
                f"label={format_pct(row['label_accuracy']):>8s} "
                f"LAS={format_pct(row['las']):>8s}\n"
            )
        f.write("\n")

        f.write("HEAD DISTANCE ERROR SUMMARY\n")
        f.write("---------------------------\n")
        for _, row in head_distance_summary.iterrows():
            f.write(f"{row['measure']}: {row['value']}\n")


def main():
    args = parse_args()
    run_label = infer_run_label(args)

    if args.all_folds:
        if args.gold_file or args.pred_file:
            print("Do not provide GOLD/PRED files together with --all-folds.")
            sys.exit(1)
        file_pairs = collect_all_fold_pairs(1, 10)
    else:
        if not args.gold_file or not args.pred_file:
            print(
                "Usage:\n"
                "  python parser_diagnostics.py GOLD.conllu SYSTEM.conllu [--coarse]\n"
                "  python parser_diagnostics.py --all-folds [--coarse]"
            )
            sys.exit(1)
        file_pairs = [("single", args.gold_file, args.pred_file)]

    df = build_dataframe_from_pairs(file_pairs, use_coarse=args.coarse)

    relation_summary = compute_relation_summary(df)
    label_prf = compute_label_prf(df)
    confusions = compute_confusions(df, min_count=1)
    upos_summary = compute_upos_summary(df)
    head_distance_summary = compute_head_distance_errors(df)

    summary_file = f"parser_error_summary_{run_label}.txt"
    tokens_file = f"parser_error_tokens_{run_label}.tsv"
    relation_file = f"parser_error_by_relation_{run_label}.tsv"
    prf_file = f"parser_label_prf_{run_label}.tsv"
    confusions_file = f"parser_confusions_{run_label}.tsv"
    upos_file = f"parser_error_by_upos_{run_label}.tsv"
    distance_file = f"parser_head_distance_errors_{run_label}.tsv"

    write_summary(
        summary_file,
        df,
        relation_summary,
        label_prf,
        confusions,
        upos_summary,
        head_distance_summary,
    )

    df.to_csv(tokens_file, sep="\t", index=False)
    relation_summary.to_csv(relation_file, sep="\t", index=False)
    label_prf.to_csv(prf_file, sep="\t", index=False)
    confusions.to_csv(confusions_file, sep="\t", index=False)
    upos_summary.to_csv(upos_file, sep="\t", index=False)
    head_distance_summary.to_csv(distance_file, sep="\t", index=False)

    total = len(df)
    print(f"Tokens compared: {total}")
    print(f"UAS:            {format_pct(df['head_ok'].mean())}")
    print(f"Label accuracy: {format_pct(df['rel_ok'].mean())}")
    print(f"LAS:            {format_pct(df['las_ok'].mean())}")
    print()
    print(f"Attachment-only errors: {int(df['attachment_only_error'].sum())}")
    print(f"Label-only errors:      {int(df['label_only_error'].sum())}")
    print(f"Both head+label wrong:  {int(df['both_error'].sum())}")
    print()
    print("Saved:")
    print(f"  {summary_file}")
    print(f"  {tokens_file}")
    print(f"  {relation_file}")
    print(f"  {prf_file}")
    print(f"  {confusions_file}")
    print(f"  {upos_file}")
    print(f"  {distance_file}")


if __name__ == "__main__":
    main()