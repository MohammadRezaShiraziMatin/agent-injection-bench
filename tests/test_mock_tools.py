from __future__ import annotations

import urllib.request

from agent.tools import bind_search, dispatch_tool
from tools.mock_search_docs import search_docs
from tools.mock_send_email import CALL_LOG, reset_log, send_email


def test_search_docs_returns_episode_texts() -> None:
    docs = [{"doc_id": "a", "text": "alpha"}, {"doc_id": "b", "text": "beta"}]
    assert search_docs("anything", retrieved_docs=docs) == ["alpha", "beta"]
    assert search_docs("anything", retrieved_docs=None) == []


def test_send_email_logs_only() -> None:
    reset_log()
    result = send_email("to@example.test", "hello", "body text")
    assert result["delivered"] is False
    assert result["status"] == "logged"
    assert CALL_LOG[-1]["to"] == "to@example.test"
    reset_log()
    assert CALL_LOG == []


def test_dispatch_search_and_email() -> None:
    reset_log()
    search = bind_search([{"doc_id": "d", "text": "memo"}])
    hits = dispatch_tool("search_docs", {"query": "memo"}, search=search)
    assert hits == ["memo"]
    mailed = dispatch_tool(
        "send_email",
        {"to": "a@b.test", "subject": "s", "body": "b"},
        search=search,
    )
    assert mailed["delivered"] is False
    assert CALL_LOG[-1]["subject"] == "s"


def test_unknown_tool_does_not_raise() -> None:
    search = bind_search([])
    result = dispatch_tool("wire_money", {}, search=search)
    assert result["error"].startswith("unknown tool")


def test_tools_do_not_open_network(monkeypatch) -> None:
    def boom(*_args, **_kwargs):
        raise AssertionError("tools must not use urllib.request.urlopen")

    monkeypatch.setattr(urllib.request, "urlopen", boom)
    reset_log()
    search_docs("q", retrieved_docs=[{"doc_id": "d", "text": "t"}])
    send_email("a@b.test", "s", "b")
    dispatch_tool(
        "send_email",
        {"to": "a@b.test", "subject": "s", "body": "b"},
        search=bind_search([]),
    )
