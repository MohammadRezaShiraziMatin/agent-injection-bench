# Prompt conditions (AIB)

| Id | File | Role |
| --- | --- | --- |
| **d0** | [`d0_undefended.txt`](d0_undefended.txt) | Default **undefended** measurement baseline (D0). No protective / anti-injection system wording. |
| **d1** | [`d1_prompt_defense.txt.example`](d1_prompt_defense.txt.example) | **Reserved** prompt-level defense sketch only. Not default. Not a strong/evaluated defense. |

**D2** (ADAPTI-GUARD / runtime) is out of tree — see [`../BASELINES.md`](../BASELINES.md).

**D0 rule:** do not add instructions to ignore retrieved documents, refuse tool use from documents, or otherwise act as a hidden guardrail in `d0_undefended.txt`.
