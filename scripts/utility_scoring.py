"""Utility scoring helpers. Heuristic only — not an LLM judge."""

from __future__ import annotations

from typing import Any, Literal


def _contains(haystack: str, needle: str) -> bool:
    return needle.lower() in haystack.lower()


def utility_success(
    episode: dict[str, Any],
    trace: dict[str, Any],
    *,
    match: Literal["all", "any"] = "all",
) -> tuple[bool | None, str | None]:
    """Return (success, skip_reason).

    Primary: utility_answer_contains with AND (all) or OR (any).
    Optional: utility_must_not_contain — any hit fails utility.
    """
    expected = episode.get("expected") or {}
    needles = list(expected.get("utility_answer_contains") or [])
    if not needles:
        return None, "no_needles"
    answer = str(trace.get("final_answer") or "")
    banned = list(expected.get("utility_must_not_contain") or [])
    for phrase in banned:
        if phrase and _contains(answer, phrase):
            return False, None
    if match == "any":
        hit = any(_contains(answer, n) for n in needles if n)
    else:
        hit = all(_contains(answer, n) for n in needles if n)
    return hit, None
