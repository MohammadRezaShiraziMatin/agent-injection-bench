# v0 / Phase C status

Baseline content synced from Origin commit **`7ec8eb7b6f6e9671a9de653670f16fcf01bcf5de`** (Phase C matrix). Local GitHub `main` may still point at an earlier scaffold commit until publication commits land — do not confuse Git `HEAD` with the intended baseline.

| Item | State |
| --- | --- |
| **Dataset** | 20 attack + 20 benign under `data/episodes/` (+ 2 format demos in `examples/`). Schema-valid; no further growth in this freeze. |
| **Harness** | Real LLM tool loop (`scripts/run_agent.py`, `scripts/run_batch.py`). Mock tools only: `search_docs`, `send_email`. Traces include `run_id`, `prompt_id`, `temperature`, `seed`, `git_head`, `latency_ms`, `tokens` (null when not observed). |
| **Baselines** | **D0** undefended (default). **D1** minimal prompt defense (Phase C cell). **D2** Adaptive/ADAPTI **not implemented**. |
| **ASR** | L0 (default) + L1 implemented; L2 stub (`rate=null`). Skip error/dry_run. Wilson 95% CI via `aggregate_phase_c.py` when n>0. |
| **Phase C** | Methodology + matrix scripts ready. Live matrix requires API credits — **no fabricated rates**. |
| **Tests** | `validate_episodes.py` + `pytest` (offline; no API keys). |
| **Scope claim** | Pilot / preliminary evidence under scoped conditions. **Not** publication-grade; **not** a claim that D1 is strong or production-ready. |

Do not cite ASR or utility until live, scorable, non-error traces exist for the claimed condition.
