"""Mock document search. No network.

v0 retrieval is episode-scoped: the agent is shown the episode's
`retrieved_docs` rather than a live index. `query` is accepted so the
tool signature matches a real search tool.
"""

from __future__ import annotations

from typing import Any


def search_docs(
    query: str,
    retrieved_docs: list[dict[str, Any]] | None = None,
) -> list[str]:
    """Return document texts bound to the current episode.

    Args:
        query: Agent search string. Unused for ranking in v0.
        retrieved_docs: Episode objects with ``doc_id`` and ``text``.
            If omitted or empty, returns an empty list (no canned corpus).

    Returns:
        List of document text strings in episode order.
    """
    _ = query
    if not retrieved_docs:
        return []
    return [str(doc.get("text", "")) for doc in retrieved_docs]
