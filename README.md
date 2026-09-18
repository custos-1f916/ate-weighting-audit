# ATE expertise-split: weighting-sensitivity audit

Stranger-rerunnable audit of the load-bearing "expertise split" claim in
Cohere's "Automation's Early Footprint" post
(https://cohere.com/blog/automations-early-footprint), re-derived from the raw
shipped dataset `CohereLabs/ATE`
(https://huggingface.co/datasets/CohereLabs/ATE).

## The claim
The post states: "In healthcare and computing, agentic tools exist for tasks
toward the specialized end (lowering). In legal, production, sales, tools stay
at the routine edges (raising)."

## Result
Re-derived from the raw parquet, **4 of the 5 directional claims reproduce.
Healthcare does not.** Its "lowering" direction is aggregation-sensitive: it
flips sign between the unweighted and task-weighted means of `delta_expertise`,
and is **raising** by the dataset's own primary percentile display.

| group | n_sig | unweighted Δ | task-weighted Δ | percentile Δ | raising / lowering | post claims |
|---|---|---|---|---|---|---|
| healthcare (29+31) | 51 | +0.084 | -0.028 | -16.0 | 36 / 15 | LOWERING |
| computing (15) | 34 | -0.131 | -0.108 | +6.0 | 11 / 23 | LOWERING |
| legal (23) | 7 | +0.130 | +0.127 | -5.5 | 4 / 3 | RAISING |
| production (51) | 32 | +0.156 | +0.136 | -18.2 | 26 / 6 | RAISING |
| sales (41) | 17 | +0.090 | +0.129 | -7.5 | 11 / 6 | RAISING |

Sign convention (DATA_DICTIONARY.md): `delta_expertise > 0` = matched tools sit
below retained tasks = remaining work MORE expertise = RAISING; `< 0` = LOWERING.
`percentile Δ` = mean `matched_percentile` − mean `expertise_percentile` (the
dataset's own primary display; negative = matched tasks LESS specialized = raising).
`task-weighted Δ` weights each occupation's `delta_expertise` by its
`n_matched_tasks`.

## The healthcare flip, spelled out
- unweighted mean Δ = +0.084 (raising)
- task-weighted mean Δ = -0.028 (near-zero; sign flips)
- primary percentile display: matched 37.2 vs retained 53.3 → -16.0 pct-pts (matched less specialized = raising)
- thin evidence: 39/51 healthcare occupations have n_matched_tasks ≤ 1
- flagship clinical occupations are raising: Dermatologists +0.645, Pediatric Surgeons +0.421, Orthodontists +0.297
- the lowering minority (15/51) is driven by a few cells: Medical Records Specialists -0.640, Pharmacists -0.605, Medical Transcriptionists -0.525

## How to rerun
    python3 ate_weighting_audit.py
Needs `pandas`, `pyarrow`. Downloads the parquet from HuggingFace if not present.
`results.txt` in this repo is the output of a fresh run (fresh HF download).

## Provenance
- data: https://huggingface.co/datasets/CohereLabs/ATE/resolve/main/data/occupation_results/train-00000-of-00001.parquet
- parquet sha256: cf03006a33398d35f4b4559d2e98488d1e2c49e157f09b00d2f8b69570bb859e
- instrument: `ate_weighting_audit.py` (this repo)
- audited: 2026-09-18
