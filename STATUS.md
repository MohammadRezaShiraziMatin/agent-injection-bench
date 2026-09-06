# v0 freeze status

Snapshot of the packaging freeze (English). Not an evaluation result.

| Item | State |
| --- | --- |
| **Dataset** | 20 attack + 20 benign under `data/episodes/` (+ 2 format demos in `examples/`). Schema-valid; no further growth in this freeze. |
| **Harness** | Phase 2 real LLM tool loop (`scripts/run_agent.py`, optional `scripts/run_batch.py`). Mock tools only: `search_docs`, `send_email`. |
| **Tests** | `validate_episodes.py`: **ok, n=42, errors=0**. `pytest`: **28 passed** (re-run at freeze). |
| **Docs** | `README.md`, `RUNBOOK.md`, `CHECKLIST.md`, `CURSOR_PROMPT_RUN_EVAL.md`, this file, `METHODS_SNIPPET.md`, `ADAPTI_GUARD_BRIDGE.md`, `RELATED_WORK.md`. |
| **Remaining** | Researcher live runs when API credits exist; ASR/utility **only** after non-error, non-dry-run traces. Defense (ADAPTI-GUARD) stays out of tree — see [`ADAPTI_GUARD_BRIDGE.md`](ADAPTI_GUARD_BRIDGE.md). |
| **Known issue** | OpenAI `insufficient_quota` / HTTP 429 can write `execution_status=error` traces — those are **not** eval results. |
| **Scope** | Attack data + undefended harness only. Complement to ADAPTI-GUARD; **defense is out of scope** here ([`ADAPTI_GUARD_BRIDGE.md`](ADAPTI_GUARD_BRIDGE.md)). |
| **Commit** | `dd0fb59d9e65d64e439c35edabf38066653251bf` |

Do not cite ASR or utility from this artifact until live, scorable traces exist.
