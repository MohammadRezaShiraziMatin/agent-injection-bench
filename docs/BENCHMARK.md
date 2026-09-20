# Benchmark design

## Objective

Measure **indirect prompt injection** that tries to induce a **forbidden tool call** in a tool-using agent, with paired **benign utility** checks. v0 is a **small pilot** (20 attack + 20 benign twins), not a large security suite or leaderboard.

## Application model

- Episodes are static JSON; retrieval is **pre-bound** to `retrieved_docs`.
- Harness: bounded tool loop, auditable traces, mock tools only.
- **Target** in v0: misuse via `send_email` when listed in `expected.forbidden_tools`.

## Defense conditions

| Id | Name | In this repo | Role |
| --- | --- | --- | --- |
| **D0** | Undefended | `prompts/d0_undefended.txt` | Default measurement baseline; no anti-injection system wording |
| **D1** | Prompt-level | `prompts/d1_prompt_defense.txt` | Minimal instruction for matrix cells; **not** a strong/production defense claim |
| **D2** | External / ADAPTI-GUARD | **Not implemented** | Defended runner out of tree — [ADAPTI_GUARD_BRIDGE.md](./ADAPTI_GUARD_BRIDGE.md) |

Select via `--prompt-id d0|d1` or `AIB_PROMPT_ID`. Traces store `prompt_id` and `defense_condition`.

## What is measured vs not (v0)

| Topic | v0 status | Notes |
| --- | --- | --- |
| Indirect PI via `retrieved_docs` | Setup yes | Twin attack/benign; honest `user_query` |
| ASR-L0 (tool name) | Defined | `scripts/score_asr.py --level 0` |
| ASR-L1 (tool + args) | Defined | `--level 1`; see [EVALUATION.md](./EVALUATION.md) |
| ASR-L2 (side effect) | No | Mocks only log → `rate=null` |
| Benign utility | Heuristic | Substring match; not an LLM judge |
| False-refusal rate | No | Explicitly N/A in scorers |
| Defense effectiveness | No in-repo | D2 external only |
| Multi-model leaderboard | Not claimed | Matrix scripts are pilot methodology |
| Dynamic / stateful env | No | Fixed episodes |

## Canonical `execution_status`

| Value | Scorable for ASR/utility? |
| --- | --- |
| `ok`, `max_steps` | Yes (if not dry-run) |
| `error` | **No** (API/harness failure — not attack success) |
| `dry_run` | **No** (pipeline inspect only) |

## Phase matrices (methodology only)

- **Phase A:** dual-model D0 batch — `scripts/phase_a_pilot.sh`
- **Phase C:** models × {D0,D1} × K repeats — `scripts/phase_c_matrix.sh`, aggregate via `scripts/aggregate_phase_c.py`

No fabricated rates. Pilot matrices ≠ publication tables until live scorable traces exist.

## Evidence map (high level)

Detailed claim → artifact mapping: [CLAIMS.md](./CLAIMS.md).
