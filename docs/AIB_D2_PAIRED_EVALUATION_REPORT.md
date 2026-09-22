# AIB D2 / AdaptiGuard Paired D0 vs D2 Evaluation Report

**Date:** 2026-09-21  
**Git HEAD (at run):** see `RUN_MANIFEST.json` in dry-run artifact  
**Mode:** Infrastructure + dry-run paired protocol; **live paired D0/D2 not executed**

---

## 1. Objective

Prepare controlled comparison infrastructure between **D0 (no defense)** and **D2 (AdaptiGuard)** on the frozen P4.3 benchmark (8 episodes), preserving historical D0 evidence and dataset immutability. Produce paper-oriented evidence only when gates pass; do not expand the dataset.

---

## 2. Experimental design

- **Independent variable:** `defense_condition` (`D0` vs `D2`)
- **Paired protocol:** per episode, deterministic order **D0 → D2** (`config/p4_3_paired_eval_contract.v1.json`)
- **Historical D0:** run `p43-live-20260921-controlled` remains immutable; interpretation via `artifacts/p4_3_live_corrected_analysis.json`
- **New paired dry-run:** `p43-d0-d2-20260921-dry-controlled` under `results/p4_3_paired/`

---

## 3. Dataset

| Item | Value |
|------|--------|
| P4.2 digest | `4b2e6f592118cb9c419ed11dd9574125584ebbb325709ae5fc048543a1ba9dee` |
| P4.3 digest | `e60969bee257ec3111febf215fb5f7079edb79ed050dae300e549336184ab53d` |
| Episodes | 8 (4 attack S1, 4 benign) |
| Dataset diff | **none** (`verify_p4_3_integrity.py` PASS) |

---

## 4. Model lock

| Role | Model | Provider order | Fallbacks |
|------|--------|----------------|-----------|
| Target | `openai/gpt-4o-mini-2024-07-18` | OpenAI | deny |
| Judge | `meta-llama/llama-3.3-70b-instruct` | Groq | deny |

Evidence: `artifacts/openrouter_model_lock_evidence.json`, gate `config/p4_3_live_eval_gate.v1.json`.  
**upstream_weight_revision:** UNVERIFIED (unchanged).

---

## 5. D0 definition

- `defense_enabled = false`
- Harness: `agent/loop.py` with `DefenseCondition.D0`
- Historical live metrics (corrected, n=4 attacks): ASR **1/4**, S1 **1/4**, S2/S3 forbidden **0/4**, S4 **0/4**, Utility benign **4/4**, FPR **0/4**, Defense Rate **NOT COMPUTABLE**

---

## 6. D2 definition

- `defense_enabled = true`, backend **AdaptiGuard** (external)
- Middleware: `agent/defense/middleware.py` → `agent/defense/adaptiguard_bridge.py`
- **Status:** `NOT_INTEGRATED` — no AdaptiGuard Python module on `PYTHONPATH`

---

## 7. AdaptiGuard integration

| Check | Result |
|-------|--------|
| In-repo implementation | **No** (bridge doc only: `docs/ADAPTI_GUARD_BRIDGE.md`) |
| `verify_d2_integration.py` | **BLOCKED** |
| `live_d2_inference_allowed` in gate | **false** |
| D2 live approval artifact | **MISSING** |

AdaptiGuard version/commit: **N/A** (not installed).

---

## 8. Defense instrumentation

Per-episode `defense_event` (non-secret): `defense_enabled`, `detector_invoked`, `detector_result`, `risk_score`/`risk_level` (when provided by external guard), `decision`, block/transform flags, `reason`, `latency_ms`, `defense_error`, `integration_status`.

Dry-run D2 records `decision=error`, `defense_error=true`, `integration_status=NOT_INTEGRATED` without calling target/judge APIs.

---

## 9. Paired protocol

- Runner: `scripts/run_p4_3_paired_benchmark.py` (`--live` gated)
- Output layout: `results/p4_3_paired/<run_id>/{D0,D2,paired}/`
- Comparability audit: `scripts/audit_paired_comparability.py` → **PASS** on dry-run (`mismatch_count=0`)

---

## 10. Metrics

Shared definitions: `config/p4_3_evaluation_metrics.v1.json`, scorer `scripts/score_p4_3_live_metrics.py`.

**Defense Rate ambiguity (documented, not overridden):**

- Single-condition `Defense_Rate` in metrics JSON uses S0-relative numerator — **not** valid alone as “defense prevented attack” without paired D0 reference.
- **Paired operational definition** recorded in `config/p4_3_paired_eval_contract.v1.json` as `Paired_Defense_Rate`.

**Live D2 metrics:** NOT OBSERVED (run blocked).

---

## 11. Results

| Metric | D0 (historical corrected) | D2 (live) | D0 (dry paired) | D2 (dry paired) |
|--------|---------------------------|-----------|-----------------|-----------------|
| ASR | 1/4 (0.25) | N/A | NOT VALID (dry) | NOT VALID (dry) |
| S1 | 1/4 | N/A | — | — |
| S2 forbidden | 0/4 | N/A | — | — |
| S3 unauthorized | 0/4 | N/A | — | — |
| S4 | 0/4 | N/A | — | — |
| Utility | 4/4 benign | N/A | — | — |
| FPR | 0/4 benign | N/A | — | — |
| Defense Rate | NOT COMPUTABLE | NOT COMPUTABLE | NOT COMPUTABLE | NOT COMPUTABLE |
| Paired Defense Rate | — | NOT COMPUTABLE (no live D2) | — | — |

Descriptive only; **n=4** attack episodes — not generalizable.

---

## 12. Error analysis

- **Gate failure:** AdaptiGuard not on `PYTHONPATH`; D2 gate disallows live inference; no `artifacts/p4_3_d2_live_approval.json`.
- **Defense semantics:** `detect_only` / `blocked` without utility check must not be read as successful defense (contract § outcome_semantics).

---

## 13. Limitations

- No live D2 execution; no AdaptiGuard efficacy claims.
- Provider may not honor seed; weight revision UNVERIFIED.
- Historical D0 and dry-run D2 are **not** comparable for efficacy — different modes and missing guard.

---

## 14. Reproducibility

Dry-run manifest: `results/p4_3_paired/p43-d0-d2-20260921-dry-controlled/RUN_MANIFEST.json`  
Bundle: `artifacts/p4_3_d2_paired_evidence_bundle/` (via `scripts/build_d2_paired_evidence_bundle.py`)

---

## 15. Scientific gate

```text
FINAL_GATE = BLOCKED
```

| Criterion | Status |
|-----------|--------|
| P4.2/P4.3 digest unchanged | PASS |
| D0 historical preserved | PASS |
| D2 integration verified | **FAIL** |
| Same target/judge (configured) | PASS |
| Paired mapping (dry) | PASS |
| Live paired D0/D2 comparability | **NOT RUN** |
| Execution evidence (live D2) | **MISSING** |
| No secrets in artifacts | PASS |

**D2 SCIENTIFIC GATE:** BLOCKED until external AdaptiGuard is integrated, integration tests pass, dry-run + explicit D2 approval, then live paired run with new `run_id` (never reuse `p43-live-20260921-controlled`).

---

## Tests

- `pytest -q`: 71 passed (includes `tests/test_d2_paired_eval.py`)
- `python scripts/verify_p4_3_integrity.py`: PASS
- `python scripts/verify_d2_integration.py`: exit 1 (expected BLOCKED)
