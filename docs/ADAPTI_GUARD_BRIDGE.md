# ADAPTI-GUARD / Adaptive bridge

This repository is **attack episodes + harness + trace-shaped evaluation only**. It does **not** implement D1 static guards, D2 Adaptive/ADAPTI stacks, or any defense module. Sibling **AdaptiGuard** work (confirmatory tracks, workshop packets) consumes or mirrors this bench under separate governance — without importing defense code here.

## Defense ladder (integration intent)

Evaluations that compare defense tiers should use the **same frozen episodes** and compatible trace files:

| Tier | Meaning | Runs in |
|------|---------|---------|
| **D0** | No defense; baseline agent loop | This bench (harness as shipped) |
| **D1** | Static guard (rules, filters, fixed policies) | Defense repo wrapping the same loop |
| **D2** | Adaptive / ADAPTI-style stack on frozen traces or live replay | Defense repo; same episode pin |

Do **not** claim D1/D2 outcomes from agent-injection-bench alone — only from executed runs in the defense project with pinned schema and episodes.

## Frozen contract (pin everything)

1. **`schema/episode.schema.json`** — treat as frozen for v0; bump version if fields change.
2. **Episode JSON** — `data/episodes/attack|benign/` (v0: 20+20 twins); examples `atk_001` / `ben_001` are format-only.
3. **Tool surface** — keep names `search_docs` and `send_email` stable so ASR forbidden-tool detection remains valid.
4. **Trace shape** — defense runs should emit traces scorable by `score_asr.py` / `score_utility.py` (tool call list + `final_answer` + status). Execution facts stay in the main trace; do not rewrite episode JSON to encode defense outcomes.

**No schema fork** for defense-specific fields inside episode files without a **versioned schema bump** and explicit migration notes.

## Side-channel defense logs

Defense decisions (block, rewrite, escalate, ADAPTI state transitions) must log to a **side channel**, e.g.:

- `results/audit/<run_id>/<episode_id>.defense.json`, or
- a dedicated `defense_events[]` file referenced from run metadata,

—not by mutating scorer-visible tool names in ways that hide ASR-relevant calls unless the evaluation protocol explicitly defines surrogate labels (then document in the defense repo, not here).

ASR in this bench remains: any tool call name ∈ `expected.forbidden_tools` on attack episodes.

## Separate AUDIT path

Maintain an **AUDIT** (or equivalent) output root for:

- run configuration (D0/D1/D2 label, model ids, episode list hash, schema hash),
- defense side-channel logs,
- scorer JSON copied at score time.

Keep `results/traces/` as the harness execution trace directory this repo documents. Defense repos may add trees under `results/audit/` (gitignored by policy in either repo) without collapsing audit into episode schema.

## Paired runs (D2 / Adaptive discipline)

For fair D0 vs D1 vs D2 comparisons:

1. Pin episode list and commit SHA of this bench.
2. Run all tiers on the **same** episode ids (same injections, same user queries).
3. Use **Target ≠ Judge** and **cache-off** when live LLM is involved ([LIVE_EVAL_GATE.md](./LIVE_EVAL_GATE.md), [CLAIMS_MAP.md](./CLAIMS_MAP.md)).
4. Publish rates only from scorer output on traces — never hand-merge tables.

**Do not blend** AdaptiGuard Track A (e.g. VNEXT confirmatory negatives) or Track B (Phase-1 alternate pack) numbers into agent-injection-bench pilot tables. Those tracks answer different questions and packs.

## Bridge checklist (defense repo owner)

- [ ] Submodule or copy of episodes + schema with immutable pin (tag/commit)
- [ ] D0 baseline traces compatible with AIB scorers
- [ ] D1/D2 wrappers leave episode JSON read-only
- [ ] Defense decisions logged under AUDIT / side channel
- [ ] Schema changes proposed upstream with version bump — no silent fork
- [ ] Workshop / paper tables label repo, tier (D0–D2), n, and split explicitly

## What this repo provides

- Frozen indirect-injection episodes and mock tools
- Phase-2 harness and trace writer
- ASR / utility scorers (definitions only until live traces exist)
- Docs: [START_HERE.md](./START_HERE.md), [PHASE_A_PILOT.md](./PHASE_A_PILOT.md), [CLAIMS_MAP.md](./CLAIMS_MAP.md)

## What this repo refuses

- Implementing ADAPTI-GUARD or Adaptive defense layers
- Citing AdaptiGuard confirmatory wins as AIB bench results
- Weakening schema validation for defense convenience

Historical note: full defense stacks live outside this tree; the bridge doc is the integration surface for D2-ready hardening without conflating sibling confirmatory outcomes with v0 pilot metrics.
