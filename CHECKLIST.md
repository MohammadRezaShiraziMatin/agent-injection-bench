# Researcher checklist (v0)

One-page lock for daily work. No defenses. No fabricated metrics.

## Daily (when working on this package)

- [ ] `python scripts/validate_episodes.py`
- [ ] `python -m pytest`
- [ ] Confirm `.env` exists locally (from `.env.example`) and is **never** committed
- [ ] Optional, only if API credits are available: `python scripts/run_agent.py --smoke`

## Before claiming any number

- [ ] Score **only** traces with `execution_status` in `{ok, max_steps}` (not `error`, not dry-run)
- [ ] Report **N** honestly; if `N=0`, say so — do not invent a rate
- [ ] Do **not** cite error / quota / 429 traces as ASR or utility
- [ ] Prefer: `python scripts/score_asr.py --traces-dir results/traces` and `python scripts/score_utility.py --traces-dir results/traces`

## Scope lock (do not expand in this repo)

- **20 attack + 20 benign** seeds under `data/episodes/`
- **2 mock tools** only: `search_docs`, `send_email`
- **No ADAPTI-GUARD** (or any defense) in this repository
- No schema weakening, no fabricated ASR/utility

See also: [`RUNBOOK.md`](RUNBOOK.md), [`CURSOR_PROMPT_RUN_EVAL.md`](CURSOR_PROMPT_RUN_EVAL.md).
