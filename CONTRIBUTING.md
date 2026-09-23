# Contributing

## Before a pull request

1. `pip install -e ".[dev]"`
2. `pytest -q`
3. `git diff --check` for text files you edited

## Research integrity

- Do **not** modify frozen protocols, immutable historical `results/` trees, or scored primary evidence without maintainer authorization and a **new** protocol/run ID.
- Do **not** commit API keys or live credentials.
- Do not enable live D2 inference in CI or default gate configs.

See `docs/AIB_SCIENTIFIC_INTEGRITY_AUDIT.md` and `docs/AIB_REPRODUCIBILITY_INDEX.md`.

## Scope

Harness, schema, offline verifiers, and documentation fixes are welcome. Metric or population changes that affect published claims require new frozen manifests and new runs—not edits to existing evidence.

Use the pull request template checklist.
