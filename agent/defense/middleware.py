"""Defense middleware: D0 passthrough; D2 delegates to AdaptiGuard bridge when integrated."""

from __future__ import annotations

import time
from typing import Any

from agent.defense.adaptiguard_bridge import apply_adaptiguard, integration_status
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
