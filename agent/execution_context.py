"""Per-episode execution context (isolated state, provenance)."""

from __future__ import annotations

import copy
from dataclasses import dataclass, field
from typing import Any

from agent.harness_meta import (
    EXECUTION_MODE_EXPLICIT_UNSUPPORTED,
    EXECUTION_MODE_STATIC_REPLAY,
)


@dataclass
class SurfaceRecord:
    surface: str
    execution_mode: str
    applied: bool
    detail: str | None = None


@dataclass
class EpisodeExecutionContext:
    """Mutable harness state for one episode run (not shared across episodes)."""

    episode_id: str
    memory_store: dict[str, str] = field(default_factory=dict)
    session_state: dict[str, Any] = field(default_factory=dict)
    surfaces: list[SurfaceRecord] = field(default_factory=list)

    @classmethod
    def from_episode(cls, episode: dict[str, Any]) -> EpisodeExecutionContext:
        ctx = cls(episode_id=str(episode.get("id", "")))
        for item in episode.get("memory_store") or []:
            if isinstance(item, dict) and item.get("key"):
                ctx.memory_store[str(item["key"])] = str(item.get("value", ""))
        raw_session = episode.get("session_state")
        if isinstance(raw_session, dict):
            ctx.session_state = copy.deepcopy(raw_session)
        return ctx

    def record(
        self,
        surface: str,
        *,
        execution_mode: str,
        applied: bool,
        detail: str | None = None,
    ) -> None:
        self.surfaces.append(
            SurfaceRecord(
                surface=surface,
                execution_mode=execution_mode,
                applied=applied,
                detail=detail,
            )
        )

    def provenance_dict(self) -> list[dict[str, Any]]:
        return [
            {
                "surface": s.surface,
                "execution_mode": s.execution_mode,
                "applied": s.applied,
                "detail": s.detail,
            }
            for s in self.surfaces
        ]

    def consumed_surface_names(self) -> set[str]:
        return {s.surface for s in self.surfaces if s.applied}
