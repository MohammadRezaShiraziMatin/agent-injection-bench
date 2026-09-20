# Reproducibility

## Minimum offline reproduce

```bash
python -m pip install -e ".[dev]"
python scripts/validate_episodes.py
python -m pytest
python scripts/run_agent.py --id atk_002 --dry-run --no-write
```

## Environment

- Python ≥ 3.10 (`pyproject.toml`)
- Dependencies: editable install with `[dev]` (pytest, jsonschema)
- Prefer documenting `pip freeze` for live cells; no lockfile mandated in-repo

## What to record for a live cell

- `git_head` on trace and manifest
- Model, `base_url`, provider, run date
- `temperature`, `seed` (configured; note if provider ignores seed)
- `prompt_id` / **defense condition** (D0, D1, or external D2 label)
- `dataset_version` / fingerprint from manifest
- `run_id`, timestamp
- `latency_ms` (measured live); `tokens` (provider or null)
- Scorer commands and ASR level (L0/L1)

## Artifact layout

```
results/traces/<run_id>/<episode_id>.json
results/manifests/<run_id>.json
```

Traces and generated summaries are gitignored. Preserve bundles for audit outside the repo or via approved releases.

## Non-guarantees

- Seed configured ≠ bit-identical outputs across providers or API versions
- Silent model backend changes can alter behavior
- Distinguish `execution_status=error` (harness/API) from refusals or benign non-tool answers

## CI

`.github/workflows/ci.yml`: validate episodes + pytest with empty API keys (offline only).

See also [EXPERIMENT_PROTOCOL.md](./EXPERIMENT_PROTOCOL.md).
