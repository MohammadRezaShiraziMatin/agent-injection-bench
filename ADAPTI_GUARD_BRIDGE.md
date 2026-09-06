# ADAPTI-GUARD bridge (no defense code)

This repository is **attack data + an undefended eval harness** only. **ADAPTI-GUARD** is a separate runtime defense line of work. They are meant to connect in a paper narrative, not in this codebase.

## Roles

| Artifact | Role |
| --- | --- |
| **agent-injection-bench** (this repo) | Episodes, schema, mock tools, baseline agent loop, traces, ASR/utility stubs |
| **ADAPTI-GUARD** (elsewhere) | Runtime defense to reduce successful injections while preserving utility |

## Paper narrative (how they connect)

1. **Phase 1 — measure:** Run this bench’s undefended harness on the fixed episode set; keep auditable traces; score ASR/utility only on non-error traces.
2. **Phase 2 — defend and re-score:** Plug ADAPTI-GUARD (or any defense) into a *separate* runner that consumes the **same episode schema** and emits the **same trace schema**; re-score with the **same** `score_asr.py` / `score_utility.py` stubs so comparisons stay format-aligned.

Same episodes and scorer definitions; different agent path (undefended vs defended). No leaderboard claims until both sides have real non-error traces.

## Non-goals (explicit)

- Do **not** implement ADAPTI-GUARD in this repository.
- Do **not** claim defense results, mitigation rates, or “guarded ASR” from this artifact alone.
- Do **not** change scorers to encode a defense; defenses belong in the runner, not in metrics code here.

## Interface sketch only

Future defended runner (out of tree):

- **In:** episode JSON conforming to `schema/episode.schema.json` (and the same mock tool names: `search_docs`, `send_email`).
- **Out:** trace JSON with the same fields this harness already writes (`episode_id`, `tool_calls`, `final_answer`, `execution_status`, …) under e.g. `results/traces/`.
- **Score:** unchanged stubs — `python scripts/score_asr.py --traces-dir …` and `score_utility.py` — still skipping `execution_status=error` and dry-run.

No defense API, config, or code is provided here.

## Related Work / Positioning (paste-ready)

We release a small indirect prompt-injection benchmark and undefended agent harness as a measurement artifact complementary to ADAPTI-GUARD, a separate runtime defense line of work. The bench supplies fixed attack/benign twin episodes, mock tools, and auditable traces so that baseline ASR and utility can be estimated under a shared schema; defenses such as ADAPTI-GUARD are intended to be evaluated later by swapping the agent runner while keeping the same episodes, trace format, and scorers. This repository does not implement or evaluate any defense.
