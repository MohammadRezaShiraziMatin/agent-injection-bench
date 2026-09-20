# Status

Snapshot for agent-injection-bench v0 (pilot packaging). **Not publication-grade results** until live scorable traces are archived.

| Item | State |
| --- | --- |
| **Dataset** | 20 attack + 20 benign twins under `data/episodes/` (+ 2 format demos in `examples/`). Schema-valid; v0 freeze. |
| **Documentation** | Canonical research docs under `docs/`; paper drafts under `paper/`. |
| **Harness** | LLM tool loop; mock `search_docs`, `send_email`. Traces: `run_id`, `prompt_id`, `defense_condition`, `git_head`, `latency_ms`, `tokens`. |
| **Defense conditions** | **D0** default; **D1** minimal prompt; **D2** ADAPTI external only. |
| **Scoring** | ASR-L0/L1 + utility heuristic; L2 stub; Wilson CI in aggregator when `n>0`. |
| **Tests / CI** | `validate_episodes.py` + `pytest` offline; GitHub Actions on push/PR. |
| **Live traces in repo** | None committed (`results/traces/` gitignored). |
| **Empirical rates** | **None published** — see [docs/CLAIMS.md](docs/CLAIMS.md). |

Do not cite ASR or utility until non-error, non-dry-run traces exist for the stated model and defense condition.
