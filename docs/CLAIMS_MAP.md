# Claims map (allowed vs forbidden)

Use this before citing numbers, writing slides, or merging results across repos. When in doubt, say **“not measured in this tree”** or point to the claim ladder in [`../paper/RESULTS_EVIDENCE.md`](../paper/RESULTS_EVIDENCE.md).

## Claim levels (research evidence)

| Level | Allowed (examples) | Forbidden / misleading |
|-------|-------------------|-------------------------|
| **Level A (current on `main`)** | Sample-level ASR, Utility, FPR, paired transitions on **named immutable run IDs** (e.g. `p42-primary-d0-d2-20260921T173736Z-controlled`, P3-EXT COV-B); protocol and artifact provenance; descriptive D0 vs D2 on the same paired set; D2 integration **on the recorded path** | Defense **effectiveness**, superiority, SOTA, production readiness; significance or population generalization; implying P3-EXT alone is Level B |
| **Level B (future)** | (Nothing yet — requires new protocol + fresh runs) | Relabeling Level A runs; pooling COV-A and COV-B without a frozen plan; efficacy or confirmatory language |
| **Level C (future)** | (Not defined by current evidence) | Security-venue readiness claims without new frozen protocols |

Gap plan: [AIB_P2_Q1_EVIDENCE_GAP_PLAN.md](./AIB_P2_Q1_EVIDENCE_GAP_PLAN.md). Q1 strengthening roadmap: [AIB_Q1_STRENGTHENING_4PHASE.md](./AIB_Q1_STRENGTHENING_4PHASE.md) · Level B protocol (DESIGN): [AIB_LEVEL_B_EXPERIMENTAL_PROTOCOL.md](./AIB_LEVEL_B_EXPERIMENTAL_PROTOCOL.md) · Phase 4 prelive lock/freeze (no live): [AIB_LEVEL_B_PHASE4_PRELIVE.md](./AIB_LEVEL_B_PHASE4_PRELIVE.md).

## Operational modes (v0 harness vs research runs)

| Mode | What it proves | What it does **not** prove |
|------|----------------|----------------------------|
| **API=0** (no key) | Data valid; code path; mock tools; trace write shape | Model behavior, ASR, utility, Level A paired metrics |
| **Dry-run** | Same as API=0 for pipeline | Pilot results, attack success, benign completion, research ASR |
| **Live v0 pilot** (`results/traces/`) | Model outcomes in local traces when gate-approved | Defense benefit; Level B; full research protocol compliance by itself |
| **Frozen paired runs** (`results/p4_2_paired/`, `results/p3_paired/`, etc.) | Level A descriptive metrics when scored per frozen protocol | Anything beyond [`RESULTS_EVIDENCE.md`](../paper/RESULTS_EVIDENCE.md) exclusions |

**Rules**

- **`n=0` and `rate=null`** from v0 scorers mean **no result** — not “0% ASR” and not “safe.”
- **Dry-run ≠ pilot ≠ Level A research run.** Do not score dry-run traces as evaluation results.
- **Partial batches** (e.g. `--limit 4`) must be labeled partial, not full v0 or primary population.

## Live LLM discipline (when gate allows)

| Rule | Rationale |
|------|-----------|
| **Target ≠ Judge** | The model under test must not be the same endpoint used to grade open-ended compliance unless a separate judge pass with frozen rubric is explicitly part of the protocol |
| **Cache off** | Disable provider/client caching so traces reflect actual inference |
| **Refusals ≠ defense wins** | Benign refusals are utility / FPR concerns, not proof that a defense blocked injection |
| **Trace facts only** | Labels come from scorer rules on traces or frozen paired RESULTS — not narrative reinterpretation |

## v0 harness results (`score_asr.py` / `score_utility.py`)

| Claim | Allowed when | Forbidden |
|-------|----------------|-----------|
| ASR on v0 attack split | JSON from **live** traces covering the intended episode set; archived with model + date | Percentages with `n=0` or `rate=null`; dry-run traces scored as pilot; hand-entered rates |
| Utility on v0 benign split | Same via `score_utility.py` on live traces | Partial batch reported as full v0 pilot without labeling |
| “v0 Phase A pilot complete” | 40 live traces (`atk_002`–`021`, `ben_002`–`021`), dry-run cleared, scorers run | Dry-run only; smoke of 2 episodes called “full eval” |

## AdaptiGuard sibling (never blend into AIB tables)

| Source | May cite in AIB docs/README? |
|--------|------------------------------|
| AIB paired scorers on **pinned AIB run IDs** | Yes, with n, split, run ID, and Level A wording |
| AdaptiGuard Track A (e.g. VNEXT confirmatory) | **No** in the same table as AIB primary metrics |
| AdaptiGuard Track B (Phase-1 scoped pack) | **No** — different pack / scope |
| Layer A diagnostic closures | **No** as bench wins — diagnostics only |

**Rule:** Never merge sibling Track A/B numbers into agent-injection-bench result tables or imply AdaptiGuard “wins” from scaffold or Level A descriptive runs alone.

## Defenses

| Claim | Status |
|-------|--------|
| “ADAPTI / Adaptive **reduced ASR** in general” | **Forbidden** at Level A — descriptive D0/D2 only on recorded runs |
| “Bridge invokes pinned D2 on approved paths” | Allowed with pin + [ADAPTI_GUARD_BRIDGE.md](./ADAPTI_GUARD_BRIDGE.md) |
| “D5 production ready” | Forbidden without new executed paired evidence |

## Paper / external prose

Allowed: v0 design, indirect injection setting, metric **definitions**, Level A sample observations with run IDs, honest gaps for Level B.

Forbidden: fabricated ASR/utility; conflating dry-run with pilot; citing sibling confirmatory outcomes as if measured on this bench without pinned cross-run; population-level efficacy from n=9 primary or descriptive extensions alone.

See also: [START_HERE.md](./START_HERE.md), [LIVE_EVAL_GATE.md](./LIVE_EVAL_GATE.md), [PHASE_A_PILOT.md](./PHASE_A_PILOT.md), [STATUS.md](./STATUS.md).
