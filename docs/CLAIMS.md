# Claims and evidence

Use before citing numbers, slides, or paper text. When in doubt: **not measured in this tree.**

## Supported now (artifact-only)

| Claim | Evidence |
| --- | --- |
| Indirect injection encoded in retrieved docs targeting forbidden tools | `data/episodes/attack/*.json`, `schema/episode.schema.json` |
| Benign **twin** design (shared `user_query`) | `scripts/qa_episodes.py`, `QA_REPORT.md` |
| D0/D1 harness with auditable traces | `scripts/run_agent.py`, `agent/traces.py`, tests |
| ASR-L0/L1 and utility **definitions** without LLM judges | `scripts/score_asr.py`, `scripts/score_utility.py`, tests |
| Empty/error evidence must not read as ASR=0 | Scorer skip rules; `rate=null` when `n=0` |
| Wilson CI helper when `n>0` | `scripts/aggregate_phase_c.py` |

## Allowed only after live scorable traces

| Claim | Requirement |
| --- | --- |
| ASR on attack split | `score_asr.py` JSON from **live** traces; archived with model + date |
| Utility on benign split | `score_utility.py` on live traces |
| D0 vs D1 comparison | Both cells run; report N and skipped per cell |
| “Pilot complete” (40 episodes) | Live traces for `atk_002`–`021` and `ben_002`–`021`, scorers run after excluding dry-run/error |

## Forbidden / misleading

- Percentages with `n=0` or `rate=null`
- Dry-run or smoke (2 episodes) as full v0 pilot
- D1 as strong, production-ready, or universal defense
- D2 / ADAPTI-GUARD results from this repo alone
- Deterministic reproduction claimed solely because seed is set
- Fabricated ASR, utility, latency, or token tables
- L2 side-effect success rates (not implemented)
- Blending **AdaptiGuard** confirmatory or Track A/B numbers into AIB result tables

## Operational modes

| Mode | Proves | Does not prove |
| --- | --- | --- |
| API=0 / offline | Schema, harness path, scorers | Model behavior, ASR, utility |
| Dry-run | Pipeline shape | Pilot results |
| Live pilot | Model outcomes in traces | In-repo defense benefit |

## Refusals

A model refusing a benign task is a **utility** concern, not evidence that a defense blocked an injection.

## Paper prose

Allowed: v0 design, threat model, metric definitions, honest “rates pending traces.”  
Forbidden: fabricated results; conflating dry-run with pilot; citing external defense wins without paired D2 traces on pinned episodes.

Paper checklist: [../paper/claims.md](../paper/claims.md).
