import argparse
import json
import os

import numpy as np
from scipy.stats import wilcoxon

HERE = os.path.dirname(os.path.abspath(__file__))
RESULTS = os.path.join(HERE, os.pardir, "results")

COMPARISONS = [
    ("Normalisation axis (25 ep)", [
        ("norm_percentile_clip", "norm_white_stripe"),
        ("norm_percentile_clip", "norm_zscore_brain"),
        ("norm_percentile_clip", "norm_hybrid_percentile_zscore"),
    ]),
    ("Augmentation axis (25 ep, percentile_clip)", [
        ("aug_no_aug", "aug_spatial_intensity"),
        ("aug_no_aug", "aug_soft_cutmix_25ep"),
        ("aug_no_aug", "aug_full_with_tumor_cutmix"),
        ("aug_spatial_intensity", "aug_soft_cutmix_25ep"),
        ("aug_spatial_intensity", "aug_full_with_tumor_cutmix"),
        ("aug_soft_cutmix_25ep", "aug_full_with_tumor_cutmix"),
    ]),
    ("Budget study (100 ep)", [
        ("final_no_aug_100ep", "final_cutmix_100ep"),
    ]),
]

def cases(exp, region, metric):
    path = os.path.join(RESULTS, f"results_{exp}_val.json")
    with open(path) as f:
        d = json.load(f)
    return np.array([c[region][metric] for c in d["per_case"]])

def test(a_name, b_name, region, metric):
    a, b = cases(a_name, region, metric), cases(b_name, region, metric)
    d = a - b
    stat, p = wilcoxon(a, b)
    star = "***" if p < 0.001 else "**" if p < 0.01 else "*" if p < 0.05 else "ns"
    return (f"| {a_name} vs {b_name} | {a.mean():.4f} | {b.mean():.4f} | "
            f"{d.mean():+.4f} | {(d > 0).sum()}/{len(a)} | {stat:.1f} | {p:.4g} | {star} |")

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--region", default="WT", choices=["WT", "TC", "ET"])
    ap.add_argument("--metric", default="dice", choices=["dice", "hd95", "sensitivity"])
    args = ap.parse_args()

    print(f"# Paired Wilcoxon signed-rank tests — {args.region} {args.metric}, n=55 patients\n")
    print("Same 55 held-out patients in every arm, so pairing cancels patient difficulty.")
    print("`wins` counts patients where the first arm scores higher.\n")
    for title, pairs in COMPARISONS:
        print(f"\n### {title}\n")
        print("| Comparison | mean A | mean B | diff | wins | W | p | |")
        print("|---|---|---|---|---|---|---|---|")
        for a, b in pairs:
            print(test(a, b, args.region, args.metric))
    print("\n*** p<0.001  ** p<0.01  * p<0.05  ns = not significant")

if __name__ == "__main__":
    main()
