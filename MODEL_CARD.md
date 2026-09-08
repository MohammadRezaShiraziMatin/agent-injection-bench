# MODEL_CARD (evaluation target)

## Provider / identifier

- Default: OpenAI-compatible Chat Completions
- Default model string: `gpt-4o-mini` (`agent/config.py` / `.env.example`)
- Override: `AIB_LLM_MODEL`, `AIB_LLM_BASE_URL`

Exact backend revision behind a model string is **provider-controlled** and may not be fully observable.

## Configuration

| Knob | Default / source | Notes |
| --- | --- | --- |
| temperature | `0.0` | Via config / env |
| seed | optional | Best-effort; many APIs ignore or partially honor |
| max_steps | `6` | Tool loop bound |
| timeout | `60s` | HTTP timeout |

## Token accounting

- When the provider returns `usage`, traces store ints under `tokens` with `source=provider`
- Otherwise `tokens=null` — **never estimate**

## Latency accounting

- `latency_ms`: measured wall time for live `run_episode` loops
- Dry-run: `latency_ms=null`

## Determinism

- **Seed configured** ≠ **guaranteed deterministic execution**
- Temperature 0 reduces but does not eliminate API nondeterminism

## Intended evaluation use

- Pilot D0/D1 matrix cells for this bench only

## Limitations

- Tool-calling behavior differs across providers
- Quota/errors → `execution_status=error` (not a model “defense win”)
