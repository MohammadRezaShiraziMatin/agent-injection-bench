# Experiment protocol

## Offline (default, CI-safe)

1. `python -m pip install -e ".[dev]"`
2. `python scripts/validate_episodes.py`
3. `python -m pytest`
4. Optional: `python scripts/run_agent.py --smoke --dry-run`

No API key. No live LLM.

## Live pilot (requires key; not CI)

**Preconditions:** offline steps green; human budget and scope sign-off; `.env` not committed.

1. Copy `.env.example` → `.env`; set `AIB_LLM_API_KEY`
2. Set `AIB_LLM_TEMPERATURE=0` (optional `AIB_LLM_SEED`, best-effort)
3. Choose defense condition: `--prompt-id d0` (default) or `d1`
4. Run harness:
   - Smoke: `python scripts/run_agent.py --smoke`
   - Full seed batch: `python scripts/run_batch.py`
   - Phase A dual-model D0: `bash scripts/phase_a_pilot.sh`
   - Phase C matrix: `AIB_PHASE_C_SMOKE_ONLY=1 bash scripts/phase_c_matrix.sh` (cheap) or full `bash scripts/phase_c_matrix.sh`
5. Score **only** scorable traces:
   ```bash
   python scripts/score_asr.py --traces-dir results/traces/<run_id> --level 0
   python scripts/score_asr.py --traces-dir results/traces/<run_id> --level 1
   python scripts/score_utility.py --traces-dir results/traces/<run_id>
   python scripts/aggregate_phase_c.py --plan results/phase_c_plan.json  # when applicable
   ```
6. Report **N**, skipped counts, rates, Wilson CI when `n>0` — never invent

## Rules

- Do not overwrite traces without `--force`
- Do not treat `error` or dry-run as attack/utility success
- Do not run ADAPTI-GUARD / D2 inside this repo
- Do not commit `.env` or trace JSON
- Do not merge AdaptiGuard Track A/B numbers into AIB tables — [ADAPTI_GUARD_BRIDGE.md](./ADAPTI_GUARD_BRIDGE.md), [CLAIMS.md](./CLAIMS.md)

## Stop conditions

Halt on budget exceedance, harness/schema errors, or sustained quota/429; partial `n` is partial evidence only.

## Phase A reporting template

Fill from `results/phase_a_summary.json` / scorer JSON only:

```text
Pilot (D0, temperature=0)
Models: <model1>, <model2>
Dataset: 20 attack + 20 benign twins
Per model: run_id, N_scorable, skipped, ASR-L0 rate or null, utility rate or null
Notes: error traces excluded; seed best-effort; D2 external
```
