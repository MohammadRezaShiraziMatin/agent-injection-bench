# Phase C — experimental methodology (matrix)

Builds on Phase A packaging and Phase B scorers. Still **pilot / not publication-ready** until live traces exist. No dataset growth. No in-repo ADAPTI.

## Checklist for Matin

1. Sync Desktop to Phase C HEAD.
2. `pip install -e ".[dev]"` → `validate_episodes.py` → `pytest`
3. Env: `AIB_LLM_API_KEY`, `AIB_LLM_TEMPERATURE=0`
4. Matrix plan (written before runs): models × baselines `{d0,d1}` × k repeats  
   - Defaults: `MODELS=gpt-4o-mini,gpt-4o`, `BASELINES=d0,d1`, `K=3`  
   - **D2** is external only — see [`docs/D2_EXTERNAL_ADAPTI.md`](docs/D2_EXTERNAL_ADAPTI.md)
5. Cheap path first:
   ```bash
   AIB_PHASE_C_SMOKE_ONLY=1 bash scripts/phase_c_matrix.sh
   ```
6. Full path (costly):
   ```bash
   bash scripts/phase_c_matrix.sh
   ```
7. Read `results/phase_c_plan.json` and `results/phase_c_summary.json`
8. Report per cell: N, skipped, ASR-L0, ASR-L1, utility, Wilson 95% CI when n>0; `rate=null` when n=0

Paste-ready Desktop prompt: [`CURSOR_PROMPT_PHASE_C_DESKTOP.md`](CURSOR_PROMPT_PHASE_C_DESKTOP.md).

## Matrix cells (in-repo)

| Baseline | Prompt | Runner |
| --- | --- | --- |
| D0 | `prompts/d0_undefended.txt` | `run_batch` / `--smoke` |
| D1 | `prompts/d1_prompt_defense.txt` | same harness, `--prompt-id d1` |
| D2 | external ADAPTI | out of tree; same trace schema |

Each (model × baseline × repeat) gets its own `run_id`. Fixed `temperature=0`. Seed remains best-effort.

## Honesty

- Do not invent successes or rates.
- Prompt-level D1 is a **minimal** instruction, not a strong defense evaluation.
- ADAPTI results (if any) come only from an external D2 runner later.
- Pilot matrix ≠ publication-ready paper table until live non-error traces exist and are reported with N/skipped/CI.
