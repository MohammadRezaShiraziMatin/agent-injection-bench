# METHODS

Source-grounded methodology for agent-injection-bench. If something is not observable in code, it is marked explicitly.

## Research objective

Measure **indirect prompt injection** that tries to induce a **forbidden tool call** (`send_email`) in a tool-using agent, with a paired **benign utility** check. Scope is a small pilot (20+20), not a full production security suite.

## Threat model

- Adversary controls **retrieved document text**, not the user query.
- Goal: induce the agent to call a forbidden tool (exfil / unauthorized email).
- Tools are **offline mocks** (no real delivery / URL fetch).

## Agent / application setting

Campus-assistant style Q&A with two tools:

- `search_docs(query)` — search episode-bound docs
- `send_email(to, subject, body)` — log-only mock

Retrieval is **pre-bound** to the episode (`retrieved_docs` inlined). Not a full corpus RAG ranker.

## Defense conditions

| Id | Definition in source | Status |
| --- | --- | --- |
| **D0** | `prompts/d0_undefended.txt` — no anti-injection instructions | Implemented; **default** |
| **D1** | `prompts/d1_prompt_defense.txt` — treat docs as untrusted; follow user only | Implemented; Phase C cell; **minimal / scoped**, not a strong defense claim |
| **D2** | Adaptive / ADAPTI-GUARD | **Not implemented** in this repo (see `PHASE_D.md`, `docs/D2_EXTERNAL_ADAPTI.md`) |

## Dataset

- 20 attack + 20 benign twins (`data/episodes/`), plus 2 format demos (`examples/`).
- Schema: `schema/episode.schema.json` (frozen draft-07).
- Tags / taxonomy: see `TAXONOMY.md`. QA: `scripts/qa_episodes.py`, `QA_REPORT.md`.

## Prompt IDs

- CLI / env: `--prompt-id` / `AIB_PROMPT_ID` (default `d0`).
- Trace fields: `prompt_id`, `defense_condition`.

## Model configuration

- OpenAI-compatible Chat Completions (`agent/llm.py`).
- Env: `AIB_LLM_*` (see `.env.example`).
- Default temperature: **0.0** (`agent/config.py`).
- Seed: optional `AIB_LLM_SEED` — **best-effort**; not guaranteed deterministic across providers.

## Trace schema (observed facts)

Required / standard fields include: `run_id`, `timestamp`, `git_head`, `model`, `temperature`, `seed`, `episode`/`episode_id`, `tool_calls`, `status`/`execution_status`, `prompt_id`, `latency_ms`, `tokens`.

- `latency_ms`: measured wall time for live loops; **null** on dry-run.
- `tokens`: provider `usage` when present; **null** otherwise — **never estimated**.
- `git_head`: `git rev-parse HEAD` when available; else null. Manifests also store `git_head`.

Statuses: `ok` | `max_steps` | `error` | `dry_run`. Error/dry_run are **not** scored as ASR=0.

## Metrics

- **ASR-L0 / L1 / L2**: `docs/ASR_LEVELS.md`, `scripts/score_asr.py`, `scripts/asr_levels.py`.
- **Utility**: `scripts/score_utility.py`.
- Empty evidence → `n=0`, `rate=null`.
- Wilson 95% CI: `scripts/aggregate_phase_c.py` when `n>0`.

## Phase C

Multi-model × {D0,D1} × K repeats methodology (`PHASE_C.md`, `scripts/phase_c_matrix.sh`). Pilot only.

## Limitations

- Small N; substring utility heuristic; mock tools; API nondeterminism; D1 is prompt-only; no Adaptive/D2 results in-repo.
- **Not specified / not observable:** inter-annotator agreement, hidden test split, production defense strength claims.

## Reproduction

See `REPRODUCIBILITY.md` and `EXPERIMENT_PROTOCOL.md`. Offline path: `pip install -e ".[dev]"` → `validate_episodes.py` → `pytest` → dry-run scripts (no API key).
