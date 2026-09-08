# CONTRIBUTING

## Setup

```bash
python -m venv .venv
# activate, then:
python -m pip install -e ".[dev]"
```

## Tests / validation

```bash
python scripts/validate_episodes.py
python -m pytest
```

Default contribution path is **offline** (no API keys).

## Policies

- **No secrets** in git (`.env` ignored; use `.env.example` names only)
- **No live LLM** in CI or default PR checks
- Do not commit `results/traces/**/*.json` or manifests with secrets
- Do not invent ASR/utility/CI numbers
- Do not implement Adaptive/D2 in this repository
- Do not claim D1 is production-ready or universally strong

## Experiment artifacts

- Write under `results/traces/<run_id>/` and `results/manifests/`
- Prefer `--dry-run` for harness smoke tests

## Commits

- Small, focused commits; English messages
- Do not rewrite shared history or force-push `main` without explicit agreement
