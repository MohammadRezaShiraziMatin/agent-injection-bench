# EXPERIMENT_PROTOCOL

## Offline (default, CI-safe)

1. `python -m pip install -e ".[dev]"`
2. `python scripts/validate_episodes.py`
3. `python -m pytest`
4. Optional dry-run: `python scripts/run_agent.py --smoke --dry-run`

No API key. No live LLM.

## Live pilot (requires key; not CI)

1. Copy `.env.example` → `.env`; set `AIB_LLM_API_KEY`
2. Set `AIB_LLM_TEMPERATURE=0` (optional seed)
3. Choose `--prompt-id d0` (default) or `d1`
4. `python scripts/run_batch.py` (or Phase C matrix script)
5. Score: `score_asr.py --level 0|1`, `score_utility.py`, optional `aggregate_phase_c.py`
6. Record N, skipped, rate, Wilson CI when n>0 — never invent

## Rules

- Do not overwrite traces without `--force`
- Do not treat error/dry_run as attack success
- Do not run Adaptive/D2 in this repo
- Do not commit `.env` or trace JSON
