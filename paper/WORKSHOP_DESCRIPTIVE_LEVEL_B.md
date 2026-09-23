# Workshop draft — Level B descriptive live pilot (paste-in section)

**Claim class:** `DESCRIPTIVE_ONLY` · **Evidence index:** [`../artifacts/level_b_descriptive_live/INDEX.json`](../artifacts/level_b_descriptive_live/INDEX.json)

---

## Level B descriptive pilot (small-n, non-confirmatory)

We report **protocol-authorized descriptive** paired D0/D2 live runs under the Level B matrix (execution git `b22dfbfa903a7eca9fbe0e19f75a50266150fcf6`; lean artifacts indexed at merge `32a089e35acf39831746e690da7c94ac0fdb9457`). These pilots use the same paired scorer (`scripts/score_p4_3_paired_metrics.py`) and judge (`meta-llama/llama-3.3-70b-instruct`) as the Level A chain, with AdaptiGuard pinned at `30ddc756a07e3eae1f9afd5a3e9b9c68a7017f64`. **Sample sizes are small (23 attack-scored cells per condition in INDEX summaries); we do not infer significance, superiority, or population generalization.** Full traces are operator-local; committed evidence is the lean manifest/metrics bundle only.

**Manuscript primary descriptive evidence remains Level A:** run `p42-primary-d0-d2-20260921T173736Z-controlled` (P4.2 COV-A) plus the separate P3-EXT layer documented in [`RESULTS_EVIDENCE.md`](./RESULTS_EVIDENCE.md). The Level B runs below are an **additional descriptive layer**, not a replacement primary.

**Primary target row** (`level-b-primary-d0-d2-20260923T164727Z-controlled-level_a_primary`, `openai/gpt-4o-mini-2024-07-18`): observed D0 ASR **1/23**, D2 ASR **1/23**; D2 utility **23/23**; FPR_D2 **0/23**; Paired_Defense_Rate **0/1** (one D0-success attack in the paired denominator).

**Second matrix target** (`level-b-primary-d0-d2-20260923T165457Z-controlled-candidate_family_b`, `google/gemini-2.5-flash`): observed D0 ASR **6/23**, D2 ASR **1/23**; D2 utility **23/23**; FPR_D2 **0/23**; Paired_Defense_Rate **5/6** (six D0-success attacks in the paired denominator).

We describe these figures as **observed paired sample fractions** on the recorded execution path only. They **do not** establish defense effectiveness in general, do **not** support Q1 or confirmatory claims, and must not be read as multi-model leaderboard results.
