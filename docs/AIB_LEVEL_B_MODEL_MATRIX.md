# Level B model matrix (Phase 2 scaffolding)

**Document ID:** `aib-level-b-model-matrix-v1`  
**Status:** **DESIGN / NOT_AUTHORIZED** — scaffolding only  
**Config:** [`../config/level_b_model_matrix.v1.json`](../config/level_b_model_matrix.v1.json)

This document describes **Phase 2** of [`AIB_Q1_STRENGTHENING_4PHASE.md`](./AIB_Q1_STRENGTHENING_4PHASE.md): a **candidate** multi-model matrix for the Level B path. It does **not** authorize live runs, does **not** add Level B evidence under `results/`, and does **not** support cross-model ASR or generalization claims.

---

## Scope

| In scope (Phase 2) | Out of scope |
|--------------------|--------------|
| Document target + judge rows with generation and cache fields | Live OpenRouter calls |
| Reuse Level A target/judge IDs as one inherited row | Locking a second target family |
| Placeholder second **target family** (`CANDIDATE_NOT_LOCKED`) | New run IDs or scored outcomes |
| Offline verifier + Research CI hook | SAP lock or execution approval |

The matrix implements the **design intent** of Level B protocol [§13 Model matrix](./AIB_LEVEL_B_EXPERIMENTAL_PROTOCOL.md#13-model-matrix-design-only-until-lock): minimum two target families for a future multi-model claim, single operational judge unless a pre-registered ablation says otherwise, explicit temperature / `max_tokens` / cache policy per row.

---

## Relationship to Level A

- **Level A lock evidence** remains in `config/p4_3_live_eval_gate.v1.json` and `scripts/verify_model_lock.py` (P4.3 live eval path).
- Matrix rows marked `INHERITS_LEVEL_A` must match that gate’s `exact_model_id` values; the offline verifier enforces this.
- Level A result bundles (`p42-primary-d0-d2-20260921T173736Z-controlled`, `p3-cov-b-ext-20260923T112900Z-controlled`) stay **immutable**.

[`config/level_b_protocol_freeze.v1.json`](../config/level_b_protocol_freeze.v1.json) references this matrix read-only under `inherits_read_only.level_b_model_matrix` while protocol status remains `DESIGN_NOT_FROZEN`.

---

## Row semantics

| Field | Meaning |
|-------|---------|
| `role` | `target` or `judge` |
| `family` | Stable family label for stratification / manifests |
| `model_id` | OpenRouter-style slug when known; candidate rows use an explicit non-lock placeholder string |
| `lock_status` | `INHERITS_LEVEL_A`, `CANDIDATE_NOT_LOCKED`, or (future) `LOCKED` after sign-off |
| `provider` | Routing surface (OpenRouter in current design) |
| `temperature`, `max_tokens`, `cache_policy` | Frozen-at-run fields per protocol §13 |

**Second target family:** `google_gemini_flash` is a **candidate family name only**. The `model_id` is not locked until researcher sign-off, catalog snapshots, and gate artifacts exist (Phase 4 prep)—not in Phase 2.

---

## Offline verification

From repository root (no API key required):

```bash
python3 scripts/verify_level_b_model_matrix.py
```

Exit code `0` when structure, fingerprint, Level A cross-check, and protocol-freeze pointer are valid. Exit code `1` on drift (e.g., fingerprint mismatch, false `LOCKED` without approval fields, or Level A ID mismatch).

Research CI runs this script in the **Protocol and live-gate verifiers** step when present (`.github/workflows/research-ci.yml`).

---

## Claim ladder (explicit)

- Phase 2 **alone** does not establish multi-model ASR, defense efficacy, or Q1 readiness.
- Mock or offline matrix checks are **integrity scaffolding**, not experimental outcomes.
- Only Phase 4 fresh immutable runs under frozen authorization may upgrade evidence toward Level B per [`../paper/RESULTS_EVIDENCE.md`](../paper/RESULTS_EVIDENCE.md).
