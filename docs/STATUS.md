# Status

**Entry:** [START_HERE.md](./START_HERE.md)

**v0 scaffold:** complete (data + harness + scorers + tests + Phase A runbook + D2 bridge docs).  
**Live Phase A pilot:** not completed on main until 40 live traces are archived and scored.  
**Evaluation numbers:** none published — no full live traces scored; do not invent ASR/utility ([CLAIMS_MAP.md](./CLAIMS_MAP.md)).

| Area | State |
|------|--------|
| Schema | Frozen draft-07 |
| Episodes | 20 attack + 20 benign + 2 examples |
| Harness | Phase 2 tool loop (max 6 steps) |
| Defenses | Intentionally absent |
| ASR / utility | Scorer code only; rates require traces |
| False-refusal | N/A |

## Recreated locally

This Desktop tree was **reimplemented from the recovered v0 specification** (cloud Origin HEAD `6d6eaf58` was not clonable from native Windows without Origin auth). Behavior and IDs match the spec; prose may differ from the private Origin copy.

## Next

1. `origin auth login` (WSL) **or** create a GitHub remote and push
2. Add `.env` with a key and run `run_batch.py`
3. Score with `score_asr.py` / `score_utility.py` and record rates only from that output
