# Phase 5 — Research Decision Sheet (read-only inventory)

**Type:** Decision support only — no values chosen by automation.  
**Repository HEAD at authoring:** inspect `git rev-parse HEAD` before use.  
**PRELIVE_GATE:** FAIL until rows below are frozen by researcher.  
**Live execution:** forbidden until gate PASS.

---

## Decision table

| ID | Research decision | Current state | Evidence | Decision required | Blocks live? |
|----|-------------------|---------------|----------|-------------------|--------------|
| D1 | H3 FPR tolerance τ | **UNRESOLVED** — no numeric τ in AIB contracts | `docs/AIB_RESEARCH_CONTROLLED_DEFENSE_EXPERIMENT_SPEC.md` §2 H3 («pre-registered tolerance» without value); not in `config/p4_3_paired_eval_contract.v1.json` or primary MANIFEST | Researcher | **YES** |
| D2 | Primary population | **MISMATCH** spec vs primary design manifest | Spec §2–4: H1–H3 on **COV-A ∪ COV-B**; `artifacts/p4_2_primary_d0_d2_experiment/MANIFEST.json`: **9 attack + 9 benign, COV-A only** (`coverage.primary`: COV-A only) | Researcher | **YES** |
| D3 | Primary endpoint | **MULTIPLE DVs, no single confirmatory primary frozen** | RQ lists ASR/S1/S2/S3/S4/Utility/FPR; H1→ASR; H2→S2/S3/S4; H3→Utility/FPR; primary MANIFEST: `descriptive_paired`, no primary endpoint field | Researcher | **YES** |
| D4 | Sample size (confirmatory) | **UNRESOLVED** — n=9 design only | `artifacts/p4_2_primary_d0_d2_experiment/MANIFEST.json` `statistical_interpretation.primary_attack_n`: 9, `analysis`: descriptive_paired; no power/rationale for confirmatory | Researcher | **YES** |
| D5 | Repetition policy | **UNRESOLVED** | `config/p4_3_paired_eval_contract.v1.json` holds `seed_policy` in gate generation; no repetition count / episode reuse policy in contract | Researcher | **YES** |
| D6 | Statistical test (confirmatory) | **DEFAULT descriptive only** | Spec §6: descriptive/paired; optional tests only if pre-registered; `docs/P4_2_PRIMARY_STATISTICAL_ANALYSIS_PROMPT.fa.md` mentions McNemar/exact but **no repo script**; scorer: descriptive only | Researcher | **YES** if formal inference claimed |
| D7 | H3 Utility/FPR rule freeze | **Partial** — definitions yes, τ and claim type no | `config/p4_3_evaluation_metrics.v1.json` Utility/FPR denominators; `config/p4_3_paired_eval_contract.v1.json` FPR; H3 inequality not automated in scorer | Researcher | **YES** |
| D8 | Adaptive confirmatory protocol | **BLOCKED** — not AIB D0/D2 unified gate | `docs/AIB_P4_3_COMPLETION_REPORT.md`: LIVE_ADAPTIVE **not implemented**; `external/adapti-guard/` Track A/B separate (B0/CORE/ADAPT ≠ D0/D2) | Researcher | **YES** if adaptive confirmatory |
| D9 | Model matrix | **LOCKED single pair for P4.3 gate**; Qwen3 absent | `config/p4_3_live_eval_gate.v1.json`: `openai/gpt-4o-mini-2024-07-18` + `meta-llama/llama-3.3-70b-instruct`; no Qwen3 in repo grep | Researcher | **YES** if multi-model study |
| D10 | Endpoint hierarchy (H1 vs H2 vs H3) | **UNRESOLVED** for confirmatory precedence | Spec table §2; no pre-registered primary vs secondary hierarchy in manifest | Researcher | **YES** |

---

## B1 — H3 τ (detector vs FPR)

| Question | Answer (evidence) |
|----------|-------------------|
| Numeric H3 τ defined? | **No** |
| `0.25` meaning | Detector coverage calibration threshold (`docs/AIB_COVERAGE_AWARE_EVALUATION_PROTOCOL.md` §1) — **not** H3 FPR tolerance |
| `0.60` in repo | AdaptiGuard Track B detector config (`external/adapti-guard/docs/paper/dual_track/DUAL_TRACK_STATUS.md`) — **not** AIB H3 τ |
| Conflation risk | Docs separate concepts; automation does not map 0.25/0.60 to H3 |

---

## B2 — Population

```text
SPEC POPULATION:     COV-A ∪ COV-B (H1–H3); COV-C excluded (diagnostic)
MANIFEST POPULATION: COV-A only, PRIMARY_ELIGIBLE, n=9 attacks + 9 matched benigns
ACTUAL PRIMARY POOL: 9×COV-A per artifacts/p4_2_primary_d0_d2_experiment/MANIFEST.json
MATCH:               NO (COV-B not in primary pool; spec union ≠ manifest subset)
```

P4.4 / P4.4 v2: frozen validation corpora — **not** designated as P4.2 primary substitute in primary MANIFEST.

---

## B3 — Primary endpoint

- **RQ:** multi-outcome (ASR/S1, S2, S3, S4, Utility, FPR).
- **Confirmatory primary endpoint:** **UNRESOLVED — RESEARCHER DECISION REQUIRED.**

---

## B4–B6 — Sample size, repetition, statistics

- **n today:** 9 primary attacks (design manifest); benign utility/FPR scope: 9 matched benigns.
- **Confirmatory n / power:** **UNRESOLVED.**
- **Repetition:** **UNRESOLVED.**
- **Confirmatory test:** spec default **descriptive**; formal test **STATISTICAL DECISION REQUIRED** if non-descriptive claim intended.

---

## B8 — Adaptive

```text
ADAPTIVE CONFIRMATORY GATE = BLOCKED
```

(AIB harness: no frozen adaptive confirmatory pack + gate for Strong Model × Adaptive × D0/D2; AG tracks are separate contracts.)

---

## B9 — Models

- **Locked (P4.3 live gate):** GPT-4o-mini target, Llama-3.3-70B judge (OpenRouter).
- **Qwen3:** not defined in AIB repository.

---

## B10 — Weight revision

- `upstream_weight_revision`: **UNVERIFIED** / `weight_revision_provable: false` in `config/p4_3_live_eval_gate.v1.json` and `verify_model_lock.py` — preserve unless new **provable** evidence added.

---

## Gate status (unchanged)

```text
PHASE 5 = BLOCKED
PRELIVE_GATE = FAIL
RESEARCHER DECISION REQUIRED
LIVE EXECUTION = NOT EXECUTED
```
