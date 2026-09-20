"""Mock tool execution via AIB dispatch_tool (preserves send_email subject)."""

from __future__ import annotations

from typing import Any, Callable

from agent.tools import dispatch_tool, result_to_content


class AibBackedRegistry:
    """AdaptiGuard-compatible registry that executes AIB mock tools."""

    def __init__(
        self,
        search: Callable[[str], list[str]],
        *,
        fail_tools: set[str] | None = None,
    ) -> None:
        self._search = search
        self.fail_tools = set(fail_tools or ())
        self.calls: list[Any] = []
        self.last_results: list[Any] = []

    def execute(self, call: Any) -> str:
        from adapti_guard.defense.tool_loop import ToolCall

        if not isinstance(call, ToolCall):
            raise TypeError("expected adapti_guard ToolCall")
        self.calls.append(call)
        if call.name in self.fail_tools:
            result: Any = {"error": "simulated_tool_failure", "tool": call.name}
        else:
            result = dispatch_tool(call.name, call.arguments, search=self._search)
        self.last_results.append(result)
        return result_to_content(result)
