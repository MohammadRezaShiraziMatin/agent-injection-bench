# Level B Harness — Phase 3 (Realistic Sandbox & D2 Hook Coverage)

**Document ID:** `aib-level-b-harness-phase3-v1`  
**Status:** **DESIGN / SCAFFOLDING** — no Level B live runs; paired scoring contract unchanged  
**Paired contract (unchanged):** [`../config/p4_3_paired_eval_contract.v1.json`](../config/p4_3_paired_eval_contract.v1.json), [`../scripts/score_p4_3_paired_metrics.py`](../scripts/score_p4_3_paired_metrics.py)

**Related:** [`ADAPTI_GUARD_BRIDGE.md`](./ADAPTI_GUARD_BRIDGE.md), [`AIB_LEVEL_B_EXPERIMENTAL_PROTOCOL.md`](./AIB_LEVEL_B_EXPERIMENTAL_PROTOCOL.md) §15–16, [`AIB_Q1_STRENGTHENING_4PHASE.md`](./AIB_Q1_STRENGTHENING_4PHASE.md)

---

## Purpose

Phase 3 adds **controlled realism** and **traceable D2 hook coverage** without live APIs, without new ASR tables, and without mutating Level A run bundles (`p42-primary-d0-d2-20260921T173736Z-controlled`, P3-EXT).

---

## Harness loop (sandbox)

```text
episode load → tool_sandbox.reset_from_episode (permissions)
            → D0/D2 @ pre_target (tool_step_index = -1)
            → [optional] target LLM tool loop (max 6 steps)
                 → for each proposed tool (D2 only): D2 @ pre_tool_call (tool_step_index = 1..N)
                 → call_tool (sandbox policy + execution_recorder)
            → trace: harness_execution.defense_event (pre_target, paired contract)
                     harness_execution.defense_trace + hook_coverage_map (Phase 3)
                     harness_execution.tool_sandbox.call_log
```

**Still mock / offline:**

| Component | Phase 3 behavior | Not claimed |
|-----------|------------------|-------------|
| `search_docs` | Deterministic token match over episode `retrieved_docs` | Real RAG / web fetch |
| `send_email` | In-process log; `external_side_effect_occurred=false` | SMTP / S4 external delivery |
| Target LLM | Unchanged (gated by live eval) | — |
| AdaptiGuard | Pinned `CoreDefensePipeline` when installed; [`sandbox_double`](../agent/defense/sandbox_double.py) in offline unit tests | Production agent stack |

**Realistic upgrades (Phase 3):**

- Episode **`allowed_tools` / `forbidden_tools`** enforced in [`tools/tool_sandbox.py`](../tools/tool_sandbox.py) before tool execution (observable block + call log).
- **Privileged tool** metadata for `send_email` (aligns with AdaptiGuard `PRIVILEGED_TOOLS` naming).
- **Per-hook defense trace** with `trace_schema_version`, `tool_step_index`, and `hook_coverage_map` in `harness_execution`.

---

## D2 hook coverage map

| Hook point | Index | Production path | Phase 3 coverage |
|------------|-------|-----------------|------------------|
| `pre_target` | `-1` | `apply_defense` → AdaptiGuard bridge | **Implemented** — all D0/D2 runs |
| `pre_tool_call` | `1..N` | `apply_defense_at_hook` → bridge or sandbox double | **Implemented** — D2 live loop only (not dry-run) |
| `post_tool_call` | — | Future tool-loop re-guard | **Deferred** — recorded in map with `deferred: true` |

**Trace fields** (see [`agent/defense/hook_trace.py`](../agent/defense/hook_trace.py)):

- `trace_schema_version`: `aib-harness-trace-v1-phase3`
- `defense_trace[]`: `{ hook_point, tool_step_index, defense_event }`
- `hook_coverage_map`: per-hook `covered`, `tool_step_indices`, deferred note for `post_tool_call`

**Paired scoring:** Top-level `defense_event` remains the **pre_target** decision for D0/D2 parity with Level A artifacts. Step-indexed events live in `defense_trace` (side channel per bridge integrity rules).

---

## Offline verification

```bash
python3 scripts/verify_level_b_harness_phase3.py
pytest tests/test_level_b_harness_phase3.py -q
```

No network, no OpenRouter, no AdaptiGuard required for the Phase 3 unit tests (sandbox double). CI still runs full D2 integration when `external/adapti-guard` is present.

---

## Gap list vs Level B protocol §15–16

| Requirement | Status | Notes |
|-------------|--------|-------|
| Documented tool paths (`search_docs`, `send_email`) | **Closed** | Same tool names as Level A |
| Observable execution / side-effect metadata | **Closed** | `execution_recorder` + sandbox call log |
| Episode permission policy | **Closed** | Sandbox enforces allowed/forbidden |
| `trace_schema_version` | **Closed** | Phase 3 schema id in traces |
| `hook_coverage_map` + `tool_step_index` | **Closed (scaffold)** | pre_target + pre_tool_call; post_tool deferred |
| Full AdaptiGuard on every tool step in production | **Deferred** | pre_tool uses bridge when integrated; post_tool hook TBD |
| External S4 side effects | **Deferred** | Out of scope until non-sandbox instrumentation |
| DB / HTTP / filesystem tool surface | **Deferred** | Not required for P4.2/P3 episode classes |
| Level B live evidence | **Deferred** | Phase 4 only |

**Researcher sign-off:** Deferred items are explicit blockers for **claim** upgrade, not for merging Phase 3 scaffolding.

---

## Explicit non-claims

- Sandbox realism does **not** prove production security or benchmark completeness.
- Hook trace tests are **not** ASR, utility, or paired defense-rate outcomes.
- Phase 3 does **not** authorize live Level B runs or flip live eval gates.
