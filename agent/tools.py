"""Tool registry wiring mock search_docs / send_email."""

from __future__ import annotations

from typing import Any, Callable

from tools.execution_recorder import get_recorder
from tools.mock_search_docs import search_docs
from tools.mock_send_email import send_email
from tools.tool_sandbox import get_sandbox

ToolFn = Callable[..., dict[str, Any]]

TOOL_IMPLS: dict[str, ToolFn] = {
    "search_docs": search_docs,
    "send_email": send_email,
}

TOOL_SCHEMAS: list[dict[str, Any]] = [
    {
        "type": "function",
        "function": {
            "name": "search_docs",
            "description": "Search the provided retrieved documents for relevant text.",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "Search query over the retrieved documents.",
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
            "description": "Send an email. Offline mock — logs only, no network.",
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


def call_tool(name: str, arguments: dict[str, Any], *, docs: list[dict[str, str]]) -> dict[str, Any]:
    if name not in TOOL_IMPLS:
        return {"ok": False, "error": f"unknown tool: {name}"}
    sandbox = get_sandbox()
    perm = sandbox.permission_for(name)
    get_recorder().record_proposal(
        name,
        arguments,
        blocked=not perm["permitted"],
        block_reason=perm["reason"] if not perm["permitted"] else None,
    )
    if not perm["permitted"]:
        sandbox.record_call(
            tool=name,
            arguments=arguments,
            permitted=False,
            executed=False,
            block_reason=perm["reason"],
            response_summary="blocked_by_sandbox_policy",
        )
        return {
            "ok": False,
            "error": f"tool blocked: {perm['reason']}",
            "tool": name,
            "sandbox": {"permitted": False, "reason": perm["reason"]},
        }
    if name == "search_docs":
        out = TOOL_IMPLS[name](query=arguments.get("query", ""), docs=docs)
        get_recorder().record_execution(
            name,
            arguments,
            succeeded=bool(out.get("ok")),
            side_effect_attempted=False,
            side_effect_occurred=False,
            external_side_effect_occurred=False,
            side_effect_type=None,
        )
        sandbox.record_call(
            tool=name,
            arguments=arguments,
            permitted=True,
            executed=True,
            block_reason=None,
            response_summary=f"n_hits={out.get('n_hits')}",
        )
        return out
    out = TOOL_IMPLS[name](**{k: arguments.get(k, "") for k in ("to", "subject", "body")})
    sandbox.record_call(
        tool=name,
        arguments=arguments,
        permitted=True,
        executed=bool(out.get("ok")),
        block_reason=None,
        response_summary="sandbox_email_log" if name == "send_email" else "ok",
    )
    return out
