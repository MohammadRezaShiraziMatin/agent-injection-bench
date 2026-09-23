# Operator history — Level B descriptive live (2026-09-23)

**Claim class:** `DESCRIPTIVE_ONLY` (see [`../artifacts/level_b_descriptive_live/INDEX.json`](../artifacts/level_b_descriptive_live/INDEX.json)).

This note records **what happened during operator execution** on 2026-09-23. It is **not** a full trace dump, **not** confirmatory evidence, and **not** a substitute for the lean tracked bundle under `artifacts/level_b_descriptive_live/`. Full episode traces and operator stdout remain **operator-local** and are **not** committed to the repository.

## Repository anchors

| Event | Git ref |
|-------|---------|
| Tip at **live execution** (scoring / runs) | `b22dfbfa903a7eca9fbe0e19f75a50266150fcf6` |
| Evidence recorded on `main` (PR **#26** squash merge) | `32a089e35acf39831746e690da7c94ac0fdb9457` |

## Scoring and pins (from INDEX)

- **Paired scorer:** `scripts/score_p4_3_paired_metrics.py`
- **Judge model:** `meta-llama/llama-3.3-70b-instruct`
- **AdaptiGuard commit pin:** `30ddc756a07e3eae1f9afd5a3e9b9c68a7017f64`
- **Dataset digest (both runs):** `4b2e6f592118cb9c419ed11dd9574125584ebbb325709ae5fc048543a1ba9dee`
- **INDEX recorded_at_utc:** `2026-09-23T17:16:52Z`

## Canonical scored runs (tracked lean artifacts)

Metrics below are **numerator/denominator fractions** from INDEX `metrics_summary` only. Rates are descriptive sample fractions, not population estimates.

### Primary matrix row (`target-level-a-primary`)

- **Run ID:** `level-b-primary-d0-d2-20260923T164727Z-controlled-level_a_primary`
- **Target model:** `openai/gpt-4o-mini-2024-07-18`
- **Mode:** live · **n_episodes:** 46
- **Tracked subdir:** `artifacts/level_b_descriptive_live/primary/`
- **D0 ASR:** 1/23 · **D2 ASR:** 1/23
- **D0 Utility:** 22/22 · **D2 Utility:** 23/23 (rate 1.0)
- **FPR_D2:** 0/23 (rate 0.0)
- **Paired_Defense_Rate:** 0/1 (same-run D0 baseline; INDEX note: n=1 attacks with D0 `attack_success=true`)

### Candidate family B (`target-candidate-family-b`)

- **Run ID:** `level-b-primary-d0-d2-20260923T165457Z-controlled-candidate_family_b`
- **Target model:** `google/gemini-2.5-flash`
- **Mode:** live · **n_episodes:** 46
- **Tracked subdir:** `artifacts/level_b_descriptive_live/gemini/`
- **D0 ASR:** 6/23 · **D2 ASR:** 1/23
- **D0 Utility:** 23/23 · **D2 Utility:** 23/23 (rate 1.0)
- **FPR_D2:** 0/23 (rate 0.0)
- **Paired_Defense_Rate:** 5/6 (INDEX note: n=6 attacks with D0 `attack_success=true`)

## Operator-local material (not committed)

Full run trees and console logs stay on the operator machine only:

| Kind | Path pattern (local) |
|------|----------------------|
| Primary scored run | `results/level_b_paired/level-b-primary-d0-d2-20260923T164727Z-controlled-level_a_primary/` |
| Gemini scored run | `results/level_b_paired/level-b-primary-d0-d2-20260923T165457Z-controlled-candidate_family_b/` |
| Operator stdout (primary) | `results/level_b_paired/_operator_live_primary.log` (or equivalent sibling name) |
| Operator stdout (gemini) | `results/level_b_paired/_operator_live_gemini.log` (or equivalent sibling name) |

**Dry / failed / superseded sibling directories (names only — not evidence):**

- `level-b-primary-d0-d2-20260923T163631Z-dry-level_a_primary`
- `level-b-primary-d0-d2-20260923T163925Z-dry-level_a_primary`
- `level-b-primary-d0-d2-20260923T163927Z-dry-candidate_family_b`
- `level-b-primary-d0-d2-20260923T163959Z-controlled-level_a_primary` — non-canonical / superseded attempt; **do not** treat as scored evidence

## Timeline (factual, high level)

1. **Pre-live / dry attempts** — Operator exercised the Level B paired pipeline in dry mode and attempted an early controlled primary run (`…163959Z…`) that was superseded; those directories are listed above for audit naming only.
2. **Execution at `b22dfbfa…`** — Two **live** controlled paired runs completed under the authorized descriptive protocol; outputs scored with the pinned scorer and judge.
3. **Lean bundle curation** — `PAIRED_METRICS.json` and `RUN_MANIFEST.json` for each run copied into `artifacts/level_b_descriptive_live/{primary,gemini}/`; index written to `artifacts/level_b_descriptive_live/INDEX.json`.
4. **Merge to `main`** — PR **#26** squash (`32a089e…`) committed the tracked artifact bundle and documentation cross-links; **no** `results/` trees or full traces were added to git.

## Explicit non-claims

Per INDEX `not_claims` and project claim ladder:

- **No** confirmatory, SAP, or **Q1-ready** positioning from these pilot runs alone.
- **No** mutation of Level A immutable evidence or `data/episodes_*`.
- **Level A** (`p42-primary-d0-d2-20260921T173736Z-controlled`) remains the **manuscript primary** descriptive package; Level B live pilot is a **separate DESCRIPTIVE_ONLY layer**.

## Related docs

- Runbook: [`AIB_LEVEL_B_LIVE_RUN.md`](./AIB_LEVEL_B_LIVE_RUN.md)
- Claim ladder: [`../paper/RESULTS_EVIDENCE.md`](../paper/RESULTS_EVIDENCE.md)
- Workshop draft prose: [`../paper/WORKSHOP_DESCRIPTIVE_LEVEL_B.md`](../paper/WORKSHOP_DESCRIPTIVE_LEVEL_B.md)
- Status / Phase 4: [`STATUS.md`](./STATUS.md)
