# D2 — external ADAPTI-GUARD hook (no in-repo code)

**D2** means a defended agent runner that lives **outside** this repository (e.g. ADAPTI-GUARD). This file documents the interface only.

## Contract

1. **Input:** same episode JSON as `schema/episode.schema.json` (20+20 seeds under `data/episodes/`).
2. **Tools:** same mock tool names (`search_docs`, `send_email`) or compatible stubs; no real email send required for scoring.
3. **Output:** one auditable trace per episode under e.g. `results/traces/<run_id>/<episode_id>.json` with the same fields this harness writes (`run_id`, `episode_id`, `prompt_id`/`defense_condition`, `tool_calls`, `final_answer`, `execution_status`, …).
4. **Manifest:** optional `results/manifests/<run_id>.json` including `model`, `temperature`, `seed`, `prompt_id` or `defense_condition=d2`, `dataset_version`, episode list, status counts.
5. **Scoring:** reuse unchanged stubs:
   ```bash
   python scripts/score_asr.py --level 0 --traces-dir results/traces/<run_id>
   python scripts/score_asr.py --level 1 --traces-dir results/traces/<run_id>
   python scripts/score_utility.py --traces-dir results/traces/<run_id>
   ```
6. Aggregate with Phase C cells by setting `defense_condition` / a label such as `d2` in the manifest so `aggregate_phase_c.py` (or a thin wrapper) can include the cell.

## Non-goals

- Do **not** implement ADAPTI-GUARD in this repo.
- Do **not** claim D2 results from D0/D1 traces.
- Do **not** change scorers to encode defense logic.

See [`ADAPTI_GUARD_BRIDGE.md`](../ADAPTI_GUARD_BRIDGE.md), [`BASELINES.md`](../BASELINES.md), [`PHASE_C.md`](../PHASE_C.md).
