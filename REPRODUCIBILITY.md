# REPRODUCIBILITY

See also `PHASE_F.md`.

## Minimum offline reproduce

```bash
python -m pip install -e ".[dev]"
python scripts/validate_episodes.py
python -m pytest
python scripts/run_agent.py --id atk_002 --dry-run --no-write
```

## What must be recorded for a live cell

- `git_head` (trace + manifest)
- model, base_url, temperature, seed (configured vs honored)
- prompt_id / defense_condition
- dataset fingerprint / version fields
- run_id, timestamp
- latency_ms (measured) and tokens (provider or null)
- scorer commands and level (L0/L1)

## Non-guarantees

- Seed does not imply deterministic outputs
- Provider model ids may change backend behavior
- Quota/HTTP errors produce `execution_status=error` — not eval outcomes
