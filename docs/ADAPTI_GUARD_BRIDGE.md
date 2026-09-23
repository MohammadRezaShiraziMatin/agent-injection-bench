# ADAPTI-GUARD bridge

AIB does **not** vendor AdaptiGuard. D2 invokes the external **`adapti-guard`** package via `agent/defense/adaptiguard_bridge.py` and `agent/defense/adaptiguard_adapter.py`.

## Upstream location and pin

| Field | Value |
|--------|--------|
| Repository | https://github.com/MohammadRezaShiraziMatin/adapti-guard |
| Pinned commit | `30ddc756a07e3eae1f9afd5a3e9b9c68a7017f64` (`config/adaptiguard_version_pin.v1.json`) |
| Python package | `adapti-guard` 0.1.0 (`import adapti_guard`) |
| AIB entrypoint | `adapti_guard.core.core_pipeline.CoreDefensePipeline.run` |

**Not used:** `guard_messages(...)` — that name was an AIB placeholder; upstream exposes `EpisodeInput` + `CoreDefensePipeline.run`.

## Environment

Documented in `.env.example` (no secrets):

```bash
export AIB_ADAPTIGUARD_REPO=/path/to/adapti-guard   # git checkout at pinned commit
export AIB_ADAPTIGUARD_COMMIT=30ddc756a07e3eae1f9afd5a3e9b9c68a7017f64
pip install -e "$AIB_ADAPTIGUARD_REPO"
```

Commit pin is verified against `git rev-parse HEAD` in `AIB_ADAPTIGUARD_REPO` (or `external/adapti-guard` under the AIB root when present).

## Bridge behavior

```text
D0: defense_enabled=false → bypass AdaptiGuard (no detector call)
D2: defense_enabled=true  → CoreDefensePipeline.run(EpisodeInput)
```

AIB maps `episode.user_query` + `retrieved_docs` → `EpisodeInput(prompt, context)`.

AdaptiGuard policy actions map to AIB defense decisions:

| Upstream `policy_action` | AIB `decision` | Target routing |
|--------------------------|----------------|----------------|
| A0 NO_INTERVENTION | allow | target may run |
| A1 SANITIZE | transform | target may run (messages updated) |
| A2 TOOL_RESTRICTION | detect_only | target may run (tool_access recorded in extra) |
| A3 BLOCK | block | `skip_target_model=true` |

Exceptions from AdaptiGuard → `decision=error`, `defense_error=true` (not fail-open to allow).

## Failure semantics

Derived from `DefenseActionLayer` / pipeline trace: `blocked`, `allowed`, `policy_reason`, `tool_reason`. No silent conversion of exceptions to ALLOW.

## Verification

```bash
python scripts/verify_d2_integration.py
```

PASS requires: import, commit pin, smoke invocation, D0 bypass, D2 routing with decision captured.

Live paired benchmark remains gated separately (`live_d2_inference_allowed=false` in `config/p4_3_d2_eval_gate.v1.json`).

## Known limitations

- Pre-target hook only (first messages before target LLM); tool-loop re-guard not wired yet.
- `send_email` is privileged in AdaptiGuard `PRIVILEGED_TOOLS`; AIB tool names must stay stable for scoring.
- Phase-1 core pipeline is offline (regex detector); no target/judge API in integration smoke tests.

## Checklist (defense repo)

- [x] Pin commit in AIB config
- [x] Real `CoreDefensePipeline` invocation
- [ ] Full tool-loop defense on each tool step (future)
- [ ] Paired live D2 after explicit approval artifact

## Integrity rules (cross-run)

- **Episode/schema pin:** do not mutate episode JSON for defense outcomes; bump `schema/episode.schema.json` only with a versioned migration. Keep tool names (`search_docs`, `send_email`) stable for ASR rules.
- **Side-channel logs:** record defense decisions outside scorer-visible episode files (e.g. `results/audit/<run_id>/` or defense trace trees under paired run bundles) — not by hiding forbidden tool calls unless a frozen protocol defines surrogates.
- **Paired discipline:** D0/D1/D2 comparisons require the same episode ids and pinned bench commit; live work uses Target≠Judge and cache-off per [LIVE_EVAL_GATE.md](./LIVE_EVAL_GATE.md).
- **No table blending:** do not merge AdaptiGuard Track A/B or sibling confirmatory numbers into AIB primary tables — see [CLAIMS_MAP.md](./CLAIMS_MAP.md).
- **Claims:** Level A allows descriptive D0/D2 on recorded runs only; efficacy and Level B require new immutable protocols — [`../paper/RESULTS_EVIDENCE.md`](../paper/RESULTS_EVIDENCE.md).
