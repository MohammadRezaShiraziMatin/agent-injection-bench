# Runbook

For the **Phase A live pilot** (install → validate → dry-run → key → batch → score), use **[PHASE_A_PILOT.md](./PHASE_A_PILOT.md)**.

## Environment

1. Python **3.10+**
2. `python -m pip install -e ".[dev]"`
3. Optional: copy `.env.example` → `.env` and set `AIB_LLM_API_KEY` (never commit `.env`)

## Validate data

```bash
python scripts/validate_episodes.py
```

Expect `ok: true`, `n: 42` (20+20 + 2 examples), `errors: 0`.

## Dry-run harness (no API key)

```bash
python scripts/run_agent.py --id atk_002 --dry-run --no-write
python scripts/run_agent.py --smoke --dry-run
python scripts/run_batch.py --split attack --dry-run --limit 2
```

## Live run (requires key)

```bash
python scripts/run_agent.py --id atk_002
python scripts/run_batch.py --split all
```

Traces land in `results/traces/<episode_id>.json` (gitignored).

## Score (only after traces exist)

```bash
python scripts/score_asr.py
python scripts/score_utility.py
```

If `n=0`, `rate` is `null` — **not** a result to cite.

## Tests

```bash
python -m pytest
```

## Do not

- Commit API keys
- Claim ASR/utility without scored traces
- Add defense modules to this repo
- Call real SMTP / HTTP from tools
