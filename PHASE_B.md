# Phase B — research-grade evaluation layer (pilot+)

Builds on Phase A packaging ([`PHASE_A.md`](PHASE_A.md)). Still **not publication-ready**. Keep N=20+20. No ADAPTI/defense code. No fabricated metrics.

## Checklist for Matin

1. Sync Desktop to the Phase B HEAD (`git pull` or desktop tarball).
2. Package checks: `pip install -e ".[dev]"` → `python scripts/validate_episodes.py` → `python -m pytest`
3. Taxonomy: `python scripts/report_taxonomy.py` (see [`TAXONOMY.md`](TAXONOMY.md))
4. Dataset QA: `python scripts/qa_episodes.py` → read [`QA_REPORT.md`](QA_REPORT.md)
5. After live D0 traces exist under `results/traces/<run_id>/`:
   ```bash
   python scripts/score_asr.py --level 0 --traces-dir results/traces/<run_id>
   python scripts/score_asr.py --level 1 --traces-dir results/traces/<run_id>
   python scripts/score_utility.py --traces-dir results/traces/<run_id>          # AND needles
   python scripts/score_utility.py --match any --traces-dir results/traces/<run_id>  # optional OR
   ```
6. Manifests include `dataset_version` (content hash) — cite it with any pilot numbers.
7. Report honestly: N, skipped, ASR-L0, ASR-L1, utility (AND); null if N=0. No overclaim.

## What Phase B adds

| Item | Status |
| --- | --- |
| ASR L1 tool+args | Implemented (`--level 1`); L0 remains default |
| Utility AND (+ optional OR, must_not) | Implemented; still substring heuristic |
| Attack taxonomy families | Tagged + `report_taxonomy.py` |
| Dataset QA | `qa_episodes.py` + `QA_REPORT.md` |
| `dataset_version` on manifests | Implemented |

## Non-goals

- No dataset growth beyond 20+20  
- No in-repo ADAPTI / D2  
- No LLM-as-judge utility  
- No published leaderboard claims  
