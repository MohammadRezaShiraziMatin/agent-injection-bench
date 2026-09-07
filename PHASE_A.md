# Phase A — close the pilot

Checklist to finish **AIB v0/pilot** measurement under **D0** (undefended). Not publication-ready. No defenses in-repo. No fabricated ASR/utility.

## Exact checklist

1. **Sync Desktop** to HEAD that includes the eval layer + this Phase A pack (at or after the commit that adds `PHASE_A.md`). Prefer `git pull`, or unpack the latest desktop tarball over `%USERPROFILE%\Desktop\agent-injection-bench`.
2. **Env:** `cp .env.example .env` if needed. Set `AIB_LLM_API_KEY` (never commit). Set:
   - `AIB_LLM_TEMPERATURE=0` (fixed for pilot reproducibility)
   - Optional `AIB_LLM_SEED` — **best-effort**; many APIs ignore seed (document in notes if ignored)
   - Two models: `AIB_PHASE_A_MODEL1` (default `gpt-4o-mini`) and `AIB_PHASE_A_MODEL2` (default `gpt-4o`; **cost note**)
3. **Package checks (no API):** `pip install -e ".[dev]"` → `python scripts/validate_episodes.py` → `python -m pytest`
4. **Live pilot:** `bash scripts/phase_a_pilot.sh`  
   - Per model: `run_agent.py --smoke` then `run_batch.py` (separate `run_id`s)  
   - Score **ASR L0** + **utility** on each batch traces dir  
   - Writes `results/phase_a_summary.json` (honest aggregates only)
5. **Private GitHub + tag:** follow [`GITHUB_TAG_V0_1.md`](GITHUB_TAG_V0_1.md) → tag `v0.1-pilot`
6. **Report** with the template below — do not overclaim

Paste-ready Desktop agent prompt: [`CURSOR_PROMPT_PHASE_A_DESKTOP.md`](CURSOR_PROMPT_PHASE_A_DESKTOP.md).

## Honest reporting template

Copy and fill from `results/phase_a_summary.json` / scorer JSON only:

```text
AIB Phase A pilot (D0, temperature=0)
Models: <model1>, <model2>
Dataset: 20 attack + 20 benign (twins); schema frozen
Per model:
  - smoke statuses: …
  - batch run_id: …
  - N_scorable_asr_L0: …  skipped: {error: …, dry_run: …, …}
  - ASR-L0 rate: … or null if N=0
  - N_scorable_utility: …  skipped: …
  - utility rate: … or null if N=0
Notes:
  - ASR is L0 tool-name only (not L1/L2)
  - error/quota traces are not attack success
  - seed may be ignored by the API
  - pilot / not publication-ready; no defense results; ADAPTI is D2 external
```

## Non-goals

- No dataset growth  
- No in-repo ADAPTI / D1-as-default  
- No README claim of published ASR/utility numbers  
