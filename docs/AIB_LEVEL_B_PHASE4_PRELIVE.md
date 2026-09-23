# Level B — Phase 4 prelive checklist (no live execution)

**Document ID:** `aib-level-b-phase4-prelive-v1`  
**Status:** **PRELIVE / KEY_RECEIVED_PENDING_AUTH** — lock + freeze complete; live still blocked  
**Evidence level on `main`:** **Level A only** until fresh Level B run IDs exist under `results/level_b_paired/`.

**Do not execute live Level B runs yet.** No OpenRouter inference for Level B benchmarks, no new ASR tables, no relabeling of Level A bundles.

---

## What is ready (offline)

| Artifact | Path | State |
|----------|------|--------|
| Execution approval (blocked) | `artifacts/level_b_phase4_execution_approval.json` | `KEY_RECEIVED_PENDING_AUTH`, `authorized: false` |
| Population manifest | `artifacts/level_b_primary_d0_d2_experiment/MANIFEST.json` | **`FROZEN`** — expanded COV-A (23+23), `live_execution: false` |
| Live eval gate | `config/level_b_live_eval_gate.v1.json` | `live_inference_allowed: false`; second target catalog wired |
| Catalog lock (Gemini) | `artifacts/level_b_openrouter_model_lock_evidence.json` | `google/gemini-2.5-flash` fingerprint |
| Protocol freeze stub | `config/level_b_protocol_freeze.v1.json` | `DESIGN_NOT_FROZEN` (confirmatory SAP not locked) |
| Model matrix | `config/level_b_model_matrix.v1.json` | `NOT_AUTHORIZED`; second target **`LOCKED`** |
| Harness Phase 3 | `config/level_b_harness_contract.v1.json` + verifier | Sandbox / trace scaffolding complete |
| Results namespace | `results/level_b_paired/` | Empty placeholder — **no runs** |

**Frozen population:** expanded COV-A 23+23 (9 historical primary-eligible + 14 COV-A secondary-eligible). Alternate pool documented in manifest: P3-EXT COV-B (42+42) — **not selected**. Freeze rationale recorded in manifest `freeze_rationale`.

**Pairing:** D0 then D2; benign = pair-matched per `config/p4_3_paired_eval_contract.v1.json`.

---

## What Matin must supply before live can flip

1. **Human approval fields** — fill `operator`, `approved_at_utc`, set `status` to `EXPLICIT` or `AUTHORIZED`, set `authorized: true` only with complete chain (not agent-forged).
2. **Enable gate** — set `config/level_b_live_eval_gate.v1.json` → `preflight.live_inference_allowed: true` **only after** sign-off.
3. **Runtime env** — `AIB_LEVEL_B_LIVE_EXECUTION=1` and `OPENROUTER_API_KEY` on the runner (key may exist out-of-band already; that alone does not authorize live).
4. **Protocol + SAP (if confirmatory)** — move `config/level_b_protocol_freeze.v1.json` to `FROZEN` only with SAP LOCK and power memo if confirmatory claims are desired; otherwise keep descriptive-only language in authorization.
5. **AdaptiGuard pin** — confirm `config/adaptiguard_version_pin.v1.json` or document supersession at live authorization.
6. **Git commit pin** — record SHA in approval when signing.

Completed prelive steps (no live flip): second target lock, population freeze, catalog evidence, offline verifier PASS.

Immutable Level A runs (`p42-primary-d0-d2-20260921T173736Z-controlled`, `p3-cov-b-ext-20260923T112900Z-controlled`) must **not** be mutated or re-scored as Level B.

---

## Run prelive verifiers (offline, no API key)

```bash
python3 scripts/verify_level_b_phase4_prelive_gate.py
python3 scripts/verify_level_b_model_matrix.py
python3 scripts/verify_level_b_harness_phase3.py
pytest tests/test_level_b_phase4_prelive_gate.py tests/test_level_b_model_matrix.py -q
```

Expected: Phase 4 prelive gate **PASS**, mode `PRELIVE_LOCKED_FROZEN_AWAITING_LIVE_APPROVAL`, model matrix **DESIGN / NOT_AUTHORIZED**, harness Phase 3 **PASS**, `live_inference_allowed: false`.

If approval is set to `EXPLICIT` / `authorized: true` without gate enablement and operator fields, `verify_level_b_phase4_prelive_gate.py` must **FAIL** (fail-closed).

---

## Explicit non-claims

- Frozen manifest **≠** Level B scored evidence  
- Phase 4 prelive lock/freeze **≠** Q1-ready experimental outcomes  
- No ASR numbers from this phase; no relabeling of Level A bundles  

Program context: [`AIB_Q1_STRENGTHENING_4PHASE.md`](./AIB_Q1_STRENGTHENING_4PHASE.md) · Protocol design: [`AIB_LEVEL_B_EXPERIMENTAL_PROTOCOL.md`](./AIB_LEVEL_B_EXPERIMENTAL_PROTOCOL.md)
