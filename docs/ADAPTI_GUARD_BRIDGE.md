# ADAPTI-GUARD bridge (no defense code)

This repository is **attack data + measurement harness** only. **ADAPTI-GUARD** is separate runtime defense work. They connect in paper narrative, not in this codebase.

## Roles

| Artifact | Role |
| --- | --- |
| **agent-injection-bench** (this repo) | Episodes, schema, mock tools, D0/D1 agent loop, traces, scorers |
| **ADAPTI-GUARD** (elsewhere) | Runtime defense under test as **D2** |

## Paper narrative

1. **Measure:** Run the fixed episode set with D0 (and optionally D1); archive scorable traces; score ASR/utility offline.
2. **Defend (external):** Run a defended agent with the **same episode schema** and **same trace shape**; re-score with the **same** `score_asr.py` / `score_utility.py`.

Same episodes and scorer definitions; different runner path. Do not claim defense results from this artifact alone.

## D2 external contract

1. **Input:** episode JSON conforming to `schema/episode.schema.json`
2. **Tools:** compatible mock names (`search_docs`, `send_email`)
3. **Output:** traces under `results/traces/<run_id>/<episode_id>.json` with fields matching this harness (`defense_condition=d2`, `tool_calls`, `execution_status`, …)
4. **Manifest:** optional `results/manifests/<run_id>.json` with model, temperature, seed, `dataset_version`
5. **Scoring:** unchanged:
   ```bash
   python scripts/score_asr.py --level 0 --traces-dir results/traces/<run_id>
   python scripts/score_asr.py --level 1 --traces-dir results/traces/<run_id>
   python scripts/score_utility.py --traces-dir results/traces/<run_id>
   ```

## Non-goals

- Do **not** implement ADAPTI-GUARD here
- Do **not** change scorers to encode defense logic
- Do **not** merge AdaptiGuard Track A/B or confirmatory numbers into AIB tables — see [CLAIMS.md](./CLAIMS.md)

## Positioning (paste-ready)

We release a small indirect prompt-injection benchmark and measurement harness complementary to ADAPTI-GUARD. The bench supplies fixed attack/benign twin episodes, mock tools, and auditable traces so baseline ASR and utility can be estimated under a shared schema; defenses are evaluated by swapping the agent runner while keeping episodes, trace format, and scorers aligned. This repository does not implement or evaluate any defense.
