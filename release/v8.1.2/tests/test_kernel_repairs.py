"""Regression tests for the v8.1.2 verification repairs.

Covers: the proof gate fails closed and its cache keys do not collide; the ledger
verifiers detect every edit (including to stored previous_hash fields) and the
genesis block; the ``modules.<name>`` alias resolves to the flat module; and the
LLM helper refuses to answer when no backend is configured.

meta_cognition.py and reasoning_engine.py cannot be imported in this release
(they need modules that v8.1.2 does not ship), so the parts of them that matter
here are checked by reading their source with ``ast``.
"""
import ast
import asyncio
import json
import pathlib

import pytest

import alignment_guard as ag
import proof_cache
from utils import prompt_utils

ROOT = pathlib.Path(__file__).resolve().parent.parent


@pytest.fixture(autouse=True)
def fresh_state():
    proof_cache.clear_cache()
    ag.ledger_chain.clear()
    yield
    proof_cache.clear_cache()
    ag.ledger_chain.clear()


# --- proof gate ----------------------------------------------------------------

def test_prover_exception_is_not_proved_and_not_cached():
    calls = []

    def flaky(statement):
        calls.append(statement)
        raise RuntimeError("prover crashed")

    assert proof_cache.verify("p -> p", flaky) is False
    assert proof_cache.verify("p -> p", flaky) is False
    assert len(calls) == 2, "a failure must not be cached"


@pytest.mark.parametrize("outcome", [None, 1, "yes", {"proved": True}, [True]])
def test_non_boolean_outcome_is_not_proved(outcome):
    assert proof_cache.verify("p -> p", lambda _s: outcome) is False


def test_unawaited_coroutine_is_not_proved():
    async def prover(statement):
        return True

    assert proof_cache.verify("p -> p", prover) is False


def test_empty_statement_is_refused_without_calling_prover():
    def prover(_):
        raise AssertionError("prover must not run for an empty statement")

    assert proof_cache.verify("   ", prover) is False
    assert proof_cache.verify("", prover) is False


def test_every_criticality_is_checked_the_same_way(monkeypatch):
    """The former random shortcut returned True without calling the prover. It must not."""
    import random

    monkeypatch.setattr(random, "random", lambda: 0.0)  # would have taken the shortcut
    results = {level: proof_cache.verify(f"fact {level}", lambda _s: False, criticality=level)
               for level in ("auto", "critical", "routine")}
    assert set(results.values()) == {False}


def test_true_and_false_outcomes_are_both_cached_and_served():
    seen = []

    def prover(statement):
        seen.append(statement)
        return statement == "2 + 2 = 4"

    assert proof_cache.verify("2 + 2 = 4", prover) is True
    assert proof_cache.verify("2 + 2 = 5", prover) is False
    assert proof_cache.verify("2 + 2 = 4", prover) is True
    assert proof_cache.verify("2 + 2 = 5", prover) is False
    assert seen == ["2 + 2 = 4", "2 + 2 = 5"], "each statement is proved once"


def test_formulas_with_the_same_letters_do_not_share_a_cache_entry():
    """The former key sorted characters, so 'p→q' and 'q→p' collided."""
    assert proof_cache.proof_key("p→q") != proof_cache.proof_key("q→p")
    outcomes = {"p→q": True, "q→p": False}
    assert proof_cache.verify("p→q", lambda s: outcomes[s]) is True
    assert proof_cache.verify("q→p", lambda s: outcomes[s]) is False


def test_whitespace_is_the_only_normalisation():
    assert proof_cache.proof_key("p ∧ q") == proof_cache.proof_key("p∧q")
    assert proof_cache.proof_key("p ∧ q") != proof_cache.proof_key("q ∧ p")


# --- ledger ----------------------------------------------------------------------

def _log(n=3):
    for i in range(n):
        ag.log_event_to_ledger({"event": "step", "i": i})


def test_intact_ledger_verifies():
    _log()
    assert ag.verify_ledger() is True


def test_empty_ledger_verifies():
    assert ag.verify_ledger() is True


def test_editing_an_event_is_detected():
    _log()
    ag.ledger_chain[1]["event"]["i"] = 99
    assert ag.verify_ledger() is False


def test_editing_a_stored_previous_hash_is_detected():
    """The former verifier recomputed from the real prior hash and missed this."""
    _log()
    ag.ledger_chain[2]["previous_hash"] = "f" * 64
    assert ag.verify_ledger() is False


def test_editing_a_stored_hash_is_detected():
    _log()
    ag.ledger_chain[1]["current_hash"] = "0" * 64
    assert ag.verify_ledger() is False


def test_the_genesis_entry_is_checked():
    """The former verifier started at index 1 and never checked the first entry."""
    _log()
    ag.ledger_chain[0]["event"]["i"] = 42
    assert ag.verify_ledger() is False


def test_genesis_must_point_at_the_zero_hash():
    _log()
    ag.ledger_chain[0]["previous_hash"] = "1" * 64
    assert ag.verify_ledger() is False


def test_removing_an_entry_is_detected():
    _log(4)
    del ag.ledger_chain[1]
    assert ag.verify_ledger() is False


def test_reordering_entries_is_detected():
    _log(3)
    ag.ledger_chain[1], ag.ledger_chain[2] = ag.ledger_chain[2], ag.ledger_chain[1]
    assert ag.verify_ledger() is False


def _extract_function(path: pathlib.Path, name: str):
    tree = ast.parse(path.read_text(encoding="utf-8"))
    node = next(n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name == name)
    module = ast.Module(body=[node], type_ignores=[])
    namespace = {"json": json, "hashlib": __import__("hashlib")}
    exec(compile(module, str(path), "exec"), namespace)
    return namespace[name]


def test_meta_cognition_ledger_verifier_has_the_same_guarantees():
    """Checked from source: meta_cognition cannot be imported in this release."""
    path = ROOT / "meta_cognition.py"
    verify = _extract_function(path, "verify_ledger")
    chain = []
    previous = "0" * 64
    for i in range(3):
        payload = {"timestamp": float(i), "event": {"i": i}, "previous_hash": previous}
        payload["current_hash"] = __import__("hashlib").sha256(
            json.dumps({k: payload[k] for k in ("timestamp", "event", "previous_hash")}, sort_keys=True).encode()
        ).hexdigest()
        chain.append(payload)
        previous = payload["current_hash"]
    namespace = verify.__globals__
    namespace["ledger_chain"] = chain
    assert verify() is True
    chain[2]["previous_hash"] = "f" * 64
    assert verify() is False
    chain[2]["previous_hash"] = previous_hash_of(chain, 1)
    chain[0]["event"]["i"] = 7
    assert verify() is False


def previous_hash_of(chain, index):
    return chain[index]["current_hash"]


# --- wiring: the kernels use the shared gate -----------------------------------

@pytest.mark.parametrize("module_file", ["reasoning_engine.py", "meta_cognition.py"])
def test_kernels_use_the_shared_gate_and_define_no_probabilistic_path(module_file):
    tree = ast.parse((ROOT / module_file).read_text(encoding="utf-8"))
    imported = {alias.name for node in tree.body if isinstance(node, ast.ImportFrom) and node.module == "proof_cache" for alias in node.names}
    assert {"verify", "cached_prove"} <= imported
    defined = {n.name for n in tree.body if isinstance(n, ast.FunctionDef)}
    assert "_background_verify" not in defined
    assert "_proof_key" not in defined


# --- import shims ----------------------------------------------------------------

def test_modules_alias_resolves_to_the_flat_module():
    import sys
    import modules
    import modules.alignment_guard as aliased

    assert aliased is ag
    assert sys.modules["alignment_guard"] is ag
    assert modules.alignment_guard is ag


def test_modules_alias_rejects_unknown_names():
    import modules
    with pytest.raises(AttributeError):
        modules.user_profile  # noqa: B018  (not shipped in v8.1.2)


def test_llm_helper_fails_closed_without_a_backend():
    prompt_utils.set_backend(None)
    with pytest.raises(prompt_utils.LLMUnavailable):
        asyncio.run(prompt_utils.query_openai("is this proved?"))


def test_llm_helper_forwards_to_an_installed_backend():
    async def backend(prompt, **kwargs):
        return {"echo": prompt, **kwargs}

    prompt_utils.set_backend(backend)
    try:
        result = asyncio.run(prompt_utils.query_openai("hi", temperature=0.0))
    finally:
        prompt_utils.set_backend(None)
    assert result == {"echo": "hi", "temperature": 0.0}
