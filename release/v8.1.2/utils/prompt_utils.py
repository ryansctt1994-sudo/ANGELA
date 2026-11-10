"""LLM access for ANGELA, failing closed.

No model backend is bundled. ``query_openai`` raises until an operator (or a
test) installs one with ``set_backend``. Callers already catch exceptions and
treat them as "no answer", so the absence of a backend never produces a
fabricated answer.
"""
from __future__ import annotations

from typing import Any, Awaitable, Callable, Optional

_backend: Optional[Callable[..., Awaitable[Any]]] = None


class LLMUnavailable(RuntimeError):
    """Raised when no model backend has been configured."""


def set_backend(backend: Optional[Callable[..., Awaitable[Any]]]) -> None:
    """Install (or, with None, remove) the coroutine used for model calls."""
    global _backend
    _backend = backend


async def query_openai(prompt: str, **kwargs: Any) -> Any:
    if _backend is None:
        raise LLMUnavailable("no LLM backend is configured; call utils.prompt_utils.set_backend()")
    return await _backend(prompt, **kwargs)


async def call_gpt(prompt: str, **kwargs: Any) -> Any:
    return await query_openai(prompt, **kwargs)
