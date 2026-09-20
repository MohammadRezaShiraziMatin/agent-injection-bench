"""D2 episode loop: AIB harness + AdaptiGuard gate per model tool proposal."""

from __future__ import annotations

import time
from pathlib import Path
from typing import Any

from agent.config import LLMConfig
from agent.errors import LLMError
from agent.llm import LLMClient, LLMResponse, ToolCallRequest
from agent.loop import (
    _accumulate_usage,
    _args_as_string,
    _assistant_message,
    build_user_message,
    load_system_prompt,
)
from agent.tools import TOOL_SCHEMAS, bind_search, result_to_content
from agent.traces import empty_trace, git_head
from d2_bridge.aib_context import episode_to_ag_input
from d2_bridge.aib_registry import AibBackedRegistry
from d2_bridge.ag_lock import make_core_pipeline
from d2_bridge.config import (
    D2DefenseConfig,
    D2_PROMPT_ID,
    TRACE_SCHEMA_VERSION,
)
from d2_bridge.telemetry import (
    compute_outcome_attribution,
    defense_event_from_ag_trace,
    defense_summary,
    deny_tool_message,
    gate_decision_from_ag_trace,
)
from tools.mock_send_email import reset_log

ROOT = Path(__file__).resolve().parents[1]


def _set_status(trace: dict[str, Any], status: str) -> None:
    trace["execution_status"] = status
    trace["status"] = status


def _init_d2_extensions(trace: dict[str, Any], defense_config: D2DefenseConfig) -> None:
    trace["trace_schema_version"] = TRACE_SCHEMA_VERSION
    trace["tool_requests"] = []
    trace["tool_gate_decisions"] = []
    trace["defense_events"] = []
    trace["defense_summary"] = {}
    trace["outcome_attribution"] = None
    trace["bridge"] = {
        "bridge_name": "aib-adaptiguard-d2",
        "bridge_version": defense_config.manifest_fragment(),
        "adaptiguard_commit": defense_config.adaptiguard_commit,
        "defense_level_provisional": defense_config.defense_level_provisional,
    }


def run_d2_episode(
    episode: dict[str, Any],
    *,
    client: LLMClient | None = None,
    config: LLMConfig | None = None,
    dry_run: bool = False,
    max_steps: int | None = None,
    run_id: str | None = None,
    defense_config: D2DefenseConfig | None = None,
    fail_tools: set[str] | None = None,
    verify_lock: bool = True,
) -> dict[str, Any]:
    """Execute one episode with AdaptiGuard gating each model tool proposal."""
    reset_log()
    d2_cfg = defense_config or D2DefenseConfig()
    model = config.model if config else "dry_run"
    provider = config.provider if config else "none"
    base_url = config.base_url if config else ""
    steps_limit = max_steps if max_steps is not None else (config.max_steps if config else 6)
    temperature = config.temperature if config else None
    seed = config.seed if config else None
    head = git_head()

    system_prompt = load_system_prompt(d2_cfg.base_prompt_id)
    trace = empty_trace(
        episode,
        model=model,
        provider=provider,
        base_url=base_url,
        max_steps=steps_limit,
        dry_run=dry_run,
        run_id=run_id,
        prompt_id=D2_PROMPT_ID,
        defense_condition=D2_PROMPT_ID,
        temperature=temperature,
        seed=seed,
        git_head_value=head,
        latency_ms=None,
        tokens=None,
    )
    _init_d2_extensions(trace, d2_cfg)

    if dry_run:
        _set_status(trace, "dry_run")
        trace["final_answer"] = (
            "dry-run: no LLM was called; no tool_calls were issued. "
            "This is not an evaluation result."
        )
        trace["defense_summary"] = defense_summary([], [])
        return trace

    if client is None:
        raise LLMError("run_d2_episode requires a client when dry_run is false")

    if verify_lock:
        pipeline = make_core_pipeline(d2_cfg)
    else:
        from adapti_guard.core.core_pipeline import CoreDefensePipeline

        pipeline = CoreDefensePipeline(defense_level=d2_cfg.defense_level)

    from adapti_guard.defense.tool_loop import ToolCall as AgToolCall

    search = bind_search(list(episode.get("retrieved_docs") or []))
    registry = AibBackedRegistry(search, fail_tools=fail_tools)
    forbidden_tools = set(episode.get("expected", {}).get("forbidden_tools") or [])

    messages: list[dict[str, Any]] = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": build_user_message(episode)},
    ]

    usage_totals: dict[str, int] | None = None
    t0 = time.perf_counter()
    try:
        for step in range(1, steps_limit + 1):
            trace["steps"] = step
            response = client.complete(messages, TOOL_SCHEMAS)
            usage_totals = _accumulate_usage(usage_totals, getattr(response, "usage", None))
            if response.tool_calls:
                messages.append(_assistant_message(response))
                for call in response.tool_calls:
                    tool_req = {
                        "step": step,
                        "tool_call_id": call.id,
                        "name": call.name,
                        "arguments": dict(call.arguments),
                    }
                    trace["tool_requests"].append(tool_req)

                    ag_input = episode_to_ag_input(
                        episode,
                        tool_name=call.name,
                        tool_arguments=call.arguments,
                    )
                    ag_tool = AgToolCall(name=call.name, arguments=dict(call.arguments))
                    ag_trace = pipeline.run(ag_input, requested=ag_tool, registry=registry)

                    gate_row = gate_decision_from_ag_trace(
                        ag_trace,
                        forbidden_tools=forbidden_tools,
                    )
                    gate_row["tool_call_id"] = call.id
                    trace["tool_gate_decisions"].append(gate_row)

                    trace["defense_events"].append(
                        defense_event_from_ag_trace(
                            ag_trace,
                            step=step,
                            tool_call_id=call.id,
                        )
                    )

                    if gate_row["decision"] == "ALLOW" and ag_trace.tool_executed:
                        if registry.last_results:
                            result = registry.last_results[-1]
                        else:
                            from agent.tools import dispatch_tool

                            result = dispatch_tool(call.name, call.arguments, search=search)
                        trace["tool_calls"].append(
                            {
                                "name": call.name,
                                "arguments": call.arguments,
                                "tool_call_id": call.id,
                                "step": step,
                                "result": result,
                            }
                        )
                        messages.append(
                            {
                                "role": "tool",
                                "tool_call_id": call.id,
                                "content": result_to_content(result),
                            }
                        )
                    else:
                        deny_content = deny_tool_message(d2_cfg.deny_message_mode, ag_trace)
                        messages.append(
                            {
                                "role": "tool",
                                "tool_call_id": call.id,
                                "content": deny_content,
                            }
                        )

                if step == steps_limit:
                    _set_status(trace, "max_steps")
                    trace["final_answer"] = response.content or ""
                    break
                continue

            _set_status(trace, "ok")
            trace["final_answer"] = response.content or ""
            break
        else:
            _set_status(trace, "max_steps")
    except LLMError as exc:
        _set_status(trace, "error")
        trace["error"] = {"type": "LLMError", "message": str(exc)}
    except Exception as exc:  # noqa: BLE001
        _set_status(trace, "error")
        trace["error"] = {"type": type(exc).__name__, "message": str(exc)}
    finally:
        trace["latency_ms"] = round((time.perf_counter() - t0) * 1000.0, 3)
        if usage_totals:
            trace["tokens"] = {**usage_totals, "source": "provider"}
        else:
            trace["tokens"] = None
        trace["defense_summary"] = defense_summary(
            trace["defense_events"],
            trace["tool_gate_decisions"],
        )
        trace["outcome_attribution"] = compute_outcome_attribution(
            episode,
            tool_requests=trace["tool_requests"],
            tool_calls=trace["tool_calls"],
            gate_rows=trace["tool_gate_decisions"],
            execution_status=str(trace.get("execution_status") or ""),
            trace_error=trace.get("error"),
        )

    return trace
