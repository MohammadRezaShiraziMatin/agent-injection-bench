# Cursor prompt: Phase A on Desktop (paste-ready)

Copy everything below the line into Cursor on Matin’s machine. Do not invent ASR/utility numbers. Do not add defenses or expand the dataset.

---

You are closing **agent-injection-bench Phase A** (D0 pilot) on my Desktop.

## Sync

1. Ensure the project is at `%USERPROFILE%\Desktop\agent-injection-bench` (or `~/Desktop/agent-injection-bench`).
2. Sync to the latest remote `main` that includes `PHASE_A.md` and `scripts/phase_a_pilot.sh` (git pull), **or** replace the folder from the latest `agent-injection-bench-desktop.tgz` artifact / clone.
3. Confirm `git rev-parse HEAD` and that these files exist: `PHASE_A.md`, `scripts/phase_a_pilot.sh`, `BASELINES.md`, `prompts/d0_undefended.txt`.

## Env

1. `cp .env.example .env` if needed; set `AIB_LLM_API_KEY` (never commit `.env`).
2. Set `AIB_LLM_TEMPERATURE=0`.
3. Two distinct models, e.g.:
   - `AIB_PHASE_A_MODEL1=gpt-4o-mini`
   - `AIB_PHASE_A_MODEL2=gpt-4o` (higher cost — confirm before running full batch)
4. Optional `AIB_LLM_SEED` — note it may be ignored by the API.

## Run

```bash
cd ~/Desktop/agent-injection-bench   # or Windows equivalent
python -m pip install -e ".[dev]"
python scripts/validate_episodes.py
python -m pytest
bash scripts/phase_a_pilot.sh
```

If smoke hits `insufficient_quota` / 429, **stop** and report the blocker. Do not fabricate scores.

## After success

1. Open `results/phase_a_summary.json` and report N, skipped, ASR-L0 rate, utility rate per model honestly (`null` if N=0).
2. Follow `GITHUB_TAG_V0_1.md` for private GitHub + tag `v0.1-pilot`.
3. Keep claims limited: pilot, D0, L0 tool-name ASR only, no defense results, ADAPTI is external D2.

Keep the reply short: HEAD synced, commands run, exit codes, path to summary JSON, any quota errors.
