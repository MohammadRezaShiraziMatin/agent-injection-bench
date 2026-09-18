# Checklist (v0)

- [x] Frozen `schema/episode.schema.json`
- [x] 20 attack + 20 benign twin episodes
- [x] Examples `atk_001` / `ben_001`
- [x] Mock tools: `search_docs`, `send_email` (offline)
- [x] Agent harness: config / llm / load / loop / tools / traces
- [x] Scripts: validate, run_agent, run_batch, score_asr, score_utility
- [x] Tests + `pip install -e ".[dev]"`
- [x] Docs: README, START_HERE, CLAIMS_MAP, LIVE_EVAL_GATE, runbook, Phase A pilot, status, methods, related work, ADAPTI bridge
- [x] `.gitignore` excludes `.env`, `.venv/`, `__pycache__/`, `results/traces/*.json`, `*.egg-info/`
- [ ] Live LLM batch (requires user API key — not part of scaffold)
- [ ] Report ASR/utility from real traces (do not fabricate)
- [ ] GitHub remote + push (see STATUS / final report)
- [ ] ADAPTI-GUARD evaluation (separate repo; bridge doc only)
