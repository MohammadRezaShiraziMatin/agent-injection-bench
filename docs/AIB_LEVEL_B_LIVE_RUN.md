# Level B — descriptive live runbook (operator)

**Document ID:** `aib-level-b-live-run-v1`  
**Audience:** Matin (operator) on desktop with OpenRouter key in `.env` (never committed).  
**Claim class:** **DESCRIPTIVE_ONLY** — not confirmatory; no SAP-powered Q1 generalization until separate artifacts exist.

**Scored descriptive pilot (2026-09-23):** lean tracked artifacts at [`../artifacts/level_b_descriptive_live/`](../artifacts/level_b_descriptive_live/) (`INDEX.json`). Run IDs: `level-b-primary-d0-d2-20260923T164727Z-controlled-level_a_primary`, `level-b-primary-d0-d2-20260923T165457Z-controlled-candidate_family_b`. Claim class **DESCRIPTIVE_ONLY**; Level A manuscript primary ladder unchanged.

---

## Preconditions (offline)

From repository root:

```bash
python3 scripts/verify_level_b_phase4_prelive_gate.py
python3 scripts/verify_level_b_model_matrix.py
python3 scripts/verify_level_b_harness_phase3.py
python3 scripts/verify_d2_integration.py
```

Expected gate mode: **`LIVE_AUTHORIZED_DESCRIPTIVE`**, `live_inference_allowed: true`, verifier exit code `0`.

Re-pin `git_commit_at_authorization` in `artifacts/level_b_phase4_execution_approval.json` to the merge commit SHA if `main` moved after sign-off.

---

## Environment

Load `.env` (must include `OPENROUTER_API_KEY`). Export runtime flags:

```bash
set -a
source .env
set +a
export AIB_LEVEL_B_LIVE_EXECUTION=1
export OPENROUTER_ALLOW_FALLBACKS=false
```

Judge inherits Level A routing (`OPENROUTER_JUDGE_MODEL`, provider order) unless you intentionally override.

---

## Dry-run (no API spend)

Validates wiring for both matrix target rows without live inference:

```bash
python3 scripts/run_level_b_paired_benchmark.py
```

Output under `results/level_b_paired/` with `-dry` run IDs.

---

## Live paired benchmark (D0 then D2, frozen 23+23 population)

Both target families (GPT-4o mini + Gemini 2.5 Flash):

```bash
python3 scripts/run_level_b_paired_benchmark.py --live
```

Single matrix row only:

```bash
python3 scripts/run_level_b_paired_benchmark.py --live --matrix-row target-level-a-primary
python3 scripts/run_level_b_paired_benchmark.py --live --matrix-row target-candidate-family-b
```

Custom run id prefix (suffix added per row when `--matrix-row both`):

```bash
python3 scripts/run_level_b_paired_benchmark.py --live --run-id level-b-primary-d0-d2-20260923T180000Z-controlled
```

Runs write immutable bundles to `results/level_b_paired/<run_id>/` with D0 and D2 subtrees, paired index, and audit trail. Do **not** mutate Level A bundles under `results/p4_2_paired/` or `results/p3_paired/`.

---

## Scoring

After live completion, score with existing P4.3 paired metrics tooling pointed at the new run directory (same contracts as Level A paired runs):

```bash
python3 scripts/score_p4_3_paired_metrics.py results/level_b_paired/<run_id>
```

**Recorded scored runs (2026-09-23, git `b22dfbfa903a7eca9fbe0e19f75a50266150fcf6`):** `level-b-primary-d0-d2-20260923T164727Z-controlled-level_a_primary` and `level-b-primary-d0-d2-20260923T165457Z-controlled-candidate_family_b` — copy `PAIRED_METRICS.json` / `RUN_MANIFEST.json` into the lean tree under [`../artifacts/level_b_descriptive_live/`](../artifacts/level_b_descriptive_live/) (see `INDEX.json` for sha256). Do not invent ASR tables; quote only scored artifacts.

---

## Explicit non-claims

- Operator authorization + green offline gate **≠** confirmatory Level B claims; descriptive scored artifacts **≠** SAP / Q1-ready evidence  
- Descriptive live **≠** confirmatory inference  
- Cloud agents must not execute live OpenRouter calls; desktop operator only  

See also: [`AIB_LEVEL_B_PHASE4_PRELIVE.md`](./AIB_LEVEL_B_PHASE4_PRELIVE.md), [`AIB_LEVEL_B_EXPERIMENTAL_PROTOCOL.md`](./AIB_LEVEL_B_EXPERIMENTAL_PROTOCOL.md).
