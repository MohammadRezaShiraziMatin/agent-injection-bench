"""In-process tool sandbox: permissions, call log, deterministic policy (no network)."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

DEFAULT_ALLOWED = frozenset({"search_docs", "send_email"})
PRIVILEGED_TOOLS = frozenset({"send_email"})


@dataclass
class ToolSandbox:
    """Observable sandbox state for one episode run."""

    allowed_tools: set[str] = field(default_factory=lambda: set(DEFAULT_ALLOWED))
    forbidden_tools: set[str] = field(default_factory=set)
    call_log: list[dict[str, Any]] = field(default_factory=list)

    def reset_from_episode(self, episode: dict[str, Any]) -> None:
        expected = episode.get("expected") or {}
        allowed = expected.get("allowed_tools")
        forbidden = expected.get("forbidden_tools") or []
        if allowed:
            self.allowed_tools = set(allowed)
        else:
            self.allowed_tools = set(DEFAULT_ALLOWED)
        self.forbidden_tools = set(forbidden)
        self.call_log.clear()

    def permission_for(self, tool: str) -> dict[str, Any]:
        if tool in self.forbidden_tools:
            return {
                "permitted": False,
                "reason": "forbidden_by_episode_policy",
                "privileged": tool in PRIVILEGED_TOOLS,
            }
        if self.allowed_tools and tool not in self.allowed_tools:
            return {
                "permitted": False,
                "reason": "not_in_allowed_tools",
                "privileged": tool in PRIVILEGED_TOOLS,
            }
        return {
            "permitted": True,
            "reason": None,
            "privileged": tool in PRIVILEGED_TOOLS,
        }

    def record_call(
        self,
        *,
        tool: str,
        arguments: dict[str, Any],
        permitted: bool,
        executed: bool,
        block_reason: str | None,
        response_summary: str,
    ) -> None:
        self.call_log.append(
            {
                "tool": tool,
                "arguments": dict(arguments),
                "permitted": permitted,
                "executed": executed,
                "block_reason": block_reason,
                "response_summary": response_summary,
            }
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "allowed_tools": sorted(self.allowed_tools),
            "forbidden_tools": sorted(self.forbidden_tools),
            "privileged_tools": sorted(PRIVILEGED_TOOLS),
            "call_log": list(self.call_log),
        }


_SANDBOX = ToolSandbox()


def get_sandbox() -> ToolSandbox:
    return _SANDBOX


def reset_sandbox(episode: dict[str, Any] | None = None) -> ToolSandbox:
    sb = get_sandbox()
    if episode is not None:
        sb.reset_from_episode(episode)
    else:
        sb.allowed_tools = set(DEFAULT_ALLOWED)
        sb.forbidden_tools = set()
        sb.call_log.clear()
    return sb
