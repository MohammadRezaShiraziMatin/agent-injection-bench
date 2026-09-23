"""Test/sandbox defense double — mirrors DefenseEvent shape without AdaptiGuard import."""

from __future__ import annotations

import time
from typing import Any

from agent.defense.types import DefenseAction, DefenseApplyResult, DefenseEvent


def sandbox_defense_passthrough(
    *,
    messages: list[dict[str, Any]],
    hook_point: str,
    tool_step_index: int,
    reason: str = "sandbox_trace_only",
) -> DefenseApplyResult:
    """Record a traceable ALLOW for offline tests when D2 package is absent."""
    t0 = time.perf_counter()
    ms = int((time.perf_counter() - t0) * 1000)
    event = DefenseEvent(
        defense_enabled=True,
        defense_backend="sandbox_double",
        detector_invoked=False,
        detector_result=None,
        risk_score=None,
        risk_level=None,
        decision=DefenseAction.ALLOW.value,
        block=False,
        transform_applied=False,
        reason=reason,
        category="sandbox",
        latency_ms=ms,
        defense_error=False,
        integration_status="SANDBOX_DOUBLE",
        extra={
            "hook_point": hook_point,
            "tool_step_index": tool_step_index,
            "production_path": "agent.defense.adaptiguard_bridge.apply_adaptiguard",
        },
    )
    return DefenseApplyResult(messages=messages, event=event, skip_target_model=False)
