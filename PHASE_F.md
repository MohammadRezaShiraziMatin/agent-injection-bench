# PHASE_F — Reproducibility

## Environment

- Python ≥ 3.10 (see `pyproject.toml`)
- OS: documented by the runner (Windows / Linux / WSL)

## Dependencies

```bash
python -m pip install -e ".[dev]"
```

Prefer locking versions in the runner’s environment report (pip freeze). No lockfile is mandated in-repo yet.

## Commit / baseline

- Intended content baseline: `7ec8eb7b6f6e9671a9de653670f16fcf01bcf5de`
- Every manifest and trace should record **`git_head`** actually used at run time

## Dataset version

- Episode files under `data/episodes/`
- Manifest includes `dataset_version` / fingerprint helpers in `agent/traces.py`

## Model / version

- Record `model`, `base_url` / provider, API date if known
- Provider model strings can change behavior without id changes — note run date

## Configuration

- `.env` from `.env.example` (never commit secrets)
- Temperature, seed, max_steps, timeout, prompt_id / defense_condition

## Seed caveats

- Seed is **best-effort** on OpenAI-compatible APIs
- Configuring a seed does **not** guarantee bit-identical outputs

## API nondeterminism

- Retries, load balancing, and silent model updates can change results
- Distinguish `execution_status=error` (API/harness failure) from model refusals / non-tool answers

## Commands (offline)

```bash
python scripts/validate_episodes.py
python -m pytest
python scripts/run_agent.py --id atk_002 --dry-run --no-write
```

## Artifact structure

```
results/traces/<run_id>/<episode_id>.json
results/manifests/<run_id>.json
```

Traces are gitignored; keep manifests/traces for audit outside git or via approved release bundles.
