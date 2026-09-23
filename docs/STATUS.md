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
| 2 | Multi-model matrix scaffolding | **Complete on `main`** — [`AIB_LEVEL_B_MODEL_MATRIX.md`](AIB_LEVEL_B_MODEL_MATRIX.md) (`DESIGN` / `NOT_AUTHORIZED`) |
| 3 | Realistic harness & D2 trace coverage | **Complete (scaffolding)** — [`AIB_LEVEL_B_HARNESS_PHASE3.md`](AIB_LEVEL_B_HARNESS_PHASE3.md) |
| 4 | Fresh immutable Level B live runs | **Prep in progress** — [`AIB_LEVEL_B_PHASE4_PRELIVE.md`](AIB_LEVEL_B_PHASE4_PRELIVE.md) (`AWAITING_KEY`; no live API) |

Level A runs remain the only scored research evidence until Phase 4 **live** execution completes. Prelive scaffolding (approval JSON, draft manifest, offline gate) does not add Level B evidence. Gap context: [`AIB_P2_Q1_EVIDENCE_GAP_PLAN.md`](AIB_P2_Q1_EVIDENCE_GAP_PLAN.md).

**v0 harness (optional, separate from Level B):**

1. `origin auth login` (WSL) **or** create a GitHub remote and push
2. Add `.env` with a key and run `run_batch.py` only after [LIVE_EVAL_GATE.md](./LIVE_EVAL_GATE.md) sign-off
3. Score with `score_asr.py` / `score_utility.py` and record rates only from that output
