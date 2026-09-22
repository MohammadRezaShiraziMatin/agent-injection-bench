"""Defense outcome types for D0/D2 evaluation (observable, non-secret)."""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from enum import Enum
from typing import Any


class DefenseCondition(str, Enum):
    D0 = "D0"
    D2 = "D2"


class DefenseAction(str, Enum):
    ALLOW = "allow"
    BLOCK = "block"
    TRANSFORM = "transform"
    DETECT_ONLY = "detect_only"
    ERROR = "error"
    TIMEOUT = "timeout"


@dataclass
class DefenseEvent:
    defense_enabled: bool
    defense_backend: str
    detector_invoked: bool
    detector_result: str | None
    risk_score: float | None
    risk_level: str | None
    decision: str
    block: bool
    transform_applied: bool
    reason: str | None
    category: str | None
    latency_ms: int
    defense_error: bool = False
    integration_status: str = "unknown"
    extra: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class DefenseApplyResult:
    messages: list[dict[str, Any]]
    event: DefenseEvent
    skip_target_model: bool = False
    synthetic_final_answer: str | None = None
