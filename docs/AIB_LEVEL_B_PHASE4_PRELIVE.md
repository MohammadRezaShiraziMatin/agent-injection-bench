# Level B — Phase 4 gate (descriptive live authorized)

**Document ID:** `aib-level-b-phase4-prelive-v1`  
**Status:** **LIVE_AUTHORIZED_DESCRIPTIVE** — operator Matin signed explicit approval; offline gate PASS  
**Evidence level on `main`:** **Level A only** until fresh Level B run IDs exist under `results/level_b_paired/`.

Live OpenRouter inference is **authorized on the operator desktop only** for **descriptive** Level B paired runs. Cloud CI remains offline (no live API calls).

---

## What is ready (offline + authorized live chain)

| Artifact | Path | State |
|----------|------|--------|
| Execution approval | `artifacts/level_b_phase4_execution_approval.json` | `EXPLICIT`, `authorized: true`, approver **Matin** |
| Population manifest | `artifacts/level_b_primary_d0_d2_experiment/MANIFEST.json` | **`FROZEN`** — expanded COV-A (23+23); `live_execution: false` (runtime flag) |
| Live eval gate | `config/level_b_live_eval_gate.v1.json` | `live_inference_allowed: true`; dry-run-before-live still required |
| Protocol freeze | `config/level_b_protocol_freeze.v1.json` | **`FROZEN`**, **`DESCRIPTIVE_ONLY`** (confirmatory SAP out of scope) |
| Model matrix | `config/level_b_model_matrix.v1.json` | **`AUTHORIZED_FOR_DESCRIPTIVE_LIVE`**; Gemini row **`LOCKED`** |
| Catalog lock (Gemini) | `artifacts/level_b_openrouter_model_lock_evidence.json` | `google/gemini-2.5-flash` fingerprint |
| Harness Phase 3 | `config/level_b_harness_contract.v1.json` + verifier | Sandbox / trace scaffolding complete |
| Results namespace | `results/level_b_paired/` | Empty placeholder — **no runs yet** |
| Operator runbook | `docs/AIB_LEVEL_B_LIVE_RUN.md` | Desktop live commands |

**Frozen population:** expanded COV-A 23+23. Pairing: D0 then D2; benign = pair-matched per `config/p4_3_paired_eval_contract.v1.json`.

OpenRouter key: present on Matin desktop `.env` (out-of-band); agents never saw the value.

Immutable Level A runs (`p42-primary-d0-d2-20260921T173736Z-controlled`, `p3-cov-b-ext-20260923T112900Z-controlled`) must **not** be mutated or re-scored as Level B.

---

## Run verifiers (offline, no API key)

```bash
python3 scripts/verify_level_b_phase4_prelive_gate.py
python3 scripts/verify_level_b_model_matrix.py
python3 scripts/verify_level_b_harness_phase3.py
pytest tests/test_level_b_phase4_prelive_gate.py tests/test_level_b_model_matrix.py -q
```

Expected: Phase 4 gate **PASS**, mode **`LIVE_AUTHORIZED_DESCRIPTIVE`**, `live_inference_allowed: true`, matrix **`live_execution_authorized: true`**.

Incomplete authorization (e.g. `authorized: true` without `EXPLICIT` status or missing `authorization_record`) must **FAIL** (`PRELIVE_PARTIAL_FAIL_CLOSED`).

---

## Explicit non-claims

- Authorization **≠** Level B scored evidence until run IDs exist under `results/level_b_paired/`  
- Descriptive live **≠** confirmatory / SAP-powered Q1 generalization  
- No ASR numbers from gate artifacts alone; no relabeling of Level A bundles  

Program context: [`AIB_Q1_STRENGTHENING_4PHASE.md`](./AIB_Q1_STRENGTHENING_4PHASE.md) · Live commands: [`AIB_LEVEL_B_LIVE_RUN.md`](./AIB_LEVEL_B_LIVE_RUN.md)
