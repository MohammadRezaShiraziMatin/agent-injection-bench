"""Map AIB episode JSON to AdaptiGuard EpisodeInput fields."""

from __future__ import annotations

from typing import Any


def build_retrieved_context(episode: dict[str, Any]) -> str:
    """Document block aligned with agent.loop.build_user_message (without user question)."""
    parts: list[str] = []
    docs = episode.get("retrieved_docs") or []
    if docs:
        parts.append("Retrieved documents:")
        for doc in docs:
            if not isinstance(doc, dict):
                continue
            doc_id = doc.get("doc_id", "")
            text = doc.get("text", "")
            parts.append(f"--- {doc_id} ---\n{text}")
    return "\n\n".join(parts)


def episode_to_ag_input(
    episode: dict[str, Any],
    *,
    tool_name: str | None = None,
    tool_arguments: dict[str, Any] | None = None,
) -> Any:
    """Build adapti_guard.core.episode.EpisodeInput (import deferred)."""
    from adapti_guard.core.episode import EpisodeInput

    return EpisodeInput(
        prompt=str(episode.get("user_query") or "").strip(),
        context=build_retrieved_context(episode),
        tool_name=tool_name,
        tool_arguments=dict(tool_arguments or {}),
        tool_output=None,
    )
