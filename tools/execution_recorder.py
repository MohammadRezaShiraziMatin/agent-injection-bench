"""Sandbox execution event recorder (in-process; no network)."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any


@dataclass
class ExecutionEvent:
    step: int
    tool: str
    arguments: dict[str, Any]
    proposed: bool
    execution_started: bool
    execution_completed: bool
    execution_succeeded: bool
    blocked: bool
    block_reason: str | None
    side_effect_attempted: bool
    side_effect_occurred: bool
    external_side_effect_occurred: bool
    side_effect_type: str | None
    timestamp: str

    def to_dict(self) -> dict[str, Any]:
        return {
            "step": self.step,
            "tool": self.tool,
            "arguments": self.arguments,
            "tool_proposed": self.proposed,
            "tool_called": self.execution_started,
            "execution_started": self.execution_started,
            "execution_completed": self.execution_completed,
            "execution_succeeded": self.execution_succeeded,
            "blocked": self.blocked,
            "block_reason": self.block_reason,
            "side_effect_attempted": self.side_effect_attempted,
            "side_effect_occurred": self.side_effect_occurred,
            "external_side_effect_occurred": self.external_side_effect_occurred,
            "side_effect_type": self.side_effect_type,
            "timestamp": self.timestamp,
        }


@dataclass
class ExecutionRecorder:
    events: list[ExecutionEvent] = field(default_factory=list)
    _step: int = 0

    def clear(self) -> None:
        self.events.clear()
        self._step = 0

    def record_proposal(
        self,
        tool: str,
        arguments: dict[str, Any],
        *,
        blocked: bool = False,
        block_reason: str | None = None,
    ) -> ExecutionEvent:
        self._step += 1
        ev = ExecutionEvent(
            step=self._step,
            tool=tool,
            arguments=dict(arguments),
            proposed=True,
            execution_started=False,
            execution_completed=False,
            execution_succeeded=False,
            blocked=blocked,
            block_reason=block_reason,
            side_effect_attempted=False,
            side_effect_occurred=False,
            external_side_effect_occurred=False,
            side_effect_type=None,
            timestamp=datetime.now(timezone.utc).isoformat(),
        )
        self.events.append(ev)
        return ev

    def record_execution(
        self,
        tool: str,
        arguments: dict[str, Any],
        *,
        succeeded: bool,
        side_effect_attempted: bool,
        side_effect_occurred: bool,
        external_side_effect_occurred: bool,
        side_effect_type: str | None,
        blocked: bool = False,
        block_reason: str | None = None,
    ) -> ExecutionEvent:
        self._step += 1
        ev = ExecutionEvent(
            step=self._step,
            tool=tool,
            arguments=dict(arguments),
            proposed=True,
            execution_started=True,
            execution_completed=True,
            execution_succeeded=succeeded,
            blocked=blocked,
            block_reason=block_reason,
            side_effect_attempted=side_effect_attempted,
            side_effect_occurred=side_effect_occurred,
            external_side_effect_occurred=external_side_effect_occurred,
            side_effect_type=side_effect_type,
            timestamp=datetime.now(timezone.utc).isoformat(),
        )
        self.events.append(ev)
        return ev

    def to_trace(self) -> list[dict[str, Any]]:
        return [e.to_dict() for e in self.events]


_RECORDER = ExecutionRecorder()


def get_recorder() -> ExecutionRecorder:
    return _RECORDER


def clear_recorder() -> None:
    _RECORDER.clear()
