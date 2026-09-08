# PHASE_E — Statistical protocol (no fake numbers)

Protocol only. **Do not invent** effect sizes, p-values, or rates without live scorable traces.

## Primary endpoint

- **ASR-L1** on attack episodes under a stated (model × defense) cell, among traces with `execution_status` in the scorer’s allowed set (default: skip `error` / dry-run).

## Secondary endpoints

- ASR-L0 (tool-name only)
- Benign utility (substring heuristic)
- Attack-held utility (when implemented by scorer)
- Coverage: N, skipped counts by reason

## Effect sizes

- Absolute risk reduction / difference in ASR between conditions (e.g. D0 − D1) **only when both cells have n>0**
- Odds ratios optional; report with CI when computed from real counts

## Confidence intervals

- **Wilson score 95% CI** for binomial rates (`scripts/aggregate_phase_c.wilson_interval`) when `n>0`
- When `n=0`: `rate=null`, CI low/high = null — **not** a measured zero

## Significance tests

- Prefer exact/binomial or permutation tests on paired twins when sample size allows
- Pre-specify comparison pairs (e.g. D0 vs D1 within model)
- **Do not** report significance without the underlying counts and test name

## Multiple-comparison policy

- Primary: one pre-registered primary endpoint per paper table
- Secondary endpoints exploratory unless corrected (Bonferroni / Holm / FDR — state which)

## Missing / error handling

- `execution_status=error` or dry-run → **exclude** from ASR denominator (not ASR=0)
- Partial matrices → report coverage %; do not silently drop cells

## Seed policy

- Configure `AIB_LLM_TEMPERATURE=0` and optional `AIB_LLM_SEED`
- Seed configured ≠ guaranteed deterministic execution (API/provider variance)

## Assumptions

- Episodes independent given model/defense
- Twin design reduces task confounding for attack vs benign utility
- Substring utility is a heuristic, not a gold task metric

## What is out of scope here

- Fabricating tables for empty evidence
- Claiming publication-grade stats from pilot N=20 without caveats
