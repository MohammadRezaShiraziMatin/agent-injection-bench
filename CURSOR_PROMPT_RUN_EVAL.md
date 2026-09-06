# Cursor prompt: run local eval (paste-ready)

Copy everything below the line into Cursor on a machine with API credits. Do not invent metrics.

---

You are helping me run **agent-injection-bench** v0 locally. Constraints:

- Do **not** expand the dataset, change the schema, add defenses, or invent ASR/utility numbers.
- Do **not** treat `execution_status=error` or dry-run traces as attack success.
- If OpenAI returns `insufficient_quota` / HTTP 429, **stop** live runs and report that blocker. Do not fabricate scores.

Steps (in order):

1. Ensure `.env` exists (`cp .env.example .env` if needed). Load/use `AIB_LLM_API_KEY` or `OPENAI_API_KEY`. Never commit secrets.
2. `pip install -e ".[dev]"` if needed.
3. Run `python scripts/validate_episodes.py` and `python -m pytest`. Report pass/fail.
4. Run `python scripts/run_agent.py --smoke`. If quota/429 or other API errors, stop and summarize failures. Do not continue to batch.
5. Optional only if smoke succeeded: `python scripts/run_batch.py` (continues on error; prints ok/error counts only — not ASR).
6. Run scorers **only if** `results/traces/` has at least one non-error, non-dry-run trace:
   - `python scripts/score_asr.py --traces-dir results/traces`
   - `python scripts/score_utility.py --traces-dir results/traces`
7. Print an honest summary: for each metric, report `n`, `successes`, and `rate` (or `null` if `n=0`). If `n=0`, say there is no evaluation result. Never invent numbers.

Keep the response short. Cite commands and exit outcomes only.
