# Defense ladder (baselines)

Pilot measurement conditions for agent-injection-bench. **D0 is the primary baseline.** No ADAPTI-GUARD code in this repository.

| Id | Name | Status in this repo | Role |
| --- | --- | --- | --- |
| **D0** | Undefended | **Implemented** — [`prompts/d0_undefended.txt`](prompts/d0_undefended.txt) | Default measurement baseline: no defense module, no protective anti-injection system wording. |
| **D1** | Prompt-level defense | **Reserved only** — see [`prompts/d1_prompt_defense.txt.example`](prompts/d1_prompt_defense.txt.example) | Future prompt-only condition. Not enabled as default. Do not treat the example as a strong or evaluated defense. |
| **D2** | External / runtime defense | **Out of tree** | ADAPTI-GUARD (and similar) evaluated later as **one defense under test** via a separate runner that reuses episode/trace schemas ([`ADAPTI_GUARD_BRIDGE.md`](ADAPTI_GUARD_BRIDGE.md)). |

## Rules

- Baseline scientific runs use **`--prompt-id d0`** (default).
- Do not claim D1/D2 results from this artifact until those conditions are actually run and traced.
- Switching the ladder must not rewrite history: traces live under `results/traces/<run_id>/` and are not overwritten without `--force`.

See also: [`QUALITY_TABLE_V0.md`](QUALITY_TABLE_V0.md), [`docs/ASR_LEVELS.md`](docs/ASR_LEVELS.md), [`ROADMAP_P0.md`](ROADMAP_P0.md).
