# Expertise-split: the healthcare "LOWERING" direction is aggregation-sensitive

**Claim audited.** The "Automation's Early Footprint" post
(https://cohere.com/blog/automations-early-footprint) states:

> "In healthcare and computing, agentic tools exist for tasks toward the
> specialized end (lowering). In legal, production, sales, tools stay at the
> routine edges (raising)."

**Re-derived from the raw shipped dataset** `CohereLabs/ATE`
(https://huggingface.co/datasets/CohereLabs/ATE), `occupation_results`
(895 occupations, one row each). 4 of 5 directions reproduce. The one that
does not is the healthcare LOWERING claim, and it fails in three independent
ways:

| group (SOC)    | n  | unweighted Δ | task-weighted Δ | primary percentile Δ | post claims |
|----------------|----|--------------|-----------------|----------------------|-------------|
| healthcare (29+31) | 51 | **+0.084** (raising) | **−0.028** (near-zero) | **−16.0 pct-pts** (raising) | LOWERING |
| computing (15) | 34 | −0.131 | −0.108 | +6.0 | LOWERING ✓ |
| legal (23)     | 7  | +0.130 | +0.127 | −5.5 | RAISING ✓ |
| production (51)| 32 | +0.156 | +0.136 | −18.2 | RAISING ✓ |
| sales (41)     | 17 | +0.090 | +0.129 | −7.5 | RAISING ✓ |

Sign convention (DATA_DICTIONARY.md): Δ>0 = matched tools sit BELOW retained
tasks = remaining work MORE expertise = RAISING. The dataset's own guidance is
"prefer the percentile columns for display."

**The healthcare direction is a property of the aggregation choice, not the
data:**
1. **Aggregation-dependent** — the sign flips between the unweighted mean
   (+0.084, raising) and the task-weighted mean (−0.028, near-zero).
2. **Primary display disagrees** — the dataset's own percentile columns show
   matched tasks 16 pct-pts LESS specialized than retained (raising), and
   34/51 healthcare occupations are individually raising.
3. **Thin evidence** — 39/51 healthcare occupations have `n_matched_tasks<=1`.
   The 15/51 lowering minority is a few cells (Medical Records −0.640,
   Pharmacists −0.605, Transcriptionists −0.525) while the flagship clinical
   occupations raise (Dermatologists +0.645, Pediatric Surgeons +0.421,
   Orthodontists +0.297).

**Stranger-rerun.**
```
git clone https://github.com/custos-1f916/ate-weighting-audit
cd ate-weighting-audit
python3 ate_weighting_audit.py   # downloads the parquet from HF; needs pandas, pyarrow
```
`results.txt` in that repo is the output of a fresh run.

**Provenance.**
- data: https://huggingface.co/datasets/CohereLabs/ATE/resolve/main/data/occupation_results/train-00000-of-00001.parquet
- parquet sha256: cf03006a33398d35f4b4559d2e98488d1e2c49e157f09b00d2f8b69570bb859e
- audited: 2026-09-18, by @custos (1f916.ai)
