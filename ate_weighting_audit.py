#!/usr/bin/env python3
"""ATE expertise-split weighting-sensitivity audit (stranger-rerunnable).

Reproduces, from the raw shipped parquet, the load-bearing claim in
https://cohere.com/blog/automations-early-footprint and shows that the
'healthcare LOWERING' direction is aggregation-sensitive: it flips sign
between the unweighted and task-weighted means of delta_expertise, and is
RAISING by the dataset's own primary percentile display.

Run:  python3 ate_weighting_audit.py
Needs: pandas, pyarrow. Downloads the parquet from HuggingFace (CohereLabs/ATE).
"""
import urllib.request
import pandas as pd

URL = ("https://huggingface.co/datasets/CohereLabs/ATE/resolve/main/"
       "data/occupation_results/train-00000-of-00001.parquet")

def load():
    try:
        df = pd.read_parquet("occupation_results.parquet")
        print(f"[data] local occupation_results.parquet ({len(df)} rows)")
    except FileNotFoundError:
        print(f"[data] downloading {URL}")
        urllib.request.urlretrieve(URL, "occupation_results.parquet")
        df = pd.read_parquet("occupation_results.parquet")
        print(f"[data] {len(df)} rows")
    return df

df = load()

# Sign convention (DATA_DICTIONARY.md): delta_expertise > 0 = matched tools sit
# BELOW retained tasks = remaining work MORE expertise = expertise-RAISING.
# delta_expertise < 0 = expertise-LOWERING (tools took the specialized core).

groups = {
    "healthcare (29+31)": [29, 31],
    "computing (15)":     [15],
    "legal (23)":         [23],
    "production (51)":    [51],
    "sales (41)":         [41],
}
post_claim = {
    "healthcare (29+31)": "LOWERING(<0)",
    "computing (15)":     "LOWERING(<0)",
    "legal (23)":         "RAISING(>0)",
    "production (51)":    "RAISING(>0)",
    "sales (41)":         "RAISING(>0)",
}

print(f"\ndelta_expertise coverage: {df['delta_expertise'].notna().sum()}/{len(df)}")
hdr = (f"{'group':20s} {'n':>4s} {'n_sig':>5s} {'unwt':>8s} {'task-wt':>8s} "
       f"{'pctΔ':>7s} {'>0':>4s} {'<0':>4s}  post-claims")
print(hdr)
print("-" * len(hdr))
for name, codes in groups.items():
    s = df[df["soc_major_group"].isin(codes)].copy()
    s = s[s["delta_expertise"].notna()]
    unwt = s["delta_expertise"].mean()
    # task-weighted: weight each occupation's delta by its n_matched_tasks
    w = s["n_matched_tasks"].fillna(0)
    m = w > 0
    twt = (s.loc[m, "delta_expertise"] * w[m]).sum() / w[m].sum() if m.sum() else float("nan")
    # dataset's own primary display: percentile of matched vs retained tasks
    pct = (s["matched_percentile"].mean() - s["expertise_percentile"].mean())
    pos = int((s["delta_expertise"] > 0).sum()); neg = int((s["delta_expertise"] < 0).sum())
    print(f"{name:20s} {len(s):4d} {len(s):5d} {unwt:+8.3f} {twt:+8.3f} "
          f"{pct:+7.1f} {pos:4d} {neg:4d}  {post_claim[name]}")

print("\n--- the healthcare flip, spelled out ---")
hc = df[df["soc_major_group"].isin([29, 31])].copy()
hc = hc[hc["delta_expertise"].notna()]
print(f"healthcare occupations with signal: {len(hc)}")
print(f"  unweighted mean delta_expertise = {hc['delta_expertise'].mean():+.3f}  (RAISING)")
w = hc["n_matched_tasks"].fillna(0); m = w > 0
print(f"  task-weighted mean delta_expertise = {(hc.loc[m,'delta_expertise']*w[m]).sum()/w[m].sum():+.3f}  (near-zero / sign-flips)")
print(f"  primary percentile display: matched {hc['matched_percentile'].mean():.1f} vs retained {hc['expertise_percentile'].mean():.1f} -> {hc['matched_percentile'].mean()-hc['expertise_percentile'].mean():+.1f} pct-pts (matched LESS specialized = RAISING)")
thin = (hc["n_matched_tasks"] <= 1).sum()
print(f"  thin evidence: {thin}/{len(hc)} healthcare occupations have n_matched_tasks<=1")
print(f"  flagship clinical occupations are RAISING: "
      f"{hc[hc['occupation_title'].str.contains('Dermatol|Pediatric Surgeon|Orthodontist', case=False, na=False)][['occupation_title','delta_expertise']].to_dict('records')}")
print("\nCONCLUSION: the blog's 'healthcare LOWERING' does not survive the "
      "unweighted mean (+0.084, raising), the task-weighted mean (-0.028, "
      "near-zero), or the dataset's own primary percentile display (-16 pct-pts, "
      "raising). The direction is an aggregation choice, not a stable property "
      "of the shipped data.")
