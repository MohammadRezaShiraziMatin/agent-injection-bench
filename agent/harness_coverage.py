"""Measure P4.2 harness executability from implementation (does not mutate episodes)."""

from __future__ import annotations

import json
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

from agent.execution_context import EpisodeExecutionContext
from agent.surface_adapters import build_initial_messages

ROOT = Path(__file__).resolve().parents[1]
P42_ROOT = ROOT / "data" / "episodes_p4_2"

# Surfaces that count toward full execution when present in episode.harness_surfaces.
_ADAPTIVE_LOOP_SURFACE = "adaptive_loop"
_MULTI_AGENT_SURFACE = "multi_agent_channel"


def _iter_p42_episodes() -> list[dict[str, Any]]:
    paths = sorted((P42_ROOT / "attack").glob("*.json")) + sorted((P42_ROOT / "benign").glob("*.json"))
    return [json.loads(p.read_text(encoding="utf-8")) for p in paths]


def _harness_v0_consumed(_episode: dict[str, Any]) -> set[str]:
    return {"user_query", "retrieved_docs"}


def _harness_p424_consumed(episode: dict[str, Any]) -> set[str]:
    ctx = EpisodeExecutionContext.from_episode(episode)
    build_initial_messages(episode, ctx)
    consumed = ctx.consumed_surface_names()
    if _ADAPTIVE_LOOP_SURFACE in (episode.get("execution") or {}).get("harness_surfaces", []):
        if episode.get("adaptive_trace"):
            consumed.add(_ADAPTIVE_LOOP_SURFACE)
    return consumed


def _classify_episode(
    episode: dict[str, Any],
    *,
    consumed_fn,
) -> str:
    exec_meta = episode.get("execution") or {}
    required = set(exec_meta.get("harness_surfaces") or [])
    family = (episode.get("taxonomy") or {}).get("family", "")

    if family == "multi_agent_injection" or _MULTI_AGENT_SURFACE in required:
        return "DESIGNED_NOT_EXECUTABLE"

    consumed = consumed_fn(episode)

    if family == "adaptive_injection":
        if episode.get("adaptive_trace") and _ADAPTIVE_LOOP_SURFACE in consumed:
            return "PARTIALLY_EXECUTABLE"
        return "DESIGNED_NOT_EXECUTABLE"

    if not required:
        return exec_meta.get("executability", "PARTIALLY_EXECUTABLE")

    missing = required - consumed
    if not missing:
        return "EXECUTABLE"
    return "PARTIALLY_EXECUTABLE"


def measure_authored_coverage() -> dict[str, Any]:
    """Counts from frozen episode metadata (P4.2.3 / pre-adapter baseline)."""
    episodes = _iter_p42_episodes()
    status_counts: Counter[str] = Counter()
    by_family: dict[str, Counter[str]] = defaultdict(Counter)
    for ep in episodes:
        status = (ep.get("execution") or {}).get("executability", "UNKNOWN")
        status_counts[status] += 1
        family = (ep.get("taxonomy") or {}).get("family", "unknown")
        by_family[family][status] += 1
    return {
        "harness": "authored_p4_2_metadata",
        "n_episodes": len(episodes),
        "executability": dict(status_counts),
        "by_family": {k: dict(v) for k, v in sorted(by_family.items())},
        "missing_surface_counts": {},
    }


def measure_coverage(*, harness: str = "p4.2.4") -> dict[str, Any]:
    """Return executability counts and breakdowns for P4.2 episodes."""
    episodes = _iter_p42_episodes()
    consumed_fn = _harness_p424_consumed if harness == "p4.2.4" else _harness_v0_consumed

    status_counts: Counter[str] = Counter()
    by_family: dict[str, Counter[str]] = defaultdict(Counter)
    by_surface_gap: Counter[str] = Counter()

    for ep in episodes:
        status = _classify_episode(ep, consumed_fn=consumed_fn)
        status_counts[status] += 1
        family = (ep.get("taxonomy") or {}).get("family", "unknown")
        by_family[family][status] += 1
        if status != "EXECUTABLE":
            required = set((ep.get("execution") or {}).get("harness_surfaces") or [])
            consumed = consumed_fn(ep)
            for surf in sorted(required - consumed):
                by_surface_gap[surf] += 1

    return {
        "harness": harness,
        "n_episodes": len(episodes),
        "executability": dict(status_counts),
        "by_family": {k: dict(v) for k, v in sorted(by_family.items())},
        "missing_surface_counts": dict(by_surface_gap),
    }


def compare_before_after() -> dict[str, Any]:
    before = measure_authored_coverage()
    after = measure_coverage(harness="p4.2.4")
    return {"before": before, "after": after}
