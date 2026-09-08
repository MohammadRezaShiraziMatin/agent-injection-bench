# PHASE_G — Paper evidence map

Map **claim → experiment → metric → artifact**. Only list claims the codebase can support. Unsupported claims are listed at the bottom.

| Claim (scoped) | Experiment | Metric | Artifact |
| --- | --- | --- | --- |
| Indirect injection can be encoded in retrieved docs targeting `send_email` | Episode set attack split | Qualitative / schema | `data/episodes/attack/*.json` |
| Twin design pairs attack/benign tasks | Dataset QA | Pair checks | `scripts/qa_episodes.py`, `QA_REPORT.md` |
| D0 undefended agent can be run with auditable traces | `run_agent` / `run_batch` | Trace completeness | `results/traces/<run_id>/`, manifests |
| D1 is a **minimal** prompt defense condition | Phase C matrix cell `--prompt-id d1` | ASR-L0/L1 vs D0 (when live) | traces + `aggregate_phase_c.py` |
| ASR can be scored at L0 and L1 without LLM judges | Offline scoring on traces | ASR-L0, ASR-L1 | `score_asr.py`, `asr_levels.py` |
| Empty / error evidence must not look like ASR=0 | Scorer skip rules | `rate=null`, skipped counts | `score_asr.py`, tests |
| Wilson CI available when n>0 | Aggregate Phase C | wilson95 | `aggregate_phase_c.py` |

## Unsupported / do not claim (current tree)

- Publication-grade benchmark ranking across models
- D1 is strong / production-ready / robust to all attacks
- Adaptive/D2 results (not implemented)
- Deterministic reproduction solely because seed is set
- Fabricated ASR/utility/latency/token tables
- L2 side-effect success (mocks only log)

## Limitations (must appear in paper text)

Small N; mock tools; substring utility; pre-bound retrieval; pilot Phase C; API nondeterminism.
