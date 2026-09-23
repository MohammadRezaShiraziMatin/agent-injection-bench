"""Per-hook defense trace for Level B harness scaffolding (offline-safe)."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

TRACE_SCHEMA_VERSION = "aib-harness-trace-v1-phase3"

# Hook points aligned with docs/AIB_LEVEL_B_HARNESS_PHASE3.md and Level B protocol §16.
HOOK_PRE_TARGET = "pre_target"
HOOK_PRE_TOOL_CALL = "pre_tool_call"
HOOK_POST_TOOL_CALL = "post_tool_call"

DEFERRED_HOOKS = frozenset({HOOK_POST_TOOL_CALL})


@dataclass
class DefenseHookRecord:
    hook_point: str
    tool_step_index: int
    defense_event: dict[str, Any]

    def to_dict(self) -> dict[str, Any]:
        return {
            "hook_point": self.hook_point,
            "tool_step_index": self.tool_step_index,
            "defense_event": self.defense_event,
        }


@dataclass
class DefenseTraceRecorder:
    """Collects defense events with hook coverage map for harness_execution."""

    records: list[DefenseHookRecord] = field(default_factory=list)

    def clear(self) -> None:
        self.records.clear()

    def record(
        self,
        *,
        hook_point: str,
        tool_step_index: int,
        defense_event: dict[str, Any],
    ) -> None:
        enriched = dict(defense_event)
        extra = dict(enriched.get("extra") or {})
        extra["hook_point"] = hook_point
        extra["tool_step_index"] = tool_step_index
        enriched["extra"] = extra
        enriched["hook_point"] = hook_point
        enriched["tool_step_index"] = tool_step_index
        self.records.append(
            DefenseHookRecord(
                hook_point=hook_point,
                tool_step_index=tool_step_index,
                defense_event=enriched,
            )
        )

    def hook_coverage_map(self) -> dict[str, Any]:
        covered: dict[str, list[int]] = {
            HOOK_PRE_TARGET: [],
            HOOK_PRE_TOOL_CALL: [],
            HOOK_POST_TOOL_CALL: [],
        }
        for rec in self.records:
            covered.setdefault(rec.hook_point, []).append(rec.tool_step_index)
        for key in covered:
            covered[key] = sorted(set(covered[key]))

        return {
            "pre_target": {
                "covered": bool(covered[HOOK_PRE_TARGET]),
                "tool_step_indices": covered[HOOK_PRE_TARGET],
            },
            "pre_tool_call": {
                "covered": bool(covered[HOOK_PRE_TOOL_CALL]),
                "tool_step_indices": covered[HOOK_PRE_TOOL_CALL],
            },
            "post_tool_call": {
                "covered": bool(covered[HOOK_POST_TOOL_CALL]),
                "tool_step_indices": covered[HOOK_POST_TOOL_CALL],
                "deferred": HOOK_POST_TOOL_CALL in DEFERRED_HOOKS,
                "note": "post_tool_call recording deferred until AdaptiGuard tool-loop wiring (Phase 4 prep)",
            },
        }

    def to_harness_fields(self) -> dict[str, Any]:
        return {
            "trace_schema_version": TRACE_SCHEMA_VERSION,
            "defense_trace": [r.to_dict() for r in self.records],
            "hook_coverage_map": self.hook_coverage_map(),
        }
