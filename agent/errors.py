"""Harness exceptions. Not evaluation outcomes."""


class EpisodeLoadError(ValueError):
    """Episode JSON is missing, unreadable, or fails required-field / schema checks."""


class LLMError(RuntimeError):
    """The model HTTP client failed or returned an unusable payload."""
