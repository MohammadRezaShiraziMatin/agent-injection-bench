# CHANGELOG

## Baseline

- **Origin / content baseline:** `7ec8eb7b6f6e9671a9de653670f16fcf01bcf5de` — Phase C multi-model×D0/D1 matrix, D2 hook docs, CI aggregator, ASR-L0/L1, twin dataset, D0/D1 prompts.

Note: a separate GitHub `main` tip may historically show an earlier scaffold SHA; treat **7ec8eb7** as the scientific baseline for this publication-readiness work.

## Unreleased — publication readiness / hygiene (working tree)

- Expand `.gitignore`; add `.cursorignore`, `.gitattributes`
- Trace fields: `git_head`, `latency_ms`, `tokens` (null when unobserved), `status` alias, `episode`
- Provider usage extraction when present (`agent/llm.py`)
- Docs: `METHODS.md`, `DATA_CARD.md`, `MODEL_CARD.md`, `EXPERIMENT_PROTOCOL.md`, `REPRODUCIBILITY.md`, `PHASE_D.md`–`PHASE_G.md`, `CONTRIBUTING.md`, `CHANGELOG.md`
- Align `README.md` / `STATUS.md` with ASR-L1 and Phase C D0/D1 scope (no overclaim)
- Minimal GitHub Actions CI (offline tests/validation)

## Future — Adaptive / D2

- Not implemented. See `PHASE_D.md`. No Adaptive results in this changelog entry.
