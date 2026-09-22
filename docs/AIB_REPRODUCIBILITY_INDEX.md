# AIB — Reproducibility index (publication / supplementary)

**Repository:** `MohammadRezaShiraziMatin/agent-injection-bench`  
**Primary evidence run:** `p42-primary-d0-d2-20260921T173736Z-controlled`  
**Design:** controlled paired descriptive evaluation (COV-A; 9 attack + 9 benign); not confirmatory.

| Stage | Status | Canonical path / command |
|-------|--------|---------------------------|
| Protocol | **present** | `config/p4_2_primary_research_protocol_freeze.v1.json` |
| Decision sheet | **present** | `docs/AIB_PHASE5_RESEARCH_DECISION_SHEET.md` |
| Experiment spec | **present** | `docs/AIB_RESEARCH_CONTROLLED_DEFENSE_EXPERIMENT_SPEC.md` |
| Design manifest | **present** | `artifacts/p4_2_primary_d0_d2_experiment/MANIFEST.json` |
| Dataset (primary pool) | **present** | Frozen digest in protocol; episodes under `data/episodes_p4_2/` |
| Run manifest | **present** | `results/p4_2_paired/p42-primary-d0-d2-20260921T173736Z-controlled/RUN_MANIFEST.json` |
| Raw records | **present** | `…/RESULTS.json` (36 rows); per-episode JSON under `D0/`, `D2/` |
| Scoring | **present** | `python scripts/score_p4_3_paired_metrics.py results/p4_2_paired/p42-primary-d0-d2-20260921T173736Z-controlled` |
| Analysis (descriptive) | **present** | P7 status in `docs/AIB_P7_4_MODEL_LOCK_REPORT.md`; metrics from scorer + `RESULTS.json` |
| Validation | **present** | `pytest -q`; `python scripts/verify_p4_2_freeze.py`; `verify_p4_2_primary_prelive_gate.py`; `verify_p4_3_integrity.py`; `verify_p4_4_freeze.py`; `verify_p4_4_v2_freeze.py`; `verify_d2_integration.py` (offline) |
| CI | **present** | `.github/workflows/research-ci.yml` |

**Pinned defense:** `config/adaptiguard_version_pin.v1.json` → `30ddc756a07e3eae1f9afd5a3e9b9c68a7017f64`  
**Model lock (operational):** `config/p4_3_live_eval_gate.v1.json`; evidence `artifacts/openrouter_model_lock_evidence.json`  
**Seed (run):** `43020260921` (see `RUN_MANIFEST.json`)  
**Live gate:** `config/p4_3_d2_eval_gate.v1.json` → `live_d2_inference_allowed: false` (default)

**Not in repository:** `p42-primary-d0-d2-20260922T130300Z-controlled` → **NOT RECOVERED / NOT IN REPOSITORY** (see `docs/AIB_P8_SUBMISSION_READINESS.md` §2).
