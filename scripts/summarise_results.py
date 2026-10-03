import argparse
import glob
import json
import os

REGIONS = ("WT", "TC", "ET")
HERE = os.path.dirname(os.path.abspath(__file__))
RESULTS = os.path.join(HERE, os.pardir, "results")

def load(pattern):
    out = []
    for path in sorted(glob.glob(pattern)):
        with open(path) as f:
            out.append((os.path.basename(path), json.load(f)))
    return out

def row(res, metric):
    cells = []
    for r in REGIONS:
        m = res["aggregate"][r][metric]
        fmt = "{:.4f} ± {:.3f}" if metric == "dice" else "{:.2f} ± {:.2f}"
        cells.append(fmt.format(m["mean"], m["std"]))
    return cells

def table(entries, metric, title):
    print(f"\n### {title} — {metric}\n")
    print("| Experiment | Normalisation | " + " | ".join(REGIONS) + " |")
    print("|---|---|" + "---|" * len(REGIONS))
    for _, res in entries:
        print(f"| {res['experiment']} | {res['norm_strategy']} | "
              + " | ".join(row(res, metric)) + " |")

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--include-superseded", action="store_true")
    args = ap.parse_args()

    entries = load(os.path.join(RESULTS, "results_*_val.json"))
    if args.include_superseded:
        entries += load(os.path.join(RESULTS, "superseded", "results_*_val.json"))

    print(f"# Results — {len(entries)} runs, {entries[0][1]['num_cases']} validation cases, "
          f"seed {entries[0][1]['seed']}")
    for metric in ("dice", "hd95", "sensitivity", "specificity"):
        table(entries, metric, "All arms")

if __name__ == "__main__":
    main()
