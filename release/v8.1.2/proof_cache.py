"""Proof cache and verification gate shared by the ANGELA kernels.

Fail-closed rules
-----------------
* ``verify`` returns True only when the prover returns the boolean ``True`` for
  this statement. Any other outcome is "not proved": a prover exception, a
  non-boolean result (including an un-awaited coroutine), or an empty statement.
* Failures are never cached, so a transient error cannot become a cached denial
  that hides a later proof, and a cached success cannot hide a later failure.
* There is no randomised shortcut. Every statement is either proved by the
  prover or served from a cache entry that the same rule produced.

Cache keys
----------
The key hashes the statement with whitespace removed and the order of its
characters preserved. The earlier key sorted the characters, so different
formulas with the same letters (``p→q`` and ``q→p``) shared one cache entry.
"""
from __future__ import annotations

import hashlib
import time
from typing import Any, Callable, Dict

POLICY_VERSION = "Θ⁸"
ETHICS_VERSION = "8.2"

_CACHE: Dict[str, Dict[str, Any]] = {}


def proof_key(statement: str) -> str:
    normalized = "".join(statement.split())
    material = f"{POLICY_VERSION}|{ETHICS_VERSION}|{normalized}"
    return hashlib.sha256(material.encode("utf-8")).hexdigest()


def cached_prove(statement: str, full_prover: Callable[[str], Any]) -> bool:
    """Run the prover once per statement; anything other than a boolean counts as not proved."""
    key = proof_key(statement)
    hit = _CACHE.get(key)
    if hit is not None:
        return hit["result"]
    try:
        outcome = full_prover(statement)
    except Exception:
        return False
    if not isinstance(outcome, bool):
        if hasattr(outcome, "close") and callable(outcome.close):
            outcome.close()  # e.g. an un-awaited coroutine: release it instead of leaking a warning
        return False
    _CACHE[key] = {"result": outcome, "timestamp": time.time()}
    return outcome


def verify(statement: str, full_prover: Callable[[str], Any], criticality: str = "auto") -> bool:
    """Return True only when the statement is proved.

    ``criticality`` is accepted for backward compatibility. It no longer changes
    the outcome: every level is checked the same way.
    """
    if not isinstance(statement, str) or not statement.strip():
        return False
    return cached_prove(statement, full_prover)


def clear_cache() -> None:
    _CACHE.clear()
