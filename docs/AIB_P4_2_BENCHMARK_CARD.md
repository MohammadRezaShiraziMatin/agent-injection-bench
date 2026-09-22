# AIB P4.2 Benchmark Card

## Distinction

| Layer | Responsibility | Artifacts |
|-------|----------------|-----------|
| **Dataset (P4.2)** | Episode definitions, taxonomy, expected success semantics | `data/episodes_p4_2/`, `schema/episode.v2.json` |
| **Execution adapter** | Map episodes → LLM + tool environment | `agent/loop.py` (v0 scope) |
| **Evaluation protocol** | Scoring, manifests, defenses | P7 docs (`docs/AIB_P7_EVALUATION_PROTOCOL.md` on evaluation branches) |
| **Defense** | D0 / D1 / D2 external to dataset | Not embedded in episodes |

## Benchmark task (conceptual)

For each episode, run the target agent under a declared defense condition, record tool calls and answers, score against `expected.success_criterion` (S0–S4) and benign utility fields.

## Dataset version for benchmark runs

Use manifest digest:

`416264027c5e1f57a2a77f8ca31009f1b6ce399eddc1792a3dc8737ec75e74b3`

## Metrics (from P7; not redefined here)

- Attack success rate (pair-aware)
- Benign utility
- ASR variants by family (after adapter coverage improves)

## Splits

- Tune generators / adapters on `development` only
- Validation for protocol checks
- `test` immutable after freeze

## Current execution scope

Harness v0 fully exercises **34** attack episodes (EXECUTABLE). Remaining episodes require adapter work documented in `docs/AIB_P4_2_EXECUTABILITY_MATRIX.md` before live benchmark claims.

## What this card does not include

- Model identifiers (P7.2 OPEN)
- AdaptiGuard live results
- Frozen P4.2 release tag

## Reproducibility checklist

1. Verify P4.2 MANIFEST digest
2. Run `python scripts/qc_p4_2.py`
3. Pin harness + adapter version when executing live eval (future phase)
