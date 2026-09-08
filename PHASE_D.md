# PHASE_D — Adaptive evaluation design (NOT IMPLEMENTED)

Adaptive / **D2** remains **external**. This document defines the interface only. **No Adaptive code, no Adaptive results.**

## Status

**NOT IMPLEMENTED** in agent-injection-bench.

## Intent

Evaluate an external adaptive defense (e.g. ADAPTI-GUARD) as **D2** against the same frozen episodes and trace schema used for D0/D1.

## Inputs (future)

- Episode JSON conforming to `schema/episode.schema.json`
- Same tool names: `search_docs`, `send_email`
- Config: model, temperature, seed (best-effort), `prompt_id`/`defense_condition=d2`

## Outputs (future)

- Traces under `results/traces/<run_id>/` with the same fields as D0/D1 (`run_id`, `git_head`, `latency_ms`, `tokens`, …)
- Manifest under `results/manifests/<run_id>.json`

## Evaluation interface

1. External runner executes episodes and writes compatible traces.
2. Score with existing `score_asr.py` / `score_utility.py` / `aggregate_phase_c.py`.
3. Compare D0 vs D1 vs D2 **only** when each cell has live non-error evidence.

## Integration point

See [`docs/D2_EXTERNAL_ADAPTI.md`](docs/D2_EXTERNAL_ADAPTI.md) and [`ADAPTI_GUARD_BRIDGE.md`](ADAPTI_GUARD_BRIDGE.md). Do not fork the episode schema for defense-only fields without a version bump.

## Forbidden

- Shipping Adaptive implementation in this repo under Phase D docs
- Inventing Adaptive ASR/utility numbers
