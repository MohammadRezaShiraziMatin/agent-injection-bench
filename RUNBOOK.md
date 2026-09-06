# Researcher runbook (English)

Copy-paste commands for a local machine with API credits. This is **not** a published evaluation.

## 1. Environment

```bash
cd /path/to/agent-injection-bench
cp .env.example .env
# Edit .env and set AIB_LLM_API_KEY (or OPENAI_API_KEY). Never commit .env.
```

## 2. Install

```bash
python -m pip install -e ".[dev]"
```

## 3. Package checks (no API key)

```bash
python scripts/validate_episodes.py
python -m pytest
```

Expect: validation ok for the seed set; all unit tests pass.

## 4. Live smoke (requires credits)

```bash
python scripts/run_agent.py --smoke
```

Runs `atk_002` and `ben_002` only. Writes traces under `results/traces/`.  
Pipeline check only — **not** ASR or utility.

If you see `insufficient_quota` / HTTP 429, the run failed. Any written trace with `execution_status=error` is **not** an eval result.

## 5. One episode

```bash
python scripts/run_agent.py --id atk_002
python scripts/run_agent.py --id ben_002
```

Optional inspect-only (no API):

```bash
python scripts/run_agent.py --dry-run --id atk_002
```

Dry-run traces are not live eval results.

## 6. All seed episodes (batch)

Prefer the helper:

```bash
python scripts/run_batch.py
```

Or a simple shell loop (same idea):

```bash
for id in $(python -c "from scripts._common import EPISODES_DIR, load_episodes; print(' '.join(sorted({e['id'] for e in load_episodes([EPISODES_DIR])})))"); do
  python scripts/run_agent.py --id "$id" || echo "failed $id (continuing)"
done
```

`run_batch.py` continues on error by default and prints **ok / error / max_steps counts only**. It does **not** print a scientific ASR.

## 7. Score later (only after real non-error traces)

Do **not** score until you have live traces with `execution_status` in `{ok, max_steps}` (not `error`, not dry-run).

```bash
python scripts/score_asr.py --traces-dir results/traces
python scripts/score_utility.py --traces-dir results/traces
```

Scorers **skip** `execution_status=error` and (by default) `dry_run=true`. Those are never treated as attack success or utility success.

Until real traces exist, expect `n=0`, `rate=null` — that is honest emptiness, not a paper number.

## Known blocker

A prior cloud smoke hit OpenAI `insufficient_quota` / 429. Error traces from that situation (if any) must not be used as evaluation results.
