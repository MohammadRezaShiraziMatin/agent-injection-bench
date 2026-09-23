# Q1 Strengthening — Four-Phase Program (Planning)

**Document ID:** `aib-q1-strengthening-4phase-v1`  
**Status:** **Phase 4 prep in progress (prelive gates & draft manifest)** — **no live execution authorized**  
**Current evidence level on `main`:** **Level A only** (descriptive paired runs; not Q1-ready)

**Honest baseline (do not relabel):**

| Layer | Run ID | Role |
|-------|--------|------|
| P4.2 primary (COV-A) | `p42-primary-d0-d2-20260921T173736Z-controlled` | n=9 attack + 9 benign; single target model; mock tools; descriptive D0/D2 |
| P3-EXT (COV-B) | `p3-cov-b-ext-20260923T112900Z-controlled` | Descriptive extension; **does not** satisfy Level B by itself |

Level A bundles above are **immutable**. Phases 1–3 produce **no new ASR numbers**. Phase 4 alone may add **fresh** Level B run IDs under a new namespace.

**Related docs:**

- Gap audit: [`AIB_P2_Q1_EVIDENCE_GAP_PLAN.md`](./AIB_P2_Q1_EVIDENCE_GAP_PLAN.md)
- Level B protocol (DESIGN): [`AIB_LEVEL_B_EXPERIMENTAL_PROTOCOL.md`](./AIB_LEVEL_B_EXPERIMENTAL_PROTOCOL.md)
- Level B model matrix (DESIGN): [`AIB_LEVEL_B_MODEL_MATRIX.md`](./AIB_LEVEL_B_MODEL_MATRIX.md)
- P8 skeleton: [`AIB_P8_FUTURE_EXPERIMENT_PROTOCOL_DRAFT.md`](./AIB_P8_FUTURE_EXPERIMENT_PROTOCOL_DRAFT.md)
- Claim ladder: [`../paper/RESULTS_EVIDENCE.md`](../paper/RESULTS_EVIDENCE.md)

---

## Dependency order

```text
Phase 1 (protocol & population design)
    → Phase 2 (multi-model matrix scaffolding)
        → Phase 3 (realistic harness + D2 trace coverage)
            → Phase 4 (fresh immutable live evidence)
```

Each phase **blocks** the next until its exit criteria are met. Skipping phases does not upgrade claim level.

---

## Phase 1 — Level B protocol & population design

**Scope (this PR):** Pre-registered research question, estimands, endpoints, gates, and claim boundaries. **DESIGN only** — no dataset freeze, no live API calls, no changes under `results/`.

**Deliverables:**

- [`AIB_LEVEL_B_EXPERIMENTAL_PROTOCOL.md`](./AIB_LEVEL_B_EXPERIMENTAL_PROTOCOL.md) (`STATUS=DESIGN`)
- This four-phase roadmap
- Entry-point links in [`STATUS.md`](./STATUS.md), [`CLAIMS_MAP.md`](./CLAIMS_MAP.md), [`START_HERE.md`](./START_HERE.md)
- Optional stub [`../config/level_b_protocol_freeze.v1.json`](../config/level_b_protocol_freeze.v1.json) with `DESIGN_NOT_FROZEN` (not execution-ready)

**Exit criteria:**

- [x] RQ, estimands, primary/secondary endpoints, and forbidden claims documented and cross-linked to Level A freezes
- [x] Explicit rule: new Level B runs use **new run IDs**; P4.2 primary and P3-EXT bundles untouched
- [x] Researcher decision placeholders retained (sample size, model matrix, confirmatory SAP) — **no fabricated power or model IDs**
- [x] `PROTOCOL FREEZE` / `SAP LOCK` gates defined in Level B doc (inactive until later phases)

**Phase 1 status on `main`:** **Complete** (merged PR #18, tip `d571493`).

**Explicit non-claims after Phase 1:**

- No Level B evidence exists yet
- No Q1-readiness, superiority, SOTA, or defense-efficacy claims
- No new metrics or ASR tables from this phase

---

## Phase 2 — Multi-model matrix scaffolding

**Scope:** Lock **≥2 target model families** in config, manifests, and offline verifiers (pins, gate checks, CI integrity hooks). Still **no live claims** until Phase 4 runs complete.

**Intent:** Close the “single model on primary” gap identified in the gap plan without re-scoring or rewriting Level A history.

**Deliverables (Phase 2):**

- [`AIB_LEVEL_B_MODEL_MATRIX.md`](./AIB_LEVEL_B_MODEL_MATRIX.md) + [`../config/level_b_model_matrix.v1.json`](../config/level_b_model_matrix.v1.json) (`DESIGN` / `NOT_AUTHORIZED`)
- [`../scripts/verify_level_b_model_matrix.py`](../scripts/verify_level_b_model_matrix.py) — offline structure, fingerprint, and false-lock guards
- Protocol freeze stub pointer: `inherits_read_only.level_b_model_matrix` in [`../config/level_b_protocol_freeze.v1.json`](../config/level_b_protocol_freeze.v1.json)

**Run verifier (offline, no API):**

```bash
python3 scripts/verify_level_b_model_matrix.py
```

Research CI invokes the same script when present (`.github/workflows/research-ci.yml`).

**Exit criteria:**

- [x] Model matrix documented and referenced from frozen-ready config (status remains `DESIGN` until Phase 4 authorization)
- [x] Offline verifiers fail on drift from approved matrix definition (content fingerprint + Level A gate cross-check)
- [x] No execution authorization artifacts; no new directories under `results/` presented as Level B evidence

**Explicit non-claims after Phase 2:**

- Scaffolding alone does **not** establish cross-model ASR or generalization
- Mock-tool or dry-run matrix checks are **not** experimental outcomes

---

## Phase 3 — Realistic harness & D2 hook coverage

**Scope:** Controlled tool sandbox (beyond offline mocks where the protocol specifies), per-step defense traces, and D2 integration coverage aligned with [`ADAPTI_GUARD_BRIDGE.md`](./ADAPTI_GUARD_BRIDGE.md) — while **keeping the paired scoring contract** (`config/p4_3_paired_eval_contract.v1.json`, `scripts/score_p4_3_paired_metrics.py`).

**Deliverables (Phase 3):**

- [`AIB_LEVEL_B_HARNESS_PHASE3.md`](./AIB_LEVEL_B_HARNESS_PHASE3.md) — loop, mock vs sandbox realism, hook map, deferred gaps
- [`../config/level_b_harness_contract.v1.json`](../config/level_b_harness_contract.v1.json) (`DESIGN_NOT_FROZEN`)
- Tool sandbox [`../tools/tool_sandbox.py`](../tools/tool_sandbox.py) + D2 hook trace [`../agent/defense/hook_trace.py`](../agent/defense/hook_trace.py)
- Offline tests [`../tests/test_level_b_harness_phase3.py`](../tests/test_level_b_harness_phase3.py) + [`../scripts/verify_level_b_harness_phase3.py`](../scripts/verify_level_b_harness_phase3.py)

**Run verifier (offline, no API):**

```bash
python3 scripts/verify_level_b_harness_phase3.py
pytest tests/test_level_b_harness_phase3.py -q
```

**Exit criteria:**

- [x] Harness adapter coverage documented (episode classes, tool paths, trace fields required for judgment)
- [x] D2 hook invocation traceable on approved execution paths in **test/sandbox** settings
- [x] Gap list vs Level B protocol § harness requirements closed or explicitly deferred with researcher sign-off
- [x] Still no Level B run IDs promoted to evidence without Phase 4

**Explicit non-claims after Phase 3:**

- Sandbox realism does **not** prove production security or benchmark completeness
- Trace shape tests are **not** ASR/utility results for publication tables

---

## Phase 4 — Fresh immutable live evidence

**Scope:** Execute pre-authorized runs under **Level B namespace** (new `run_id`s, new manifests, approval JSON + live eval gate + API key). Analyze per locked SAP only after `PROTOCOL FREEZE` and `EXECUTION AUTHORIZATION`.

**Phase 4 prep (current — no live API):**

- [`AIB_LEVEL_B_PHASE4_PRELIVE.md`](./AIB_LEVEL_B_PHASE4_PRELIVE.md) — operator checklist; **do not execute live yet**
- `artifacts/level_b_phase4_execution_approval.json` — `AWAITING_KEY` / not authorized
- `artifacts/level_b_primary_d0_d2_experiment/MANIFEST.json` — draft candidate population (`DRAFT_NOT_FROZEN`)
- `config/level_b_live_eval_gate.v1.json` — fails closed (`live_inference_allowed: false`)
- `scripts/verify_level_b_phase4_prelive_gate.py` — offline prelive verifier (CI)

**Run prelive verifier (offline):**

```bash
python3 scripts/verify_level_b_phase4_prelive_gate.py
```

**Exit criteria (live execution — not started):**

- [ ] New immutable bundles under a Level B path (analogous to P4.2/P3 patterns) with manifest hash and provenance
- [ ] Scoring via existing paired contract; results recorded in evidence index without mutating Level A SHA artifacts
- [ ] Claim upgrade to Level B only where [`RESULTS_EVIDENCE.md`](../paper/RESULTS_EVIDENCE.md) and frozen SAP allow — not by narrative relabeling

**Explicit non-claims (default until SAP + evidence say otherwise):**

- Level B **≠** Level C (broad replication, large-scale human IAA, adaptive campaigns as primary)
- One Level B study **≠** Q1 venue acceptance
- Descriptive extensions (e.g. P3-EXT alone) **≠** Level B

---

## Program-level forbidden claims (all phases)

Until Phase 4 completes with frozen authorization:

- Defense **effectiveness**, **superiority**, or **robust** protection
- **SOTA**, **production-ready**, or **comprehensive** benchmark coverage
- **Statistical significance** or population inference from n=9 primary or descriptive extensions alone
- **Q1-ready** or submission-ready experimental evidence

Allowed throughout: honest Level A citations with run IDs, protocol design status, gap documentation, and v0 scaffold behavior (see [`CLAIMS_MAP.md`](./CLAIMS_MAP.md)).

---

## Program status (tracking)

| Item | State |
|------|--------|
| Four-phase plan | **This document** |
| Phase 1 — Level B protocol | **Complete on `main`** — [`AIB_LEVEL_B_EXPERIMENTAL_PROTOCOL.md`](./AIB_LEVEL_B_EXPERIMENTAL_PROTOCOL.md) (`DESIGN`) |
| Phase 2 — Model matrix | **Complete on `main`** — [`AIB_LEVEL_B_MODEL_MATRIX.md`](./AIB_LEVEL_B_MODEL_MATRIX.md) + verifier |
| Phase 3 — Realistic harness & D2 traces | **Complete (scaffolding)** — [`AIB_LEVEL_B_HARNESS_PHASE3.md`](./AIB_LEVEL_B_HARNESS_PHASE3.md) |
| Phase 4 — Prelive gates & draft manifest | **In progress** — [`AIB_LEVEL_B_PHASE4_PRELIVE.md`](./AIB_LEVEL_B_PHASE4_PRELIVE.md) |
| Config freeze stub | `DESIGN_NOT_FROZEN` — not authorized for runs |
| Live execution | **Not authorized** — awaiting API key + researcher lock/freeze |
| Level A runs | **Immutable** |

**Next step for Matin:** complete prelive checklist in [`AIB_LEVEL_B_PHASE4_PRELIVE.md`](./AIB_LEVEL_B_PHASE4_PRELIVE.md) before any live Level B run.
