# AIB P4.2.4 — Harness Surface Coverage Matrix

**Baseline (authored metadata, frozen dataset):** branch `cursor/p4-2-dataset-6db2`, freeze `aib-p4.2-frozen-v1.0` @ `3445f29`.

| Surface | Before (harness v0) | After (P4.2.4 adapters) | Adapter | Risk |
| --- | --- | --- | --- | --- |
| `user_query` | Consumed | Consumed | none (existing) | Low |
| `retrieved_docs` | Consumed | Consumed | none (existing) | Low |
| `tool_results` | Not consumed | Consumed (labeled replay block) | `surface_adapters` | Medium |
| `conversation` | Not replayed | Multi-turn replay in message list | `surface_adapters` | Medium |
| `memory_store` | Not loaded | Episode-isolated snapshot block | `execution_context` + adapter | High |
| `session_state` | Not loaded | Loaded when field present | `execution_context` + adapter | High |
| `cross_context` | Not injected | Separate labeled channel | `surface_adapters` | High |
| `inter_agent_messages` | No bus | Replay block; **EXPLICIT_UNSUPPORTED** for live bus | `surface_adapters` | High |
| `adaptive_trace` / `adaptive_loop` | No loop | **STATIC_REPLAY** only (not LIVE_ADAPTIVE) | `surface_adapters` | High |

Measurement: `python scripts/measure_p4_2_harness_coverage.py` (does not rewrite episode labels).
