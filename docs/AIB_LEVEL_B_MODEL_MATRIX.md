# Level B model matrix (Phase 2 scaffolding → Phase 4 prelive lock)

**Document ID:** `aib-level-b-model-matrix-v1`  
**Status:** **DESIGN / AUTHORIZED_FOR_DESCRIPTIVE_LIVE** — second target **LOCKED**; desktop live authorized (evidence pending run IDs)  
**Config:** [`../config/level_b_model_matrix.v1.json`](../config/level_b_model_matrix.v1.json)

This document describes the Level B multi-model matrix on the Q1 strengthening path ([`AIB_Q1_STRENGTHENING_4PHASE.md`](./AIB_Q1_STRENGTHENING_4PHASE.md)). Phase 4 **prelive** locks the second target family (`google/gemini-2.5-flash`) with OpenRouter catalog evidence. That lock does **not** authorize live runs, does **not** add Level B evidence under `results/`, and does **not** support cross-model ASR or generalization claims until fresh immutable run IDs exist.

---

## Scope

| In scope (prelive lock) | Out of scope |
|-------------------------|--------------|
| Two target families with explicit generation and cache fields | Live OpenRouter inference |
| Level A target/judge IDs as inherited rows | Matrix-level `AUTHORIZED` or live gate enablement |
| **LOCKED** second target (`google/gemini-2.5-flash`) + catalog snapshot | New run IDs or scored outcomes |
| Offline verifiers + Research CI | Confirmatory SAP lock or forged operator approval |

The matrix implements Level B protocol [§13 Model matrix](./AIB_LEVEL_B_EXPERIMENTAL_PROTOCOL.md#13-model-matrix-design-only-until-lock): minimum two target families for a future multi-model claim, single operational judge unless a pre-registered ablation says otherwise, explicit temperature / `max_tokens` / cache policy per row.

---

## Relationship to Level A

- **Level A lock evidence** remains in `config/p4_3_live_eval_gate.v1.json` and `scripts/verify_model_lock.py` (P4.3 live eval path).
- Matrix rows marked `INHERITS_LEVEL_A` must match that gate’s `exact_model_id` values; the offline verifier enforces this.
- Level A result bundles (`p42-primary-d0-d2-20260921T173736Z-controlled`, `p3-cov-b-ext-20260923T112900Z-controlled`) stay **immutable**.

[`config/level_b_protocol_freeze.v1.json`](../config/level_b_protocol_freeze.v1.json) is **`FROZEN`** with **`DESCRIPTIVE_ONLY`** claim class (confirmatory SAP remains out of scope).

---

## Row semantics

| Field | Meaning |
|-------|---------|
| `role` | `target` or `judge` |
| `family` | Stable family label for stratification / manifests |
| `model_id` | OpenRouter-style slug when known |
| `lock_status` | `INHERITS_LEVEL_A`, `CANDIDATE_NOT_LOCKED`, or `LOCKED` after sign-off |
| `catalog_lock_evidence` | Path to OpenRouter catalog fingerprint JSON (second target) |
| `provider` | Routing surface (OpenRouter in current design) |
| `temperature`, `max_tokens`, `cache_policy` | Frozen-at-run fields per protocol §13 |
| `routing_notes` | Provider order and fallback policy (`Google`, `allow_fallbacks: false` for Gemini row) |

**Second target family:** `google_gemini_flash` → **`google/gemini-2.5-flash`** (`LOCKED`). Evidence: [`../artifacts/level_b_openrouter_model_lock_evidence.json`](../artifacts/level_b_openrouter_model_lock_evidence.json), wired in [`../config/level_b_live_eval_gate.v1.json`](../config/level_b_live_eval_gate.v1.json).

---

## Offline verification

From repository root (no API key required):

```bash
python3 scripts/verify_level_b_model_matrix.py
python3 scripts/verify_level_b_phase4_prelive_gate.py
```

Exit code `0` when structure, fingerprint, Level A cross-check, catalog chain, and protocol-freeze pointer are valid. Exit code `1` on drift (e.g., fingerprint mismatch, false matrix `AUTHORIZED`, or Level A ID mismatch).

Research CI runs these scripts in the **Protocol and live-gate verifiers** step when present (`.github/workflows/research-ci.yml`).

---

## Claim ladder (explicit)

- Prelive lock **alone** does not establish multi-model ASR, defense efficacy, or Q1 readiness.
- Mock or offline matrix checks are **integrity scaffolding**, not experimental outcomes.
- Only Phase 4 **live** fresh immutable runs under frozen authorization may upgrade evidence toward Level B per [`../paper/RESULTS_EVIDENCE.md`](../paper/RESULTS_EVIDENCE.md).
