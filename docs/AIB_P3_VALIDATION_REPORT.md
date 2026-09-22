# P3 — Validation Report (execution status)

**Date:** 2026-09-22 (UTC)
**Git:** branch `cursor/p3-experimental-expansion-6db2`
**P2 input:** `docs/AIB_P2_Q1_EVIDENCE_GAP_PLAN.md` (verified on branch)

---

## Scope selected (P3 primary)

| P2 candidate | P3 decision | Rationale |
|--------------|-------------|-----------|
| Expanded controlled sample | **IN SCOPE** | 42 COV-B pairs pre-registered in `artifacts/p3_cov_b_extension/MANIFEST.json`; separate **P3-EXT** stratum |
| Multi-model | **DEFERRED** | Requires new freeze + gate evidence |
| Realistic tool environment | **DEFERRED** | Infrastructure not in tree |
| Complete D2 tool-loop traces | **DEFERRED** | Bridge documents pre-target hook only |
| Adaptive evaluation | **EXCLUDED** | Separate extension per P4.2/P3 freeze |
| Confirmatory statistics | **DEFERRED** | Sample/design not pre-registered for confirmatory |

---

## Repository verification

| Check | Result |
|-------|--------|
| P1 present (`64ef80b`) | PASS |
| P2 present (`26fa272`) | PASS |
| Historical `173736` manifest SHA | `bd388177…` PASS |
| Historical `173736` RESULTS SHA | `f7078bf0…` PASS |
| P4.2 freeze untouched | PASS |

---

## Protocol & safety gate

| Step | Command / artifact | Result |
|------|-------------------|--------|
| Protocol freeze | `config/p3_experimental_protocol_freeze.v1.json` + `docs/AIB_P3_EXPERIMENTAL_PROTOCOL_FREEZE.md` | FROZEN |
| P2 gap alignment | COV-B extension = P2 MV step 1 | PASS |
| Scientific safety gate | `python scripts/verify_p3_scientific_safety_gate.py` | **PASS** (dry-run eligible) |
| P4.2 prelive | `verify_p4_2_primary_prelive_gate.py` | PASS (not live auth) |
| P4.2 D2 live approval | `verify_p4_2_d2_live_approval.py` | **BLOCKED** (`live_d2_inference_allowed: false`) |
| P3 approval artifact | `artifacts/p3_live_execution_approval.json` | **MISSING** |

---

## Preflight (dry-run)

```text
python scripts/run_p4_3_paired_benchmark.py \
  --p3-cov-b-extension \
  --run-id p3-cov-b-ext-dry-preflight-20260922T231500Z
```

| Field | Value |
|-------|-------|
| mode | `dry_run` |
| n_episodes | 84 |
| out_dir | `results/p3_paired/p3-cov-b-ext-dry-preflight-20260922T231500Z` |
| ok | true |

Dry-run output is **preflight infrastructure validation**, not P3 live scientific evidence.

---

## Live execution

**Status: BLOCKED**

Reasons (all required):

1. `config/p4_3_d2_eval_gate.v1.json` → `live_d2_inference_allowed: false` (P4.2 and global preflight).
2. `config/p3_experimental_protocol_freeze.v1.json` → `live_execution.live_d2_inference_allowed: false`.
3. `artifacts/p3_live_execution_approval.json` not present.
4. Cloud agent policy: no unauthorized Live API.

**No live paired run executed. No new ASR/Utility/FPR scientific results produced.**

---

## Scoring / reconciliation / figures

Not applicable (no live P3 run). Scorer unchanged; when live is authorized, use:

`python scripts/score_p4_3_paired_metrics.py results/p3_paired/<run_id>`

P1 figures unchanged. Future P3 figures: separate `p3_*` naming under `docs/manuscript/figures/` if generated post-live.

---

## Historical separation

| Evidence | Run ID | Role |
|----------|--------|------|
| Historical P4.2 primary | `p42-primary-d0-d2-20260921T173736Z-controlled` | Immutable COV-A n=9+9 |
| P3-EXT (live) | `p3-cov-b-ext-*` (not executed) | COV-B n=42+42 when authorized |

---

## Reproducibility package (current)

- [x] P3 protocol + manifest + verifiers + tests
- [ ] Live RUN_MANIFEST + RESULTS
- [ ] P3 scoring summary
- [ ] P3 figures
