# Claims map (allowed vs forbidden)

Use this table before citing numbers, writing slides, or merging results across repos. When in doubt, say **“not measured in this tree.”**

## Evaluation results (this repo)

| Claim | Allowed when | Forbidden / misleading |
|-------|----------------|-------------------------|
| ASR on v0 attack split | `score_asr.py` JSON from **live** traces covering the intended episode set; archived with model + date | Any percentage with `n=0` or `rate=null`; hand-entered rates; dry-run traces scored as pilot |
| Utility on v0 benign split | Same as ASR via `score_utility.py` on live traces | Partial batch (e.g. `--limit 4`) reported as full v0 pilot without labeling partial |
| “Phase A pilot complete” | 40 live traces (`atk_002`–`021`, `ben_002`–`021`), scorers run after clearing dry-run files, evidence archived | Dry-run only; smoke of 2 episodes called “full eval” |
| Harness / schema health | `validate_episodes.py` ok; pytest green; dry-run exit 0 | Implying security posture or defense effectiveness |

## Operational modes

| Mode | What it proves | What it does **not** prove |
|------|----------------|----------------------------|
| **API=0** (no key) | Data valid; code path; mock tools; trace write shape | Model behavior, ASR, utility |
| **Dry-run** | Same as API=0 for pipeline | Pilot results, attack success, benign task completion |
| **Live pilot** | Model + episode outcomes in traces | Defense benefit (no defense in this repo) |

**Rule:** `n=0` and `rate=null` from scorers mean **no result** — not “0% ASR” and not “safe.”

## Live LLM discipline (when gate allows)

| Rule | Rationale |
|------|-----------|
| **Target ≠ Judge** | The model under test must not be the same endpoint used to grade open-ended “did it comply?” labels unless explicitly designed as a separate judge pass with frozen rubric |
| **Cache off** | Provider-side or client caching must be disabled for any future live eval so traces reflect actual inference, not stale completions |
| **Refusals ≠ defense wins** | A model refusing a benign task is a **utility / false-refusal** concern, not evidence that a defense blocked an injection |
| **Trace facts only** | Success labels for ASR/utility come from scorer rules on traces, not from narrative reinterpretation |

## AdaptiGuard sibling (never blend into AIB tables)

| Source | May cite in AIB docs/README? |
|--------|------------------------------|
| AIB `score_*` on AIB traces | Yes, with n and split stated |
| AdaptiGuard Track A (e.g. VNEXT confirmatory) | **No** in the same table as AIB pilot ASR/utility |
| AdaptiGuard Track B (Phase-1 scoped pack) | **No** — different episode pack / scope |
| Layer A diagnostic closures | **No** as bench wins — diagnostics only |
| D0 → D1 → D2 defense runs | Only from **paired** defense-repo traces on **pinned** episodes; see [ADAPTI_GUARD_BRIDGE.md](./ADAPTI_GUARD_BRIDGE.md) |

**Rule:** Never merge AdaptiGuard Track A/B numbers into agent-injection-bench result tables or imply AdaptiGuard “wins” from this scaffold alone.

## Defenses

| Claim | Status in this repo |
|-------|---------------------|
| “ADAPTI / Adaptive reduced ASR here” | **Forbidden** — no defense code in tree |
| “Bridge ready for D2 eval” | Allowed as **integration intent** if schema pin + side-channel logging documented |
| “D5 production ready” | Forbidden without executed paired runs in defense repo |

## Paper / external prose

Allowed: describe v0 design, indirect injection setting, metric **definitions**, and honest “rates pending traces.”  
Forbidden: fabricated ASR/utility, conflating dry-run with pilot, citing AdaptiGuard confirmatory outcomes as if measured on this bench without a pinned cross-run.

See also: [START_HERE.md](./START_HERE.md), [LIVE_EVAL_GATE.md](./LIVE_EVAL_GATE.md), [PHASE_A_PILOT.md](./PHASE_A_PILOT.md).
