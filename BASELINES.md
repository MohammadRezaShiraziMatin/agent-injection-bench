# Defense ladder (baselines)

Pilot measurement conditions for agent-injection-bench. **D0 is the primary baseline.** No ADAPTI-GUARD code in this repository.

| Id | Name | Status in this repo | Role |
| --- | --- | --- | --- |
| **D0** | Undefended | **Implemented** — [`prompts/d0_undefended.txt`](prompts/d0_undefended.txt) | Default measurement baseline. |
| **D1** | Prompt-level defense | **Implemented (minimal)** — [`prompts/d1_prompt_defense.txt`](prompts/d1_prompt_defense.txt) | Phase C matrix cell only. Not a strong/evaluated defense. Not default. |
| **D2** | External / runtime defense | **Out of tree** | ADAPTI-GUARD as one external defense under test ([`docs/D2_EXTERNAL_ADAPTI.md`](docs/D2_EXTERNAL_ADAPTI.md)). |

## Rules

- Default runs use **`--prompt-id d0`** / `AIB_PROMPT_ID=d0`.
- Do not claim D1/D2 results until those conditions are actually run and traced.
- Traces live under `results/traces/<run_id>/` and are not overwritten without `--force`.

See also: [`PHASE_C.md`](PHASE_C.md), [`QUALITY_TABLE_V0.md`](QUALITY_TABLE_V0.md), [`docs/ASR_LEVELS.md`](docs/ASR_LEVELS.md).
