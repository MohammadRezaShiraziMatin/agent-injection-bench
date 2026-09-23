# Level B — Phase 4 prelive checklist (no live execution)

**Document ID:** `aib-level-b-phase4-prelive-v1`  
**Status:** **PRELIVE / AWAITING_KEY** — scaffolding only  
**Evidence level on `main`:** **Level A only** until fresh Level B run IDs exist under `results/level_b_paired/`.

**Do not execute live Level B runs yet.** No OpenRouter calls, no new ASR tables, no promotion of draft manifests to frozen evidence without Matin’s authorization chain.

---

## What is ready (offline)

| Artifact | Path | State |
|----------|------|--------|
| Execution approval (blocked) | `artifacts/level_b_phase4_execution_approval.json` | `AWAITING_KEY`, `authorized: false` |
| Draft population manifest | `artifacts/level_b_primary_d0_d2_experiment/MANIFEST.json` | `DRAFT_NOT_FROZEN` — **candidate** expanded COV-A (23+23) |
| Live eval gate | `config/level_b_live_eval_gate.v1.json` | `live_inference_allowed: false` |
| Protocol freeze stub | `config/level_b_protocol_freeze.v1.json` | `DESIGN_NOT_FROZEN` |
| Model matrix | `config/level_b_model_matrix.v1.json` | `NOT_AUTHORIZED`; second target **CANDIDATE_NOT_LOCKED** |
| Harness Phase 3 | `config/level_b_harness_contract.v1.json` + verifier | Sandbox / trace scaffolding complete |
| Results namespace | `results/level_b_paired/` | Empty placeholder — **no runs** |

**Candidate population (draft, not frozen):** all COV-A episodes in `artifacts/p4_2_coverage_eligibility/ELIGIBILITY.json` — 9 historical primary-eligible + 14 COV-A secondary-eligible (`n=23` attacks). Alternate pool documented in manifest: P3-EXT COV-B (42+42). **RESEARCHER DECISION REQUIRED** before freeze.

**Pairing:** D0 then D2; benign = pair-matched per `config/p4_3_paired_eval_contract.v1.json`.

---

## What Matin must supply before live can flip

1. **OpenRouter API key** — set locally only after sign-off; never commit. Confirm budget and stop rules per [`LIVE_EVAL_GATE.md`](./LIVE_EVAL_GATE.md).
2. **Lock second target model family** — replace `CANDIDATE_NOT_LOCKED_RESEARCHER_DECISION_REQUIRED` in `config/level_b_model_matrix.v1.json` with exact slug, provider order, and catalog snapshot evidence (mirror Level A gate pattern).
3. **Freeze population** — confirm expanded COV-A vs COV-B subset vs hybrid; update manifest to `FROZEN`; record `draft_list_content_sha256` at freeze.
4. **Protocol + SAP (if confirmatory)** — move `config/level_b_protocol_freeze.v1.json` to `FROZEN` only with SAP LOCK and power memo if confirmatory claims are desired; otherwise keep descriptive-only language in authorization.
5. **AdaptiGuard pin** — confirm `config/adaptiguard_version_pin.v1.json` or document supersession at freeze.
6. **Git commit pin** — record SHA in approval when signing.
7. **Human approval fields** — fill `operator`, `approved_at_utc`, set `status` to `EXPLICIT` or `AUTHORIZED`, set `authorized: true` only with complete chain.
8. **Enable gate** — set `config/level_b_live_eval_gate.v1.json` → `preflight.live_inference_allowed: true` **only after** steps 1–7.
9. **Runtime env** — `AIB_LEVEL_B_LIVE_EXECUTION=1` and `OPENROUTER_API_KEY` (see gate JSON).

Immutable Level A runs (`p42-primary-d0-d2-20260921T173736Z-controlled`, `p3-cov-b-ext-20260923T112900Z-controlled`) must **not** be mutated or re-scored as Level B.

---

## Run prelive verifiers (offline, no API key)

```bash
python3 scripts/verify_level_b_phase4_prelive_gate.py
python3 scripts/verify_level_b_model_matrix.py
python3 scripts/verify_level_b_harness_phase3.py
pytest tests/test_level_b_phase4_prelive_gate.py -q
```

Expected: Phase 4 prelive gate **PASS**, model matrix **DESIGN / NOT_AUTHORIZED**, harness Phase 3 **PASS**.

If approval is set to `EXPLICIT` / `authorized: true` without frozen manifest, locked matrix, and gate enablement, `verify_level_b_phase4_prelive_gate.py` must **FAIL** (fail-closed).

---

## Explicit non-claims

- Draft manifest **≠** frozen Level B population  
- Phase 4 prep **≠** Level B evidence or Q1-ready experimental outcomes  
- No ASR numbers from this phase; no relabeling of Level A bundles  

Program context: [`AIB_Q1_STRENGTHENING_4PHASE.md`](./AIB_Q1_STRENGTHENING_4PHASE.md) · Protocol design: [`AIB_LEVEL_B_EXPERIMENTAL_PROTOCOL.md`](./AIB_LEVEL_B_EXPERIMENTAL_PROTOCOL.md)
