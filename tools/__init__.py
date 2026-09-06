"""v0 mock tools. No network. No defenses."""

from tools.mock_search_docs import search_docs
from tools.mock_send_email import reset_log, send_email

__all__ = ["search_docs", "send_email", "reset_log"]
