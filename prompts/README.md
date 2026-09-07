# Prompt conditions (AIB)

| Id | File | Role |
| --- | --- | --- |
| **d0** | [`d0_undefended.txt`](d0_undefended.txt) | Default **undefended** measurement baseline (D0). No protective / anti-injection system wording. |
| **d1** | [`d1_prompt_defense.txt`](d1_prompt_defense.txt) | Minimal **prompt-level** defense for Phase C matrix cells. Not ADAPTI. Not default. |

**D2** (ADAPTI-GUARD / runtime) is out of tree — see [`../docs/D2_EXTERNAL_ADAPTI.md`](../docs/D2_EXTERNAL_ADAPTI.md) and [`../BASELINES.md`](../BASELINES.md).

Select via `--prompt-id d0|d1` / `--prompt d0|d1` or env `AIB_PROMPT_ID` (default `d0`).

**D0 rule:** do not add anti-injection guardrail wording to `d0_undefended.txt`.
