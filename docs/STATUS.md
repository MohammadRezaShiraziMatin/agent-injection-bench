# Status

**Entry:** [START_HERE.md](./START_HERE.md) · **Claims:** [CLAIMS_MAP.md](./CLAIMS_MAP.md) · **Claim ladder:** [`../paper/RESULTS_EVIDENCE.md`](../paper/RESULTS_EVIDENCE.md)

## Research evidence (P4.2 / P3-EXT)

**Current claim level: Level A** (descriptive paired evaluation; immutable tracked runs).

- **P4.2 primary (COV-A):** `p42-primary-d0-d2-20260921T173736Z-controlled` — 9 attack + 9 benign.
- **P3-EXT (COV-B):** `p3-cov-b-ext-20260923T112900Z-controlled` — 42 attack + 42 benign per D0/D2 file; descriptive extension only; **not** Level B by itself.

Level B needs a new experimental protocol and fresh immutable evidence. Gap plan: [`AIB_P2_Q1_EVIDENCE_GAP_PLAN.md`](AIB_P2_Q1_EVIDENCE_GAP_PLAN.md). Evidence / claim index: [`../paper/RESULTS_EVIDENCE.md`](../paper/RESULTS_EVIDENCE.md).

---

**v0 scaffold:** complete (data + harness + scorers + tests).  
**v0 evaluation numbers:** none from v0 traces alone; research ASR/utility/FPR come only from scored P4.2/P3 paired runs above.

| Area | State |
|------|--------|
| Schema | Frozen draft-07 |
| Episodes | 20 attack + 20 benign + 2 examples |
| Harness | Phase 2 tool loop (max 6 steps) |
| Defenses | Intentionally absent |
| ASR / utility | Scorer code only; rates require traces |
| False-refusal | N/A |

## Recreated locally

This Desktop tree was **reimplemented from the recovered v0 specification** (cloud Origin HEAD `6d6eaf58` was not clonable from native Windows without Origin auth). Behavior and IDs match the spec; prose may differ from the private Origin copy.

## Next

**Q1 strengthening (Level B path):** Four-phase program — [`AIB_Q1_STRENGTHENING_4PHASE.md`](AIB_Q1_STRENGTHENING_4PHASE.md).

| Phase | Focus | Status |
|-------|--------|--------|
| 1 | Level B protocol & population design (no execution) | **Complete on `main`** — [`AIB_LEVEL_B_EXPERIMENTAL_PROTOCOL.md`](AIB_LEVEL_B_EXPERIMENTAL_PROTOCOL.md) (`DESIGN`) |
| 2 | Multi-model matrix scaffolding | **Descriptive live authorized on `main`** — [`AIB_LEVEL_B_MODEL_MATRIX.md`](AIB_LEVEL_B_MODEL_MATRIX.md) (second target **LOCKED**; matrix `AUTHORIZED_FOR_DESCRIPTIVE_LIVE`) |
| 3 | Realistic harness & D2 trace coverage | **Complete (scaffolding)** — [`AIB_LEVEL_B_HARNESS_PHASE3.md`](AIB_LEVEL_B_HARNESS_PHASE3.md) |
| 4 | Fresh immutable Level B live runs | **Descriptive live scored (lean tracked artifacts)** — [`AIB_LEVEL_B_PHASE4_PRELIVE.md`](AIB_LEVEL_B_PHASE4_PRELIVE.md) · runbook [`AIB_LEVEL_B_LIVE_RUN.md`](AIB_LEVEL_B_LIVE_RUN.md) · index [`../artifacts/level_b_descriptive_live/INDEX.json`](../artifacts/level_b_descriptive_live/INDEX.json) |

Phase 4 **DESCRIPTIVE_ONLY** live paired runs (scored with `scripts/score_p4_3_paired_metrics.py` at git `b22dfbfa903a7eca9fbe0e19f75a50266150fcf6`):

- `level-b-primary-d0-d2-20260923T164727Z-controlled-level_a_primary` — `openai/gpt-4o-mini-2024-07-18` · matrix `target-level-a-primary`
- `level-b-primary-d0-d2-20260923T165457Z-controlled-candidate_family_b` — `google/gemini-2.5-flash` · matrix `target-candidate-family-b`

Lean scored bundles: [`artifacts/level_b_descriptive_live/`](../artifacts/level_b_descriptive_live/) (full traces remain operator-local under `results/level_b_paired/`). **Claim class remains DESCRIPTIVE_ONLY** — gate authorization ≠ confirmatory inference; no SAP / Q1-ready claim; Level A immutable runs and `data/episodes_*` must not be mutated. Level A remains the cited primary descriptive package for manuscript evidence; Level B pilot runs are a separate layer. Operator timeline (no traces): [`OPERATOR_HISTORY_LEVEL_B_2026-09-23.md`](OPERATOR_HISTORY_LEVEL_B_2026-09-23.md) · workshop paste-in prose: [`../paper/WORKSHOP_DESCRIPTIVE_LEVEL_B.md`](../paper/WORKSHOP_DESCRIPTIVE_LEVEL_B.md). Gap context: [`AIB_P2_Q1_EVIDENCE_GAP_PLAN.md`](AIB_P2_Q1_EVIDENCE_GAP_PLAN.md).

**v0 harness (optional, separate from Level B):**

1. `origin auth login` (WSL) **or** create a GitHub remote and push
2. Add `.env` with a key and run `run_batch.py` only after [LIVE_EVAL_GATE.md](./LIVE_EVAL_GATE.md) sign-off
3. Score with `score_asr.py` / `score_utility.py` and record rates only from that output
