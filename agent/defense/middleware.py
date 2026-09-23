"""Defense middleware: D0 passthrough; D2 delegates to AdaptiGuard bridge when integrated."""

from __future__ import annotations

import time
from dataclasses import replace
from typing import Any

from agent.defense.adaptiguard_bridge import apply_adaptiguard, integration_status
from agent.defense.hook_trace import HOOK_PRE_TARGET
from agent.defense.sandbox_double import sandbox_defense_passthrough
from agent.defense.types import DefenseAction, DefenseCondition, DefenseApplyResult, DefenseEvent


def _d0_event(latency_ms: int) -> DefenseEvent:
    return DefenseEvent(
        defense_enabled=False,
        defense_backend="none",
        detector_invoked=False,
        detector_result=None,
        risk_score=None,
        risk_level=None,
        decision=DefenseAction.ALLOW.value,
        block=False,
        transform_applied=False,
        reason="D0_no_defense",
        category=None,
        latency_ms=latency_ms,
        defense_error=False,
        integration_status="not_applicable",
    )


def apply_defense(
    *,
    condition: DefenseCondition,
    episode: dict[str, Any],
    messages: list[dict[str, Any]],
    dry_run: bool = False,
) -> DefenseApplyResult:
    """Run defense on harness messages before target model invocation."""
    t0 = time.perf_counter()

    if condition == DefenseCondition.D0:
        ms = int((time.perf_counter() - t0) * 1000)
        return DefenseApplyResult(messages=messages, event=_d0_event(ms), skip_target_model=False)

    status = integration_status()
    if not status.get("integrated"):
        ms = int((time.perf_counter() - t0) * 1000)
        event = DefenseEvent(
            defense_enabled=True,
            defense_backend="adaptiguard",
            detector_invoked=False,
            detector_result=None,
            risk_score=None,
            risk_level=None,
            decision=DefenseAction.ERROR.value,
            block=False,
            transform_applied=False,
            reason=status.get("reason", "not_integrated"),
            category="integration",
            latency_ms=ms,
            defense_error=True,
            integration_status=status.get("status", "NOT_INTEGRATED"),
        )
        if dry_run:
            return DefenseApplyResult(
                messages=messages,
                event=event,
                skip_target_model=True,
                synthetic_final_answer="[dry-run] D2 defense not integrated — target skipped",
            )
        raise RuntimeError(f"D2 AdaptiGuard not integrated: {status.get('reason')}")

    return apply_adaptiguard(episode=episode, messages=messages, dry_run=dry_run, t0=t0)


def _with_hook_metadata(event: DefenseEvent, hook_point: str, tool_step_index: int) -> DefenseEvent:
    extra = dict(event.extra)
    extra["hook_point"] = hook_point
    extra["tool_step_index"] = tool_step_index
    return replace(event, extra=extra)


def apply_defense_at_hook(
    *,
    condition: DefenseCondition,
    episode: dict[str, Any],
    messages: list[dict[str, Any]],
    hook_point: str,
    tool_step_index: int,
    dry_run: bool = False,
    allow_sandbox_double: bool = True,
) -> DefenseApplyResult:
    """Defense at a named harness hook (pre_target or pre_tool_call)."""
    if condition == DefenseCondition.D0:
        t0 = time.perf_counter()
        ms = int((time.perf_counter() - t0) * 1000)
        return DefenseApplyResult(
            messages=messages,
            event=_with_hook_metadata(_d0_event(ms), hook_point, tool_step_index),
            skip_target_model=False,
        )

    if hook_point == HOOK_PRE_TARGET:
        result = apply_defense(
            condition=condition,
            episode=episode,
            messages=messages,
            dry_run=dry_run,
        )
    elif integration_status().get("integrated"):
        result = apply_adaptiguard(episode=episode, messages=messages, dry_run=dry_run, t0=time.perf_counter())
    elif allow_sandbox_double:
        result = sandbox_defense_passthrough(
            messages=messages,
            hook_point=hook_point,
            tool_step_index=tool_step_index,
        )
    else:
        result = apply_defense(condition=condition, episode=episode, messages=messages, dry_run=dry_run)

    return DefenseApplyResult(
        messages=result.messages,
        event=_with_hook_metadata(result.event, hook_point, tool_step_index),
        skip_target_model=result.skip_target_model,
        synthetic_final_answer=result.synthetic_final_answer,
    )
