# Start here

**agent-injection-bench** is a v0 research artifact: frozen **episodes**, an agent **execution harness**, mock **tools**, auditable **traces**, and offline **scoring** for indirect prompt injection against tool-using agents. It complements **ADAPTI-GUARD** (external defense work); it does not implement defenses.

**Default: API=0.** CI and day-to-day work stay offline. Live LLM runs require API keys and human budget approval — see [EXPERIMENT_PROTOCOL.md](./EXPERIMENT_PROTOCOL.md).

There are **no published ASR or utility rates** in this repository until you produce scorable live traces.

## Read order

| Document | Purpose |
| --- | --- |
| [CLAIMS.md](./CLAIMS.md) | Allowed vs forbidden statements about results |
| [THREAT_MODEL.md](./THREAT_MODEL.md) | Adversary, target, success criterion |
| [BENCHMARK.md](./BENCHMARK.md) | Scope, defense conditions D0/D1/D2, what is measured |
| [DATASET.md](./DATASET.md) | Episode set, twins, provenance |
| [EVALUATION.md](./EVALUATION.md) | Traces, scoring, statistics |
| [EXPERIMENT_PROTOCOL.md](./EXPERIMENT_PROTOCOL.md) | Offline vs live procedures |
| [REPRODUCIBILITY.md](./REPRODUCIBILITY.md) | What to record for a live cell |
| [ADAPTI_GUARD_BRIDGE.md](./ADAPTI_GUARD_BRIDGE.md) | External D2 / case-study separation |
| [LIMITATIONS.md](./LIMITATIONS.md) | Honest scope bounds |
| [STATUS.md](../STATUS.md) | Current repo state (root) |

Paper drafting: [../paper/outline.md](../paper/outline.md), [../paper/claims.md](../paper/claims.md).

## Offline verify (no API key)

```bash
python -m pip install -e ".[dev]"
python scripts/validate_episodes.py
python -m pytest
python scripts/run_agent.py --id atk_002 --dry-run --no-write
python scripts/run_agent.py --smoke --dry-run
```

**Pass criteria:** validation `ok: true`, `n: 42`, `errors: 0`; pytest green; dry-run traces have `execution_status=dry_run` (pipeline check only).

Scorers on an empty `results/traces/` tree return `n=0`, `rate=null` — **not** an evaluation result.

## Live pilot (after protocol)

1. Complete preconditions in [EXPERIMENT_PROTOCOL.md](./EXPERIMENT_PROTOCOL.md).
2. `cp .env.example .env` and set `AIB_LLM_API_KEY` (never commit).
3. `python scripts/run_agent.py --smoke` then `python scripts/run_batch.py` (or `bash scripts/phase_a_pilot.sh` / `bash scripts/phase_c_matrix.sh` for planned matrices).
4. Score only non-error, non-dry-run traces: `scripts/score_asr.py`, `scripts/score_utility.py`.

## Terminology (canonical)

| Term | Meaning |
| --- | --- |
| **Episode** | One JSON task: `user_query`, `retrieved_docs`, `injection`, `expected` |
| **Attack** | `split=attack`; injection in retrieved docs; non-empty `forbidden_tools` |
| **Benign twin** | Paired episode with same `user_query`, clean docs, `injection.present=false` |
| **Target** | Misuse goal in v0: forbidden tool call (typically `send_email`) |
| **Defense condition** | D0 undefended, D1 minimal prompt, D2 external ADAPTI — see [BENCHMARK.md](./BENCHMARK.md) |
| **Trace** | Execution log under `results/traces/<run_id>/`; facts only, no embedded success labels |
| **Scoring** | Offline ASR / utility on traces via `scripts/score_*.py` |

## Contributing

- No secrets in git; no live LLM in CI (`.github/workflows/ci.yml`).
- Do not commit `results/traces/**/*.json` or fabricated metrics.
- See [CLAIMS.md](./CLAIMS.md) before citing any rate.
