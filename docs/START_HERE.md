# Start here (agent-injection-bench)

This repo is a **v0 scaffold**: frozen episodes, offline mock tools, harness + trace writers, and ASR/utility scorers. It is **attack + evaluation infrastructure only** — no defense implementation, no published live pilot rates until real traces exist.

**Default posture: API=0** — do not set `AIB_LLM_API_KEY` unless you have passed the live-eval gate in [LIVE_EVAL_GATE.md](./LIVE_EVAL_GATE.md). Offline verification is the expected day-to-day mode for CI and contributors.

## Read order

| Doc | Purpose |
|-----|---------|
| [CLAIMS_MAP.md](./CLAIMS_MAP.md) | What you may and may not say about results |
| [PHASE_A_PILOT.md](./PHASE_A_PILOT.md) | Operator runbook when a live pilot is approved |
| [LIVE_EVAL_GATE.md](./LIVE_EVAL_GATE.md) | Human sign-off, budget, stop rules (design only) |
| [ADAPTI_GUARD_BRIDGE.md](./ADAPTI_GUARD_BRIDGE.md) | D0/D1/D2 integration with sibling AdaptiGuard work |
| [RUNBOOK.md](./RUNBOOK.md) | Short command reference |
| [STATUS.md](./STATUS.md) | Factual repo state (no invented metrics) |

## Offline verify (API=0)

From repo root with Python **3.10+**:

```bash
python3 -m venv .venv
source .venv/bin/activate
python3 -m pip install -e ".[dev]"
python3 scripts/validate_episodes.py
python3 -m pytest
python3 scripts/run_agent.py --id atk_002 --dry-run
python3 scripts/run_agent.py --smoke --dry-run
python3 scripts/run_batch.py --split all --dry-run --limit 4
python3 scripts/score_asr.py
python3 scripts/score_utility.py
```

**Pass criteria**

- Validate: `"ok": true`, `"n": 42`, `"errors": 0`
- Pytest: all green
- Dry-run traces: `"status": "dry_run"` — pipeline check only ([CLAIMS_MAP.md](./CLAIMS_MAP.md))
- Scorers with no live traces: `n=0`, `rate=null` — **not** an evaluation result; do not cite ASR/utility

## Live pilot (only after gate)

1. Complete [LIVE_EVAL_GATE.md](./LIVE_EVAL_GATE.md) sign-off (human budget, model pin, Target≠Judge, cache-off).
2. Follow [PHASE_A_PILOT.md](./PHASE_A_PILOT.md) — remove stale dry-run traces before scoring live output.

## Relationship to AdaptiGuard (sibling)

AdaptiGuard confirmatory work (Track A/B, Layer A diagnostics) lives in a **separate** repository. This bench supplies frozen episodes and trace-shaped facts; it does **not** host defense code or blended Track A/B tables. See [ADAPTI_GUARD_BRIDGE.md](./ADAPTI_GUARD_BRIDGE.md) and [CLAIMS_MAP.md](./CLAIMS_MAP.md).

## Current status (honest)

| Item | State |
|------|--------|
| Schema + 20+20 episodes | Frozen v0 |
| Harness + scorers + tests | Present |
| Phase A pilot runbook | [PHASE_A_PILOT.md](./PHASE_A_PILOT.md) |
| Live pilot traces on main | **Not done** until 40 scored live traces are archived |
| ASR / utility rates in docs | **None** — do not invent |

Update [STATUS.md](./STATUS.md) only with dated facts after a completed live pilot.
