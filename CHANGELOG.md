# CHANGELOG

## Unreleased — documentation standardization

- Canonical research docs under `docs/` (START_HERE, THREAT_MODEL, TAXONOMY, BENCHMARK, DATASET, EVALUATION, REPRODUCIBILITY, EXPERIMENT_PROTOCOL, CLAIMS, LIMITATIONS, ADAPTI_GUARD_BRIDGE)
- Paper workspace under `paper/` (outline, claims checklist, figures/tables placeholders)
- Root `README.md` shortened to entry point; `STATUS.md` updated
- Superseded scattered root/phase docs removed after merge (see git history)
- Code references updated to `docs/` paths; behavior unchanged

## Prior baseline (eval layer)

- Phase C multi-model×D0/D1 matrix scripts, ASR-L0/L1, twin dataset, D0/D1 prompts, trace metadata (`git_head`, latency, tokens)
- Content fingerprint: manifests include `dataset_version`

## Future — D2 / ADAPTI-GUARD

- Not implemented in this repository. External runner contract: [docs/ADAPTI_GUARD_BRIDGE.md](docs/ADAPTI_GUARD_BRIDGE.md).
