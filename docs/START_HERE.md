# Start here (agent-injection-bench)

This repository combines a **v0 scaffold** (frozen episodes, offline mock tools, harness, trace writers, ASR/utility scorers) with **research evaluation infrastructure** (paired D0/D2 protocols, immutable run bundles, descriptive metrics). It is **evaluation + attack data** — not a venue for defense efficacy claims without frozen evidence.

**Default posture: API=0** — do not set `AIB_LLM_API_KEY` for day-to-day work. Offline verification is what CI and contributors should run. Live LLM spend requires human sign-off per [LIVE_EVAL_GATE.md](./LIVE_EVAL_GATE.md).

## Evidence posture (read before citing numbers)

| Layer | What exists on `main` | What it supports |
|-------|------------------------|------------------|
| **Level A (research)** | Controlled paired descriptive runs (e.g. P4.2 primary `p42-primary-d0-d2-20260921T173736Z-controlled`, P3-EXT COV-B) | Sample-level observations on pinned runs, protocol provenance, descriptive D0/D2 behavior — **not** confirmatory efficacy or generalization |
| **Level B** | Not satisfied by current runs alone | Requires a **new experimental protocol** and **fresh immutable run IDs** — see gap plan |
| **v0 harness pilot** | Runbook only until 40 live v0 traces are archived | Local `results/traces/` ASR/utility from `score_*.py` on **live** traces only |

Canonical claim ladder and allowed/forbidden wording: [`../paper/RESULTS_EVIDENCE.md`](../paper/RESULTS_EVIDENCE.md). Factual run inventory: [STATUS.md](./STATUS.md). Gap plan: [AIB_P2_Q1_EVIDENCE_GAP_PLAN.md](./AIB_P2_Q1_EVIDENCE_GAP_PLAN.md). **Q1 / Level B path (design only until Phase 4 runs):** [AIB_Q1_STRENGTHENING_4PHASE.md](./AIB_Q1_STRENGTHENING_4PHASE.md). Claim discipline (modes, blending, dry-run): [CLAIMS_MAP.md](./CLAIMS_MAP.md).

## Read order

| Doc | Purpose |
|-----|---------|
| [CLAIMS_MAP.md](./CLAIMS_MAP.md) | Allowed vs forbidden claims (v0 + Level A/B) |
| [STATUS.md](./STATUS.md) | Current repo state and run IDs (no invented metrics) |
| [PHASE_A_PILOT.md](./PHASE_A_PILOT.md) | Operator runbook for **v0** live harness pilot (40 episodes) |
| [LIVE_EVAL_GATE.md](./LIVE_EVAL_GATE.md) | Human sign-off, budget, stop rules (**design only**) |
| [ADAPTI_GUARD_BRIDGE.md](./ADAPTI_GUARD_BRIDGE.md) | D2 integration pin and integrity rules |
| [RUNBOOK.md](./RUNBOOK.md) | Short command reference |

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

- Validate: `"ok": true`, `"errors": 0` (episode count per validator output)
- Pytest: all green
- Dry-run traces: `"status": "dry_run"` — pipeline check only ([CLAIMS_MAP.md](./CLAIMS_MAP.md))
- Scorers with no live v0 traces: `n=0`, `rate=null` — **not** an evaluation result; do not cite ASR/utility from that output

**Research metrics** for Level A come from frozen paired run directories and `scripts/score_p4_3_paired_metrics.py` on archived bundles — not from dry-run or empty v0 trace folders.

## Live work (only after gate)

1. Complete [LIVE_EVAL_GATE.md](./LIVE_EVAL_GATE.md) sign-off (human budget, model pin, Target≠Judge, cache-off).
2. **v0 full harness pilot:** follow [PHASE_A_PILOT.md](./PHASE_A_PILOT.md) — remove stale dry-run traces before scoring live output.
3. **New research runs:** use frozen protocol configs and approval artifacts under `config/`; do not relabel existing Level A run IDs as Level B.

## Relationship to AdaptiGuard

D2 invokes pinned upstream `adapti-guard` for **recorded execution paths** on approved research runs. AdaptiGuard confirmatory tracks in sibling repos stay **out of AIB result tables**. See [ADAPTI_GUARD_BRIDGE.md](./ADAPTI_GUARD_BRIDGE.md) and [CLAIMS_MAP.md](./CLAIMS_MAP.md).
