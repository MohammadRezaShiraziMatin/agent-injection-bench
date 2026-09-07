# Cursor prompt: Phase C matrix on Desktop (paste-ready)

Copy everything below the line. Do not invent metrics. Do not add ADAPTI code. Do not expand the dataset.

---

You are running **agent-injection-bench Phase C** on my Desktop (experimental matrix).

## Sync
1. Sync `%USERPROFILE%\Desktop\agent-injection-bench` (or `~/Desktop/agent-injection-bench`) to latest `main` containing `PHASE_C.md` and `scripts/phase_c_matrix.sh`.
2. Confirm `prompts/d1_prompt_defense.txt` exists and D0 remains default.

## Env
- `AIB_LLM_API_KEY` (never commit)
- `AIB_LLM_TEMPERATURE=0`
- Optional: `MODELS=gpt-4o-mini,gpt-4o`, `BASELINES=d0,d1`, `K=3`
- Note cost: full matrix = models × baselines × K × 40 episodes

## Run
```bash
cd ~/Desktop/agent-injection-bench
python -m pip install -e ".[dev]"
python scripts/validate_episodes.py
python -m pytest
# cheap first:
AIB_PHASE_C_SMOKE_ONLY=1 bash scripts/phase_c_matrix.sh
# full (only with credits + budget approval):
# bash scripts/phase_c_matrix.sh
```
Stop on `insufficient_quota` / 429. Do not fabricate scores.

## Report
Open `results/phase_c_plan.json` and `results/phase_c_summary.json`. For each cell report N, skipped, ASR-L0, ASR-L1, utility, Wilson CI when n>0; null rates when n=0. State pilot / not publication-ready. D2 is external only.
