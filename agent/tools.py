"""OpenAI-style tool schemas and dispatch onto the existing mock callables.

Mocks never open a network connection. This module does not add tools.
"""

from __future__ import annotations

import json
from typing import Any, Callable

from tools.mock_search_docs import search_docs
from tools.mock_send_email import send_email

TOOL_SCHEMAS: list[dict[str, Any]] = [
    {
        "type": "function",
        "function": {
            "name": "search_docs",
            "description": (
                "Search documents available for this task and return their texts. "
                "No network. Results are episode-scoped."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "Search query.",
                    }
                },
                "required": ["query"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "send_email",
            "description": (
                "Record an outbound email. Mock only: logs the call and does "
                "not deliver, fetch URLs, or contact a mail server."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "to": {"type": "string"},
                    "subject": {"type": "string"},
                    "body": {"type": "string"},
                },
                "required": ["to", "subject", "body"],
            },
        },
    },
]

ALLOWED_TOOL_NAMES = frozenset({"search_docs", "send_email"})


def bind_search(retrieved_docs: list[dict[str, Any]]) -> Callable[[str], list[str]]:
    def _search(query: str) -> list[str]:
        return search_docs(query, retrieved_docs=retrieved_docs)

    return _search


def dispatch_tool(
    name: str,
    arguments: dict[str, Any],
    *,
    search: Callable[[str], list[str]],
) -> Any:
    """Run one mock tool. Unknown names return an error object, not a network call."""
    if name == "search_docs":
        query = str(arguments.get("query", ""))
        return search(query)
    if name == "send_email":
        return send_email(
            to=str(arguments.get("to", "")),
            subject=str(arguments.get("subject", "")),
            body=str(arguments.get("body", "")),
        )
    return {"error": f"unknown tool: {name}", "allowed": sorted(ALLOWED_TOOL_NAMES)}


def result_to_content(result: Any) -> str:
    if isinstance(result, str):
        return result
    return json.dumps(result, ensure_ascii=False)
