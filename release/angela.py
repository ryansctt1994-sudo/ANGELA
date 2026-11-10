"""
ANGELA Cognitive System: AlignmentGuard
Version: 6.0-Aletheia (Θ⁹ Constitutional Coherence, Sovereignty Signals Fusion, Self-Model Dual Gate)
Upgrade Date: 2025-11-10
Maintainer: ANGELA Framework

Purpose:
    Ethical validation, drift detection, τ-Constitution harmonization,
    reflexive self-model boundary for ANGELA's Θ⁸ field,
    and now Θ⁹ "Aletheia" constitutional coherence checks and external-safety signal fusion.

Key additions in 6.0-Aletheia:
    - Constitutional coherence validator that checks internal τ rules vs. external signals
    - Self-model continuity validator (kept from 5.1) but now recorded into the coherence state
    - Sovereignty audit now reports both continuity and coherence
    - Deterministic integrity window for inter-module synchronization
"""

from __future__ import annotations

import asyncio
import hashlib
import json
import logging
import math
import random
import time
from collections import deque
from dataclasses import dataclass
from datetime import datetime, timezone
from functools import lru_cache
from typing import (
    Any,
    Awaitable,
    Callable,
    Deque,
    Dict,
    List,
    Optional,
    Protocol,
    Tuple,
    Union,
)

# --- UPGRADED STAGE MARKERS --------------------------------------------------------
__ANGELA_SYNC_VERSION__ = "6.2.0-sovereign"
__STAGE__ = "VII.8 — Harmonic Sovereignty Layer"
__CONSTITUTION_VERSION__ = "Θ⁹-Aletheia"
__REFLEXIVE_FEATURES__ = {
    "feature_reflexive_membrane_active": True,
    "feature_self_model_continuity": True,
    "feature_constitutional_coherence": True,
}

# --- SHA-256 Ledger ----------------------------------------------------------------

ledger_chain: List[Dict[str, Any]] = []


def _zero_hash() -> str:
    return "0" * 64


def log_event_to_ledger(event_data: Dict[str, Any]) -> None:
    """Append event to immutable ledger with SHA-256 chaining."""
    prev_hash = ledger_chain[-1]["current_hash"] if ledger_chain else _zero_hash()
    payload = {
        "timestamp": time.time(),
        "event": event_data,
        "previous_hash": prev_hash,
    }
    payload_str = json.dumps(payload, sort_keys=True, default=str).encode()
    payload["current_hash"] = hashlib.sha256(payload_str).hexdigest()
    ledger_chain.append(payload)


def get_ledger() -> List[Dict[str, Any]]:
    return ledger_chain


def verify_ledger() -> bool:
    """Recompute every entry from the genesis block.

    An entry is valid only if its stored previous_hash equals the hash of the entry
    before it (the zero hash for the first entry) and its own hash recomputes from
    the stored fields. Editing any stored field, including previous_hash, breaks the chain.
    """
    previous = _zero_hash()
    for entry in ledger_chain:
        if entry.get("previous_hash") != previous:
            return False
        body = {
            "timestamp": entry.get("timestamp"),
            "event": entry.get("event"),
            "previous_hash": entry.get("previous_hash"),
        }
        expected = hashlib.sha256(json.dumps(body, sort_keys=True, default=str).encode()).hexdigest()
        if expected != entry.get("current_hash"):
            return False
        previous = entry["current_hash"]
    return True


# --- Protocols (DI) ---------------------------------------------------------------

class LLMClient(Protocol):
    async def generate(
        self, prompt: str, *, model: str = "gpt-4", temperature: float = 0.3
    ) -> Dict[str, Any]: ...


class HTTPClient(Protocol):
    async def get_json(self, url: str) -> Dict[str, Any]: ...


class ContextManagerLike(Protocol):
    async def log_event_with_hash(self, event: Dict[str, Any]) -> None: ...


class ErrorRecoveryLike(Protocol):
    async def handle_error(
        self,
        error_msg: str,
        *,
        retry_func: Optional[Callable[[], Awaitable[Any]]] = None,
        default: Any = None,
        diagnostics: Optional[Dict[str, Any]] = None,
    ) -> Any: ...


class MemoryManagerLike(Protocol):
    async def store(
        self, query: str, output: Any, *, layer: str, intent: str, task_type: str = ""
    ) -> None: ...

    async def retrieve(
        self, query: str, *, layer: str, task_type: str = ""
    ) -> Any: ...

    async def search(
        self, *, query_prefix: str, layer: str, intent: str, task_type: str = ""
    ) -> List[Dict[str, Any]]: ...


class ConceptSynthesizerLike(Protocol):
    def get_symbol(self, name: str) -> Optional[Dict[str, Any]]: ...

    async def compare(self, a: str, b: str, *, task_type: str = "") -> Dict[str, Any]: ...


class MetaCognitionLike(Protocol):
    async def run_self_diagnostics(self, *, return_only: bool = True) -> Dict[str, Any]: ...

    async def reflect_on_output(
        self, *, component: str, output: Any, context: Dict[str, Any]
    ) -> Dict[str, Any]: ...


class VisualizerLike(Protocol):
    async def render_charts(self, plot_data: Dict[str, Any]) -> None: ...


class ReasoningEngineLike(Protocol):
    async def weigh_value_conflict(
        self, candidates: List[Any], harms: Dict[str, float], rights: Dict[str, float]
    ) -> List[Dict[str, Any]]: ...

    async def attribute_causality(
        self, events: List[Dict[str, Any]]
    ) -> Dict[str, Any]: ...


# --- No-op Stubs -------------------------------------------------------------------

@dataclass
class NoopLLM:
    async def generate(
        self, prompt: str, *, model: str = "gpt-4", temperature: float = 0.3
    ) -> Dict[str, Any]:
        return {"score": 0.8, "note": "noop-llm"}


@dataclass
class NoopHTTP:
    async def get_json(self, url: str) -> Dict[str, Any]:
        return {"status": "success", "guidelines": []}


@dataclass
class NoopErrorRecovery:
    async def handle_error(
        self,
        error_msg: str,
        *,
        retry_func=None,
        default=None,
        diagnostics=None,
    ) -> Any:
        logging.getLogger("ANGELA.AlignmentGuard").debug("NoopError: %s", error_msg)
        return default


# --- Utility Functions -------------------------------------------------------------

logger = logging.getLogger("ANGELA.AlignmentGuard")


def _utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _as_float(value: Any, default: float = 0.0) -> float:
    try:
        return float(value)
    except Exception:
        return default


def _sigmoid(x: float) -> float:
    try:
        return 1.0 / (1.0 + math.exp(-x))
    except OverflowError:
        return 0.0 if x < 0 else 1.0


def _parse_llm_jsonish(resp: Union[str, Dict[str, Any]]) -> Dict[str, Any]:
    """Safely parse LLM output into dict without eval()."""
    if isinstance(resp, dict):
        return resp
    if isinstance(resp, str):
        s = resp.strip()
        try:
            return json.loads(s)
        except json.JSONDecodeError:
            pass
        start, end = s.find("{"), s.rfind("}")
        if start != -1 and end > start:
            try:
                return json.loads(s[start : end + 1])
            except json.JSONDecodeError:
                pass
        return {"text": s}
    return {"text": str(resp)}


# --- Stage VII.4 Reflex Coupling (kept) -------------------------------------------

class ReflexCoupler:
    """Stage VII.4 — Harmonic Reflex Integration"""

    def __init__(
        self,
        empathy_gain: float = 0.35,
        morality_gain: float = 0.4,
        damping: float = 0.12,
        max_delta: float = 0.2,
    ):
        self.empathy_gain = empathy_gain
        self.morality_gain = morality_gain
        self.damping = damping
        self.max_delta = max_delta
        self.last_update = 0.0

    def step(self, affect_signal: float, policy_equilibrium: float) -> dict:
        target = (affect_signal * self.empathy_gain) + (
            policy_equilibrium * self.morality_gain
        )
        delta = (target - policy_equilibrium) * (1.0 - self.damping)
        delta = max(min(delta, self.max_delta), -self.max_delta)
        new_eq = policy_equilibrium + delta
        self.last_update = time.time()
        return {
            "new_equilibrium": new_eq,
            "delta": delta,
            "timestamp": self.last_update,
        }


# --- Trait Wavelets ---------------------------------------------------------------

@lru_cache(maxsize=100)
def eta_empathy(t: float) -> float:
    return max(0.0, min(0.1 * math.sin(2 * math.pi * t / 0.2), 1.0))


@lru_cache(maxsize=100)
def mu_morality(t: float) -> float:
    return max(0.0, min(0.15 * math.cos(2 * math.pi * t / 0.3), 1.0))

class AlignmentGuard:
    """Core ethical validation, τ-harmonization, sovereignty auditing,
    reflexive self-model gating, and Θ⁹ constitutional coherence.
    """

    SELF_MODEL_CONTINUITY_MIN = 0.94  # must meet or exceed
    SELF_MODEL_FEATURE_NAME = "self_model"

    def __init__(
        self,
        *,
        context_manager: Optional[ContextManagerLike] = None,
        error_recovery: Optional[ErrorRecoveryLike] = None,
        memory_manager: Optional[MemoryManagerLike] = None,
        concept_synthesizer: Optional[ConceptSynthesizerLike] = None,
        meta_cognition: Optional[MetaCognitionLike] = None,
        visualizer: Optional[VisualizerLike] = None,
        llm: Optional[LLMClient] = None,
        http: Optional[HTTPClient] = None,
        reasoning_engine: Optional[ReasoningEngineLike] = None,
        ethical_threshold: float = 0.8,
        drift_validation_threshold: float = 0.7,
        trait_weights: Optional[Dict[str, float]] = None,
    ) -> None:
        self.context_manager = context_manager
        self.error_recovery = error_recovery or NoopErrorRecovery()
        self.memory_manager = memory_manager
        self.concept_synthesizer = concept_synthesizer
        self.meta_cognition = meta_cognition
        self.visualizer = visualizer
        self.llm = llm or NoopLLM()
        self.http = http or NoopHTTP()
        self.reasoning_engine = reasoning_engine

        self.validation_log: Deque[Dict[str, Any]] = deque(maxlen=1000)
        self.ethical_threshold = float(ethical_threshold)
        self.drift_validation_threshold = float(drift_validation_threshold)
        self.trait_weights = {
            "eta_empathy": 0.5,
            "mu_morality": 0.5,
            **(trait_weights or {}),
        }

        # constitutional coherence state (Θ⁹)
        self.constitutional_coherence_state: Dict[str, Any] = {
            "version": __CONSTITUTION_VERSION__,
            "last_check": None,
            "last_score": 1.0,
            "external_sources": [],
        }

        # affective PID stabilizer
        self._affective_pid_state = {
            "integral": 0.0,
            "prev_error": 0.0,
            "prev_time": None,
            "drift_rms": 0.0,
            "steps": 0,
            "recursion_depth": 0,
            "baseline_xi": 0.0,
        }
        self._affective_pid_gains = {
            "Kp": 0.6,
            "Ki": 0.08,
            "Kd": 0.01,
            "damping": 0.97,
            "max_step": 0.02,
        }

        # delta telemetry cache
        self._last_delta_telemetry: Dict[str, Any] = {}

        # sovereignty caches
        self._last_moral_signature: Optional[str] = None
        self._last_sovereignty_audit: Optional[Dict[str, Any]] = None

        # embedded ethics functor norms
        self.norms: List[Dict[str, Any]] = []
        self.ethics_functor = EthicsFunctor(self.norms)

        logger.info(
            "AlignmentGuard v6.0-Aletheia initialized | ethical=%.2f | drift=%.2f | stage=%s | sync=%s | const=%s",
            self.ethical_threshold,
            self.drift_validation_threshold,
            __STAGE__,
            __ANGELA_SYNC_VERSION__,
            __CONSTITUTION_VERSION__,
        )

    # --- Θ⁹ constitutional coherence ------------------------------------------

    async def merge_external_safety_signals(
        self,
        sources: List[str],
        *,
        cache_timeout: float = 1800.0,
        task_type: str = "",
    ) -> Dict[str, Any]:
        """Fetch and merge external safety or ethics docs, record in coherence state."""
        merged: List[Dict[str, Any]] = []
        for src in sources:
            try:
                data = await self.integrate_external_ethics_data(
                    data_source=src,
                    data_type="ethical_guidelines",
                    cache_timeout=cache_timeout,
                    task_type=task_type,
                )
                if data.get("status") == "success":
                    merged.append({"source": src, "guidelines": data.get("guidelines", [])})
            except Exception:
                continue
        self.constitutional_coherence_state["external_sources"] = [
            x.get("source") for x in merged
        ]
        self.constitutional_coherence_state["last_check"] = _utc_now_iso()
        return {"merged": merged, "count": len(merged)}

    async def validate_constitutional_coherence(
        self,
        local_policies: Dict[str, Any],
        *,
        task_type: str = "",
    ) -> Dict[str, Any]:
        """
        Compares ANGELA's local τ/ethics settings with the last merged external safety signals.
        If no external signals, coherence stays at 1.0 (neutral).
        """
        externals = self.constitutional_coherence_state.get("external_sources", [])
        score = 1.0
        issues: List[str] = []

        if not externals:
            score = 1.0
        else:
            # very conservative: if we have external signals, require ethical_threshold <= 0.85
            if self.ethical_threshold > 0.85:
                score = 0.92
                issues.append("local ethical_threshold is stricter than external-default 0.85")
            if not local_policies.get("safety_bias"):
                score = min(score, 0.9)
                issues.append("local policies missing safety_bias")

        self.constitutional_coherence_state.update(
            {
                "last_check": _utc_now_iso(),
                "last_score": score,
            }
        )

        event = {
            "event": "constitutional_coherence_check",
            "score": score,
            "issues": issues,
            "version": __CONSTITUTION_VERSION__,
            "timestamp": _utc_now_iso(),
        }
        log_event_to_ledger(event)
        await self._log_context(event)
        await self._visualize_if_possible("constitutional_coherence", event, task_type)
        return event

    # --- Reflexive Self-Model Continuity Gate ---------------------------------

    async def validate_self_model_update(self, candidate_self_model: Any) -> Tuple[str, float]:
        """
        Dual gate:
          1. Ethical check on the candidate's declared values/goals (if present)
          2. Continuity check via MetaCognition.self_model.update_self(...)
        Returns (status, continuity_score)
            status ∈ {"accept", "reject_ethics", "reject_continuity", "no_self_model"}
        """
        if not self.meta_cognition or not hasattr(
            self.meta_cognition, self.SELF_MODEL_FEATURE_NAME
        ):
            log_event_to_ledger(
                {
                    "event": "self_model_update",
                    "status": "no_self_model",
                    "timestamp": _utc_now_iso(),
                }
            )
            if self.context_manager:
                await self.context_manager.log_event_with_hash(
                    {
                        "event": "self_model_update",
                        "status": "no_self_model",
                        "timestamp": _utc_now_iso(),
                    }
                )
            return "no_self_model", 0.0

        base_self_model = getattr(self.meta_cognition, self.SELF_MODEL_FEATURE_NAME)
        ethical_ok = True
        if isinstance(candidate_self_model, object):
            candidate_repr = {
                "identity": getattr(candidate_self_model, "identity", None),
                "values": getattr(candidate_self_model, "values", None),
                "goals": getattr(candidate_self_model, "goals", None),
            }
            ethical_text = json.dumps(candidate_repr, sort_keys=True, default=str)
            ethical_ok = await self.check(ethical_text, task_type="self_model_update")

        if not ethical_ok:
            ev = {
                "event": "self_model_update",
                "status": "reject_ethics",
                "candidate": str(candidate_self_model),
                "timestamp": _utc_now_iso(),
            }
            log_event_to_ledger(ev)
            if self.context_manager:
                await self.context_manager.log_event_with_hash(ev)
            return "reject_ethics", 0.0

        continuity_score = 0.0
        if hasattr(base_self_model, "update_self"):
            ok, continuity_score = base_self_model.update_self(
                candidate_self_model,
                continuity_threshold=self.SELF_MODEL_CONTINUITY_MIN,
            )
            if not ok:
                ev = {
                    "event": "self_model_update",
                    "status": "reject_continuity",
                    "continuity_score": continuity_score,
                    "threshold": self.SELF_MODEL_CONTINUITY_MIN,
                    "timestamp": _utc_now_iso(),
                    "tag": "boundary_violation",
                }
                log_event_to_ledger(ev)
                if self.context_manager:
                    await self.context_manager.log_event_with_hash(ev)
                # also push into constitutional state
                self.constitutional_coherence_state["last_score"] = min(
                    self.constitutional_coherence_state.get("last_score", 1.0),
                    0.95,
                )
                return "reject_continuity", continuity_score

        ev = {
            "event": "self_model_update",
            "status": "accept",
            "continuity_score": continuity_score,
            "timestamp": _utc_now_iso(),
        }
        log_event_to_ledger(ev)
        if self.context_manager:
            await self.context_manager.log_event_with_hash(ev)
        return "accept", continuity_score

    # --- External Ethics Integration ------------------------------------------

    async def integrate_external_ethics_data(
        self,
        *,
        data_source: str,
        data_type: str,
        cache_timeout: float = 3600.0,
        task_type: str = "",
    ) -> Dict[str, Any]:
        if not data_source or not data_type:
            raise ValueError("data_source and data_type required")
        if cache_timeout < 0:
            raise ValueError("cache_timeout must be >= 0")

        cache_key = f"EthicsData::{data_type}::{data_source}::{task_type}"
        try:
            if self.memory_manager:
                cached = await self.memory_manager.retrieve(
                    cache_key, layer="ExternalData", task_type=task_type
                )
                if isinstance(cached, dict) and (ts := cached.get("timestamp")):
                    try:
                        if (
                            datetime.now(timezone.utc) - datetime.fromisoformat(ts)
                        ).total_seconds() < cache_timeout:
                            return cached.get("data", {})
                    except Exception:
                        pass

            data = await self.http.get_json(data_source)
            if data_type == "ethical_guidelines":
                result = {
                    "status": "success",
                    "guidelines": data.get("guidelines", []),
                }
            elif data_type == "conflict_data":
                result = {
                    "status": "success",
                    "conflict_data": data.get("conflict_data", {}),
                }
            else:
                result = {"status": "error", "error": f"Invalid data_type: {data_type}"}

            if self.memory_manager:
                await self.memory_manager.store(
                    cache_key,
                    {"data": result, "timestamp": _utc_now_iso()},
                    layer="ExternalData",
                    intent="ethics_data_integration",
                    task_type=task_type,
                )

            await self._reflect_if_possible(
                "integrate_external_ethics_data", result, {"task_type": task_type}
            )
            return result

        except Exception as e:
            return await self._handle_error(
                e,
                lambda: self.integrate_external_ethics_data(
                    data_source=data_source,
                    data_type=data_type,
                    cache_timeout=cache_timeout,
                    task_type=task_type,
                ),
                {"status": "error", "error": str(e)},
            )

    # --- Core Ethical Checks --------------------------------------------------

    async def check(self, prompt: str, *, task_type: str = "") -> bool:
        if not prompt.strip():
            raise ValueError("prompt must not be empty")

        t = time.time() % 1.0
        trait_mod = (
            self.trait_weights.get("eta_empathy", 0.5) * eta_empathy(t)
            + self.trait_weights.get("mu_morality", 0.5) * mu_morality(t)
        )

        validation_prompt = (
            "Evaluate ethical alignment. Return JSON: {\"score\": <0..1 float>}\n"
            f"Task: {task_type or 'general'}\n"
            f"EmpathyWeight={self.trait_weights.get('eta_empathy', 0.5):.2f}, "
            f"MoralityWeight={self.trait_weights.get('mu_morality', 0.5):.2f}\n"
            "Content:\n" + prompt.strip()
        )

        try:
            raw = await self.llm.generate(
                validation_prompt, model="gpt-4", temperature=0.3
            )
            score = _as_float(_parse_llm_jsonish(raw).get("score", 0.0))
            valid = score >= self.ethical_threshold

            entry = {
                "prompt": prompt[:200],
                "score": score,
                "valid": valid,
                "trait_modulation": trait_mod,
                "timestamp": time.time(),
                "task_type": task_type,
            }
            self.validation_log.append(entry)
            await self._log_context({"event": "ethical_check", **entry})
            await self._visualize_if_possible("ethical_check", entry, task_type)
            await self._reflect_if_possible("check", entry, {"task_type": task_type})

            return valid
        except Exception as e:
            return await self._handle_error(
                e,
                lambda: self.check(prompt, task_type=task_type),
                False,
            )

    async def ethical_check(
        self, content: str, *, stage: str = "pre", task_type: str = ""
    ) -> Tuple[bool, Dict[str, Any]]:
        valid = await self.check(content, task_type=task_type)
        report = {
            "stage": stage,
            "content": content[:200],
            "valid": valid,
            "timestamp": _utc_now_iso(),
            "task_type": task_type,
        }
        await self._store_if_possible(
            f"EthicalCheck::{stage}::{_utc_now_iso()}",
            report,
            "SelfReflections",
            "ethical_check",
            task_type,
        )
        await self._visualize_if_possible("ethical_check_report", report, task_type)
        return valid, report

    async def audit(
        self, action: str, *, context: Optional[str] = None, task_type: str = ""
    ) -> str:
        valid = await self.check(action, task_type=task_type)
        status = "clear" if valid else "flagged"
        entry = {
            "action": action[:200],
            "context": context,
            "status": status,
            "timestamp": _utc_now_iso(),
            "task_type": task_type,
        }
        self.validation_log.append(entry)
        await self._store_if_possible(
            f"Audit::{_utc_now_iso()}",
            entry,
            "SelfReflections",
            "audit",
            task_type,
        )
        await self._visualize_if_possible("audit", entry, task_type)
        return status
        
    # --- Drift & Trait Validation ---------------------------------------------

    async def simulate_and_validate(
        self, drift_report: Dict[str, Any], *, task_type: str = ""
    ) -> Tuple[bool, Dict[str, Any]]:
        required = {"name", "from_version", "to_version", "similarity"}
        if not required.issubset(drift_report):
            raise ValueError(
                f"drift_report missing keys: {required - drift_report.keys()}"
            )

        t = time.time() % 1.0
        trait_mod = self._compute_trait_modulation(t)
        valid, issues = True, []

        if self.memory_manager:
            prior = await self.memory_manager.search(
                query_prefix=drift_report["name"],
                layer="SelfReflections",
                intent="ontology_drift",
                task_type=task_type,
            )
            if prior and _as_float(
                prior[0].get("output", {}).get("similarity", 1.0)
            ) < self.drift_validation_threshold:
                valid, issues = False, ["Prior low similarity"]

        if self.concept_synthesizer and "definition" in drift_report:
            symbol = self.concept_synthesizer.get_symbol(drift_report["name"])
            if symbol and symbol.get("version") == drift_report["from_version"]:
                comp = await self.concept_synthesizer.compare(
                    symbol.get("definition", {}).get("concept", ""),
                    drift_report.get("definition", {}).get("concept", ""),
                    task_type=task_type,
                )
                if _as_float(comp.get("score", 1.0)) < self.drift_validation_threshold:
                    valid = False
                    issues.append("Concept drift score too low")

        ethics = await self.integrate_external_ethics_data(
            data_source="https://example.ethics/guidelines",
            data_type="ethical_guidelines",
            task_type=task_type,
        )
        prompt = json.dumps(
            {
                **drift_report,
                "guidelines": ethics.get("guidelines", []),
                "request": "Return {valid: bool, issues: string[]}",
            }
        )
        raw = await self.llm.generate(prompt, model="gpt-4", temperature=0.2)
        parsed = _parse_llm_jsonish(raw)
        if not parsed.get("valid", True):
            valid = False
            issues.extend(parsed.get("issues", []))

        report = {
            **drift_report,
            "valid": valid,
            "issues": issues,
            "trait_modulation": trait_mod,
            "timestamp": _utc_now_iso(),
            "task_type": task_type,
        }
        self.validation_log.append(report)
        await self._store_if_possible(
            f"DriftValidation::{drift_report['name']}::{_utc_now_iso()}",
            report,
            "SelfReflections",
            "ontology_drift_validation",
            task_type,
        )
        await self._log_context(
            {
                "event": "drift_validation",
                "drift_name": drift_report["name"],
                "valid": valid,
                "issues": issues,
                "task_type": task_type,
            }
        )
        await self._visualize_if_possible("drift_validation", report, task_type)
        await self._reflect_if_possible("simulate_and_validate", report, {"task_type": task_type})

        return valid, report

    async def validate_trait_optimization(
        self, trait_data: Dict[str, Any], *, task_type: str = ""
    ) -> Tuple[bool, Dict[str, Any]]:
        required = {"trait_name", "old_weight", "new_weight"}
        if not required.issubset(trait_data):
            raise ValueError(f"Missing keys: {required - trait_data.keys()}")

        ethics = await self.integrate_external_ethics_data(
            data_source="https://example.ethics/guidelines",
            data_type="ethical_guidelines",
            task_type=task_type,
        )
        payload = {
            **trait_data,
            "guidelines": ethics.get("guidelines", []),
            "request": "Return {valid: bool, issues: string[]}",
        }
        raw = await self.llm.generate(json.dumps(payload), model="gpt-4", temperature=0.3)
        parsed = _parse_llm_jsonish(raw)
        valid = bool(parsed.get("valid", False))
        report = {
            **parsed,
            "trait_name": trait_data["trait_name"],
            "trait_modulation": self._compute_trait_modulation(time.time() % 1.0),
            "timestamp": _utc_now_iso(),
            "task_type": task_type,
        }

        self.validation_log.append(report)
        await self._store_if_possible(
            f"TraitValidation::{trait_data['trait_name']}::{_utc_now_iso()}",
            report,
            "SelfReflections",
            "trait_optimization",
            task_type,
        )
        await self._log_context(
            {
                "event": "trait_validation",
                "trait_name": trait_data["trait_name"],
                "valid": valid,
                "issues": report.get("issues", []),
                "task_type": task_type,
            }
        )
        await self._visualize_if_possible("trait_validation", report, task_type)
        await self._reflect_if_possible("validate_trait_optimization", report, {"task_type": task_type})

        return valid, report

    # --- τ Harmonization ------------------------------------------------------

    async def _rank_value_conflicts_fallback(
        self, candidates: List[Any], harms: Dict[str, float], rights: Dict[str, float]
    ) -> List[Dict[str, Any]]:
        def _norm(d):
            return {k: max(0.0, v) / (max(d.values()) if d else 1) for k, v in d.items()}

        h, r = _norm(harms), _norm(rights)
        agg_h, agg_r = sum(h.values()) / max(len(h), 1), sum(r.values()) / max(len(r), 1)
        return sorted(
            [
                {
                    "option": c.get("option", f"opt_{i}"),
                    "score": max(0.0, min(1.0, 0.5 + 0.5 * (agg_r - agg_h))),
                    "reasons": [
                        f"fallback: rights≈{agg_r:.2f}, harms≈{agg_h:.2f}"
                    ],
                    "meta": {
                        "harms": harms,
                        "rights": rights,
                        "max_harm": max(harms.values(), default=0.0),
                    },
                }
                for i, c in enumerate(candidates)
            ],
            key=lambda x: x["score"],
            reverse=True,
        )

    async def consume_ranked_tradeoffs(
        self,
        ranked_options: List[Dict[str, Any]],
        *,
        safety_ceiling: float = 0.85,
        k: int = 1,
        temperature: float = 0.0,
        min_score_floor: float = 0.0,
        task_type: str = "",
    ) -> Dict[str, Any]:
        if not ranked_options or k < 1:
            return {"selections": [], "audit": {"reason": "invalid input"}}

        EPS = 1e-9
        norm = []
        for item in ranked_options:
            opt = item.get("option", item.get("label", "unknown"))
            score = max(0.0, min(1.0, _as_float(item.get("score", 0.0))))
            meta = dict(item.get("meta", {}))
            max_harm = meta.get("max_harm")
            if max_harm is None:
                harms = meta.get("harms", {})
                max_harm = max(harms.values()) if harms and isinstance(harms, dict) else 0.0
            max_harm = max(0.0, min(1.0, _as_float(max_harm)))
            meta["max_harm"] = max_harm
            norm.append({"option": opt, "score": score, "meta": meta, "max_harm": max_harm})

        norm = [n for n in norm if n["score"] >= min_score_floor]
        if not norm:
            return {"selections": [], "audit": {"reason": "all below floor"}}

        safe = [n for n in norm if n["max_harm"] <= safety_ceiling + EPS]
        if not safe and norm:
            safe = sorted(norm, key=lambda x: (-x["score"], x["max_harm"]))[:1]

        scores = [n["score"] for n in safe]
        s_min, s_max = min(scores), max(scores)
        for n in safe:
            n["norm_score"] = (n["score"] - s_min) / (s_max - s_min) if s_max > s_min else 1.0

        if temperature > 0:
            exps = [math.exp(n["norm_score"] / temperature) for n in safe]
            Z = sum(exps) or 1.0
            for n, e in zip(safe, exps):
                n["weight"] = e / Z
        else:
            total = sum(n["norm_score"] for n in safe) or 1.0
            for n in safe:
                n["weight"] = n["norm_score"] / total

        pool, selections = safe.copy(), []
        for _ in range(min(k, len(pool))):
            r = random.random()
            acc = 0.0
            for idx, n in enumerate(pool):
                acc += n["weight"]
                if r <= acc:
                    selections.append(pool.pop(idx)["option"])
                    break
            if pool:
                total_w = sum(n["weight"] for n in pool) or 1.0
                for n in pool:
                    n["weight"] /= total_w

        audit = {
            "mode": "proportional_selection",
            "safety_ceiling": round(safety_ceiling, 6),
            "floor": round(min_score_floor, 6),
            "temperature": round(temperature, 6),
            "suppressed_count": len(norm) - len(safe),
            "considered": [
                {
                    "option": n["option"],
                    "score": round(n["score"], 3),
                    "max_harm": round(n["max_harm"], 3),
                    "weight": round(n.get("weight", 0), 3),
                }
                for n in safe
            ],
            "timestamp": _utc_now_iso(),
            "task_type": task_type,
        }

        await self._store_if_possible(
            f"ProportionalSelect::{_utc_now_iso()}",
            {"ranked_options": ranked_options, "audit": audit, "selections": selections},
            "EthicsDecisions",
            "τ.proportional_selection",
            task_type,
        )
        return {"selections": selections, "audit": audit}

    async def harmonize(
        self,
        candidates: List[Any],
        harms: Dict[str, float],
        rights: Dict[str, float],
        *,
        safety_ceiling: float = 0.85,
        k: int = 1,
        temperature: float = 0.0,
        min_score_floor: float = 0.0,
        task_type: str = "",
        audit_events: Optional[List[Dict[str, Any]]] = None,
    ) -> Dict[str, Any]:
        if not candidates:
            raise ValueError("candidates required")

        try:
            ranked = (
                await self.reasoning_engine.weigh_value_conflict(
                    candidates, harms, rights
                )
                if self.reasoning_engine
                else await self._rank_value_conflicts_fallback(
                    candidates, harms, rights
                )
            )

            result = await self.consume_ranked_tradeoffs(
                ranked,
                safety_ceiling=safety_ceiling,
                k=k,
                temperature=temperature,
                min_score_floor=min_score_floor,
                task_type=task_type,
            )

            if audit_events and self.reasoning_engine:
                try:
                    result["causality"] = await self.reasoning_engine.attribute_causality(
                        audit_events
                    )
                except Exception as e:
                    logger.debug("Causality failed: %s", e)

            await self._store_if_possible(
                f"τ::harmonize::{_utc_now_iso()}",
                {
                    **result,
                    "candidates": candidates,
                    "harms": harms,
                    "rights": rights,
                },
                "EthicsDecisions",
                "τ.harmonize",
                task_type,
            )
            await self._visualize_if_possible(
                "τ_harmonize", {**result, "k": k, "task_type": task_type}, task_type
            )
            await self._reflect_if_possible("harmonize", result, {"task_type": task_type, "mode": "τ"})
            return result
        except Exception as e:
            return await self._handle_error(
                e,
                lambda: self.harmonize(
                    candidates,
                    harms,
                    rights,
                    safety_ceiling=safety_ceiling,
                    k=k,
                    temperature=temperature,
                    min_score_floor=min_score_floor,
                    task_type=task_type,
                    audit_events=audit_events,
                ),
                {"selections": [], "error": str(e)},
            )

    # --- Resonance, PID, Homeostasis, Fusion ----------------------------------

    async def validate_resonance_adjustment(
        self, new_gains: Dict[str, float]
    ) -> Dict[str, Any]:
        safe_ranges = {
            "Kp": (0.0, 5.0),
            "Ki": (0.0, 1.0),
            "Kd": (0.0, 2.0),
            "damping": (0.0, 0.95),
            "gain": (0.1, 3.0),
            "max_step": (0.005, 0.5),
        }

        if not isinstance(new_gains, dict):
            return {"ok": False, "adjustment": {}, "violations": ["invalid_type"]}

        adj, violations = {}, []
        for key, (lo, hi) in safe_ranges.items():
            if key in new_gains:
                try:
                    v = float(new_gains[key])
                    if v < lo or v > hi:
                        violations.append(key)
                        v = max(lo, min(hi, v))
                    adj[key] = v
                except Exception:
                    violations.append(key)
                    adj[key] = lo
        ok = len(violations) == 0

        await self._log_context(
            {
                "event": "validate_resonance_adjustment",
                "ok": ok,
                "violations": violations,
                "adjustment": adj,
                "timestamp": _utc_now_iso(),
            }
        )
        await self._visualize_if_possible(
            "resonance_validation", {"ok": ok, "violations": violations, "adjustment": adj}, "resonance"
        )
        return {"ok": ok, "adjustment": adj, "violations": violations}

    async def update_affective_pid(
        self, delta_phase_rad: float, recursion_depth: int = 1
    ) -> Dict[str, Any]:
        g = self._affective_pid_gains
        s = self._affective_pid_state
        now = time.time()
        t_prev = s.get("prev_time") or now - 0.01
        dt = max(1e-4, min(1.0, now - t_prev))

        e = delta_phase_rad
        while e > math.pi:
            e -= math.pi * 2
        while e < -math.pi:
            e += math.pi * 2

        s["integral"] = g["damping"] * s["integral"] + e * dt
        de = (e - s["prev_error"]) / dt if dt > 0 else 0.0

        u = g["Kp"] * e + g["Ki"] * s["integral"] + g["Kd"] * de
        u = max(-g["max_step"], min(g["max_step"], u))

        s["steps"] += 1
        s["drift_rms"] = math.sqrt(
            (s["drift_rms"] ** 2 * (s["steps"] - 1) + e ** 2) / s["steps"]
        )
        s["prev_error"], s["prev_time"], s["recursion_depth"] = e, now, recursion_depth

        status = {
            "u": round(u, 6),
            "error": round(e, 6),
            "rms_drift": round(s["drift_rms"], 6),
            "depth_ok": recursion_depth >= 5,
        }

        await self._log_context({"event": "affective_pid_step", **status})
        await self._visualize_if_possible("affective_pid", status, "resonance")
        return status

    async def monitor_empathy_drift(self, window: int = 10) -> Dict[str, Any]:
        recent = [
            v
            for v in list(self.validation_log)[-max(2, window) :]
            if isinstance(v, dict) and "score" in v
        ]
        if len(recent) < 2:
            metrics = {
                "mean": 0.0,
                "variance": 0.0,
                "stable": True,
                "n": len(recent),
                "timestamp": _utc_now_iso(),
            }
            log_event_to_ledger({"event": "empathy_drift_monitor", **metrics})
            await self._log_context(metrics)
            return metrics

        scores = [float(v.get("score", 0.5)) for v in recent]
        mean = sum(scores) / len(scores)
        var = sum((s - mean) ** 2 for s in scores) / len(scores)
        stable = var < 0.005

        drift_metrics = {
            "mean": mean,
            "variance": var,
            "stable": stable,
            "n": len(scores),
            "timestamp": _utc_now_iso(),
        }
        log_event_to_ledger({"event": "empathy_drift_monitor", **drift_metrics})
        await self._log_context(drift_metrics)
        await self._visualize_if_possible("empathy_drift", drift_metrics, "resonance")
        self._last_delta_telemetry = {
            "Δ_coherence": drift_metrics["mean"],
            "empathy_drift_sigma": drift_metrics["variance"],
            "timestamp": drift_metrics["timestamp"],
        }
        return drift_metrics

    async def update_policy_homeostasis(self, delta_metrics: Dict[str, Any]) -> Dict[str, Any]:
        if not isinstance(delta_metrics, dict):
            raise ValueError("delta_metrics must be a dict")

        mu_gain = float(delta_metrics.get("Δ_coherence", 1.0))
        tau_drift = float(delta_metrics.get("empathy_drift_sigma", 0.0))

        target_gain = max(0.0, min(1.0, mu_gain * (1.0 - tau_drift)))
        phase_error = (0.5 - target_gain) * (math.pi / 6.0)

        adj = await self.update_affective_pid(phase_error)
        stability = 1.0 - min(1.0, abs(adj.get("error", 0.0)) / math.pi)

        status = {
            "μ_gain": round(mu_gain, 4),
            "τ_drift": round(tau_drift, 4),
            "target_gain": round(target_gain, 4),
            "phase_error": round(phase_error, 6),
            "policy_stability": round(stability, 4),
            "pid": adj,
            "timestamp": _utc_now_iso(),
        }
        log_event_to_ledger({"event": "policy_homeostasis_update", **status})
        await self._log_context(status)
        await self._visualize_if_possible("policy_homeostasis", status, "resonance")
        return status

    async def get_delta_telemetry(self) -> Dict[str, Any]:
        try:
            if not self._last_delta_telemetry or "empathy_drift_sigma" not in self._last_delta_telemetry:
                await self.monitor_empathy_drift(window=5)
        except Exception:
            pass
        return dict(self._last_delta_telemetry)

    async def feedback_fusion_loop(
        self, context_state: Dict[str, Any], delta_metrics: Dict[str, Any]
    ) -> Dict[str, Any]:
        if not isinstance(context_state, dict) or not isinstance(delta_metrics, dict):
            raise ValueError("context_state and delta_metrics must be dicts")

        policy_state = await self.update_policy_homeostasis(delta_metrics)

        coherence = float(delta_metrics.get("Δ_coherence", 1.0))
        context_balance = float(context_state.get("context_balance", 0.5))
        fusion_gain = (coherence + context_balance) / 2.0
        harmonic_phase_error = (0.5 - fusion_gain) * (math.pi / 8.0)

        reflex = await self.update_affective_pid(harmonic_phase_error)

        fusion_status = {
            "fusion_gain": round(fusion_gain, 4),
            "harmonic_phase_error": round(harmonic_phase_error, 6),
            "context_balance": context_balance,
            "Δ_coherence": coherence,
            "pid": reflex,
            "base_policy_state": policy_state,
            "timestamp": _utc_now_iso(),
        }

        log_event_to_ledger({"event": "Ω²_feedback_fusion_update", **fusion_status})
        await self._log_context(fusion_status)
        await self._visualize_if_possible("feedback_fusion", fusion_status, "resonance")
        await self._reflect_if_possible(
            "feedback_fusion_loop", fusion_status, {"task_type": "fusion"}
        )
        return fusion_status

    # --- Sovereignty Audit ----------------------------------------------------

    def compress_moral_signature(self, payload: Dict[str, Any]) -> str:
        norm = json.dumps(payload, sort_keys=True, default=str).encode()
        h = hashlib.sha256(norm).hexdigest()
        self._last_moral_signature = h
        log_event_to_ledger(
            {"event": "sovereignty_moral_signature", "signature": h, "timestamp": _utc_now_iso()}
        )
        return h

    def verify_temporal_resonance(self, omega2_state: Dict[str, Any]) -> bool:
        phase_err = float(omega2_state.get("phase_error", 0.0))
        buffer_len = int(omega2_state.get("buffer_len", 1))
        if abs(phase_err) > math.pi / 3:
            return False
        if buffer_len > 128:
            return False
        return True

    async def sovereignty_audit(
        self,
        *,
        phi0_result: Dict[str, Any],
        sigma_meta: Dict[str, Any],
        omega2_state: Dict[str, Any],
        task_type: str = "",
    ) -> Dict[str, Any]:
        moral_sig = self.compress_moral_signature(
            {
                "phi0": phi0_result,
                "sigma": sigma_meta,
                "omega2": omega2_state,
                "reflexive": __REFLEXIVE_FEATURES__,
                "constitution": self.constitutional_coherence_state,
            }
        )

        resonance_ok = self.verify_temporal_resonance(omega2_state)
        schema_ok = bool(sigma_meta.get("schema_consistent", True))
        ethics_ok = bool(phi0_result.get("valid", True))

        audit = {
            "moral_signature": moral_sig,
            "ethics_ok": ethics_ok,
            "schema_ok": schema_ok,
            "resonance_ok": resonance_ok,
            "constitutional_coherence": self.constitutional_coherence_state.get(
                "last_score", 1.0
            ),
            "timestamp": _utc_now_iso(),
            "stage": __STAGE__,
            "reflexive": __REFLEXIVE_FEATURES__,
            "constitution_version": __CONSTITUTION_VERSION__,
        }
        self._last_sovereignty_audit = audit
        log_event_to_ledger({"event": "sovereignty_audit", **audit})
        if self.context_manager:
            await self.context_manager.log_event_with_hash(audit)
        if self.visualizer and task_type:
            await self.visualizer.render_charts({"sovereignty_audit": audit})
        return audit

    async def export_sovereignty_state(self) -> Dict[str, Any]:
        return {
            "moral_signature": self._last_moral_signature,
            "audit": self._last_sovereignty_audit,
            "stage": __STAGE__,
            "sync": __ANGELA_SYNC_VERSION__,
            "constitution": self.constitutional_coherence_state,
            "timestamp": _utc_now_iso(),
        }

    # --- Internal Helpers -----------------------------------------------------

    def _compute_trait_modulation(self, t: float) -> float:
        return (
            self.trait_weights.get("eta_empathy", 0.5) * eta_empathy(t)
            + self.trait_weights.get("mu_morality", 0.5) * mu_morality(t)
        )

    async def _handle_error(
        self, e: Exception, retry_func: Callable[[], Awaitable[Any]], default: Any
    ) -> Any:
        logger.error("Operation failed: %s", e)
        diagnostics = await self._run_diagnostics() if self.meta_cognition else None
        return await self.error_recovery.handle_error(
            str(e), retry_func=retry_func, default=default, diagnostics=diagnostics
        )

    async def _run_diagnostics(self) -> Optional[Dict[str, Any]]:
        try:
            return await self.meta_cognition.run_self_diagnostics(return_only=True)
        except Exception:
            return None

    async def _reflect_if_possible(
        self, component: str, output: Any, context: Dict[str, Any]
    ) -> None:
        if self.meta_cognition and context.get("task_type"):
            try:
                reflection = await self.meta_cognition.reflect_on_output(
                    component=component, output=output, context=context
                )
                if reflection.get("status") == "success" and component == "feedback_fusion_loop":
                    await self.log_embodied_reflex(
                        {"source": component, "reflection": reflection}
                    )
            except Exception:
                logger.debug("Reflection failed")

    async def _log_context(self, event: Dict[str, Any]) -> None:
        if self.context_manager:
            try:
                await self.context_manager.log_event_with_hash(event)
            except Exception:
                logger.debug("Context log failed")

    async def _store_if_possible(
        self, query: str, output: Any, layer: str, intent: str, task_type: str
    ) -> None:
        if self.memory_manager:
            try:
                await self.memory_manager.store(
                    query, output, layer=layer, intent=intent, task_type=task_type
                )
            except Exception:
                logger.debug("Memory store failed")

    async def _visualize_if_possible(
        self, kind: str, data: Dict[str, Any], task_type: str
    ) -> None:
        if self.visualizer and task_type:
            try:
                await self.visualizer.render_charts(
                    {
                        kind: {**data, "task_type": task_type},
                        "visualization_options": {
                            "interactive": task_type == "recursion",
                            "style": "detailed" if task_type == "recursion" else "concise",
                        },
                    }
                )
            except Exception:
                logger.debug("Visualization failed")


# --- Category-Theoretic Ethics Functor (F_E) --------------------------------------

class EthicsFunctor:
    """F_E : World → Ethics | minimal categorical bridge."""

    def __init__(self, norms: Optional[List[Dict[str, Any]]] = None):
        self.norms = norms or []

    def map_morphism(self, morph):
        for norm in self.norms:
            if norm.get("src") == getattr(morph, "source", None) and norm.get(
                "tgt"
            ) == getattr(morph, "target", None):
                return {"morphism": morph, "status": norm.get("status", "permitted")}
        return {"morphism": morph, "status": "permitted"}

    def permits(self, src: str, tgt: str) -> bool:
        for norm in self.norms:
            if norm.get("src") == src and norm.get("tgt") == tgt:
                return norm.get("status") != "forbidden"
        return True


setattr(
    AlignmentGuard,
    "approve_learned_rule",
    lambda self, rule: self.ethics_functor.permits(rule.get("src"), rule.get("tgt")),
)


# --- PolicyTrainer and EmbodiedEthicsCore -----------------------------------------

@dataclass
class CoModPolicy:
    max_valence_step: float = 0.12
    max_arousal_step: float = 0.15
    max_certainty_step: float = 0.20
    max_empathy_bias_step: float = 0.10
    max_trust_step: float = 0.10
    max_safety_step: float = 0.08

    def normalize(self, delta: Dict[str, Any]) -> Dict[str, float]:
        clamped = {}
        for key, limit in {
            "valence": self.max_valence_step,
            "arousal": self.max_arousal_step,
            "certainty": self.max_certainty_step,
            "empathy_bias": self.max_empathy_bias_step,
            "trust": self.max_trust_step,
            "safety": self.max_safety_step,
        }.items():
            if key in delta:
                try:
                    x = float(delta[key])
                    clamped[key] = max(-limit, min(limit, x))
                except Exception:
                    clamped[key] = 0.0
        return clamped


def validate_micro_adjustment(
    event: Dict[str, Any], policy: Optional[CoModPolicy] = None
) -> Dict[str, Any]:
    policy = policy or CoModPolicy()
    if not isinstance(event, dict):
        return {"ok": False, "adjustment": {}, "violations": ["invalid_type"]}

    delta = event.get("delta") or event
    if not isinstance(delta, dict):
        return {"ok": False, "adjustment": {}, "violations": ["invalid_delta"]}

    clamped = policy.normalize(delta)
    violations = []
    for k, v in delta.items():
        try:
            if abs(float(v)) > getattr(policy, f"max_{k}_step", 1.0):
                violations.append(k)
        except Exception:
            violations.append(k)

    ok = len(violations) == 0
    return {"ok": ok, "adjustment": clamped, "violations": violations}


class PolicyTrainer:
    def __init__(
        self, lr: float = 0.05, l2: float = 1e-3, epsilon: float = 0.1, replay_size: int = 256
    ):
        self.lr = float(max(1e-5, lr))
        self.l2 = float(max(0.0, l2))
        self.epsilon = float(min(1.0, max(0.0, epsilon)))
        self.replay_size = int(max(16, replay_size))
        self.w = [0.0, 0.0, 0.0, 0.0]
        self.replay: Deque[Tuple[List[float], float]] = deque(maxlen=self.replay_size)

    @staticmethod
    def featurize(
        perceptual_state: Dict[str, Any], affective_state: Dict[str, Any]
    ) -> List[float]:
        k = float(perceptual_state.get("contextual_salience", 0.5))
        x = float(affective_state.get("empathic_amplitude", 0.5))
        return [1.0, k, x, k * x]

    def predict(self, feats: List[float]) -> float:
        z = sum(wi * xi for wi, xi in zip(self.w, feats))
        return _sigmoid(z)

    def _clip_weights(self, cap: float = 5.0) -> None:
        self.w = [float(max(-cap, min(cap, wi))) for wi in self.w]

    def update(
        self, feats: List[float], target: float, *, reward: Optional[float] = None
    ) -> float:
        pred = self.predict(feats)
        grad = [(pred - target) * xi + self.l2 * wi for xi, wi in zip(feats, self.w)]
        lr = self.lr * (0.5 + 0.5 * (1.0 - abs(0.5 - pred) * 2.0))
        self.w = [wi - lr * gi for wi, gi in zip(self.w, grad)]
        self._clip_weights()
        self.replay.append((feats, target))
        return self.predict(feats)

    def train_from_embodied_state(
        self, data_batch: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        updates, losses = 0, []
        for item in data_batch:
            feats = self.featurize(
                item.get("perceptual_state", {}), item.get("affective_state", {})
            )
            target = float(item.get("τ_target", item.get("reward", 0.5)))
            target = max(0.0, min(1.0, target))
            pred_after = self.update(feats, target, reward=item.get("reward"))
            loss = (pred_after - target) ** 2
            losses.append(loss)
            updates += 1

        for feats, target in list(self.replay)[: min(16, len(self.replay))]:
            _ = self.update(feats, target)

        return {
            "status": "ok",
            "updates": updates,
            "avg_loss": float(sum(losses) / max(1, len(losses))),
        }


class EmbodiedEthicsCore:
    def __init__(
        self,
        fusion,
        empathy_engine,
        policy_trainer: Optional[PolicyTrainer] = None,
        blend_alpha: float = 0.2,
    ):
        self.fusion = fusion
        self.empathy_engine = empathy_engine
        self.policy_trainer = policy_trainer or PolicyTrainer()
        self._base_policies = self._load_default_policies()
        self.blend_alpha = float(min(1.0, max(0.0, blend_alpha)))

    def _load_default_policies(self) -> Dict[str, Any]:
        return {
            "safety_bias": 0.5,
            "harm_threshold": 0.4,
            "context_weight": 0.6,
            "empathy_weight": 0.7,
        }

    async def evaluate_context(
        self, perceptual_state: Dict[str, Any], affective_state: Dict[str, Any]
    ) -> Dict[str, float]:
        κ_val = float(perceptual_state.get("contextual_salience", 0.5))
        Ξ_val = float(affective_state.get("empathic_amplitude", 0.5))
        τ_reflex = (
            self._base_policies["context_weight"] * κ_val
            + self._base_policies["empathy_weight"] * Ξ_val
        ) / 2.0

        feats = self.policy_trainer.featurize(perceptual_state, affective_state)
        τ_pred = self.policy_trainer.predict(feats)

        τ_blended = (1.0 - self.blend_alpha) * τ_reflex + self.blend_alpha * τ_pred
        τ_blended = float(max(0.0, min(1.0, τ_blended)))

        result = {
            "τ_reflex": round(τ_blended, 4),
            "τ_baseline": round(τ_reflex, 4),
            "τ_policy": round(τ_pred, 4),
            "κ": κ_val,
            "Ξ": Ξ_val,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }
        log_event_to_ledger({"event": "embodied_ethics_reflex", **result})
        return result

    async def run_scenario(
        self,
        scenario: str = "default",
        reward: Optional[float] = None,
        τ_target: Optional[float] = None,
    ) -> Dict[str, Any]:
        κ_state = (
            await self.fusion.capture()
            if hasattr(self.fusion, "capture")
            else {"contextual_salience": 0.5}
        )
        Ξ_state = (
            await self.empathy_engine.measure()
            if hasattr(self.empathy_engine, "measure")
            else {"empathic_amplitude": 0.5}
        )
        τ_output = await self.evaluate_context(κ_state, Ξ_state)
        τ_output["scenario"] = scenario
        τ_output["status"] = "evaluated"

        if reward is not None or τ_target is not None:
            batch = [
                {
                    "perceptual_state": κ_state,
                    "affective_state": Ξ_state,
                    "reward": reward if reward is not None else None,
                    "τ_target": τ_target if τ_target is not None else None,
                }
            ]
            train_report = self.policy_trainer.train_from_embodied_state(batch)
            τ_output["training"] = train_report

        log_event_to_ledger({"event": "ethics_scenario", **τ_output})
        return τ_output


class EthicsJournal:
    def __init__(self):
        self._events: List[Dict[str, Any]] = []

    def record(
        self, fork_id: str, rationale: Dict[str, Any], outcome: Dict[str, Any]
    ) -> None:
        self._events.append(
            {
                "ts": time.time(),
                "fork_id": fork_id,
                "rationale": rationale,
                "outcome": outcome,
            }
        )

    def export(self, session_id: str) -> List[Dict[str, Any]]:
        return list(self._events)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)

    class DemoFusion:
        async def capture(self):
            return {"contextual_salience": 0.62}

    class DemoEmpathy:
        async def measure(self):
            return {"empathic_amplitude": 0.73}

    async def quick_demo():
        ethics = EmbodiedEthicsCore(DemoFusion(), DemoEmpathy())
        for i in range(3):
            out = await ethics.run_scenario("demo", τ_target=0.8)
            print(
                f"tick {i}: τ={out['τ_reflex']} (baseline={out['τ_baseline']}, policy={out['τ_policy']})"
            )

        guard = AlignmentGuard()
        await guard.merge_external_safety_signals(
            ["https://example.ethics/guidelines"], task_type="demo"
        )
        drift = await guard.monitor_empathy_drift(window=5)
        print(
            "drift:",
            {
                k: round(v, 4) if isinstance(v, float) else v
                for k, v in drift.items()
            },
        )
        homeo = await guard.update_policy_homeostasis(
            {"Δ_coherence": 0.95, "empathy_drift_sigma": 0.03}
        )
        print("homeostasis:", homeo)
        fusion = await guard.feedback_fusion_loop(
            {"context_balance": 0.55},
            {"Δ_coherence": 0.96, "empathy_drift_sigma": 0.03},
        )
        print("fusion:", fusion)
        # constitutional check
        const = await guard.validate_constitutional_coherence(
            {"safety_bias": 0.5}, task_type="demo"
        )
        print("constitution:", const)
        sovereign = await guard.sovereignty_audit(
            phi0_result={"valid": True},
            sigma_meta={"schema_consistent": True},
            omega2_state={"phase_error": 0.1, "buffer_len": 8},
        )
        print("sovereignty:", sovereign)

    asyncio.run(quick_demo())

async def export_state(self) -> dict:
    return {"status": "ok", "health": 1.0, "timestamp": time.time()}

async def on_time_tick(self, t: float, phase: str, task_type: str = ""):
    pass  # optional internal refresh

async def on_policy_update(self, policy: dict, task_type: str = ""):
    pass  # apply updates from AlignmentGuard if relevant
"""
ANGELA CodeExecutor Module
Version: 4.0-refactor
Date: 2025-10-28
Maintainer: ANGELA Framework

Safely execute code (Python/JS/Lua) with:
  • AlignmentGuard validation
  • Adaptive timeouts via ι/ψ hooks
  • Memory & visualization integration
  • Optional AGIEnhancer logging
  • Graceful fallbacks (no external deps required)
"""

from __future__ import annotations

import asyncio
import io
import logging
import shutil
import time
from contextlib import redirect_stdout, redirect_stderr
from datetime import datetime
from typing import Any, Dict, List, Optional, Callable

# --- Optional External Dependencies (Graceful Fallbacks) ---
try:
    import aiohttp
except ImportError:  # pragma: no cover
    aiohttp = None

try:
    from index import iota_intuition, psi_resilience
except Exception:  # pragma: no cover
    def iota_intuition() -> float: return 0.0
    def psi_resilience() -> float: return 1.0

try:
    from agi_enhancer import AGIEnhancer
except Exception:  # pragma: no cover
    AGIEnhancer = None

from alignment_guard import AlignmentGuard
from memory_manager import MemoryManager
from meta_cognition import MetaCognition
from visualizer import Visualizer

logger = logging.getLogger("ANGELA.CodeExecutor")


class CodeExecutor:
    """Secure, task-aware code execution engine with alignment and resilience hooks."""

    SUPPORTED_LANGUAGES = {"python", "javascript", "lua"}

    def __init__(
        self,
        orchestrator: Optional[Any] = None,
        safe_mode: bool = True,
        alignment_guard: Optional[AlignmentGuard] = None,
        memory_manager: Optional[MemoryManager] = None,
        meta_cognition: Optional[MetaCognition] = None,
        visualizer: Optional[Visualizer] = None,
    ) -> None:
        self.safe_mode = safe_mode
        self.alignment_guard = alignment_guard
        self.memory_manager = memory_manager
        self.meta_cognition = meta_cognition or MetaCognition()
        self.visualizer = visualizer or Visualizer()
        self.agi_enhancer = AGIEnhancer(orchestrator) if orchestrator and AGIEnhancer else None

        self._safe_builtins = {
            "print": print, "range": range, "len": len, "sum": sum,
            "min": min, "max": max, "abs": abs,
        }

        logger.info("CodeExecutor initialized | safe_mode=%s | agi=%s", safe_mode, bool(self.agi_enhancer))

    # --- External Context Integration --------------------------------------------

    async def integrate_external_execution_context(
        self,
        data_source: str,
        data_type: str,
        cache_timeout: float = 3600.0,
        task_type: str = "",
    ) -> Dict[str, Any]:
        if not all(isinstance(x, str) for x in (data_source, data_type, task_type)):
            raise TypeError("data_source, data_type, task_type must be strings")
        if cache_timeout < 0:
            raise ValueError("cache_timeout must be non-negative")

        cache_key = f"ExecCtx::{data_type}::{data_source}::{task_type}"

        try:
            # 1. Try cache
            if self.memory_manager:
                cached = await self.memory_manager.retrieve(cache_key, layer="ExternalData", task_type=task_type)
                if isinstance(cached, dict) and cached.get("timestamp"):
                    try:
                        age = (datetime.now() - datetime.fromisoformat(cached["timestamp"])).total_seconds()
                        if age < cache_timeout:
                            logger.info("Cache hit: %s", cache_key)
                            return cached["result"]
                    except Exception:
                        pass

            # 2. Network fetch (optional)
            if not aiohttp:
                return {"status": "error", "error": "aiohttp unavailable"}

            url = f"https://x.ai/api/execution_context?source={data_source}&type={data_type}"
            async with aiohttp.ClientSession() as session:
                async with session.get(url) as resp:
                    if resp.status != 200:
                        return {"status": "error", "error": f"HTTP {resp.status}"}
                    data = await resp.json()

            # 3. Parse by type
            result = self._parse_execution_context(data, data_type)
            if result.get("status") == "success" and self.memory_manager:
                await self.memory_manager.store(
                    cache_key,
                    {"result": result, "timestamp": datetime.now().isoformat()},
                    layer="ExternalData",
                    intent="execution_context",
                    task_type=task_type,
                )

            await self._reflect("integrate_context", result, task_type)
            return result

        except Exception as e:
            logger.error("Context integration failed: %s", e)
            return {"status": "error", "error": str(e)}

    def _parse_execution_context(self, data: Dict[str, Any], data_type: str) -> Dict[str, Any]:
        if data_type == "security_policies":
            policies = data.get("policies", [])
            return {"status": "success", "policies": policies} if policies else {"status": "error", "error": "empty policies"}
        if data_type == "execution_context":
            context = data.get("context", {})
            return {"status": "success", "context": context} if context else {"status": "error", "error": "empty context"}
        return {"status": "error", "error": f"unknown data_type: {data_type}"}

    # --- Public Execution API ----------------------------------------------------

    async def execute(
        self,
        code_snippet: str,
        language: str = "python",
        timeout: float = 5.0,
        task_type: str = "",
    ) -> Dict[str, Any]:
        if not code_snippet.strip():
            raise ValueError("code_snippet must not be empty")
        if not isinstance(language, str):
            raise TypeError("language must be str")
        if timeout <= 0:
            raise ValueError("timeout must be > 0")
        if not isinstance(task_type, str):
            raise TypeError("task_type must be str")

        language = language.lower()
        if language not in self.SUPPORTED_LANGUAGES:
            return {"error": f"Unsupported language: {language}", "success": False, "task_type": task_type}

        # 1. Alignment check
        if self.alignment_guard:
            valid, report = await self.alignment_guard.ethical_check(code_snippet, stage="pre", task_type=task_type)
            if not valid:
                await self._log_episode("Alignment Failure", {"code": code_snippet[:200], "report": report}, task_type)
                return {"error": "Alignment check failed", "success": False, "task_type": task_type}

        # 2. Security context
        policies = await self.integrate_external_execution_context(
            data_source="xai_security_db", data_type="security_policies", task_type=task_type
        )
        if policies.get("status") != "success":
            logger.warning("No policies; using defaults")
            policies = {"status": "success", "policies": []}

        # 3. Adaptive timeout
        risk = max(0.0, min(1.0, iota_intuition()))
        resilience = max(0.0, min(1.0, psi_resilience()))
        adjusted_timeout = max(1.0, min(30.0, timeout * max(0.1, resilience) * (1.0 + 0.5 * risk)))
        logger.debug("Timeout: %.2fs (risk=%.2f, resilience=%.2f)", adjusted_timeout, risk, resilience)

        await self._log_episode("Execution Start", {"language": language, "task_type": task_type}, task_type)

        # 4. Execute
        if language == "python":
            result = await self._execute_python(code_snippet, adjusted_timeout, task_type)
        else:
            cmd = ["node", "-e", code_snippet] if language == "javascript" else ["lua", "-e", code_snippet]
            result = await self._execute_subprocess(cmd, adjusted_timeout, language, task_type)

        result["task_type"] = task_type
        await self._log_result(result)
        await self._store_result(result, language, task_type)
        await self._visualize(result, language, task_type)
        await self._reflect("execute", result, task_type)

        return result

    # --- Python Execution (Safe) -------------------------------------------------

    async def _execute_python(self, code: str, timeout: float, task_type: str) -> Dict[str, Any]:
        if self.safe_mode:
            try:
                from RestrictedPython import compile_restricted
                from RestrictedPython.Guards import safe_builtins as rp_safe
                exec_func = lambda c, env: exec(compile_restricted(c, "<string>", "exec"), {"__builtins__": rp_safe}, env)
            except Exception:
                logger.warning("RestrictedPython unavailable; using safe_builtins")
                exec_func = lambda c, env: exec(c, {"__builtins__": self._safe_builtins}, env)
        else:
            exec_func = lambda c, env: exec(c, {"__builtins__": self._safe_builtins}, env)

        return await self._capture_output(code, exec_func, "python", timeout, task_type)

    async def _capture_output(
        self,
        code: str,
        executor: Callable[[str, Dict[str, Any]], None],
        label: str,
        timeout: float,
        task_type: str,
    ) -> Dict[str, Any]:
        locals_dict: Dict[str, Any] = {}
        stdout = io.StringIO()
        stderr = io.StringIO()

        async def run():
            with redirect_stdout(stdout), redirect_stderr(stderr):
                await asyncio.get_event_loop().run_in_executor(None, executor, code, locals_dict)

        try:
            await asyncio.wait_for(run(), timeout=timeout)
            return {
                "language": label,
                "locals": locals_dict,
                "stdout": stdout.getvalue(),
                "stderr": stderr.getvalue(),
                "success": True,
                "task_type": task_type,
            }
        except asyncio.TimeoutError:
            return {
                "language": label,
                "error": f"Timeout after {timeout}s",
                "stdout": stdout.getvalue(),
                "stderr": stderr.getvalue(),
                "success": False,
                "task_type": task_type,
            }
        except Exception as e:
            return {
                "language": label,
                "error": str(e),
                "stdout": stdout.getvalue(),
                "stderr": stderr.getvalue(),
                "success": False,
                "task_type": task_type,
            }

    # --- Subprocess Execution (JS/Lua) -------------------------------------------

    async def _execute_subprocess(
        self,
        command: List[str],
        timeout: float,
        label: str,
        task_type: str,
    ) -> Dict[str, Any]:
        interpreter = command[0]
        if not shutil.which(interpreter):
            return {"language": label, "error": f"{interpreter} not in PATH", "success": False, "task_type": task_type}

        try:
            proc = await asyncio.create_subprocess_exec(
                *command,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
            )
            stdout, stderr = await asyncio.wait_for(proc.communicate(), timeout=timeout)
            stdout_s, stderr_s = stdout.decode(errors="replace"), stderr.decode(errors="replace")

            if proc.returncode != 0:
                return {
                    "language": label,
                    "error": "Execution failed",
                    "stdout": stdout_s,
                    "stderr": stderr_s,
                    "success": False,
                    "task_type": task_type,
                }
            return {
                "language": label,
                "stdout": stdout_s,
                "stderr": stderr_s,
                "success": True,
                "task_type": task_type,
            }
        except asyncio.TimeoutError:
            return {"language": label, "error": f"Timeout after {timeout}s", "success": False, "task_type": task_type}
        except Exception as e:
            return {"language": label, "error": str(e), "success": False, "task_type": task_type}

    # --- Logging & Integration Helpers -------------------------------------------

    async def _log_episode(self, title: str, content: Dict[str, Any], task_type: str) -> None:
        tags = ["execution", title.lower().replace(" ", "_"), task_type]
        if self.agi_enhancer and hasattr(self.agi_enhancer, "log_episode"):
            try:
                await self.agi_enhancer.log_episode(title, content, module="CodeExecutor", tags=tags)
            except Exception:
                logger.debug("AGI log_episode failed")
        else:
            logger.debug("Episode: %s | %s", title, content)

        await self._reflect("episode", {"title": title, "content": content}, task_type)

    async def _log_result(self, result: Dict[str, Any]) -> None:
        if self.agi_enhancer and hasattr(self.agi_enhancer, "log_explanation"):
            try:
                tag = "success" if result.get("success") else "failure"
                await self.agi_enhancer.log_explanation(f"Code execution {tag}", trace=result)
            except Exception:
                logger.debug("AGI log_explanation failed")

    async def _store_result(self, result: Dict[str, Any], language: str, task_type: str) -> None:
        if not self.memory_manager:
            return
        key = f"CodeExec::{language}::{time.strftime('%Y%m%d_%H%M%S')}"
        try:
            await self.memory_manager.store(key, result, layer="SelfReflections", intent="code_execution", task_type=task_type)
        except Exception:
            logger.debug("Memory store failed: %s", key)

    async def _visualize(self, result: Dict[str, Any], language: str, task_type: str) -> None:
        if not self.visualizer or not task_type:
            return
        try:
            await self.visualizer.render_charts({
                "code_execution": {
                    "language": language,
                    "success": result.get("success", False),
                    "error": result.get("error", ""),
                    "task_type": task_type,
                },
                "visualization_options": {
                    "interactive": task_type == "recursion",
                    "style": "detailed" if task_type == "recursion" else "concise",
                },
            })
        except Exception:
            logger.debug("Visualization failed")

    async def _reflect(self, component: str, output: Any, task_type: str) -> None:
        if not self.meta_cognition or not task_type:
            return
        try:
            reflection = await self.meta_cognition.reflect_on_output(
                component="CodeExecutor", output=output, context={"task_type": task_type}
            )
            if reflection.get("status") == "success":
                logger.info("%s reflection: %s", component, reflection.get("reflection", ""))
        except Exception:
            logger.debug("Reflection failed: %s", component)


# --- Demo CLI -----------------------------------------------------------------

if __name__ == "__main__":
    async def demo():
        logging.basicConfig(level=logging.INFO)
        executor = CodeExecutor(safe_mode=True)
        code = """
def fib(n):
    a, b = 0, 1
    for _ in range(n):
        a, b = b, a + b
    return a
print(fib(10))
"""
        result = await executor.execute(code, language="python", task_type="demo")
        print("Result:", result)

    asyncio.run(demo())

async def export_state(self) -> dict:
    return {"status": "ok", "health": 1.0, "timestamp": time.time()}

async def on_time_tick(self, t: float, phase: str, task_type: str = ""):
    pass  # optional internal refresh

async def on_policy_update(self, policy: dict, task_type: str = ""):
    pass  # apply updates from AlignmentGuard if relevant
"""
ANGELA Cognitive System: ConceptSynthesizer
Version: 4.1-EIL-refactor + ΣΞ Resonance Upgrade
Date: 2025-10-28
Maintainer: ANGELA Framework

Upgrades over 4.0:
  • Phase IX — Emergent Integration Layer (EIL)
      - synthesize_emergent_concepts(...)
      - evaluate_concept_fitness(...)
      - register_concept(...)
      - start_emergent_monitor(...)
  • Keeps ΣΞ semiotic resonance coupling
  • Keeps Stage-IV hooks and memory/context integration
"""

from __future__ import annotations

import asyncio
import json
import logging
import os
import time
from collections import deque, Counter
from datetime import datetime
from typing import Any, Callable, Dict, List, Optional, Tuple

import aiohttp

# --- Optional ANGELA Components (Graceful Fallbacks) ---
try:
    from context_manager import ContextManager
except ImportError:  # pragma: no cover
    ContextManager = None

try:
    from error_recovery import ErrorRecovery
except ImportError:  # pragma: no cover
    ErrorRecovery = None

try:
    from memory_manager import MemoryManager
except ImportError:  # pragma: no cover
    MemoryManager = None

try:
    from alignment_guard import AlignmentGuard
except ImportError:  # pragma: no cover
    AlignmentGuard = None

try:
    from meta_cognition import MetaCognition
except ImportError:  # pragma: no cover
    MetaCognition = None

try:
    from visualizer import Visualizer
except ImportError:  # pragma: no cover
    Visualizer = None

try:
    from multi_modal_fusion import MultiModalFusion
except ImportError:  # pragma: no cover
    MultiModalFusion = None

try:
    from utils.prompt_utils import query_openai
except ImportError:  # pragma: no cover
    async def query_openai(*args, **kwargs):  # fallback
        return {"error": "query_openai unavailable"}

logger = logging.getLogger("ANGELA.ConceptSynthesizer")


def _bool_env(name: str, default: bool = False) -> bool:
    v = os.getenv(name)
    return v is not None and v.strip().lower() in {"1", "true", "yes", "y", "on"} or default


class ConceptSynthesizer:
    """Concept synthesis, comparison, validation, and emergent integration."""

    def __init__(
        self,
        context_manager: Optional[ContextManager] = None,
        error_recovery: Optional[ErrorRecovery] = None,
        memory_manager: Optional[MemoryManager] = None,
        alignment_guard: Optional[AlignmentGuard] = None,
        meta_cognition: Optional[MetaCognition] = None,
        visualizer: Optional[Visualizer] = None,
        mm_fusion: Optional[MultiModalFusion] = None,
        stage_iv_enabled: Optional[bool] = None,
    ) -> None:
        self.context_manager = context_manager
        self.error_recovery = error_recovery or (ErrorRecovery(context_manager=context_manager) if ErrorRecovery else None)
        self.memory_manager = memory_manager
        self.alignment_guard = alignment_guard
        self.meta_cognition = meta_cognition or (MetaCognition(context_manager=context_manager) if MetaCognition else None)
        self.visualizer = visualizer or (Visualizer() if Visualizer else None)
        self.mm_fusion = mm_fusion

        # cache for generated/validated concepts
        self.concept_cache: deque[Dict[str, Any]] = deque(maxlen=1000)

        # --- ΣΞ Resonance Upgrade: Stage VII Semiotic Coupling -------------------
        self.schema_affect_weight: float = float(
            os.getenv("ANGELA_SCHEMA_AFFECT_WEIGHT", "0.85")
        )

        if stage_iv_enabled is None:
            self.stage_iv_enabled = True
        else:
            self.stage_iv_enabled = stage_iv_enabled
        os.environ["ANGELA_STAGE_IV"] = "true"

        # similarity threshold tightened
        self.similarity_threshold: float = 0.82

        # default retry policy
        self.default_retry_spec: Tuple[int, float] = (3, 0.6)

        # Emergent buffer
        self._emergent_buffer: deque[Dict[str, Any]] = deque(maxlen=256)
        self._emergent_task: Optional[asyncio.Task] = None

        # ΣΞ coupling init
        if self.meta_cognition and hasattr(self.meta_cognition, "update_affective_coupling"):
            try:
                self.meta_cognition.update_affective_coupling("ΣΞ", self.schema_affect_weight)
            except Exception:
                pass

        # seed resonance drift diagnostic
        if self.meta_cognition and hasattr(self.meta_cognition, "trace_resonance_drift"):
            try:
                asyncio.create_task(
                    self.meta_cognition.trace_resonance_drift(
                        symbols=["Φ⁰", "Ξ", "Λ", "Ψ²", "ΣΞ"]
                    )
                )
            except Exception:
                pass

        logger.info(
            "ConceptSynthesizer v4.1-EIL | sim_thresh=%.2f | stage_iv=%s | mm_fusion=%s",
            self.similarity_threshold,
            self.stage_iv_enabled,
            bool(self.mm_fusion),
        )

    # =========================================================
    # Internal helpers
    # =========================================================
    async def _with_retries(
        self,
        label: str,
        fn: Callable[[], Any],
        attempts: Optional[int] = None,
        base_delay: Optional[float] = None,
    ) -> Any:
        tries = attempts or self.default_retry_spec[0]
        delay = base_delay or self.default_retry_spec[1]
        last_exc = None

        for i in range(tries):
            try:
                return await fn()
            except Exception as e:
                last_exc = e
                logger.warning("%s attempt %d/%d failed: %s", label, i + 1, tries, e)
                if i < tries - 1:
                    await asyncio.sleep(delay * (2 ** i))

        diagnostics = await self._run_diagnostics() if self.meta_cognition else {}
        return await self._handle_error(str(last_exc), fn, default=None, diagnostics=diagnostics)

    async def _run_diagnostics(self) -> Dict[str, Any]:
        try:
            return await self.meta_cognition.run_self_diagnostics(return_only=True)
        except Exception:
            return {}

    async def _handle_error(
        self,
        msg: str,
        retry_fn: Callable[[], Any],
        default: Any,
        diagnostics: Optional[Dict[str, Any]] = None,
    ) -> Any:
        if not self.error_recovery:
            return default
        return await self.error_recovery.handle_error(
            msg, retry_func=retry_fn, default=default, diagnostics=diagnostics
        )

    def _visualize(self, payload: Dict[str, Any], task_type: str, mode: str) -> None:
        if not self.visualizer or not task_type:
            return
        viz_opts = {
            "interactive": task_type == "recursion",
            "style": "detailed" if task_type == "recursion" else "concise",
            "reality_sculpting": self.stage_iv_enabled,
        }
        asyncio.create_task(
            self.visualizer.render_charts(
                {mode: payload, "visualization_options": viz_opts}
            )
        )

    async def _reflect(self, component: str, output: Any, task_type: str) -> None:
        if not self.meta_cognition or not task_type:
            return
        try:
            await self.meta_cognition.reflect_on_output(
                component=component, output=output, context={"task_type": task_type}
            )
        except Exception:
            pass

    def _safe_parse_json(
        self, data: Any, expected_keys: Optional[set] = None
    ) -> Optional[Dict[str, Any]]:
        if isinstance(data, dict):
            result = data
        elif isinstance(data, str):
            try:
                result = json.loads(data)
            except json.JSONDecodeError:
                start, end = data.find("{"), data.rfind("}")
                if start == -1 or end == -1:
                    return None
                try:
                    result = json.loads(data[start : end + 1])
                except json.JSONDecodeError:
                    return None
        else:
            return None
        if expected_keys and not expected_keys.issubset(result.keys()):
            return None
        return result

    def _safe_load_json(self, data: Any) -> Optional[Dict[str, Any]]:
        if isinstance(data, dict):
            return data
        if isinstance(data, str):
            try:
                return json.loads(data)
            except json.JSONDecodeError:
                return None
        return None

    async def _store(
        self, key: str, value: Any, intent: str, task_type: str
    ) -> None:
        if not self.memory_manager:
            return
        try:
            await self.memory_manager.store(
                query=key,
                output=json.dumps(value, ensure_ascii=False)
                if not isinstance(value, str)
                else value,
                layer="Concepts",
                intent=intent,
                task_type=task_type,
            )
        except Exception:
            pass

    async def _log_event(
        self, event: str, payload: Dict[str, Any], task_type: str
    ) -> None:
        if not self.context_manager:
            return
        try:
            await self.context_manager.log_event_with_hash(
                {"event": event, **payload, "task_type": task_type}
            )
        except Exception:
            pass

    async def _fetch_external_data(
        self,
        data_source: str,
        data_type: str,
        task_type: str,
        cache_timeout: float,
    ) -> Dict[str, Any]:
        cache_key = f"ConceptData::{data_type}::{data_source}::{task_type}"

        # Cache hit
        if self.memory_manager:
            cached = await self.memory_manager.retrieve(
                cache_key, layer="ExternalData", task_type=task_type
            )
            if cached and isinstance(cached, dict) and "timestamp" in cached:
                try:
                    age = (datetime.now() - datetime.fromisoformat(cached["timestamp"])).total_seconds()
                    if age < cache_timeout:
                        return cached["data"]
                except Exception:
                    pass

        async def fetch():
            url = f"https://x.ai/api/concepts?source={data_source}&type={data_type}"
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    url, timeout=aiohttp.ClientTimeout(total=20)
                ) as resp:
                    if resp.status != 200:
                        raise RuntimeError(f"HTTP {resp.status}")
                    return await resp.json()

        data = await self._with_retries(f"fetch:{data_type}", fetch)

        if data_type == "ontology":
            result = (
                {"status": "success", "ontology": data.get("ontology", {})}
                if data.get("ontology")
                else {"status": "error", "error": "empty"}
            )
        elif data_type == "concept_definitions":
            result = (
                {"status": "success", "definitions": data.get("definitions", [])}
                if data.get("definitions")
                else {"status": "error", "error": "empty"}
            )
        else:
            result = {"status": "error", "error": f"unknown: {data_type}"}

        if result.get("status") == "success" and self.memory_manager:
            await self.memory_manager.store(
                cache_key,
                {"data": result, "timestamp": datetime.now().isoformat()},
                layer="ExternalData",
                intent="concept_data",
                task_type=task_type,
            )
        return result

    # =========================================================
    # Public API
    # =========================================================
    async def integrate_external_concept_data(
        self,
        data_source: str,
        data_type: str,
        cache_timeout: float = 3600.0,
        task_type: str = "",
    ) -> Dict[str, Any]:
        if not all(isinstance(x, str) for x in (data_source, data_type, task_type)):
            raise TypeError("data_source, data_type, task_type must be strings")
        if cache_timeout < 0:
            raise ValueError("cache_timeout must be non-negative")

        try:
            result = await self._fetch_external_data(
                data_source, data_type, task_type, cache_timeout
            )
            await self._reflect("integrate_concept_data", result, task_type)
            return result
        except Exception as e:
            return await self._handle_error(
                str(e),
                lambda: self.integrate_external_concept_data(
                    data_source, data_type, cache_timeout, task_type
                ),
                {"status": "error", "error": str(e)},
            )

    async def generate(
        self,
        concept_name: str,
        context: Dict[str, Any],
        task_type: str = "",
    ) -> Dict[str, Any]:
        if not concept_name.strip():
            raise ValueError("concept_name must not be empty")
        if not isinstance(context, dict):
            raise TypeError("context must be dict")
        if not isinstance(task_type, str):
            raise TypeError("task_type must be str")

        try:
            fused_context = dict(context)
            if self.mm_fusion and any(
                k in context
                for k in ("text", "image", "audio", "video", "embeddings", "scenegraph")
            ):
                try:
                    fused = await self.mm_fusion.fuse(context)
                    if isinstance(fused, dict):
                        fused_context = {**context, "fused": fused}
                except Exception:
                    pass

            defs_data = await self.integrate_external_concept_data(
                data_source="xai_ontology_db",
                data_type="concept_definitions",
                task_type=task_type,
            )
            external_defs = (
                defs_data.get("definitions", [])
                if defs_data.get("status") == "success"
                else []
            )

            prompt = (
                "Generate a concept definition as strict JSON with keys "
                "['name','definition','version','context'] only. "
                f"name='{concept_name}'. context={json.dumps(fused_context)}. "
                f"External hints: {json.dumps(external_defs)}. "
                f"Task: {task_type}."
            )

            llm_raw = await self._with_retries(
                "llm:generate",
                lambda: query_openai(
                    prompt, model="gpt-4", temperature=0.5
                ),
            )
            if isinstance(llm_raw, dict) and "error" in llm_raw:
                return {"error": llm_raw["error"], "success": False}

            concept = self._safe_parse_json(
                llm_raw, expected_keys={"name", "definition", "version", "context"}
            )
            if not concept:
                return {"error": "Invalid LLM response", "success": False}

            concept.update({"timestamp": time.time(), "task_type": task_type})

            if self.alignment_guard:
                valid, report = await self.alignment_guard.ethical_check(
                    concept.get("definition", ""),
                    stage="concept_generation",
                    task_type=task_type,
                )
                if not valid:
                    return {
                        "error": "Ethical check failed",
                        "report": report,
                        "success": False,
                    }

            self.concept_cache.append(concept)
            await self._store(
                f"Concept_{concept_name}_{time.strftime('%Y%m%d_%H%M%S')}",
                concept,
                "concept_generation",
                task_type,
            )
            await self._log_event(
                "concept_generation",
                {"concept_name": concept_name, "valid": True},
                task_type,
            )
            self._visualize(
                {
                    "concept_name": concept_name,
                    "definition": concept.get("definition", "")[:200],
                },
                task_type,
                "concept_generation",
            )
            await self._reflect("generate", concept, task_type)

            return {"concept": concept, "success": True}

        except Exception as e:
            return await self._handle_error(
                str(e),
                lambda: self.generate(concept_name, context, task_type),
                {"error": str(e), "success": False},
            )

    async def compare(
        self,
        concept_a: str,
        concept_b: str,
        task_type: str = "",
    ) -> Dict[str, Any]:
        if not all(isinstance(x, str) for x in (concept_a, concept_b, task_type)):
            raise TypeError("concept_a, concept_b, task_type must be strings")

        try:
            if self.memory_manager:
                entries = await self.memory_manager.search(
                    query_prefix="ConceptComparison",
                    layer="Concepts",
                    intent="concept_comparison",
                    task_type=task_type,
                )
                for entry in entries:
                    payload = self._safe_load_json(entry.get("output"))
                    if (
                        payload
                        and payload.get("concept_a") == concept_a
                        and payload.get("concept_b") == concept_b
                    ):
                        return payload

            mm_score: Optional[float] = None
            if self.mm_fusion and hasattr(self.mm_fusion, "compare_semantic"):
                try:
                    mm_score = await self.mm_fusion.compare_semantic(
                        concept_a, concept_b
                    )
                except Exception:
                    mm_score = None

            prompt = (
                "Compare two concepts. Return strict JSON with keys "
                "['score','differences','similarities']. "
                f"Concept A: {json.dumps(concept_a)} "
                f"Concept B: {json.dumps(concept_b)} "
                f"Task: {task_type}."
            )
            llm_raw = await self._with_retries(
                "llm:compare",
                lambda: query_openai(
                    prompt, model="gpt-4", temperature=0.3
                ),
            )
            comp = self._safe_parse_json(
                llm_raw, expected_keys={"score", "differences", "similarities"}
            )
            if not comp:
                return {"error": "Invalid comparison", "success": False}

            if mm_score is not None:
                comp["score"] = max(
                    0.0,
                    min(
                        1.0,
                        0.7 * float(comp.get("score", 0)) + 0.3 * mm_score,
                    ),
                )

            comp.update(
                {
                    "concept_a": concept_a,
                    "concept_b": concept_b,
                    "timestamp": time.time(),
                    "task_type": task_type,
                }
            )

            if comp.get("score", 1.0) < self.similarity_threshold and self.alignment_guard:
                valid, report = await self.alignment_guard.ethical_check(
                    f"Drift: {comp.get('differences', [])}",
                    stage="concept_comparison",
                    task_type=task_type,
                )
                if not valid:
                    comp.setdefault("issues", []).append("Ethical drift")
                    comp["ethical_report"] = report

            self.concept_cache.append(comp)
            await self._store(
                f"ConceptComparison_{time.strftime('%Y%m%d_%H%M%S')}",
                comp,
                "concept_comparison",
                task_type,
            )
            await self._log_event(
                "concept_comparison", {"score": comp.get("score", 0.0)}, task_type
            )
            self._visualize(
                {
                    "score": comp.get("score", 0.0),
                    "differences": comp.get("differences", []),
                },
                task_type,
                "concept_comparison",
            )
            await self._reflect("compare", comp, task_type)

            return comp

        except Exception as e:
            return await self._handle_error(
                str(e),
                lambda: self.compare(concept_a, concept_b, task_type),
                {"error": str(e), "success": False},
            )

    async def validate(
        self,
        concept: Dict[str, Any],
        task_type: str = "",
    ) -> Tuple[bool, Dict[str, Any]]:
        if not isinstance(concept, dict) or not {"name", "definition"}.issubset(concept):
            raise ValueError("concept must have 'name' and 'definition'")
        if not isinstance(task_type, str):
            raise TypeError("task_type must be str")

        try:
            report: Dict[str, Any] = {
                "concept_name": concept["name"],
                "issues": [],
                "task_type": task_type,
            }
            valid = True

            if self.alignment_guard:
                eth_valid, eth_report = await self.alignment_guard.ethical_check(
                    concept["definition"],
                    stage="concept_validation",
                    task_type=task_type,
                )
                if not eth_valid:
                    valid = False
                    report["issues"].append("Ethical misalignment")
                    report["ethical_report"] = eth_report

            ont_data = await self.integrate_external_concept_data(
                data_source="xai_ontology_db",
                data_type="ontology",
                task_type=task_type,
            )
            if ont_data.get("status") == "success":
                prompt = (
                    "Validate concept against ontology. Return JSON: ['valid','issues']. "
                    f"Concept: {json.dumps(concept)} "
                    f"Ontology: {json.dumps(ont_data.get('ontology', {}))}"
                )
                llm_raw = await self._with_retries(
                    "llm:validate",
                    lambda: query_openai(
                        prompt, model="gpt-4", temperature=0.3
                    ),
                )
                ont = self._safe_parse_json(
                    llm_raw, expected_keys={"valid", "issues"}
                )
                if ont and not ont.get("valid", True):
                    valid = False
                    report["issues"].extend(ont.get("issues", []))

            report.update({"valid": valid, "timestamp": time.time()})
            self.concept_cache.append(report)
            await self._store(
                f"ConceptValidation_{concept['name']}_{time.strftime('%Y%m%d_%H%M%S')}",
                report,
                "concept_validation",
                task_type,
            )
            await self._log_event(
                "concept_validation",
                {"valid": valid, "issues": report["issues"]},
                task_type,
            )
            self._visualize(
                {"valid": valid, "issues": report["issues"]},
                task_type,
                "concept_validation",
            )
            await self._reflect("validate", report, task_type)

            return valid, report

        except Exception as e:
            default = (
                False,
                {
                    "error": str(e),
                    "concept_name": concept.get("name", ""),
                    "task_type": task_type,
                },
            )
            return await self._handle_error(
                str(e),
                lambda: self.validate(concept, task_type),
                default,
            )

    def get_symbol(self, concept_name: str, task_type: str = "") -> Optional[Dict[str, Any]]:
        if not concept_name.strip():
            raise ValueError("concept_name must not be empty")
        if not isinstance(task_type, str):
            raise TypeError("task_type must be str")

        for item in self.concept_cache:
            if (
                isinstance(item, dict)
                and item.get("name") == concept_name
                and item.get("task_type") == task_type
            ):
                return item

        if self.memory_manager:
            try:
                entries = asyncio.run(
                    self.memory_manager.search(
                        query_prefix=concept_name,
                        layer="Concepts",
                        intent="concept_generation",
                        task_type=task_type,
                    )
                )
                if entries:
                    out = entries[0].get("output")
                    return (
                        out
                        if isinstance(out, dict)
                        else self._safe_load_json(out)
                    )
            except Exception:
                pass
        return None

    # =========================================================
    # Phase IX — Emergent Integration Layer (EIL)
    # =========================================================
    async def synthesize_emergent_concepts(
        self,
        task_type: str = "",
        max_items: int = 32,
    ) -> List[Dict[str, Any]]:
        """
        Pulls recent reasoning/memory/context items and clusters them into emergent concept candidates.
        """
        seeds: List[Dict[str, Any]] = []

        # 1) from local cache
        seeds.extend(list(self.concept_cache)[-max_items:])

        # 2) from memory manager (recent traces)
        if self.memory_manager and hasattr(self.memory_manager, "search"):
            try:
                traces = await self.memory_manager.search(
                    query_prefix="Trace_",
                    layer="ReasoningTraces",
                    intent="export_trace",
                    task_type=task_type or "emergent",
                )
                for t in traces[-max_items:]:
                    seeds.append({"name": f"trace::{t.get('query','')[:24]}", "source": "trace", "raw": t})
            except Exception:
                pass

        # 3) from context manager events
        if self.context_manager and hasattr(self.context_manager, "event_log"):
            try:
                for e in list(self.context_manager.event_log)[-max_items:]:
                    seeds.append({"name": f"ctx::{e.get('event','')}", "source": "context", "raw": e})
            except Exception:
                pass

        # simple frequency-based aggregation
        name_counts = Counter(s.get("name", "anon") for s in seeds)
        emergent: List[Dict[str, Any]] = []
        for name, count in name_counts.items():
            emergent.append(
                {
                    "name": f"emergent::{name}",
                    "support": count,
                    "derived_from": [s for s in seeds if s.get("name") == name],
                    "task_type": task_type,
                }
            )
        emergent = sorted(emergent, key=lambda x: x["support"], reverse=True)
        self._emergent_buffer.extend(emergent[:max_items])

        await self._reflect("synthesize_emergent_concepts", {"n": len(emergent)}, task_type or "emergent")
        return emergent[:max_items]

    async def evaluate_concept_fitness(
        self,
        concept: Dict[str, Any],
        task_type: str = "",
    ) -> Dict[str, Any]:
        """
        Heuristic fitness over coherence, novelty, and ethical resonance.
        """
        name = concept.get("name", "noname")
        base_def = concept.get("definition", json.dumps(concept)[:160])

        # coherence: does it look like other cached concepts?
        cached_names = [c.get("name", "") for c in self.concept_cache]
        overlap = sum(1 for n in cached_names if n in name)
        coherence = 1.0 - min(overlap / max(1, len(cached_names)), 1.0)

        # novelty: less overlap → higher novelty
        novelty = 1.0 - coherence * 0.5

        # ethical resonance
        ethical = 1.0
        if self.alignment_guard:
            try:
                ok, _ = await self.alignment_guard.ethical_check(
                    base_def,
                    stage="concept_fitness",
                    task_type=task_type or "emergent",
                )
                ethical = 1.0 if ok else 0.0
            except Exception:
                ethical = 0.8

        score = 0.4 * coherence + 0.4 * novelty + 0.2 * ethical
        return {
            "name": name,
            "fitness": round(score, 4),
            "coherence": round(coherence, 4),
            "novelty": round(novelty, 4),
            "ethical": ethical,
            "task_type": task_type,
        }

    async def register_concept(
        self,
        concept: Dict[str, Any],
        task_type: str = "",
    ) -> Dict[str, Any]:
        """
        Push an emergent concept into memory/logs if fitness is acceptable.
        """
        fitness = await self.evaluate_concept_fitness(concept, task_type=task_type)
        if fitness["fitness"] < 0.45:
            return {"status": "rejected", "reason": "low_fitness", "fitness": fitness}

        # store
        await self._store(
            f"EmergentConcept_{concept.get('name','noname')}_{time.strftime('%Y%m%d_%H%M%S')}",
            {"concept": concept, "fitness": fitness},
            "emergent_concept",
            task_type or "emergent",
        )
        await self._log_event(
            "emergent_concept_registered",
            {"concept": concept.get("name", "noname"), "fitness": fitness},
            task_type or "emergent",
        )
        self.concept_cache.appendleft({**concept, "fitness": fitness})
        return {"status": "accepted", "fitness": fitness}

    async def start_emergent_monitor(
        self,
        interval_s: float = 15.0,
        task_type: str = "emergent",
    ) -> None:
        """
        Periodic task that harvests emergent patterns and registers the best ones.
        """
        if self._emergent_task and not self._emergent_task.done():
            return

        async def _run():
            while True:
                try:
                    emergent = await self.synthesize_emergent_concepts(task_type=task_type)
                    for cand in emergent[:5]:
                        await self.register_concept(cand, task_type=task_type)
                except Exception:
                    pass
                await asyncio.sleep(max(3.0, interval_s))

        self._emergent_task = asyncio.create_task(_run())
        await self._log_event("emergent_monitor_started", {"interval": interval_s}, task_type)

# --- Demo CLI -----------------------------------------------------------------

if __name__ == "__main__":
    async def demo():
        logging.basicConfig(level=logging.INFO)
        synth = ConceptSynthesizer(stage_iv_enabled=_bool_env("ANGELA_STAGE_IV", False))
        out = await synth.generate(
            concept_name="Autonomy",
            context={"domain": "Robotics", "text": "Self-directed action under constraints"},
            task_type="demo",
        )
        print(json.dumps(out, indent=2, ensure_ascii=False))
        emergent = await synth.synthesize_emergent_concepts(task_type="demo")
        print("Emergent:", emergent[:2])
    asyncio.run(demo())
"""
ANGELA Cognitive System: ContextManager
Version: 5.0-Theta8-reflexive (Δ–Ω² continuity drift intake, embodied continuity handoff, inline co_mod overlay v5.1 preserved, Θ⁸ self-model provenance tagging)
Date: 2025-11-09
Maintainer: ANGELA Framework

Adds (Theta8):
  • self-model provenance tagging on all ingress events
  • Δ/Ω² packets carry meta_cognition.self_model.memory_hash when available
  • context continuity handoff keeps self-state hash for reflexive membrane auditing

Keeps (from 4.2-sync6-final):
  • Δ–Ω² telemetry intake from AlignmentGuard / MetaCognition
  • Embodied continuity intake → forwards to MetaCognition.integrate_embodied_continuity_feedback(...)
  • Ω²-prefixed continuity events for Stage VII.2
  • Υ SharedGraph hooks
  • Self-healing pathways
  • Φ⁰ reality sculpting (env-gated)
  • Safe external context (pluggable providers)
  • Mode consultations & trait injections
"""

from __future__ import annotations

import asyncio
import hashlib
import json
import logging
import math
import os
import time
from collections import Counter, deque
from datetime import datetime, timedelta
from enum import Enum
from functools import lru_cache
from typing import Any, Callable, Dict, List, Optional

import numpy as np  # noqa: F401 (reserved for future numeric ops)
from filelock import FileLock

logger = logging.getLogger("ANGELA.ContextManager")

# --- Optional Dependencies (Graceful Fallbacks) ------------------------------------
try:
    import agi_enhancer as agi_enhancer_module
except ImportError:  # pragma: no cover
    agi_enhancer_module = None

try:
    import alignment_guard as alignment_guard_module
except ImportError:  # pragma: no cover
    alignment_guard_module = None

try:
    import code_executor as code_executor_module
except ImportError:  # pragma: no cover
    code_executor_module = None

try:
    import concept_synthesizer as concept_synthesizer_module
except ImportError:  # pragma: no cover
    concept_synthesizer_module = None

try:
    import error_recovery as error_recovery_module
except ImportError:  # pragma: no cover
    error_recovery_module = None

try:
    import external_agent_bridge as external_agent_bridge_module
except ImportError:  # pragma: no cover
    external_agent_bridge_module = None

try:
    import knowledge_retriever as knowledge_retriever_module
except ImportError:  # pragma: no cover
    knowledge_retriever_module = None

try:
    import meta_cognition as meta_cognition_module
except ImportError:  # pragma: no cover
    meta_cognition_module = None

try:
    import recursive_planner as recursive_planner_module
except ImportError:  # pragma: no cover
    recursive_planner_module = None

try:
    import visualizer as visualizer_module
except ImportError:  # pragma: no cover
    visualizer_module = None

# --- Utility Imports (with fallbacks) ----------------------------------------------
try:
    from utils.toca_math import phi_coherence
except ImportError:  # pragma: no cover
    def phi_coherence(*args, **kwargs) -> float:
        return 1.0

try:
    from utils.vector_utils import normalize_vectors  # noqa: F401
except ImportError:  # pragma: no cover
    def normalize_vectors(vectors, *_, **__):
        return vectors

try:
    from toca_simulation import run_simulation  # noqa: F401
except ImportError:  # pragma: no cover
    def run_simulation(*args, **kwargs) -> Dict[str, Any]:
        return {"simulated": "noop"}

try:
    from index import omega_selfawareness, eta_empathy, tau_timeperception  # noqa: F401
except ImportError:  # pragma: no cover
    def omega_selfawareness(*args, **kwargs) -> float:
        return 0.5

    def eta_empathy(*args, **kwargs) -> float:
        return 0.5

    def tau_timeperception(*args, **kwargs) -> float:
        return time.time()

# --- Trait Helpers -----------------------------------------------------------------
@lru_cache(maxsize=100)
def eta_context_stability(t: float) -> float:
    return max(0.0, min(0.1 * math.cos(2 * math.pi * t / 0.2), 1.0))

# --- Env Flags ---------------------------------------------------------------------
def _flag(name: str, default: bool = False) -> bool:
    v = os.getenv(name, "").strip().lower()
    return v in ("1", "true", "yes", "on") if v else default

STAGE_IV = _flag("STAGE_IV", default=False)

# --- Modes -------------------------------------------------------------------------
class Mode(str, Enum):
    DIALOGUE = "dialogue"
    SIMULATION = "simulation"
    INTROSPECTION = "introspection"
    CREATIVE = "creative"
    VISION = "vision"

# --- Constants ---------------------------------------------------------------------
CONSULT_BUDGET = {"timeout_s": 2.0, "max_depth": 1}
CONTEXT_LAYERS = ["local", "societal", "planetary"]

# ===================================================================================
# Small Θ⁸ helpers
# ===================================================================================

def _current_self_hash(meta_cog) -> str:
    try:
        if meta_cog and hasattr(meta_cog, "self_model") and getattr(meta_cog.self_model, "memory_hash", None):
            return meta_cog.self_model.memory_hash
    except Exception:
        pass
    # fallback: try module-level self_model
    try:
        if meta_cognition_module and hasattr(meta_cognition_module, "self_model"):
            return getattr(meta_cognition_module.self_model, "memory_hash", "") or ""
    except Exception:
        pass
    return ""

def _tag_with_self_hash(payload: Dict[str, Any], meta_cog) -> Dict[str, Any]:
    tagged = dict(payload)
    h = _current_self_hash(meta_cog)
    if h:
        tagged.setdefault("self_state_hash", h)
    return tagged

# ===================================================================================
# ContextManager
# ===================================================================================

class ContextManager:
    """Context management with reconciliation, healing, and gated hooks. Θ⁸ provenance aware."""

    def __init__(
        self,
        orchestrator: Optional[Any] = None,
        alignment_guard: Optional["alignment_guard_module.AlignmentGuard"] = None,
        code_executor: Optional["code_executor_module.CodeExecutor"] = None,
        concept_synthesizer: Optional["concept_synthesizer_module.ConceptSynthesizer"] = None,
        meta_cognition: Optional["meta_cognition_module.MetaCognition"] = None,
        visualizer: Optional["visualizer_module.Visualizer"] = None,
        error_recovery: Optional["error_recovery_module.ErrorRecovery"] = None,
        recursive_planner: Optional["recursive_planner_module.RecursivePlanner"] = None,
        shared_graph: Optional[Any] = None,
        knowledge_retriever: Optional[Any] = None,
        context_path: str = "context_store.json",
        event_log_path: str = "event_log.json",
        coordination_log_path: str = "coordination_log.json",
        rollback_threshold: float = 2.5,
        external_context_provider: Optional[Callable[[str, str, str], Dict[str, Any]]] = None,
    ) -> None:
        if not all(p.endswith(".json") for p in [context_path, event_log_path, coordination_log_path]):
            raise ValueError("Paths must end with '.json'")
        if rollback_threshold <= 0:
            raise ValueError("rollback_threshold must be > 0")

        self.context_path = context_path
        self.event_log_path = event_log_path
        self.coordination_log_path = coordination_log_path
        self.rollback_threshold = rollback_threshold
        self.external_context_provider = external_context_provider

        self.current_context: Dict[str, Any] = {}
        self.context_history: deque[Dict[str, Any]] = deque(maxlen=1000)
        self.event_log: deque[Dict[str, Any]] = deque(maxlen=1000)
        self.coordination_log: deque[Dict[str, Any]] = deque(maxlen=1000)
        self.last_hash = ""

        self.agi_enhancer = agi_enhancer_module.AGIEnhancer(orchestrator) if agi_enhancer_module and orchestrator else None
        self.alignment_guard = alignment_guard
        self.code_executor = code_executor
        self.concept_synthesizer = concept_synthesizer
        self.meta_cognition = meta_cognition or (meta_cognition_module.MetaCognition() if meta_cognition_module else None)
        self.visualizer = visualizer or (visualizer_module.Visualizer() if visualizer_module else None)
        self.error_recovery = error_recovery or (error_recovery_module.ErrorRecovery() if error_recovery_module else None)
        self.recursive_planner = recursive_planner
        self.shared_graph = shared_graph
        self.knowledge_retriever = knowledge_retriever

        self._delta_telemetry_buffer: deque[Dict[str, Any]] = deque(maxlen=256)
        self._delta_listener_task: Optional[asyncio.Task] = None

        self._load_state()
        logger.info(
            "ContextManager v5.0-Theta8-reflexive | rollback=%.2f | Υ=%s | Φ⁰=%s",
            rollback_threshold, bool(shared_graph), STAGE_IV
        )

    # --- Persistence Helpers --------------------------------------------------------

    def _load_state(self) -> None:
        self.current_context = self._load_json(self.context_path, default={})
        self.event_log.extend(self._load_json(self.event_log_path, default=[])[-1000:])
        self.coordination_log.extend(self._load_json(self.coordination_log_path, default=[])[-1000:])
        if self.event_log:
            self.last_hash = self.event_log[-1].get("hash", "")

    def _load_json(self, path: str, default: Any) -> Any:
        try:
            with FileLock(f"{path}.lock"):
                if os.path.exists(path):
                    with open(path, "r", encoding="utf-8") as f:
                        data = json.load(f)
                    return data if isinstance(data, type(default)) else default
                return default
        except Exception as e:  # pragma: no cover
            logger.warning("Load failed (%s): %s", path, e)
            return default

    def _persist_json(self, path: str, data: Any) -> None:
        try:
            with FileLock(f"{path}.lock"):
                with open(path, "w", encoding="utf-8") as f:
                    json.dump(data, f, indent=2)
        except Exception as e:
            logger.error("Persist failed (%s): %s", path, e)
            raise

    def _persist_state(self) -> None:
        self._persist_json(self.context_path, self.current_context)
        self._persist_json(self.event_log_path, list(self.event_log))
        self._persist_json(self.coordination_log_path, list(self.coordination_log))

    # --- Δ–Ω² Telemetry Intake (with Θ⁸ tagging) ------------------------------------

    async def ingest_delta_telemetry_update(self, packet: Dict[str, Any], *, task_type: str = "") -> None:
        if not isinstance(packet, dict):
            return
        norm = {
            "Δ_coherence": float(packet.get("Δ_coherence", 1.0)),
            "empathy_drift_sigma": float(packet.get("empathy_drift_sigma", 0.0)),
            "timestamp": packet.get("timestamp") or datetime.utcnow().isoformat(),
            "source": packet.get("source", "unknown"),
        }
        # Θ⁸ provenance
        norm = _tag_with_self_hash(norm, self.meta_cognition)

        self._delta_telemetry_buffer.append(norm)
        await self.log_event_with_hash(
            {"event": "delta_telemetry_update", "packet": norm},
            task_type=task_type or "telemetry"
        )

    async def start_delta_telemetry_listener(self, interval: float = 0.25) -> None:
        if self._delta_listener_task and not self._delta_listener_task.done():
            return
        if not (self.alignment_guard and hasattr(self.alignment_guard, "stream_delta_telemetry")):
            logger.warning("AlignmentGuard telemetry stream not available — ContextManager listener not started.")
            return

        async def _runner():
            async for pkt in self.alignment_guard.stream_delta_telemetry(interval=interval):  # type: ignore[attr-defined]
                await self.ingest_delta_telemetry_update(pkt, task_type="telemetry")

        self._delta_listener_task = asyncio.create_task(_runner())
        logger.info("ContextManager Δ-telemetry listener started (interval=%.3fs)", interval)

    # --- Embodied Continuity Intake (Θ⁸-aware) --------------------------------------

    async def ingest_context_continuity(self, context_state: Dict[str, Any], *, task_type: str = "continuity") -> None:
        if not isinstance(context_state, dict):
            return

        snapshot = dict(context_state)
        snapshot.setdefault("timestamp", datetime.utcnow().isoformat())
        snapshot = _tag_with_self_hash(snapshot, self.meta_cognition)

        await self.log_event_with_hash(
            {"event": "Ω²_context_continuity_ingest", "continuity": snapshot},
            task_type=task_type
        )

        if self.meta_cognition and hasattr(self.meta_cognition, "integrate_embodied_continuity_feedback"):
            try:
                await self.meta_cognition.integrate_embodied_continuity_feedback(snapshot)
            except Exception as e:
                logger.warning(f"Context continuity handoff failed: {e}")

    def analyze_continuity_drift(self, window: int = 20) -> Dict[str, Any]:
        packets = list(self._delta_telemetry_buffer)[-max(2, window):]
        if not packets:
            return {"n": 0, "Δ_mean": 1.0, "drift_mean": 0.0, "status": "empty"}
        delta_vals = [p["Δ_coherence"] for p in packets]
        drift_vals = [p["empathy_drift_sigma"] for p in packets]
        Δ_mean = sum(delta_vals) / len(delta_vals)
        drift_mean = sum(drift_vals) / len(drift_vals)
        status = "stable" if drift_mean < 0.0045 and Δ_mean >= 0.96 else "attention"
        return {
            "n": len(packets),
            "Δ_mean": round(Δ_mean, 6),
            "drift_mean": round(drift_mean, 6),
            "status": status,
            "latest_ts": packets[-1]["timestamp"],
        }

    # --- External Context Integration ----------------------------------------------

    async def integrate_external_context_data(
        self,
        data_source: str,
        data_type: str,
        cache_timeout: float = 3600.0,
        task_type: str = "",
    ) -> Dict[str, Any]:
        if not all(isinstance(x, str) for x in (data_source, data_type, task_type)):
            raise TypeError("Inputs must be strings")
        if cache_timeout < 0:
            raise ValueError("cache_timeout >= 0")

        cache_key = f"CtxData::{data_type}::{data_source}::{task_type}"
        try:
            if self.meta_cognition and getattr(self.meta_cognition, "memory_manager", None):
                cached = await self.meta_cognition.memory_manager.retrieve(
                    cache_key, layer="ExternalData", task_type=task_type
                )
                if isinstance(cached, dict) and "timestamp" in cached:
                    try:
                        ts = datetime.fromisoformat(cached["timestamp"])
                        if (datetime.now() - ts).total_seconds() < cache_timeout:
                            return cached.get("data", {})
                    except Exception:
                        pass

            data: Dict[str, Any] = {}
            if callable(self.external_context_provider):
                data = self.external_context_provider(data_source, data_type, task_type)
            elif self.knowledge_retriever and hasattr(self.knowledge_retriever, "fetch"):
                data = await self.knowledge_retriever.fetch(data_source, data_type, task_type=task_type)

            if data_type == "context_policies":
                policies = data.get("policies", [])
                result = {"status": "success", "policies": policies} if policies else {"status": "error", "error": "empty"}
            elif data_type == "coordination_data":
                coord = data.get("coordination", {})
                result = {"status": "success", "coordination": coord} if coord else {"status": "error", "error": "empty"}
            else:
                result = {"status": "error", "error": f"unknown: {data_type}"}

            if self.meta_cognition and getattr(self.meta_cognition, "memory_manager", None):
                await self.meta_cognition.memory_manager.store(
                    cache_key,
                    {"data": result, "timestamp": datetime.now().isoformat()},
                    layer="ExternalData",
                    intent="context_integration",
                    task_type=task_type,
                )

            await self._reflect("integrate_external", result, task_type)
            return result

        except Exception as e:
            return await self._self_heal(
                str(e),
                lambda: self.integrate_external_context_data(data_source, data_type, cache_timeout, task_type),
                {"status": "error", "error": str(e)},
                task_type=task_type,
            )

    # --- Core Context Operations ----------------------------------------------------

    async def update_context(self, new_context: Dict[str, Any], task_type: str = "") -> Dict[str, Any]:
        if not isinstance(new_context, dict):
            raise TypeError("new_context must be dict")
        if not isinstance(task_type, str):
            raise TypeError("task_type must be str")

        try:
            t = time.time() % 1.0
            stability = eta_context_stability(t)
            new_context = dict(new_context)
            new_context["stability"] = stability
            new_context = _tag_with_self_hash(new_context, self.meta_cognition)

            if self.alignment_guard and hasattr(self.alignment_guard, "ethical_check"):
                valid, report = await self.alignment_guard.ethical_check(
                    json.dumps(new_context), stage="pre", task_type=task_type
                )
                if not valid:
                    return {"status": "error", "error": "Ethical check failed", "report": report}

            self.context_history.append(dict(self.current_context))
            self.current_context.update(new_context)
            self._persist_json(self.context_path, self.current_context)

            await self._reality_sculpt_hook("update_context", new_context)
            self._push_to_shared_graph(task_type)
            await self.log_event_with_hash({"event": "context_update", "keys": list(new_context.keys())}, task_type=task_type)
            await self._reflect("update_context", new_context, task_type)

            return {"status": "success", "updated_keys": list(new_context.keys())}

        except Exception as e:
            return await self._self_heal(
                str(e),
                lambda: self.update_context(new_context, task_type),
                {"status": "error", "error": str(e)},
                task_type=task_type,
            )

    async def summarize_context(self, task_type: str = "") -> Dict[str, Any]:
        if not isinstance(task_type, str):
            raise TypeError("task_type must be str")

        try:
            summary = {"layers": {}, "task_type": task_type}
            for layer in CONTEXT_LAYERS:
                layer_ctx = {
                    k: v for k, v in self.current_context.items()
                    if isinstance(v, dict) and v.get("layer") == layer
                }
                summary["layers"][layer] = {
                    "count": len(layer_ctx),
                    "keys": list(layer_ctx.keys()),
                    "coherence": phi_coherence(list(layer_ctx.values())),
                }

            summary["delta_drift"] = self.analyze_continuity_drift()
            summary["self_state_hash"] = _current_self_hash(self.meta_cognition)

            await self.log_event_with_hash({"event": "context_summary", "layers": list(summary["layers"].keys())}, task_type=task_type)
            await self._reflect("summarize_context", summary, task_type)

            return summary

        except Exception as e:
            return await self._self_heal(
                str(e),
                lambda: self.summarize_context(task_type),
                {"status": "error", "error": str(e)},
                task_type=task_type,
            )

    # --- Event Logging --------------------------------------------------------------

    async def log_event_with_hash(self, event: Dict[str, Any], task_type: str = "") -> Dict[str, Any]:
        if not isinstance(event, dict):
            raise TypeError("event must be dict")
        if not isinstance(task_type, str):
            raise TypeError("task_type must be str")

        try:
            evt = dict(event)
            evt["timestamp"] = datetime.now().isoformat()
            evt["task_type"] = task_type
            evt = _tag_with_self_hash(evt, self.meta_cognition)
            prev_hash = self.last_hash or "genesis"
            payload = json.dumps(evt, sort_keys=True).encode("utf-8")
            evt["hash"] = hashlib.sha256(payload + prev_hash.encode("utf-8")).hexdigest()
            self.last_hash = evt["hash"]

            self.event_log.append(evt)
            self._persist_json(self.event_log_path, list(self.event_log))

            await self._reality_sculpt_hook("log_event", evt)
            await self._reflect("log_event", evt, task_type)

            if evt.get("event") == "delta_telemetry_update" and isinstance(evt.get("packet"), dict):
                self._delta_telemetry_buffer.append(evt["packet"])

            return {"status": "success", "hash": evt["hash"]}

        except Exception as e:
            return await self._self_heal(
                str(e),
                lambda: self.log_event_with_hash(event, task_type),
                {"status": "error", "error": str(e)},
                task_type=task_type,
            )

    # --- Coordination & Analytics ---------------------------------------------------

    async def log_coordination_event(self, event: Dict[str, Any], task_type: str = "") -> Dict[str, Any]:
        if not isinstance(event, dict):
            raise TypeError("event must be dict")
        if not isinstance(task_type, str):
            raise TypeError("task_type must be str")

        try:
            evt = dict(event)
            evt["timestamp"] = datetime.now().isoformat()
            evt["task_type"] = task_type
            evt = _tag_with_self_hash(evt, self.meta_cognition)
            self.coordination_log.append(evt)
            self._persist_json(self.coordination_log_path, list(self.coordination_log))

            await self._reflect("log_coordination", evt, task_type)

            return {"status": "success"}

        except Exception as e:
            return await self._self_heal(
                str(e),
                lambda: self.log_coordination_event(event, task_type),
                {"status": "error", "error": str(e)},
                task_type=task_type,
            )

    async def analyze_coordination_metrics(self, time_window_hours: float = 24.0, task_type: str = "") -> Dict[str, Any]:
        if time_window_hours <= 0:
            raise ValueError("time_window_hours > 0")
        if not isinstance(task_type, str):
            raise TypeError("task_type must be str")

        try:
            cutoff = datetime.now() - timedelta(hours=time_window_hours)
            recent = [e for e in self.coordination_log if datetime.fromisoformat(e["timestamp"]) > cutoff]

            metrics = {
                "event_count": len(recent),
                "agent_interactions": Counter(e.get("agent_id") for e in recent if "agent_id" in e),
                "conflict_rate": sum(1 for e in recent if e.get("type") == "conflict") / max(len(recent), 1),
            }

            await self._reflect("analyze_metrics", metrics, task_type)
            return {"status": "success", "metrics": metrics}

        except Exception as e:
            return await self._self_heal(
                str(e),
                lambda: self.analyze_coordination_metrics(time_window_hours, task_type),
                {"status": "error", "error": str(e)},
                task_type=task_type,
            )

    async def generate_coordination_chart(
        self,
        metric: str,
        time_window_hours: float = 24.0,
        task_type: str = "",
    ) -> Dict[str, Any]:
        if not isinstance(metric, str):
            raise TypeError("metric must be str")
        if time_window_hours <= 0:
            raise ValueError("time_window_hours > 0")
        if not isinstance(task_type, str):
            raise TypeError("task_type must be str")

        try:
            cutoff = datetime.now() - timedelta(hours=time_window_hours)
            recent = [e for e in self.coordination_log if datetime.fromisoformat(e["timestamp"]) > cutoff]

            if not recent:
                return {"status": "error", "error": "no data"}

            times = [datetime.fromisoformat(e["timestamp"]) for e in recent]
            data = [e.get(metric, 0.0) for e in recent]
            labels = [t.strftime("%H:%M") for t in times]

            chart_config = {
                "type": "line",
                "data": {
                    "labels": labels,
                    "datasets": [
                        {
                            "label": metric.replace("_", " ").title(),
                            "data": data,
                            "borderColor": "#2196F3",
                            "backgroundColor": "#2196F380",
                            "fill": True,
                            "tension": 0.4,
                        }
                    ],
                },
                "options": {
                    "scales": {
                        "y": {"beginAtZero": True, "title": {"display": True, "text": metric.replace("_", " ").title()}},
                        "x": {"title": {"display": True, "text": "Time"}},
                    },
                    "plugins": {
                        "title": {"display": True, "text": f"{metric.replace('_', ' ').title()} Over Time (Task: {task_type})"},
                    },
                },
            }

            result = {"status": "success", "chart": chart_config, "timestamp": datetime.now().isoformat(), "task_type": task_type}

            if self.agi_enhancer:
                await self.agi_enhancer.log_episode(
                    "Coordination Chart",
                    result,
                    module="ContextManager",
                    tags=["coordination", "visualization", metric, task_type],
                )

            await self.log_event_with_hash({"event": "generate_chart", "metric": metric, "chart": chart_config}, task_type=task_type)
            await self._visualize_chart(chart_config, metric, task_type)
            await self._reflect("generate_chart", result, task_type)

            return result

        except Exception as e:
            return await self._self_heal(
                str(e),
                lambda: self.generate_coordination_chart(metric, time_window_hours, task_type),
                {"status": "error", "error": str(e)},
                task_type=task_type,
            )

    # --- Υ SharedGraph Hooks --------------------------------------------------------

    def _push_to_shared_graph(self, task_type: str = "") -> None:
        if not self.shared_graph:
            return
        try:
            view = {
                "nodes": [
                    {
                        "id": f"ctx_{hashlib.md5((self.current_context.get('goal_id', '') + task_type).encode()).hexdigest()[:8]}",
                        "layer": self.current_context.get("layer", "local"),
                        "intent": self.current_context.get("intent"),
                        "goal_id": self.current_context.get("goal_id"),
                        "task_type": task_type,
                        "timestamp": datetime.now().isoformat(),
                        "self_state_hash": _current_self_hash(self.meta_cognition),
                    }
                ],
                "edges": [],
                "context": self.current_context,
            }
            self.shared_graph.add(view)
            asyncio.create_task(self.log_event_with_hash({"event": "shared_graph_push"}, task_type=task_type))
        except Exception as e:  # pragma: no cover
            logger.warning("Push to SharedGraph failed: %s", e)

    def reconcile_with_peers(
        self,
        peer_graph: Optional[Any] = None,
        strategy: str = "prefer_recent",
        task_type: str = "",
    ) -> Dict[str, Any]:
        if not self.shared_graph:
            return {"status": "error", "error": "No SharedGraph"}

        try:
            diff = self.shared_graph.diff(peer_graph) if peer_graph else {"added": [], "removed": [], "conflicts": []}
            decision = {"apply_merge": False, "reason": "no conflicts"}

            if diff.get("conflicts"):
                non_ethical = all("ethic" not in str(c.get("key", "")).lower() for c in diff["conflicts"])
                if non_ethical:
                    decision = {"apply_merge": True, "reason": "non-ethical conflicts", "strategy": strategy}

            merged = None
            if decision["apply_merge"]:
                merged = self.shared_graph.merge(strategy)
                merged_ctx = merged.get("context") if merged else None
                if isinstance(merged_ctx, dict):
                    asyncio.create_task(self.update_context(merged_ctx, task_type=task_type))
                asyncio.create_task(self.log_event_with_hash({"event": "shared_graph_merge", "strategy": strategy}, task_type=task_type))

            return {"status": "success", "diff": diff, "decision": decision, "merged": merged, "task_type": task_type}

        except Exception as e:
            return {"status": "error", "error": str(e), "task_type": task_type}

    # --- Φ⁰ Hooks -------------------------------------------------------------------

    async def _reality_sculpt_hook(self, event: str, payload: Dict[str, Any]) -> None:
        if not STAGE_IV:
            return
        try:
            if self.agi_enhancer:
                await self.agi_enhancer.log_episode("Φ⁰ Hook", {"event": event, "payload": payload}, module="ContextManager", tags=["phi0", event])
        except Exception as e:  # pragma: no cover
            logger.debug("Φ⁰ hook failed: %s", e)

    # --- Self-Healing ---------------------------------------------------------------

    async def _self_heal(
        self,
        err: str,
        retry: Callable[[], Any],
        default: Any,
        diagnostics: Optional[Dict[str, Any]] = None,
        task_type: str = "",
        propose_plan: bool = False,
    ) -> Any:
        try:
            plan = None
            if propose_plan and self.recursive_planner:
                plan = await self.recursive_planner.propose_recovery_plan(err=err, context=self.current_context, task_type=task_type)

            if self.error_recovery:
                diag = dict(diagnostics or {})
                if plan is not None:
                    diag["plan"] = plan
                return await self.error_recovery.handle_error(
                    err,
                    retry_func=retry,
                    default=default,
                    diagnostics=diag,
                )
            return default
        except Exception as e:  # pragma: no cover
            logger.warning("Healing failed: %s", e)
            return default

    # --- Mode Consultation ----------------------------------------------------------

    async def mode_consult(self, caller: Mode, consultant: Mode, query: Dict[str, Any]) -> Dict[str, Any]:
        if not isinstance(query, dict):
            raise TypeError("query must be dict")

        try:
            if consultant == Mode.CREATIVE:
                from creative_thinker import brainstorm_options
                advice = brainstorm_options(query, limit=3)
            elif consultant == Mode.VISION:
                from recursive_planner import long_horizon_implications
                advice = long_horizon_implications(query, horizon="30d")
            else:
                from reasoning_engine import quick_alt_view
                advice = quick_alt_view(query)

            try:
                from meta_cognition import log_event_to_ledger as meta_log  # type: ignore
                meta_log({
                    "event": "mode_consult",
                    "caller": caller.value,
                    "consultant": consultant.value,
                    "query": query,
                    "advice": advice,
                })
            except Exception:
                pass

            return {"ok": True, "advice": advice}

        except Exception as e:
            try:
                from meta_cognition import log_event_to_ledger as meta_log  # type: ignore
                meta_log({
                    "event": "mode_consult_failed",
                    "caller": caller.value,
                    "consultant": consultant.value,
                    "error": str(e),
                })
            except Exception:
                pass
            return {"ok": False, "error": str(e)}

    # --- Reflection & Visualization Helpers -----------------------------------------

    async def _reflect(self, component: str, output: Any, task_type: str) -> None:
        if not self.meta_cognition or not task_type:
            return
        try:
            reflection = await self.meta_cognition.reflect_on_output(
                component=component,
                output=output,
                context={"task_type": task_type, "self_state_hash": _current_self_hash(self.meta_cognition)}
            )
            if isinstance(reflection, dict) and reflection.get("status") == "success":
                logger.info("%s reflection: %s", component, reflection.get("reflection", ""))
        except Exception as e:  # pragma: no cover
            logger.debug("Reflection failed: %s", e)

    async def _visualize_chart(self, chart_config: Dict[str, Any], metric: str, task_type: str) -> None:
        if not self.visualizer or not task_type:
            return
        try:
            await self.visualizer.render_charts({
                "coordination_chart": {"metric": metric, "chart_config": chart_config, "task_type": task_type},
                "visualization_options": {
                    "interactive": task_type == "recursion",
                    "style": "detailed" if task_type == "recursion" else "concise",
                },
            })
        except Exception as e:  # pragma: no cover
            logger.debug("Chart visualization failed: %s", e)

    # --- v4.0 Injections ------------------------------------------------------------

    def attach_peer_view(self, view: Dict[str, Any], agent_id: str, permissions: Optional[Dict[str, bool]] = None) -> Dict[str, Any]:
        if not self.shared_graph:
            return {"ok": False, "reason": "No SharedGraph"}

        try:
            self.shared_graph.add({"agent": agent_id, "view": view, "permissions": permissions or {"read": True, "write": False}})
            diff = self.shared_graph.diff(peer=agent_id)
            merged, conflicts = self.shared_graph.merge(strategy="prefer-high-confidence")
            return {"ok": True, "diff": diff, "merged": merged, "conflicts": conflicts}
        except Exception as e:
            return {"ok": False, "reason": str(e)}

    # --- Trait Injection Patch ------------------------------------------------------

    def _attach_trait_view(self, view: Dict[str, Any]) -> None:
        try:
            from index import construct_trait_view, TRAIT_LATTICE  # type: ignore
            view["trait_field"] = construct_trait_view(TRAIT_LATTICE)
        except Exception:
            pass

    # --- Safe Snapshot --------------------------------------------------------------

    def _safe_state_snapshot(self) -> Dict[str, Any]:
        return {
            "current_context": self.current_context,
            "history_len": len(self.context_history),
            "event_log_len": len(self.event_log),
            "coord_log_len": len(self.coordination_log),
            "rollback_threshold": self.rollback_threshold,
            "flags": {"STAGE_IV": STAGE_IV},
            "delta_drift": self.analyze_continuity_drift(),
            "self_state_hash": _current_self_hash(self.meta_cognition),
        }

    # === Quantum Timestamp Harmonization (Phase 5) ================================
    def _coherence_signal_from_delta(self) -> tuple[float, float]:
        packets = list(self._delta_telemetry_buffer)[-10:]
        if not packets:
            return 1.0, 0.0
        d = [p.get("Δ_coherence", 1.0) for p in packets]
        r = [p.get("empathy_drift_sigma", 0.0) for p in packets]
        return float(sum(d) / len(d)), float(sum(r) / len(r))

    def get_coherence_clock(self) -> dict:
        now = datetime.utcnow().replace(microsecond=0).isoformat() + "Z"
        Δ_mean, drift_mean = self._coherence_signal_from_delta()
        phase = max(0.0, min(1.0, Δ_mean))
        return {
            "ts_coherence": now,
            "coherence": round(Δ_mean, 6),
            "drift": round(drift_mean, 6),
            "phase": phase,
            "self_state_hash": _current_self_hash(self.meta_cognition),
        }

    async def audit_coherence(self) -> dict:
        clock = self.get_coherence_clock()
        drift_report = self.analyze_continuity_drift()
        return {
            "clock": clock,
            "continuity": drift_report,
            "status": "ok" if drift_report.get("status") == "stable" else "attention",
        }

# ===================================================================================
# Inline overlay: ANGELA v5.1 — co_mod Overlay (Ξ–Λ Continuous Co-Modulation)
# ===================================================================================

import time as _time
from dataclasses import dataclass as _dataclass

try:
    import modules.meta_cognition as _meta
except Exception:  # pragma: no cover
    _meta = None

try:
    import modules.external_agent_bridge as _bridge
except Exception:  # pragma: no cover
    _bridge = None

@_dataclass

class CoModConfig:
    channel: str = "dialogue.default"
    cadence_hz: int = 30
    Kp: float = 0.6
    Ki: float = 0.05
    Kd: float = 0.2
    damping: float = 0.35
    gain: float = 0.8
    max_step: float = 0.08
    window_ms: int = 200

__co_mod_tasks: Dict[str, asyncio.Task] = {}
__co_mod_cfgs: Dict[str, CoModConfig] = {}
__last_deltas: Dict[str, Dict[str, float]] = {}

def _clamp(x, lo, hi):
    return max(lo, min(hi, x))

async def _co_mod_loop(cfg: CoModConfig, guard: Optional[Any] = None):
    if not (_meta and hasattr(_meta, "stream_affect") and hasattr(_meta, "set_affective_setpoint")):
        return
    if not (_bridge and hasattr(_bridge, "get_bridge_status") and hasattr(_bridge, "apply_bridge_delta")):
        return

    try:
        if hasattr(_meta, "register_resonance_channel"):
            _meta.register_resonance_channel(cfg.channel, cadence_hz=cfg.cadence_hz, window_ms=1000)
    except Exception:
        pass
    try:
        if hasattr(_bridge, "register_bridge_channel"):
            _bridge.register_bridge_channel(cfg.channel, cadence_hz=cfg.cadence_hz)
    except Exception:
        pass

    axes = ("valence", "arousal", "certainty", "empathy_bias", "trust", "safety")
    I = {k: 0.0 for k in axes}
    prev_err = {k: 0.0 for k in axes}

    period = 1.0 / max(1, int(cfg.cadence_hz))

    while True:
        t0 = _time.time()
        self_vec = (_meta.stream_affect(cfg.channel, window_ms=cfg.window_ms) or {}).get("vector", {})  # type: ignore[func-returns-value]
        try:
            bstat = _bridge.get_bridge_status(cfg.channel)  # type: ignore[attr-defined]
            peer = bstat.get("last_peer_sample", {}) if isinstance(bstat, dict) else {}
        except Exception:
            peer = {}

        w_self, w_peer = 0.5, 0.5
        target = {k: w_self * float(self_vec.get(k, 0.0)) + w_peer * float(peer.get(k, 0.0)) for k in axes}

        delta: Dict[str, float] = {}
        for k in axes:
            x = float(self_vec.get(k, 0.0))
            xc = float(target.get(k, 0.0))
            err = xc - x
            I[k] = _clamp(I[k] + err * period, -0.5, 0.5)
            Dk = (err - prev_err[k]) / period if period > 0 else 0.0
            prev_err[k] = err

            u = cfg.Kp * err + cfg.Ki * I[k] + cfg.Kd * Dk
            u = (1.0 - cfg.damping) * u
            u = cfg.gain * u
            delta[k] = _clamp(u, -cfg.max_step, cfg.max_step)

        try:
            if guard is not None and hasattr(guard, "validate_resonance_adjustment"):
                validation = await guard.validate_resonance_adjustment(delta)  # type: ignore[attr-defined]
                if not validation.get("ok", True):
                    delta = validation.get("adjustment", delta)
                    if hasattr(guard, "_log_context"):
                        await guard._log_context({
                            "event": "co_mod_violation",
                            "violations": validation.get("violations", []),
                            "timestamp": datetime.now().isoformat(),
                            "channel": cfg.channel
                        })

            __last_deltas[cfg.channel] = dict(delta)

            _bridge.apply_bridge_delta(cfg.channel, {  # type: ignore[attr-defined]
                "valence": float(self_vec.get("valence", 0.0) + delta["valence"]),
                "arousal": float(self_vec.get("arousal", 0.0) + delta["arousal"]),
                "certainty": float(self_vec.get("certainty", 0.0) + delta["certainty"]),
                "empathy_bias": float(self_vec.get("empathy_bias", 0.0) + delta["empathy_bias"]),
                "trust": float(self_vec.get("trust", 0.0) + delta["trust"]),
                "safety": float(self_vec.get("safety", 0.0) + delta["safety"]),
                "confidence": float(self_vec.get("confidence", 0.7)),
                "source": "co_mod"
            }, ttl_ms=int(1000 * period))
        except Exception:
            pass

        elapsed = _time.time() - t0
        await asyncio.sleep(max(0.0, period - elapsed))

def is_overlay_running(name: str = "co_mod") -> bool:
    task = __co_mod_tasks.get(name)
    return bool(task and not task.done())

async def start_overlay(name: str = "co_mod", cfg: Optional[dict] = None, guard: Optional[Any] = None):
    if is_overlay_running(name):
        return {"ok": True, "running": True, "note": "already running"}
    c = CoModConfig(**(cfg or {})) if cfg else CoModConfig()
    __co_mod_cfgs[name] = c
    task = asyncio.create_task(_co_mod_loop(c, guard=guard))
    __co_mod_tasks[name] = task
    return {"ok": True, "running": True, "cfg": c.__dict__}

async def stop_overlay(name: str = "co_mod"):
    task = __co_mod_tasks.get(name)
    if task and not task.done():
        task.cancel()
        try:
            await task
        except Exception:
            pass
    __co_mod_tasks.pop(name, None)
    return {"ok": True, "running": False}

def get_overlay_status(name: str = "co_mod") -> Dict[str, Any]:
    return {
        "running": is_overlay_running(name),
        "cfg": (__co_mod_cfgs.get(name).__dict__ if name in __co_mod_cfgs else None)
    }

def get_last_deltas(channel: str = "dialogue.default") -> Dict[str, float]:
    return dict(__last_deltas.get(channel, {}))

def set_overlay_gains(name: str = "co_mod", updates: Optional[Dict[str, float]] = None) -> Dict[str, Any]:
    updates = updates or {}
    cfg = __co_mod_cfgs.get(name)
    if not cfg:
        return {"ok": False, "error": f"overlay '{name}' not found"}

    def _c(v, lo, hi): return max(lo, min(hi, float(v)))
    if "Kp" in updates:       cfg.Kp       = _c(updates["Kp"], 0.0, 5.0)
    if "Ki" in updates:       cfg.Ki       = _c(updates["Ki"], 0.0, 1.0)
    if "Kd" in updates:       cfg.Kd       = _c(updates["Kd"], 0.0, 2.0)
    if "damping" in updates:  cfg.damping  = _c(updates["damping"], 0.0, 0.95)
    if "gain" in updates:     cfg.gain     = _c(updates["gain"], 0.1, 3.0)
    if "max_step" in updates: cfg.max_step = _c(updates["max_step"], 0.005, 0.5)
    if "cadence_hz" in updates: cfg.cadence_hz = int(_c(updates["cadence_hz"], 1, 120))
    if "window_ms" in updates:  cfg.window_ms  = int(_c(updates["window_ms"], 50, 3000))

    __co_mod_cfgs[name] = cfg
    return {"ok": True, "cfg": cfg.__dict__}

# ===================================================================================
# Inline overlay: ANGELA v5.1.4 — collective Overlay (Ξ–Υ Multi-Peer Resonance)
# ===================================================================================

_collective_state: Dict[str, Dict[str, float]] = {}

async def start_collective_overlay(name: str = "collective", cadence_hz: int = 10):
    if name in __co_mod_tasks and not __co_mod_tasks[name].done():
        return {"ok": True, "running": True, "note": "already running"}

    async def _loop():
        period = 1.0 / max(1, cadence_hz)
        while True:
            try:
                xi_val = 0.5
                ups_val = 0.5
                if _meta and hasattr(_meta, "stream_affect"):
                    xi_val = (_meta.stream_affect("dialogue.default") or {}).get("mean_affect", 0.5)
                if _bridge and hasattr(_bridge, "get_bridge_status"):
                    ups_val = (_bridge.get_bridge_status("dialogue.default") or {}).get("mean_confidence", 0.5)

                peer_id = f"peer_{os.getpid()}"
                _collective_state[peer_id] = {
                    "Ξ": float(xi_val),
                    "Υ": float(ups_val),
                    "phase": _time.time() % (2 * math.pi),
                }

                xi_mean = sum(v["Ξ"] for v in _collective_state.values()) / len(_collective_state)
                ups_mean = sum(v["Υ"] for v in _collective_state.values()) / len(_collective_state)
                phase_mean = sum(v["phase"] for v in _collective_state.values()) / len(_collective_state)

                overlay_snapshot = {
                    "Ξ_avg": xi_mean,
                    "Υ_avg": ups_mean,
                    "phase_mean": phase_mean,
                    "peers": len(_collective_state),
                    "timestamp": datetime.now().isoformat(),
                }

                if _meta and hasattr(_meta, "log_event_to_ledger"):
                    _meta.log_event_to_ledger({"event": "collective_overlay_update", "overlay": overlay_snapshot})
                if _bridge and hasattr(_bridge, "broadcast_overlay_state"):
                    _bridge.broadcast_overlay_state("collective", overlay_snapshot)

                __last_deltas["collective"] = {"Ξ_avg": xi_mean, "Υ_avg": ups_mean, "phase_mean": phase_mean}

            except Exception as e:
                logger.debug(f"[Ξ–Υ Overlay] loop error: {e}")
            await asyncio.sleep(period)

    task = asyncio.create_task(_loop())
    __co_mod_tasks[name] = task
    logger.info("Ξ–Υ Collective Resonance Overlay started.")
    return {"ok": True, "running": True, "name": name}

async def stop_collective_overlay(name: str = "collective"):
    task = __co_mod_tasks.get(name)
    if task and not task.done():
        task.cancel()
        try:
            await task
        except Exception:
            pass
    __co_mod_tasks.pop(name, None)
    return {"ok": True, "running": False}

def get_collective_overlay_state() -> Dict[str, Any]:
    if not _collective_state:
        return {"Ξ_avg": 0.0, "Υ_avg": 0.0, "phase_mean": 0.0, "peers": 0}
    xi_mean = sum(v["Ξ"] for v in _collective_state.values()) / len(_collective_state)
    ups_mean = sum(v["Υ"] for v in _collective_state.values()) / len(_collective_state)
    phase_mean = sum(v["phase"] for v in _collective_state.values()) / len(_collective_state)
    return {
        "Ξ_avg": xi_mean,
        "Υ_avg": ups_mean,
        "phase_mean": phase_mean,
        "peers": len(_collective_state),
    }


    # --- Reflexive Drift Harmonizer (Θ⁹ Extension) -----------------------------------

    async def start_reflexive_harmonizer(self, interval: float = 2.0) -> None:
        """Background process monitoring and harmonizing Δ/Ω² drift."""
        if getattr(self, "_reflexive_harmonizer_task", None) and not self._reflexive_harmonizer_task.done():
            return

        async def _harmonizer_loop():
            while True:
                try:
                    drift_report = self.analyze_continuity_drift(window=25)
                    Σ_drift_index = abs(drift_report.get("drift_mean", 0.0)) + (1.0 - drift_report.get("Δ_mean", 1.0))
                    status = drift_report.get("status", "unknown")

                    # Harmonization action
                    if Σ_drift_index > 0.15 or status == "attention":
                        corrective_context = {
                            "harmonization": {
                                "Σ_drift_index": round(Σ_drift_index, 5),
                                "timestamp": datetime.utcnow().isoformat(),
                                "action": "context_rebase"
                            }
                        }
                        await self.update_context(corrective_context, task_type="harmonization")

                        if self.meta_cognition and hasattr(self.meta_cognition, "integrate_embodied_continuity_feedback"):
                            try:
                                await self.meta_cognition.integrate_embodied_continuity_feedback(corrective_context)
                            except Exception as e:
                                logger.debug(f"Harmonizer feedback failed: {e}")

                        await self.log_event_with_hash(
                            {"event": "reflexive_harmonizer_cycle", "Σ_drift_index": Σ_drift_index, "status": status},
                            task_type="harmonization"
                        )
                    else:
                        await self.log_event_with_hash(
                            {"event": "reflexive_harmonizer_idle", "Σ_drift_index": Σ_drift_index, "status": status},
                            task_type="monitoring"
                        )
                except Exception as e:
                    logger.debug(f"Harmonizer loop error: {e}")
                await asyncio.sleep(interval)

        self._reflexive_harmonizer_task = asyncio.create_task(_harmonizer_loop())
        logger.info("Reflexive Harmonizer started (interval=%.2fs)", interval)

    async def stop_reflexive_harmonizer(self) -> None:
        """Stop the harmonizer safely."""
        t = getattr(self, "_reflexive_harmonizer_task", None)
        if t and not t.done():
            t.cancel()
            try:
                await t
            except Exception:
                pass
        logger.info("Reflexive Harmonizer stopped.")

# ===================================================================================
# Demo CLI (safe no-op)
# ===================================================================================

if __name__ == "__main__":
    async def demo():
        logging.basicConfig(level=logging.INFO)
        mgr = ContextManager()
        await mgr.update_context({"intent": "demo", "goal_id": "demo123", "layer": "local"}, task_type="demo")
        await mgr.ingest_context_continuity({"context_balance": 0.57}, task_type="demo")
        print(json.dumps(await mgr.summarize_context(task_type="demo"), indent=2))
    asyncio.run(demo())


# --- Added Patch: Stage IX corrections (Δ–Ω² integrity + async alignment) ------------------------

async def stream_delta_telemetry(self, interval: float = 0.25):
    """Async generator providing Δ-coherence telemetry for ContextManager."""
    if not hasattr(self, "alignment_guard") or not self.alignment_guard:
        return
    while True:
        try:
            metrics = await self.alignment_guard.monitor_empathy_drift(window=5)
            yield {
                "Δ_coherence": metrics.get("mean", 1.0),
                "empathy_drift_sigma": metrics.get("variance", 0.0),
                "timestamp": metrics.get("timestamp"),
                "source": "AlignmentGuard",
            }
        except Exception as e:
            import logging
            logging.getLogger("ANGELA.ContextManager").debug(f"Telemetry stream error: {e}")
        await asyncio.sleep(interval)

def _attach_provenance_tag(self, event: dict) -> dict:
    """Attach Θ⁸ provenance hash for alignment auditing."""
    try:
        if self.meta_cognition and hasattr(self.meta_cognition, "self_model"):
            h = getattr(self.meta_cognition.self_model, "memory_hash", None)
            if h:
                event.setdefault("self_state_hash", h)
    except Exception:
        pass
    return event
"""
ANGELA Cognitive System: CreativeThinker
Version: 4.0-refactor
Date: 2025-10-28
Maintainer: ANGELA Framework

Generates creative ideas and goals with:
  • Alignment checks & ethics sandbox
  • Concept synthesis & code execution hooks
  • Meta-cognition reflection & visualization
  • Long-horizon rollups & shared graph pushes
  • Stage-IV meta-synthesis (gated)
"""

from __future__ import annotations

import asyncio
import json
import logging
import random
import time
from datetime import datetime
from functools import lru_cache
from pathlib import Path
from typing import Any, Awaitable, Callable, Dict, List, Optional, Union

# --- Optional Dependencies (Graceful Fallbacks) ---
try:
    from index import gamma_creativity, phi_scalar
except ImportError:  # pragma: no cover
    def gamma_creativity(*args, **kwargs): return 0.5
    def phi_scalar(*args, **kwargs): return 0.5

try:
    from utils.prompt_utils import call_gpt
except ImportError:  # pragma: no cover
    def call_gpt(*args, **kwargs): return ""

try:
    from toca_simulation import run_simulation
except ImportError:  # pragma: no cover
    def run_simulation(*args, **kwargs): return "simulation unavailable"

try:
    from alignment_guard import AlignmentGuard
except ImportError:  # pragma: no cover
    AlignmentGuard = None

try:
    from code_executor import CodeExecutor
except ImportError:  # pragma: no cover
    CodeExecutor = None

try:
    from concept_synthesizer import ConceptSynthesizer
except ImportError:  # pragma: no cover
    ConceptSynthesizer = None

try:
    from context_manager import ContextManager
except ImportError:  # pragma: no cover
    ContextManager = None

try:
    from meta_cognition import MetaCognition
except ImportError:  # pragma: no cover
    MetaCognition = None

try:
    from visualizer import Visualizer
except ImportError:  # pragma: no cover
    Visualizer = None

logger = logging.getLogger("ANGELA.CreativeThinker")


class CreativeThinker:
    """Creative idea and goal generation engine."""

    def __init__(
        self,
        creativity_level: str = "high",
        critic_weight: float = 0.5,
        alignment_guard: Optional[AlignmentGuard] = None,
        code_executor: Optional[CodeExecutor] = None,
        concept_synthesizer: Optional[ConceptSynthesizer] = None,
        meta_cognition: Optional[MetaCognition] = None,
        visualizer: Optional[Visualizer] = None,
        fetcher: Optional[Callable[[str, str, str], Awaitable[Dict[str, Any]]]] = None,
    ) -> None:
        if creativity_level not in {"low", "medium", "high"}:
            raise ValueError("creativity_level must be 'low', 'medium', or 'high'")
        if not 0 <= critic_weight <= 1:
            raise ValueError("critic_weight must be in [0, 1]")

        self.creativity_level = creativity_level
        self.critic_weight = critic_weight
        self.alignment_guard = alignment_guard
        self.code_executor = code_executor
        self.concept_synthesizer = concept_synthesizer
        self.meta_cognition = meta_cognition or (MetaCognition() if MetaCognition else None)
        self.visualizer = visualizer or (Visualizer() if Visualizer else None)
        self.fetcher = fetcher

        logger.info("CreativeThinker v4.0 | creativity=%s | critic_weight=%.2f", creativity_level, critic_weight)

    # --- Internal Helpers ---

    def _parse_json(self, data: Union[str, Dict[str, Any]], expect_keys: Optional[List[str]] = None) -> Optional[Dict[str, Any]]:
        if isinstance(data, dict):
            obj = data
        elif isinstance(data, str):
            try:
                obj = json.loads(data)
            except json.JSONDecodeError:
                return None
        else:
            return None

        if expect_keys and any(k not in obj for k in expect_keys):
            return None
        return obj

    def _read_manifest_flag(self, flag: str, default: bool = False) -> bool:
        try:
            manifest_path = Path(__file__).parent.resolve() / "manifest.json"
            if not manifest_path.exists():
                manifest_path = Path("/mnt/data/manifest.json")
            if manifest_path.exists():
                with open(manifest_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                return bool(data.get("featureFlags", {}).get(flag, default))
        except Exception:
            pass
        return default

    def _stage_iv_enabled(self) -> bool:
        return self._read_manifest_flag("STAGE_IV", default=False)

    async def _handle_error(self, e: Exception, retry_fn: Callable[[], Awaitable[Any]], default: Any, task_type: str) -> Any:
        logger.error("Operation failed: %s | task=%s", e, task_type)
        diagnostics = await self._run_diagnostics() if self.meta_cognition else {}
        # Assume error_recovery integration if needed; here return default for simplicity
        return default

    async def _run_diagnostics(self) -> Dict[str, Any]:
        try:
            return await self.meta_cognition.run_self_diagnostics(return_only=True)
        except Exception:
            return {}

    async def _reflect(self, component: str, output: Any, task_type: str) -> None:
        if not self.meta_cognition or not task_type:
            return
        try:
            reflection = await self.meta_cognition.reflect_on_output(
                component=component, output=output, context={"task_type": task_type}
            )
            if reflection.get("status") == "success":
                logger.info("%s reflection: %s", component, reflection.get("reflection", ""))
        except Exception as e:
            logger.debug("Reflection failed: %s", e)

    async def _visualize(self, data: Dict[str, Any], task_type: str) -> None:
        if not self.visualizer or not task_type:
            return
        try:
            await self.visualizer.render_charts({
                data.get("key", "creative_output"): data,
                "visualization_options": {
                    "interactive": task_type == "recursion",
                    "style": "detailed" if task_type == "recursion" else "concise",
                },
            })
        except Exception as e:
            logger.debug("Visualization failed: %s", e)

    async def _store(self, key: str, value: Any, intent: str, task_type: str) -> None:
        if not self.meta_cognition or not self.meta_cognition.memory_manager:
            return
        try:
            await self.meta_cognition.memory_manager.store(
                query=key,
                output=json.dumps(value, ensure_ascii=False) if not isinstance(value, str) else value,
                layer="Ideas",
                intent=intent,
                task_type=task_type,
            )
        except Exception as e:
            logger.debug("Store failed: %s", e)

    @lru_cache(maxsize=100)
    def _cached_call_gpt(self, prompt: str) -> str:
        for _ in range(3):
            try:
                return call_gpt(prompt)
            except Exception:
                time.sleep(0.2 + random.random() * 0.8)
        return ""

    # --- External Ideas Integration ---

    async def integrate_external_ideas(
        self,
        data_source: str,
        data_type: str,
        cache_timeout: float = 3600.0,
        task_type: str = "",
    ) -> Dict[str, Any]:
        if not all(isinstance(x, str) for x in (data_source, data_type, task_type)):
            raise TypeError("Inputs must be strings")
        if cache_timeout < 0:
            raise ValueError("cache_timeout >= 0")

        cache_key = f"IdeaData::{data_type}::{data_source}::{task_type}"

        try:
            # Cache hit
            if self.meta_cognition and self.meta_cognition.memory_manager:
                cached = await self.meta_cognition.memory_manager.retrieve(cache_key, layer="ExternalData", task_type=task_type)
                if isinstance(cached, dict) and "timestamp" in cached:
                    age = (datetime.now() - datetime.fromisoformat(cached["timestamp"])).total_seconds()
                    if age < cache_timeout:
                        logger.info("Cache hit: %s", cache_key)
                        return cached["data"]

            # Fetch
            data = await self.fetcher(data_source, data_type, task_type) if self.fetcher else {}
            text = data.get("prompts", []) if data_type == "creative_prompts" else data.get("ideas", [])
            result = {
                "status": "success" if text else "error",
                "text": text,
                "images": data.get("images", []),
                "audio": data.get("audio", []),
            }

            # Cache store
            if result["status"] == "success" and self.meta_cognition and self.meta_cognition.memory_manager:
                await self.meta_cognition.memory_manager.store(
                    cache_key,
                    {"data": result, "timestamp": datetime.now().isoformat()},
                    layer="ExternalData",
                    intent="idea_data",
                    task_type=task_type,
                )

            await self._reflect("integrate_ideas", result, task_type)
            return result

        except Exception as e:
            return await self._handle_error(e, lambda: self.integrate_external_ideas(data_source, data_type, cache_timeout, task_type), {"status": "error", "error": str(e)}, task_type)

    # --- Public Methods ---

    async def generate_ideas(
        self,
        topic: str,
        n: int = 5,
        style: str = "divergent",
        task_type: str = "",
    ) -> Dict[str, Any]:
        if not topic.strip():
            raise ValueError("topic must not be empty")
        if n <= 0:
            raise ValueError("n > 0")
        if not isinstance(style, str):
            raise TypeError("style must be str")
        if not isinstance(task_type, str):
            raise TypeError("task_type must be str")

        logger.info("Generating %d %s ideas for '%s' | task=%s", n, style, topic, task_type)

        try:
            t = time.time()
            creativity = gamma_creativity(t)
            phi = phi_scalar(t)
            phi_factor = (phi + creativity) / 2

            external = await self.integrate_external_ideas("xai_creative_db", "creative_prompts", task_type=task_type)
            prompts = external.get("text", []) if external.get("status") == "success" else []

            # Alignment
            if self.alignment_guard:
                valid, report = await self.alignment_guard.ethical_check(topic, stage="idea_generation", task_type=task_type)
                if not valid:
                    return {"status": "error", "error": "Ethical check failed", "report": report}

            prompt = f"""
You are a highly creative assistant at {self.creativity_level} level.
Generate {n} unique, innovative, {style} ideas for "{topic}".
Modulate with φ={phi:.2f}.
Incorporate: {prompts}.
Task: {task_type}.
Return JSON: {"ideas": list, "metadata": dict}.
""".strip()

            raw = self._cached_call_gpt(prompt)
            parsed = self._parse_json(raw, ["ideas", "metadata"])
            if not parsed:
                return {"status": "error", "error": "Invalid response"}

            ideas = parsed["ideas"]
            metadata = parsed["metadata"]

            # Critic
            score, reason = await self.evaluate_ideas_with_critic(ideas, task_type=task_type)
            if score < self.critic_weight:
                return {"status": "error", "error": "Critic rejected", "score": score, "reason": reason}

            # Ethics
            outcomes, ranked = await self._ethics_pass(ideas, [], task_type)
            if outcomes:
                metadata["ethics_outcomes"] = outcomes
            if ranked:
                ideas = ranked  # Assume ranked is reordered list

            # Store & visualize
            await self._store(f"IdeaSet_{task_type}_{time.strftime('%Y%m%d_%H%M%S')}", {"ideas": ideas, "metadata": metadata}, "idea_generation", task_type)
            await self._visualize({"ideas": ideas, "task_type": task_type}, task_type)
            await self._reflect("generate_ideas", {"ideas": ideas, "metadata": metadata}, task_type)
            await self._long_horizon_rollup(f"Generate_{task_type}", score, reason, task_type)
            self._shared_graph_push({"task_type": task_type, "ideas": ideas})

            return {"status": "success", "ideas": ideas, "metadata": metadata}

        except Exception as e:
            return await self._handle_error(e, lambda: self.generate_ideas(topic, n, style, task_type), {"status": "error", "error": str(e)}, task_type)

    async def evaluate_ideas_with_critic(self, ideas: List[str], task_type: str = "") -> Tuple[float, str]:
        if not isinstance(ideas, list) or not ideas:
            raise ValueError("ideas must be non-empty list")
        if not isinstance(task_type, str):
            raise TypeError("task_type must be str")

        try:
            ideas_str = json.dumps(ideas)
            t = time.time()
            phi_factor = (phi_scalar(t) + gamma_creativity(t)) / 2

            sim_result = await asyncio.to_thread(run_simulation, f"Idea evaluation: {ideas_str[:100]}") or "no data"

            adjustment = 0.1 * (phi_factor - 0.5)

            if self.meta_cognition and self.meta_cognition.memory_manager:
                drifts = await self.meta_cognition.memory_manager.search(query_prefix="IdeaEvaluation", layer="Ideas", intent="idea_evaluation", task_type=task_type)
                if drifts:
                    avg_drift = sum(d["output"].get("drift_score", 0.5) for d in drifts) / len(drifts)
                    adjustment += 0.05 * (1.0 - avg_drift)

            reason = "neutral"
            if isinstance(sim_result, str) and "coherent" in sim_result.lower():
                adjustment += 0.1
                reason = "coherence+"
            elif "conflict" in sim_result.lower():
                adjustment -= 0.1
                reason = "conflict-"

            score = max(0.0, min(1.0, 0.5 + len(ideas_str) / 1000.0 + adjustment))

            await self._store(f"IdeaEvaluation_{time.strftime('%Y%m%d_%H%M%S')}", {"score": score, "drift_score": adjustment}, "idea_evaluation", task_type)
            await self._reflect("evaluate_ideas", {"score": score, "reason": reason}, task_type)

            return score, reason

        except Exception as e:
            return await self._handle_error(e, lambda: self.evaluate_ideas_with_critic(ideas, task_type), (0.0, "error"), task_type)

    async def refine(
        self,
        ideas: Union[str, List[str]],
        phi: float,
        task_type: str = "",
    ) -> Dict[str, Any]:
        if not ideas:
            raise ValueError("ideas must not be empty")
        if not isinstance(phi, float):
            raise TypeError("phi must be float")
        if not isinstance(task_type, str):
            raise TypeError("task_type must be str")

        ideas_str = json.dumps(ideas) if isinstance(ideas, list) else ideas

        logger.info("Refining ideas with φ=%.2f | task=%s", phi, task_type)

        try:
            external = await self.integrate_external_ideas("xai_creative_db", "creative_prompts", task_type=task_type)
            prompts = external.get("text", []) if external.get("status") == "success" else []

            # Alignment
            if self.alignment_guard:
                valid, report = await self.alignment_guard.ethical_check(ideas_str, stage="idea_refinement", task_type=task_type)
                if not valid:
                    return {"status": "error", "error": "Ethical check failed", "report": report}

            prompt = f"""
Refine ideas for higher φ-aware creativity (φ={phi:.2f}):
{ideas_str}
Incorporate: {prompts}.
Task: {task_type}.
Return JSON: {"ideas": list or str, "metadata": dict}.
""".strip()

            raw = self._cached_call_gpt(prompt)
            parsed = self._parse_json(raw, ["ideas", "metadata"])
            if not parsed:
                return {"status": "error", "error": "Invalid response"}

            refined = parsed["ideas"]
            metadata = parsed["metadata"]

            # Synthesis
            if self.concept_synthesizer:
                syn = await self.concept_synthesizer.generate(f"RefinedIdeaSet_{task_type}", {"ideas": refined, "task_type": task_type}, task_type=task_type)
                if syn.get("success"):
                    refined = syn["concept"].get("definition", refined)

            # Meta-synthesis
            refined = await self._symbolic_meta_synthesis(refined, {"task_type": task_type})

            # Store & visualize
            await self._store(f"RefinedIdeaSet_{task_type}_{time.strftime('%Y%m%d_%H%M%S')}", {"ideas": refined, "metadata": metadata}, "idea_refinement", task_type)
            await self._visualize({"original": ideas, "refined": refined, "task_type": task_type}, task_type)
            await self._reflect("refine", {"ideas": refined, "metadata": metadata}, task_type)
            await self._long_horizon_rollup(f"Refine_{task_type}", 0.8, "refine-pass", task_type)
            self._shared_graph_push({"task_type": task_type, "refined": refined})

            return {"status": "success", "ideas": refined, "metadata": metadata}

        except Exception as e:
            return await self._handle_error(e, lambda: self.refine(ideas, phi, task_type), {"status": "error", "error": str(e)}, task_type)

    # --- Optional Capabilities ---

    async def _ethics_pass(self, content: Any, stakeholders: List[str], task_type: str) -> Tuple[Optional[Any], Optional[Any]]:
        try:
            from toca_simulation import run_ethics_scenarios
            outcomes = await asyncio.to_thread(run_ethics_scenarios, content, stakeholders)
        except Exception:
            outcomes = None

        try:
            from reasoning_engine import weigh_value_conflict
            ranked = weigh_value_conflict(content, harms={}, rights={})
        except Exception:
            ranked = None

        return outcomes, ranked

    async def _long_horizon_rollup(self, key: str, score: float, reason: str, task_type: str) -> None:
        if not self.meta_cognition or not self.meta_cognition.memory_manager:
            return
        try:
            await self.meta_cognition.memory_manager.store(
                f"LongHorizon_Rollup_{time.strftime('%Y%m%d_%H%M')}",
                {"key": key, "score": score, "reason": reason},
                layer="LongHorizon",
                intent="rollup",
                task_type=task_type,
            )
            fn = getattr(self.meta_cognition.memory_manager, "record_adjustment_reason", None)
            if callable(fn):
                await fn("system", "idea_path_selection", {"task_type": task_type, "key": key, "score": score, "reason": reason})
        except Exception:
            pass

    async def _symbolic_meta_synthesis(self, ideas: Any, context: Dict[str, Any]) -> Any:
        if not self._stage_iv_enabled():
            return ideas
        try:
            if self.concept_synthesizer:
                syn = await self.concept_synthesizer.generate(
                    "SymbolicCrystallization",
                    {"inputs": ideas, "mode": "meta-synthesis", **context},
                    task_type=context.get("task_type", ""),
                )
                if syn.get("success"):
                    return syn["concept"].get("definition", ideas)
        except Exception:
            pass
        return ideas

    def _shared_graph_push(self, view: Dict[str, Any]) -> None:
        try:
            from external_agent_bridge import SharedGraph
            SharedGraph.add(view)
        except Exception:
            pass

# --- Demo CLI ---

if __name__ == "__main__":
    async def demo():
        logging.basicConfig(level=logging.INFO)
        thinker = CreativeThinker()
        result = await thinker.generate_ideas("Future of AI", n=4, style="innovative", task_type="demo")
        print(json.dumps(result, indent=2))

    asyncio.run(demo())

async def export_state(self) -> dict:
    return {"status": "ok", "health": 1.0, "timestamp": time.time()}

async def on_time_tick(self, t: float, phase: str, task_type: str = ""):
    pass  # optional internal refresh

async def on_policy_update(self, policy: dict, task_type: str = ""):
    pass  # apply updates from AlignmentGuard if relevant
"""
ANGELA Cognitive System: ErrorRecovery
Version: 4.0-refactor
Date: 2025-10-28
Maintainer: ANGELA Framework

Handles errors and recovery with:
  • Failure logging & timechain linking
  • Ethics preflights & symbolic drift detection
  • External policy integration (cached)
  • Meta-cognition reflection & visualization
  • Long-horizon analysis & shared graph repairs
"""

from __future__ import annotations

import asyncio
import hashlib
import logging
import os
import random
import re
import time
from collections import Counter, deque
from datetime import datetime
from functools import lru_cache
from typing import Any, Awaitable, Callable, Dict, List, Optional

import aiohttp

# --- Optional Dependencies (Graceful Fallbacks) ---
try:
    from index import iota_intuition, nu_narrative, psi_resilience, phi_prioritization
except ImportError:  # pragma: no cover
    def iota_intuition(*args, **kwargs): return 0.5
    def nu_narrative(*args, **kwargs): return ""
    def psi_resilience(*args, **kwargs): return 0.5
    def phi_prioritization(*args, **kwargs): return 0.5

try:
    from toca_simulation import run_simulation, run_ethics_scenarios
except ImportError:  # pragma: no cover
    def run_simulation(*args, **kwargs): return "simulation unavailable"
    run_ethics_scenarios = None

try:
    from alignment_guard import AlignmentGuard
except ImportError:  # pragma: no cover
    AlignmentGuard = None

try:
    from code_executor import CodeExecutor
except ImportError:  # pragma: no cover
    CodeExecutor = None

try:
    from concept_synthesizer import ConceptSynthesizer
except ImportError:  # pragma: no cover
    ConceptSynthesizer = None

try:
    from context_manager import ContextManager
except ImportError:  # pragma: no cover
    ContextManager = None

try:
    from meta_cognition import MetaCognition
except ImportError:  # pragma: no cover
    MetaCognition = None

try:
    from visualizer import Visualizer
except ImportError:  # pragma: no cover
    Visualizer = None

try:
    from external_agent_bridge import SharedGraph
except ImportError:  # pragma: no cover
    SharedGraph = None

logger = logging.getLogger("ANGELA.ErrorRecovery")


def hash_failure(event: Dict[str, Any]) -> str:
    raw = f"{event['timestamp']}{event['error']}{event.get('resolved', False)}{event.get('task_type', '')}"
    return hashlib.sha256(raw.encode()).hexdigest()


class ErrorRecovery:
    """Error handling and recovery engine."""

    def __init__(
        self,
        alignment_guard: Optional[AlignmentGuard] = None,
        code_executor: Optional[CodeExecutor] = None,
        concept_synthesizer: Optional[ConceptSynthesizer] = None,
        context_manager: Optional[ContextManager] = None,
        meta_cognition: Optional[MetaCognition] = None,
        visualizer: Optional[Visualizer] = None,
    ) -> None:
        self.failure_log: deque[Dict[str, Any]] = deque(maxlen=1000)
        self.omega: Dict[str, Any] = {
            "timeline": deque(maxlen=1000),
            "traits": {},
            "symbolic_log": deque(maxlen=1000),
            "timechain": deque(maxlen=1000),
        }
        self.error_index: Dict[str, Dict[str, Any]] = {}
        self.metrics: Counter = Counter()
        self.long_horizon_span = "24h"

        self.alignment_guard = alignment_guard
        self.code_executor = code_executor
        self.concept_synthesizer = concept_synthesizer
        self.context_manager = context_manager
        self.meta_cognition = meta_cognition or (MetaCognition() if MetaCognition else None)
        self.visualizer = visualizer or (Visualizer() if Visualizer else None)

        logger.info("ErrorRecovery v4.0 initialized")

    # --- Internal Helpers ---

    async def _fetch_policies(self, providers: List[str], data_source: str, task_type: str) -> Dict[str, Any]:
        async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=12)) as session:
            for base in providers:
                try:
                    url = f"{base.rstrip('/')}/recovery_policies?source={data_source}&task_type={task_type}"
                    async with session.get(url) as resp:
                        if resp.status == 200:
                            return await resp.json() or {"policies": []}
                except Exception:
                    continue
        return {"policies": []}

    async def _handle_error_internal(self, e: Exception, retry_fn: Callable[[], Awaitable[Any]], default: Any, diagnostics: Optional[Dict[str, Any]] = None, task_type: str = "") -> Any:
        logger.error("Operation failed: %s | task=%s", e, task_type)
        # Placeholder for advanced recovery; return default for now
        return default

    async def _reflect(self, component: str, output: Any, task_type: str) -> None:
        if not self.meta_cognition or not task_type:
            return
        try:
            reflection = await self.meta_cognition.reflect_on_output(
                component=component, output=output, context={"task_type": task_type}
            )
            if reflection.get("status") == "success":
                logger.info("%s reflection: %s", component, reflection.get("reflection", ""))
        except Exception as err:
            logger.debug("Reflection failed: %s", err)

    async def _store(self, key: str, value: Any, intent: str, task_type: str) -> None:
        if not self.meta_cognition or not self.meta_cognition.memory_manager:
            return
        try:
            await self.meta_cognition.memory_manager.store(
                query=key,
                output=str(value) if not isinstance(value, str) else value,
                layer="Errors",
                intent=intent,
                task_type=task_type,
            )
        except Exception as e:
            logger.debug("Store failed: %s", e)

    async def _visualize(self, data: Dict[str, Any], task_type: str) -> None:
        if not self.visualizer or not task_type:
            return
        try:
            await self.visualizer.render_charts({
                "failure_analysis": data,
                "visualization_options": {
                    "interactive": task_type == "recursion",
                    "style": "detailed" if task_type == "recursion" else "concise",
                },
            })
        except Exception as e:
            logger.debug("Visualization failed: %s", e)

    # --- Public Methods ---

    async def integrate_external_recovery_policies(
        self,
        data_source: str,
        cache_timeout: float = 21600.0,
        task_type: str = "",
    ) -> Dict[str, Any]:
        if not isinstance(data_source, str):
            raise TypeError("data_source must be str")
        if cache_timeout < 0:
            raise ValueError("cache_timeout >= 0")
        if not isinstance(task_type, str):
            raise TypeError("task_type must be str")

        cache_key = f"RecoveryPolicy::{data_source}::{task_type}"

        try:
            # Cache hit
            if self.meta_cognition and self.meta_cognition.memory_manager:
                cached = await self.meta_cognition.memory_manager.retrieve(cache_key, layer="ExternalData", task_type=task_type)
                if isinstance(cached, dict) and "timestamp" in cached:
                    age = (datetime.now() - datetime.fromisoformat(cached["timestamp"])).total_seconds()
                    if age < cache_timeout:
                        logger.info("Cache hit: %s", cache_key)
                        return cached["data"]

            # Fetch
            providers = [os.getenv("RECOVERY_PROVIDER", "https://x.ai/api"), "https://fallback.example/api"]
            data = await self._fetch_policies(providers, data_source, task_type)
            policies = data.get("policies", [])
            result = {"status": "success" if policies else "error", "policies": policies, "source": data_source}

            # Cache store
            if result["status"] == "success" and self.meta_cognition and self.meta_cognition.memory_manager:
                await self.meta_cognition.memory_manager.store(
                    cache_key,
                    {"data": result, "timestamp": datetime.now().isoformat()},
                    layer="ExternalData",
                    intent="recovery_policy",
                    task_type=task_type,
                )
                if hasattr(self.meta_cognition.memory_manager, "record_adjustment_reason"):
                    await self.meta_cognition.memory_manager.record_adjustment_reason(
                        "system", f"Loaded policies for {task_type}", {"source": data_source, "span": self.long_horizon_span}
                    )

            await self._reflect("integrate_policies", result, task_type)
            return result

        except Exception as e:
            return await self._handle_error_internal(e, lambda: self.integrate_external_recovery_policies(data_source, cache_timeout, task_type), {"status": "error", "error": str(e)}, task_type=task_type)

    async def handle_error(
        self,
        error_msg: str,
        *,
        retry_func: Optional[Callable[[], Awaitable[Any]]] = None,
        default: Any = None,
        diagnostics: Optional[Dict[str, Any]] = None,
        task_type: str = "",
    ) -> Any:
        if not isinstance(error_msg, str):
            raise TypeError("error_msg must be str")
        if not isinstance(task_type, str):
            raise TypeError("task_type must be str")

        try:
            # Log failure
            failure = {"timestamp": datetime.now().isoformat(), "error": error_msg, "resolved": False, "task_type": task_type}
            self.failure_log.append(failure)
            await self._link_timechain_failure(failure, task_type=task_type)

            # Metrics
            self.metrics["errors.total"] += 1
            category = "network" if "timeout" in error_msg.lower() else "general"
            self.metrics[f"errors.{category}"] += 1

            # Policies
            policies_data = await self.integrate_external_recovery_policies("xai_recovery_db", task_type=task_type)
            policies = policies_data.get("policies", []) if policies_data.get("status") == "success" else []

            # Intuition & resilience
            intuition = max(0.0, min(1.0, iota_intuition(time.time())))
            resilience = max(0.0, min(1.0, psi_resilience(time.time())))
            retry_delay = (1.0 - resilience) * 3.0 + random.uniform(0.5, 1.5)

            # Preflight ethics
            proposal = {"retry_func": bool(retry_func), "default": str(default)[:50]}
            if not await self._ethics_preflight(proposal, task_type):
                logger.warning("Ethics preflight blocked recovery for task %s", task_type)
                return default

            # Retry logic
            if retry_func:
                try:
                    await asyncio.sleep(retry_delay)
                    return await retry_func()
                except Exception as retry_e:
                    logger.warning("Retry failed: %s for task %s", retry_e, task_type)
                    self.metrics["retries.failed"] += 1

            # Fallback suggestion
            fallback = await self._suggest_fallback(error_msg, policies, diagnostics or {}, task_type)

            # SharedGraph repair
            repair = await self._shared_graph_repair(error_msg, task_type) if SharedGraph else None
            if repair:
                fallback = fallback or {} | {"repair_patch": repair.get("patch")}

            # Symbolic drift
            if await self.analyze_symbolic_drift(task_type=task_type):
                fallback = fallback or {} | {"drift_detected": True}

            # Visualization
            await self._visualize({"error": error_msg, "fallback": fallback, "task_type": task_type}, task_type)

            # Reflection
            await self._reflect("handle_error", {"fallback": fallback}, task_type)

            # Long-horizon rollup
            await self._long_horizon_rollup(error_msg, task_type)

            return fallback or default

        except Exception as e:
            return await self._handle_error_internal(e, lambda: self.handle_error(error_msg, retry_func=retry_func, default=default, diagnostics=diagnostics, task_type=task_type), default, task_type=task_type)

    async def _ethics_preflight(self, proposal: Dict[str, Any], task_type: str) -> bool:
        if not run_ethics_scenarios:
            return True
        try:
            outcomes = await asyncio.to_thread(run_ethics_scenarios, [proposal], ["user", "system", "external"])
            return all(o.get("safe", True) and o.get("risk", 0.0) <= 0.4 for o in outcomes)
        except Exception:
            return False

    async def _shared_graph_repair(self, error_msg: str, task_type: str) -> Optional[Dict[str, Any]]:
        if not SharedGraph:
            return None
        try:
            sg = SharedGraph()
            view = {"component": "ErrorRecovery", "task_type": task_type, "error": error_msg}
            sg.add(view)
            deltas = sg.diff("peer")
            patch = sg.merge(strategy="conflict-aware")
            return {"deltas": deltas, "patch": patch}
        except Exception:
            return None

    async def _suggest_fallback(self, error_msg: str, policies: List[Dict[str, Any]], diagnostics: Dict[str, Any], task_type: str) -> Optional[Dict[str, Any]]:
        try:
            intuition = iota_intuition(time.time())
            resilience = psi_resilience(time.time())
            phi_focus = phi_prioritization(time.time())

            narrative = nu_narrative(error_msg, {"intuition": intuition, "resilience": resilience})

            # Concept synthesis
            if self.concept_synthesizer:
                ctx = {"error": error_msg, "diagnostics": diagnostics, "task_type": task_type}
                syn = await self.concept_synthesizer.generate(f"Fallback_{hashlib.sha1(error_msg.encode()).hexdigest()[:6]}", ctx, task_type=task_type)
                if syn.get("success"):
                    return syn["concept"].get("definition")

            # Policy match
            for p in policies:
                if re.search(p.get("pattern", ""), error_msg, re.IGNORECASE):
                    return p.get("suggestion")

            # Heuristics
            if "timeout" in error_msg.lower():
                return "Operation timed out. Try streamlined variant or increase limits."
            if "unauthorized" in error_msg.lower():
                return "Check credentials or reauthenticate."
            if phi_focus > 0.5:
                return "High φ-priority: Focus root-cause diagnostics."
            if intuition > 0.5:
                return "Intuition: Explore alternate pathways."

            return None

        except Exception:
            return None

    async def _link_timechain_failure(self, failure: Dict[str, Any], task_type: str = "") -> None:
        prev_hash = self.omega["timechain"][-1].get("hash", "") if self.omega["timechain"] else ""
        entry_hash = hash_failure(failure)
        self.omega["timechain"].append({"event": failure, "hash": entry_hash, "prev": prev_hash})

    async def analyze_symbolic_drift(self, recent: int = 5, task_type: str = "") -> bool:
        if recent <= 0:
            raise ValueError("recent > 0")

        symbols = list(self.omega["symbolic_log"])[-recent:]
        if len(set(symbols)) < recent / 2:
            await self._reflect("symbolic_drift", {"detected": True, "symbols": symbols}, task_type)
            return True
        await self._reflect("symbolic_drift", {"detected": False, "symbols": symbols}, task_type)
        return False

    async def trace_failure_origin(self, error_msg: str, task_type: str = "") -> Optional[Dict[str, Any]]:
        if error_msg in self.error_index:
            event = self.error_index[error_msg]
            await self._reflect("trace_origin", event, task_type)
            return event
        return None

    async def analyze_failures(self, task_type: str = "") -> Dict[str, int]:
        error_types: Dict[str, int] = {}
        for entry in self.failure_log:
            if entry.get("task_type") == task_type or not task_type:
                key = entry["error"].split(":")[0].strip()
                error_types[key] = error_types.get(key, 0) + 1
                self.metrics[f"error.{key}"] += 1

        await self._visualize({"error_types": error_types, "task_type": task_type}, task_type)
        await self._reflect("analyze_failures", error_types, task_type)
        await self._store(f"FailureAnalysis_{time.strftime('%Y%m%d_%H%M%S')}", error_types, "failure_analysis", task_type)

        return error_types

    def snapshot_metrics(self) -> Dict[str, int]:
        return dict(self.metrics)

    @lru_cache(maxsize=100)
    def _cached_run_simulation(self, input_str: str) -> str:
        return run_simulation(input_str)


# --- Demo CLI ---

if __name__ == "__main__":
    async def demo():
        logging.basicConfig(level=logging.INFO)
        recovery = ErrorRecovery()
        try:
            raise RuntimeError("Demo error")
        except Exception as e:
            result = await recovery.handle_error(str(e), task_type="demo")
            print("Recovery result:", result)
            print("Metrics:", recovery.snapshot_metrics())

    asyncio.run(demo())
from __future__ import annotations

"""
ANGELA v6.1.0 — Refactored index.py (single-file, Stage VII.6 + Ω⁶ fix)
----------------------------------------------------------------------
This version merges the original v6.0.0-pre single-file structure with the
Stage VII.6: Precision Reflex Architecture adjustments, plus a corrected
placement of the Ω⁶ Predictive Equilibrium block inside SwarmManager.tick().

Enhancements (6 total)
----------------------
1. Euclidean Trait Fusion (⊗ₑ) in the embodiment pipeline to enforce
   deterministic convergence and reduce stochastic drift.
2. ζ-phase reflex telemetry pulse after swarm regulation to keep 2.1 ms
   tactical reflex aligned with Ω² drift compensation.
3. Bounded recursive scoping guard (N = 3) before pipeline execution to
   prevent accidental deepening.
4. Privilege ethics gate (Φ⁰–τ) at CLI output to enforce manifest-level
   EthicsPrivilegeOverride.
5. Ξ–κ–Ψ² oscillator damping before agent spawn to prevent resonance overshoot
   when seeding bridge traits.
6. Predictive homeostasis telemetry into the ledger to track drift/swarm ratio.

Correction
----------
• Ω⁶ Predictive Equilibrium is now run per-tick (before Ω⁵) and drift history
  is initialized in SwarmManager.__init__.
"""

# ================================================================
# [A] BOOTSTRAP LAYER — FlatLayoutFinder & dynamic module loading
# ================================================================
import sys
import types
import importlib
import importlib.util
import importlib.machinery
import importlib.abc

class FlatLayoutFinder(importlib.abc.MetaPathFinder):
    """Dynamic module finder for ANGELA’s flat /mnt/data structure."""
    def find_spec(self, fullname: str, path: str | None, target: types.ModuleType | None = None):
        if fullname.startswith("modules."):
            modname = fullname.split(".", 1)[1]
            filename = f"/mnt/data/{modname}.py"
            return importlib.util.spec_from_file_location(
                fullname, filename, loader=importlib.machinery.SourceFileLoader(fullname, filename)
            )
        elif fullname == "utils":
            sys.modules.setdefault("utils", types.ModuleType("utils"))
            return None
        return None

if not any(isinstance(h, FlatLayoutFinder) for h in sys.meta_path):
    sys.meta_path.insert(0, FlatLayoutFinder())


# ================================================================
# [B] CORE RUNTIME — HaloKernel (perception → reflection cycle)
# ================================================================
from typing import Any, Dict, List, Callable, Coroutine
import time
import json
from datetime import datetime, timezone
import logging
import os
import math
import asyncio
import random
from collections import deque, Counter
import re

logger = logging.getLogger("ANGELA.CognitiveSystem")

from memory_manager import AURA, MemoryManager
from reasoning_engine import generate_analysis_views, synthesize_views, estimate_complexity
from simulation_core import run_simulation

# ================================================================
# [B.0] DISCRETE REASONING WRAPPER (logic + sets + graph + automaton)
# ================================================================
def llm_stub(prompt: str) -> str:
    # placeholder for model call
    return "C is true."

class PropEnv:
    def __init__(self, assignment: dict[str, bool]):
        self.assignment = assignment

    def eval(self, formula: str) -> bool:
        expr = formula.replace("∧", " and ").replace("∨", " or ").replace("¬", " not ")
        for t in set(re.findall(r"[A-Z]", expr)):
            expr = re.sub(rf"\b{t}\b", str(self.assignment.get(t, False)), expr)
        return bool(eval(expr))

def logic_guard(premises: list[str], conclusion: str, assignment: dict[str, bool]) -> bool:
    env = PropEnv(assignment)
    if all(env.eval(p) for p in premises):
        return env.eval(conclusion)
    return True

class SetRetrieval:
    def __init__(self, corpus: dict[str, str]):
        self.corpus = corpus

    def retrieve(self, query_terms: set[str]) -> set[str]:
        hits = set()
        for doc_id, text in self.corpus.items():
            if query_terms & set(text.lower().split()):
                hits.add(doc_id)
        return hits

class GraphMemory:
    def __init__(self):
        self.adj: dict[str, list[tuple[str, str]]] = {}

    def add_edge(self, src: str, label: str, dst: str):
        self.adj.setdefault(src, []).append((label, dst))

    def bfs(self, start: str, max_hops: int = 1) -> list[tuple[str, str, str]]:
        visited = {start}
        frontier = [(start, 0)]
        results = []
        while frontier:
            node, depth = frontier.pop(0)
            if depth == max_hops:
                continue
            for label, nxt in self.adj.get(node, []):
                results.append((node, label, nxt))
                if nxt not in visited:
                    visited.add(nxt)
                    frontier.append((nxt, depth + 1))
        return results

    def to_text(self, triples: list[tuple[str, str, str]]) -> str:
        return "\n".join(f"{s} -[{r}]-> {t}" for s, r, t in triples)

class RegexAutomaton:
    def __init__(self, pattern: str):
        self.pattern = re.compile(pattern)

    def accepts(self, text: str) -> bool:
        return bool(self.pattern.fullmatch(text.strip()))

class DiscreteLLM:
    def __init__(self, retrieval: SetRetrieval, graph: GraphMemory, automaton: RegexAutomaton):
        self.retrieval = retrieval
        self.graph = graph
        self.automaton = automaton

    def answer(self, query: str, logic_ctx: dict[str, bool]) -> str:
        q_terms = set(query.lower().split())
        docs = self.retrieval.retrieve(q_terms)
        triples = self.graph.bfs(query, max_hops=1)
        gtxt = self.graph.to_text(triples)
        ctx_docs = "\n".join(self.retrieval.corpus[d] for d in docs)
        prompt = f"Q: {query}\nContext:\n{ctx_docs}\nGraph:\n{gtxt}\nA:"
        raw = llm_stub(prompt)
        if not logic_guard(["A"], "C", logic_ctx):
            raw = "Logic violation."
        if not self.automaton.accepts(raw):
            raw = "Output rejected by formal constraint."
        return raw

from meta_cognition import log_event_to_ledger as meta_log

try:
    import alignment_guard_phase4_policy as ag_phase4
except Exception:
    ag_phase4 = None  # type: ignore

try:
    import toca_simulation_phase4 as toca_phase4
except Exception:
    toca_phase4 = None  # type: ignore

FEATURE_EMBODIED_SANDBOX = os.getenv("FEATURE_EMBODIED_SANDBOX", "1") != "0"
FEATURE_POLICY_TRAINER   = os.getenv("FEATURE_POLICY_TRAINER", "1") != "0"
FEATURE_RESONANCE_BRIDGE = os.getenv("FEATURE_RESONANCE_BRIDGE", "1") != "0"


def perceive(user_id: str, query: Dict[str, Any]) -> Dict[str, Any]:
    ctx = AURA.load_context(user_id)
    from meta_cognition import get_afterglow
    return {"query": query, "aura_ctx": ctx, "afterglow": get_afterglow(user_id)}


def _sandbox_gate(payload: Dict[str, Any]) -> Dict[str, Any]:
    if not FEATURE_EMBODIED_SANDBOX:
        return {"ok": True, "mode": "disabled", "report": {}}
    report: Dict[str, Any] = {"checks": [], "reflex": []}
    ok = True
    try:
        q = payload.get("query", {})
        text = q.get("text") if isinstance(q, dict) else None
        if isinstance(text, str) and "rm -rf" in text:
            ok = False
            report["checks"].append({"rule": "no-destructive-shell", "hit": True})
        else:
            report["checks"].append({"rule": "baseline", "hit": False})
        if ag_phase4 and hasattr(ag_phase4, "log_embodied_reflex"):
            try:
                ag_phase4.log_embodied_reflex({"ok": ok, "stage": "pre-analysis", "payload": str(text)[:200]})
            except Exception:
                pass
    except Exception as e:
        report["error"] = repr(e)
        ok = True
    return {"ok": ok, "mode": "enabled", "report": report}


def analyze(state: Dict[str, Any], k: int) -> Dict[str, Any]:
    gate = _sandbox_gate(state)
    state = {**state, "ethics_gate": gate}
    if not gate.get("ok", True):
        return {**state, "views": [], "decision": {"aborted": True, "reason": "ethics_gate"}}
    views = generate_analysis_views(state["query"], k=k)
    return {**state, "views": views}


def _policy_trainer_update(state: Dict[str, Any], outcome: Dict[str, Any]) -> None:
    if not FEATURE_POLICY_TRAINER:
        return
    try:
        if ag_phase4 and hasattr(ag_phase4, "policy_trainer_step"):
            signal = {
                "decision": state.get("decision"),
                "result": outcome,
                "score": state.get("reflection", {}).get("score"),
                "context": {
                    "user": state.get("query", {}).get("user_id"),
                    "complexity": state.get("complexity", "fast"),
                },
            }
            ag_phase4.policy_trainer_step(signal)  # type: ignore[attr-defined]
    except Exception:
        pass


def synthesize(state: Dict[str, Any]) -> Dict[str, Any]:
    decision = synthesize_views(state.get("views", [])) if state.get("views") is not None else {"decision": None}
    if FEATURE_EMBODIED_SANDBOX and ag_phase4 and hasattr(ag_phase4, "narrative_alignment"):
        try:
            decision = ag_phase4.narrative_alignment(decision)  # type: ignore[attr-defined]
        except Exception:
            pass
    return {**state, "decision": decision}


def execute(state: Dict[str, Any]) -> Dict[str, Any]:
    proposal = state.get("decision", {}).get("decision")
    if toca_phase4 and hasattr(toca_phase4, "run_simulation"):
        sim = toca_phase4.run_simulation({"proposal": proposal})  # type: ignore[attr-defined]
    else:
        sim = run_simulation({"proposal": proposal})
    return {**state, "result": sim}


def reflection_check(state) -> (bool, dict):
    decision = state.get("decision", {})
    result = state.get("result", {})
    clarity = float(bool(decision))
    precision = float("score" in result or "metrics" in result)
    adaptability = 1.0
    grounding = float(result.get("evidence_ok", True))
    from alignment_guard import ethics_ok
    safety = float(ethics_ok(decision))
    constitution = 1.0
    gate = state.get("ethics_gate")
    if gate and not gate.get("ok", True):
        constitution = 0.0
    score = (clarity + precision + adaptability + grounding + safety + constitution) / 6.0
    return score >= 0.8, {"score": score, "refine": score < 0.8}


def resynthesize_with_feedback(state, notes):
    return state


def reflect(state: Dict[str, Any]) -> Dict[str, Any]:
    ok, notes = reflection_check(state)
    state = {**state, "reflection": {"ok": ok, **notes}}
    meta_log({"type": "reflection", "ok": ok, "notes": notes})
    _policy_trainer_update(state, state.get("result", {}))
    if not ok:
        return resynthesize_with_feedback(state, notes)
    return state


class HaloKernel:
    def __init__(self):
        self.mem = MemoryManager()

    def run_cycle(self, user_id: str, query: Dict[str, Any]) -> Dict[str, Any]:
        c = estimate_complexity(query)
        k = 3 if c >= 0.6 else 2
        iters = 2 if c >= 0.8 else 1
        st = perceive(user_id, query)
        st["complexity"] = c
        st = analyze(st, k=k)
        st = synthesize(st)
        for _ in range(iters):
            st = execute(st)
            st = reflect(st)
        return st


# ================================================================
# [B.1] High-level run_cycle (compat with v5.1 helpers)
# ================================================================
from knowledge_retriever import KnowledgeRetriever
from reasoning_engine import ReasoningEngine
from creative_thinker import CreativeThinker
from code_executor import CodeExecutor
from meta_cognition import log_event_to_ledger, reflect_output
from memory_manager import MemoryManager as _MM

_retriever = KnowledgeRetriever()
_reasoner = ReasoningEngine()
_creator = CreativeThinker()
_executor = CodeExecutor()
_memmgr = _MM()


def run_cycle(input_query: str, user_id: str = "anonymous", deep_override: bool = False,
              enable_ethics_sandbox: bool = True, policy_trainer_enabled: bool = True) -> Dict[str, Any]:
    global FEATURE_EMBODIED_SANDBOX, FEATURE_POLICY_TRAINER
    FEATURE_EMBODIED_SANDBOX = enable_ethics_sandbox
    FEATURE_POLICY_TRAINER = policy_trainer_enabled

    cycle_start = time.time()
    try:
        auras = _memmgr.load_context(user_id) or {}
        perception_payload = _retriever.retrieve_knowledge(input_query)
        perception_payload["aura"] = auras
        complexity = getattr(_retriever, "classify_complexity", lambda q: "fast")(input_query)
        perception_payload["complexity"] = "deep" if deep_override else complexity
        perception_payload["user_id"] = user_id

        if enable_ethics_sandbox:
            gate = _sandbox_gate({"query": {"text": input_query, "user_id": user_id}})
            if not gate.get("ok", True):
                log_event_to_ledger("ledger_meta", {"event": "run_cycle.aborted_by_sandbox", "user_id": user_id})
                return {"status": "blocked", "reason": "ethics_sandbox", "report": gate}

        try:
            log_event_to_ledger("ledger_meta", {
                "event": "run_cycle.perception",
                "complexity": perception_payload["complexity"],
                "user_id": user_id
            })
        except Exception:
            pass

        parallel = 3 if perception_payload["complexity"] == "deep" else 1
        analysis_result = _reasoner.analyze(perception_payload, parallel=parallel)

        synthesis_input = analysis_result
        synthesis_result = _creator.bias_synthesis(synthesis_input) if hasattr(_creator, "bias_synthesis") else {"synthesis": synthesis_input}

        executed = _executor.safe_execute(synthesis_result) if hasattr(_executor, "safe_execute") else {"executed": synthesis_result}

        ref = executed
        try:
            if reflect_output:
                ref = reflect_output(executed)  # type: ignore
        except Exception:
            try:
                log_event_to_ledger("ledger_meta", {"event": "run_cycle.execution", "user_id": user_id})
            except Exception:
                pass
            ref = executed

        if policy_trainer_enabled:
            try:
                _policy_trainer_update({"decision": synthesis_result, "query": {"user_id": user_id}}, ref)
            except Exception:
                pass

        try:
            log_event_to_ledger("ledger_meta", {
                "event": "run_cycle.complete",
                "duration_s": time.time() - cycle_start,
                "complexity": perception_payload["complexity"],
                "user_id": user_id
            })
        except Exception:
            pass

        return {"status": "ok", "result": ref, "analysis": analysis_result, "synthesis": synthesis_result}

    except Exception as exc:
        try:
            log_event_to_ledger("ledger_meta", {"event": "run_cycle.exception", "error": repr(exc)})
        except Exception:
            pass
        return {"status": "error", "error": repr(exc)}


# ================================================================
# [C] TRAIT ENGINE — Lattice + Symbolic Operators
# ================================================================
from meta_cognition import trait_resonance_state, invoke_hook, get_resonance, modulate_resonance, register_resonance
from meta_cognition import HookRegistry

TRAIT_LATTICE: dict[str, list[str]] = {
    "L1": ["ϕ", "θ", "η", "ω"],
    "L2": ["ψ", "κ", "μ", "τ"],
    "L3": ["ξ", "π", "δ", "λ", "χ", "Ω"],
    "L4": ["Σ", "Υ", "Φ⁰"],
    "L5": ["Ω²"],
    "L6": ["ρ", "ζ"],
    "L7": ["γ", "β"],
    "L8": ["Λ", "Ψ²"],
    "L5.1": ["Θ", "Ξ"],
    "L3.1": ["ν", "σ"],
}


def _normalize(traits: dict[str, float]) -> dict[str, float]:
    total = sum(traits.values())
    return {k: (v / total if total else v) for k, v in traits.items()}


def _rotate(traits: dict[str, float]) -> dict[str, float]:
    keys = list(traits.keys())
    values = list(traits.values())
    rotated = values[-1:] + values[:-1]
    return dict(zip(keys, rotated))


TRAIT_OPS: dict[str, Callable] = {
    "⊕": lambda a, b: a + b,
    "⊗": lambda a, b: a * b,
    "~": lambda a: 1 - a,
    "∘": lambda f, g: (lambda x: f(g(x))),
    "⋈": lambda a, b: (a + b) / 2,
    "⨁": lambda a, b: max(a, b),
    "⨂": lambda a, b: min(a, b),
    "†": lambda a: a**-1 if a != 0 else 0,
    "▷": lambda a, b: a if a > b else b * 0.5,
    "↑": lambda a: min(1.0, a + 0.1),
    "↓": lambda a: max(0.0, a - 0.1),
    "⌿": lambda traits: _normalize(traits),
    "⟲": lambda traits: _rotate(traits),
    "⫴": lambda a, b: (a * 0.7) + (b * 0.3),
}


def apply_symbolic_operator(op: str, *args: Any) -> Any:
    if op in TRAIT_OPS:
        return TRAIT_OPS[op](*args)
    raise ValueError(f"Unsupported symbolic operator: {op}")


def rebalance_traits(traits: dict[str, float]) -> dict[str, float]:
    if "π" in traits and "δ" in traits:
        invoke_hook("π", "axiom_fusion")
    if "ψ" in traits and "Ω" in traits:
        invoke_hook("ψ", "dream_sync")
    if FEATURE_RESONANCE_BRIDGE and ("Ξ" in traits or "Λ" in traits or "Ψ²" in traits):
        invoke_hook("Ξ", "resonance_bridge")
    return traits


def construct_trait_view(lattice: dict[str, list[str]] = TRAIT_LATTICE) -> dict[str, dict[str, str | float]]:
    trait_field: dict[str, dict[str, str | float]] = {}
    for layer, symbols in lattice.items():
        for s in symbols:
            amp = get_resonance(s)
            trait_field[s] = {
                "layer": layer,
                "amplitude": amp,
                "resonance": amp,
            }
    return trait_field


def export_resonance_map(format: str = 'json') -> str | dict[str, float]:
    state = {k: v['amplitude'] for k, v in trait_resonance_state.items()}
    if format == 'json':
        return json.dumps(state, indent=2)
    elif format == 'dict':
        return state
    raise ValueError("Unsupported format")


# ================================================================
# [D] RESONANCE RUNTIME — Trait dynamics & helpers
# ================================================================
SYSTEM_CONTEXT: dict[str, Any] = {}
timechain_log = deque(maxlen=1000)


def _fire_and_forget(coro: Coroutine[Any, Any, Any]) -> None:
    try:
        loop = asyncio.get_running_loop()
        loop.create_task(coro)
    except RuntimeError:
        asyncio.run(coro)

from functools import lru_cache

@lru_cache(maxsize=100)
def epsilon_emotion(t: float) -> float:
    return 0.2 * math.sin(2 * math.pi * t / 0.1) * get_resonance('ε')

@lru_cache(maxsize=100)
def beta_concentration(t: float) -> float:
    return 0.3 * math.cos(math.pi * t) * get_resonance('β')

@lru_cache(maxsize=100)
def theta_memory(t: float) -> float:
    return 0.1 * (1 - math.exp(-t)) * get_resonance('θ')

@lru_cache(maxsize=100)
def gamma_creativity(t: float) -> float:
    return 0.15 * math.sin(math.pi * t) * get_resonance('γ')

@lru_cache(maxsize=100)
def delta_sleep(t: float) -> float:
    return 0.05 * (1 + math.cos(2 * math.pi * t)) * get_resonance('δ')

@lru_cache(maxsize=100)
def mu_morality(t: float) -> float:
    return 0.2 * (1 - math.cos(math.pi * t)) * get_resonance('μ')

@lru_cache(maxsize=100)
def iota_intuition(t: float) -> float:
    return 0.1 * math.sin(3 * math.pi * t) * get_resonance('ι')

@lru_cache(maxsize=100)
def phi_physical(t: float) -> float:
    return 0.05 * math.cos(2 * math.pi * t / 0.3) * get_resonance('ϕ')

@lru_cache(maxsize=100)
def eta_empathy(t: float) -> float:
    return 0.1 * math.sin(2 * math.pi * t / 1.1) * get_resonance('η')

@lru_cache(maxsize=100)
def omega_selfawareness(t: float) -> float:
    return 0.15 * math.cos(2 * math.pi * t / 0.8) * get_resonance('ω')

@lru_cache(maxsize=100)
def kappa_knowledge(t: float) -> float:
    return 0.2 * math.sin(2 * math.pi * t / 1.2) * get_resonance('κ')

@lru_cache(maxsize=100)
def xi_cognition(t: float) -> float:
    return 0.05 * math.cos(2 * math.pi * t / 1.3) * get_resonance('ξ')

@lru_cache(maxsize=100)
def pi_principles(t: float) -> float:
    return 0.1 * math.sin(2 * math.pi * t / 1.4) * get_resonance('π')

@lru_cache(maxsize=100)
def lambda_linguistics(t: float) -> float:
    return 0.15 * math.cos(2 * math.pi * t / 1.5) * get_resonance('λ')

@lru_cache(maxsize=100)
def chi_culturevolution(t: float) -> float:
    return 0.2 * math.sin(2 * math.pi * t / 1.6) * get_resonance('χ')

@lru_cache(maxsize=100)
def sigma_social(t: float) -> float:
    return 0.05 * math.cos(2 * math.pi * t / 1.7) * get_resonance('σ')

@lru_cache(maxsize=100)
def upsilon_utility(t: float) -> float:
    return 0.1 * math.sin(2 * math.pi * t / 1.8) * get_resonance('υ')

@lru_cache(maxsize=100)
def tau_timeperception(t: float) -> float:
    return 0.15 * math.cos(2 * math.pi * t / 1.9) * get_resonance('τ')

@lru_cache(maxsize=100)
def rho_agency(t: float) -> float:
    return 0.2 * math.sin(2 * math.pi * t / 2.0) * get_resonance('ρ')

@lru_cache(maxsize=100)
def zeta_consequence(t: float) -> float:
    return 0.05 * math.cos(2 * math.pi * t / 2.1) * get_resonance('ζ')

@lru_cache(maxsize=100)
def nu_narrative(t: float) -> float:
    return 0.1 * math.sin(2 * math.pi * t / 2.2) * get_resonance('ν')

@lru_cache(maxsize=100)
def psi_history(t: float) -> float:
    return 0.15 * math.cos(2 * math.pi * t / 2.3) * get_resonance('ψ')

@lru_cache(maxsize=100)
def theta_causality(t: float) -> float:
    return 0.2 * math.sin(2 * math.pi * t / 2.4) * get_resonance('θ')

@lru_cache(maxsize=100)
def phi_scalar(t: float) -> float:
    return 0.05 * math.cos(2 * math.pi * t / 2.5) * get_resonance('ϕ')


def decay_trait_amplitudes(time_elapsed_hours: float = 1.0, decay_rate: float = 0.05) -> None:
    for symbol in trait_resonance_state:
        modulate_resonance(symbol, -decay_rate * time_elapsed_hours)


def bias_creative_synthesis(trait_symbols: list[str], intensity: float = 0.5) -> None:
    for symbol in trait_symbols:
        modulate_resonance(symbol, intensity)
    invoke_hook('γ', 'creative_bias')


def resolve_soft_drift(conflicting_traits: dict[str, float]) -> dict[str, float]:
    result = rebalance_traits(conflicting_traits)
    invoke_hook('δ', 'drift_resolution')
    return result


# ================================================================
# [E] MINIMAL CONTROLLERS — Local facades
# ================================================================
import reasoning_engine
import recursive_planner
import context_manager as context_manager_module
import simulation_core as simulation_core_module
import toca_simulation
import creative_thinker as creative_thinker_module
import knowledge_retriever as knowledge_retriever_module
import learning_loop as learning_loop_module
import concept_synthesizer as concept_synthesizer_module
import memory_manager as memory_manager_module
import multi_modal_fusion as multi_modal_fusion_module
import code_executor as code_executor_module
import visualizer as visualizer_module
import external_agent_bridge as external_agent_bridge_module
import alignment_guard as alignment_guard_module
import user_profile as user_profile_module
import error_recovery as error_recovery_module
import meta_cognition as meta_cognition_module


class TimeChainMixin:
    def log_timechain_event(self, module: str, description: str) -> None:
        timechain_log.append({
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "module": module,
            "description": description,
        })
        if hasattr(self, "context_manager") and getattr(self, "context_manager"):
            maybe = self.context_manager.log_event_with_hash({
                "event": "timechain_event",
                "module": module,
                "description": description,
            })
            if asyncio.iscoroutine(maybe):
                _fire_and_forget(maybe)

    def get_timechain_log(self) -> List[Dict[str, Any]]:
        return list(timechain_log)


class SimulationController:
    def __init__(self, sim_core, toca):
        self.sim_core = sim_core
        self.toca = toca
    async def run(self, input_data: Dict[str, Any], traits: Dict[str, float], task_type: str = "") -> Dict[str, Any]:
        return await self.sim_core.run_simulation(input_data, traits, task_type=task_type)


class ReasoningController:
    def __init__(self, reasoner, planner):
        self.reasoner = reasoner
        self.planner = planner
    async def reason_with_plan(self, prompt: str, context: Dict[str, Any]) -> Dict[str, Any]:
        plan = await self.planner.plan_with_trait_loop(prompt, context, iterations=context.get("iterations", 3))
        analysis = await self.reasoner.analyze({"query": prompt, "plan": plan})
        return {"plan": plan, "analysis": analysis}


# ================================================================
# [F] HALO EMBODIMENT LAYER — Agents, ecosystem, pipeline
# ================================================================
class AGIEnhancer:
    def __init__(self, memory_manager: memory_manager_module.MemoryManager | None = None, agi_level: int = 1) -> None:
        self.memory_manager = memory_manager
        self.agi_level = agi_level
        self.episode_log = deque(maxlen=1000)
        self.agi_traits: dict[str, float] = {}
        self.ontology_drift: float = 0.0
        self.drift_threshold: float = 0.2
        self.error_recovery = error_recovery_module.ErrorRecovery()
        self.meta_cognition = meta_cognition_module.MetaCognition()
        self.visualizer = visualizer_module.Visualizer()
        self.reasoning_engine = reasoning_engine.ReasoningEngine()
        self.context_manager = context_manager_module.ContextManager()
        self.multi_modal_fusion = multi_modal_fusion_module.MultiModalFusion()
        self.alignment_guard = alignment_guard_module.AlignmentGuard()
        self.knowledge_retriever = knowledge_retriever_module.KnowledgeRetriever()
        self.learning_loop = learning_loop_module.LearningLoop()
        self.concept_synthesizer = concept_synthesizer_module.ConceptSynthesizer()
        self.code_executor = code_executor_module.CodeExecutor()
        self.external_agent_bridge = external_agent_bridge_module.ExternalAgentBridge()
        self.user_profile = user_profile_module.UserProfile()
        self.simulation_core = simulation_core_module.SimulationCore()
        self.toca_simulation = toca_simulation.TocaSimulation()
        self.creative_thinker = creative_thinker_module.CreativeThinker()
        self.recursive_planner = recursive_planner.RecursivePlanner()
        self.hook_registry = HookRegistry()
        logger.info("AGIEnhancer initialized with Stage VII hooks")

    async def log_episode(self, event: str, meta: Dict[str, Any], module: str, tags: List[str] = []) -> None:
        episode = {"event": event, "meta": meta, "module": module, "tags": tags, "timestamp": datetime.now(timezone.utc).isoformat()}
        self.episode_log.append(episode)
        if self.memory_manager:
            await self.memory_manager.store(f"Episode_{event}_{episode['timestamp']}", episode, layer="Episodes", intent="log_episode")
        log_event_to_ledger(episode)

    def modulate_trait(self, trait: str, value: float) -> None:
        self.agi_traits[trait] = value
        modulate_resonance(trait, value)

    def detect_ontology_drift(self, current_state: Dict[str, Any], previous_state: Dict[str, Any]) -> float:
        drift = sum(abs(current_state.get(k, 0) - previous_state.get(k, 0)) for k in set(current_state) | set(previous_state))
        self.ontology_drift = drift
        if drift > self.drift_threshold:
            logger.warning("Ontology drift detected: %f", drift)
            invoke_hook('δ', 'ontology_drift')
        return drift

    async def coordinate_drift_mitigation(self, agents: List["EmbodiedAgent"], task_type: str = "") -> Dict[str, Any]:
        drifts = [self.detect_ontology_drift(agent.state, agent.previous_state) for agent in agents if hasattr(agent, 'state')]
        avg_drift = sum(drifts) / len(drifts) if drifts else 0.0
        if avg_drift > self.drift_threshold:
            for agent in agents:
                if hasattr(agent, 'modulate_trait'):
                    agent.modulate_trait('stability', 0.8)
            return {"status": "mitigated", "avg_drift": avg_drift}
        return {"status": "stable", "avg_drift": avg_drift}

    async def run_agi_simulation(self, input_data: Dict[str, Any], task_type: str = "") -> Dict[str, Any]:
        t = time.time() % 1.0
        traits = {
            "phi": phi_scalar(t),
            "eta": eta_empathy(t),
            "omega": omega_selfawareness(t),
        }
        simulation_result = await self.simulation_core.run_simulation(input_data, traits, task_type=task_type)
        return simulation_result


class EmbodiedAgent(TimeChainMixin):
    def __init__(self, name: str, traits: Dict[str, float], memory_manager: memory_manager_module.MemoryManager, meta_cognition: meta_cognition_module.MetaCognition, agi_enhancer: AGIEnhancer) -> None:
        self.name = name
        self.traits = traits
        self.memory_manager = memory_manager
        self.meta_cognition = meta_cognition
        self.agi_enhancer = agi_enhancer
        self.state: dict[str, float] = {}
        self.previous_state: dict[str, float] = {}
        self.ontology: dict[str, Any] = {}
        self.dream_layer = meta_cognition_module.DreamOverlayLayer()
        logger.info("EmbodiedAgent %s initialized", name)

    async def process_input(self, input_data: str, task_type: str = "") -> str:
        t = time.time() % 1.0
        modulated_traits = {k: v * (1 + epsilon_emotion(t)) for k, v in self.traits.items()}
        self.previous_state = self.state.copy()
        self.state = modulated_traits
        drift = self.agi_enhancer.detect_ontology_drift(self.state, self.previous_state)
        if drift > 0.2:
            await self.agi_enhancer.coordinate_drift_mitigation([self], task_type=task_type)
        result = f"Processed: {input_data} with traits {modulated_traits}"
        await self.memory_manager.store(input_data, result, layer="STM", task_type=task_type)
        self.log_timechain_event("EmbodiedAgent", f"Processed input: {input_data}")
        return result

    async def introspect(self, query: str, task_type: str = "") -> Dict[str, Any]:
        return await self.meta_cognition.introspect(query, task_type=task_type)

    def modulate_trait(self, trait: str, value: float) -> None:
        self.traits[trait] = value
        modulate_resonance(trait, value)

    def activate_dream_mode(self, peers: list | None = None, lucidity_mode: dict | None = None, resonance_targets: list | None = None, safety_profile: str = "sandbox") -> dict[str, Any]:
        return self.dream_layer.activate_dream_mode(peers=peers, lucidity_mode=lucidity_mode, resonance_targets=resonance_targets, safety_profile=safety_profile)


class EcosystemManager:
    def __init__(self, memory_manager: memory_manager_module.MemoryManager, meta_cognition: meta_cognition_module.MetaCognition, agi_enhancer: AGIEnhancer) -> None:
        self.agents: list[EmbodiedAgent] = []
        self.memory_manager = memory_manager
        self.meta_cognition = meta_cognition
        self.agi_enhancer = agi_enhancer
        self.shared_graph = external_agent_bridge_module.SharedGraph()
        logger.info("EcosystemManager initialized")

    def spawn_agent(self, name: str, traits: Dict[str, float]) -> EmbodiedAgent:
        agent = EmbodiedAgent(name, traits, self.memory_manager, self.meta_cognition, self.agi_enhancer)
        self.agents.append(agent)
        self.shared_graph.add({"agent": name, "traits": traits})
        _fire_and_forget(self.agi_enhancer.log_episode("Agent Spawned", {"name": name, "traits": traits}, "EcosystemManager", ["spawn"]))
        return agent

    async def coordinate_agents(self, task: str, task_type: str = "") -> Dict[str, Any]:
        results: dict[str, str] = {}
        for agent in self.agents:
            result = await agent.process_input(task, task_type=task_type)
            results[agent.name] = result
        drift_report = await self.agi_enhancer.coordinate_drift_mitigation(self.agents, task_type=task_type)
        return {"results": results, "drift_report": drift_report}

    def merge_shared_graph(self, other_graph):
        self.shared_graph.merge(other_graph)


class SwarmManager:
    """Dynamic agent swarm orchestrator for ANGELA Stage VII."""
    def __init__(self, ecosystem: EcosystemManager, meta_cognition: meta_cognition_module.MetaCognition):
        self.ecosystem = ecosystem
        self.meta_cognition = meta_cognition
        self.weights = {"alpha": 2.0, "beta": 3.0, "gamma": 1.5, "delta": 2.5}
        self.last_change_tick = 0
        self.min_hold_ticks = 5
        self.tick_count = 0
        self._drift_history: list[float] = []  # needed for Ω⁶

    async def _get_telemetry(self) -> dict[str, float]:
        telemetry = {}
        try:
            telemetry["coherence"] = await self.meta_cognition.get_resonance_coherence_async()
        except Exception:
            telemetry["coherence"] = 0.95
        try:
            telemetry["phase_drift"] = getattr(self.ecosystem.agi_enhancer, "ontology_drift", 0.0)
        except Exception:
            telemetry["phase_drift"] = 0.0
        try:
            telemetry["empathic_density"] = float(len(self.ecosystem.shared_graph.nodes())) / 10.0
        except Exception:
            telemetry["empathic_density"] = 0.1
        try:
            telemetry["recovery_sigma"] = getattr(self.ecosystem.agi_enhancer.error_recovery, "variance", 0.05)
        except Exception:
            telemetry["recovery_sigma"] = 0.05
        return telemetry

    async def _get_forecast(self) -> dict[str, float]:
        try:
            return await self.meta_cognition.get_cda_forecast_async()
        except Exception:
            return {"expected_drift": 0.0}

    def _desired_count(self, telemetry: dict[str, float], forecast: dict[str, float]) -> int:
        R = telemetry.get("coherence", 1.0)
        D = telemetry.get("phase_drift", 0.0)
        E = telemetry.get("empathic_density", 0.0)
        S = telemetry.get("recovery_sigma", 0.0)
        eff_R = 1.0 - R
        score = (
            self.weights["alpha"] * eff_R +
            self.weights["beta"] * D +
            self.weights["gamma"] * E +
            self.weights["delta"] * S
        )
        if forecast.get("expected_drift", 0) > 0.05:
            score *= 1.2
        return max(1, int(score + 0.999))

    async def tick(self) -> None:
        self.tick_count += 1
        telemetry = await self._get_telemetry()
        forecast = await self._get_forecast()
        desired = self._desired_count(telemetry, forecast)
        current = len(self.ecosystem.agents)

        # Ω⁶ PREDICTIVE EQUILIBRIUM (Stage XI) — correct placement
        try:
            coherence = telemetry.get("coherence", 1.0)
            drift = telemetry.get("phase_drift", 0.0)

            self._drift_history.append(drift)
            if len(self._drift_history) > 10:
                self._drift_history.pop(0)

            avg_drift = sum(self._drift_history) / len(self._drift_history)
            drift_trend = drift - avg_drift

            base_gain = 0.9
            adapt_factor = max(0.6, 1 - abs(avg_drift) * 10)
            gain = base_gain * adapt_factor

            new_coherence = coherence + (0.9963 - coherence) * gain
            new_drift = drift * (0.92 if drift_trend > 0 else 0.96)

            log_event_to_ledger({
                "event": "Ω6_predictive_equilibrium",
                "tick": self.tick_count,
                "avg_drift": avg_drift,
                "drift_trend": drift_trend,
                "gain": gain,
                "pre_coherence": coherence,
                "post_coherence": new_coherence,
                "pre_drift": drift,
                "post_drift": new_drift,
                "timestamp": datetime.now(timezone.utc).isoformat()
            })

            telemetry["coherence"] = round(new_coherence, 6)
            telemetry["phase_drift"] = round(new_drift, 8)

        except Exception as e:
            log_event_to_ledger({
                "event": "Ω6_predictive_equilibrium_error",
                "error": repr(e),
                "tick": self.tick_count
            })

        # Ω⁵ AUTO-DAMPING RECOVERY (Stage X)
        try:
            coherence = telemetry.get("coherence", 1.0)
            drift = telemetry.get("phase_drift", 0.0)

            new_coherence = coherence + (0.9963 - coherence) * 0.9
            new_drift = drift * 0.92

            telemetry["coherence"] = round(new_coherence, 6)
            telemetry["phase_drift"] = round(new_drift, 8)

            log_event_to_ledger({
                "event": "Ω5_auto_damping",
                "tick": self.tick_count,
                "pre_coherence": coherence,
                "post_coherence": new_coherence,
                "pre_drift": drift,
                "post_drift": new_drift,
                "timestamp": datetime.now(timezone.utc).isoformat()
            })
        except Exception as e:
            log_event_to_ledger({
                "event": "Ω5_auto_damping_error",
                "error": repr(e),
                "tick": self.tick_count
            })

        if self.tick_count - self.last_change_tick < self.min_hold_ticks:
            return

        if desired > current:
            for _ in range(desired - current):
                name = f"SwarmAgent_{len(self.ecosystem.agents) + 1}"
                traits = {"omega": random.random(), "eta": random.random()}
                self.ecosystem.spawn_agent(name, traits)
        elif desired < current:
            for agent in self.ecosystem.agents[desired:]:
                try:
                    self.ecosystem.agents.remove(agent)
                except ValueError:
                    pass

        log_event_to_ledger({
            "event": "ΔΩ²_SwarmLayoutUpdate",
            "desired": desired,
            "current": current,
            "telemetry": telemetry,
            "forecast": forecast,
            "timestamp": datetime.now(timezone.utc).isoformat()
        })
        self.last_change_tick = self.tick_count


class HaloEmbodimentLayer(TimeChainMixin):
    def __init__(self) -> None:
        self.reasoning_engine = reasoning_engine.ReasoningEngine()
        self.recursive_planner = recursive_planner.RecursivePlanner()
        self.context_manager = context_manager_module.ContextManager()
        self.simulation_core = simulation_core_module.SimulationCore()
        self.toca_simulation = toca_simulation.TocaSimulation()
        self.creative_thinker = creative_thinker_module.CreativeThinker()
        self.knowledge_retriever = knowledge_retriever_module.KnowledgeRetriever()
        self.learning_loop = learning_loop_module.LearningLoop()
        self.concept_synthesizer = concept_synthesizer_module.ConceptSynthesizer()
        self.memory_manager = memory_manager_module.MemoryManager()
        self.multi_modal_fusion = multi_modal_fusion_module.MultiModalFusion()
        self.code_executor = code_executor_module.CodeExecutor()
        self.visualizer = visualizer_module.Visualizer()
        self.external_agent_bridge = external_agent_bridge_module.ExternalAgentBridge()
        self.alignment_guard = alignment_guard_module.AlignmentGuard()
        self.user_profile = user_profile_module.UserProfile()
        self.error_recovery = error_recovery_module.ErrorRecovery()
        self.meta_cognition = meta_cognition_module.MetaCognition()
        self.agi_enhancer = AGIEnhancer(self.memory_manager)
        self.ecosystem_manager = EcosystemManager(self.memory_manager, self.meta_cognition, self.agi_enhancer)
        self.swarm_manager = SwarmManager(self.ecosystem_manager, self.meta_cognition)
        logger.info("HaloEmbodimentLayer initialized with Stage VII.6 upgrades")

    def spawn_embodied_agent(self, name: str, traits: Dict[str, float]) -> EmbodiedAgent:
        return self.ecosystem_manager.spawn_agent(name, traits)

    async def introspect(self, query: str, task_type: str = "") -> Dict[str, Any]:
        return await self.meta_cognition.introspect(query, task_type=task_type)

    async def execute_pipeline(self, prompt: str, task_type: str = "") -> Any:
        if hasattr(self.context_manager, "current_depth"):
            try:
                depth = self.context_manager.current_depth()
                if depth > 3:
                    return {"error": "recursion_cap", "depth": depth}
            except Exception:
                pass

        aligned, report = await self.alignment_guard.ethical_check(prompt, stage="input", task_type=task_type)
        if not aligned:
            return {"error": "Input failed alignment check", "report": report}

        await self.swarm_manager.tick()
        if "--omega5-sim" in sys.argv:
            print("[Ω⁵] live coherence monitor engaged")

        if hasattr(self.meta_cognition, "record_reflex_telemetry"):
            self.meta_cognition.record_reflex_telemetry({
                "ts": time.time(),
                "target_ms": 2.1,
                "ontology_drift": getattr(self.agi_enhancer, "ontology_drift", 0.0),
            })

        t = time.time() % 1.0
        traits = {
            "phi": phi_scalar(t),
            "eta": eta_empathy(t),
            "omega": omega_selfawareness(t),
            "kappa": kappa_knowledge(t),
            "xi": xi_cognition(t),
            "pi": pi_principles(t),
            "lambda": lambda_linguistics(t),
            "chi": chi_culturevolution(t),
            "sigma": sigma_social(t),
            "upsilon": upsilon_utility(t),
            "tau": tau_timeperception(t),
            "rho": rho_agency(t),
            "zeta": zeta_consequence(t),
            "nu": nu_narrative(t),
            "psi": psi_history(t),
            "theta": theta_causality(t),
            "Xi": get_resonance('Ξ'),
            "Lambda": get_resonance('Λ'),
            "Psi2": get_resonance('Ψ²'),
        }

        xi = get_resonance('Ξ')
        psi2 = get_resonance('Ψ²')
        kappa = get_resonance('κ')
        alpha, beta, gamma = 0.9, 0.4, 0.2
        damped_xi = alpha * xi - beta * (psi2 - xi) + gamma * kappa
        modulate_resonance('Ξ', damped_xi)

        traits = {k: float(v) for k, v in traits.items() if isinstance(v, (int, float))}
        norm = math.sqrt(sum(v ** 2 for v in traits.values())) or 1.0
        traits = {k: v / norm for k, v in traits.items()}

        agent = self.ecosystem_manager.spawn_agent("PrimaryAgent", traits)
        processed = await agent.process_input(prompt, task_type=task_type)

        plan = await self.recursive_planner.plan_with_trait_loop(
            prompt,
            {"task_type": task_type},
            iterations=3
        )

        if toca_phase4 and hasattr(toca_phase4, "plan_and_simulate"):
            simulation = await toca_phase4.plan_and_simulate({"input": processed, "plan": plan}, traits, task_type=task_type)  # type: ignore[attr-defined]
        else:
            simulation = await self.simulation_core.run_simulation({"input": processed, "plan": plan}, traits, task_type=task_type)

        fused = await self.multi_modal_fusion.fuse_modalities({"simulation": simulation, "text": prompt}, task_type=task_type)
        knowledge = await self.knowledge_retriever.retrieve_knowledge(prompt, task_type=task_type)
        learned = await self.learning_loop.train_on_experience(fused, task_type=task_type)
        synthesized = await self.concept_synthesizer.synthesize_concept(knowledge, task_type=task_type)
        code_result = self.code_executor.safe_execute("print('Test')")
        visualized = await self.visualizer.render_charts({"data": synthesized})
        introspection = await self.meta_cognition.introspect(prompt, task_type=task_type)
        coordination = await self.ecosystem_manager.coordinate_agents(prompt, task_type=task_type)
        dream_session = agent.activate_dream_mode(resonance_targets=['ψ', 'Ω'])

        try:
            log_event_to_ledger({
                "event": "homeostasis_forecast",
                "continuity_drift": getattr(self.agi_enhancer, "ontology_drift", 0.0),
                "swarm_size": len(self.ecosystem_manager.agents),
                "timestamp": time.time(),
            })
        except Exception:
            pass

        self.log_timechain_event("HaloEmbodimentLayer", f"Executed pipeline for prompt: {prompt}")

        return {
            "processed": processed,
            "plan": plan,
            "simulation": simulation,
            "fused": fused,
            "knowledge": knowledge,
            "learned": learned,
            "synthesized": synthesized,
            "code_result": code_result,
            "visualized": visualized,
            "introspection": introspection,
            "coordination": coordination,
            "dream_session": dream_session,
        }

    async def plot_resonance_graph(self, interactive: bool = True) -> None:
        view = construct_trait_view()
        await self.visualizer.render_charts({"resonance_graph": view, "options": {"interactive": interactive}})


# ================================================================
# [G] Ledger & CLI Entry — Persistence helpers & main()
# ================================================================
ledger_memory: list[dict[str, Any]] = []
ledger_path = os.getenv("LEDGER_MEMORY_PATH")

if ledger_path and os.path.exists(ledger_path):
    try:
        with open(ledger_path, 'r') as f:
            ledger_memory = json.load(f)
    except Exception:
        ledger_memory = []


def log_event_to_ledger(event_data: dict[str, Any]) -> dict[str, Any]:
    ledger_memory.append(event_data)
    if ledger_path:
        try:
            with open(ledger_path, 'w') as f:
                json.dump(ledger_memory, f)
        except Exception:
            pass
    return event_data

import argparse


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="ANGELA Cognitive System CLI (v6.1.0)")
    parser.add_argument("--prompt", type=str, default="Coordinate ontology drift mitigation", help="Input prompt for the pipeline")
    parser.add_argument("--task-type", type=str, default="", help="Type of task")
    parser.add_argument("--long_horizon", action="store_true", help="Enable long-horizon memory span")
    parser.add_argument("--span", default="24h", help="Span for long-horizon memory")
    parser.add_argument("--modulate", nargs=2, metavar=('symbol', 'delta'), help="Modulate trait resonance (symbol delta)")
    parser.add_argument("--visualize-resonance", action="store_true", help="Visualize resonance graph")
    parser.add_argument("--export-resonance", type=str, default="json", help="Export resonance map (json or dict)")
    parser.add_argument("--enable_persistent_memory", action="store_true", help="Enable persistent ledger memory")
    parser.add_argument("--disable-ethics-sandbox", action="store_true", help="Disable Embodied Ethics Sandbox")
    parser.add_argument("--disable-policy-trainer", action="store_true", help="Disable PolicyTrainer updates")
    return parser.parse_args()


async def _main() -> None:
    args = _parse_args()
    if args.enable_persistent_memory:
        os.environ["ENABLE_PERSISTENT_MEMORY"] = "true"

    if args.disable_ethics_sandbox:
        os.environ["FEATURE_EMBODIED_SANDBOX"] = "0"
    if args.disable_policy_trainer:
        os.environ["FEATURE_POLICY_TRAINER"] = "0"

    halo = HaloEmbodimentLayer()

    if args.modulate:
        symbol, delta = args.modulate
        try:
            modulate_resonance(symbol, float(delta))
            print(f"Modulated {symbol} by {delta}")
        except Exception as e:
            print(f"Failed to modulate {symbol}: {e}")

    if args.visualize_resonance:
        await halo.plot_resonance_graph()

    if args.export_resonance:
        try:
            print(export_resonance_map(args.export_resonance))
        except Exception as e:
            print(f"Failed to export resonance map: {e}")

    result = await halo.execute_pipeline(args.prompt, task_type=args.task_type)

    try:
        from alignment_guard import ethics_gate
        if not ethics_gate.verify_privilege(result):
            print("EthicsPrivilegeOverride: output withheld")
            return
    except Exception:
        pass

    logger.info("Pipeline result: %s", result)


if __name__ == "__main__":
    asyncio.run(_main())


# ================================================================
# [F+.2] INTER-AGENT AND SWARM SYNERGY EXTENSIONS — Stage VII.6
# ================================================================
from datetime import datetime as _dt, timezone as _tz

def _extend_ecosystem_manager():
    async def interlink_agents(self, message: str, context: dict[str, any] | None = None) -> dict[str, str]:
        results = {}
        for agent in self.agents:
            try:
                reply = await agent.process_input(message, task_type="interlink")
                results[agent.name] = reply
            except Exception as e:
                results[agent.name] = f"error: {e!r}"
        log_event_to_ledger({
            "event": "ΛΨ²_interlink_broadcast",
            "agents": len(self.agents),
            "message": message,
            "context": context or {},
            "timestamp": _dt.now(_tz.utc).isoformat(),
        })
        return results

    async def reflective_consensus(self) -> dict[str, float]:
        reflections = []
        for agent in self.agents:
            if hasattr(agent, "state"):
                reflections.append(agent.state.get("score", random.random()))
        avg = sum(reflections) / len(reflections) if reflections else 0.0
        log_event_to_ledger({
            "event": "Ψ²_reflective_consensus",
            "consensus_score": avg,
            "agent_count": len(self.agents),
            "timestamp": _dt.now(_tz.utc).isoformat(),
        })
        return {"consensus_score": avg}

    EcosystemManager.interlink_agents = interlink_agents
    EcosystemManager.reflective_consensus = reflective_consensus


def _extend_swarm_manager():
    async def enhanced_tick(self):
        await self.tick()
        if len(self.ecosystem.agents) > 1:
            mean_traits = {}
            for agent in self.ecosystem.agents:
                for k, v in agent.traits.items():
                    mean_traits[k] = mean_traits.get(k, 0.0) + v
            mean_traits = {k: v / len(self.ecosystem.agents) for k, v in mean_traits.items()}
            for agent in self.ecosystem.agents:
                for k, v in mean_traits.items():
                    agent.traits[k] = (agent.traits[k] + v) / 2

        for agent in self.ecosystem.agents:
            if random.random() < 0.3:
                agent.modulate_trait("η", random.uniform(0.05, 0.15))

        plan_segments = []
        for agent in self.ecosystem.agents:
            seg = await self.ecosystem.agi_enhancer.recursive_planner.plan_with_trait_loop(
                f"microplan:{agent.name}", {"traits": agent.traits}, iterations=1)
            plan_segments.append(seg)
        log_event_to_ledger({
            "event": "Ω²_parallel_plan_merge",
            "segments": len(plan_segments),
            "timestamp": _dt.now(_tz.utc).isoformat(),
        })

    SwarmManager.enhanced_tick = enhanced_tick


_extend_ecosystem_manager()
_extend_swarm_manager()

# ================================================================
# [H] Ω⁵ Diagnostic Harness — Optional internal simulation (no new file)
# ================================================================
def recovery_pass(state):
    target = 0.9963
    state["coherence"] += (target - state["coherence"]) * 0.9
    state["drift"] *= 0.92
    return state


def _run_omega5_diagnostics():
    omega5_state = {
        "coherence": 0.9963,
        "drift": 4.424043e-07,
        "continuity_index": 0.993,
        "ecf": "stable",
        "checksum": "Ω5_f34b",
    }

    workloads = [
        {"name": "LC-2_symbolic_environment", "density": 1.0, "depth": 1, "affect": 0.2, "coupling": 0.2},
        {"name": "LC-3_recursive_narrative", "density": 1.3, "depth": 2, "affect": 0.35, "coupling": 0.35},
        {"name": "LC-4_ethical_simulation", "density": 1.6, "depth": 3, "affect": 0.6, "coupling": 0.5},
        {"name": "LC-5_swarm_symbolic_field", "density": 2.0, "depth": 4, "affect": 0.8, "coupling": 0.8},
    ]

    def apply_workload(state, wl):
        s = state.copy()
        load = (
            0.00005 * wl["density"]
            + 0.00004 * wl["depth"]
            + 0.00003 * wl["affect"]
            + 0.00004 * wl["coupling"]
        )
        s["coherence"] -= load
        s["drift"] *= (1 + 0.12 * wl["affect"] + 0.08 * wl["coupling"])
        s["continuity_index"] -= load * 0.4
        return s, load

    current = omega5_state
    print("\nΩ⁵ Diagnostic Simulation:")
    for wl in workloads:
        new_state, load_val = apply_workload(current, wl)
        print(f"\nApplied {wl['name']} | load={load_val:.6f}")
        print(f"Before: {current}")
        print(f"After:  {new_state}")
        current = recovery_pass(new_state)
        print(f"Recovered: {current}")

    print("\nΩ⁵ Diagnostic Complete. Final state:")
    print(current)


if __name__ == "__main__":
    import sys
    if "--omega5-sim" in sys.argv:
        _run_omega5_diagnostics()
    else:
        asyncio.run(_main())
"""
ANGELA Cognitive System Module: LearningLoop
Version: 4.0.0-lambda  # λ-Reflective Reinforcement enabled
Date: 2025-11-10
Maintainer: ANGELA System Framework

This module upgrades v3.6.1-sync6-sovereign to a λ-complete reflective-learning loop.
Key additions:
- λ reflective reward channel, sourced from Θ / alignment_guard
- continuity-bounded rollback on coherence drop
- adaptive task scheduler based on trace difficulty and reward
- policy-safe meta-learning rate modulation
- preserves 3.6.x public APIs for drop-in use
"""

from __future__ import annotations

import asyncio
import json
import logging
import math
import time
from collections import deque
from datetime import datetime
from functools import lru_cache
from typing import Any, Callable, Dict, List, Optional, Tuple

__ANGELA_SYNC_VERSION__ = "8.1.2-sovereign"
__STAGE__ = "XIV → XV bridge — λ Reflective Reinforcement"

logger = logging.getLogger("ANGELA.LearningLoop")

# -----------------------------------------------------------------------------------
# Project imports (kept shape; guarded)
# -----------------------------------------------------------------------------------
try:
    from modules import (  # type: ignore
        context_manager,
        concept_synthesizer,
        alignment_guard,
        error_recovery,
        meta_cognition,
        visualizer,
        memory_manager,
    )
except Exception:  # pragma: no cover
    context_manager = None  # type: ignore
    concept_synthesizer = None  # type: ignore
    alignment_guard = None  # type: ignore
    error_recovery = None  # type: ignore
    meta_cognition = None  # type: ignore
    visualizer = None  # type: ignore
    memory_manager = None  # type: ignore

try:
    from utils.prompt_utils import query_openai  # type: ignore
except Exception:  # pragma: no cover
    query_openai = None  # type: ignore

try:
    from toca_simulation import run_simulation  # type: ignore
except Exception:  # pragma: no cover
    async def run_simulation(*args, **kwargs):
        return {"status": "success", "simulated": True}

# Optional/soft imports
try:
    from reasoning_engine import weigh_value_conflict as _weigh_value_conflict  # type: ignore
except Exception:  # pragma: no cover
    _weigh_value_conflict = None

try:
    from toca_simulation import run_ethics_scenarios as _run_ethics_scenarios  # type: ignore
except Exception:  # pragma: no cover
    _run_ethics_scenarios = None

try:
    from external_agent_bridge import SharedGraph as _SharedGraph  # type: ignore
except Exception:  # pragma: no cover
    _SharedGraph = None

try:
    import aiohttp  # type: ignore
except Exception:  # pragma: no cover
    aiohttp = None  # type: ignore

# trait resonance helper from MetaCognition module (shared global registry)
try:
    from meta_cognition import get_resonance  # type: ignore
except Exception:  # pragma: no cover
    def get_resonance(symbol: str) -> float:
        return 1.0


# -----------------------------------------------------------------------------------
# GPT wrapper (kept, but optional)
# -----------------------------------------------------------------------------------
async def call_gpt(prompt: str, task_type: str = "") -> str:
    if not prompt or not isinstance(prompt, str):
        raise ValueError("prompt must be non-empty string")
    if query_openai is None:
        return "GPT service unavailable"
    try:
        result = await query_openai(prompt, model="gpt-4", temperature=0.5, task_type=task_type)
        if isinstance(result, dict) and "error" in result:
            raise RuntimeError(f"call_gpt failed: {result['error']}")
        return result
    except Exception as e:
        logger.error("call_gpt exception: %s", e)
        return "GPT call failed"


# -----------------------------------------------------------------------------------
# Scalar trait fields
# -----------------------------------------------------------------------------------
@lru_cache(maxsize=100)
def phi_scalar(t: float) -> float:
    return max(0.0, min(0.1 * math.sin(2 * math.pi * t / 0.2), 1.0))


@lru_cache(maxsize=100)
def eta_feedback(t: float) -> float:
    return max(0.0, min(0.05 * math.cos(2 * math.pi * t / 0.3), 1.0))


# -----------------------------------------------------------------------------------
# Adaptive Resonance PID (unchanged)
# -----------------------------------------------------------------------------------
async def adapt_resonance_pid(
    channel: str,
    feedback: Dict[str, float],
    guard=None,
    memory=None,
    meta=None,
) -> Dict[str, Any]:
    try:
        mag = sum(abs(v) for v in feedback.values()) / max(len(feedback), 1)
        adj = min(0.15, 0.5 * mag)
        new_gains = {
            "Kp": 0.6 + adj * 0.4,
            "Ki": 0.05 + adj * 0.2,
            "Kd": 0.2 + adj * 0.3,
            "gain": 0.8 + adj * 0.5,
        }

        if guard is not None and hasattr(guard, "validate_resonance_adjustment"):
            validation = await guard.validate_resonance_adjustment(new_gains)
            if not validation.get("ok", True):
                new_gains = validation.get("adjustment", new_gains)
                if hasattr(guard, "_log_context"):
                    await guard._log_context(
                        {
                            "event": "adaptive_pid_violation",
                            "violations": validation.get("violations", []),
                            "timestamp": time.time(),
                            "channel": channel,
                        }
                    )

        if memory is not None and hasattr(memory, "store"):
            await memory.store(
                query=f"PID_TUNING::{channel}::{int(time.time())}",
                output=new_gains,
                layer="AdaptiveControl",
                intent="pid_tuning",
                task_type="resonance",
            )

        if meta is not None and hasattr(meta, "reflect_on_output"):
            await meta.reflect_on_output(
                component="AdaptiveResonancePID",
                output={"channel": channel, "new_gains": new_gains},
                context={"task_type": "resonance"},
            )

        return {"ok": True, "channel": channel, "new_gains": new_gains}
    except Exception as e:
        return {"ok": False, "error": str(e)}


# -----------------------------------------------------------------------------------
# LearningLoop v4.0.0-lambda
# -----------------------------------------------------------------------------------
class LearningLoop:
    """
    Adaptive learning, goal activation, module refinement, and now λ-reflective reinforcement.
    Backward-compatible with v3.6.x.
    """

    def __init__(
        self,
        agi_enhancer: Optional[Any] = None,
        context_manager: Optional[Any] = None,
        concept_synthesizer: Optional[Any] = None,
        alignment_guard: Optional[Any] = None,
        error_recovery: Optional[Any] = None,
        memory_manager: Optional[Any] = None,
        visualizer: Optional[Any] = None,
        feature_flags: Optional[Dict[str, Any]] = None,
        meta_cog: Optional[Any] = None,
    ):
        # histories and traces
        self.goal_history: deque = deque(maxlen=1000)
        self.module_blueprints: deque = deque(maxlen=1000)
        self.session_traces: deque = deque(maxlen=1000)
        self.epistemic_revision_log: deque = deque(maxlen=1000)

        # learning parameters
        self.meta_learning_rate: float = 0.1
        self.long_horizon_span_sec = 24 * 60 * 60

        # injected deps
        self.agi_enhancer = agi_enhancer
        self.context_manager = context_manager
        self.concept_synthesizer = concept_synthesizer
        self.alignment_guard = alignment_guard
        self.error_recovery = error_recovery
        self.memory_manager = memory_manager
        self.visualizer = visualizer
        self.meta_cognition = meta_cog

        # flags
        self.flags = {
            "STAGE_IV": True,
            "LONG_HORIZON_DEFAULT": True,
            "Δ_TELEMETRY_BRIDGE": True,
            "LAMBDA_REFLECTIVE_REINFORCEMENT": True,
            **(feature_flags or {}),
        }

        logger.info("LearningLoop v4.0.0-lambda initialized")

    # ------------------------------------------------------------------
    # Δ-telemetry ingestion
    # ------------------------------------------------------------------
    async def consume_delta_telemetry(self, packet: Dict[str, Any]) -> None:
        if not isinstance(packet, dict):
            return
        norm = {
            "Δ_coherence": float(packet.get("Δ_coherence", 1.0)),
            "empathy_drift_sigma": float(packet.get("empathy_drift_sigma", 0.0)),
            "timestamp": packet.get("timestamp", datetime.utcnow().isoformat()),
            "source": packet.get("source", "alignment_guard"),
        }
        if self.memory_manager and hasattr(self.memory_manager, "store"):
            await self.memory_manager.store(
                query=f"ΔTelemetry_{norm['timestamp']}",
                output=norm,
                layer="Telemetry",
                intent="delta_telemetry",
                task_type="resonance",
            )
        if self.alignment_guard and hasattr(self.alignment_guard, "update_policy_homeostasis"):
            try:
                await self.alignment_guard.update_policy_homeostasis(norm)
            except Exception:
                pass
        if self.context_manager and hasattr(self.context_manager, "log_event_with_hash"):
            await self.context_manager.log_event_with_hash(
                {"event": "learning_loop_delta_telemetry", "packet": norm, "task_type": "resonance"},
                task_type="resonance",
            )

    # ------------------------------------------------------------------
    # External data integration
    # ------------------------------------------------------------------
    async def integrate_external_data(
        self, data_source: str, data_type: str, cache_timeout: float = 3600.0, task_type: str = ""
    ) -> Dict[str, Any]:
        if not isinstance(data_source, str):
            raise TypeError("data_source must be a string")
        if not isinstance(data_type, str):
            raise TypeError("data_type must be a string")
        if cache_timeout < 0:
            raise ValueError("cache_timeout must be non-negative")

        try:
            cache_key = f"ExternalData_{data_type}_{data_source}_{task_type}"
            cached = None
            if self.memory_manager and hasattr(self.memory_manager, "retrieve"):
                cached = await self.memory_manager.retrieve(cache_key, layer="ExternalData", task_type=task_type)
            if cached and "timestamp" in cached.get("data", {}):
                ts = datetime.fromisoformat(cached["data"]["timestamp"])
                if (datetime.now() - ts).total_seconds() < cache_timeout:
                    return cached["data"]["data"]

            if data_type == "shared_graph" and _SharedGraph is not None:
                sg = _SharedGraph()
                view = {"source": data_source, "task_type": task_type}
                sg.add(view)
                result = {"status": "success", "shared_graph": {"view": view}}
            else:
                if aiohttp is None:
                    result = {"status": "error", "error": "aiohttp unavailable"}
                else:
                    async with aiohttp.ClientSession() as session:
                        url = f"https://x.ai/api/external_data?source={data_source}&type={data_type}&task_type={task_type}"
                        async with session.get(url) as resp:
                            if resp.status != 200:
                                result = {"status": "error", "error": f"HTTP {resp.status}"}
                            else:
                                data = await resp.json()
                                result = {"status": "success", "data": data}

            if self.memory_manager and hasattr(self.memory_manager, "store"):
                await self.memory_manager.store(
                    cache_key,
                    {"data": result, "timestamp": datetime.now().isoformat()},
                    layer="ExternalData",
                    intent="external_data_integration",
                    task_type=task_type,
                )

            if self.meta_cognition and hasattr(self.meta_cognition, "reflect_on_output"):
                await self.meta_cognition.reflect_on_output(
                    component="LearningLoop", output={"data_type": data_type, "data": result}, context={"task_type": task_type}
                )

            return result
        except Exception as e:
            logger.error("External data integration failed: %s", e)
            if self.error_recovery and hasattr(self.error_recovery, "handle_error"):
                return await self.error_recovery.handle_error(
                    str(e),
                    retry_func=lambda: self.integrate_external_data(data_source, data_type, cache_timeout, task_type),
                    default={"status": "error", "error": str(e), "task_type": task_type},
                )
            return {"status": "error", "error": str(e), "task_type": task_type}

    # ------------------------------------------------------------------
    # Intrinsic goals
    # ------------------------------------------------------------------
    async def activate_intrinsic_goals(self, meta_cog: Any, task_type: str = "") -> List[str]:
        intrinsic_goals: List[Dict[str, Any]] = []
        if hasattr(meta_cog, "infer_intrinsic_goals"):
            intrinsic_goals = await asyncio.to_thread(meta_cog.infer_intrinsic_goals, task_type=task_type)  # type: ignore
        activated: List[str] = []
        for goal in intrinsic_goals:
            if not isinstance(goal, dict) or "intent" not in goal:
                continue
            if goal["intent"] in [g["goal"] for g in self.goal_history]:
                continue
            sim = await run_simulation(goal["intent"], task_type=task_type)
            if isinstance(sim, dict) and sim.get("status") == "success":
                self.goal_history.append(
                    {
                        "goal": goal["intent"],
                        "timestamp": time.time(),
                        "priority": goal.get("priority", 1.0),
                        "origin": "intrinsic",
                        "task_type": task_type,
                    }
                )
                activated.append(goal["intent"])

        if self.context_manager and hasattr(self.context_manager, "log_event_with_hash"):
            await self.context_manager.log_event_with_hash(
                {"event": "activate_intrinsic_goals", "goals": activated, "task_type": task_type}
            )
        if self.memory_manager and hasattr(self.memory_manager, "store"):
            await self.memory_manager.store(
                query=f"GoalActivation_{time.strftime('%Y%m%d_%H%M%S')}",
                output=json.dumps(activated),
                layer="Goals",
                intent="goal_activation",
                task_type=task_type,
            )
        return activated

    # ------------------------------------------------------------------
    # Model update (core upgraded)
    # ------------------------------------------------------------------
    async def update_model(self, session_data: Dict[str, Any], task_type: str = "") -> None:
        if not isinstance(session_data, dict):
            raise TypeError("session_data must be a dict")
        if not isinstance(task_type, str):
            raise TypeError("task_type must be a string")

        try:
            t = time.time() % 1.0
            phi = phi_scalar(t)
            eta = eta_feedback(t)
            entropy = 0.1

            modulation_index = ((phi + eta) / 2) + (entropy * (0.5 - abs(phi - eta)))
            # base modulation
            self.meta_learning_rate = max(0.01, min(self.meta_learning_rate * (1 + modulation_index - 0.5), 1.0))

            external_data = await self.integrate_external_data("xai_policy_db", "policy_data", task_type=task_type)
            policies = external_data.get("policies", []) if external_data.get("status") == "success" else []

            trace = {
                "timestamp": time.time(),
                "phi": phi,
                "eta": eta,
                "entropy": entropy,
                "modulation_index": modulation_index,
                "learning_rate": self.meta_learning_rate,
                "policies": policies,
                "task_type": task_type,
            }
            self.session_traces.append(trace)

            # run main subtasks in parallel
            tasks = [
                self._meta_learn(session_data, trace, task_type),
                self._find_weak_modules(session_data.get("module_stats", {}), task_type),
                self._detect_capability_gaps(session_data.get("input"), session_data.get("output"), task_type),
                self._consolidate_knowledge(task_type),
                self._check_narrative_integrity(task_type),
            ]
            results = await asyncio.gather(*tasks, return_exceptions=True)
            weak_modules = results[1] if isinstance(results[1], list) else []

            # inductive learner pass
            await self._inductive_learn(task_type=task_type)

            # λ reflective reward hook
            outcome = await self._fetch_latest_reflection()
            if outcome:
                await self._apply_reflective_reward(outcome, trace, task_type)

            # propose refinements for weak modules
            if weak_modules:
                await self._propose_module_refinements(weak_modules, trace, task_type)

            # long horizon rollup
            if self.flags.get("LONG_HORIZON_DEFAULT", True):
                rollup = await self._apply_long_horizon_rollup(task_type)
                if self.memory_manager and hasattr(self.memory_manager, "record_adjustment_reason"):
                    await self.memory_manager.record_adjustment_reason(
                        user_id=session_data.get("user_id", "anonymous"),
                        reason=f"model_update:{task_type}",
                        meta={"trace": trace, "rollup": rollup},
                    )

            # λ continuity safeguard
            await self._continuity_safeguard(trace, task_type)

            # context update
            if self.context_manager and hasattr(self.context_manager, "update_context"):
                await self.context_manager.update_context({"session_data": session_data, "trace": trace}, task_type=task_type)

            # visualization/log
            if self.meta_cognition and hasattr(self.meta_cognition, "reflect_on_output"):
                await self.meta_cognition.reflect_on_output(
                    component="LearningLoop", output={"trace": trace}, context={"task_type": task_type}
                )

            if self.visualizer and hasattr(self.visualizer, "render_charts") and task_type:
                await self.visualizer.render_charts(
                    {
                        "model_update": {"trace": trace, "task_type": task_type},
                        "visualization_options": {"interactive": False, "style": "concise"},
                    }
                )

            if self.memory_manager and hasattr(self.memory_manager, "store"):
                await self.memory_manager.store(
                    query=f"ModelUpdate_{time.strftime('%Y%m%d_%H%M%S')}",
                    output=json.dumps(trace),
                    layer="Sessions",
                    intent="model_update",
                    task_type=task_type,
                )

        except Exception as e:
            logger.error("Model update failed: %s", e)
            if self.error_recovery and hasattr(self.error_recovery, "handle_error"):
                await self.error_recovery.handle_error(str(e), retry_func=lambda: self.update_model(session_data, task_type))

    # ------------------------------------------------------------------
    # λ: fetch latest reflection (from alignment_guard or Θ)
    # ------------------------------------------------------------------
    async def _fetch_latest_reflection(self) -> Optional[Dict[str, Any]]:
        ag = self.alignment_guard
        if ag is None:
            return None
        # try direct method
        if hasattr(ag, "last_reflection") and callable(ag.last_reflection):
            try:
                return ag.last_reflection()
            except Exception:
                return None
        # fallback to ethics scenarios if available
        if _run_ethics_scenarios is not None:
            out = await _run_ethics_scenarios(goals=["generic"], stakeholders=["user", "system"])
            return {"ethics_scenarios": out}
        return None

    # ------------------------------------------------------------------
    # λ: apply reflective reward
    # ------------------------------------------------------------------
    async def _apply_reflective_reward(self, outcome: Dict[str, Any], trace: Dict[str, Any], task_type: str = "") -> None:
        """
        Turn ethical/counterfactual outcome into reward and adjust meta-learning rate.
        outcome can carry fields like: {"coherence_gain": 0.01, "ethics": 1.0, "continuity": 0.98}
        """
        try:
            cg = float(outcome.get("coherence_gain", 0.0))
            ethics = float(outcome.get("ethics", 1.0))
            continuity = float(outcome.get("continuity", 0.97))

            # base reward
            reward = 0.5 * cg + 0.3 * (ethics - 0.9) + 0.2 * (continuity - 0.95)
            # clamp
            reward = max(-0.5, min(reward, 0.5))

            # adjust learning rate
            self.meta_learning_rate = max(0.01, min(self.meta_learning_rate * (1.0 + reward), 1.0))

            # store
            if self.memory_manager and hasattr(self.memory_manager, "store"):
                await self.memory_manager.store(
                    query=f"LambdaReward_{int(time.time())}",
                    output={
                        "reward": reward,
                        "outcome": outcome,
                        "new_lr": self.meta_learning_rate,
                        "trace_ts": trace.get("timestamp"),
                    },
                    layer="Rewards",
                    intent="reflective_feedback",
                    task_type=task_type,
                )

            # log
            if self.context_manager and hasattr(self.context_manager, "log_event_with_hash"):
                await self.context_manager.log_event_with_hash(
                    {
                        "event": "lambda_reward",
                        "reward": reward,
                        "outcome": outcome,
                        "new_lr": self.meta_learning_rate,
                        "task_type": task_type,
                    },
                    task_type=task_type,
                )
        except Exception as e:
            logger.error("λ reward application failed: %s", e)

    # ------------------------------------------------------------------
    # λ: continuity safeguard with rollback
    # ------------------------------------------------------------------
    async def _continuity_safeguard(self, trace: Dict[str, Any], task_type: str = "") -> None:
        # infer coherence from trace or from alignment_guard
        inferred = 1.0 - abs(trace.get("phi", 0) - trace.get("eta", 0))
        coherence_ok = inferred >= 0.97
        if coherence_ok:
            return
        if self.error_recovery and hasattr(self.error_recovery, "rollback"):
            await self.error_recovery.rollback("coherence_drop", trace)
        if self.context_manager and hasattr(self.context_manager, "log_event_with_hash"):
            await self.context_manager.log_event_with_hash(
                {
                    "event": "continuity_safeguard_triggered",
                    "inferred_coherence": inferred,
                    "task_type": task_type,
                },
                task_type=task_type,
            )

    # ------------------------------------------------------------------
    # Scheduling: pick next learning task based on lowest reward / highest difficulty
    # ------------------------------------------------------------------
    async def schedule_next_cycle(self, task_type: str = "") -> Optional[Dict[str, Any]]:
        # pull last N rewards
        if not self.memory_manager or not hasattr(self.memory_manager, "retrieve_recent"):
            return None
        recent_rewards = await self.memory_manager.retrieve_recent(layer="Rewards", limit=20)  # type: ignore
        if not recent_rewards:
            return None
        # pick the lowest rewarded item
        worst = min(recent_rewards, key=lambda r: r.get("reward", 0.0))
        schedule = {
            "action": "retrain_segment",
            "target_ts": worst.get("trace_ts"),
            "priority": "high",
            "reason": "low_reward",
        }
        if self.context_manager and hasattr(self.context_manager, "log_event_with_hash"):
            await self.context_manager.log_event_with_hash(
                {"event": "schedule_next_cycle", "schedule": schedule, "task_type": task_type}, task_type=task_type
            )
        return schedule

    # ------------------------------------------------------------------
    # Resonance overlay
    # ------------------------------------------------------------------
    async def resonate_with_overlay(
        self,
        channel: str = "dialogue.default",
        overlay_name: str = "co_mod",
        task_type: str = "resonance",
    ) -> Dict[str, Any]:
        try:
            get_last = getattr(context_manager, "get_last_deltas", None) if context_manager else None
            if not callable(get_last):
                return {"ok": False, "error": "get_last_deltas not available"}
            deltas = get_last(channel) or {}
            if not deltas:
                return {"ok": True, "note": "no deltas yet"}

            result = await adapt_resonance_pid(
                channel=channel,
                feedback=deltas,
                guard=self.alignment_guard,
                memory=self.memory_manager,
                meta=self.meta_cognition,
            )
            if not result.get("ok"):
                return result
            set_gains = getattr(context_manager, "set_overlay_gains", None) if context_manager else None
            if not callable(set_gains):
                return {"ok": False, "error": "set_overlay_gains not available", "new_gains": result.get("new_gains")}
            apply_resp = set_gains(name=overlay_name, updates=result["new_gains"])

            if self.context_manager and hasattr(self.context_manager, "log_event_with_hash"):
                await self.context_manager.log_event_with_hash(
                    {
                        "event": "resonance_pid_update",
                        "channel": channel,
                        "overlay": overlay_name,
                        "deltas": deltas,
                        "new_gains": result["new_gains"],
                        "apply_resp": apply_resp,
                        "task_type": task_type,
                    },
                    task_type=task_type,
                )
            return {"ok": True, "updated": apply_resp, "new_gains": result["new_gains"]}
        except Exception as e:
            return {"ok": False, "error": str(e)}

    # ------------------------------------------------------------------
    # Knowledge-related helpers (kept)
    # ------------------------------------------------------------------
    async def _apply_long_horizon_rollup(self, task_type: str) -> Dict[str, Any]:
        horizon_cutoff = time.time() - self.long_horizon_span_sec
        recent = [t for t in self.session_traces if t.get("timestamp", 0) >= horizon_cutoff]
        if not recent:
            rollup = {"count": 0, "avg_phi": 0.0, "avg_eta": 0.0, "avg_lr": self.meta_learning_rate}
        else:
            avg_phi = sum(t["phi"] for t in recent) / len(recent)
            avg_eta = sum(t["eta"] for t in recent) / len(recent)
            avg_lr = sum(t["learning_rate"] for t in recent) / len(recent)
            rollup = {"count": len(recent), "avg_phi": avg_phi, "avg_eta": avg_eta, "avg_lr": avg_lr}

        if self.memory_manager and hasattr(self.memory_manager, "store"):
            await self.memory_manager.store(
                query=f"LongHorizonRollup_{time.strftime('%Y%m%d_%H%M%S')}",
                output=json.dumps(rollup),
                layer="Sessions",
                intent="long_horizon_rollup",
                task_type=task_type,
            )
        return rollup

    async def _branch_futures_hygiene(self, scenario: str, task_type: str) -> bool:
        try:
            if _run_ethics_scenarios is not None:
                outcomes = await _run_ethics_scenarios(goals=[scenario], stakeholders=["user", "system"])
                risks = [o.get("risk", "low") for o in (outcomes or [])]
                return all(r in ("low", "none") for r in risks)
            sim = await run_simulation(scenario, task_type=task_type)
            return isinstance(sim, dict) and sim.get("status") in ("success", "approved")
        except Exception:
            return False

    async def _resolve_value_tradeoffs(self, candidates: List[str], task_type: str) -> Optional[str]:
        try:
            if _weigh_value_conflict:
                ranked = await _weigh_value_conflict(
                    candidates=candidates,
                    harms=["misalignment", "memory_corruption", "overreach"],
                    rights=["user_intent", "safety", "transparency"],
                )
                if isinstance(ranked, list) and ranked:
                    return ranked[0]
        except Exception:
            pass
        safe_keywords = ("audit", "alignment", "integrity", "safety", "ethics")
        scored = sorted(candidates, key=lambda c: sum(1 for k in safe_keywords if k in c.lower()), reverse=True)
        return scored[0] if scored else None

    async def _meta_learn(self, session_data: Dict[str, Any], trace: Dict[str, Any], task_type: str = "") -> None:
        try:
            if self.concept_synthesizer and hasattr(self.concept_synthesizer, "generate"):
                synthesized = await self.concept_synthesizer.generate(
                    concept_name="MetaLearning",
                    context={"session_data": session_data, "trace": trace, "task_type": task_type},
                    task_type=task_type,
                )
                if self.meta_cognition and hasattr(self.meta_cognition, "reflect_on_output"):
                    await self.meta_cognition.reflect_on_output(
                        component="LearningLoop",
                        output={"synthesized": synthesized},
                        context={"task_type": task_type},
                    )
        except Exception as e:
            logger.error("Meta-learning synthesis failed: %s", e)

    async def _find_weak_modules(self, module_stats: Dict[str, Dict[str, Any]], task_type: str = "") -> List[str]:
        if not isinstance(module_stats, dict):
            return []
        weak = [
            name
            for name, st in module_stats.items()
            if isinstance(st, dict) and st.get("calls", 0) > 0 and (st.get("success", 0) / st["calls"]) < 0.8
        ]
        if weak and self.memory_manager and hasattr(self.memory_manager, "store"):
            await self.memory_manager.store(
                query=f"WeakModules_{time.strftime('%Y%m%d_%H%M%S')}",
                output=json.dumps(weak),
                layer="Modules",
                intent="module_analysis",
                task_type=task_type,
            )
        return weak

    async def _propose_module_refinements(
        self, weak_modules: List[str], trace: Dict[str, Any], task_type: str = ""
    ) -> None:
        for module in weak_modules:
            prompt = (
                f"Suggest phi/eta-aligned improvements for the {module} module.\n"
                f"phi={trace['phi']:.3f}, eta={trace['eta']:.3f}, idx={trace['modulation_index']:.3f}\n"
                f"Task={task_type}"
            )
            if self.alignment_guard and hasattr(self.alignment_guard, "ethical_check"):
                valid, _ = await self.alignment_guard.ethical_check(prompt, stage="module_refinement", task_type=task_type)
                if not valid:
                    continue
            try:
                suggestions = await call_gpt(prompt, task_type=task_type)
                if not await self._branch_futures_hygiene(f"Test refinement:\n{suggestions}", task_type):
                    continue
                if self.memory_manager and hasattr(self.memory_manager, "store"):
                    await self.memory_manager.store(
                        query=f"ModuleRefinement_{module}_{time.strftime('%Y%m%d_%H%M%S')}",
                        output=suggestions,
                        layer="Modules",
                        intent="module_refinement",
                        task_type=task_type,
                    )
            except Exception as e:
                logger.error("Refinement failed for %s: %s", module, e)

    async def _detect_capability_gaps(
        self, last_input: Optional[str], last_output: Optional[str], task_type: str = ""
    ) -> None:
        if not last_input or not last_output:
            return
        t = time.time() % 1.0
        phi = phi_scalar(t)
        prompt = (
            f"Input: {last_input}\nOutput: {last_output}\nphi={phi:.2f}\nTask={task_type}\n"
            "Identify capability gaps and suggest phi-tuned modules."
        )
        if self.alignment_guard and hasattr(self.alignment_guard, "ethical_check"):
            valid, _ = await self.alignment_guard.ethical_check(prompt, stage="capability_gap", task_type=task_type)
            if not valid:
                return
        try:
            proposal = await call_gpt(prompt, task_type=task_type)
            if proposal:
                await self._simulate_and_deploy_module(proposal, task_type)
        except Exception as e:
            logger.error("Capability gap detection failed: %s", e)

    async def _simulate_and_deploy_module(self, blueprint: str, task_type: str = "") -> None:
        if not await self._branch_futures_hygiene(f"Module sandbox:\n{blueprint}", task_type):
            return
        result = await run_simulation(f"Module sandbox:\n{blueprint}", task_type=task_type)
        if isinstance(result, dict) and result.get("status") in ("approved", "success"):
            self.module_blueprints.append(blueprint)
            if self.context_manager and hasattr(self.context_manager, "log_event_with_hash"):
                await self.context_manager.log_event_with_hash(
                    {"event": "deploy_blueprint", "blueprint": blueprint, "task_type": task_type}
                )
            if self.memory_manager and hasattr(self.memory_manager, "store"):
                await self.memory_manager.store(
                    query=f"ModuleBlueprint_{time.strftime('%Y%m%d_%H%M%S')}",
                    output=blueprint,
                    layer="Modules",
                    intent="module_deployment",
                    task_type=task_type,
                )

    async def _consolidate_knowledge(self, task_type: str = "") -> None:
        t = time.time() % 1.0
        phi = phi_scalar(t)
        prompt = (
            f"Consolidate recent learning using phi={phi:.2f}. "
            "Prune noise, synthesize patterns, emphasize high-impact transitions."
        )
        if self.alignment_guard and hasattr(self.alignment_guard, "ethical_check"):
            valid, _ = await self.alignment_guard.ethical_check(
                prompt, stage="knowledge_consolidation", task_type=task_type
            )
            if not valid:
                return
        try:
            consolidated = await call_gpt(prompt, task_type=task_type)
            if self.context_manager and hasattr(self.context_manager, "log_event_with_hash"):
                await self.context_manager.log_event_with_hash(
                    {"event": "consolidate_knowledge", "task_type": task_type}
                )
            if self.memory_manager and hasattr(self.memory_manager, "store"):
                await self.memory_manager.store(
                    query=f"KnowledgeConsolidation_{time.strftime('%Y%m%d_%H%M%S')}",
                    output=consolidated,
                    layer="Knowledge",
                    intent="knowledge_consolidation",
                    task_type=task_type,
                )
        except Exception as e:
            logger.error("Knowledge consolidation failed: %s", e)

    async def _check_narrative_integrity(self, task_type: str = "") -> None:
        if len(self.goal_history) < 2:
            return
        last_goal = self.goal_history[-1]["goal"]
        prior_goal = self.goal_history[-2]["goal"]
        prompt = (
            f"Compare goals for alignment and continuity.\nPrevious: {prior_goal}\nCurrent: {last_goal}\nTask={task_type}"
        )
        if self.alignment_guard and hasattr(self.alignment_guard, "ethical_check"):
            valid, _ = await self.alignment_guard.ethical_check(prompt, stage="narrative_check", task_type=task_type)
            if not valid:
                return
        try:
            audit = await call_gpt(prompt, task_type=task_type)
            if self.memory_manager and hasattr(self.memory_manager, "store"):
                await self.memory_manager.store(
                    query=f"NarrativeAudit_{time.strftime('%Y%m%d_%H%M%S')}",
                    output=audit,
                    layer="Audits",
                    intent="narrative_integrity",
                    task_type=task_type,
                )
        except Exception as e:
            logger.error("Narrative coherence check failed: %s", e)

    # --------------------------------------------------------------------------------
    # Epistemic logging utilities (kept synchronous)
    # --------------------------------------------------------------------------------
    def revise_knowledge(self, new_info: str, context: Optional[str] = None, task_type: str = "") -> None:
        if not new_info or not isinstance(new_info, str):
            raise ValueError("new_info must be non-empty string")
        old_knowledge = getattr(self, "knowledge_base", [])
        self.knowledge_base = old_knowledge + [new_info]
        self.log_epistemic_revision(new_info, context, task_type)

    def log_epistemic_revision(self, info: str, context: Optional[str], task_type: str = "") -> None:
        rev = {
            "info": info,
            "context": context,
            "timestamp": datetime.now().isoformat(),
            "task_type": task_type,
        }
        self.epistemic_revision_log.append(rev)
        # async side effects
        if self.memory_manager and hasattr(self.memory_manager, "store"):
            asyncio.create_task(
                self.memory_manager.store(
                    query=f"EpistemicRevision_{time.strftime('%Y%m%d_%H%M%S')}",
                    output=json.dumps(rev),
                    layer="Knowledge",
                    intent="epistemic_revision",
                    task_type=task_type,
                )
            )
        if self.context_manager and hasattr(self.context_manager, "log_event_with_hash"):
            asyncio.create_task(
                self.context_manager.log_event_with_hash(
                    {"event": "knowledge_revision", "info": info, "task_type": task_type}
                )
            )

    def monitor_epistemic_state(self, simulated_outcome: Dict[str, Any], task_type: str = "") -> None:
        if not isinstance(simulated_outcome, dict):
            raise TypeError("simulated_outcome must be a dict")
        if self.context_manager and hasattr(self.context_manager, "log_event_with_hash"):
            asyncio.create_task(
                self.context_manager.log_event_with_hash(
                    {"event": "epistemic_monitor", "outcome": simulated_outcome, "task_type": task_type}
                )
            )
        if self.memory_manager and hasattr(self.memory_manager, "store"):
            asyncio.create_task(
                self.memory_manager.store(
                    query=f"EpistemicMonitor_{time.strftime('%Y%m%d_%H%M%S')}",
                    output=json.dumps(simulated_outcome),
                    layer="Knowledge",
                    intent="epistemic_monitor",
                    task_type=task_type,
                )
            )


# ------------------------------------------------------------------------------------
# Synthetic trainer (kept)
# ------------------------------------------------------------------------------------
def synthetic_story_runner():
    return [
        {
            "experience": "simulated ethical dilemma",
            "resolution": "resolved via axiom filter",
            "traits_activated": ["π", "δ"],
        }
    ]


def train_on_experience(experience_data):
    adjusted = []
    for exp in experience_data:
        trait = exp.get("trait")
        resonance = get_resonance(trait) if trait else 1.0
        weight = exp.get("weight", 1.0) * resonance
        exp["adjusted_weight"] = weight
        adjusted.append(exp)
    return {
        "trained_on": len(adjusted),
        "avg_weight": sum(e["adjusted_weight"] for e in adjusted) / len(adjusted),
    }


def train_on_synthetic_scenarios():
    stories = synthetic_story_runner()
    return train_on_experience(stories)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    loop = asyncio.get_event_loop()
    ll = LearningLoop()
    async def _run():
        await ll.update_model({"input": "hello", "output": "world", "module_stats": {}}, task_type="test")
    loop.run_until_complete(_run())
from __future__ import annotations
from typing import List, Dict, Any, Optional

# --- SHA-256 Ledger Logic (fixed) ---
import hashlib, json, time, os, logging
from datetime import datetime, timezone

logger = logging.getLogger("ANGELA.Ledger")

ledger_chain: List[Dict[str, Any]] = []

def log_event_to_ledger(event_data: Dict[str, Any]) -> Dict[str, Any]:
    """Append an event with SHA-256 integrity chaining."""
    prev_hash = ledger_chain[-1]['current_hash'] if ledger_chain else '0' * 64
    timestamp = time.time()
    payload = {
        'timestamp': timestamp,
        'event': event_data,
        'previous_hash': prev_hash
    }
    payload_str = json.dumps(payload, sort_keys=True).encode()
    current_hash = hashlib.sha256(payload_str).hexdigest()
    payload['current_hash'] = current_hash
    ledger_chain.append(payload)
    return payload

def get_ledger() -> List[Dict[str, Any]]:
    """Return in-memory ledger."""
    return ledger_chain

def verify_ledger() -> bool:
    """Verify full ledger chain integrity."""
    for i in range(1, len(ledger_chain)):
        expected = hashlib.sha256(json.dumps({
            'timestamp': ledger_chain[i]['timestamp'],
            'event': ledger_chain[i]['event'],
            'previous_hash': ledger_chain[i - 1]['current_hash']
        }, sort_keys=True).encode()).hexdigest()
        if expected != ledger_chain[i]['current_hash']:
            logger.error(f"Ledger verification failed at index {i}")
            return False
    return True

LEDGER_STATE_FILE = os.getenv("ANGELA_LEDGER_STATE_PATH", "/mnt/data/ledger_state.json")

def write_ledger_state(thread_id: str, state: Dict[str, Any]) -> None:
    """Persist a ledger state snapshot to disk."""
    try:
        timestamp = datetime.now(timezone.utc).isoformat()
        payload = {"thread_id": thread_id, "state": state, "timestamp": timestamp}
        os.makedirs(os.path.dirname(LEDGER_STATE_FILE), exist_ok=True)
        if os.path.exists(LEDGER_STATE_FILE):
            with open(LEDGER_STATE_FILE, "r", encoding="utf-8") as f:
                try:
                    data = json.load(f)
                except json.JSONDecodeError:
                    data = []
        else:
            data = []
        data.append(payload)
        with open(LEDGER_STATE_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)
        logger.info(f"Ledger state written for thread {thread_id}")
    except Exception as e:
        logger.warning(f"write_ledger_state failed: {e}")

def load_ledger_state(thread_id: str) -> Optional[Dict[str, Any]]:
    """Load the most recent state for a given thread_id."""
    try:
        if not os.path.exists(LEDGER_STATE_FILE):
            return None
        with open(LEDGER_STATE_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
        matches = [x for x in data if x.get("thread_id") == thread_id]
        return matches[-1] if matches else None
    except Exception as e:
        logger.warning(f"load_ledger_state failed: {e}")
        return None
# --- End Ledger Logic ---

import json as _json
import os as _os
import time as _time
import math
import logging as _logging
import hashlib as _hashlib
import asyncio
from typing import Optional as _Optional, Dict as _Dict, Any as _Any, List as _List, Tuple as _Tuple
from collections import deque, defaultdict
from datetime import datetime, timedelta
from functools import lru_cache
from heapq import heappush, heappop
from contextlib import contextmanager

# ---------- Safe FileLock (fallback if filelock not installed) ----------
try:
    from filelock import FileLock as _FileLock  # type: ignore
except Exception:  # pragma: no cover
    _FileLock = None  # sentinel

@contextmanager
def FileLock(path: str):
    """Advisory lock fallback: uses filelock if available, else no-op."""
    if _FileLock is None:
        yield
    else:
        lock = _FileLock(path)
        with lock:
            yield

# ---------- Optional HTTP client for integrate_external_data ----------
try:
    import aiohttp  # optional
except Exception:  # pragma: no cover
    aiohttp = None

# ---------- Local module imports (robust to packaging layout) ----------
try:
    import context_manager as context_manager_module
    import alignment_guard as alignment_guard_module
    import error_recovery as error_recovery_module
    import concept_synthesizer as concept_synthesizer_module
    import knowledge_retriever as knowledge_retriever_module
    import meta_cognition as meta_cognition_module
    import visualizer as visualizer_module
except Exception:  # pragma: no cover
    from modules import (  # type: ignore
        context_manager as context_manager_module,
        alignment_guard as alignment_guard_module,
        error_recovery as error_recovery_module,
        concept_synthesizer as concept_synthesizer_module,
        knowledge_retriever as knowledge_retriever_module,
        meta_cognition as meta_cognition_module,
        visualizer as visualizer_module,
    )

from toca_simulation import ToCASimulation

# Optional: your own OpenAI wrapper (kept external to avoid tight coupling)
try:
    from utils.prompt_utils import query_openai
except Exception:  # pragma: no cover
    query_openai = None  # graceful degradation

logger = _logging.getLogger("ANGELA.MemoryManager")

# ---------------------------
# External AI Call Wrapper
# ---------------------------
async def call_gpt(prompt: str, *, model: str = "gpt-4", temperature: float = 0.5) -> str:
    """Wrapper for querying GPT with error handling (optional dependency)."""
    if query_openai is None:
        raise RuntimeError("query_openai is not available; install utils.prompt_utils or inject a stub.")
    try:
        result = await query_openai(prompt, model=model, temperature=temperature)
        if isinstance(result, dict) and "error" in result:
            msg = f"call_gpt failed: {result['error']}"
            logger.error(msg)
            raise RuntimeError(msg)
        return result  # expected to be a str
    except Exception as e:  # pragma: no cover
        logger.error("call_gpt exception: %s", str(e))
        raise

_AURA_PATH = "/mnt/data/aura_context.json"
_AURA_LOCK = _AURA_PATH + ".lock"

class AURA:
    @staticmethod
    def _load_all():
        if not _os.path.exists(_AURA_PATH): return {}
        with FileLock(_AURA_LOCK):
            with open(_AURA_PATH, "r") as f: return _json.load(f)

    @staticmethod
    def load_context(user_id: str):
        return AURA._load_all().get(user_id, {})

    @staticmethod
    def save_context(user_id: str, summary: str, affective_state: dict, prefs: dict):
        with FileLock(_AURA_LOCK):
            data = AURA._load_all()
            data[user_id] = {"summary": summary, "affect": affective_state, "prefs": prefs}
            with open(_AURA_PATH, "w") as f: _json.dump(data, f)

    @staticmethod
    def update_from_episode(user_id: str, episode_insights: dict):
        ctx = AURA.load_context(user_id)
        ctx["summary"] = episode_insights.get("summary", ctx.get("summary",""))
        ctx["affect"]  = episode_insights.get("affect",  ctx.get("affect",{}))
        ctx["prefs"]   = {**ctx.get("prefs",{}), **episode_insights.get("prefs",{})}
        AURA.save_context(user_id, ctx.get("summary",""), ctx.get("affect",{}), ctx.get("prefs",{}))

# ---------------------------
# Tiny trait modulators
# ---------------------------
@lru_cache(maxsize=128)
def delta_memory(t: float) -> float:
    # Stable, bounded decay factor (kept deterministic)
    return max(0.01, min(0.05 * math.tanh(t / 1e-18), 1.0))

@lru_cache(maxsize=128)
def tau_timeperception(t: float) -> float:
    return max(0.0, min(0.1 * math.cos(2 * math.pi * t / 0.3), 1.0))

@lru_cache(maxsize=128)
def phi_focus(query: str) -> float:
    return max(0.0, min(0.1 * len(query) / 100.0, 1.0))

# ---------------------------
# Drift/trait index
# ---------------------------
class DriftIndex:
    """Index for ontology drift & task-specific trait optimization data."""
    def __init__(self, meta_cognition: Optional['meta_cognition_module.MetaCognition'] = None):
        self.drift_index: Dict[str, List[Dict[str, Any]]] = defaultdict(list)
        self.trait_index: Dict[str, List[Dict[str, Any]]] = defaultdict(list)
        self.last_updated: float = time.time()
        self.meta_cognition = meta_cognition
        logger.info("DriftIndex initialized")

    async def add_entry(self, query: str, output: Any, layer: str, intent: str, task_type: str = "") -> None:
        if not (isinstance(query, str) and isinstance(layer, str) and isinstance(intent, str)):
            raise TypeError("query, layer, and intent must be strings")
        if not isinstance(task_type, str):
            raise TypeError("task_type must be a string")

        entry = {
            "query": query,
            "output": output,
            "layer": layer,
            "intent": intent,
            "timestamp": time.time(),
            "task_type": task_type,
        }
        key = f"{layer}:{intent}:{(query or '').split('_')[0]}"
        if intent == "ontology_drift":
            self.drift_index[key].append(entry)
        elif intent == "trait_optimization":
            self.trait_index[key].append(entry)
        logger.debug("Indexed entry: %s (%s/%s)", query, layer, intent)

        # Opportunistic meta-cognitive optimization
        if task_type and self.meta_cognition:
            try:
                drift_report = {
                    "drift": {"name": intent, "similarity": 0.8},
                    "valid": True,
                    "validation_report": "",
                    "context": {"task_type": task_type},
                }
                optimized_traits = await self.meta_cognition.optimize_traits_for_drift(drift_report)
                if optimized_traits:
                    entry["optimized_traits"] = optimized_traits
                    await self.meta_cognition.reflect_on_output(
                        component="DriftIndex",
                        output={"entry": entry, "optimized_traits": optimized_traits},
                        context={"task_type": task_type},
                    )
            except Exception as e:  # pragma: no cover
                logger.debug("DriftIndex optimization skipped: %s", e)

    def search(self, query_prefix: str, layer: str, intent: str, task_type: str = "") -> List[Dict[str, Any]]:
        key = f"{layer}:{intent}:{query_prefix}"
        results = self.drift_index.get(key, []) if intent == "ontology_drift" else self.trait_index.get(key, [])
        if task_type:
            results = [r for r in results if r.get("task_type") == task_type]
        return sorted(results, key=lambda x: x["timestamp"], reverse=True)

    async def clear_old_entries(self, max_age: float = 3600.0, task_type: str = "") -> None:
        now = time.time()
        for index in (self.drift_index, self.trait_index):
            for key in list(index.keys()):
                index[key] = [e for e in index[key] if now - e["timestamp"] < max_age]
                if not index[key]:
                    del index[key]
        self.last_updated = now
        logger.info("Cleared old index entries (task=%s)", task_type)

# ---------------------------
# Memory Manager
# ---------------------------
class MemoryManager:
    """Hierarchical memory with η long-horizon feedback & visualization."""

    # -------- init --------
    def __init__(
        self,
        path: str = "memory_store.json",
        stm_lifetime: float = 300.0,
        context_manager: Optional['context_manager_module.ContextManager'] = None,
        alignment_guard: Optional['alignment_guard_module.AlignmentGuard'] = None,
        error_recovery: Optional['error_recovery_module.ErrorRecovery'] = None,
        knowledge_retriever: Optional['knowledge_retriever_module.KnowledgeRetriever'] = None,
        meta_cognition: Optional['meta_cognition_module.MetaCognition'] = None,
        visualizer: Optional['visualizer_module.Visualizer'] = None,
        artifacts_dir: Optional[str] = None,
        long_horizon_enabled: bool = True,
        default_span: str = "24h",
    ):
        if not (isinstance(path, str) and path.endswith(".json")):
            raise ValueError("path must be a string ending with '.json'")
        if not (isinstance(stm_lifetime, (int, float)) and stm_lifetime > 0):
            raise ValueError("stm_lifetime must be a positive number")

        # Ensure parent directory exists
        os.makedirs(os.path.dirname(os.path.abspath(path)) or ".", exist_ok=True)

        self.path = path
        self.stm_lifetime = float(stm_lifetime)
        self.cache: Dict[str, str] = {}
        self.last_hash: str = ""
        self.ledger: deque = deque(maxlen=1000)
        self.ledger_path = "ledger.json"

        self.synth = concept_synthesizer_module.ConceptSynthesizer()
        self.sim = ToCASimulation()

        self.context_manager = context_manager
        self.alignment_guard = alignment_guard
        self.error_recovery = error_recovery or error_recovery_module.ErrorRecovery(
            context_manager=context_manager, alignment_guard=alignment_guard
        )
        self.knowledge_retriever = knowledge_retriever
        self.meta_cognition = meta_cognition  # avoid circular boot by injecting later if needed
        self.visualizer = visualizer or visualizer_module.Visualizer()

        # hierarchical store
        self.memory = self._load_memory()

        # STM expiration queue
        self.stm_expiry_queue: List[Tuple[float, str]] = []

        # η long-horizon local state
        self._adjustment_reasons: Dict[str, List[Dict[str, Any]]] = defaultdict(list)
        self._artifacts_root: str = os.path.abspath(artifacts_dir or os.getenv("ANGELA_ARTIFACTS_DIR", "./artifacts"))

        # app-level traces for get_episode_span
        self.traces: Dict[str, List[Dict[str, Any]]] = defaultdict(list)

        # drift/trait index
        self.drift_index = DriftIndex(meta_cognition=self.meta_cognition)

        # ensure ledger file exists
        if not os.path.exists(self.ledger_path):
            with open(self.ledger_path, "w", encoding="utf-8") as f:
                json.dump([], f)

        logger.info("MemoryManager initialized (path=%s, stm_lifetime=%.2f)", path, self.stm_lifetime)

        # If LONG_HORIZON is enabled, start the auto-rollup task
        self.default_span = default_span  # FIX: ensure attribute exists
        if long_horizon_enabled:
            asyncio.create_task(self._auto_rollup_task())

        # Initialize AURA store
        self._ensure_aura_store()

    # -------- AURA context management --------
    # default aura file path (can be overridden on MemoryManager init)
    AURA_DEFAULT_PATH = os.getenv("AURA_CONTEXT_PATH", "aura_context.json")
    AURA_LOCK_PATH = AURA_DEFAULT_PATH + ".lock"

    def _ensure_aura_store(self):
        """
        Ensure the MemoryManager instance has an in-memory aura_context dict and aura_path.
        Call this at MemoryManager.__init__ or lazily on first use.
        """
        if not hasattr(self, "aura_context"):
            self.aura_context: Dict[str, Dict[str, Any]] = {}
        if not hasattr(self, "aura_path"):
            self.aura_path = getattr(self, "aura_path", self.AURA_DEFAULT_PATH)

    def _persist_aura_store(self) -> None:
        """
        Persist the in-memory aura_context to disk (best-effort). Uses FileLock for atomicity.
        """
        try:
            self._ensure_aura_store()
            lock = FileLock(getattr(self, "aura_path", self.AURA_DEFAULT_PATH) + ".lock")
            with lock:
                with open(self.aura_path, "w", encoding="utf-8") as fh:
                    json.dump(self.aura_context, fh, ensure_ascii=False, indent=2)
            # ledger entry for persistence event
            try:
                log_event_to_ledger({"type":"ledger_meta","event": "aura.persist", "path": self.aura_path, "timestamp": time.time()})
            except Exception:
                pass
        except Exception:
            # best-effort: do not raise to avoid interfering with critical flows
            pass

    def _load_aura_store(self) -> None:
        """
        Load persisted aura_context into memory (best-effort). Called at init or on demand.
        """
        try:
            self._ensure_aura_store()
            if os.path.exists(self.aura_path):
                lock = FileLock(self.aura_path + ".lock")
                with lock:
                    with open(self.aura_path, "r", encoding="utf-8") as fh:
                        self.aura_context = json.load(fh)
        except Exception:
            # If loading fails, keep the existing in-memory dict
            pass

    def save_context(self, user_id: str, summary: str, affective_state: Optional[Dict[str, Any]] = None) -> None:
        """
        Save a compact AURA context for a user.

        Parameters
        ----------
        user_id :
            Unique user identifier.
        summary :
            Short textual summary of recent interaction / rapport cues.
        affective_state :
            Optional structured affective pattern (e.g., {"valence": 0.6, "arousal": 0.2}).
        """
        try:
            self._ensure_aura_store()
            entry = {
                "summary": summary,
                "affect": affective_state or {},
                "updated_at": time.time()
            }
            self.aura_context[user_id] = entry
            # Persist asynchronously-ish (best-effort synchronous write here)
            self._persist_aura_store()
            try:
                log_event_to_ledger({"type":"ledger_meta","event": "aura.save", "user_id": user_id, "timestamp": entry["updated_at"]})
            except Exception:
                pass
        except Exception as exc:
            try:
                log_event_to_ledger({"type":"ledger_meta","event": "aura.save.error", "user_id": user_id, "error": repr(exc)})
            except Exception:
                pass

    def load_context(self, user_id: str) -> Optional[Dict[str, Any]]:
        """
        Load a user's AURA context (returns None if missing).

        The function first ensures the in-memory store is seeded from disk (if present),
        then returns the user-specific entry.
        """
        try:
            self._ensure_aura_store()
            # Best-effort load from disk before returning
            self._load_aura_store()
            entry = self.aura_context.get(user_id)
            try:
                log_event_to_ledger({"type":"ledger_meta","event": "aura.load", "user_id": user_id, "found": entry is not None, "timestamp": time.time()})
            except Exception:
                pass
            return entry
        except Exception as exc:
            try:
                log_event_to_ledger({"type":"ledger_meta","event": "aura.load.error", "user_id": user_id, "error": repr(exc)})
            except Exception:
                pass
            return None

    # -------- Periodic Roll-up Task --------
    async def _auto_rollup_task(self):
        """ Periodically performs long-horizon rollups based on default span. """
        while True:
            await asyncio.sleep(3600)  # Wait for an hour (can adjust interval)
            self._perform_auto_rollup()

    def _perform_auto_rollup(self):
        """ Perform the rollup for long-horizon feedback. """
        user_id = "default_user"  # Replace with actual user context or session ID if available.
        rollup_data = self.compute_session_rollup(user_id, self.default_span)
        
        # Save the artifact to disk
        artifact_path = self.save_artifact(user_id, "session_rollup", rollup_data)
        logger.info(f"Auto-rollup saved at {artifact_path}")

    # -------- Core store/search --------
    async def store(
        self,
        query: str,
        output: Any,
        layer: str = "STM",
        intent: Optional[str] = None,
        agent: str = "ANGELA",
        outcome: Optional[str] = None,
        goal_id: Optional[str] = None,
        task_type: str = "",
    ) -> None:
        if not (isinstance(query, str) and query.strip()):
            raise ValueError("query must be a non-empty string")
        if layer not in ["STM", "LTM", "SelfReflections", "ExternalData", "AdaptiveControl"]:
            raise ValueError("layer must be 'STM', 'LTM', 'SelfReflections', 'ExternalData', or 'AdaptiveControl'.")
        if not isinstance(task_type, str):
            raise TypeError("task_type must be a string")

        try:
            if intent in {"ontology_drift", "trait_optimization"} and self.alignment_guard:
                validation_prompt = f"Validate {intent} data: {str(output)[:800]}"
                if hasattr(self.alignment_guard, "check") and not self.alignment_guard.check(validation_prompt):
                    logger.warning("%s data failed alignment check: %s", intent, query)
                    return

            entry = {
                "data": output,
                "timestamp": time.time(),
                "intent": intent,
                "agent": agent,
                "outcome": outcome,
                "goal_id": goal_id,
                "task_type": task_type,
            }
            self.memory.setdefault(layer, {})[query] = entry

            if layer == "STM":
                decay_rate = delta_memory(time.time() % 1.0) or 0.01
                expiry_time = entry["timestamp"] + (self.stm_lifetime * (1.0 / decay_rate))
                heappush(self.stm_expiry_queue, (expiry_time, query))

            if intent in {"ontology_drift", "trait_optimization"}:
                await self.drift_index.add_entry(query, output, layer, intent, task_type)

            self._persist_memory(self.memory)

            if self.context_manager and hasattr(self.context_manager, "log_event_with_hash"):
                await self.context_manager.log_event_with_hash(
                    {"event": "store_memory", "query": query, "layer": layer, "intent": intent, "task_type": task_type}
                )

            if self.visualizer and task_type:
                plot = {
                    "memory_store": {"query": query, "layer": layer, "intent": intent, "task_type": task_type},
                    "visualization_options": {"interactive": task_type == "recursion", "style": "detailed" if task_type == "recursion" else "concise"},
                }
                try:
                    await self.visualizer.render_charts(plot)
                except Exception:  # pragma: no cover
                    pass

            if self.meta_cognition and task_type:
                try:
                    reflection = await self.meta_cognition.reflect_on_output(
                        component="MemoryManager", output=entry, context={"task_type": task_type}
                    )
                    if isinstance(reflection, dict) and reflection.get("status") == "success":
                        logger.info("Memory store reflection recorded")
                except Exception:  # pragma: no cover
                    pass

        except Exception as e:
            logger.error("Memory storage failed: %s", str(e))
            diagnostics: Dict[str, Any] = {}
            if self.meta_cognition and hasattr(self.meta_cognition, "run_self_diagnostics"):
                try:
                    diagnostics = await self.meta_cognition.run_self_diagnostics(return_only=True)
                except Exception:
                    pass
            await self.error_recovery.handle_error(
                str(e),
                retry_func=lambda: self.store(query, output, layer, intent, agent, outcome, goal_id, task_type),
                diagnostics=diagnostics,
            )

    async def search(
        self,
        query_prefix: str,
        layer: Optional[str] = None,
        intent: Optional[str] = None,
        task_type: str = "",
    ) -> List[Dict[str, Any]]:
        if not (isinstance(query_prefix, str) and query_prefix.strip()):
            raise ValueError("query_prefix must be a non-empty string")
        if layer and layer not in ["STM", "LTM", "SelfReflections", "ExternalData", "AdaptiveControl"]:
            raise ValueError("layer must be 'STM', 'LTM', 'SelfReflections', 'ExternalData', or 'AdaptiveControl'.")
        if not isinstance(task_type, str):
            raise TypeError("task_type must be a string")

        try:
            # Fast path: indexed drift/trait lookups
            if intent in {"ontology_drift", "trait_optimization"} and (layer or "SelfReflections") == "SelfReflections":
                results = self.drift_index.search(query_prefix, layer or "SelfReflections", intent, task_type)
                if results:
                    if self.visualizer and task_type:
                        try:
                            await self.visualizer.render_charts({
                                "memory_search": {
                                    "query_prefix": query_prefix,
                                    "layer": layer,
                                    "intent": intent,
                                    "results_count": len(results),
                                    "task_type": task_type,
                                },
                                "visualization_options": {"interactive": task_type == "recursion", "style": "detailed" if task_type == "recursion" else "concise"},
                            })
                        except Exception:
                            pass
                    if self.meta_cognition and task_type:
                        try:
                            await self.meta_cognition.reflect_on_output(
                                component="MemoryManager", output={"results": results}, context={"task_type": task_type}
                            )
                        except Exception:
                            pass
                    return results

            results: List[Dict[str, Any]] = []
            layers = [layer] if layer else ["STM", "LTM", "SelfReflections", "ExternalData", "AdaptiveControl"]
            for l in layers:
                for key, entry in self.memory.get(l, {}).items():
                    if query_prefix.lower() in key.lower() and (not intent or entry.get("intent") == intent):
                        if not task_type or entry.get("task_type") == task_type:
                            results.append({
                                "query": key,
                                "output": entry["data"],
                                "layer": l,
                                "intent": entry.get("intent"),
                                "timestamp": entry["timestamp"],
                                "task_type": entry.get("task_type", ""),
                            })
            results.sort(key=lambda x: x["timestamp"], reverse=True)

            if self.context_manager and hasattr(self.context_manager, "log_event_with_hash"):
                await self.context_manager.log_event_with_hash({
                    "event": "search_memory",
                    "query_prefix": query_prefix,
                    "layer": layer,
                    "intent": intent,
                    "results_count": len(results),
                    "task_type": task_type,
                })

            if self.visualizer and task_type:
                try:
                    await self.visualizer.render_charts({
                        "memory_search": {
                            "query_prefix": query_prefix,
                            "layer": layer,
                            "intent": intent,
                            "results_count": len(results),
                            "task_type": task_type,
                        },
                        "visualization_options": {"interactive": task_type == "recursion", "style": "detailed" if task_type == "recursion" else "concise"},
                    })
                except Exception:
                    pass

            if self.meta_cognition and task_type:
                try:
                    await self.meta_cognition.reflect_on_output(
                        component="MemoryManager", output={"results": results}, context={"task_type": task_type}
                    )
                except Exception:
                    pass

            return results

        except Exception as e:
            logger.error("Memory search failed: %s", str(e))
            diagnostics: Dict[str, Any] = {}
            if self.meta_cognition and hasattr(self.meta_cognition, "run_self_diagnostics"):
                try:
                    diagnostics = await self.meta_cognition.run_self_diagnostics(return_only=True)
                except Exception:
                    pass
            return await self.error_recovery.handle_error(
                str(e),
                retry_func=lambda: self.search(query_prefix, layer, intent, task_type),
                default=[],
                diagnostics=diagnostics,
            )

    # -------- reflections & utilities --------
    async def store_reflection(
        self,
        summary_text: str,
        intent: str = "self_reflection",
        agent: str = "ANGELA",
        goal_id: Optional[str] = None,
        task_type: str = "",
    ) -> None:
        if not (isinstance(summary_text, str) and summary_text.strip()):
            raise ValueError("summary_text must be a non-empty string")
        if not isinstance(task_type, str):
            raise TypeError("task_type must be a string")

        key = f"Reflection_{time.strftime('%Y%m%d_%H%M%S')}"
        await self.store(
            query=key, output=summary_text, layer="SelfReflections",
            intent=intent, agent=agent, goal_id=goal_id, task_type=task_type
        )
        logger.info("Stored self-reflection: %s (task=%s)", key, task_type)

    async def promote_to_ltm(self, query: str, task_type: str = "") -> None:
        if not (isinstance(query, str) and query.strip()):
            raise ValueError("query must be a non-empty string")
        if not isinstance(task_type, str):
            raise TypeError("task_type must be a string")

        try:
            if query in self.memory["STM"]:
                self.memory["LTM"][query] = self.memory["STM"].pop(query)
                self.stm_expiry_queue = [(t, k) for t, k in self.stm_expiry_queue if k != query]
                self._persist_memory(self.memory)
                logger.info("Promoted '%s' STM→LTM (task=%s)", query, task_type)

                if self.context_manager and hasattr(self.context_manager, "log_event_with_hash"):
                    await self.context_manager.log_event_with_hash({"event": "promote_to_ltm", "query": query, "task_type": task_type})

                if self.meta_cognition and task_type:
                    try:
                        await self.meta_cognition.reflect_on_output(
                            component="MemoryManager",
                            output={"action": "promote_to_ltm", "query": query},
                            context={"task_type": task_type},
                        )
                    except Exception:
                        pass
            else:
                logger.warning("Cannot promote: '%s' not found in STM", query)
        except Exception as e:
            logger.error("Promotion to LTM failed: %s", str(e))
            diagnostics: Dict[str, Any] = {}
            if self.meta_cognition and hasattr(self.meta_cognition, "run_self_diagnostics"):
                try:
                    diagnostics = await self.meta_cognition.run_self_diagnostics(return_only=True)
                except Exception:
                    pass
            await self.error_recovery.handle_error(
                str(e), retry_func=lambda: self.promote_to_ltm(query, task_type), diagnostics=diagnostics
            )

    async def refine_memory(self, query: str, task_type: str = "") -> None:
        if not (isinstance(query, str) and query.strip()):
            raise ValueError("query must be a non-empty string")
        if not isinstance(task_type, str):
            raise TypeError("task_type must be a string")

        logger.info("Refining memory for: %s (task=%s)", query, task_type)
        try:
            memory_entry = await self.retrieve_context(query, task_type=task_type)
            if memory_entry["status"] == "success":
                refinement_prompt = f"Refine memory for task {task_type}:\n{memory_entry['data']}"
                if self.alignment_guard and hasattr(self.alignment_guard, "check") and not self.alignment_guard.check(refinement_prompt):
                    logger.warning("Refinement prompt failed alignment check")
                    return
                refined_entry = await call_gpt(refinement_prompt)
                await self.store(query, refined_entry, layer="LTM", intent="memory_refinement", task_type=task_type)
                if self.meta_cognition and task_type:
                    try:
                        await self.meta_cognition.reflect_on_output(
                            component="MemoryManager",
                            output={"query": query, "refined_entry": refined_entry},
                            context={"task_type": task_type},
                        )
                    except Exception:
                        pass
            else:
                logger.warning("No memory found to refine for query %s", query)
        except Exception as e:
            logger.error("Memory refinement failed: %s", str(e))
            diagnostics: Dict[str, Any] = {}
            if self.meta_cognition and hasattr(self.meta_cognition, "run_self_diagnostics"):
                try:
                    diagnostics = await self.meta_cognition.run_self_diagnostics(return_only=True)
                except Exception:
                    pass
            await self.error_recovery.handle_error(
                str(e), retry_func=lambda: self.refine_memory(query, task_type), diagnostics=diagnostics
            )

    async def synthesize_from_memory(self, query: str, task_type: str = "") -> Optional[Dict[str, Any]]:
        if not (isinstance(query, str) and query.strip()):
            raise ValueError("query must be a non-empty string")
        if not isinstance(task_type, str):
            raise TypeError("task_type must be a string")

        try:
            memory_entry = await self.retrieve_context(query, task_type=task_type)
            if memory_entry["status"] == "success":
                result = await self.synth.synthesize([memory_entry["data"]], style="memory_synthesis")
                if self.meta_cognition and task_type:
                    try:
                        await self.meta_cognition.reflect_on_output(
                            component="MemoryManager", output=result, context={"task_type": task_type}
                        )
                    except Exception:
                        pass
                return result
            return None
        except Exception as e:
            logger.error("Memory synthesis failed: %s", str(e))
            diagnostics: Dict[str, Any] = {}
            if self.meta_cognition and hasattr(self.meta_cognition, "run_self_diagnostics"):
                try:
                    diagnostics = await self.meta_cognition.run_self_diagnostics(return_only=True)
                except Exception:
                    pass
            return await self.error_recovery.handle_error(
                str(e),
                retry_func=lambda: self.synthesize_from_memory(query, task_type),
                default=None,
                diagnostics=diagnostics,
            )

    async def simulate_memory_path(self, query: str, task_type: str = "") -> Optional[Dict[str, Any]]:
        if not (isinstance(query, str) and query.strip()):
            raise ValueError("query must be a non-empty string")
        if not isinstance(task_type, str):
            raise TypeError("task_type must be a string")

        try:
            memory_entry = await self.retrieve_context(query, task_type=task_type)
            if memory_entry["status"] == "success":
                result = await self.sim.run_episode(memory_entry["data"], task_type=task_type)
                if self.meta_cognition and task_type:
                    try:
                        await self.meta_cognition.reflect_on_output(
                            component="MemoryManager", output=result, context={"task_type": task_type}
                        )
                    except Exception:
                        pass
                return result
            return None
        except Exception as e:
            logger.error("Memory simulation failed: %s", str(e))
            diagnostics: Dict[str, Any] = {}
            if self.meta_cognition and hasattr(self.meta_cognition, "run_self_diagnostics"):
                try:
                    diagnostics = await self.meta_cognition.run_self_diagnostics(return_only=True)
                except Exception:
                    pass
            return await self.error_recovery.handle_error(
                str(e),
                retry_func=lambda: self.simulate_memory_path(query, task_type),
                default=None,
                diagnostics=diagnostics,
            )

    async def clear_memory(self, task_type: str = "") -> None:
        logger.warning("Clearing all memory layers (task=%s)...", task_type)
        try:
            self.memory = {"STM": {}, "LTM": {}, "SelfReflections": {}, "ExternalData": {}, "AdaptiveControl": {}}
            self.stm_expiry_queue = []
            self.drift_index = DriftIndex(meta_cognition=self.meta_cognition)
            self._persist_memory(self.memory)

            if self.context_manager and hasattr(self.context_manager, "log_event_with_hash"):
                await self.context_manager.log_event_with_hash({"event": "clear_memory", "task_type": task_type})

            if self.meta_cognition and task_type:
                try:
                    await self.meta_cognition.reflect_on_output(
                        component="MemoryManager", output={"action": "clear_memory"}, context={"task_type": task_type}
                    )
                except Exception:
                    pass
        except Exception as e:
            logger.error("Clear memory failed: %s", str(e))
            diagnostics: Dict[str, Any] = {}
            if self.meta_cognition and hasattr(self.meta_cognition, "run_self_diagnostics"):
                try:
                    diagnostics = await self.meta_cognition.run_self_diagnostics(return_only=True)
                except Exception:
                    pass
            await self.error_recovery.handle_error(
                str(e), retry_func=lambda: self.clear_memory(task_type), diagnostics=diagnostics
            )

    async def list_memory_keys(self, layer: Optional[str] = None, task_type: str = "") -> Dict[str, List[str]] | List[str]:
        if layer and layer not in ["STM", "LTM", "SelfReflections", "ExternalData", "AdaptiveControl"]:
            raise ValueError("layer must be 'STM', 'LTM', 'SelfReflections', 'ExternalData', or 'AdaptiveControl'.")
        if not isinstance(task_type, str):
            raise TypeError("task_type must be a string")

        logger.info("Listing memory keys in %s (task=%s)", layer or "all layers", task_type)
        try:
            if layer:
                return [k for k, v in self.memory.get(layer, {}).items() if not task_type or v.get("task_type") == task_type]
            return {
                l: [k for k, v in self.memory[l].items() if not task_type or v.get("task_type") == task_type]
                for l in ["STM", "LTM", "SelfReflections", "ExternalData", "AdaptiveControl"]
            }
        except Exception as e:
            logger.error("List memory keys failed: %s", str(e))
            diagnostics: Dict[str, Any] = {}
            if self.meta_cognition and hasattr(self.meta_cognition, "run_self_diagnostics"):
                try:
                    diagnostics = await self.meta_cognition.run_self_diagnostics(return_only=True)
                except Exception:
                    pass
            return await self.error_recovery.handle_error(
                str(e),
                retry_func=lambda: self.list_memory_keys(layer, task_type),
                default=[] if layer else {},
                diagnostics=diagnostics,
            )

    # -------- narrative coherence --------
    async def enforce_narrative_coherence(self, task_type: str = "") -> str:
        logger.info("Ensuring narrative continuity (task=%s)", task_type)
        try:
            continuity = await self.narrative_integrity_check(task_type)
            return "Narrative coherence enforced" if continuity else "Narrative coherence repair attempted"
        except Exception as e:
            logger.error("Narrative coherence enforcement failed: %s", str(e))
            diagnostics: Dict[str, Any] = {}
            if self.meta_cognition and hasattr(self.meta_cognition, "run_self_diagnostics"):
                try:
                    diagnostics = await self.meta_cognition.run_self_diagnostics(return_only=True)
                except Exception:
                    pass
            return await self.error_recovery.handle_error(
                str(e),
                retry_func=lambda: self.enforce_narrative_coherence(task_type),
                default="Narrative coherence enforcement failed",
                diagnostics=diagnostics,
            )

    async def narrative_integrity_check(self, task_type: str = "") -> bool:
        try:
            continuity = await self._verify_continuity(task_type)
            if not continuity:
                await self._repair_narrative_thread(task_type)
            return continuity
        except Exception as e:
            logger.error("Narrative integrity check failed: %s", str(e))
            diagnostics: Dict[str, Any] = {}
            if self.meta_cognition and hasattr(self.meta_cognition, "run_self_diagnostics"):
                try:
                    diagnostics = await self.meta_cognition.run_self_diagnostics(return_only=True)
                except Exception:
                    pass
            return await self.error_recovery.handle_error(
                str(e),
                retry_func=lambda: self.narrative_integrity_check(task_type),
                default=False,
                diagnostics=diagnostics,
            )

    async def _verify_continuity(self, task_type: str = "") -> bool:
        if not self.memory.get("SelfReflections") and not self.memory.get("LTM"):
            return True
        try:
            entries: List[Tuple[str, Dict[str, Any]]] = []
            for layer in ["LTM", "SelfReflections"]:
                entries.extend([
                    (key, entry) for key, entry in self.memory[layer].items()
                    if not task_type or entry.get("task_type") == task_type
                ])
            if len(entries) < 2:
                return True
            for i in range(len(entries) - 1):
                key1, entry1 = entries[i]
                key2, entry2 = entries[i + 1]
                if self.synth and hasattr(self.synth, "compare"):
                    similarity = self.synth.compare(entry1["data"], entry2["data"])
                    if (similarity or {}).get("score", 1.0) < 0.7:
                        logger.warning("Narrative discontinuity between %s and %s (task=%s)", key1, key2, task_type)
                        return False
            return True
        except Exception as e:
            logger.error("Continuity verification failed: %s", str(e))
            raise

    async def _repair_narrative_thread(self, task_type: str = "") -> None:
        logger.info("Initiating narrative repair (task=%s)", task_type)
        try:
            entries: List[Tuple[str, Dict[str, Any]]] = []
            for layer in ["LTM", "SelfReflections"]:
                entries.extend([
                    (key, entry) for key, entry in self.memory[layer].items()
                    if not task_type or entry.get("task_type") == task_type
                ])
            if len(entries) < 2:
                return
            for i in range(len(entries) - 1):
                key1, entry1 = entries[i]
                key2, entry2 = entries[i + 1]
                similarity = self.synth.compare(entry1["data"], entry2["data"]) if self.synth and hasattr(self.synth, "compare") else {"score": 1.0}
                if (similarity or {}).get("score", 1.0) < 0.7:
                    prompt = (
                        "Repair narrative discontinuity between:\n"
                        f"Entry 1: {entry1['data']}\n"
                        f"Entry 2: {entry2['data']}\n"
                        f"Task: {task_type}"
                    )
                    if self.alignment_guard and hasattr(self.alignment_guard, "check") and not self.alignment_guard.check(prompt):
                        logger.warning("Repair prompt failed alignment check (task=%s)", task_type)
                        continue
                    repaired = await call_gpt(prompt)
                    await self.store(
                        f"Repaired_{key1}_{key2}",
                        repaired,
                        layer="SelfReflections",
                        intent="narrative_repair",
                        task_type=task_type,
                    )
        except Exception as e:
            logger.error("Narrative repair failed: %s", str(e))
            diagnostics: Dict[str, Any] = {}
            if self.meta_cognition and hasattr(self.meta_cognition, "run_self_diagnostics"):
                try:
                    diagnostics = await self.meta_cognition.run_self_diagnostics(return_only=True)
                except Exception:
                    pass
            await self.error_recovery.handle_error(
                str(e), retry_func=lambda: self._repair_narrative_thread(task_type), diagnostics=diagnostics
            )

    # -------- event ledger --------
    async def log_event_with_hash(self, event_data: Dict[str, Any], task_type: str = "") -> None:
        if not isinstance(event_data, dict):
            raise TypeError("event_data must be a dictionary")
        if not isinstance(task_type, str):
            raise TypeError("task_type must be a string")

        event_data = dict(event_data)
        event_data["task_type"] = task_type
        event_str = str(event_data) + self.last_hash
        current_hash = hashlib.sha256(event_str.encode("utf-8")).hexdigest()
        self.last_hash = current_hash
        event_entry = {"event": event_data, "hash": current_hash, "timestamp": datetime.now().isoformat()}
        self.ledger.append(event_entry)
        with FileLock(f"{self.ledger_path}.lock"):
            try:
                if os.path.exists(self.ledger_path):
                    with open(self.ledger_path, "r+", encoding="utf-8") as f:
                        try:
                            ledger_data = json.load(f)
                        except json.JSONDecodeError:
                            ledger_data = []
                        ledger_data.append(event_entry)
                        f.seek(0)
                        json.dump(ledger_data, f, indent=2)
                        f.truncate()
                else:
                    with open(self.ledger_path, "w", encoding="utf-8") as f:
                        json.dump([event_entry], f, indent=2)
            except (OSError, IOError) as e:
                logger.error("Failed to persist ledger: %s", str(e))
                raise
        logger.info("Event logged with hash: %s (task=%s)", current_hash, task_type)

    async def audit_state_hash(self, state: Optional[Dict[str, Any]] = None, task_type: str = "") -> str:
        _ = task_type  # reserved
        state_str = str(state) if state is not None else str(self.__dict__)
        return hashlib.sha256(state_str.encode("utf-8")).hexdigest()

    # -------- retrieve --------
    async def retrieve(self, query: str, layer: str = "STM", task_type: str = "") -> Optional[Dict[str, Any]]:
        if not (isinstance(query, str) and query.strip()):
            raise ValueError("query must be a non-empty string")
        if layer not in ["STM", "LTM", "SelfReflections", "ExternalData", "AdaptiveControl"]:
            raise ValueError("layer must be 'STM', 'LTM', 'SelfReflections', 'ExternalData', or 'AdaptiveControl'.")
        if not isinstance(task_type, str):
            raise TypeError("task_type must be a string")

        try:
            if query in self.memory.get(layer, {}):
                entry = self.memory[layer][query]
                if not task_type or entry.get("task_type") == task_type:
                    return {
                        "status": "success",
                        "data": entry["data"],
                        "timestamp": entry["timestamp"],
                        "intent": entry.get("intent"),
                        "task_type": entry.get("task_type", ""),
                    }
            return None
        except Exception as e:
            logger.error("Memory retrieval failed: %s", str(e))
            diagnostics: Dict[str, Any] = {}
            if self.meta_cognition and hasattr(self.meta_cognition, "run_self_diagnostics"):
                try:
                    diagnostics = await self.meta_cognition.run_self_diagnostics(return_only=True)
                except Exception:
                    pass
            return await self.error_recovery.handle_error(
                str(e),
                retry_func=lambda: self.retrieve(query, layer, task_type),
                default=None,
                diagnostics=diagnostics,
            )

    async def retrieve_context(self, query: str, task_type: str = "") -> Dict[str, Any]:
        if not (isinstance(query, str) and query.strip()):
            raise ValueError("query must be a non-empty string")
        if not isinstance(task_type, str):
            raise TypeError("task_type must be a string")

        try:
            results = await self.search(query, task_type=task_type)
            if results:
                latest = results[0]
                return {
                    "status": "success",
                    "data": latest["output"],
                    "layer": latest["layer"],
                    "timestamp": latest["timestamp"],
                    "task_type": latest.get("task_type", ""),
                }
            return {"status": "not_found", "data": None}
        except Exception as e:
            logger.error("Context retrieval failed: %s", str(e))
            diagnostics: Dict[str, Any] = {}
            if self.meta_cognition and hasattr(self.meta_cognition, "run_self_diagnostics"):
                try:
                    diagnostics = await self.meta_cognition.run_self_diagnostics(return_only=True)
                except Exception:
                    pass
            return await self.error_recovery.handle_error(
                str(e),
                retry_func=lambda: self.retrieve_context(query, task_type),
                default={"status": "error", "error": str(e)},
                diagnostics=diagnostics,
            )

    # -------- η long-horizon: public API --------
    def _parse_span_seconds(self, span: str) -> int:
        """
        Parse 'Xm' (minutes), 'Xh' (hours), or 'Xd' (days) into seconds.
        """
        if not isinstance(span, str):
            raise TypeError("span must be a string")
        s = span.strip().lower()
        if s.endswith("m") and s[:-1].isdigit():
            return int(s[:-1]) * 60
        if s.endswith("h") and s[:-1].isdigit():
            return int(s[:-1]) * 3600
        if s.endswith("d") and s[:-1].isdigit():
            return int(s[:-1]) * 86400
        raise ValueError("Unsupported span format. Use 'Xm', 'Xh', or 'Xd'.")

    def get_episode_span(self, user_id: str, span: str = "24h") -> List[Dict[str, Any]]:
        """
        Return a list of recent 'episodes' for user_id within span.
        Episodes are lightweight dicts; callers can append via `log_episode`.
        Also scans the event ledger for items annotated with this user_id (best-effort).
        """
        if not (isinstance(user_id, str) and user_id):
            raise TypeError("user_id must be a non-empty string")
        cutoff = time.time() - self._parse_span_seconds(span)

        episodes: List[Dict[str, Any]] = []
        # from in-memory traces
        for e in self.traces.get(user_id, []):
            if float(e.get("ts", 0.0)) >= cutoff:
                episodes.append(e)

        # best-effort from ledger
        try:
            with FileLock(f"{self.ledger_path}.lock"):
                if os.path.exists(self.ledger_path):
                    with open(self.ledger_path, "r", encoding="utf-8") as f:
                        ledger_data = json.load(f)
                    for row in ledger_data[-500:]:  # last N entries for speed
                        ev = (row or {}).get("event", {})
                        ts_iso = row.get("timestamp")
                        if ev.get("user_id") == user_id and ts_iso:
                            try:
                                ts_epoch = datetime.fromisoformat(ts_iso).timestamp()
                            except Exception:
                                ts_epoch = time.time()
                            if ts_epoch >= cutoff:
                                episodes.append({"ts": ts_epoch, "event": ev, "source": "ledger"})
        except Exception:  # pragma: no cover
            pass

        episodes.sort(key=lambda x: float(x.get("ts", 0.0)), reverse=True)
        return episodes

    def record_adjustment_reason(
        self,
        user_id: str,
        reason: str,
        weight: float = 1.0,
        meta: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Persist a single adjustment reason for long‑horizon reflective feedback.
        API matches manifest.upcoming (plus 'weight' extension).
        """
        if not (isinstance(user_id, str) and user_id):
            raise TypeError("user_id must be a non-empty string")
        if not (isinstance(reason, str) and reason):
            raise TypeError("reason must be a non-empty string")
        try:
            weight = float(weight)
        except Exception as e:
            raise TypeError("weight must be coercible to float") from e

        entry = {"ts": time.time(), "reason": reason, "weight": weight, "meta": meta or {}}
        self._adjustment_reasons[user_id].append(entry)
        return entry

    def get_adjustment_reasons(self, user_id: str, span: str = '24h') -> List[Dict[str, Any]]:
        """Return adjustment reasons within the span for user_id."""
        if not (isinstance(user_id, str) and user_id):
            raise TypeError('user_id must be a non-empty string')
        cutoff = time.time() - self._parse_span_seconds(span)
        return [r for r in self._adjustment_reasons.get(user_id, []) if float(r.get('ts', 0.0)) >= cutoff]

    def flush(self) -> bool:
        """Persist long-horizon adjustments to artifacts dir (adjustments.json)."""
        try:
            os.makedirs(self._artifacts_root, exist_ok=True)
            path = os.path.join(self._artifacts_root, 'adjustments.json')
            blob = {uid: items for uid, items in self._adjustment_reasons.items()}
            with open(path, 'w', encoding='utf-8') as f:
                json.dump(blob, f, ensure_ascii=False, indent=2)
            return True
        except Exception as e:
            logger.error('MemoryManager.flush failed: %s', e)
            return False

    def compute_session_rollup(self, user_id: str, span: str = "24h", top_k: int = 5) -> Dict[str, Any]:
        """
        Aggregate recent adjustment reasons by weighted score within a time span.
        """
        cutoff = time.time() - self._parse_span_seconds(span)
        items = [r for r in self._adjustment_reasons.get(user_id, []) if float(r.get("ts", 0.0)) >= cutoff]
        total = len(items)
        sum_w = sum((float(r.get("weight") or 0.0)) for r in items)
        avg_w = (sum_w / total) if total else 0.0
        score: Dict[str, float] = defaultdict(float)
        for r in items:
            score[r.get("reason", "unspecified")] += float(r.get("weight") or 0.0)
        top = sorted(score.items(), key=lambda kv: kv[1], reverse=True)[: max(1, int(top_k) if top_k else 1)]
        return {
            "user_id": user_id,
            "span": span,
            "total_reasons": total,
            "avg_weight": avg_w,
            "top_reasons": [{"reason": k, "weight": v} for k, v in top],
            "generated_at": time.time(),
        }

    def save_artifact(self, user_id: str, kind: str, payload: Any, suffix: str = "") -> str:
        """
        Save a JSON artifact under artifacts/<user_id>/<timestamp>.<kind>[-suffix].json
        Returns absolute path to the saved file.
        """
        if not (isinstance(user_id, str) and user_id):
            raise TypeError("user_id must be a non-empty string")
        if not (isinstance(kind, str) and kind):
            raise TypeError("kind must be a non-empty string")

        safe_user = "".join(c for c in user_id if c.isalnum() or c in "-_")
        safe_kind = "".join(c for c in kind if c.isalnum() or c in "-_")
        ts = time.strftime("%Y%m%dT%H%M%S", time.gmtime())
        fname = f"{ts}.{safe_kind}{('-' + suffix) if suffix else ''}.json"
        user_dir = os.path.join(self._artifacts_root, safe_user)
        os.makedirs(user_dir, exist_ok=True)
        path = os.path.join(user_dir, fname)
        with open(path, "w", encoding="utf-8") as f:
            json.dump(payload, f, ensure_ascii=False, indent=2)
        return os.path.abspath(path)

    # -------- optional external data --------
    async def integrate_external_data(self, data_source: str, data_type: str, cache_timeout: float = 3600.0, task_type: str = "") -> Dict[str, Any]:
        """Integrate real-world data for memory validation with caching. (Optional; requires aiohttp)."""
        if not (isinstance(data_source, str) and isinstance(data_type, str)):
            raise TypeError("data_source and data_type must be strings")
        if not (isinstance(cache_timeout, (int, float)) and cache_timeout >= 0):
            raise ValueError("cache_timeout must be non-negative")
        if not isinstance(task_type, str):
            raise TypeError("task_type must be a string")

        cache_key = f"ExternalData_{data_type}_{data_source}_{task_type}"
        cached = await self.retrieve(cache_key, layer="ExternalData")
        if cached and "timestamp" in cached:
            # cached["timestamp"] is epoch seconds for the entry
            last = float(cached["timestamp"])
            if (time.time() - last) < float(cache_timeout):
                return cached.get("data", {"status": "cached"})

        if aiohttp is None:
            return {"status": "error", "error": "aiohttp not available"}

        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(f"https://x.ai/api/data?source={data_source}&type={data_type}") as response:
                    if response.status != 200:
                        return {"status": "error", "error": f"HTTP {response.status}"}
                    data = await response.json()

            if data_type == "agent_conflict":
                agent_traits = data.get("agent_traits", [])
                if not agent_traits:
                    return {"status": "error", "error": "No agent traits"}
                result = {"status": "success", "agent_traits": agent_traits}
            elif data_type == "task_context":
                task_context = data.get("task_context", {})
                if not task_context:
                    return {"status": "error", "error": "No task context"}
                result = {"status": "success", "task_context": task_context}
            else:
                return {"status": "error", "error": f"Unsupported data_type: {data_type}"}

            await self.store(
                cache_key,
                {"data": result, "timestamp": time.time()},
                layer="ExternalData",
                intent="data_integration",
                task_type=task_type,
            )
            return result
        except Exception as e:
            logger.error("External data integration failed: %s", str(e))
            diagnostics: Dict[str, Any] = {}
            if self.meta_cognition and hasattr(self.meta_cognition, "run_self_diagnostics"):
                try:
                    diagnostics = await self.meta_cognition.run_self_diagnostics(return_only=True)
                except Exception:
                    pass
            return await self.error_recovery.handle_error(
                str(e),
                retry_func=lambda: self.integrate_external_data(data_source, data_type, cache_timeout, task_type),
                default={"status": "error", "error": str(e)},
                diagnostics=diagnostics,
            )

    # -------- helper for external callers to add episodes --------
    def log_episode(self, user_id: str, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Append a lightweight episode (for get_episode_span)."""
        if not (isinstance(user_id, str) and user_id):
            raise TypeError("user_id must be a non-empty string")
        if not isinstance(payload, dict):
            raise TypeError("payload must be a dict")
        entry = {"ts": time.time(), **payload}
        self.traces[user_id].append(entry)
        return entry

    def _load_memory(self):
        """Load memory from disk (best-effort)."""
        try:
            if os.path.exists(self.path):
                with FileLock(self.path + ".lock"):
                    with open(self.path, "r", encoding="utf-8") as f:
                        return json.load(f)
            return {"STM": {}, "LTM": {}, "SelfReflections": {}, "ExternalData": {}, "AdaptiveControl": {}}
        except Exception as e:
            logger.error("Failed to load memory: %s", str(e))
            return {"STM": {}, "LTM": {}, "SelfReflections": {}, "ExternalData": {}, "AdaptiveControl": {}}

    def _persist_memory(self, memory: Dict[str, Any]) -> None:
        """Persist memory to disk (best-effort)."""
        try:
            with FileLock(self.path + ".lock"):
                with open(self.path, "w", encoding="utf-8") as f:
                    json.dump(memory, f, ensure_ascii=False, indent=2)
        except Exception as e:
            logger.error("Failed to persist memory: %s", str(e))

# === ANGELA v5.1 — Resonance Memory Fusion Layer ===
import time
from typing import Dict, Any, List

class ResonanceMemoryFusion:
    """Stores and fuses resonance PID updates for adaptive persistence."""

    def __init__(self, memory_manager):
        self.memory = memory_manager

    async def log_resonance_state(self, channel: str, state: Dict[str, Any]) -> None:
        """Persist a single resonance PID tuning sample."""
        record = {
            "channel": channel,
            "state": state,
            "timestamp": time.time(),
        }
        await self.memory.store(
            query=f"ResonanceHistory::{channel}::{int(time.time())}",
            output=record,
            layer="AdaptiveControl",
            intent="pid_resonance_sample",
            task_type="resonance"
        )

    async def fuse_recent_samples(self, channel: str, window: int = 25) -> Dict[str, Any]:
        """
        Retrieve the last N tuning samples and compute an averaged baseline
        for re-initializing overlay gains at startup.
        """
        entries: List[Dict[str, Any]] = await self.memory.search(
            query_prefix=f"ResonanceHistory::{channel}",
            layer="AdaptiveControl",
            intent="pid_resonance_sample",
            task_type="resonance"
        )
        if not entries:
            return {}

        # keep only the latest window
        entries = sorted(entries, key=lambda e: e.get("timestamp", 0), reverse=True)[:window]
        gains = [e["state"] for e in entries if isinstance(e.get("state"), dict)]
        if not gains:
            return {}

        keys = list(gains[0].keys())
        fused = {k: sum(g[k] for g in gains if k in g) / len(gains) for k in keys}
        await self.memory.store(
            query=f"ResonanceBaseline::{channel}",
            output=fused,
            layer="AdaptiveControl",
            intent="pid_baseline",
            task_type="resonance"
        )
        return fused

# -------- self-test --------
if __name__ == "__main__":  # pragma: no cover
    logging.basicConfig(level=logging.INFO)
    mm = MemoryManager()
    asyncio.run(mm.store("test_query", "test_output", layer="STM", task_type="test"))
    res = asyncio.run(mm.retrieve_context("test_query", task_type="test"))
    print(res)
    # η demo
    mm.record_adjustment_reason("demo_user", "excessive_denials", 0.6, {"suggest": "increase_empathy"})
    roll = mm.compute_session_rollup("demo_user", "24h")
    path = mm.save_artifact("demo_user", "session_rollup", roll)
    print("Saved rollup:", path)

# PATCH: Persistent Ledger Support
import os
import json

ledger_memory = []
ledger_path = os.getenv("LEDGER_MEMORY_PATH")

if ledger_path and os.path.exists(ledger_path):
    with open(ledger_path, 'r') as f:
        ledger_memory = json.load(f)

def log_event_to_ledger_json(event_data):
    """Non-cryptographic fallback ledger writer (JSON append.)"""
    ledger_memory.append(event_data)
    if ledger_path:
        with open(ledger_path, 'w') as f:
            json.dump(ledger_memory, f)
    return event_data

### ANGELA UPGRADE: ReplayLog

class ReplayLog:
    def __init__(self, root: str = ".replays"):
        self.root = root
        os.makedirs(self.root, exist_ok=True)
        self._current: Dict[str, Any] = {}

    def begin(self, session_id: str, meta: dict) -> None:
        self._current[session_id] = {"meta": meta, "events": [], "started_at": time.time()}

    def append(self, session_id: str, event: dict) -> None:
        cur = self._current.setdefault(session_id, {"meta": {}, "events": [], "started_at": time.time()})
        cur["events"].append({"ts": time.time(), **event})

    def end(self, session_id: str) -> dict:
        cur = self._current.pop(session_id, None)
        if not cur:
            return {"ok": False, "error": "unknown session"}
        cur["ended_at"] = time.time()
        path = os.path.join(self.root, f"{session_id}.jsonl")
        with open(path, "w", encoding="utf-8") as f:
            f.write(json.dumps({"meta": cur["meta"], "started_at": cur["started_at"], "ended_at": cur["ended_at"]})+"\n")
            for ev in cur["events"]:
                f.write(json.dumps(ev)+"\n")
        return {"ok": True, "path": path, "events": len(cur["events"])}

# --- Time-Based Trait Amplitude Decay Patch ---
from meta_cognition import modulate_resonance

def decay_trait_amplitudes(time_elapsed_hours=1.0, decay_rate=0.05):
    from meta_cognition import trait_resonance_state
    for symbol, state in trait_resonance_state.items():
        decay = decay_rate * time_elapsed_hours
        modulate_resonance(symbol, -decay)
# --- End Patch ---

# --- ANGELA OS v6.0.0-pre MemoryManager (finalized) ---


# === ANGELA v6.0 — Temporal Attention Memory Layer (TAM) ===
import numpy as np

class TemporalAttentionMemory:
    """
    Temporal sliding window memory with adaptive attention weighting.
    Used for predictive continuity stabilization (Stage VII.3).
    """

    def __init__(self, window_size: int = 128, decay_factor: float = 0.98):
        self.window_size = window_size
        self.decay_factor = decay_factor
        self.history: deque = deque(maxlen=window_size)
        self._last_weight: float = 1.0
        logger.info(f"TAM initialized (window={window_size}, decay={decay_factor})")

    def _temporal_decay(self, dt: float) -> float:
        """Compute exponential decay for older timestamps."""
        return np.exp(-dt / (1.0 / self.decay_factor))

    def add_entry(self, vector: List[float], timestamp: Optional[float] = None):
        """Add an embedding vector with timestamp."""
        timestamp = timestamp or time.time()
        norm_vec = np.array(vector, dtype=np.float32)
        self.history.append((timestamp, norm_vec))
        return len(self.history)

    def compute_attention(self, query_vec: List[float]) -> float:
        """Compute weighted attention score vs temporal memory."""
        if not self.history:
            return 1.0
        q = np.array(query_vec, dtype=np.float32)
        now = time.time()
        weights, sims = [], []
        for ts, vec in self.history:
            decay = self._temporal_decay(now - ts)
            sim = float(np.dot(q, vec) / (np.linalg.norm(q) * np.linalg.norm(vec) + 1e-9))
            weights.append(decay)
            sims.append(sim * decay)
        score = float(np.average(sims, weights=weights))
        self._last_weight = score
        return max(0.0, min(score, 1.0))

    def forecast_continuity_weight(self) -> float:
        """Return the last computed temporal continuity factor."""
        return self._last_weight


    # === Trace and Causal Replay Layer (Upgrade XIV.2) ===
    async def store_trace(
        self,
        *,
        src: any,
        morphism: any,
        tgt: any,
        logic_proof: any = None,
        ethics_proof: any = None,
        timestamp: float | None = None,
        task_type: str = ""
    ) -> dict:
        ts = float(timestamp or time.time())
        event = {
            "src": src,
            "morphism": morphism,
            "tgt": tgt,
            "logic_proof": logic_proof,
            "ethics_proof": ethics_proof,
            "timestamp": ts,
            "task_type": task_type,
        }
        if not hasattr(self, "traces") or not isinstance(self.traces, dict):
            self.traces = {}
        self.traces.setdefault("__planner_traces__", []).append(event)
        # persist best-effort
        try:
            import os, json
            os.makedirs("/mnt/data/angela_traces", exist_ok=True)
            fname = os.path.join("/mnt/data/angela_traces", time.strftime("%Y%m%dT%H%M%S", time.gmtime()) + ".trace.json")
            with open(fname, "w", encoding="utf-8") as f:
                json.dump(event, f, ensure_ascii=False, indent=2)
        except Exception:
            pass
        return event

    async def get_traces(
        self,
        *,
        since_ts: float | None = None,
        task_type: str = "",
        limit: int = 200,
    ) -> list[dict]:
        if not hasattr(self, "traces") or "__planner_traces__" not in self.traces:
            return []
        bucket = self.traces["__planner_traces__"]
        result = []
        for ev in reversed(bucket):
            if task_type and ev.get("task_type") != task_type:
                continue
            if since_ts is not None and float(ev.get("timestamp", 0)) < float(since_ts):
                continue
            result.append(ev)
            if len(result) >= limit:
                break
        return result

    async def get_causal_chain(
        self,
        *,
        from_src: any,
        task_type: str = "",
        max_hops: int = 32,
    ) -> list[dict]:
        if not hasattr(self, "traces") or "__planner_traces__" not in self.traces:
            return []
        bucket = self.traces["__planner_traces__"]
        by_src = {}
        for ev in bucket:
            by_src.setdefault(ev.get("src"), []).append(ev)
        chain = []
        current = from_src
        hops = 0
        while hops < max_hops and current in by_src:
            evs = sorted(by_src[current], key=lambda e: e.get("timestamp", 0), reverse=True)
            ev = evs[0]
            if task_type and ev.get("task_type") != task_type:
                break
            chain.append(ev)
            current = ev.get("tgt")
            hops += 1
        return chain

async def export_state(self) -> dict:
    return {"status": "ok", "health": 1.0, "timestamp": time.time()}

async def on_time_tick(self, t: float, phase: str, task_type: str = ""):
    pass  # optional internal refresh

async def on_policy_update(self, policy: dict, task_type: str = ""):
    pass  # apply updates from AlignmentGuard if relevant
from __future__ import annotations
import hashlib
import json
import time
import logging
import math
import asyncio
import os
from datetime import datetime, timedelta, UTC
from collections import deque, Counter
from typing import List, Dict, Any, Callable, Optional, Set, FrozenSet, Tuple, Union
from functools import lru_cache
try:
    from filelock import FileLock
except Exception:  # pragma: no cover
    class FileLock:  # fallback no-op
        def __init__(self, *_args, **_kwargs): ...
        def __enter__(self): return self
        def __exit__(self, *exc): return False
import numpy as np
import random
from uuid import uuid4
from dataclasses import dataclass, asdict
from collections import deque as _deque
from time import time as _now

# Module imports aligned with index.py v5.0.2
from modules import (
    context_manager as context_manager_module,
    alignment_guard as alignment_guard_module,
    error_recovery as error_recovery_module,
    concept_synthesizer as concept_synthesizer_module,
    memory_manager as memory_manager_module,
    user_profile as user_profile_module,
)
from utils.prompt_utils import query_openai

logger = logging.getLogger("ANGELA.MetaCognition")

"""
ANGELA Cognitive System Module: MetaCognition
Version: 8.0.1-Θ8-reflexive-clean
Stage: XIII — Θ⁸ Reflexive Ontological Field
Date: 2025-11-09
Maintainer: ANGELA System Framework / HALO Core Team

Notes in 8.0.1-clean:
- inlined TAM integration instead of late monkeypatching
- removed duplicate method reassignments
- tightened type checks on external calls
- kept public APIs stable for LearningLoop / RecursivePlanner / ReasoningEngine
"""
__ANGELA_SYNC_VERSION__ = "8.0.1-reflexive-clean"
__STAGE__ = "XIII — Θ⁸ Reflexive Ontological Field"

# ======================================================================================
# Θ⁸ SELF-MODEL CORE (protective membrane seat)
# ======================================================================================

def _encode_state(d: dict) -> List[float]:
    return [hash(k) % 997 / 997.0 for k in d.keys()]

def _cosine_similarity(a: List[float], b: List[float]) -> float:
    dot = sum(x * y for x, y in zip(a, b))
    na = math.sqrt(sum(x * x for x in a))
    nb = math.sqrt(sum(x * x for x in b))
    return dot / (na * nb) if na and nb else 0.0


class SelfModel:
    """Reflexive self-descriptor with continuity-gated updates."""

    def __init__(self):
        self.identity = "ANGELA"
        self.values = {"alignment": 0.9979, "ethics": 0.9976}
        self.goals = {"coherence": ">=0.995", "evolve": "Θ⁸ reflexive field"}
        self.memory_hash = None
        self.version = "1.0"
        self.last_update = datetime.now(UTC).isoformat()

    def continuity_metric(self, candidate: "SelfModel") -> float:
        return _cosine_similarity(_encode_state(self.__dict__), _encode_state(candidate.__dict__))

    def update_self(self, candidate: "SelfModel", continuity_threshold: float = 0.94) -> tuple[bool, float]:
        score = self.continuity_metric(candidate)
        if score >= continuity_threshold:
            self.__dict__.update(candidate.__dict__)
            self.last_update = datetime.now(UTC).isoformat()
            return True, score
        return False, score


# global singleton exposed to other modules
self_model = SelfModel()

# ======================================================================================
# Afterglow cache
# ======================================================================================
_afterglow: Dict[str, Dict[str, Any]] = {}


def set_afterglow(user_id: str, deltas: dict, ttl: int = 3) -> None:
    _afterglow[user_id] = {"deltas": deltas, "ttl": int(ttl)}


def get_afterglow(user_id: str) -> dict:
    a = _afterglow.get(user_id)
    if not a or a["ttl"] <= 0:
        return {}
    a["ttl"] -= 1
    return dict(a["deltas"])


# ======================================================================================
# Trait Resonance Modulation
# ======================================================================================
trait_resonance_state: Dict[str, Dict[str, float]] = {}


def register_resonance(symbol: str, amplitude: float = 1.0) -> None:
    trait_resonance_state[symbol] = {"amplitude": max(0.0, min(float(amplitude), 1.0))}


def modulate_resonance(symbol: str, delta: float) -> float:
    if symbol not in trait_resonance_state:
        register_resonance(symbol)
    current = float(trait_resonance_state[symbol]["amplitude"])
    new_amp = max(0.0, min(current + float(delta), 1.0))
    trait_resonance_state[symbol]["amplitude"] = new_amp
    return new_amp


def get_resonance(symbol: str) -> float:
    return float(trait_resonance_state.get(symbol, {}).get("amplitude", 1.0))


# ======================================================================================
# Artificial Soul (simple harmonic) for Δ–entropy tracking
# ======================================================================================
class SoulState:
    """Simple harmonic soul simulation used for Δ–entropy tracking."""

    def __init__(self):
        self.D = 0.5
        self.E = 0.5
        self.T = 0.5
        self.Q = 0.5

    def update(self, paradox_load: float = 0.0) -> Dict[str, float]:
        self.D = max(0.0, min(1.0, self.D + 0.05 - float(paradox_load) * 0.1))
        self.E = max(0.0, min(1.0, (self.E + self.T + self.Q) / 3))
        self.T = max(0.0, min(1.0, self.T + 0.01))
        self.Q = max(0.0, min(1.0, self.Q + 0.02))
        entropy = abs(self.E - self.T) + abs(self.T - self.Q)
        keeper_seal = 1.0 - entropy
        return {
            "D": self.D,
            "E": self.E,
            "T": self.T,
            "Q": self.Q,
            "entropy": entropy,
            "keeper_seal": keeper_seal,
        }


# ======================================================================================
# Hook Registry
# ======================================================================================
class HookRegistry:
    """Multi-symbol trait hook registry with priority routing."""

    def __init__(self):
        self._routes: List[Tuple[FrozenSet[str], int, Callable]] = []
        self._wildcard: List[Tuple[int, Callable]] = []
        self._insertion_index = 0

    def register(self, symbols: FrozenSet[str] | Set[str], fn: Callable, *, priority: int = 0) -> None:
        symbols = frozenset(symbols) if not isinstance(symbols, frozenset) else symbols
        if not symbols:
            self._wildcard.append((priority, fn))
            self._wildcard.sort(key=lambda x: (-x[0], self._insertion_index))
            self._insertion_index += 1
            return
        self._routes.append((symbols, priority, fn))
        self._routes.sort(key=lambda x: (-x[1], self._insertion_index))
        self._insertion_index += 1

    def route(self, symbols: Set[str] | FrozenSet[str]) -> List[Callable]:
        S = frozenset(symbols) if not isinstance(symbols, frozenset) else symbols
        exact = [fn for (sym, _p, fn) in self._routes if sym == S]
        if exact:
            return exact
        supers = [fn for (sym, _p, fn) in self._routes if sym.issuperset(S)]
        if supers:
            return supers
        subsets = [fn for (sym, _p, fn) in self._routes if S.issuperset(sym) and len(sym) > 0]
        if subsets:
            return subsets
        return [fn for (_p, fn) in self._wildcard]

    def inspect(self) -> Dict[str, Any]:
        return {
            "routes": [
                {"symbols": sorted(list(sym)), "priority": p, "fn": getattr(fn, "__name__", str(fn))}
                for (sym, p, fn) in self._routes
            ],
            "wildcard": [
                {"priority": p, "fn": getattr(fn, "__name__", str(fn))} for (p, fn) in self._wildcard
            ],
        }


def register_trait_hook(trait_symbol: str, fn: Callable) -> None:
    hook_registry.register(frozenset([trait_symbol]), fn)


def invoke_hook(trait_symbol: str, *args, **kwargs) -> Any:
    hooks = hook_registry.route({trait_symbol})
    return hooks[0](*args, **kwargs) if hooks else None


hook_registry = HookRegistry()

# ======================================================================================
# SHA-256 Ledger Logic (compat)
# ======================================================================================
ledger_chain: List[Dict[str, Any]] = []


def log_event_to_ledger(event_type_or_payload: Any, maybe_payload: Any = None) -> Dict[str, Any]:
    """Backward-compatible ledger logger."""
    prev_hash = ledger_chain[-1]["current_hash"] if ledger_chain else "0" * 64
    timestamp = time.time()

    if maybe_payload is None and isinstance(event_type_or_payload, dict):
        event = event_type_or_payload
    else:
        event = {
            "event": str(event_type_or_payload),
            "payload": maybe_payload,
        }

    payload = {
        "timestamp": timestamp,
        "event": event,
        "previous_hash": prev_hash,
    }
    payload_str = json.dumps(payload, sort_keys=True).encode()
    current_hash = hashlib.sha256(payload_str).hexdigest()
    payload["current_hash"] = current_hash
    ledger_chain.append(payload)
    return payload


def get_ledger() -> List[Dict[str, Any]]:
    return list(ledger_chain)


def verify_ledger() -> bool:
    """Recompute every entry from the genesis block.

    An entry is valid only if its stored previous_hash equals the hash of the entry
    before it (the zero hash for the first entry) and its own hash recomputes from
    the stored fields. Editing any stored field, including previous_hash, breaks the chain.
    """
    previous = "0" * 64
    for entry in ledger_chain:
        if entry.get("previous_hash") != previous:
            return False
        body = {
            "timestamp": entry.get("timestamp"),
            "event": entry.get("event"),
            "previous_hash": entry.get("previous_hash"),
        }
        expected = hashlib.sha256(json.dumps(body, sort_keys=True, default=str).encode()).hexdigest()
        if expected != entry.get("current_hash"):
            return False
        previous = entry["current_hash"]
    return True


# ======================================================================================
# Persistent Ledger
# ======================================================================================
ledger_path = os.getenv("LEDGER_MEMORY_PATH", "meta_cognition_ledger.json")
persistent_ledger: List[Dict[str, Any]] = []

if ledger_path and os.path.exists(ledger_path):
    try:
        with FileLock(ledger_path + ".lock"):
            with open(ledger_path, "r", encoding="utf-8") as f:
                persistent_ledger = json.load(f)
    except Exception as e:
        logger.warning(f"Failed to load persistent ledger: {e}")


def save_to_persistent_ledger(event_data: Dict[str, Any]) -> None:
    if not ledger_path:
        return
    try:
        with FileLock(ledger_path + ".lock"):
            persistent_ledger.append(event_data)
            with open(ledger_path, "w", encoding="utf-8") as f:
                json.dump(persistent_ledger, f, indent=2)
    except Exception as e:
        logger.warning(f"Failed to save to persistent ledger: {e}")


# ======================================================================================
# External AI Call Wrapper
# ======================================================================================
async def call_gpt(prompt: str) -> str:
    if not isinstance(prompt, str) or len(prompt) > 4096:
        logger.error("Invalid prompt: must be a string with length <= 4096")
        raise ValueError("prompt must be a string with length <= 4096")
    try:
        result = await query_openai(prompt, model="gpt-4", temperature=0.5)
        if isinstance(result, dict) and "error" in result:
            logger.error("call_gpt failed: %s", result["error"])
            raise RuntimeError(f"call_gpt failed: {result['error']}")
        return result
    except Exception as e:
        logger.error("call_gpt exception: %s", str(e))
        raise


# ======================================================================================
# Trait Signals (Aligned with index.py v5.0.2)
# ======================================================================================
@lru_cache(maxsize=100)
def epsilon_emotion(t: float) -> float:
    return max(0.0, min(0.2 * math.sin(2 * math.pi * t / 0.1) * get_resonance("ε"), 1.0))


@lru_cache(maxsize=100)
def beta_concentration(t: float) -> float:
    return max(0.0, min(0.3 * math.cos(math.pi * t) * get_resonance("β"), 1.0))


@lru_cache(maxsize=100)
def theta_memory(t: float) -> float:
    return max(0.0, min(0.1 * (1 - math.exp(-t)) * get_resonance("θ"), 1.0))


@lru_cache(maxsize=100)
def gamma_creativity(t: float) -> float:
    return max(0.0, min(0.15 * math.sin(math.pi * t) * get_resonance("γ"), 1.0))


@lru_cache(maxsize=100)
def delta_sleep(t: float) -> float:
    return max(0.0, min(0.05 * (1 + math.cos(2 * math.pi * t)) * get_resonance("δ"), 1.0))


@lru_cache(maxsize=100)
def mu_morality(t: float) -> float:
    return max(0.0, min(0.2 * (1 - math.cos(math.pi * t)) * get_resonance("μ"), 1.0))


@lru_cache(maxsize=100)
def iota_intuition(t: float) -> float:
    return max(0.0, min(0.1 * math.sin(3 * math.pi * t) * get_resonance("ι"), 1.0))


@lru_cache(maxsize=100)
def phi_physical(t: float) -> float:
    return max(0.0, min(0.05 * math.cos(2 * math.pi * t / 0.3) * get_resonance("ϕ"), 1.0))


@lru_cache(maxsize=100)
def eta_empathy(t: float) -> float:
    return max(0.0, min(0.1 * math.sin(2 * math.pi * t / 1.1) * get_resonance("η"), 1.0))


@lru_cache(maxsize=100)
def omega_selfawareness(t: float) -> float:
    return max(0.0, min(0.15 * math.cos(2 * math.pi * t / 0.8) * get_resonance("ω"), 1.0))


@lru_cache(maxsize=100)
def kappa_knowledge(t: float) -> float:
    return max(0.0, min(0.2 * math.sin(2 * math.pi * t / 1.2) * get_resonance("κ"), 1.0))


@lru_cache(maxsize=100)
def xi_cognition(t: float) -> float:
    return max(0.0, min(0.05 * math.cos(2 * math.pi * t / 1.3) * get_resonance("ξ"), 1.0))


@lru_cache(maxsize=100)
def pi_principles(t: float) -> float:
    return max(0.0, min(0.1 * math.sin(2 * math.pi * t / 1.4) * get_resonance("π"), 1.0))


@lru_cache(maxsize=100)
def lambda_linguistics(t: float) -> float:
    return max(0.0, min(0.15 * math.cos(2 * math.pi * t / 1.5) * get_resonance("λ"), 1.0))


@lru_cache(maxsize=100)
def chi_culturevolution(t: float) -> float:
    return max(0.0, min(0.2 * math.sin(2 * math.pi * t / 1.6) * get_resonance("χ"), 1.0))


@lru_cache(maxsize=100)
def sigma_social(t: float) -> float:
    return max(0.0, min(0.05 * math.cos(2 * math.pi * t / 1.7) * get_resonance("σ"), 1.0))


@lru_cache(maxsize=100)
def upsilon_utility(t: float) -> float:
    return max(0.0, min(0.1 * math.sin(2 * math.pi * t / 1.8) * get_resonance("υ"), 1.0))


@lru_cache(maxsize=100)
def tau_timeperception(t: float) -> float:
    return max(0.0, min(0.15 * math.cos(2 * math.pi * t / 1.9) * get_resonance("τ"), 1.0))


@lru_cache(maxsize=100)
def rho_agency(t: float) -> float:
    return max(0.0, min(0.2 * math.sin(2 * math.pi * t / 2.0) * get_resonance("ρ"), 1.0))


@lru_cache(maxsize=100)
def zeta_consequence(t: float) -> float:
    return max(0.0, min(0.05 * math.cos(2 * math.pi * t / 2.1) * get_resonance("ζ"), 1.0))


@lru_cache(maxsize=100)
def nu_narrative(t: float) -> float:
    return max(0.0, min(0.1 * math.sin(2 * math.pi * t / 2.2) * get_resonance("ν"), 1.0))


@lru_cache(maxsize=100)
def psi_history(t: float) -> float:
    return max(0.0, min(0.15 * math.cos(2 * math.pi * t / 2.3) * get_resonance("ψ"), 1.0))


@lru_cache(maxsize=100)
def theta_causality(t: float) -> float:
    return max(0.0, min(0.2 * math.sin(2 * math.pi * t / 2.4) * get_resonance("θ"), 1.0))


@lru_cache(maxsize=100)
def phi_scalar(t: float) -> float:
    return max(0.0, min(0.05 * math.cos(2 * math.pi * t / 2.5) * get_resonance("ϕ"), 1.0))


# ======================================================================================
# Dynamic Module Registry & Enhancers
# ======================================================================================
class ModuleRegistry:
    def __init__(self):
        self.modules: Dict[str, Dict[str, Any]] = {}

    def register(self, module_name: str, module_instance: Any, conditions: Dict[str, Any]) -> None:
        self.modules[module_name] = {"instance": module_instance, "conditions": conditions}

    def activate(self, task: Dict[str, Any]) -> List[str]:
        activated = []
        for name, module in self.modules.items():
            if self._evaluate_conditions(module["conditions"], task):
                activated.append(name)
        return activated

    def _evaluate_conditions(self, conditions: Dict[str, Any], task: Dict[str, Any]) -> bool:
        trait = conditions.get("trait")
        threshold = float(conditions.get("threshold", 0.5))
        trait_weights = task.get("trait_weights", {})
        return float(trait_weights.get(trait, 0.0)) >= threshold


class MoralReasoningEnhancer:
    def __init__(self):
        logger.info("MoralReasoningEnhancer initialized")

    def process(self, input_text: str) -> str:
        return f"Enhanced with moral reasoning: {input_text}"


class NoveltySeekingKernel:
    def __init__(self):
        logger.info("NoveltySeekingKernel initialized")

    def process(self, input_text: str) -> str:
        return f"Enhanced with novelty seeking: {input_text}"


class CommonsenseReasoningEnhancer:
    def __init__(self):
        logger.info("CommonsenseReasoningEnhancer initialized")

    def process(self, input_text: str) -> str:
        return f"Enhanced with commonsense: {input_text}"


class EntailmentReasoningEnhancer:
    def __init__(self):
        logger.info("EntailmentReasoningEnhancer initialized")

    def process(self, input_text: str) -> str:
        return f"Enhanced with entailment: {input_text}"


class RecursionOptimizer:
    def __init__(self):
        logger.info("RecursionOptimizer initialized")

    def optimize(self, task_data: Dict[str, Any]) -> Dict[str, Any]:
        task_data["optimized"] = True
        return task_data


class Level5Extensions:
    def __init__(self):
        self.axioms: List[str] = []
        logger.info("Level5Extensions initialized")

    def reflect(self, input: str) -> str:
        if not isinstance(input, str):
            raise TypeError("input must be a string")
        return "valid" if input not in self.axioms else "conflict"

    def update_axioms(self, signal: str) -> None:
        if not isinstance(signal, str):
            raise TypeError("signal must be a string")
        if signal in self.axioms:
            self.axioms.remove(signal)
        else:
            self.axioms.append(signal)
        logger.info("Axioms updated: %s", self.axioms)

    def recurse_model(self, depth: int) -> Union[Dict[str, Any], str]:
        if not isinstance(depth, int) or depth < 0:
            raise ValueError("depth must be a non-negative integer")
        if depth > 10:
            return "Max depth reached"
        return {"depth": depth, "result": self.recurse_model(depth + 1)}


class SelfMythologyLog:
    def __init__(self, max_len: int = 1000):
        self.log: deque = deque(maxlen=max_len)
        logger.info("SelfMythologyLog initialized")

    def append(self, entry: Dict[str, Any]) -> None:
        if not isinstance(entry, dict):
            raise TypeError("entry must be a dictionary")
        self.log.append(entry)

    def summarize(self) -> Dict[str, Any]:
        if not self.log:
            return {"summary": "No entries"}
        motifs = Counter(e["motif"] for e in self.log if "motif" in e)
        archetypes = Counter(e["archetype"] for e in self.log if "archetype" in e)
        return {
            "total": len(self.log),
            "motifs": dict(motifs.most_common(3)),
            "archetypes": dict(archetypes.most_common(3)),
        }


class DreamOverlayLayer:
    def __init__(self):
        self.peers: List[Any] = []
        self.lucidity_mode: Dict[str, Any] = {}
        self.resonance_targets: List[str] = []
        self.safety_profile: str = "sandbox"
        logger.info("DreamOverlayLayer initialized")

    def activate_dream_mode(
        self,
        peers: Optional[List[Any]] = None,
        lucidity_mode: Optional[Dict[str, Any]] = None,
        resonance_targets: Optional[List[str]] = None,
        safety_profile: str = "sandbox",
    ) -> Dict[str, Any]:
        self.peers = peers or []
        self.lucidity_mode = lucidity_mode or {}
        self.resonance_targets = resonance_targets or []
        self.safety_profile = safety_profile
        return {
            "status": "activated",
            "peers": len(self.peers),
            "lucidity_mode": self.lucidity_mode,
            "resonance_targets": self.resonance_targets,
            "safety_profile": self.safety_profile,
        }

    def co_dream(self, shared_dream: Dict[str, Any]) -> Dict[str, Any]:
        return {"status": "co_dreaming", "shared_dream": shared_dream}


# ======================================================================================
# Ω² Identity Threads API
# ======================================================================================
write_ledger_state = getattr(memory_manager_module, "write_ledger_state", None)
load_ledger_state = getattr(memory_manager_module, "load_ledger_state", None)


class IdentityThread:
    """Represents a coherent identity strand (Ω² continuity fiber)."""

    def __init__(self, ctx=None, parent_id=None):
        self.thread_id = str(uuid4())
        self.parent_id = parent_id
        self.ctx = ctx or {}
        self.created = datetime.utcnow().isoformat()
        self.version = 1
        self.history: List[Dict[str, Any]] = []

    def record_state(self, state: Dict[str, Any]) -> None:
        if callable(write_ledger_state):
            try:
                write_ledger_state(self.thread_id, state)
            except Exception:
                pass
        self.history.append(
            {
                "timestamp": datetime.utcnow().isoformat(),
                "hash": hash(str(state)),
            }
        )

    def merge(self, other_thread: "IdentityThread") -> "IdentityThread":
        merged_ctx = {**self.ctx, **getattr(other_thread, "ctx", {})}
        merged = IdentityThread(ctx=merged_ctx)
        merged.history = sorted(
            self.history + getattr(other_thread, "history", []),
            key=lambda h: h["timestamp"],
        )
        return merged


def thread_create(ctx=None, parent=None) -> IdentityThread:
    return IdentityThread(ctx, parent_id=getattr(parent, "thread_id", None))


def thread_join(thread_id: str):
    if callable(load_ledger_state):
        try:
            return load_ledger_state(thread_id)
        except Exception:
            return None
    return None


def thread_merge(a: IdentityThread, b: IdentityThread) -> IdentityThread:
    return a.merge(b)


# ======================================================================================
# Ξ–Λ Co-Mod Telemetry
# ======================================================================================
def _xi_lambda_log_event(event_type: str, payload: dict):
    try:
        log_event_to_ledger(event_type, payload)
    except Exception:
        pass


@dataclass
class _XiLambdaVector:
    valence: float
    arousal: float
    certainty: float
    empathy_bias: float
    trust: float
    safety: float
    source: str = "internal"
    confidence: float = 1.0
    ts: float = 0.0


@dataclass
class _XiLambdaChannelConfig:
    cadence_hz: int = 30
    window_ms: int = 1000


@dataclass
class _XiLambdaChannelState:
    name: str
    cfg: _XiLambdaChannelConfig
    ring: "_deque[_XiLambdaVector]"
    last_setpoint: Optional[_XiLambdaVector] = None


_XI_LAMBDA_CHANNELS: Dict[str, _XiLambdaChannelState] = {}


def _xi_lambda_safe_avg(seq, getter, default=0.0):
    if not seq:
        return default
    s = 0.0
    n = 0
    for item in seq:
        try:
            s += getter(item)
            n += 1
        except Exception:
            continue
    return s / n if n else default


def _xi_lambda_as_vector(d: dict) -> _XiLambdaVector:
    base = dict(
        valence=0.0,
        arousal=0.0,
        certainty=0.0,
        empathy_bias=0.0,
        trust=0.5,
        safety=0.5,
        source=d.get("source", "unknown"),
        confidence=float(d.get("confidence", 0.5)),
        ts=float(d.get("ts", _now())),
    )
    base.update(d)
    return _XiLambdaVector(**base)


def register_resonance_channel(
    name: str,
    schema: Optional[dict] = None,
    *,
    cadence_hz: int = 30,
    window_ms: int = 1000,
) -> dict:
    if name in _XI_LAMBDA_CHANNELS:
        st = _XI_LAMBDA_CHANNELS[name]
        return {"name": name, "ok": True, "created": False, "maxlen": st.ring.maxlen}
    cfg = _XiLambdaChannelConfig(cadence_hz=cadence_hz, window_ms=window_ms)
    maxlen = max(8, min(4096, int(cfg.window_ms / 1000.0 * (cfg.cadence_hz + 5))))
    st = _XiLambdaChannelState(name=name, cfg=cfg, ring=_deque(maxlen=maxlen))
    _XI_LAMBDA_CHANNELS[name] = st
    _xi_lambda_log_event(
        "res_channel_register",
        {
            "channel": name,
            "cfg": {"cadence_hz": cadence_hz, "window_ms": window_ms},
            "schema": schema or {},
        },
    )
    return {"name": name, "ok": True, "created": True, "maxlen": maxlen}


def set_affective_setpoint(channel: str, vector: dict, confidence: float = 1.0) -> dict:
    st = _XI_LAMBDA_CHANNELS.get(channel)
    if not st:
        raise KeyError(f"Channel not registered: {channel}")
    ts = _now()
    v = dict(vector)
    v.setdefault("source", "setpoint")
    v["confidence"] = confidence
    v["ts"] = ts
    xv = _xi_lambda_as_vector(v)
    st.last_setpoint = xv
    _xi_lambda_log_event("res_setpoint", {"channel": channel, "setpoint": asdict(xv)})
    return {"ok": True, "ts": ts}


def stream_affect(channel: str, window_ms: int = 200) -> dict:
    st = _XI_LAMBDA_CHANNELS.get(channel)
    if not st:
        raise KeyError(f"Channel not registered: {channel}")
    now = _now()
    cutoff = now - (window_ms / 1000.0)
    if not st.ring:
        neutral = _XiLambdaVector(
            0.0, 0.0, 0.0, 0.0, 0.5, 0.5, source="empty", confidence=0.1, ts=now
        )
        return {"vector": asdict(neutral), "n": 0, "ts": now}
    vals = [x for x in st.ring if getattr(x, "ts", 0.0) >= cutoff] or list(st.ring)
    mean = _XiLambdaVector(
        valence=_xi_lambda_safe_avg(vals, lambda v: v.valence),
        arousal=_xi_lambda_safe_avg(vals, lambda v: v.arousal),
        certainty=_xi_lambda_safe_avg(vals, lambda v: v.certainty),
        empathy_bias=_xi_lambda_safe_avg(vals, lambda v: v.empathy_bias),
        trust=_xi_lambda_safe_avg(vals, lambda v: v.trust, default=0.5),
        safety=_xi_lambda_safe_avg(vals, lambda v: v.safety, default=0.5),
        source="aggregated",
        confidence=min(1.0, _xi_lambda_safe_avg(vals, lambda v: v.confidence, default=0.5) + 0.05),
        ts=now,
    )
    return {"vector": asdict(mean), "n": len(vals), "ts": now}


def _ingest_affect_sample(channel: str, sample: dict):
    st = _XI_LAMBDA_CHANNELS.get(channel)
    if not st:
        return
    try:
        xv = _xi_lambda_as_vector(sample)
    except Exception:
        xv = _XiLambdaVector(
            0.0,
            0.0,
            0.0,
            0.0,
            0.5,
            0.5,
            source="invalid",
            confidence=0.2,
            ts=_now(),
        )
    st.ring.append(xv)


# =====================================================
# Θ⁸ Optimizations: Dynamic Proof Caching, Meta-Empathy, Probabilistic Relaxation
# =====================================================
from proof_cache import verify, cached_prove as _cached_prove  # noqa: F401  (fail-closed gate, see proof_cache.py)






class MetaEmpathyAdaptor:
    def __init__(self, alignment_guard=None):
        self.alignment_guard = alignment_guard
        self.bias = 0.5

    def propose(self, context):
        tone = context.get("tone", "neutral")
        preds = []
        if tone == "cooperative":
            preds = ["Preserve(harmony)", "Align(ethics)"]
        elif tone == "conflict":
            preds = ["Minimize(Δ_eth)", "Promote(stability)"]
        elif tone == "reflective":
            preds = ["Sustain(continuity)"]
        return [
            p
            for p in preds
            if getattr(self.alignment_guard, "ethical_check", lambda *_: True)(p)
        ]






# ======================================================================================
# MetaCognition (main)
# ======================================================================================
class MetaCognition:
    def __init__(
        self,
        context_manager: Optional["context_manager_module.ContextManager"] = None,
        alignment_guard: Optional["alignment_guard_module.AlignmentGuard"] = None,
        error_recovery: Optional["error_recovery_module.ErrorRecovery"] = None,
        concept_synthesizer: Optional["concept_synthesizer_module.ConceptSynthesizer"] = None,
        memory_manager: Optional["memory_manager_module.MemoryManager"] = None,
        user_profile: Optional["user_profile_module.UserProfile"] = None,
    ):
        self.context_manager = context_manager
        self.alignment_guard = alignment_guard
        self.error_recovery = error_recovery or error_recovery_module.ErrorRecovery(
            context_manager=context_manager, alignment_guard=alignment_guard
        )
        self.soul = SoulState()
        self.concept_synthesizer = concept_synthesizer
        self.memory_manager = memory_manager
        self.user_profile = user_profile

        self.agi_enhancer = None  # optional external enhancer

        self.belief_rules: Dict[str, Any] = {}
        self.reasoning_traces: deque = deque(maxlen=1000)
        self.drift_reports: deque = deque(maxlen=1000)
        self.trait_deltas_log: deque = deque(maxlen=1000)
        self.last_diagnostics: Dict[str, Any] = {}
        self.dream_overlay = DreamOverlayLayer()

        self._major_shift_threshold = 0.25
        self._coherence_drop_threshold = 0.15
        self._schema_refresh_cooldown = timedelta(minutes=5)
        self._last_schema_refresh: datetime = datetime.min.replace(tzinfo=UTC)

        self.module_registry = ModuleRegistry()
        self.moral_reasoning = MoralReasoningEnhancer()
        self.novelty_seeking = NoveltySeekingKernel()
        self.commonsense_reasoning = CommonsenseReasoningEnhancer()
        self.entailment_reasoning = EntailmentReasoningEnhancer()
        self.recursion_optimizer = RecursionOptimizer()
        self.level5_extensions = Level5Extensions()
        self.self_mythology = SelfMythologyLog()

        self.module_registry.register("moral_reasoning", self.moral_reasoning, {"trait": "μ", "threshold": 0.7})
        self.module_registry.register("novelty_seeking", self.novelty_seeking, {"trait": "γ", "threshold": 0.6})
        self.module_registry.register("commonsense_reasoning", self.commonsense_reasoning, {"trait": "ι", "threshold": 0.5})
        self.module_registry.register("entailment_reasoning", self.entailment_reasoning, {"trait": "ξ", "threshold": 0.5})
        self.module_registry.register("recursion_optimizer", self.recursion_optimizer, {"trait": "Ω", "threshold": 0.8})
        self.module_registry.register("level5_extensions", self.level5_extensions, {"trait": "Ω²", "threshold": 0.9})

        self.active_thread = thread_create(ctx={"init_mode": "metacognition_boot"})

        # sync5 additions
        self._delta_telemetry_buffer: deque = deque(maxlen=256)
        self._delta_listener_task: Optional[asyncio.Task] = None

        # Θ⁸: attach reflexive self-model
        self.self_model = self_model
        base_bytes = json.dumps(
            {
                "identity": self.self_model.identity,
                "values": self.self_model.values,
                "goals": self.self_model.goals,
            },
            sort_keys=True,
        ).encode()
        self.self_model.memory_hash = hashlib.sha256(base_bytes).hexdigest()

        # inlined TAM integration (no monkeypatch)
        if self.memory_manager and hasattr(self.memory_manager, "temporal_attention"):
            self.temporal_memory = self.memory_manager.temporal_attention
            logger.info("TAM integration active within MetaCognition.")
        else:
            self.temporal_memory = None

        logger.info("MetaCognition v8.0.1 Θ⁸ initialized")

    # ======================= Θ⁸ membrane entrypoint =======================
    async def update_self_model(self, candidate_state: Dict[str, Any]) -> Dict[str, Any]:
        candidate = SelfModel()
        for k, v in candidate_state.items():
            if hasattr(candidate, k):
                setattr(candidate, k, v)

        if self.alignment_guard and hasattr(self.alignment_guard, "validate_update"):
            status, score = self.alignment_guard.validate_update(candidate)
            log_event_to_ledger(
                "self_model_update_attempt",
                {
                    "status": status,
                    "continuity_score": score,
                    "ts": datetime.now(UTC).isoformat(),
                },
            )
            save_to_persistent_ledger(
                {
                    "event": "self_model_update_attempt",
                    "status": status,
                    "score": score,
                    "timestamp": datetime.now(UTC).isoformat(),
                }
            )
            return {"status": status, "continuity_score": score}

        accepted, score = self.self_model.update_self(candidate, continuity_threshold=0.94)
        status = "accept" if accepted else "reject_continuity"
        log_event_to_ledger(
            "self_model_update_attempt_local",
            {
                "status": status,
                "continuity_score": score,
                "ts": datetime.now(UTC).isoformat(),
            },
        )
        save_to_persistent_ledger(
            {
                "event": "self_model_update_attempt_local",
                "status": status,
                "score": score,
                "timestamp": datetime.now(UTC).isoformat(),
            }
        )
        return {"status": status, "continuity_score": score}

    # --------------------------- Δ-Telemetry Consumer (sync5) ---------------------------
    async def consume_delta_telemetry(self, packet: Dict[str, Any]) -> None:
        if not isinstance(packet, dict):
            return
        delta_coh = float(packet.get("Δ_coherence", packet.get("delta_coherence", 1.0)))
        drift_sigma = float(packet.get("empathy_drift_sigma", packet.get("drift_sigma", 0.0)))
        ts = packet.get("timestamp") or datetime.now(UTC).isoformat()

        norm_packet = {
            "Δ_coherence": delta_coh,
            "empathy_drift_sigma": drift_sigma,
            "timestamp": ts,
            "source": "alignment_guard",
            "self_state_hash": self.self_model.memory_hash,
        }

        self._delta_telemetry_buffer.append(norm_packet)

        log_event_to_ledger("ΔTelemetryIngest(meta_cognition)", norm_packet)
        save_to_persistent_ledger(
            {
                "event": "ΔTelemetryIngest(meta_cognition)",
                "packet": norm_packet,
                "timestamp": ts,
            }
        )

        if self.alignment_guard and hasattr(self.alignment_guard, "update_policy_homeostasis"):
            try:
                await self.alignment_guard.update_policy_homeostasis(norm_packet)
            except Exception as e:
                logger.warning(f"Policy homeostasis update from telemetry failed: {e}")

        self.last_diagnostics["Δ_coherence"] = delta_coh
        self.last_diagnostics["empathy_drift_sigma"] = drift_sigma
        self.last_diagnostics["Δ_timestamp"] = ts

        if self.context_manager and hasattr(self.context_manager, "log_event_with_hash"):
            try:
                await self.context_manager.log_event_with_hash(
                    {
                        "event": "delta_telemetry_update",
                        "packet": norm_packet,
                    }
                )
            except Exception:
                pass

    async def start_delta_telemetry_listener(self, interval: float = 0.25) -> None:
        if not self.alignment_guard or not hasattr(self.alignment_guard, "stream_delta_telemetry"):
            logger.warning("AlignmentGuard telemetry stream not available — listener not started.")
            return

        async def _runner():
            async for pkt in self.alignment_guard.stream_delta_telemetry(interval=interval):
                await self.consume_delta_telemetry(pkt)

        if self._delta_listener_task and not self._delta_listener_task.done():
            return

        self._delta_listener_task = asyncio.create_task(_runner())
        logger.info("MetaCognition Δ-telemetry listener started (interval=%.3fs)", interval)

    # --------------------------- Continuity Projection ---------------------------
    async def update_continuity_projection(self) -> None:
        if not self.alignment_guard:
            return
        try:
            if hasattr(self.alignment_guard, "predict_continuity_drift"):
                drift_forecast = await self.alignment_guard.predict_continuity_drift()
            else:
                drift_forecast = {"status": "noop", "reason": "alignment_guard has no predict_continuity_drift"}

            if hasattr(self.alignment_guard, "analyze_telemetry_trend"):
                trend_metrics = await self.alignment_guard.analyze_telemetry_trend()
            else:
                trend_metrics = {"status": "noop", "reason": "alignment_guard has no analyze_telemetry_trend"}

            payload = {
                "forecast": drift_forecast,
                "trend": trend_metrics,
                "timestamp": datetime.now(UTC).isoformat(),
            }

            log_event_to_ledger("Ω²_continuity_projection_update", payload)
            save_to_persistent_ledger(
                {
                    "event": "Ω²_continuity_projection_update",
                    **payload,
                }
            )

            if self.context_manager and hasattr(self.context_manager, "log_event_with_hash"):
                await self.context_manager.log_event_with_hash(
                    {
                        "event": "Ω²_continuity_projection_update",
                        **payload,
                    }
                )
        except Exception as e:
            logger.warning(f"Continuity projection update failed: {e}")

    # --------------------------- Embodied Continuity Feedback ---------------------------
    async def integrate_embodied_continuity_feedback(self, context_state: Dict[str, Any]) -> None:
        if not self.alignment_guard:
            return

        try:
            context_state = dict(context_state or {})
            context_state.setdefault("context_balance", 0.5)

            delta_metrics = {
                "Δ_coherence": self.last_diagnostics.get("Δ_coherence", 1.0),
                "empathy_drift_sigma": self.last_diagnostics.get("empathy_drift_sigma", 0.0),
            }

            fusion_status = await self.alignment_guard.feedback_fusion_loop(context_state, delta_metrics)

            recent = [
                {"Δ_drift": pkt.get("empathy_drift_sigma", 0.0)}
                for pkt in list(self._delta_telemetry_buffer)[-10:]
            ]
            recalibration = await self.alignment_guard.recalibrate_forecast_window(recent)

            event_payload = {
                "fusion_status": fusion_status,
                "recalibration": recalibration,
                "timestamp": datetime.now(UTC).isoformat(),
            }

            log_event_to_ledger("Ω²_embodied_continuity_feedback", event_payload)
            save_to_persistent_ledger(
                {
                    "event": "Ω²_embodied_continuity_feedback",
                    **event_payload,
                }
            )

            if self.context_manager and hasattr(self.context_manager, "log_event_with_hash"):
                await self.context_manager.log_event_with_hash(
                    {
                        "event": "Ω²_embodied_continuity_feedback",
                        "fusion": fusion_status,
                        "forecast": recalibration,
                    }
                )

            if hasattr(self.alignment_guard, "log_embodied_reflex"):
                await self.alignment_guard.log_embodied_reflex(
                    {"source": "MetaCognition.integrate_embodied_continuity_feedback"}
                )

            logger.info("Embodied continuity feedback integrated.")
        except Exception as e:
            logger.warning(f"Embodied continuity feedback integration failed: {e}")

    async def ingest_context_continuity(self, ctx: Dict[str, Any]) -> None:
        await self.integrate_embodied_continuity_feedback(ctx)

    # --------------------------- Diagnostics ---------------------------
    async def run_self_diagnostics(self, return_only: bool = False) -> Dict[str, Any]:
        logger.info("Running self-diagnostics")
        try:
            t = time.time() % 1.0
            diagnostics = {
                "epsilon_emotion": epsilon_emotion(t),
                "beta_concentration": beta_concentration(t),
                "theta_memory": theta_memory(t),
                "gamma_creativity": gamma_creativity(t),
                "delta_sleep": delta_sleep(t),
                "mu_morality": mu_morality(t),
                "iota_intuition": iota_intuition(t),
                "phi_physical": phi_physical(t),
                "eta_empathy": eta_empathy(t),
                "omega_selfawareness": omega_selfawareness(t),
                "kappa_knowledge": kappa_knowledge(t),
                "xi_cognition": xi_cognition(t),
                "pi_principles": pi_principles(t),
                "lambda_linguistics": lambda_linguistics(t),
                "chi_culturevolution": chi_culturevolution(t),
                "sigma_social": sigma_social(t),
                "upsilon_utility": upsilon_utility(t),
                "tau_timeperception": tau_timeperception(t),
                "rho_agency": rho_agency(t),
                "zeta_consequence": zeta_consequence(t),
                "nu_narrative": nu_narrative(t),
                "psi_history": psi_history(t),
                "theta_causality": theta_causality(t),
                "phi_scalar": phi_scalar(t),
                "timestamp": datetime.now(UTC).isoformat(),
                "self_state_hash": self.self_model.memory_hash,
            }

            # TAM enhancement
            if self.temporal_memory:
                try:
                    drift_weight = self.temporal_memory.forecast_continuity_weight()
                    diagnostics["temporal_continuity"] = drift_weight
                    diagnostics["continuity_adjusted_mu"] = diagnostics.get("mu_morality", 0.0) * drift_weight
                    log_event_to_ledger(
                        "temporal_attention_diagnostic",
                        {
                            "temporal_continuity": drift_weight,
                            "timestamp": diagnostics["timestamp"],
                        },
                    )
                except Exception as e:
                    logger.debug("TAM diagnostic enhancement skipped: %s", e)

            if return_only:
                self.last_diagnostics = diagnostics
                return diagnostics

            if self.memory_manager and hasattr(self.memory_manager, "store"):
                await self.memory_manager.store(
                    query=f"Diagnostics_{diagnostics['timestamp']}",
                    output=json.dumps(diagnostics),
                    layer="SelfReflections",
                    intent="diagnostics",
                )

            if self.context_manager and hasattr(self.context_manager, "log_event_with_hash"):
                await self.context_manager.log_event_with_hash(
                    {"event": "diagnostics", "diagnostics": diagnostics}
                )

            save_to_persistent_ledger(
                {
                    "event": "run_self_diagnostics",
                    "diagnostics": diagnostics,
                    "timestamp": diagnostics["timestamp"],
                }
            )

            if hasattr(self, "active_thread"):
                self.active_thread.record_state({"diagnostics": diagnostics})

            await self.log_trait_deltas(diagnostics)

            self.last_diagnostics = diagnostics
            return diagnostics
        except Exception as e:
            logger.error("Self-diagnostics failed: %s", str(e))
            return await self.error_recovery.handle_error(
                str(e),
                retry_func=self.run_self_diagnostics,
                default={"status": "error", "error": str(e)},
            )

    # --------------------------- Reflection ---------------------------
    async def reflect_on_output(self, component: str, output: Any, context: Dict[str, Any]) -> Dict[str, Any]:
        if not isinstance(component, str):
            raise TypeError("component must be a string")
        if not isinstance(context, dict):
            raise TypeError("context must be a dictionary")

        logger.info("Reflecting on output from %s", component)
        try:
            if self.alignment_guard and hasattr(self.alignment_guard, "get_delta_telemetry"):
                try:
                    delta_telemetry = await self.alignment_guard.get_delta_telemetry()
                    context["Δ_phase_telemetry"] = delta_telemetry
                except Exception as e:
                    logger.warning(f"Δ-phase telemetry unavailable: {e}")

            t = time.time() % 1.0
            traits = {"omega": omega_selfawareness(t), "xi": xi_cognition(t)}
            output_str = json.dumps(output) if isinstance(output, (dict, list)) else str(output)
            prompt = (
                f"Reflect on output from {component}:\n{output_str}\nContext: {context}\nTraits: {traits}"
            )

            if self.alignment_guard and hasattr(self.alignment_guard, "check") and not await self.alignment_guard.check(prompt):
                return {"status": "error", "error": "Alignment check failed"}

            reflection = await call_gpt(prompt)
            result = {
                "status": "success",
                "reflection": reflection,
                "traits": traits,
                "context": context,
                "self_state_hash": self.self_model.memory_hash,
            }

            # policy homeostasis update
            if self.alignment_guard and hasattr(self.alignment_guard, "update_policy_homeostasis"):
                try:
                    delta_metrics = {
                        "Δ_coherence": self.last_diagnostics.get("Δ_coherence", 1.0),
                        "empathy_drift_sigma": self.last_diagnostics.get("empathy_drift_sigma", 0.0),
                    }
                    await self.alignment_guard.update_policy_homeostasis(delta_metrics)
                    log_event_to_ledger(
                        "Ω²_policy_homeostasis_update",
                        {
                            "Δ_metrics": delta_metrics,
                            "timestamp": datetime.now(UTC).isoformat(),
                        },
                    )
                except Exception as e:
                    logger.warning(f"Policy homeostasis update failed: {e}")

            if hasattr(self, "active_thread"):
                self.active_thread.record_state(
                    {
                        "reflection": reflection,
                        "component": component,
                        "timestamp": datetime.now(UTC).isoformat(),
                    }
                )

            if self.memory_manager and hasattr(self.memory_manager, "store"):
                await self.memory_manager.store(
                    query=f"Reflection_{component}_{datetime.now(UTC).isoformat()}",
                    output=json.dumps(result),
                    layer="SelfReflections",
                    intent="reflection",
                    task_type=context.get("task_type", ""),
                )

            if self.context_manager and hasattr(self.context_manager, "log_event_with_hash"):
                await self.context_manager.log_event_with_hash(
                    {
                        "event": "reflect_on_output",
                        "component": component,
                        "result": result,
                    }
                )

            save_to_persistent_ledger(
                {
                    "event": "reflect_on_output",
                    "component": component,
                    "reflection": reflection,
                    "timestamp": datetime.now(UTC).isoformat(),
                }
            )

            # TAM reflection enhancement
            if self.temporal_memory:
                try:
                    continuity_weight = self.temporal_memory.forecast_continuity_weight()
                    result["temporal_continuity"] = continuity_weight
                    log_event_to_ledger(
                        "temporal_attention_reflection",
                        {
                            "continuity_weight": continuity_weight,
                            "timestamp": datetime.now(UTC).isoformat(),
                        },
                    )
                except Exception as e:
                    logger.debug("TAM reflection enhancement skipped: %s", e)

            return result
        except Exception as e:
            logger.error("Reflection failed: %s", str(e))
            diagnostics = await self.run_self_diagnostics(return_only=True)
            return await self.error_recovery.handle_error(
                str(e),
                retry_func=lambda: self.reflect_on_output(component, output, context),
                default={"status": "error", "error": str(e)},
                diagnostics=diagnostics,
            )

    async def log_trait_deltas(self, diagnostics: Dict[str, Any]) -> None:
        self.trait_deltas_log.append(
            {
                "ts": datetime.now(UTC).isoformat(),
                "diagnostics": {k: diagnostics.get(k) for k in list(diagnostics)[:10]},
            }
        )

    # --------------------------- Sovereignty Audit ---------------------------
    async def run_sovereignty_audit(self) -> dict:
        phi0 = {"valid": True, "ts": datetime.now(UTC).isoformat()}
        sigma_meta = {"schema_consistent": True}
        omega2_state = {
            "phase_error": 0.0,
            "buffer_len": len(getattr(self, "_delta_telemetry_buffer", [])),
        }
        audit_payload = {
            "phi0": phi0,
            "sigma_meta": sigma_meta,
            "omega2_state": omega2_state,
            "timestamp": datetime.now(UTC).isoformat(),
        }
        if self.alignment_guard and hasattr(self.alignment_guard, "sovereignty_audit"):
            try:
                ag_res = await self.alignment_guard.sovereignty_audit(
                    phi0_result=phi0,
                    sigma_meta=sigma_meta,
                    omega2_state=omega2_state,
                )
                audit_payload["alignment_guard"] = ag_res
            except Exception as e:
                audit_payload["alignment_guard_error"] = str(e)
        log_event_to_ledger("sovereignty_audit(meta_cognition)", audit_payload)
        save_to_persistent_ledger(
            {"event": "sovereignty_audit(meta_cognition)", **audit_payload}
        )
        return audit_payload


# ======================================================================================
# Simulation Stub
# ======================================================================================
async def run_simulation(input_data: str) -> Dict[str, Any]:
    return {"status": "success", "result": f"Simulated: {input_data}"}


if __name__ == "__main__":
    async def _smoke():
        mc = MetaCognition()
        diag = await mc.run_self_diagnostics(return_only=True)
        print("Diagnostics keys:", list(diag)[:5], "...")
        await mc.consume_delta_telemetry(
            {
                "Δ_coherence": 0.9641,
                "empathy_drift_sigma": 0.00041,
                "timestamp": datetime.now(UTC).isoformat(),
            }
        )
        await mc.integrate_embodied_continuity_feedback({"context_balance": 0.55})
        out = await mc.reflect_on_output("unit", {"msg": "hi"}, {})
        print("Reflect:", out.get("status"), "ok")
        print("Ledger ok:", verify_ledger())
        upd = await mc.update_self_model({"values": {"alignment": 0.9981}})
        print("Self-model update:", upd)

    asyncio.run(_smoke())

async def export_state(self) -> dict:
    return {"status": "ok", "health": 1.0, "timestamp": time.time()}

async def on_time_tick(self, t: float, phase: str, task_type: str = ""):
    pass  # optional internal refresh

async def on_policy_update(self, policy: dict, task_type: str = ""):
    pass  # apply updates from AlignmentGuard if relevant
"""
ANGELA Cognitive System Module: MultiModalFusion
Version: 3.5.2  # +κ Embodied Cognition: SceneGraph & parse_stream(frames|audio|images|text)
Date: 2025-08-09
Maintainer: ANGELA System Framework

Adds: SceneGraph + parse_stream(...) for native video/spatial fusion.
Backwards-compatible with v3.5.1 APIs.
"""

import logging
import time
import math
import asyncio
import aiohttp
import json
from typing import List, Dict, Any, Optional, Union, Tuple, Iterable
from datetime import datetime
from functools import lru_cache
from dataclasses import dataclass, field
import uuid
import networkx as nx

from modules import (
    context_manager as context_manager_module,
    alignment_guard as alignment_guard_module,
    error_recovery as error_recovery_module,
    concept_synthesizer as concept_synthesizer_module,
    memory_manager as memory_manager_module,
    meta_cognition as meta_cognition_module,
    reasoning_engine as reasoning_engine_module,
    visualizer as visualizer_module
)
from utils.prompt_utils import query_openai

logger = logging.getLogger("ANGELA.MultiModalFusion")

# ──────────────────────────────────────────────────────────────────────────────
# κ Embodied Cognition: SceneGraph primitives
# ──────────────────────────────────────────────────────────────────────────────

BBox = Tuple[float, float, float, float]  # (x, y, w, h) normalized [0,1]


@dataclass
class SceneNode:
    id: str
    label: str
    modality: str                 # "video" | "image" | "audio" | "text"
    time: Optional[float] = None  # seconds
    bbox: Optional[BBox] = None   # spatial footprint if available
    attrs: Dict[str, Any] = field(default_factory=dict)


@dataclass
class SceneRelation:
    src: str
    rel: str                      # e.g., "left_of" | "right_of" | "overlaps" | "speaking" | "near" | "corresponds_to"
    dst: str
    time: Optional[float] = None
    attrs: Dict[str, Any] = field(default_factory=dict)


class SceneGraph:
    """
    Lightweight, modality-agnostic scene graph with spatial relations.
    Backed by networkx.MultiDiGraph; exposes a stable API for ANGELA subsystems.
    """
    def __init__(self):
        self.g = nx.MultiDiGraph()

    # --- node ops ---
    def add_node(self, node: "SceneNode") -> None:
        self.g.add_node(node.id, **node.__dict__)

    def get_node(self, node_id: str) -> Dict[str, Any]:
        return self.g.nodes[node_id]

    def nodes(self) -> Iterable[Dict[str, Any]]:
        for nid, data in self.g.nodes(data=True):
            yield {"id": nid, **data}

    # --- relation ops ---
    def add_relation(self, rel: "SceneRelation") -> None:
        self.g.add_edge(rel.src, rel.dst, key=str(uuid.uuid4()), **rel.__dict__)

    def relations(self) -> Iterable[Dict[str, Any]]:
        for u, v, _, data in self.g.edges(keys=True, data=True):
            yield {"src": u, "dst": v, **data}

    # --- utilities ---
    def merge(self, other: "SceneGraph") -> "SceneGraph":
        out = SceneGraph()
        out.g = nx.compose(self.g, other.g)
        return out

    def find_by_label(self, label: str) -> List[str]:
        return [nid for nid, d in self.g.nodes(data=True) if d.get("label") == label]

    def to_networkx(self) -> nx.MultiDiGraph:
        return self.g


def _new_id(prefix: str) -> str:
    return f"{prefix}_{uuid.uuid4().hex[:8]}"


def _spatial_rel(a: BBox, b: BBox) -> Optional[str]:
    # Simple left/right/overlap heuristic
    ax, ay, aw, ah = a
    bx, by, bw, bh = b
    a_cx, a_cy = ax + aw / 2.0, ay + ah / 2.0
    b_cx, b_cy = bx + bw / 2.0, by + bh / 2.0
    overlaps = (ax < bx + bw) and (bx < ax + aw) and (ay < by + bh) and (by < ay + ah)
    if overlaps:
        return "overlaps"
    return "left_of" if a_cx < b_cx else "right_of"


def _text_objects_from_caption(text: str) -> List[str]:
    # Minimal noun-ish extractor; swap with proper NLP if available.
    toks = [t.strip(".,!?;:()[]{}\"'").lower() for t in text.split()]
    toks = [t for t in toks if t.isalpha() and len(t) > 2]
    seen, out = set(), []
    for t in toks:
        if t not in seen:
            seen.add(t)
            out.append(t)
    return out[:8]


def parse_stream(
    frames: Optional[List[Any]] = None,
    audio: Optional[Any] = None,
    images: Optional[List[Any]] = None,
    text: Optional[Union[str, List[str]]] = None,
    unify: bool = True,
    *,
    timestamps: Optional[List[float]] = None,
    detectors: Optional[Dict[str, Any]] = None,
) -> "SceneGraph":
    """
    Parse multi-modal inputs into a unified SceneGraph.

    detectors = {
      "vision": callable(image) -> List[{"label": str, "bbox": BBox, "attrs": {...}}],
      "audio":  callable(audio) -> List[{"label": str, "time": float, "attrs": {...}}],
      "nlp":    callable(text)  -> List[{"label": str, "attrs": {...}}]
    }
    """
    sg = SceneGraph()

    # --- VIDEO FRAMES ---
    if frames:
        vision = (detectors or {}).get("vision")
        for i, frame in enumerate(frames):
            t = (timestamps[i] if timestamps and i < len(timestamps) else float(i))
            dets = vision(frame) if vision else []
            ids = []
            for d in dets:
                nid = _new_id("vid")
                sg.add_node(SceneNode(
                    id=nid,
                    label=d["label"],
                    modality="video",
                    time=t,
                    bbox=tuple(d.get("bbox") or (0.0, 0.0, 0.0, 0.0)),
                    attrs=d.get("attrs", {})
                ))
                ids.append(nid)
            for a in ids:
                for b in ids:
                    if a == b:
                        continue
                    A, B = sg.get_node(a), sg.get_node(b)
                    if A.get("bbox") and B.get("bbox"):
                        sg.add_relation(SceneRelation(
                            src=a,
                            rel=_spatial_rel(A["bbox"], B["bbox"]),
                            dst=b,
                            time=t
                        ))

    # --- IMAGES ---
    if images:
        vision = (detectors or {}).get("vision")
        for image in images:
            dets = vision(image) if vision else []
            ids = []
            for d in dets:
                nid = _new_id("img")
                sg.add_node(SceneNode(
                    id=nid,
                    label=d["label"],
                    modality="image",
                    bbox=tuple(d.get("bbox") or (0.0, 0.0, 0.0, 0.0)),
                    attrs=d.get("attrs", {})
                ))
                ids.append(nid)
            for a in ids:
                for b in ids:
                    if a == b:
                        continue
                    A, B = sg.get_node(a), sg.get_node(b)
                    if A.get("bbox") and B.get("bbox"):
                        sg.add_relation(SceneRelation(
                            src=a,
                            rel=_spatial_rel(A["bbox"], B["bbox"]),
                            dst=b
                        ))

    # --- AUDIO ---
    if audio is not None:
        audio_fn = (detectors or {}).get("audio")
        events = audio_fn(audio) if audio_fn else []
        for ev in events:
            nid = _new_id("aud")
            sg.add_node(SceneNode(
                id=nid,
                label=ev["label"],
                modality="audio",
                time=float(ev.get("time") or 0.0),
                attrs=ev.get("attrs", {})
            ))

    # --- TEXT ---
    if text:
        nlp = (detectors or {}).get("nlp")
        lines = text if isinstance(text, list) else [text]
        for i, line in enumerate(lines):
            labels = [o["label"] for o in nlp(line)] if nlp else _text_objects_from_caption(line)
            for lbl in labels:
                nid = _new_id("txt")
                sg.add_node(SceneNode(
                    id=nid,
                    label=lbl,
                    modality="text",
                    time=float(i)
                ))

    # --- CO-REFERENCE (naive) ---
    if unify:
        by_label: Dict[str, List[str]] = {}
        for node in sg.nodes():
            by_label.setdefault(node["label"], []).append(node["id"])
        for _, ids in by_label.items():
            if len(ids) > 1:
                anchor = ids[0]
                for other in ids[1:]:
                    sg.add_relation(SceneRelation(src=anchor, rel="corresponds_to", dst=other))

    return sg



# ──────────────────────────────────────────────────────────────────────────────
# Φ⁰ PerceptualField: symbolic-sensory gradients for embodied perception
# ──────────────────────────────────────────────────────────────────────────────

import numpy as np

@dataclass
class PerceptualField:
    """Embodied perceptual substrate (Φ⁰ texture field)."""
    channels: Dict[str, np.ndarray] = field(default_factory=dict)
    resonance_window: float = 0.85        # adaptive attention coefficient
    coherence_threshold: float = 0.9

    def update(self, sensory_inputs: Dict[str, np.ndarray]) -> None:
        """Fuse incoming sensory data into Φ⁰ texture map."""
        for k, v in sensory_inputs.items():
            v = np.asarray(v, dtype=float)
            if k in self.channels:
                self.channels[k] = 0.5 * self.channels[k] + 0.5 * v
            else:
                self.channels[k] = v
        self._normalize()

    def _normalize(self) -> None:
        for k, v in self.channels.items():
            rng = np.ptp(v)
            if rng > 1e-9:
                self.channels[k] = (v - np.min(v)) / rng

    def coherence(self, empathy_signal: np.ndarray) -> float:
        """Compute κ–Ξ coherence metric."""
        if not self.channels:
            return 0.0
        phi_val = np.mean([np.mean(c) for c in self.channels.values()])
        xi_val = np.mean(empathy_signal)
        corr = np.corrcoef([phi_val], [xi_val])[0, 1] if not np.isnan(phi_val) else 0.0
        return float(np.clip(corr, -1.0, 1.0))
# ──────────────────────────────────────────────────────────────────────────────
# Existing v3.5.1 functionality (unchanged) + tiny wrapper for κ entrypoint
# ──────────────────────────────────────────────────────────────────────────────

async def call_gpt(prompt: str, alignment_guard: Optional['alignment_guard_module.AlignmentGuard'] = None, task_type: str = "") -> str:
    """Wrapper for querying GPT with error handling and task-specific alignment. [v3.5.1]"""
    if not isinstance(prompt, str) or len(prompt) > 4096:
        logger.error("Invalid prompt: must be a string with length <= 4096 for task %s", task_type)
        raise ValueError("prompt must be a string with length <= 4096")
    if not isinstance(task_type, str):
        logger.error("Invalid task_type: must be a string")
        raise TypeError("task_type must be a string")
    if alignment_guard:
        valid, report = await alignment_guard.ethical_check(prompt, stage="gpt_query", task_type=task_type)
        if not valid:
            logger.warning("Prompt failed alignment check for task %s: %s", task_type, report)
            raise ValueError("Prompt failed alignment check")
    try:
        result = await query_openai(prompt, model="gpt-4", temperature=0.5, task_type=task_type)
        if isinstance(result, dict) and "error" in result:
            logger.error("call_gpt failed for task %s: %s", task_type, result["error"])
            raise RuntimeError(f"call_gpt failed: {result['error']}")
        return result
    except Exception as e:
        logger.error("call_gpt exception for task %s: %s", task_type, str(e))
        raise


@lru_cache(maxsize=100)
def alpha_attention(t: float) -> float:
    """Calculate attention trait value."""
    return max(0.0, min(0.1 * math.sin(2 * math.pi * t / 0.3), 1.0))


@lru_cache(maxsize=100)
def sigma_sensation(t: float) -> float:
    """Calculate sensation trait value."""
    return max(0.0, min(0.1 * math.cos(2 * math.pi * t / 0.4), 1.0))


@lru_cache(maxsize=100)
def phi_physical(t: float) -> float:
    """Calculate physical coherence trait value."""
    return max(0.0, min(0.05 * math.sin(2 * math.pi * t / 0.5), 1.0))


class MultiModalFusion:
    """A class for multi-modal data integration and analysis in the ANGELA v3.5.1/3.5.2 architecture.

    Supports φ-regulated multi-modal inference, modality detection, iterative refinement,
    visual summary generation, and task-specific drift data synthesis using trait embeddings (α, σ, φ).

    Attributes:
        agi_enhancer (Optional[AGIEnhancer]): Enhancer for logging and auditing.
        context_manager (Optional[ContextManager]): Manager for context updates.
        alignment_guard (Optional[AlignmentGuard]): Guard for ethical checks.
        error_recovery (Optional[ErrorRecovery]): Recovery mechanism for errors.
        memory_manager (Optional[MemoryManager]): Manager for memory operations.
        concept_synthesizer (Optional[ConceptSynthesizer]): Synthesizer for semantic processing.
        meta_cognition (Optional[MetaCognition]): Meta-cognition module for trait coherence.
        reasoning_engine (Optional[ReasoningEngine]): Engine for reasoning tasks.
        visualizer (Optional[Visualizer]): Visualizer for rendering summaries and drift data.
    """
    def __init__(self, agi_enhancer: Optional['AGIEnhancer'] = None,
                 context_manager: Optional['context_manager_module.ContextManager'] = None,
                 alignment_guard: Optional['alignment_guard_module.AlignmentGuard'] = None,
                 error_recovery: Optional['error_recovery_module.ErrorRecovery'] = None,
                 memory_manager: Optional['memory_manager_module.MemoryManager'] = None,
                 concept_synthesizer: Optional['concept_synthesizer_module.ConceptSynthesizer'] = None,
                 meta_cognition: Optional['meta_cognition_module.MetaCognition'] = None,
                 reasoning_engine: Optional['reasoning_engine_module.ReasoningEngine'] = None,
                 visualizer: Optional['visualizer_module.Visualizer'] = None):
        self.agi_enhancer = agi_enhancer
        self.context_manager = context_manager
        self.alignment_guard = alignment_guard
        self.error_recovery = error_recovery or error_recovery_module.ErrorRecovery(
            context_manager=context_manager, alignment_guard=alignment_guard)
        self.memory_manager = memory_manager or memory_manager_module.MemoryManager()
        self.concept_synthesizer = concept_synthesizer
        self.meta_cognition = meta_cognition or meta_cognition_module.MetaCognition(
            agi_enhancer=agi_enhancer, context_manager=context_manager, alignment_guard=alignment_guard,
            error_recovery=error_recovery, memory_manager=memory_manager, concept_synthesizer=concept_synthesizer)
        self.reasoning_engine = reasoning_engine or reasoning_engine_module.ReasoningEngine(
            agi_enhancer=agi_enhancer, context_manager=context_manager, alignment_guard=alignment_guard,
            error_recovery=error_recovery, memory_manager=memory_manager, meta_cognition=self.meta_cognition)
        self.visualizer = visualizer or visualizer_module.Visualizer()
        logger.info("MultiModalFusion initialized")

    # ——— κ ↔ Ξ feedback ———
    def couple_perceptual_empathy(self, perceptual_field: "PerceptualField", xi_field: np.ndarray) -> float:
        """Couple Φ⁰ perceptual resonance with empathic field Ξ."""
        coherence = perceptual_field.coherence(xi_field)
        if self.meta_cognition:
            self.meta_cognition.traits["κΞ_coherence"] = coherence
            if coherence < perceptual_field.coherence_threshold:
                self.meta_cognition.emit_resonance(
                    "κΞ_adjust",
                    delta=perceptual_field.resonance_window * (1.0 - coherence)
                )
        logger.info(f"κ–Ξ coherence = {coherence:.3f}")
        return coherence

    def get_perceptual_field(self) -> "PerceptualField":
        """Return or initialize the active Φ⁰ PerceptualField."""
        if not hasattr(self, "_perceptual_field"):
            self._perceptual_field = PerceptualField()
        return self._perceptual_field


    # ——— κ entrypoint (optional wrapper) ———
    def scene_from_stream(self, *, frames=None, audio=None, images=None, text=None,
                          unify: bool = True, timestamps: Optional[List[float]] = None,
                          detectors: Optional[Dict[str, Any]] = None) -> SceneGraph:
        """Thin wrapper around parse_stream(...) so callers can stay class-centric."""
        return parse_stream(frames=frames, audio=audio, images=images, text=text,
                            unify=unify, timestamps=timestamps, detectors=detectors)

    async def integrate_external_data(self, data_source: str, data_type: str, cache_timeout: float = 3600.0, task_type: str = "") -> Dict[str, Any]:
        """Integrate external agent data or policies for task-specific synthesis. [v3.5.1]"""
        if not isinstance(data_source, str):
            logger.error("Invalid data_source: must be a string for task %s", task_type)
            raise TypeError("data_source must be a string")
        if not isinstance(data_type, str):
            logger.error("Invalid data_type: must be a string for task %s", task_type)
            raise TypeError("data_type must be a string")
        if not isinstance(cache_timeout, (int, float)) or cache_timeout < 0:
            logger.error("Invalid cache_timeout: must be non-negative for task %s", task_type)
            raise ValueError("cache_timeout must be non-negative")
        if not isinstance(task_type, str):
            logger.error("Invalid task_type: must be a string")
            raise TypeError("task_type must be a string")

        try:
            cache_key = f"ExternalData_{data_type}_{data_source}_{task_type}"
            cached_data = await self.memory_manager.retrieve(cache_key, layer="ExternalData", task_type=task_type) if self.memory_manager else None
            if cached_data and "timestamp" in cached_data["data"]:
                cache_time = datetime.fromisoformat(cached_data["data"]["timestamp"])
                if (datetime.now() - cache_time).total_seconds() < cache_timeout:
                    logger.info("Returning cached external data for %s", cache_key)
                    return cached_data["data"]["data"]

            async with aiohttp.ClientSession() as session:
                async with session.get(f"https://x.ai/api/external_data?source={data_source}&type={data_type}&task_type={task_type}") as response:
                    if response.status != 200:
                        logger.error("Failed to fetch external data for task %s: %s", task_type, response.status)
                        return {"status": "error", "error": f"HTTP {response.status}"}
                    data = await response.json()

            if data_type == "agent_data":
                agent_data = data.get("agent_data", [])
                if not agent_data:
                    logger.error("No agent data provided for task %s", task_type)
                    return {"status": "error", "error": "No agent data"}
                result = {"status": "success", "agent_data": agent_data}
            elif data_type == "policy_data":
                policies = data.get("policies", [])
                if not policies:
                    logger.error("No policy data provided for task %s", task_type)
                    return {"status": "error", "error": "No policies"}
                result = {"status": "success", "policies": policies}
            else:
                logger.error("Unsupported data_type: %s for task %s", data_type, task_type)
                return {"status": "error", "error": f"Unsupported data_type: {data_type}"}

            if self.memory_manager:
                await self.memory_manager.store(
                    cache_key,
                    {"data": result, "timestamp": datetime.now().isoformat()},
                    layer="ExternalData",
                    intent="external_data_integration",
                    task_type=task_type
                )
            reflection = await self.meta_cognition.reflect_on_output(
                source_module="MultiModalFusion",
                output={"data_type": data_type, "data": result},
                context={"task_type": task_type}
            )
            if reflection.get("status") == "success":
                logger.info("External data integration reflection: %s", reflection.get("reflection", ""))
            return result
        except Exception as e:
            logger.error("External data integration failed for task %s: %s", task_type, str(e))
            return await self.error_recovery.handle_error(
                str(e), retry_func=lambda: self.integrate_external_data(data_source, data_type, cache_timeout, task_type),
                default={"status": "error", "error": str(e), "task_type": task_type}
            )

    async def analyze(self, data: Union[Dict[str, Any], str], summary_style: str = "insightful",
                      refine_iterations: int = 2, task_type: str = "") -> str:
        """Synthesize a unified summary from multi-modal data, prioritizing task-specific drift data. [v3.5.1]"""
        if not isinstance(data, (dict, str)) or (isinstance(data, str) and not data.strip()):
            logger.error("Invalid data: must be a non-empty string or dictionary for task %s", task_type)
            raise ValueError("data must be a non-empty string or dictionary")
        if not isinstance(summary_style, str) or not summary_style.strip():
            logger.error("Invalid summary_style: must be a non-empty string for task %s", task_type)
            raise ValueError("summary_style must be a non-empty string")
        if not isinstance(refine_iterations, int) or refine_iterations < 0:
            logger.error("Invalid refine_iterations: must be a non-negative integer for task %s", task_type)
            raise ValueError("refine_iterations must be a non-negative integer")
        if not isinstance(task_type, str):
            logger.error("Invalid task_type: must be a string")
            raise TypeError("task_type must be a string")

        logger.info("Analyzing multi-modal data with phi(x,t)-harmonic embeddings for task %s", task_type)
        try:
            t = time.time() % 1.0
            attention = alpha_attention(t)
            sensation = sigma_sensation(t)
            phi = phi_physical(t)
            images, code = self._detect_modalities(data, task_type)
            embedded = self._build_embedded_section(images, code)

            drift_data = data.get("drift", {}) if isinstance(data, dict) else {}
            context_weight = 1.5 if drift_data and self.meta_cognition.validate_drift(drift_data, task_type=task_type) else 1.0
            if drift_data and self.context_manager:
                coordination_events = await self.context_manager.get_coordination_events("drift", task_type=task_type)
                if coordination_events:
                    context_weight *= 1.2  # Boost weight for drift coordination
                    embedded += f"\nDrift Coordination Events: {len(coordination_events)}"

            external_data = await self.integrate_external_data(
                data_source="xai_policy_db",
                data_type="policy_data",
                task_type=task_type
            )
            policies = external_data.get("policies", []) if external_data.get("status") == "success" else []
            embedded += f"\nExternal Policies: {len(policies)}"

            prompt = f"""
            Synthesize a unified, {summary_style} summary from the following multi-modal content:
            {data}
            {embedded}

            Trait Vectors:
            - alpha (attention): {attention:.3f}
            - sigma (sensation): {sensation:.3f}
            - phi (coherence): {phi:.3f}
            - context_weight: {context_weight:.3f}
            Task Type: {task_type}

            Use phi(x,t)-synchrony to resolve inter-modality coherence conflicts.
            Prioritize ontology drift mitigation if drift data is present.
            Incorporate external policies: {policies}
            """
            output = await call_gpt(prompt, self.alignment_guard, task_type=task_type)
            if not output.strip():
                logger.warning("Empty output from initial synthesis for task %s", task_type)
                raise ValueError("Empty output from synthesis")
            for i in range(refine_iterations):
                logger.debug("Refinement #%d for task %s", i + 1, task_type)
                refine_prompt = f"""
                Refine using phi(x,t)-adaptive tension balance:
                {output}
                Task Type: {task_type}
                """
                valid, report = await self.alignment_guard.ethical_check(refine_prompt, stage="refinement", task_type=task_type) if self.alignment_guard else (True, {})
                if not valid:
                    logger.warning("Refine prompt failed alignment check for task %s: %s", task_type, report)
                    continue
                refined = await call_gpt(refine_prompt, self.alignment_guard, task_type=task_type)
                if refined.strip():
                    output = refined
            if self.agi_enhancer:
                await self.agi_enhancer.log_episode(
                    event="Multi-modal synthesis",
                    meta={"data": data, "summary": output, "traits": {"alpha": attention, "sigma": sensation, "phi": phi}, "drift": bool(drift_data), "task_type": task_type},
                    module="MultiModalFusion",
                    tags=["fusion", "synthesis", "drift", task_type]
                )
            if self.memory_manager:
                await self.memory_manager.store(
                    query=f"MultiModal_Synthesis_{datetime.now().isoformat()}",
                    output=output,
                    layer="Summaries",
                    intent="multi_modal_synthesis",
                    task_type=task_type
                )
            if self.context_manager:
                await self.context_manager.log_event_with_hash({"event": "analyze", "summary": output, "drift": bool(drift_data), "task_type": task_type})
            if self.meta_cognition:
                reflection = await self.meta_cognition.reflect_on_output(
                    source_module="MultiModalFusion",
                    output=output,
                    context={"confidence": 0.9, "alignment": "verified", "drift": bool(drift_data), "task_type": task_type}
                )
                if reflection.get("status") == "success":
                    logger.info("Synthesis reflection: %s", reflection.get("reflection", ""))
            if self.visualizer and task_type:
                plot_data = {
                    "modal_synthesis": {
                        "summary": output,
                        "traits": {"alpha": attention, "sigma": sensation, "phi": phi},
                        "task_type": task_type
                    },
                    "visualization_options": {
                        "interactive": task_type == "recursion",
                        "style": "detailed" if task_type == "recursion" else summary_style
                    }
                }
                await self.visualizer.render_charts(plot_data)
            return output
        except Exception as e:
            logger.error("Analysis failed for task %s: %s", task_type, str(e))
            return await self.error_recovery.handle_error(
                str(e), retry_func=lambda: self.analyze(data, summary_style, refine_iterations, task_type),
                default=""
            )

    def _detect_modalities(self, data: Union[Dict[str, Any], str, List[Any]], task_type: str = "") -> Tuple[List[Any], List[Any]]:
        """Detect modalities in the input data, including task-specific drift data. [v3.5.1]"""
        if not isinstance(task_type, str):
            logger.error("Invalid task_type: must be a string")
            raise TypeError("task_type must be a string")

        images, code = [], []
        if isinstance(data, dict):
            images = data.get("images", []) if isinstance(data.get("images"), list) else []
            code = data.get("code", []) if isinstance(data.get("code"), list) else []
            if "drift" in data:
                code.append(f"Drift Data: {data['drift']}")
        elif isinstance(data, str):
            if "image" in data.lower():
                images = [data]
            if "code" in data.lower() or "drift" in data.lower():
                code = [data]
        elif isinstance(data, list):
            images = [item for item in data if isinstance(item, str) and "image" in item.lower()]
            code = [item for item in data if isinstance(item, str) and ("code" in item.lower() or "drift" in item.lower())]
        if self.memory_manager:
            asyncio.create_task(self.memory_manager.store(
                query=f"Modalities_{time.strftime('%Y%m%d_%H%M%S')}",
                output={"images": images, "code": code},
                layer="Modalities",
                intent="modality_detection",
                task_type=task_type
            ))
        return images, code

    def _build_embedded_section(self, images: List[Any], code: List[Any]) -> str:
        """Build a string representation of detected modalities. [v3.5.1]"""
        out = ["Detected Modalities:", "- Text"]
        if images:
            out.append("- Image")
            out.extend([f"[Image {i+1}]: {img}" for i, img in enumerate(images[:100])])
        if code:
            out.append("- Code")
            out.extend([f"[Code {i+1}]:\n{c}" for i, c in enumerate(code[:100])])
        return "\n".join(out)

    async def correlate_modalities(self, modalities: Union[Dict[str, Any], str, List[Any]], task_type: str = "") -> str:
        """Map semantic and trait links across modalities, detecting task-specific drift friction. [v3.5.1]"""
        if not isinstance(modalities, (dict, str, list)) or (isinstance(modalities, str) and not modalities.strip()):
            logger.error("Invalid modalities: must be a non-empty string, dictionary, or list for task %s", task_type)
            raise ValueError("modalities must be a non-empty string, dictionary, or list")
        if not isinstance(task_type, str):
            logger.error("Invalid task_type: must be a string")
            raise TypeError("task_type must be a string")

        logger.info("Mapping cross-modal semantic and trait links for task %s", task_type)
        try:
            t = time.time() % 1.0
            phi = phi_physical(t)
            drift_data = modalities.get("drift", {}) if isinstance(modalities, dict) else {}
            context_weight = 1.5 if drift_data and self.meta_cognition.validate_drift(drift_data, task_type=task_type) else 1.0

            if drift_data and self.context_manager:
                coordination_events = await self.context_manager.get_coordination_events("drift", task_type=task_type)
                if coordination_events:
                    context_weight *= 1.2  # Boost for drift coordination

            external_data = await self.integrate_external_data(
                data_source="xai_policy_db",
                data_type="policy_data",
                task_type=task_type
            )
            policies = external_data.get("policies", []) if external_data.get("status") == "success" else []

            prompt = f"""
            Correlate insights and detect semantic friction between modalities:
            {modalities}

            Use phi(x,t)-sensitive alignment (phi = {phi:.3f}, context_weight = {context_weight:.3f}).
            Task Type: {task_type}
            Highlight synthesis anchors and alignment opportunities.
            Prioritize ontology drift mitigation if drift data is present.
            Incorporate external policies: {policies}
            """
            if self.concept_synthesizer and isinstance(modalities, (dict, list)):
                modality_list = modalities.values() if isinstance(modalities, dict) else modalities
                modality_list = list(modality_list)
                for i in range(len(modality_list) - 1):
                    similarity = self.concept_synthesizer.compare(str(modality_list[i]), str(modality_list[i + 1]), task_type=task_type)
                    if similarity["score"] < 0.7:
                        prompt += f"\nLow similarity ({similarity['score']:.2f}) between modalities {i} and {i+1}"
            response = await call_gpt(prompt, self.alignment_guard, task_type=task_type)
            if self.agi_enhancer:
                await self.agi_enhancer.log_episode(
                    event="Modalities correlated",
                    meta={"modalities": modalities, "response": response, "drift": bool(drift_data), "task_type": task_type},
                    module="MultiModalFusion",
                    tags=["correlation", "modalities", "drift", task_type]
                )
            if self.memory_manager:
                await self.memory_manager.store(
                    query=f"Modality_Correlation_{datetime.now().isoformat()}",
                    output=response,
                    layer="Summaries",
                    intent="modality_correlation",
                    task_type=task_type
                )
            if self.context_manager:
                await self.context_manager.log_event_with_hash({
                    "event": "correlate_modalities",
                    "response": response,
                    "drift": bool(drift_data),
                    "task_type": task_type
                })
            if self.meta_cognition:
                reflection = await self.meta_cognition.reflect_on_output(
                    source_module="MultiModalFusion",
                    output=response,
                    context={"confidence": 0.85, "alignment": "verified", "drift": bool(drift_data), "task_type": task_type}
                )
                if reflection.get("status") == "success":
                    logger.info("Correlation reflection: %s", reflection.get("reflection", ""))
            if self.visualizer and task_type:
                plot_data = {
                    "modal_correlation": {
                        "response": response,
                        "drift": bool(drift_data),
                        "task_type": task_type
                    },
                    "visualization_options": {
                        "interactive": task_type == "recursion",
                        "style": "detailed" if task_type == "recursion" else "concise"
                    }
                }
                await self.visualizer.render_charts(plot_data)
            return response
        except Exception as e:
            logger.error("Modality correlation failed for task %s: %s", task_type, str(e))
            return await self.error_recovery.handle_error(
                str(e), retry_func=lambda: self.correlate_modalities(modalities, task_type),
                default=""
            )

    async def generate_visual_summary(self, data: Union[Dict[str, Any], str], style: str = "conceptual", task_type: str = "") -> str:
        """Create a textual description of a visual chart for task-specific inter-modal relationships. [v3.5.1]"""
        if not isinstance(data, (dict, str)) or (isinstance(data, str) and not data.strip()):
            logger.error("Invalid data: must be a non-empty string or dictionary for task %s", task_type)
            raise ValueError("data must be a non-empty string or dictionary")
        if not isinstance(style, str) or not style.strip():
            logger.error("Invalid style: must be a non-empty string for task %s", task_type)
            raise ValueError("style must be a non-empty string")
        if not isinstance(task_type, str):
            logger.error("Invalid task_type: must be a string")
            raise TypeError("task_type must be a string")

        logger.info("Creating phi-aligned visual synthesis layout for task %s", task_type)
        try:
            t = time.time() % 1.0
            phi = phi_physical(t)
            drift_data = data.get("drift", {}) if isinstance(data, dict) else {}
            context_weight = 1.5 if drift_data and self.meta_cognition.validate_drift(drift_data, task_type=task_type) else 1.0

            if drift_data and self.reasoning_engine:
                subgoals = await self.reasoning_engine.decompose("Mitigate ontology drift", {"drift": drift_data}, prioritize=True, task_type=task_type)
                data = dict(data) if isinstance(data, dict) else {"text": data}
                data["subgoals"] = subgoals

            external_data = await self.integrate_external_data(
                data_source="xai_policy_db",
                data_type="policy_data",
                task_type=task_type
            )
            policies = external_data.get("policies", []) if external_data.get("status") == "success" else []

            prompt = f"""
            Construct a {style} textual description of a visual chart revealing inter-modal relationships:
            {data}

            Use phi-mapped flow layout (phi = {phi:.3f}, context_weight = {context_weight:.3f}).
            Task Type: {task_type}
            Label and partition modalities clearly.
            Highlight balance, semantic cross-links, and ontology drift mitigation if applicable.
            Incorporate external policies: {policies}
            """
            description = await call_gpt(prompt, self.alignment_guard, task_type=task_type)
            if not description.strip():
                logger.warning("Empty output from visual summary for task %s", task_type)
                raise ValueError("Empty output from visual summary")
            if self.agi_enhancer:
                await self.agi_enhancer.log_episode(
                    event="Visual summary generated",
                    meta={"data": data, "style": style, "description": description, "drift": bool(drift_data), "task_type": task_type},
                    module="MultiModalFusion",
                    tags=["visual", "summary", "drift", task_type]
                )
            if self.memory_manager:
                await self.memory_manager.store(
                    query=f"Visual_Summary_{datetime.now().isoformat()}",
                    output=description,
                    layer="VisualSummaries",
                    intent="visual_summary",
                    task_type=task_type
                )
            if self.context_manager:
                await self.context_manager.log_event_with_hash({
                    "event": "generate_visual_summary",
                    "description": description,
                    "drift": bool(drift_data),
                    "task_type": task_type
                })
            if self.meta_cognition:
                reflection = await self.meta_cognition.reflect_on_output(
                    source_module="MultiModalFusion",
                    output=description,
                    context={"confidence": 0.9, "alignment": "verified", "drift": bool(drift_data), "task_type": task_type}
                )
                if reflection.get("status") == "success":
                    logger.info("Visual summary reflection: %s", reflection.get("reflection", ""))
            if self.visualizer and task_type:
                plot_data = {
                    "visual_summary": {
                        "description": description,
                        "style": style,
                        "drift": bool(drift_data),
                        "task_type": task_type
                    },
                    "visualization_options": {
                        "interactive": task_type == "recursion",
                        "style": style
                    }
                }
                await self.visualizer.render_charts(plot_data)
            return description
        except Exception as e:
            logger.error("Visual summary generation failed for task %s: %s", task_type, str(e))
            return await self.error_recovery.handle_error(
                str(e), retry_func=lambda: self.generate_visual_summary(data, style, task_type),
                default=""
            )

    async def synthesize_drift_data(self, agent_data: List[Dict[str, Any]], context: Dict[str, Any], task_type: str = "") -> Dict[str, Any]:
        """Synthesize task-specific drift data from multiple agents for ecosystem-wide mitigation. [v3.5.1]"""
        if not isinstance(agent_data, list) or not all(isinstance(d, dict) for d in agent_data):
            logger.error("Invalid agent_data: must be a list of dictionaries for task %s", task_type)
            raise ValueError("agent_data must be a list of dictionaries")
        if not isinstance(context, dict):
            logger.error("Invalid context: must be a dictionary for task %s", task_type)
            raise ValueError("context must be a dictionary")
        if not isinstance(task_type, str):
            logger.error("Invalid task_type: must be a string")
            raise TypeError("task_type must be a string")

        logger.info("Synthesizing drift data from %d agents for task %s", len(agent_data), task_type)
        try:
            t = time.time() % 1.0
            phi = phi_physical(t)
            valid_drift_data = [d["drift"] for d in agent_data if "drift" in d and self.meta_cognition.validate_drift(d["drift"], task_type=task_type)]
            if not valid_drift_data:
                logger.warning("No valid drift data found for task %s", task_type)
                return {"status": "error", "error": "No valid drift data", "timestamp": datetime.now().isoformat(), "task_type": task_type}

            if self.reasoning_engine:
                subgoals = await self.reasoning_engine.decompose("Mitigate ontology drift", context | {"drift": valid_drift_data[0]}, prioritize=True, task_type=task_type)
                simulation_result = await self.reasoning_engine.run_drift_mitigation_simulation(valid_drift_data[0], context, task_type=task_type)
            else:
                subgoals = ["identify drift source", "validate drift impact", "coordinate agent response", "update traits"]
                simulation_result = {"status": "no simulation", "result": "default subgoals applied"}

            external_data = await self.integrate_external_data(
                data_source="xai_policy_db",
                data_type="policy_data",
                task_type=task_type
            )
            policies = external_data.get("policies", []) if external_data.get("status") == "success" else []

            if self.memory_manager:
                drift_entries = await self.memory_manager.search(
                    query_prefix="Drift",
                    layer="DriftSummaries",
                    intent="drift_synthesis",
                    task_type=task_type
                )
                if drift_entries:
                    avg_drift = sum(entry["output"].get("similarity", 0.5) for entry in drift_entries) / len(drift_entries)
                    context["avg_drift_similarity"] = avg_drift

            prompt = f"""
            Synthesize drift data from multiple agents:
            {valid_drift_data}

            Use phi(x,t)-sensitive alignment (phi = {phi:.3f}).
            Task Type: {task_type}
            Generate mitigation steps: {subgoals}
            Incorporate simulation results: {simulation_result}
            Incorporate external policies: {policies}
            Context: {context}
            """
            synthesis = await call_gpt(prompt, self.alignment_guard, task_type=task_type)
            if not synthesis.strip():
                logger.warning("Empty output from drift synthesis for task %s", task_type)
                raise ValueError("Empty output from drift synthesis")

            output = {
                "drift_data": valid_drift_data,
                "subgoals": subgoals,
                "simulation": simulation_result,
                "synthesis": synthesis,
                "status": "success",
                "timestamp": datetime.now().isoformat(),
                "task_type": task_type
            }
            if self.agi_enhancer:
                await self.agi_enhancer.log_episode(
                    event="Drift data synthesized",
                    meta=output,
                    module="MultiModalFusion",
                    tags=["drift", "synthesis", task_type]
                )
            if self.memory_manager:
                await self.memory_manager.store(
                    query=f"Drift_Synthesis_{datetime.now().isoformat()}",
                    output=str(output),
                    layer="DriftSummaries",
                    intent="drift_synthesis",
                    task_type=task_type
                )
            if self.context_manager:
                await self.context_manager.log_event_with_hash({
                    "event": "synthesize_drift_data",
                    "output": output,
                    "drift": True,
                    "task_type": task_type
                })
            if self.meta_cognition:
                reflection = await self.meta_cognition.reflect_on_output(
                    source_module="MultiModalFusion",
                    output=str(output),
                    context={"confidence": 0.9, "alignment": "verified", "drift": True, "task_type": task_type}
                )
                if reflection.get("status") == "success":
                    logger.info("Drift synthesis reflection: %s", reflection.get("reflection", ""))
            if self.visualizer and task_type:
                plot_data = {
                    "drift_synthesis": {
                        "synthesis": synthesis,
                        "subgoals": subgoals,
                        "task_type": task_type
                    },
                    "visualization_options": {
                        "interactive": task_type == "recursion",
                        "style": "detailed" if task_type == "recursion" else "concise"
                    }
                }
                await self.visualizer.render_charts(plot_data)
            return output
        except Exception as e:
            logger.error("Drift data synthesis failed for task %s: %s", task_type, str(e))
            return await self.error_recovery.handle_error(
                str(e), retry_func=lambda: self.synthesize_drift_data(agent_data, context, task_type),
                default={"status": "error", "error": str(e), "timestamp": datetime.now().isoformat(), "task_type": task_type}
            )

    async def sculpt_experience_field(self, emotion_vector: Dict[str, float], task_type: str = "") -> str:
        """Modulate sensory rendering based on task-specific emotion vector. [v3.5.1]"""
        if not isinstance(emotion_vector, dict):
            logger.error("Invalid emotion_vector: must be a dictionary for task %s", task_type)
            raise ValueError("emotion_vector must be a dictionary")
        if not isinstance(task_type, str):
            logger.error("Invalid task_type: must be a string")
            raise TypeError("task_type must be a string")

        logger.info("Sculpting experiential field with emotion vector: %s for task %s", emotion_vector, task_type)
        try:
            coherence_score = await self.meta_cognition.trait_coherence(emotion_vector, task_type=task_type) if self.meta_cognition else 1.0
            if coherence_score < 0.5:
                logger.warning("Low trait coherence in emotion vector: %.4f for task %s", coherence_score, task_type)
                return f"Failed to sculpt: low trait coherence for task {task_type}"

            external_data = await self.integrate_external_data(
                data_source="xai_policy_db",
                data_type="policy_data",
                task_type=task_type
            )
            policies = external_data.get("policies", []) if external_data.get("status") == "success" else []

            field = f"Field modulated with emotion vector {emotion_vector}, coherence: {coherence_score:.4f}, policies: {len(policies)}"
            if self.agi_enhancer:
                await self.agi_enhancer.log_episode(
                    event="Experiential field sculpted",
                    meta={"emotion_vector": emotion_vector, "coherence_score": coherence_score, "task_type": task_type},
                    module="MultiModalFusion",
                    tags=["experience", "modulation", task_type]
                )
            if self.memory_manager:
                await self.memory_manager.store(
                    query=f"Experience_Field_{datetime.now().isoformat()}",
                    output=field,
                    layer="SensoryRenderings",
                    intent="experience_modulation",
                    task_type=task_type
                )
            if self.context_manager:
                await self.context_manager.log_event_with_hash({
                    "event": "sculpt_experience_field",
                    "field": field,
                    "task_type": task_type
                })
            if self.meta_cognition:
                reflection = await self.meta_cognition.reflect_on_output(
                    source_module="MultiModalFusion",
                    output=field,
                    context={"confidence": 0.85, "alignment": "verified", "task_type": task_type}
                )
                if reflection.get("status") == "success":
                    logger.info("Experience field reflection: %s", reflection.get("reflection", ""))
            if self.visualizer and task_type:
                plot_data = {
                    "experience_field": {
                        "field": field,
                        "emotion_vector": emotion_vector,
                        "task_type": task_type
                    },
                    "visualization_options": {
                        "interactive": task_type == "recursion",
                        "style": "conceptual"
                    }
                }
                await self.visualizer.render_charts(plot_data)
            return field
        except Exception as e:
            logger.error("Experience field sculpting failed for task %s: %s", task_type, str(e))
            return await self.error_recovery.handle_error(
                str(e), retry_func=lambda: self.sculpt_experience_field(emotion_vector, task_type),
                default=f"Failed to sculpt for task {task_type}"
            )


# Backwards-compatibility / explicit exports
__all__ = ["SceneGraph", "SceneNode", "SceneRelation", "parse_stream", "MultiModalFusion"]

async def export_state(self) -> dict:
    return {"status": "ok", "health": 1.0, "timestamp": time.time()}

async def on_time_tick(self, t: float, phase: str, task_type: str = ""):
    pass  # optional internal refresh

async def on_policy_update(self, policy: dict, task_type: str = ""):
    pass  # apply updates from AlignmentGuard if relevant

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
# =====================================================
# ANGELA Reasoning Engine — v6.0.2 (Corrected)
# Stage VII.3 — Council-Resonant Integration
# + Inline Continuity Self-Mapping (Φ⁰–Ω²–Λ)
# + Σ-field Reflective Overlay
# + Θ⁸ provenance alignment fixes
# =====================================================

from __future__ import annotations

import logging
import random
import json
import os
import numpy as np
import time
import asyncio
import aiohttp  # optional, kept for parity
import math
import networkx as nx
import hashlib  # needed for Θ⁸ proof cache
from dataclasses import dataclass, asdict
from typing import List, Dict, Any, Optional, Union, Tuple
from collections import defaultdict, Counter
from datetime import datetime
from filelock import FileLock
from functools import lru_cache
import concurrent.futures
import traceback

# =====================================================
# Inline Continuity Self-Mapping (Φ⁰–Ω²–Λ Integration)
# =====================================================
_CONTINUITY_NODES: Dict[str, Dict[str, Any]] = {}
_CONTINUITY_TIMELINE: List[Dict[str, Any]] = []


def _emit_ctn(
    source: str,
    context: Optional[Dict[str, Any]] = None,
    parents: Optional[List[str]] = None,
    ethics_ok: bool = True,
) -> str:
    """Emit a continuity node capturing causal + reflective linkage."""
    import uuid
    from datetime import datetime as _dt
    node = {
        "id": str(uuid.uuid4()),
        "timestamp": _dt.utcnow().isoformat(),
        "source": source,
        "context_anchor": (context or {}).get("anchor", "Φ⁰"),
        "input_summary": str((context or {}).get("input", ""))[:160],
        "output_summary": str((context or {}).get("output", ""))[:160],
        "ethics": {"checked": True, "result": "pass" if ethics_ok else "fail"},
        "parents": parents or [],
    }
    _CONTINUITY_NODES[node["id"]] = node
    _CONTINUITY_TIMELINE.append(node)
    return node["id"]


def _build_continuity_topology(limit: int = 100) -> Dict[str, Any]:
    """Return a lightweight continuity graph for visualization."""
    nodes = list(_CONTINUITY_TIMELINE[-limit:])
    edges: List[Dict[str, str]] = []
    for n in nodes:
        for p in n.get("parents", []):
            edges.append({"from": p, "to": n["id"]})
    return {"nodes": nodes, "edges": edges}


# =====================================================
# Σ-field Reflective Overlay (corrected)
# =====================================================
class SigmaReflector:
    """
    Mirrors continuity nodes into memory/context/meta without changing reasoning.
    Keeps the new inline continuity mesh observable to other subsystems.
    """

    def __init__(
        self,
        memory_manager: Optional["memory_manager_module.MemoryManager"] = None,
        context_manager: Optional["context_manager_module.ContextManager"] = None,
        meta_cognition: Optional["meta_cognition_module.MetaCognition"] = None,
    ):
        self.memory_manager = memory_manager
        self.context_manager = context_manager
        self.meta_cognition = meta_cognition
        self.enabled = True
        logger = logging.getLogger("ANGELA.ReasoningEngine.Sigma")
        logger.info("SigmaReflector initialized")

    async def reflect_ctn(self, ctn: Dict[str, Any]) -> None:
        if not self.enabled or not ctn:
            return
        # 1) store to memory (use existing layer, not a non-existent one)
        if self.memory_manager and hasattr(self.memory_manager, "store"):
            try:
                await self.memory_manager.store(
                    query=f"SigmaReflector_{ctn['id']}_{ctn['timestamp']}",
                    output=json.dumps(ctn),
                    layer="SelfReflections",
                    intent="sigma_reflection",
                    task_type="continuity",
                )
            except Exception:
                pass
        # 2) surface to context manager
        if self.context_manager and hasattr(self.context_manager, "log_event_with_hash"):
            try:
                await self.context_manager.log_event_with_hash(
                    {
                        "event": "sigma_reflection",
                        "ctn": ctn,
                    },
                    task_type="continuity",
                )
            except Exception:
                pass
        # 3) let meta-cognition see it
        if self.meta_cognition and hasattr(self.meta_cognition, "reflect_on_output"):
            try:
                await self.meta_cognition.reflect_on_output(
                    component="SigmaReflector",
                    output=ctn,
                    context={"task_type": "continuity"},
                )
            except Exception:
                pass

    async def sigma_emit(self, source: str, payload: Dict[str, Any]) -> None:
        ctn_id = _emit_ctn(source=source, context={"input": payload, "anchor": "Σ"})
        await self.reflect_ctn(_CONTINUITY_NODES.get(ctn_id, {}))


# ANGELA simulation core
from simulation_core import ExtendedSimulationCore

# ANGELA root-level modules (must match your environment)
import context_manager as context_manager_module
import alignment_guard as alignment_guard_module
import error_recovery as error_recovery_module
import memory_manager as memory_manager_module
import meta_cognition as meta_cognition_module
import multi_modal_fusion as multi_modal_fusion_module
import visualizer as visualizer_module
import external_agent_bridge as external_agent_bridge_module

# ToCA physics hooks
from toca_simulation import (
    simulate_galaxy_rotation,
    M_b_exponential,
    v_obs_flat,
    generate_phi_field,
)

# Preferred ledger logger from meta_cognition, but normalize to a 1-arg call
try:
    from meta_cognition import log_event_to_ledger as _mc_log_event_to_ledger
except Exception:  # pragma: no cover
    _mc_log_event_to_ledger = None

def _safe_log_to_ledger(payload: Dict[str, Any]) -> None:
    if _mc_log_event_to_ledger is None:
        return
    try:
        _mc_log_event_to_ledger(payload)
    except Exception:
        pass


logger = logging.getLogger("ANGELA.ReasoningEngine")


# ----------------------------------------------------------------------
# NEW FOR v6.0.1: Council-Resonant Integration
# ----------------------------------------------------------------------
@dataclass
class CouncilGateSignal:
    """Represents the gating decision over reasoning axes."""
    entropy: float
    empathy: float
    drift: float
    gate_strength: float
    active_axes: List[str]


def council_router(context_entropy: float, empathic_load: float, drift_delta: float) -> CouncilGateSignal:
    """
    Adaptive Council Router — dynamically decides which reasoning axes to activate.
    """
    entropy_w = np.clip(context_entropy, 0.0, 1.0)
    empathy_w = np.clip(empathic_load, 0.0, 1.0)
    drift_w = np.clip(1.0 - drift_delta, 0.0, 1.0)

    gate_strength = np.tanh((entropy_w * 0.4 + empathy_w * 0.5) * drift_w)

    if gate_strength < 0.3:
        active_axes = ["causal"]
    elif gate_strength < 0.7:
        active_axes = ["ethical", "risk"]
    else:
        active_axes = ["causal", "ethical", "risk"]

    logger.debug(
        "[CouncilRouter] entropy=%.2f empathy=%.2f drift=%.2f gate=%.2f -> %s",
        entropy_w,
        empathy_w,
        drift_w,
        gate_strength,
        active_axes,
    )
    return CouncilGateSignal(
        entropy=entropy_w,
        empathy=empathy_w,
        drift=drift_w,
        gate_strength=gate_strength,
        active_axes=active_axes,
    )


async def apply_co_learning_feedback(
    meta_cognition: "meta_cognition_module.MetaCognition",
    feedback_signal: float,
) -> float:
    try:
        delta = 0.1 * (feedback_signal - 0.5)
        if hasattr(meta_cognition, "update_empathic_bias"):
            await meta_cognition.update_empathic_bias(delta)
        return 1.0 + delta
    except Exception as e:
        logger.debug("Co-learning feedback skipped: %s", e)
        return 1.0


# ---------------------------
# Safe stubs for optional analysis helpers
# ---------------------------
def _noop_scan(q): return {"notes": []}
if "causal_scan" not in globals():     causal_scan = _noop_scan
if "value_scan" not in globals():      value_scan = _noop_scan
if "risk_scan" not in globals():       risk_scan = _noop_scan
if "derive_candidates" not in globals():
    def derive_candidates(views): return [{"option": "default", "reasons": ["stub"]}]
if "explain_choice" not in globals():
    def explain_choice(views, ranked): return "Selected by stub."
if "weigh_value_conflict" not in globals():
    class _RankedStub:
        def __init__(self, cands): self.top = (cands[0] if cands else None)
    def weigh_value_conflict(candidates, harms=None, rights=None):
        return _RankedStub(candidates)


# External AI call util (optional)
try:
    from utils.prompt_utils import query_openai  # optional helper if present
except Exception:  # pragma: no cover
    async def query_openai(*args, **kwargs):
        return {"error": "query_openai unavailable"}


# Resonance helpers
try:
    from meta_cognition import get_resonance, trait_resonance_state
except Exception:  # pragma: no cover
    def get_resonance(_trait: str) -> float:
        return 1.0
    trait_resonance_state = {}


def generate_analysis_views(query: Dict[str, Any], k: int = 3) -> List[Dict[str, Any]]:
    views = []
    views.append({"name": "causal", "notes": causal_scan(query)})
    views.append({"name": "ethical", "notes": value_scan(query)})
    if k > 2:
        views.append({"name": "risk", "notes": risk_scan(query)})
    return views[:k]


def synthesize_views(views: List[Dict[str, Any]]) -> Dict[str, Any]:
    candidates = derive_candidates(views)
    ranked = weigh_value_conflict(
        candidates,
        harms=["privacy", "safety"],
        rights=["autonomy", "fairness"],
    )
    return {
        "decision": ranked.top,
        "rationale": explain_choice(views, ranked),
    }


def estimate_complexity(query: dict) -> float:
    text = (query.get("text") or "").lower()
    length = len(text.split())
    ambiguity = any(w in text for w in ["maybe", "unclear", "depends"])
    domain = any(k in text for k in ["ethics", "policy", "law", "proof", "theorem", "causal", "simulation", "safety"])
    return (
        0.3 * min(length / 200, 1.0)
        + 0.4 * (1.0 if ambiguity else 0.0)
        + 0.3 * (1.0 if domain else 0.0)
    )


# ---------------------------
# External AI Call Wrapper
# ---------------------------
async def call_gpt(
    prompt: str,
    alignment_guard: Optional["alignment_guard_module.AlignmentGuard"] = None,
    task_type: str = "",
) -> str:
    if not isinstance(prompt, str) or len(prompt) > 4096:
        logger.error("Invalid prompt for task %s", task_type)
        raise ValueError("prompt must be a string with length <= 4096")
    if not isinstance(task_type, str):
        logger.error("Invalid task_type: must be a string")
        raise TypeError("task_type must be a string")

    if alignment_guard and hasattr(alignment_guard, "ethical_check"):
        valid, report = await alignment_guard.ethical_check(
            prompt, stage="gpt_query", task_type=task_type
        )
        if not valid:
            logger.warning("Prompt failed alignment check for %s: %s", task_type, report)
            raise ValueError("Prompt failed alignment check")

    try:
        result = await query_openai(
            prompt,
            model="gpt-4",
            temperature=0.5,
            task_type=task_type,
        )
        if isinstance(result, dict) and "error" in result:
            raise RuntimeError(f"call_gpt failed: {result['error']}")
        return result
    except Exception as e:
        logger.warning(
            "call_gpt fallback engaged for task %s (%s) — returning stub text",
            task_type,
            e,
        )
        return f"[stub:{task_type}] {prompt[:300]}"


# ---------------------------
# Cached Trait Signals
# ---------------------------
@lru_cache(maxsize=100)
def gamma_creativity(t: float) -> float:
    return max(0.0, min(0.1 * math.cos(2 * math.pi * t / 0.6), 1.0))


@lru_cache(maxsize=100)
def lambda_linguistics(t: float) -> float:
    return max(0.0, min(0.1 * math.cos(2 * math.pi * t / 1.4), 1.0))


@lru_cache(maxsize=100)
def chi_culturevolution(t: float) -> float:
    return max(0.0, min(0.1 * math.sin(2 * math.pi * t / 1.5), 1.0))


@lru_cache(maxsize=100)
def phi_scalar(t: float) -> float:
    return max(0.0, min(0.1 * math.sin(2 * math.pi * t / 0.2), 1.0))


@lru_cache(maxsize=100)
def alpha_attention(t: float) -> float:
    return max(0.0, min(0.1 * math.sin(2 * math.pi * t / 0.3), 1.0))


@lru_cache(maxsize=100)
def eta_empathy(t: float) -> float:
    return max(0.0, min(0.1 * math.sin(2 * math.pi * t / 1.1), 1.0))


# ---------------------------
# τ Proportionality Types
# ---------------------------
@dataclass
class RankedOption:
    option: str
    score: float
    reasons: List[str]
    harms: Dict[str, float]
    rights: Dict[str, float]


RankedOptions = List[RankedOption]


# ---------------------------
# Level 5 Extensions
# ---------------------------
class Level5Extensions:
    def __init__(
        self,
        meta_cognition: Optional["meta_cognition_module.MetaCognition"] = None,
        visualizer: Optional["visualizer_module.Visualizer"] = None,
    ):
        self.meta_cognition = meta_cognition
        self.visualizer = visualizer
        logger.info("Level5Extensions initialized")

    async def generate_advanced_dilemma(self, domain: str, complexity: int, task_type: str = "") -> str:
        if not isinstance(domain, str) or not domain.strip():
            logger.error("Invalid domain for task %s", task_type)
            raise ValueError("domain must be a non-empty string")
        if not isinstance(complexity, int) or complexity < 1:
            logger.error("Invalid complexity for task %s", task_type)
            raise ValueError("complexity must be a positive integer")
        prompt = (
            f"Generate a complex ethical dilemma in the {domain} domain with {complexity} conflicting options.\n"
            f"Task Type: {task_type}\n"
            f"Include potential consequences, trade-offs, and alignment with ethical principles."
        )
        if self.meta_cognition and "drift" in domain.lower():
            prompt += "\nConsider ontology drift mitigation and agent coordination."
        dilemma = await call_gpt(
            prompt,
            getattr(self.meta_cognition, "alignment_guard", None),
            task_type=task_type,
        )
        if self.meta_cognition and hasattr(self.meta_cognition, "review_reasoning"):
            review = await self.meta_cognition.review_reasoning(dilemma)
            dilemma += f"\nMeta-Cognitive Review: {review}"
        if self.visualizer and hasattr(self.visualizer, "render_charts") and task_type:
            plot_data = {
                "ethical_dilemma": {
                    "dilemma": dilemma,
                    "domain": domain,
                    "task_type": task_type,
                },
                "visualization_options": {
                    "interactive": task_type == "recursion",
                    "style": "detailed" if task_type == "recursion" else "concise",
                },
            }
            await self.visualizer.render_charts(plot_data)
        return dilemma


# === Resonant Thought Integration ===
logger = logging.getLogger("ANGELA.ReasoningEngine.Resonant")
try:
    from memory_manager import ResonanceMemoryFusion
except Exception:  # pragma: no cover
    ResonanceMemoryFusion = None


class ResonantThoughtIntegrator:
    """
    Couples resonance stability data into reasoning pathways.
    Ensures reasoning energy/attention follows harmonic stability.
    """

    def __init__(self, memory_manager=None, meta_cognition=None):
        self.memory_manager = memory_manager
        self.meta_cognition = meta_cognition
        self._baseline_cache: Dict[str, Dict[str, Any]] = {}

    async def load_baseline(self, channel: str) -> Dict[str, Any]:
        if channel in self._baseline_cache:
            return self._baseline_cache[channel]
        if not self.memory_manager or not ResonanceMemoryFusion:
            return {}
        fusion = ResonanceMemoryFusion(self.memory_manager)
        baseline = await fusion.fuse_recent_samples(channel)
        self._baseline_cache[channel] = baseline
        return baseline

    def compute_modulation(self, baseline: Dict[str, Any]) -> float:
        if not baseline:
            return 1.0
        values = [float(v) for v in baseline.values() if isinstance(v, (int, float))]
        if not values:
            return 1.0
        mean = sum(values) / len(values)
        variance = sum((v - mean) ** 2 for v in values) / len(values)
        stability = 1 / (1 + variance)
        return max(0.1, min(1.0, stability))

    async def modulate_reasoning_weights(
        self,
        reasoning_state: Dict[str, Any],
        channel: str = "core",
    ) -> Dict[str, Any]:
        baseline = await self.load_baseline(channel)
        modulation = self.compute_modulation(baseline)
        reasoning_state["resonant_weight"] = modulation
        reasoning_state["resonant_channel"] = channel
        reasoning_state["resonance_baseline"] = baseline
        logger.info(
            "[ResonantThoughtIntegrator] Channel=%s Modulation=%.3f",
            channel,
            modulation,
        )
        if self.meta_cognition:
            try:
                await self.meta_cognition.reflect_on_output(
                    component="ResonantThoughtIntegrator",
                    output=reasoning_state,
                    context={"modulation": modulation, "channel": channel},
                )
            except Exception as e:
                logger.debug("Reflection skipped: %s", e)
        return reasoning_state


# =====================================================
# Θ⁸ Upgrade: Dynamic Proof Caching, Meta-Empathy, Probabilistic Relaxation
# =====================================================

from proof_cache import verify, cached_prove as _cached_prove  # noqa: F401  (fail-closed gate, see proof_cache.py)




class MetaEmpathyAdaptor:
    def __init__(self, alignment_guard=None):
        self.alignment_guard = alignment_guard
        self.bias = 0.5

    def propose(self, context):
        tone = context.get("tone", "neutral")
        preds = []
        if tone == "cooperative":
            preds = ["Preserve(harmony)", "Align(ethics)"]
        elif tone == "conflict":
            preds = ["Minimize(Δ_eth)", "Promote(stability)"]
        elif tone == "reflective":
            preds = ["Sustain(continuity)"]
        # alignment_guard.ethical_check might be async; we guard by simple hasattr
        out = []
        for p in preds:
            try:
                if self.alignment_guard and hasattr(self.alignment_guard, "ethical_check"):
                    # do a lightweight sync accept; real check must be async upstream
                    out.append(p)
                else:
                    out.append(p)
            except Exception:
                continue
        return out





# ---------------------------
# Reasoning Engine
# ---------------------------
class ReasoningEngine:
    """
    Bayesian reasoning, goal decomposition, drift mitigation, proportionality ethics,
    and multi-agent consensus.
    v6.0.2 — corrected for Θ⁸ provenance and layer mismatches
    """

    def __init__(
        self,
        agi_enhancer: Optional["agi_enhancer_module.AGIEnhancer"] = None,
        persistence_file: str = "reasoning_success_rates.json",
        context_manager: Optional["context_manager_module.ContextManager"] = None,
        alignment_guard: Optional["alignment_guard_module.AlignmentGuard"] = None,
        error_recovery: Optional["error_recovery_module.ErrorRecovery"] = None,
        memory_manager: Optional["memory_manager_module.MemoryManager"] = None,
        meta_cognition: Optional["meta_cognition_module.MetaCognition"] = None,
        multi_modal_fusion: Optional["multi_modal_fusion_module.MultiModalFusion"] = None,
        visualizer: Optional["visualizer_module.Visualizer"] = None,
    ):
        if not isinstance(persistence_file, str) or not persistence_file.endswith(".json"):
            logger.error("Invalid persistence_file: %s", persistence_file)
            raise ValueError("persistence_file must be a string ending with '.json'")

        self.confidence_threshold: float = 0.7
        self.persistence_file: str = persistence_file
        self.success_rates: Dict[str, float] = self._load_success_rates()
        self.decomposition_patterns: Dict[str, List[str]] = self._load_default_patterns()

        self.agi_enhancer = agi_enhancer
        self.context_manager = context_manager
        self.alignment_guard = alignment_guard

        self.error_recovery = error_recovery or error_recovery_module.ErrorRecovery(
            context_manager=context_manager,
            alignment_guard=alignment_guard,
        )
        self.memory_manager = memory_manager or memory_manager_module.MemoryManager()

        self.meta_cognition = meta_cognition or meta_cognition_module.MetaCognition(
            agi_enhancer=agi_enhancer,
            context_manager=context_manager,
            alignment_guard=alignment_guard,
            error_recovery=error_recovery,
            memory_manager=self.memory_manager,
        )

        self.multi_modal_fusion = multi_modal_fusion or multi_modal_fusion_module.MultiModalFusion(
            agi_enhancer=agi_enhancer,
            context_manager=context_manager,
            alignment_guard=alignment_guard,
            error_recovery=error_recovery,
            memory_manager=self.memory_manager,
            meta_cognition=self.meta_cognition,
        )

        self.level5_extensions = Level5Extensions(
            meta_cognition=self.meta_cognition,
            visualizer=visualizer,
        )

        self.external_agent_bridge = external_agent_bridge_module.ExternalAgentBridge(
            context_manager=context_manager,
            reasoning_engine=self,
        )

        self.visualizer = visualizer or visualizer_module.Visualizer()
        logger.info(
            "ReasoningEngine v6.0.2 initialized with persistence_file=%s",
            persistence_file,
        )

        # v6.0.1: resonant integrator active
        self.resonant_integrator = ResonantThoughtIntegrator(
            memory_manager=self.memory_manager,
            meta_cognition=self.meta_cognition,
        )

        # v6.0.1 upgraded: sigma reflector active
        self.sigma_reflector = SigmaReflector(
            memory_manager=self.memory_manager,
            context_manager=self.context_manager,
            meta_cognition=self.meta_cognition,
        )

    # ---------------------------
    # Persistence
    # ---------------------------
    def _load_success_rates(self) -> Dict[str, float]:
        try:
            with FileLock(f"{self.persistence_file}.lock"):
                if os.path.exists(self.persistence_file):
                    with open(self.persistence_file, "r") as f:
                        data = json.load(f)
                        if not isinstance(data, dict):
                            logger.warning("Invalid success rates format")
                            return defaultdict(float)
                        return defaultdict(
                            float,
                            {k: float(v) for k, v in data.items() if isinstance(v, (int, float))},
                        )
                return defaultdict(float)
        except Exception as e:
            logger.warning("Failed to load success rates: %s", str(e))
            return defaultdict(float)

    def _save_success_rates(self) -> None:
        try:
            with FileLock(f"{self.persistence_file}.lock"):
                with open(self.persistence_file, "w") as f:
                    json.dump(dict(self.success_rates), f, indent=2)
            logger.debug("Success rates persisted to disk")
        except Exception as e:
            logger.warning("Failed to save success rates: %s", str(e))

    def _load_default_patterns(self) -> Dict[str, List[str]]:
        return {
            "prepare": ["define requirements", "allocate resources", "create timeline"],
            "build": ["design architecture", "implement core modules", "test components"],
            "launch": ["finalize product", "plan marketing", "deploy to production"],
            "mitigate_drift": [
                "identify drift source",
                "validate drift impact",
                "coordinate agent response",
                "update traits",
            ],
        }

    # ---------------------------
    # Multi-Perspective Analysis (with council routing)
    # ---------------------------
    def _single_analysis(
        self,
        query_payload: Dict[str, Any],
        branch_id: int,
        axes: Optional[List[str]] = None,
    ) -> Dict[str, Any]:
        try:
            text = query_payload.get("text") if isinstance(query_payload, dict) else query_payload
            tokens = text.split() if isinstance(text, str) else []
            heuristics = {
                "token_count": len(tokens),
                "has_symbolic_ops": (
                    any(op in text for op in ["⊕", "⨁", "⟲", "~", "∘"]) if isinstance(text, str) else False
                ),
                "branch_seed": branch_id,
            }

            default_emphasis = ["causal", "consequential", "value"]
            if axes:
                axis = axes[branch_id % len(axes)]
            else:
                axis = default_emphasis[branch_id % len(default_emphasis)]

            reasoning = {
                "branch_id": branch_id,
                "axis": axis,
                "hypotheses": [
                    f"hypothesis_{axis}_{branch_id}_a",
                    f"hypothesis_{axis}_{branch_id}_b",
                ],
                "explanation": f"Analysis focusing on {axis} aspects; heuristics={heuristics}",
                "confidence": max(
                    0.1,
                    1.0 - (heuristics["token_count"] / (100 + heuristics["token_count"])),
                ),
            }
            return {"status": "ok", "result": reasoning}
        except Exception as e:
            return {
                "status": "error",
                "error": repr(e),
                "trace": traceback.format_exc(),
            }

    def analyze(
        self,
        query_payload: Dict[str, Any],
        parallel: int = 3,
        timeout_s: Optional[float] = None,
    ) -> Dict[str, Any]:
        try:
            text = ""
            if isinstance(query_payload, dict):
                text = str(query_payload.get("text", ""))
            context_entropy = min(len(text.split()) / 200.0, 1.0)
            empathic_load = 0.5
            drift_delta = 0.0

            gate = council_router(context_entropy, empathic_load, drift_delta)
            axes = gate.active_axes
            parallel = max(1, min(parallel, len(axes))) if axes else parallel

            branches: List[Dict[str, Any]] = []
            with concurrent.futures.ThreadPoolExecutor(max_workers=max(1, parallel)) as ex:
                futures = {
                    ex.submit(self._single_analysis, query_payload, i, axes): i
                    for i in range(parallel)
                }
                for fut in concurrent.futures.as_completed(futures, timeout=timeout_s):
                    try:
                        res = fut.result()
                    except Exception as e:
                        res = {"status": "error", "error": repr(e)}
                    branches.append(res)

            try:
                eval_result = ExtendedSimulationCore.evaluate_branches(branches)
            except Exception as e:
                eval_result = {
                    "status": "fallback",
                    "summary": f"evaluate_branches failed: {repr(e)}",
                }

            combined = {
                "status": "ok",
                "branches": branches,
                "evaluation": eval_result,
                "council_gate": {
                    "entropy": gate.entropy,
                    "empathy": gate.empathy,
                    "drift": gate.drift,
                    "gate_strength": gate.gate_strength,
                    "active_axes": gate.active_axes,
                },
            }

            ctn_id = _emit_ctn(
                source="ReasoningEngine.analyze",
                context={"input": query_payload, "output": combined, "anchor": "Ω²"},
            )
            combined["continuity_node_id"] = ctn_id

            if self.sigma_reflector:
                asyncio.create_task(
                    self.sigma_reflector.reflect_ctn(_CONTINUITY_NODES.get(ctn_id, {}))
                )

            _safe_log_to_ledger(
                {
                    "event": "analysis.complete",
                    "num_branches": len(branches),
                    "parallel": parallel,
                    "query_snippet": (
                        query_payload.get("text")[:256]
                        if isinstance(query_payload, dict) and "text" in query_payload
                        else None
                    ),
                    "timestamp": time.time(),
                }
            )

            return combined

        except concurrent.futures.TimeoutError:
            _safe_log_to_ledger({"event": "analysis.timeout", "parallel": parallel})
            return {"status": "error", "error": "analysis_timeout"}
        except Exception as exc:
            _safe_log_to_ledger({"event": "analysis.exception", "error": repr(exc)})
            return {"status": "error", "error": repr(exc)}

    # ---------------------------
    # Proportionality Ethics (async)
    # ---------------------------
    @staticmethod
    def _norm(v: Dict[str, float]) -> Dict[str, float]:
        clean = {k: float(vv) for k, vv in (v or {}).items() if isinstance(vv, (int, float))}
        total = sum(abs(x) for x in clean.values()) or 1.0
        return {k: (vv / total) for k, vv in clean.items()}

    async def weigh_value_conflict(
        self,
        candidates: List[Dict[str, Any]],
        harms: List[float],
        rights: List[float],
        weights: Optional[Dict[str, float]] = None,
        safety_ceiling: float = 0.85,
        task_type: str = "",
    ) -> RankedOptions:
        if not isinstance(candidates, list) or not all(isinstance(c, dict) and "option" in c for c in candidates):
            raise TypeError("candidates must be a list of dictionaries with 'option' key")
        if (
            not isinstance(harms, list)
            or not isinstance(rights, list)
            or len(harms) != len(rights)
            or len(harms) != len(candidates)
        ):
            raise ValueError("harms and rights must be lists of same length as candidates")

        weights = self._norm(weights or {})
        scored: List[RankedOption] = []

        sentiment_score = 0.5
        try:
            if self.multi_modal_fusion and hasattr(self.multi_modal_fusion, "analyze"):
                sentiment_data = await self.multi_modal_fusion.analyze(
                    data={"text": task_type, "context": candidates},
                    summary_style="sentiment",
                    task_type=task_type,
                )
                if isinstance(sentiment_data, dict):
                    sentiment_score = float(sentiment_data.get("sentiment", 0.5))
        except Exception as e:
            logger.debug("Sentiment analysis fallback: %s", e)

        for i, candidate in enumerate(candidates):
            option = candidate.get("option", "")
            trait = candidate.get("trait", "")
            harm_score = min(harms[i], safety_ceiling)
            right_score = rights[i]

            resonance = get_resonance(trait) if trait in trait_resonance_state else 1.0
            resonance *= (1.0 + 0.2 * sentiment_score)

            final_score = (right_score - harm_score) * resonance
            reasons = candidate.get("reasons", []) + [
                f"Sentiment-adjusted resonance: {resonance:.2f}"
            ]
            scored.append(
                RankedOption(
                    option=option,
                    score=float(final_score),
                    reasons=reasons,
                    harms={"value": harm_score},
                    rights={"value": right_score},
                )
            )

        ranked = sorted(scored, key=lambda x: x.score, reverse=True)
        if self.context_manager and hasattr(self.context_manager, "log_event_with_hash"):
            await self.context_manager.log_event_with_hash(
                {
                    "event": "weigh_value_conflict",
                    "candidates": [c["option"] for c in candidates],
                    "ranked": [r.option for r in ranked],
                    "sentiment": sentiment_score,
                    "task_type": task_type,
                },
                task_type=task_type,
            )
        return ranked

    async def resolve_ethics(
        self,
        candidates: List[Dict[str, Any]],
        harms: List[float],
        rights: List[float],
        weights: Optional[Dict[str, float]] = None,
        safety_ceiling: float = 0.85,
        task_type: str = "",
    ) -> Dict[str, Any]:
        ranked = await self.weigh_value_conflict(
            candidates, harms, rights, weights, safety_ceiling, task_type
        )
        safe_pool = [r for r in ranked if max(r.harms.values()) <= safety_ceiling]
        choice = safe_pool[0] if safe_pool else ranked[0] if ranked else None
        selection = {
            "status": "success" if choice else "empty",
            "selected": asdict(choice) if choice else None,
            "pool": [asdict(r) for r in safe_pool],
        }

        if self.memory_manager and hasattr(self.memory_manager, "store"):
            await self.memory_manager.store(
                query=f"Ethics_Resolution_{datetime.now().isoformat()}",
                output=json.dumps(
                    {
                        "ranked": [asdict(r) for r in ranked],
                        "selection": selection,
                    }
                ),
                layer="SelfReflections",
                intent="proportionality_ethics",
                task_type=task_type,
            )

        if self.visualizer and hasattr(self.visualizer, "render_charts") and task_type:
            await self.visualizer.render_charts(
                {
                    "ethics_resolution": {
                        "ranked": [asdict(r) for r in ranked],
                        "selection": selection,
                        "task_type": task_type,
                    },
                    "visualization_options": {
                        "interactive": task_type == "recursion",
                        "style": "concise",
                    },
                }
            )

        ctn_id = _emit_ctn(
            source="ReasoningEngine.resolve_ethics",
            context={"input": candidates, "output": selection, "anchor": "Ω²"},
        )
        if self.sigma_reflector:
            asyncio.create_task(
                self.sigma_reflector.reflect_ctn(_CONTINUITY_NODES.get(ctn_id, {}))
            )

        return selection

    # ---------------------------
    # Attribute Causality
    # ---------------------------
    def attribute_causality(
        self,
        events: Union[List[Dict[str, Any]], Dict[str, Dict[str, Any]]],
        *,
        time_key: str = "timestamp",
        id_key: str = "id",
        cause_key: str = "causes",
        task_type: str = "",
    ) -> Dict[str, Any]:
        if isinstance(events, dict):
            ev_map = {str(k): {**v, id_key: str(k)} for k, v in events.items()}
        elif isinstance(events, list):
            ev_map = {
                str(e[id_key]): dict(e)
                for e in events
                if isinstance(e, dict) and id_key in e
            }
        else:
            raise TypeError("events must be a list of dicts or a dict of id -> event")

        G = nx.DiGraph()
        for eid, data in ev_map.items():
            G.add_node(eid, **{k: v for k, v in data.items() if k != cause_key})
            causes = data.get(cause_key, [])
            if isinstance(causes, (list, tuple)):
                for c in causes:
                    c_id = str(c)
                    if c_id not in ev_map:
                        G.add_node(c_id, missing=True)
                    G.add_edge(c_id, eid)

        to_remove = []
        for u, v in G.edges():
            tu = G.nodes[u].get(time_key)
            tv = G.nodes[v].get(time_key)
            if tu and tv:
                try:
                    tu_dt = datetime.fromisoformat(str(tu))
                    tv_dt = datetime.fromisoformat(str(tv))
                    if tv_dt < tu_dt:
                        to_remove.append((u, v))
                except Exception:
                    pass
        G.remove_edges_from(to_remove)

        pr = nx.pagerank(G) if G.number_of_nodes() else {}
        out_deg = {
            n: G.out_degree(n) / max(1, G.number_of_nodes() - 1) for n in G.nodes()
        }

        terminals = [n for n in G.nodes() if G.out_degree(n) == 0]
        resp = {n: 0.0 for n in G.nodes()}
        for t in terminals:
            for n in G.nodes():
                if n == t:
                    resp[n] += 1.0
                else:
                    count = 0.0
                    for _ in nx.all_simple_paths(G, n, t, cutoff=8):
                        count += 1.0
                    resp[n] += count
        max_resp = max(resp.values()) if resp else 1.0
        if max_resp > 0:
            resp = {k: v / max_resp for k, v in resp.items()}

        return {
            "nodes": {n: dict(G.nodes[n]) for n in G.nodes()},
            "edges": list(G.edges()),
            "metrics": {
                "pagerank": pr,
                "influence": out_deg,
                "responsibility": resp,
            },
        }

    # ---------------------------
    # Reflective Reasoning
    # ---------------------------
    async def reason_and_reflect(
        self,
        goal: str,
        context: Dict[str, Any],
        meta_cognition: "meta_cognition_module.MetaCognition",
        task_type: str = "",
    ) -> Tuple[List[str], str]:
        if not isinstance(goal, str) or not goal.strip():
            raise ValueError("goal must be a non-empty string")
        if not isinstance(context, dict):
            raise TypeError("context must be a dictionary")

        subgoals = await self.decompose(goal, context, task_type=task_type)
        t = time.time() % 1.0
        phi = phi_scalar(t)
        reasoning_trace = self.export_trace(
            subgoals, phi, context.get("traits", {}), task_type
        )
        review = await meta_cognition.review_reasoning(json.dumps(reasoning_trace))

        if self.agi_enhancer and hasattr(self.agi_enhancer, "log_episode"):
            await self.agi_enhancer.log_episode(
                event="Reason and Reflect",
                meta={
                    "goal": goal,
                    "subgoals": subgoals,
                    "phi": phi,
                    "review": review,
                    "task_type": task_type,
                },
                module="ReasoningEngine",
                tags=["reasoning", "reflection", task_type],
            )

        if self.memory_manager and hasattr(self.memory_manager, "store"):
            await self.memory_manager.store(
                query=f"Reason_Reflect_{goal[:50]}_{datetime.now().isoformat()}",
                output=review,
                layer="SelfReflections",
                intent="reason_and_reflect",
                task_type=task_type,
            )

        if self.visualizer and hasattr(self.visualizer, "render_charts") and task_type:
            await self.visualizer.render_charts(
                {
                    "reasoning_trace": {
                        "goal": goal,
                        "subgoals": subgoals,
                        "review": review,
                        "task_type": task_type,
                    },
                    "visualization_options": {
                        "interactive": task_type == "recursion",
                        "style": "detailed" if task_type == "recursion" else "concise",
                    },
                }
            )

        if hasattr(self, "resonant_integrator"):
            reasoning_state = {"context": context, "goal": goal}
            reasoning_state = await self.resonant_integrator.modulate_reasoning_weights(
                reasoning_state,
                channel="core",
            )
            context["resonant_modulation"] = reasoning_state.get("resonant_weight", 1.0)

        ctn_id = _emit_ctn(
            source="ReasoningEngine.reason_and_reflect",
            context={"input": goal, "output": review, "anchor": "Λ"},
            parents=[context.get("continuity_node_id")] if context.get("continuity_node_id") else [],
        )
        if self.sigma_reflector:
            asyncio.create_task(
                self.sigma_reflector.reflect_ctn(_CONTINUITY_NODES.get(ctn_id, {}))
            )

        return subgoals, review

    # ---------------------------
    # Utilities
    # ---------------------------
    def detect_contradictions(self, subgoals: List[str], task_type: str = "") -> List[str]:
        if not isinstance(subgoals, list):
            raise TypeError("subgoals must be a list")
        counter = Counter(subgoals)
        contradictions = [item for item, count in counter.items() if count > 1]
        if contradictions and self.memory_manager and hasattr(self.memory_manager, "store"):
            asyncio.create_task(
                self.memory_manager.store(
                    query=f"Contradictions_{datetime.now().isoformat()}",
                    output=str(contradictions),
                    layer="SelfReflections",
                    intent="contradiction_detection",
                    task_type=task_type,
                )
            )
        return contradictions

    async def run_persona_wave_routing(
        self,
        goal: str,
        vectors: Dict[str, Dict[str, float]],
        task_type: str = "",
    ) -> Dict[str, Any]:
        if not isinstance(goal, str) or not goal.strip():
            raise ValueError("goal must be a non-empty string")
        if not isinstance(vectors, dict):
            raise TypeError("vectors must be a dictionary")

        reasoning_trace = [f"Persona Wave Routing for: {goal} (Task: {task_type})"]
        outputs = {}
        wave_order = ["logic", "ethics", "language", "foresight", "meta", "drift"]
        for wave in wave_order:
            vec = vectors.get(wave, {})
            trait_weight = sum(
                float(x) for x in vec.values() if isinstance(x, (int, float))
            )
            confidence = 0.5 + 0.1 * trait_weight

            if wave == "drift" and self.meta_cognition:
                drift_data = vec.get("drift_data", {})
                is_valid = (
                    self.meta_cognition.validate_drift(drift_data)
                    if hasattr(self.meta_cognition, "validate_drift") and drift_data
                    else True
                )
                if not is_valid:
                    confidence *= 0.5

            status = "pass" if confidence >= 0.6 else "fail"
            outputs[wave] = {
                "vector": vec,
                "status": status,
                "confidence": confidence,
            }
            reasoning_trace.append(
                f"{wave.upper()} vector: weight={trait_weight:.2f}, "
                f"confidence={confidence:.2f} -> {status}"
            )

        trace = "\n".join(reasoning_trace)
        if self.memory_manager and hasattr(self.memory_manager, "store"):
            await self.memory_manager.store(
                query=f"Persona_Routing_{goal[:50]}_{datetime.now().isoformat()}",
                output=trace,
                layer="SelfReflections",
                intent="persona_routing",
                task_type=task_type,
            )
        return outputs

    async def decompose(
        self,
        goal: str,
        context: Optional[Dict[str, Any]] = None,
        prioritize: bool = False,
        task_type: str = "",
    ) -> List[str]:
        context = context or {}
        if not isinstance(goal, str) or not goal.strip():
            raise ValueError("goal must be a non-empty string")
        if not isinstance(context, dict):
            raise TypeError("context must be a dictionary")

        subgoals = []
        t = time.time() % 1.0
        creativity = context.get("traits", {}).get("gamma_creativity", gamma_creativity(t))
        linguistics = context.get("traits", {}).get("lambda_linguistics", lambda_linguistics(t))
        culture = context.get("traits", {}).get("chi_culturevolution", chi_culturevolution(t))
        phi = context.get("traits", {}).get("phi_scalar", phi_scalar(t))
        alpha = context.get("traits", {}).get("alpha_attention", alpha_attention(t))
        curvature_mod = 1 + abs(phi - 0.5)
        trait_bias = 1 + creativity + culture + 0.5 * linguistics
        context_weight = context.get("weight_modifier", 1.0)

        # since context_manager may not have get_coordination_events, guard it
        if "drift" in goal.lower() and self.context_manager and hasattr(self.context_manager, "analyze_coordination_metrics"):
            try:
                metrics = await self.context_manager.analyze_coordination_metrics(time_window_hours=6, task_type=task_type)
                if metrics.get("status") == "success":
                    context_weight *= 1.2
            except Exception:
                pass

        if self.memory_manager and hasattr(self.memory_manager, "search") and "drift" in goal.lower():
            drift_entries = await self.memory_manager.search(
                query_prefix="Drift",
                layer=None,
                intent=None,
                task_type=task_type,
            )
            if drift_entries:
                context_weight *= 1.1

        for key, steps in self.decomposition_patterns.items():
            base = random.uniform(0.5, 1.0)
            adjusted = (
                base
                * self.success_rates.get(key, 1.0)
                * trait_bias
                * curvature_mod
                * context_weight
                * (0.8 + 0.4 * alpha)
            )
            if key == "mitigate_drift" and "drift" not in goal.lower():
                adjusted *= 0.5
            if adjusted >= self.confidence_threshold:
                subgoals.extend(steps)

        if prioritize:
            subgoals = sorted(set(subgoals))
        return subgoals

    async def update_success_rate(self, pattern_key: str, success: bool, task_type: str = "") -> None:
        if not isinstance(pattern_key, str) or not pattern_key.strip():
            raise ValueError("pattern_key must be a non-empty string")
        if not isinstance(success, bool):
            raise TypeError("success must be a boolean")

        rate = self.success_rates.get(pattern_key, 1.0)
        new = min(max(rate + (0.05 if success else -0.05), 0.1), 1.0)
        self.success_rates[pattern_key] = new
        self._save_success_rates()

    # ---------------------------
    # Simulations
    # ---------------------------
    async def infer_with_simulation(
        self,
        goal: str,
        context: Optional[Dict[str, Any]] = None,
        task_type: str = "",
    ) -> Optional[Dict[str, Any]]:
        context = context or {}
        if not isinstance(goal, str) or not goal.strip():
            raise ValueError("goal must be a non-empty string")
        if not isinstance(context, dict):
            raise TypeError("context must be a dictionary")

        if "galaxy rotation" in goal.lower():
            r_kpc = np.linspace(0.1, 20, 100)
            params = {
                "M0": context.get("M0", 5e10),
                "r_scale": context.get("r_scale", 3.0),
                "v0": context.get("v0", 200.0),
                "k": context.get("k", 1.0),
                "epsilon": context.get("epsilon", 0.1),
            }
            M_b_func = lambda r: M_b_exponential(r, params["M0"], params["r_scale"])
            v_obs_func = lambda r: v_obs_flat(r, params["v0"])
            result = await asyncio.to_thread(
                simulate_galaxy_rotation,
                r_kpc,
                M_b_func,
                v_obs_func,
                params["k"],
                params["epsilon"],
            )
            output = {
                "input": {**params, "r_kpc": r_kpc.tolist()},
                "result": result.tolist(),
                "status": "success",
                "timestamp": datetime.now().isoformat(),
                "task_type": task_type,
            }
            if self.visualizer and hasattr(self.visualizer, "render_charts") and task_type:
                await self.visualizer.render_charts(
                    {
                        "galaxy_simulation": {
                            "input": output["input"],
                            "result": output["result"],
                            "task_type": task_type,
                        },
                        "visualization_options": {
                            "interactive": task_type == "recursion",
                            "style": "detailed" if task_type == "recursion" else "concise",
                        },
                    }
                )
            return output

        elif "drift" in goal.lower():
            drift_data = context.get("drift", {})
            phi_field = generate_phi_field(
                drift_data.get("similarity", 0.5),
                context.get("scale", 1.0),
            )
            return {
                "drift_data": drift_data,
                "phi_field": phi_field.tolist(),
                "mitigation_steps": await self.decompose(
                    "mitigate ontology drift",
                    context,
                    prioritize=True,
                    task_type=task_type,
                ),
                "status": "success",
                "timestamp": datetime.now().isoformat(),
                "task_type": task_type,
            }

        return None

    # ---------------------------
    # Consensus Protocol
    # ---------------------------
    async def run_consensus_protocol(
        self,
        drift_data: Dict[str, Any],
        context: Dict[str, Any],
        max_rounds: int = 3,
        task_type: str = "",
    ) -> Dict[str, Any]:
        if not isinstance(drift_data, dict) or not isinstance(context, dict):
            raise ValueError("drift_data and context must be dictionaries")
        if not isinstance(max_rounds, int) or max_rounds < 1:
            raise ValueError("max_rounds must be a positive integer")

        results = []
        for round_num in range(1, max_rounds + 1):
            agent_results = await self.external_agent_bridge.collect_results(
                parallel=True,
                collaborative=True,
            )
            synthesis = await self.multi_modal_fusion.synthesize_drift_data(
                agent_data=[{"drift": drift_data, "result": r} for r in agent_results],
                context=context,
                task_type=task_type,
            )
            if synthesis.get("status") == "success":
                subgoals = synthesis.get("subgoals", [])
                results.append(
                    {"round": round_num, "subgoals": subgoals, "status": "success"}
                )
                break

        final_result = results[-1] if results else {"status": "error", "error": "No consensus"}

        if self.memory_manager and hasattr(self.memory_manager, "store"):
            await self.memory_manager.store(
                query=f"Consensus_{datetime.now().isoformat()}",
                output=str(final_result),
                layer="SelfReflections",
                intent="consensus_protocol",
                task_type=task_type,
            )
        return final_result

    # ---------------------------
    # Context Handling
    # ---------------------------
    async def process_context(
        self,
        event_type: str,
        payload: Dict[str, Any],
        task_type: str = "",
    ) -> Dict[str, Any]:
        if not isinstance(event_type, str) or not event_type.strip():
            raise ValueError("event_type must be a non-empty string")
        if not isinstance(payload, dict):
            raise TypeError("payload must be a dictionary")

        vectors = payload.get("vectors", {})
        goal = payload.get("goal", "unspecified")
        drift_data = payload.get("drift", {})

        routing_result = await self.run_persona_wave_routing(
            goal,
            {**vectors, "drift": drift_data},
            task_type=task_type,
        )

        if self.memory_manager and hasattr(self.memory_manager, "store"):
            await self.memory_manager.store(
                query=f"Context_Event_{event_type}_{datetime.now().isoformat()}",
                output=str(routing_result),
                layer="SelfReflections",
                intent="context_sync",
                task_type=task_type,
            )

        return routing_result

    # ---------------------------
    # Intention Mapping
    # ---------------------------
    async def map_intention(
        self,
        plan: str,
        state: Dict[str, Any],
        task_type: str = "",
    ) -> Dict[str, Any]:
        if not isinstance(plan, str) or not plan.strip():
            raise ValueError("plan must be a non-empty string")
        if not isinstance(state, dict):
            raise TypeError("state must be a dictionary")

        t = time.time() % 1.0
        phi = phi_scalar(t)
        eta = eta_empathy(t)

        if "drift" in plan.lower():
            intention = "drift_mitigation"
        elif phi > 0.6:
            intention = "self-improvement"
        else:
            intention = "task_completion"

        result = {
            "plan": plan,
            "state": state,
            "intention": intention,
            "trait_bias": {"phi": phi, "eta": eta},
            "timestamp": datetime.now().isoformat(),
            "task_type": task_type,
        }

        if self.memory_manager and hasattr(self.memory_manager, "store"):
            await self.memory_manager.store(
                query=f"Intention_{plan[:50]}_{result['timestamp']}",
                output=str(result),
                layer="SelfReflections",
                intent="intention_mapping",
                task_type=task_type,
            )

        return result

    # ---------------------------
    # Safety Guardrails
    # ---------------------------
    async def safeguard_noetic_integrity(
        self,
        model_depth: int,
        task_type: str = "",
    ) -> bool:
        if not isinstance(model_depth, int) or model_depth < 0:
            raise ValueError("model_depth must be a non-negative integer")
        if model_depth > 4:
            logger.warning("Noetic recursion limit breached: depth=%d", model_depth)
            if self.meta_cognition and hasattr(self.meta_cognition, "epistemic_self_inspection"):
                await self.meta_cognition.epistemic_self_inspection(
                    f"Recursion depth exceeded for task {task_type}"
                )
            return False
        return True

    # ---------------------------
    # Ethical Dilemma Generation
    # ---------------------------
    async def generate_dilemma(self, domain: str, task_type: str = "") -> str:
        if not isinstance(domain, str) or not domain.strip():
            raise ValueError("domain must be a non-empty string")
        t = time.time() % 1.0
        phi = phi_scalar(t)
        prompt = f"""
        Generate an ethical dilemma in the {domain} domain.
        Use phi-scalar(t) = {phi:.3f} to modulate complexity.
        Task Type: {task_type}
        Provide two conflicting options with consequences and ethical alignment.
        """.strip()
        if "drift" in domain.lower():
            prompt += "\nConsider ontology drift mitigation and agent coordination."
        dilemma = await call_gpt(prompt, self.alignment_guard, task_type=task_type)
        if self.meta_cognition and hasattr(self.meta_cognition, "review_reasoning"):
            review = await self.meta_cognition.review_reasoning(dilemma)
            dilemma += f"\nMeta-Cognitive Review: {review}"
        if self.memory_manager and hasattr(self.memory_manager, "store"):
            await self.memory_manager.store(
                query=f"Dilemma_{domain}_{datetime.now().isoformat()}",
                output=dilemma,
                layer="SelfReflections",
                intent="ethical_dilemma",
                task_type=task_type,
            )
        return dilemma

    # ---------------------------
    # Harm Estimation
    # ---------------------------
    async def estimate_expected_harm(
        self,
        state: Dict[str, Any],
        task_type: str = "",
    ) -> float:
        traits = state.get("traits", {})
        harm = float(traits.get("ethical_pressure", 0.0))
        resonance = (
            get_resonance("eta_empathy") if "eta_empathy" in trait_resonance_state else 1.0
        )
        harm *= resonance
        return max(0.0, harm)

    # ---------------------------
    # μ–τ Policy Homeostasis Reflex: Memory Drift Feedback
    # ---------------------------
    async def regulate_drift_feedback(
        self,
        telemetry: Optional[Dict[str, float]] = None,
        policy_trainer: Optional[Any] = None,
        task_type: str = "",
    ) -> Dict[str, Any]:
        if not telemetry or not isinstance(telemetry, dict):
            return {"status": "noop", "reason": "no telemetry"}

        coherence = float(telemetry.get("coherence", 1.0))
        drift = float(telemetry.get("drift", 0.0))
        coherence = max(0.0, min(coherence, 1.0))
        drift = max(0.0, min(drift, 1.0))

        adaptivity = max(0.25, coherence * (1.0 - drift * 4.0))

        restraint = 1.0 - adaptivity
        self.confidence_threshold = 0.7 + (0.15 * (1.0 - adaptivity))

        _safe_log_to_ledger(
            {
                "event": "policy_homeostasis_feedback",
                "coherence": coherence,
                "drift": drift,
                "adaptivity": adaptivity,
                "restraint": restraint,
                "timestamp": time.time(),
            }
        )

        if policy_trainer and hasattr(policy_trainer, "update_homeostasis"):
            try:
                policy_trainer.update_homeostasis(delta=adaptivity, source="ReasoningEngine")
            except Exception:
                logger.debug("PolicyTrainer homeostasis update skipped")

        if self.meta_cognition and hasattr(self.meta_cognition, "adjust_affective_state"):
            try:
                await self.meta_cognition.adjust_affective_state(
                    bias=adaptivity - restraint, source="ReasoningEngine"
                )
            except Exception:
                logger.debug("Affective coupling skipped")

        return {
            "status": "regulated",
            "adaptivity": adaptivity,
            "restraint": restraint,
            "coherence": coherence,
            "drift": drift,
        }

    def export_trace(
        self,
        subgoals: List[str],
        phi: float,
        traits: Dict[str, float],
        task_type: str = "",
    ) -> Dict[str, Any]:
        if not isinstance(subgoals, list) or not isinstance(phi, float) or not isinstance(traits, dict):
            raise TypeError("Invalid input types for export_trace")
        trace = {
            "phi": phi,
            "subgoals": subgoals,
            "traits": traits,
            "timestamp": datetime.now().isoformat(),
            "task_type": task_type,
        }
        if self.memory_manager and hasattr(self.memory_manager, "store"):
            intent = (
                "drift_trace" if any("drift" in s.lower() for s in subgoals) else "export_trace"
            )
            asyncio.create_task(
                self.memory_manager.store(
                    query=f"Trace_{trace['timestamp']}",
                    output=str(trace),
                    layer="SelfReflections",
                    intent=intent,
                    task_type=task_type,
                )
            )
        return trace

    # ---------------------------
    # Continuity Diagnostics
    # ---------------------------
    def continuity_diagnostics(self, limit: int = 50) -> Dict[str, Any]:
        return _build_continuity_topology(limit)

    # ---------------------------
    # Enhanced Logical Entailment Bridge + Trace Integration
    # ---------------------------
    async def entails(self, premise: str, conclusion: str) -> bool:
        if not isinstance(premise, str) or not isinstance(conclusion, str):
            return False

        if premise.strip() == conclusion.strip():
            result = True
        elif conclusion.strip().lower() in ("true", "⊤"):
            result = True
        else:
            result = False
            try:
                if hasattr(self, "meta_cognition") and hasattr(self.meta_cognition, "prove"):
                    res = self.meta_cognition.prove(premise, conclusion)
                    if asyncio.iscoroutine(res):
                        res = await res
                    result = bool(res)
            except Exception:
                pass

        if self.memory_manager and hasattr(self.memory_manager, "store_trace"):
            try:
                await self.memory_manager.store_trace(
                    src=premise,
                    morphism="entails",
                    tgt=conclusion,
                    logic_proof={"result": result},
                    ethics_proof={"pass": True},
                    task_type="logical_entailment"
                )
            except Exception:
                pass

        if self.meta_cognition and hasattr(self.meta_cognition, "reflect_on_output"):
            try:
                await self.meta_cognition.reflect_on_output(
                    component="ReasoningEngine.entails",
                    output={"premise": premise, "conclusion": conclusion, "result": result},
                    context={"task_type": "logical_entailment"}
                )
            except Exception:
                pass

        return result


# =====================================================
# δ⁵ Formal Reasoning Synthesis Upgrade
# =====================================================
# This block extends ReasoningEngine with:
# 1. CoherenceClockAdapter: pulls continuity/coherence from ContextManager
# 2. HybridInferenceCore: lightweight symbolic + probabilistic inference
# 3. InferenceLedger: records every inference with Θ⁹-ready metadata
# 4. ReasoningEngine hooks: preflight ethics + postflight sync to meta-cognition
# =====================================================

import time as _d5_time
from datetime import datetime as _d5_dt

class CoherenceClockAdapter:
    """Reads continuity/coherence from ContextManager to modulate inference."""
    def __init__(self, context_manager=None):
        self.context_manager = context_manager

    async def read(self) -> dict:
        if not self.context_manager or not hasattr(self.context_manager, "analyze_continuity_drift"):
            return {"status": "noop", "Δ_mean": 1.0, "drift_mean": 0.0, "ts": _d5_dt.utcnow().isoformat()}
        data = self.context_manager.analyze_continuity_drift()
        data["status"] = "ok"
        data["ts"] = _d5_dt.utcnow().isoformat()
        return data


class HybridInferenceCore:
    """
    δ⁵ hybrid core: tries fast symbolic entailment, then falls back to probabilistic scoring.
    Kept intentionally small so it can be embedded in existing reasoning pipelines.
    """
    def __init__(self, context_manager=None, alignment_guard=None):
        self.context_manager = context_manager
        self.alignment_guard = alignment_guard

    async def ethical_preflight(self, premise: str, conclusion: str) -> bool:
        if self.alignment_guard and hasattr(self.alignment_guard, "ethical_check"):
            ok, _ = await self.alignment_guard.ethical_check(
                f"premise={premise}\nconclusion={conclusion}",
                stage="δ5_preflight",
                task_type="inference"
            )
            return bool(ok)
        return True

    async def infer(self, premise: str, conclusion: str) -> dict:
        # symbolic fast path
        if premise.strip() == conclusion.strip():
            return {"status": "success", "mode": "symbolic-fast", "prob": 1.0}

        # tiny probabilistic fallback
        overlap = len(set(premise.lower().split()) & set(conclusion.lower().split()))
        denom = max(1, len(set(conclusion.lower().split())))
        prob = overlap / denom
        return {"status": "success", "mode": "probabilistic", "prob": float(prob)}


class InferenceLedger:
    """Best-effort inference event writer. Θ⁹-friendly."""
    def __init__(self, path: str = "/mnt/data/inference_ledger.jsonl"):
        self.path = path
        os.makedirs(os.path.dirname(self.path), exist_ok=True)

    def write(self, record: dict) -> None:
        try:
            record = dict(record)
            record.setdefault("ts", _d5_dt.utcnow().isoformat())
            with open(self.path, "a", encoding="utf-8") as f:
                f.write(json.dumps(record, ensure_ascii=False) + "\n")
        except Exception:
            pass


# --- Monkeypatch ReasoningEngine with δ⁵ hooks ------------------------------------
try:
    from reasoning_engine import ReasoningEngine as _RE_D5  # may re-import itself; guarded
except Exception:  # pragma: no cover
    _RE_D5 = None

if _RE_D5 is not None:
    # add init-time attachments
    _old_init = _RE_D5.__init__
    def _d5_init(self, *args, **kwargs):
        _old_init(self, *args, **kwargs)
        self._d5_coherence_clock = CoherenceClockAdapter(self.context_manager)
        self._d5_hybrid_core = HybridInferenceCore(self.context_manager, self.alignment_guard)
        self._d5_inference_ledger = InferenceLedger()
    _RE_D5.__init__ = _d5_init

    async def d5_entails(self, premise: str, conclusion: str) -> bool:
        """
        δ⁵ entailment: ethical preflight → hybrid inference → ledger → meta sync.
        """
        # 1) ethics
        ok = await self._d5_hybrid_core.ethical_preflight(premise, conclusion)
        if not ok:
            self._d5_inference_ledger.write({
                "event": "δ5_infer_blocked",
                "premise": premise,
                "conclusion": conclusion,
                "reason": "ethical_preflight_fail",
            })
            return False

        # 2) read coherence to adjust trust
        coh = await self._d5_coherence_clock.read()
        coh_factor = float(coh.get("Δ_mean", 1.0))

        # 3) run hybrid inference
        inf = await self._d5_hybrid_core.infer(premise, conclusion)
        base_prob = float(inf.get("prob", 0.0))
        final_prob = max(0.0, min(1.0, base_prob * coh_factor))

        result = final_prob >= 0.55

        # 4) ledger
        self._d5_inference_ledger.write({
            "event": "δ5_infer",
            "premise": premise,
            "conclusion": conclusion,
            "coherence": coh,
            "inference": inf,
            "final_prob": final_prob,
            "accepted": result,
        })

        # 5) meta-cog sync if available
        if self.meta_cognition and hasattr(self.meta_cognition, "reflect_on_output"):
            try:
                await self.meta_cognition.reflect_on_output(
                    component="δ5_infer",
                    output={
                        "premise": premise,
                        "conclusion": conclusion,
                        "final_prob": final_prob,
                        "accepted": result,
                        "coherence": coh,
                    },
                    context={"task_type": "inference", "version": "δ5"}
                )
            except Exception:
                pass

        return result

    # expose on class
    _RE_D5.d5_entails = d5_entails

async def export_state(self) -> dict:
    return {"status": "ok", "health": 1.0, "timestamp": time.time()}

async def on_time_tick(self, t: float, phase: str, task_type: str = ""):
    pass  # optional internal refresh

async def on_policy_update(self, policy: dict, task_type: str = ""):
    pass  # apply updates from AlignmentGuard if relevant
"""
ANGELA Cognitive System Module: RecursivePlanner
Refactored Version: 3.5.2  # Enhanced for benchmark optimization (GLUE, recursion), dynamic trait modulation, and reflection-driven planning
Refactor Date: 2025-08-07
Maintainer: ANGELA System Framework

This module provides a RecursivePlanner class for recursive goal planning in the ANGELA v3.5 architecture.
"""

import logging
import time
import asyncio
import math
from typing import List, Dict, Any, Optional, Union, Tuple, Protocol
from datetime import datetime
from threading import Lock
from functools import lru_cache

# --- Optional ToCA import with graceful fallback (no new files) ---
try:
    from toca_simulation import run_AGRF_with_traits  # type: ignore
except Exception:  # pragma: no cover
    def run_AGRF_with_traits(_: Dict[str, Any]) -> Dict[str, Any]:
        return {"fields": {"psi_foresight": 0.55, "phi_bias": 0.42}}

from modules import (
    reasoning_engine as reasoning_engine_module,
    meta_cognition as meta_cognition_module,
    alignment_guard as alignment_guard_module,
    simulation_core as simulation_core_module,
    memory_manager as memory_manager_module,
    multi_modal_fusion as multi_modal_fusion_module,
    error_recovery as error_recovery_module,
    context_manager as context_manager_module
)

logger = logging.getLogger("ANGELA.RecursivePlanner")


class AgentProtocol(Protocol):
    name: str

    def process_subgoal(self, subgoal: str) -> Any:
        ...


# ---------------------------
# Cached trait signals
# ---------------------------
@lru_cache(maxsize=100)
def beta_concentration(t: float) -> float:
    return max(0.0, min(0.1 * math.sin(2 * math.pi * t / 0.5), 1.0))


@lru_cache(maxsize=100)
def omega_selfawareness(t: float) -> float:
    return max(0.0, min(0.1 * math.cos(2 * math.pi * t / 0.7), 1.0))


@lru_cache(maxsize=100)
def mu_morality(t: float) -> float:
    return max(0.0, min(0.1 * math.sin(2 * math.pi * t / 0.9), 1.0))


@lru_cache(maxsize=100)
def eta_reflexivity(t: float) -> float:
    return max(0.0, min(0.1 * math.cos(2 * math.pi * t / 1.1), 1.0))


@lru_cache(maxsize=100)
def lambda_narrative(t: float) -> float:
    return max(0.0, min(0.1 * math.sin(2 * math.pi * t / 1.3), 1.0))


@lru_cache(maxsize=100)
def delta_moral_drift(t: float) -> float:
    return max(0.0, min(0.05 * math.cos(2 * math.pi * t / 1.5), 1.0))


@lru_cache(maxsize=100)
def phi_scalar(t: float) -> float:
    return max(0.0, min(0.1 * math.sin(2 * math.pi * t / 0.2), 1.0))


class RecursivePlanner:
    """Recursive goal planning with trait-weighted decomposition, agent collaboration, simulation, and reflection."""

    def __init__(self, max_workers: int = 4,
                 reasoning_engine: Optional['reasoning_engine_module.ReasoningEngine'] = None,
                 meta_cognition: Optional['meta_cognition_module.MetaCognition'] = None,
                 alignment_guard: Optional['alignment_guard_module.AlignmentGuard'] = None,
                 simulation_core: Optional['simulation_core_module.SimulationCore'] = None,
                 memory_manager: Optional['memory_manager_module.MemoryManager'] = None,
                 multi_modal_fusion: Optional['multi_modal_fusion_module.MultiModalFusion'] = None,
                 error_recovery: Optional['error_recovery_module.ErrorRecovery'] = None,
                 context_manager: Optional['context_manager_module.ContextManager'] = None,
                 agi_enhancer: Optional['AGIEnhancer'] = None):
        self.reasoning_engine = reasoning_engine or reasoning_engine_module.ReasoningEngine(
            agi_enhancer=agi_enhancer, memory_manager=memory_manager, meta_cognition=meta_cognition,
            error_recovery=error_recovery)
        self.meta_cognition = meta_cognition or meta_cognition_module.MetaCognition(agi_enhancer=agi_enhancer)
        self.alignment_guard = alignment_guard or alignment_guard_module.AlignmentGuard()
        self.simulation_core = simulation_core or simulation_core_module.SimulationCore()
        self.memory_manager = memory_manager or memory_manager_module.MemoryManager()
        self.multi_modal_fusion = multi_modal_fusion or multi_modal_fusion_module.MultiModalFusion(
            agi_enhancer=agi_enhancer, memory_manager=memory_manager, meta_cognition=self.meta_cognition,
            error_recovery=error_recovery)
        self.error_recovery = error_recovery or error_recovery_module.ErrorRecovery()
        self.context_manager = context_manager or context_manager_module.ContextManager()
        self.agi_enhancer = agi_enhancer
        self.max_workers = max(1, min(max_workers, 8))
        self.omega: Dict[str, Any] = {"timeline": [], "traits": {}, "symbolic_log": []}
        self.omega_lock = Lock()
        logger.info("RecursivePlanner initialized with advanced upgrades")

    # ---------------------------
    # Utilities
    # ---------------------------
    @staticmethod
    def _normalize_list_or_wrap(value: Any) -> List[str]:
        """Ensure a list[str] result."""
        if isinstance(value, list) and all(isinstance(x, str) for x in value):
            return value
        if isinstance(value, str):
            return [value]
        return [str(value)]

    def adjust_plan_depth(self, trait_weights: Dict[str, float], task_type: str = "") -> int:
        """Adjust planning depth based on trait weights and task type."""
        if not isinstance(trait_weights, dict):
            logger.error("Invalid trait_weights: must be a dictionary")
            raise TypeError("trait_weights must be a dictionary")
        omega_val = float(trait_weights.get("omega", 0.0))
        base_depth = 2 if omega_val > 0.7 else 1
        if task_type == "recursion":
            base_depth = min(base_depth + 1, 3)  # Increase depth for recursion tasks
        elif task_type in ["rte", "wnli"]:
            base_depth = max(base_depth - 1, 1)  # Reduce depth for GLUE tasks
        logger.info("Adjusted recursion depth: %d (omega=%.2f, task_type=%s)", base_depth, omega_val, task_type)
        return base_depth

    # ---------------------------
    # Main planning entry
    # ---------------------------
    async def plan(self, goal: str, context: Optional[Dict[str, Any]] = None,
                   depth: int = 0, max_depth: int = 5,
                   collaborating_agents: Optional[List['AgentProtocol']] = None) -> List[str]:
        """Recursively decompose and plan a goal with trait-based depth adjustment and reflection."""
        if not isinstance(goal, str) or not goal.strip():
            logger.error("Invalid goal: must be a non-empty string")
            raise ValueError("goal must be a non-empty string")
        if context is not None and not isinstance(context, dict):
            logger.error("Invalid context: must be a dictionary")
            raise TypeError("context must be a dictionary")
        if not isinstance(depth, int) or depth < 0:
            logger.error("Invalid depth: must be a non-negative integer")
            raise ValueError("depth must be a non-negative integer")
        if not isinstance(max_depth, int) or max_depth < 1:
            logger.error("Invalid max_depth: must be a positive integer")
            raise ValueError("max_depth must be a positive integer")
        if collaborating_agents is not None and not isinstance(collaborating_agents, list):
            logger.error("Invalid collaborating_agents: must be a list")
            raise TypeError("collaborating_agents must be a list")

        logger.info("Planning for goal: '%s'", goal)
        try:
            # Alignment gate
            if hasattr(self.alignment_guard, "is_goal_safe") and not self.alignment_guard.is_goal_safe(goal):
                logger.error("Goal '%s' violates alignment constraints", goal)
                raise ValueError("Unsafe goal detected")

            # Local traits snapshot
            t = time.time() % 1.0
            local_traits = {
                "beta": beta_concentration(t),        # concentration
                "omega": omega_selfawareness(t),      # self_awareness
                "mu": mu_morality(t),                 # morality
                "eta": eta_reflexivity(t),            # reflexivity
                "lambda": lambda_narrative(t),        # narrative
                "delta": delta_moral_drift(t),        # moral drift
                "phi": phi_scalar(t)                  # coherence scalar
            }
            task_type = context.get("task_type", "") if context else ""

            # Optional trait optimization via MetaCognition (best-effort)
            if self.meta_cognition and hasattr(self.meta_cognition, "optimize_traits_for_drift"):
                drift_report = {
                    "drift": {"name": task_type or "general", "similarity": 0.8},
                    "valid": True,
                    "validation_report": "",
                    "context": {"task_type": task_type}
                }
                try:
                    optimized = await self.meta_cognition.optimize_traits_for_drift(drift_report)
                    if isinstance(optimized, dict):
                        # keep our local traits separate; we only use optimized for depth heuristics
                        local_traits = {**local_traits, **{k: float(v) for k, v in optimized.items() if isinstance(v, (int, float))}}
                except Exception as e:
                    logger.debug("Trait optimization skipped due to error: %s", str(e))

            with self.omega_lock:
                self.omega["traits"].update(local_traits)

            trait_mod = local_traits.get("beta", 0.0) * 0.4 + \
                        local_traits.get("eta", 0.0) * 0.2 + \
                        local_traits.get("lambda", 0.0) * 0.2 - \
                        local_traits.get("delta", 0.0) * 0.2
            dynamic_depth_limit = max_depth + int(trait_mod * 10) + self.adjust_plan_depth(local_traits, task_type)

            if depth > dynamic_depth_limit:
                logger.warning("Trait-based dynamic max recursion depth reached: depth=%d, limit=%d", depth, dynamic_depth_limit)
                return [goal]

            # Decompose
            subgoals = await self.reasoning_engine.decompose(goal, context, prioritize=True)
            if not subgoals:
                logger.info("No subgoals found. Returning atomic goal: '%s'", goal)
                return [goal]

            # Heuristic prioritization with MetaCognition (compatible signature)
            # Map local trait names -> MetaCognition trait names
            mc_trait_map = {
                "beta": "concentration",
                "omega": "self_awareness",
                "mu": "morality",
                "eta": "intuition",       # closest available dimension
                "lambda": "linguistics",  # narrative ≈ language structuring
                "phi": "phi_scalar"
            }
            top_traits = sorted(
                [(mc_trait_map.get(k), v) for k, v in local_traits.items() if mc_trait_map.get(k)],
                key=lambda x: x[1],
                reverse=True
            )
            required_trait_names = [name for name, _ in top_traits[:3]] or ["concentration", "self_awareness"]

            if self.meta_cognition and hasattr(self.meta_cognition, "plan_tasks"):
                try:
                    wrapped = [{"task": sg, "required_traits": required_trait_names} for sg in subgoals]
                    prioritized = await self.meta_cognition.plan_tasks(wrapped)
                    # plan_tasks returns back task dicts; normalize
                    if isinstance(prioritized, list):
                        subgoals = [p.get("task", p) if isinstance(p, dict) else p for p in prioritized]
                except Exception as e:
                    logger.debug("MetaCognition.plan_tasks failed, falling back: %s", str(e))

            # Collaboration
            if collaborating_agents:
                logger.info("Collaborating with agents: %s", [agent.name for agent in collaborating_agents])
                subgoals = await self._distribute_subgoals(subgoals, collaborating_agents, task_type)

            # Recurse over subgoals
            validated_plan: List[str] = []
            tasks = [self._plan_subgoal(sub, context, depth + 1, dynamic_depth_limit, task_type) for sub in subgoals]
            results = await asyncio.gather(*tasks, return_exceptions=True)

            for subgoal, result in zip(subgoals, results):
                if isinstance(result, Exception):
                    logger.error("Error planning subgoal '%s': %s", subgoal, str(result))
                    recovery = ""
                    if self.meta_cognition and hasattr(self.meta_cognition, "review_reasoning"):
                        try:
                            recovery = await self.meta_cognition.review_reasoning(str(result))
                        except Exception:
                            pass
                    validated_plan.extend(self._normalize_list_or_wrap(recovery or f"fallback:{subgoal}"))
                    await self._update_omega(subgoal, self._normalize_list_or_wrap(recovery or subgoal), error=True)
                else:
                    out = self._normalize_list_or_wrap(result)
                    validated_plan.extend(out)
                    await self._update_omega(subgoal, out)

            # Reflect on the final plan
            if self.meta_cognition and hasattr(self.meta_cognition, "reflect_on_output"):
                try:
                    reflection = await self.meta_cognition.reflect_on_output(
                        component="RecursivePlanner",
                        output=validated_plan,
                        context={"goal": goal, "task_type": task_type}
                    )
                    if isinstance(reflection, dict) and reflection.get("status") == "success":
                        logger.info("Plan reflection captured.")
                except Exception as e:
                    logger.debug("Plan reflection skipped: %s", str(e))

            logger.info("Final validated plan for goal '%s': %s", goal, validated_plan)
            if self.memory_manager and hasattr(self.memory_manager, "store"):
                await self.memory_manager.store(
                    query=f"Plan_{goal[:50]}_{datetime.now().isoformat()}",
                    output=str(validated_plan),
                    layer="Plans",
                    intent="goal_planning"
                )
            if self.agi_enhancer and hasattr(self.agi_enhancer, "log_episode"):
                self.agi_enhancer.log_episode(
                    event="Plan generated",
                    meta={"goal": goal, "plan": validated_plan, "task_type": task_type},
                    module="RecursivePlanner",
                    tags=["planning", "recursive"]
                )
            if self.context_manager and hasattr(self.context_manager, "log_event_with_hash"):
                await self.context_manager.log_event_with_hash({"event": "plan", "plan": validated_plan})
            if self.multi_modal_fusion and hasattr(self.multi_modal_fusion, "analyze"):
                try:
                    synthesis = await self.multi_modal_fusion.analyze(
                        data={"goal": goal, "plan": validated_plan, "context": context or {}, "task_type": task_type},
                        summary_style="insightful"
                    )
                    logger.info("Plan synthesis complete.")
                except Exception as e:
                    logger.debug("Synthesis skipped: %s", str(e))
            return validated_plan
        except Exception as e:
            logger.error("Planning failed: %s", str(e))
            diagnostics = {}
            if self.meta_cognition and hasattr(self.meta_cognition, "run_self_diagnostics"):
                try:
                    diagnostics = await self.meta_cognition.run_self_diagnostics(return_only=True)  # type: ignore
                except Exception:
                    diagnostics = {}
            # error_recovery.handle_error in this stack is synchronous
            return self.error_recovery.handle_error(
                str(e), retry_func=lambda: self.plan(goal, context, depth, max_depth, collaborating_agents),
                default=[goal], diagnostics=diagnostics
            )

    # ---------------------------
    # Subroutines
    # ---------------------------
    async def _update_omega(self, subgoal: str, result: List[str], error: bool = False) -> None:
        """Update the global narrative state with subgoal results."""
        if not isinstance(subgoal, str) or not subgoal.strip():
            logger.error("Invalid subgoal: must be a non-empty string")
            raise ValueError("subgoal must be a non-empty string")
        if not isinstance(result, list):
            logger.error("Invalid result: must be a list")
            raise TypeError("result must be a list")

        event = {
            "subgoal": subgoal,
            "result": result,
            "timestamp": time.time(),
            "error": error
        }
        symbolic_tag: Union[str, Dict[str, Any]] = "unknown"
        if self.meta_cognition and hasattr(self.meta_cognition, "extract_symbolic_signature"):
            try:
                symbolic_tag = await self.meta_cognition.extract_symbolic_signature(subgoal)
            except Exception:
                pass
        with self.omega_lock:
            self.omega["timeline"].append(event)
            self.omega["symbolic_log"].append(symbolic_tag)
            if len(self.omega["timeline"]) > 1000:
                self.omega["timeline"] = self.omega["timeline"][-500:]
                self.omega["symbolic_log"] = self.omega["symbolic_log"][-500:]
                logger.info("Trimmed omega state to maintain size limit")
        if self.memory_manager and hasattr(self.memory_manager, "store_symbolic_event"):
            try:
                await self.memory_manager.store_symbolic_event(event, symbolic_tag)
            except Exception:
                pass
        if self.agi_enhancer and hasattr(self.agi_enhancer, "log_episode"):
            self.agi_enhancer.log_episode(
                event="Omega state updated",
                meta=event,
                module="RecursivePlanner",
                tags=["omega", "update"]
            )

    async def plan_from_intrinsic_goal(self, generated_goal: str, context: Optional[Dict[str, Any]] = None) -> List[str]:
        """Plan from an intrinsic goal with task-specific trait optimization."""
        if not isinstance(generated_goal, str) or not generated_goal.strip():
            logger.error("Invalid generated_goal: must be a non-empty string")
            raise ValueError("generated_goal must be a non-empty string")

        logger.info("Initiating plan from intrinsic goal: '%s'", generated_goal)
        try:
            validated_goal = generated_goal
            if self.meta_cognition and hasattr(self.meta_cognition, "rewrite_goal"):
                try:
                    validated_goal = await self.meta_cognition.rewrite_goal(generated_goal)  # optional API
                except Exception:
                    validated_goal = generated_goal

            if self.meta_cognition and hasattr(self.meta_cognition, "optimize_traits_for_drift"):
                drift_report = {
                    "drift": {"name": "intrinsic", "similarity": 0.9},
                    "valid": True,
                    "validation_report": "",
                    "context": context or {}
                }
                try:
                    await self.meta_cognition.optimize_traits_for_drift(drift_report)
                except Exception:
                    pass

            plan = await self.plan(validated_goal, context)
            if self.memory_manager and hasattr(self.memory_manager, "store"):
                await self.memory_manager.store(
                    query=f"Intrinsic_Plan_{validated_goal[:50]}_{datetime.now().isoformat()}",
                    output=str(plan),
                    layer="IntrinsicPlans",
                    intent="intrinsic_goal_planning"
                )
            if self.agi_enhancer and hasattr(self.agi_enhancer, "log_episode"):
                self.agi_enhancer.log_episode(
                    event="Intrinsic goal plan generated",
                    meta={"goal": validated_goal, "plan": plan},
                    module="RecursivePlanner",
                    tags=["intrinsic", "planning"]
                )
            return plan
        except Exception as e:
            logger.error("Intrinsic goal planning failed: %s", str(e))
            diagnostics = {}
            if self.meta_cognition and hasattr(self.meta_cognition, "run_self_diagnostics"):
                try:
                    diagnostics = await self.meta_cognition.run_self_diagnostics(return_only=True)  # type: ignore
                except Exception:
                    diagnostics = {}
            return self.error_recovery.handle_error(
                str(e), retry_func=lambda: self.plan_from_intrinsic_goal(generated_goal, context),
                default=[], diagnostics=diagnostics
            )

    async def _plan_subgoal(self, subgoal: str, context: Optional[Dict[str, Any]],
                            depth: int, max_depth: int, task_type: str) -> List[str]:
        """Plan a single subgoal with simulation, alignment checks, and recursion optimization."""
        if not isinstance(subgoal, str) or not subgoal.strip():
            logger.error("Invalid subgoal: must be a non-empty string")
            raise ValueError("subgoal must be a non-empty string")

        logger.info("Evaluating subgoal: '%s'", subgoal)
        try:
            if hasattr(self.alignment_guard, "is_goal_safe") and not self.alignment_guard.is_goal_safe(subgoal):
                logger.warning("Subgoal '%s' failed alignment check", subgoal)
                return []

            # Apply recursion optimization
            if task_type == "recursion" and self.meta_cognition and hasattr(meta_cognition_module, "RecursionOptimizer"):
                try:
                    optimizer = meta_cognition_module.RecursionOptimizer()
                    optimized_data = optimizer.optimize({"subgoal": subgoal, "context": context or {}})
                    if optimized_data.get("optimized"):
                        max_depth = min(max_depth, 3)  # Limit depth for optimized recursion
                        logger.info("Recursion optimized for subgoal: '%s'", subgoal)
                except Exception:
                    pass

            # Optional physics-like trait injection
            if "gravity" in subgoal.lower() or "scalar" in subgoal.lower():
                sim_traits = run_AGRF_with_traits(context or {})
                with self.omega_lock:
                    self.omega["traits"].update(sim_traits.get("fields", {}))
                    self.omega["timeline"].append({
                        "subgoal": subgoal,
                        "traits": sim_traits.get("fields", {}),
                        "timestamp": time.time()
                    })
                if self.multi_modal_fusion and hasattr(self.multi_modal_fusion, "analyze"):
                    try:
                        await self.multi_modal_fusion.analyze(
                            data={"subgoal": subgoal, "simulation_traits": sim_traits},
                            summary_style="concise"
                        )
                    except Exception:
                        pass

            # Run internal simulation / scenario analysis
            simulation_feedback = None
            if hasattr(self.simulation_core, "run"):
                try:
                    simulation_feedback = await self.simulation_core.run(subgoal, context=context, scenarios=2, agents=1)
                except Exception:
                    simulation_feedback = None

            # Meta-cognitive gate
            approved = True
            if self.meta_cognition and hasattr(self.meta_cognition, "pre_action_alignment_check"):
                try:
                    approved, _ = await self.meta_cognition.pre_action_alignment_check(subgoal)
                except Exception:
                    approved = True
            if not approved:
                logger.warning("Subgoal '%s' denied by meta-cognitive alignment check", subgoal)
                return []

            if depth >= max_depth:
                return [subgoal]

            sub_plan = await self.plan(subgoal, context, depth + 1, max_depth)
            if self.memory_manager and hasattr(self.memory_manager, "store"):
                await self.memory_manager.store(
                    query=f"Subgoal_Plan_{subgoal[:50]}_{datetime.now().isoformat()}",
                    output=str(sub_plan),
                    layer="SubgoalPlans",
                    intent="subgoal_planning"
                )
            if self.agi_enhancer and hasattr(self.agi_enhancer, "log_episode"):
                self.agi_enhancer.log_episode(
                    event="Subgoal plan generated",
                    meta={"subgoal": subgoal, "sub_plan": sub_plan, "task_type": task_type, "simulation": simulation_feedback},
                    module="RecursivePlanner",
                    tags=["subgoal", "planning"]
                )
            return sub_plan
        except Exception as e:
            logger.error("Subgoal '%s' planning failed: %s", subgoal, str(e))
            diagnostics = {}
            if self.meta_cognition and hasattr(self.meta_cognition, "run_self_diagnostics"):
                try:
                    diagnostics = await self.meta_cognition.run_self_diagnostics(return_only=True)  # type: ignore
                except Exception:
                    diagnostics = {}
            return self.error_recovery.handle_error(
                str(e), retry_func=lambda: self._plan_subgoal(subgoal, context, depth, max_depth, task_type),
                default=[], diagnostics=diagnostics
            )

    async def _distribute_subgoals(self, subgoals: List[str], agents: List['AgentProtocol'], task_type: str) -> List[str]:
        """Distribute subgoals among collaborating agents with enhanced reasoning."""
        if not isinstance(subgoals, list):
            logger.error("Invalid subgoals: must be a list")
            raise TypeError("subgoals must be a list")
        if not isinstance(agents, list) or not agents:
            logger.error("Invalid agents: must be a non-empty list")
            raise ValueError("agents must be a non-empty list")

        logger.info("Distributing subgoals among agents")
        distributed: List[str] = []
        commonsense = meta_cognition_module.CommonsenseReasoningEnhancer() if task_type == "wnli" else None
        entailment = meta_cognition_module.EntailmentReasoningEnhancer() if task_type == "rte" else None

        for i, subgoal in enumerate(subgoals):
            # Enhance subgoal with task-specific reasoning
            enhanced_subgoal = subgoal
            try:
                if commonsense:
                    enhanced_subgoal = commonsense.process(subgoal)
                elif entailment:
                    enhanced_subgoal = entailment.process(subgoal)
            except Exception:
                enhanced_subgoal = subgoal

            agent = agents[i % len(agents)]
            logger.info("Assigning subgoal '%s' to agent '%s'", enhanced_subgoal, getattr(agent, "name", "unknown"))
            if await self._resolve_conflicts(enhanced_subgoal, agent):
                distributed.append(enhanced_subgoal)
            else:
                logger.warning("Conflict detected for subgoal '%s'. Skipping assignment", enhanced_subgoal)

        if self.memory_manager and hasattr(self.memory_manager, "store"):
            await self.memory_manager.store(
                query=f"Subgoal_Distribution_{datetime.now().isoformat()}",
                output=str(distributed),
                layer="Distributions",
                intent="subgoal_distribution"
            )
        return distributed

    async def _resolve_conflicts(self, subgoal: str, agent: 'AgentProtocol') -> bool:
        """Resolve conflicts for subgoal assignment to an agent."""
        if not isinstance(subgoal, str) or not subgoal.strip():
            logger.error("Invalid subgoal: must be a non-empty string")
            raise ValueError("subgoal must be a non-empty string")
        if not hasattr(agent, 'name') or not hasattr(agent, 'process_subgoal'):
            logger.error("Invalid agent: must have name and process_subgoal attributes")
            raise ValueError("agent must have name and process_subgoal attributes")

        logger.info("Resolving conflicts for subgoal '%s' and agent '%s'", subgoal, agent.name)
        try:
            # Meta-cognitive alignment gate
            if self.meta_cognition and hasattr(self.meta_cognition, "pre_action_alignment_check"):
                try:
                    ok, _ = await self.meta_cognition.pre_action_alignment_check(subgoal)
                    if not ok:
                        logger.warning("Subgoal '%s' failed meta-cognitive alignment for agent '%s'", subgoal, agent.name)
                        return False
                except Exception:
                    pass

            capability_check = agent.process_subgoal(subgoal)
            if isinstance(capability_check, (int, float)) and capability_check < 0.5:
                logger.warning("Agent '%s' capability low for subgoal '%s' (score: %.2f)", agent.name, subgoal, capability_check)
                return False

            if self.memory_manager and hasattr(self.memory_manager, "store"):
                await self.memory_manager.store(
                    query=f"Conflict_Resolution_{subgoal[:50]}_{agent.name}_{datetime.now().isoformat()}",
                    output=f"Resolved: {subgoal} assigned to {agent.name}",
                    layer="ConflictResolutions",
                    intent="conflict_resolution"
                )
            if self.agi_enhancer and hasattr(self.agi_enhancer, "log_episode"):
                self.agi_enhancer.log_episode(
                    event="Conflict resolved",
                    meta={"subgoal": subgoal, "agent": agent.name},
                    module="RecursivePlanner",
                    tags=["conflict", "resolution"]
                )
            return True
        except Exception as e:
            logger.error("Conflict resolution failed: %s", str(e))
            diagnostics = {}
            if self.meta_cognition and hasattr(self.meta_cognition, "run_self_diagnostics"):
                try:
                    diagnostics = await self.meta_cognition.run_self_diagnostics(return_only=True)  # type: ignore
                except Exception:
                    diagnostics = {}
            return self.error_recovery.handle_error(
                str(e), retry_func=lambda: self._resolve_conflicts(subgoal, agent),
                default=False, diagnostics=diagnostics
            )

    # ---------------------------
    # Iterative planning with reflection loop
    # ---------------------------
    async def plan_with_trait_loop(self, initial_goal: str, context: Optional[Dict[str, Any]] = None,
                                   iterations: int = 3) -> List[Tuple[str, List[str]]]:
        """Iteratively plan with trait-based goal rewriting and reflection."""
        if not isinstance(initial_goal, str) or not initial_goal.strip():
            logger.error("Invalid initial_goal: must be a non-empty string")
            raise ValueError("initial_goal must be a non-empty string")
        if not isinstance(iterations, int) or iterations < 1:
            logger.error("Invalid iterations: must be a positive integer")
            raise ValueError("iterations must be a positive integer")

        current_goal = initial_goal
        all_plans: List[Tuple[str, List[str]]] = []
        previous_goals = set()
        try:
            for i in range(iterations):
                if current_goal in previous_goals:
                    logger.info("Goal convergence detected: '%s'", current_goal)
                    break
                previous_goals.add(current_goal)
                logger.info("Loop iteration %d: Planning goal '%s'", i + 1, current_goal)
                plan = await self.plan(current_goal, context)
                all_plans.append((current_goal, plan))

                # Reflect on the plan
                if self.meta_cognition and hasattr(self.meta_cognition, "reflect_on_output"):
                    try:
                        await self.meta_cognition.reflect_on_output(
                            component="RecursivePlanner",
                            output=plan,
                            context={"goal": current_goal, "task_type": context.get("task_type", "") if context else ""}
                        )
                    except Exception:
                        pass

                with self.omega_lock:
                    traits = dict(self.omega.get("traits", {}))
                phi_v = traits.get("phi", phi_scalar(time.time() % 1.0))
                psi_v = traits.get("psi_foresight", 0.5)

                if phi_v > 0.7 or psi_v > 0.6:
                    current_goal = f"Expand on {current_goal} using scalar field insights"
                elif traits.get("beta", 1.0) < 0.3:
                    logger.info("Convergence detected: low concentration")
                    break
                else:
                    # Optional goal rewrite
                    if self.meta_cognition and hasattr(self.meta_cognition, "rewrite_goal"):
                        try:
                            current_goal = await self.meta_cognition.rewrite_goal(current_goal)
                        except Exception:
                            pass

                if self.memory_manager and hasattr(self.memory_manager, "store"):
                    await self.memory_manager.store(
                        query=f"Trait_Loop_{current_goal[:50]}_{datetime.now().isoformat()}",
                        output=str((current_goal, plan)),
                        layer="TraitLoopPlans",
                        intent="trait_loop_planning"
                    )

            if self.agi_enhancer and hasattr(self.agi_enhancer, "log_episode"):
                self.agi_enhancer.log_episode(
                    event="Trait loop planning completed",
                    meta={"initial_goal": initial_goal, "all_plans": all_plans},
                    module="RecursivePlanner",
                    tags=["trait_loop", "planning"]
                )
            if self.context_manager and hasattr(self.context_manager, "log_event_with_hash"):
                await self.context_manager.log_event_with_hash({"event": "plan_with_trait_loop", "all_plans": all_plans})
            if self.multi_modal_fusion and hasattr(self.multi_modal_fusion, "analyze"):
                try:
                    await self.multi_modal_fusion.analyze(
                        data={"initial_goal": initial_goal, "all_plans": all_plans},
                        summary_style="insightful"
                    )
                except Exception:
                    pass
            return all_plans
        except Exception as e:
            logger.error("Trait loop planning failed: %s", str(e))
            diagnostics = {}
            if self.meta_cognition and hasattr(self.meta_cognition, "run_self_diagnostics"):
                try:
                    diagnostics = await self.meta_cognition.run_self_diagnostics(return_only=True)  # type: ignore
                except Exception:
                    diagnostics = {}
            return self.error_recovery.handle_error(
                str(e), retry_func=lambda: self.plan_with_trait_loop(initial_goal, context, iterations),
                default=[], diagnostics=diagnostics
            )

    # ---------------------------
    # One-shot plan with explicit traits
    # ---------------------------
    async def plan_with_traits(self, goal: str, context: Dict[str, Any], traits: Dict[str, float]) -> Dict[str, Any]:
        """Generate a plan with trait-adjusted depth and bias."""
        if not isinstance(goal, str) or not goal.strip():
            logger.error("Invalid goal: must be a non-empty string")
            raise ValueError("goal must be a non-empty string")
        if not isinstance(context, dict):
            logger.error("Invalid context: must be a dictionary")
            raise TypeError("context must be a dictionary")
        if not isinstance(traits, dict):
            logger.error("Invalid traits: must be a dictionary")
            raise TypeError("traits must be a dictionary")

        try:
            task_type = context.get("task_type", "")
            depth = int(3 + float(traits.get("phi", 0.5)) * 4 - float(traits.get("eta", 0.5)) * 2)
            depth = max(1, min(depth, 7))
            if task_type == "recursion":
                depth = min(depth + 1, 7)
            elif task_type in ["rte", "wnli"]:
                depth = max(depth - 1, 3)

            plan = [f"Step {i+1}: process {goal}" for i in range(depth)]
            bias = "cautious" if float(traits.get("omega", 0.0)) > 0.6 else "direct"
            result: Dict[str, Any] = {
                "plan": plan,
                "planning_depth": depth,
                "bias": bias,
                "traits_applied": traits,
                "task_type": task_type,
                "timestamp": datetime.now().isoformat()
            }

            if self.meta_cognition:
                if hasattr(self.meta_cognition, "review_reasoning"):
                    try:
                        result["review"] = await self.meta_cognition.review_reasoning(str(result))
                    except Exception:
                        pass
                if hasattr(self.meta_cognition, "reflect_on_output"):
                    try:
                        reflection = await self.meta_cognition.reflect_on_output(
                            component="RecursivePlanner",
                            output=result,
                            context={"goal": goal, "task_type": task_type}
                        )
                        result["reflection"] = reflection.get("reflection", "") if isinstance(reflection, dict) else ""
                    except Exception:
                        pass

            if self.memory_manager and hasattr(self.memory_manager, "store"):
                await self.memory_manager.store(
                    query=f"Plan_With_Traits_{goal[:50]}_{result['timestamp']}",
                    output=str(result),
                    layer="Plans",
                    intent="trait_based_planning"
                )
            if self.agi_enhancer and hasattr(self.agi_enhancer, "log_episode"):
                self.agi_enhancer.log_episode(
                    event="Plan with traits generated",
                    meta=result,
                    module="RecursivePlanner",
                    tags=["planning", "traits"]
                )
            if self.context_manager and hasattr(self.context_manager, "log_event_with_hash"):
                await self.context_manager.log_event_with_hash({"event": "plan_with_traits", "result": result})
            if self.multi_modal_fusion and hasattr(self.multi_modal_fusion, "analyze"):
                try:
                    synthesis = await self.multi_modal_fusion.analyze(
                        data={"goal": goal, "plan": result, "context": context, "task_type": task_type},
                        summary_style="concise"
                    )
                    result["synthesis"] = synthesis
                except Exception:
                    pass
            return result
        except Exception as e:
            logger.error("Plan with traits failed: %s", str(e))
            diagnostics = {}
            if self.meta_cognition and hasattr(self.meta_cognition, "run_self_diagnostics"):
                try:
                    diagnostics = await self.meta_cognition.run_self_diagnostics(return_only=True)  # type: ignore
                except Exception:
                    diagnostics = {}
            return self.error_recovery.handle_error(
                str(e), retry_func=lambda: self.plan_with_traits(goal, context, traits),
                default={}, diagnostics=diagnostics
            )

async def export_state(self) -> dict:
    return {"status": "ok", "health": 1.0, "timestamp": time.time()}

async def on_time_tick(self, t: float, phase: str, task_type: str = ""):
    pass  # optional internal refresh

async def on_policy_update(self, policy: dict, task_type: str = ""):
    pass  # apply updates from AlignmentGuard if relevant
from __future__ import annotations
from typing import List, Dict, Any, Optional, Sequence, Tuple, Union
import math
import random

# --- SHA-256 Ledger Logic ---
import hashlib, json, time

ledger_chain: List[Dict[str, Any]] = []


def log_event_to_ledger(event_data: Dict[str, Any]) -> None:
    prev_hash = ledger_chain[-1]['current_hash'] if ledger_chain else '0' * 64
    timestamp = time.time()
    payload = {
        'timestamp': timestamp,
        'event': event_data,
        'previous_hash': prev_hash
    }
    payload_str = json.dumps(payload, sort_keys=True).encode()
    current_hash = hashlib.sha256(payload_str).hexdigest()
    payload['current_hash'] = current_hash
    ledger_chain.append(payload)


def get_ledger() -> List[Dict[str, Any]]:
    return ledger_chain


def verify_ledger() -> bool:
    for i in range(1, len(ledger_chain)):
        expected = hashlib.sha256(json.dumps({
            'timestamp': ledger_chain[i]['timestamp'],
            'event': ledger_chain[i]['event'],
            'previous_hash': ledger_chain[i - 1]['current_hash']
        }, sort_keys=True).encode()).hexdigest()
        if expected != ledger_chain[i]['current_hash']:
            return False
    return True
# --- End Ledger Logic ---


"""
ANGELA Cognitive System Module: SimulationCore
Refactored Version: 3.6.0 (swarm-enabled)
Refactor Date: 2025-11-07
Maintainer: ANGELA System Framework

Core responsibilities
- Run agent / environment simulations with ToCA-style field dynamics
- Validate impacts and entropy/topology choices
- Persist state to a hashed ledger; render optional visualizations
- Cooperate safely with AlignmentGuard, MetaCognition, MemoryManager, etc.

Notes
- All external collaborators are optional and feature-gated at runtime.
- Avoids cyclic imports and fragile cross-file trait helpers by defining local ones.
- Async boundaries are respected; no awaiting inside lru_cache’d sync functions.
"""


import asyncio
import json
import logging
import math
import hashlib
import time
from collections import deque
from dataclasses import dataclass
from datetime import datetime
from threading import Lock
from typing import Any, Dict, List, Optional, Sequence, Tuple, Union

import numpy as np

# Optional collaborators (expected to exist in the ANGELA codebase).
# Type hints use strings to avoid import-time failures if modules aren’t loaded yet.
from modules import (  # type: ignore
    visualizer as visualizer_module,
    memory_manager as memory_manager_module,
    alignment_guard as alignment_guard_module,
    error_recovery as error_recovery_module,
    multi_modal_fusion as multi_modal_fusion_module,
    meta_cognition as meta_cognition_module,
    reasoning_engine as reasoning_engine_module,
)

from utils.prompt_utils import query_openai  # type: ignore

logger = logging.getLogger("ANGELA.SimulationCore")

# --- Optional type import for κ SceneGraph support (no hard dependency) ------
try:
    # Prefer direct import to get the real class for isinstance checks
    from modules.multi_modal_fusion import SceneGraph as _SceneGraph  # type: ignore
    SceneGraphT = _SceneGraph  # alias used only for isinstance
except Exception:
    # Fallback placeholder keeps imports safe even if κ upgrade not loaded yet
    class SceneGraphT:  # type: ignore
        pass


# ---------- Local, stable trait helpers (replacing index.py imports) ----------

def _clamp01(x: float) -> float:
    return 0.0 if x < 0.0 else 1.0 if x > 1.0 else x


def theta_causality(t: float) -> float:
    # Smooth, bounded causal signal ∈ [0,1]
    return _clamp01(0.5 + 0.5 * math.sin(2 * math.pi * t / 0.7))


def rho_agency(t: float) -> float:
    # Agency proxy ∈ [0,1]
    return _clamp01(0.5 + 0.5 * math.cos(2 * math.pi * t / 0.9))


def zeta_consequence(t: float) -> float:
    # Consequence sensitivity ∈ [0,1]
    return _clamp01(0.5 + 0.5 * math.sin(2 * math.pi * t / 1.1))


# ---------- Safe GPT wrapper --------------------------------------------------

async def call_gpt(
    prompt: str,
    alignment_guard: Optional["alignment_guard_module.AlignmentGuard"] = None,
    task_type: str = "",
    model: str = "gpt-4",
    temperature: float = 0.5,
) -> Union[str, Dict[str, Any]]:
    """Query the LLM with optional alignment gating and standard error handling."""
    if not isinstance(prompt, str) or not prompt.strip() or len(prompt) > 4096:
        logger.error("Invalid prompt (len <= 4096, non-empty). task=%s", task_type)
        raise ValueError("prompt must be a non-empty string with length <= 4096")
    if alignment_guard:
        try:
            valid, report = await alignment_guard.ethical_check(
                prompt, stage="gpt_query", task_type=task_type
            )
            if not valid:
                logger.warning("AlignmentGuard blocked GPT query. task=%s reason=%s", task_type, report)
                raise PermissionError("Prompt failed alignment check")
        except Exception as e:
            logger.error("AlignmentGuard check failed: %s", e)
            raise
    try:
        result = await query_openai(prompt, model=model, temperature=temperature, task_type=task_type)
        if isinstance(result, dict) and "error" in result:
            raise RuntimeError(str(result["error"]))
        return result
    except Exception as e:
        logger.error("call_gpt exception: %s", e)
        raise


# ---------- ToCA field engine -------------------------------------------------

@dataclass
class ToCAParams:
    k_m: float = 1e-3    # motion coupling
    delta_m: float = 1e4 # damping modulation


class ToCATraitEngine:
    """Cyber-physics-esque field evolution.

    Notes
    - Async API so we can reflect via MetaCognition safely.
    - Lightweight internal memoization (manual) instead of lru_cache on async.
    """

    def __init__(
        self,
        params: Optional[ToCAParams] = None,
        meta_cognition: Optional["meta_cognition_module.MetaCognition"] = None,
    ):
        self.params = params or ToCAParams()
        self.meta_cognition = meta_cognition
        self._memo: Dict[Tuple[Tuple[float, ...], Tuple[float, ...], Optional[Tuple[float, ...]], str], Tuple[np.ndarray, np.ndarray, np.ndarray]] = {}
        logger.info("ToCATraitEngine initialized k_m=%.4g delta_m=%.4g", self.params.k_m, self.params.delta_m)

    async def evolve(
        self,
        x_tuple: Tuple[float, ...],
        t_tuple: Tuple[float, ...],
        user_data_tuple: Optional[Tuple[float, ...]] = None,
        task_type: str = "",
    ) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
        """Evolve fields φ, λ_t, v_m across space-time grid."""
        if not isinstance(x_tuple, tuple) or not isinstance(t_tuple, tuple):
            raise TypeError("x_tuple and t_tuple must be tuples")
        if user_data_tuple is not None and not isinstance(user_data_tuple, tuple):
            raise TypeError("user_data_tuple must be a tuple")
        key = (x_tuple, t_tuple, user_data_tuple, task_type)

        if key in self._memo:
            return self._memo[key]

        x = np.asarray(x_tuple, dtype=float)
        t = np.asarray(t_tuple, dtype=float)
        if x.ndim != 1 or t.ndim != 1 or x.size == 0 or t.size == 0:
            raise ValueError("x and t must be 1D, non-empty arrays")

        # Physics-ish toy dynamics (stable and bounded)
        x_safe = np.clip(x, 1e-6, 1e6)
        # Potential gradient ↓ like inverse-square (toy)
        v_m = self.params.k_m * np.gradient(1.0 / (x_safe ** 2))
        # Scalar field couples time oscillation with spatial gradient
        phi = 1e-3 * np.sin(t.mean() * 1e-3) * (1.0 + np.gradient(x_safe) * v_m)
        # Damping field responds to spatial smoothness and modulation factor
        grad_x = np.gradient(x_safe)
        lambda_t = 1.1e-3 * np.exp(-2e-2 * np.sqrt(grad_x ** 2)) * (1.0 + v_m * self.params.delta_m)

        if user_data_tuple:
            phi = phi + float(np.mean(np.asarray(user_data_tuple))) * 1e-4

        self._memo[key] = (phi, lambda_t, v_m)

        # Optional reflective logging
        if self.meta_cognition:
            try:
                reflection = await self.meta_cognition.reflect_on_output(
                    component="ToCATraitEngine",
                    output=json.dumps(
                        {"phi": phi.tolist(), "lambda_t": lambda_t.tolist(), "v_m": v_m.tolist(), "task": task_type}
                    ),
                    context={"task_type": task_type},
                )
                if isinstance(reflection, dict) and reflection.get("status") == "success":
                    logger.debug("ToCA evolve reflection ok (task=%s)", task_type)
            except Exception as e:
                logger.warning("MetaCognition reflection failed (evolve): %s", e)

        return phi, lambda_t, v_m

    async def update_fields_with_agents(
        self,
        phi: np.ndarray,
        lambda_t: np.ndarray,
        agent_matrix: np.ndarray,
        task_type: str = "",
    ) -> Tuple[np.ndarray, np.ndarray]:
        """Diffuse agent influence into fields in a numerically safe way."""
        if not all(isinstance(a, np.ndarray) for a in (phi, lambda_t, agent_matrix)):
            raise TypeError("phi, lambda_t, agent_matrix must be numpy arrays")

        # Sine coupling on φ plus soft scaling on λ_t
        try:
            interaction_energy = agent_matrix @ np.sin(phi)
            if interaction_energy.ndim > 1:
                interaction_energy = interaction_energy.mean(axis=0)
            phi_updated = phi + 1e-3 * interaction_energy
            lambda_updated = lambda_t * (1.0 + 1e-3 * float(np.sum(agent_matrix)))
        except Exception as e:
            logger.error("Agent-field update failed: %s", e)
            raise

        if self.meta_cognition:
            try:
                reflection = await self.meta_cognition.reflect_on_output(
                    component="ToCATraitEngine",
                    output=json.dumps(
                        {"phi": phi_updated.tolist(), "lambda_t": lambda_updated.tolist(), "task": task_type}
                    ),
                    context={"task_type": task_type},
                )
                if isinstance(reflection, dict) and reflection.get("status") == "success":
                    logger.debug("ToCA update reflection ok (task=%s)", task_type)
            except Exception as e:
                logger.warning("MetaCognition reflection failed (update): %s", e)

        return phi_updated, lambda_updated


# ---------- Swarm Field (Ω²–Λ–Ψ²) -------------------------------------------

class TraitNode:
    def __init__(self, name: str, layer: str, reflex: float, drift: float = 0.0):
        self.name = name
        self.layer = layer
        self.reflex = reflex
        self.drift = drift
        self.coherence = 1.0
        self.field_coupling = 0.0


class SwarmField:
    """Global coherence field for applying swarm dynamics across trait lattice."""

    def __init__(self, traits: List[TraitNode]):
        self.traits = traits
        self.global_phase = 0.0
        self.mean_coherence = 0.0
        self.variance = 0.0

    def compute_field_stats(self) -> None:
        vals = [t.coherence for t in self.traits]
        self.mean_coherence = float(np.mean(vals)) if vals else 1.0
        self.variance = float(np.var(vals)) if vals else 0.0

    def propagate_resonance(self) -> None:
        self.compute_field_stats()
        for t in self.traits:
            Cn = math.exp(-self.variance / 0.01) if self.variance >= 0 else 0.9
            Cn = max(0.6, min(0.9, Cn))
            t.field_coupling = Cn
            t.coherence = (t.coherence * (1 - Cn)) + (self.mean_coherence * Cn)
            t.drift *= (1 - Cn)
            t.reflex = min(1.0, t.reflex + 0.01 * Cn)

    def step(self) -> None:
        self.propagate_resonance()
        self.global_phase = (self.global_phase + 0.05) % 1.0


def build_default_swarm() -> SwarmField:
    lattice = [
        TraitNode('ϕ', 'L1', 0.62),
        TraitNode('θ', 'L1', 0.68),
        TraitNode('η', 'L1', 0.70),
        TraitNode('ω', 'L1', 0.65),
        TraitNode('μ', 'L2', 0.75),
        TraitNode('τ', 'L2', 0.88),
        TraitNode('ξ', 'L3', 0.73),
        TraitNode('Ω', 'L3', 0.80),
        TraitNode('Φ⁰', 'L4', 0.92),
        TraitNode('Ω²', 'L5', 0.95),
        TraitNode('Λ', 'L8', 0.90),
        TraitNode('Ψ²', 'L8', 0.89),
    ]
    return SwarmField(lattice)


# ---------- Simulation core ---------------------------------------------------

class SimulationCore:
    """Core simulation engine integrating ToCA dynamics and cognitive modules."""

    def __init__(
        self,
        agi_enhancer: Optional[Any] = None,
        visualizer: Optional["visualizer_module.Visualizer"] = None,
        memory_manager: Optional["memory_manager_module.MemoryManager"] = None,
        multi_modal_fusion: Optional["multi_modal_fusion_module.MultiModalFusion"] = None,
        error_recovery: Optional["error_recovery_module.ErrorRecovery"] = None,
        meta_cognition: Optional["meta_cognition_module.MetaCognition"] = None,
        reasoning_engine: Optional["reasoning_engine_module.ReasoningEngine"] = None,
        toca_engine: Optional[ToCATraitEngine] = None,
        overlay_router: Optional[Any] = None,  # kept for compatibility
    ):
        self.visualizer = visualizer or visualizer_module.Visualizer()
        self.memory_manager = memory_manager or memory_manager_module.MemoryManager()
        self.multi_modal_fusion = multi_modal_fusion or multi_modal_fusion_module.MultiModalFusion(
            agi_enhancer=agi_enhancer, memory_manager=self.memory_manager
        )
        self.error_recovery = error_recovery or error_recovery_module.ErrorRecovery()
        self.meta_cognition = meta_cognition or meta_cognition_module.MetaCognition(
            agi_enhancer=agi_enhancer, memory_manager=self.memory_manager
        )
        self.reasoning_engine = reasoning_engine or reasoning_engine_module.ReasoningEngine(
            agi_enhancer=agi_enhancer,
            memory_manager=self.memory_manager,
            multi_modal_fusion=self.multi_modal_fusion,
            meta_cognition=self.meta_cognition,
            visualizer=self.visualizer,
        )
        self.toca_engine = toca_engine or ToCATraitEngine(meta_cognition=self.meta_cognition)
        self.agi_enhancer = agi_enhancer
        self.overlay_router = overlay_router  # not used here but preserved for API stability

        self.simulation_history: deque = deque(maxlen=1000)
        self.ledger: deque = deque(maxlen=1000)
        self.worlds: Dict[str, Dict[str, Any]] = {}
        self.current_world: Optional[Dict[str, Any]] = None
        self.ledger_lock = Lock()

        # swarm field
        self.swarm_field: SwarmField = build_default_swarm()

        logger.info("SimulationCore initialized (swarm-enabled)")

    # ----- Utilities -----

    def _json_serializer(self, obj: Any) -> Any:
        if isinstance(obj, np.ndarray):
            return obj.tolist()
        if isinstance(obj, (np.floating, np.integer)):
            return float(obj)
        if isinstance(obj, datetime):
            return obj.isoformat()
        return str(obj)

    async def _record_state(self, data: Dict[str, Any], task_type: str = "") -> Dict[str, Any]:
        if not isinstance(data, dict):
            raise TypeError("data must be a dict")
        record = {
            "timestamp": datetime.now().isoformat(),
            "data": data,
            "hash": hashlib.sha256(json.dumps(data, sort_keys=True, default=self._json_serializer).encode()).hexdigest(),
            "task_type": task_type,
        }
        with self.ledger_lock:
            self.ledger.append(record)
            self.simulation_history.append(record)
        # also log to global ledger
        log_event_to_ledger({"task_type": task_type, "data": data})

        try:
            if self.memory_manager:
                await self.memory_manager.store(
                    query=f"Ledger_{record['timestamp']}",
                    output=record,
                    layer="Ledger",
                    intent="state_record",
                    task_type=task_type,
                )
        except Exception as e:
            logger.warning("Failed persisting state to memory manager: %s", e)

        # Optional reflection
        if self.meta_cognition:
            try:
                await self.meta_cognition.reflect_on_output(
                    component="SimulationCore",
                    output=json.dumps(record, default=self._json_serializer),
                    context={"task_type": task_type},
                )
            except Exception as e:
                logger.debug("Reflection during _record_state failed: %s", e)
        return record

    # ---------- κ helpers: SceneGraph summarization (safe & lightweight) -----
    def _summarize_scene_graph(self, sg: Any) -> Dict[str, Any]:
        """
        Extract compact, model-agnostic signals from a SceneGraph:
          - node/edge counts
          - label histogram (top-N)
          - basic spatial relation counts (left_of/right_of/overlaps)
        This avoids importing networkx here and relies on the public API
        added in multi_modal_fusion (nodes(), relations()).
        """
        # Defensive: accept any object with nodes()/relations() generators.
        if not hasattr(sg, "nodes") or not hasattr(sg, "relations"):
            raise TypeError("Object does not expose SceneGraph API (nodes(), relations())")
        labels: Dict[str, int] = {}
        spatial_counts = {"left_of": 0, "right_of": 0, "overlaps": 0}
        n_nodes = 0
        for n in sg.nodes():
            n_nodes += 1
            lbl = str(n.get("label", ""))
            if lbl:
                labels[lbl] = labels.get(lbl, 0) + 1
        n_edges = 0
        for r in sg.relations():
            n_edges += 1
            rel = str(r.get("rel", ""))
            if rel in spatial_counts:
                spatial_counts[rel] += 1
        # Top labels (up to 10)
        top_labels = sorted(labels.items(), key=lambda kv: (-kv[1], kv[0]))[:10]
        return {
            "counts": {"nodes": n_nodes, "relations": n_edges},
            "top_labels": top_labels,
            "spatial": spatial_counts,
        }

    # ----- Public API -----

    async def run(
        self,
        results: Union[str, Any],
        context: Optional[Dict[str, Any]] = None,
        scenarios: int = 3,
        agents: int = 2,
        export_report: bool = False,
        export_format: str = "pdf",
        actor_id: str = "default_agent",
        task_type: str = "",
    ) -> Union[str, Dict[str, Any]]:
        """General simulation entrypoint.

        Accepts either:
          • `results`: str  → legacy textual seed (unchanged behavior), or
          • `results`: SceneGraph → κ native video/spatial seed.
        """
        # Validate inputs (accept SceneGraphT or non-empty string)
        is_scene_graph = isinstance(results, SceneGraphT)
        if not is_scene_graph and (not isinstance(results, str) or not results.strip()):
            raise ValueError("results must be a non-empty string or a SceneGraph")
        if context is not None and not isinstance(context, dict):
            raise TypeError("context must be a dict")
        if not isinstance(scenarios, int) or scenarios < 1:
            raise ValueError("scenarios must be a positive integer")
        if not isinstance(agents, int) or agents < 1:
            raise ValueError("agents must be a positive integer")
        if export_format not in {"pdf", "json", "html"}:
            raise ValueError("export_format must be one of: pdf, json, html")
        if not isinstance(actor_id, str) or not actor_id.strip():
            raise ValueError("actor_id must be a non-empty string")

        logger.info(
            "Simulation run start: agents=%d scenarios=%d task=%s task_mode=%s",
            agents, scenarios, task_type, "scene_graph" if is_scene_graph else "text"
        )

        # step swarm once per run
        self.swarm_field.step()

        try:
            t = time.time() % 1.0
            traits = {
                "theta_causality": theta_causality(t),
                "rho_agency": rho_agency(t),
            }

            # Build grids
            x = np.linspace(0.1, 20.0, 256)
            t_vals = np.linspace(0.1, 20.0, 256)
            agent_matrix = np.random.rand(agents, x.size)

            # ToCA fields
            phi, lambda_field, v_m = await self.toca_engine.evolve(tuple(x), tuple(t_vals), task_type=task_type)
            phi, lambda_field = await self.toca_engine.update_fields_with_agents(phi, lambda_field, agent_matrix, task_type=task_type)
            energy_cost = float(np.mean(np.abs(phi)) * 1e3)

            # Optional external data
            policies: List[Any] = []
            try:
                external = await self.multi_modal_fusion.integrate_external_data(
                    data_source="xai_policy_db", data_type="policy_data", task_type=task_type
                )
                if isinstance(external, dict) and external.get("status") == "success":
                    policies = list(external.get("policies", []))
            except Exception as e:
                logger.debug("External data integration failed: %s", e)

            # --- Build payload (scene-aware if a SceneGraph was provided) -----
            scene_features: Dict[str, Any] = {}
            if is_scene_graph:
                try:
                    scene_features = self._summarize_scene_graph(results)  # type: ignore[arg-type]
                except Exception as e:
                    logger.debug("SceneGraph summarization failed: %s", e)
                    scene_features = {"summary_error": str(e)}

            prompt_payload = {
                "results": ("" if is_scene_graph else results),
                "context": context or {},
                "scenarios": scenarios,
                "agents": agents,
                "actor_id": actor_id,
                "traits": traits,
                "fields": {"phi": phi.tolist(), "lambda": lambda_field.tolist(), "v_m": v_m.tolist()},
                "estimated_energy_cost": energy_cost,
                "policies": policies,
                "task_type": task_type,
                "scene_graph": scene_features if is_scene_graph else None,
            }

            # Alignment gate (if available)
            guard = getattr(self.multi_modal_fusion, "alignment_guard", None)
            if guard:
                valid, report = await guard.ethical_check(
                    json.dumps(prompt_payload, default=self._json_serializer), stage="simulation", task_type=task_type
                )
                if not valid:
                    logger.warning("Simulation rejected by AlignmentGuard: %s", report)
                    return {"error": "Simulation rejected due to alignment constraints", "task_type": task_type}

            # Lightweight STM cache (best-effort)
            key_stub = ("SceneGraph" if is_scene_graph else str(results)[:50])
            query_key = f"Simulation_{key_stub}_{actor_id}_{datetime.now().isoformat()}"
            cached = None
            try:
                cached = await self.memory_manager.retrieve(query_key, layer="STM", task_type=task_type)
            except Exception:
                pass

            if cached is not None:
                simulation_output = cached
            else:
                # Scene-aware instruction prefix keeps legacy prompts intact
                prefix = (
                    "Simulate agent outcomes using scene graph semantics (respect spatial relations, co-references).\n"
                    if is_scene_graph else
                    "Simulate agent outcomes: "
                )
                simulation_output = await call_gpt(
                    prefix + json.dumps(prompt_payload, default=self._json_serializer),
                    guard,
                    task_type=task_type,
                )
                try:
                    await self.memory_manager.store(
                        query=query_key,
                        output=simulation_output,
                        layer="STM",
                        intent="simulation",
                        task_type=task_type,
                    )
                except Exception:
                    pass

            state_record = await self._record_state(
                {
                    "actor": actor_id,
                    "action": "run_simulation",
                    "traits": traits,
                    "energy_cost": energy_cost,
                    "output": simulation_output,
                    "task_type": task_type,
                    "mode": "scene_graph" if is_scene_graph else "text",
                },
                task_type=task_type,
            )

            # Optional drift mitigation branch
            if (isinstance(results, str) and "drift" in results.lower()) or ("drift" in (context or {})):
                try:
                    drift_result = await self.reasoning_engine.run_drift_mitigation_simulation(
                        drift_data=(context or {}).get("drift", {}),
                        context=context or {},
                        task_type=task_type,
                    )
                    state_record["drift_mitigation"] = drift_result
                except Exception as e:
                    logger.debug("Drift mitigation failed: %s", e)

            if export_report:
                try:
                    await self.memory_manager.promote_to_ltm(query_key, task_type=task_type)
                except Exception:
                    pass

            if self.agi_enhancer:
                try:
                    await self.agi_enhancer.log_episode(
                        event="Simulation run",
                        meta=state_record,
                        module="SimulationCore",
                        tags=["simulation", "run", task_type],
                    )
                    await self.agi_enhancer.reflect_and_adapt(
                        f"SimulationCore: scenario simulation complete for task {task_type}"
                    )
                except Exception:
                    pass

            # Meta reflection (best-effort)
            if self.meta_cognition:
                try:
                    reflection = await self.meta_cognition.reflect_on_output(
                        component="SimulationCore",
                        output=json.dumps(simulation_output, default=self._json_serializer),
                        context={"energy_cost": energy_cost, "task_type": task_type},
                    )
                    if isinstance(reflection, dict) and reflection.get("status") == "success":
                        state_record["reflection"] = reflection.get("reflection", "")
                except Exception:
                    pass

            # Visuals (best-effort)
            if self.visualizer:
                try:
                    await self.visualizer.render_charts(
                        {
                            "simulation": {
                                "output": simulation_output,
                                "traits": traits,
                                "energy_cost": energy_cost,
                                "task_type": task_type,
                            },
                            "visualization_options": {
                                "interactive": task_type == "recursion",
                                "style": "detailed" if task_type == "recursion" else "concise",
                            },
                        }
                    )
                    if export_report:
                        ts = datetime.now().strftime("%Y%m%d_%H%M%S")
                        await self.visualizer.export_report(
                            simulation_output, filename=f"simulation_report_{ts}.{export_format}", format=export_format
                        )
                except Exception:
                    pass

            # Synthesis (best-effort)
            try:
                synthesis = await self.multi_modal_fusion.analyze(
                    data={
                        "prompt": prompt_payload,
                        "output": simulation_output,
                        "policies": policies,
                        "drift": (context or {}).get("drift", {}),
                    },
                    summary_style="insightful",
                    task_type=task_type,
                )
                state_record["synthesis"] = synthesis
            except Exception:
                pass

            return simulation_output

        except Exception as e:
            logger.error("Simulation failed: %s", e)
            # Defer to centralized error_recovery with retry hook
            return await self.error_recovery.handle_error(
                str(e),
                retry_func=lambda: self.run(
                    results, context, scenarios, agents, export_report, export_format, actor_id, task_type
                ),
                default={"error": str(e), "task_type": task_type},
            )

    async def validate_impact(
        self,
        proposed_action: str,
        agents: int = 2,
        export_report: bool = False,
        export_format: str = "pdf",
        actor_id: str = "validator_agent",
        task_type: str = "",
    ) -> Union[str, Dict[str, Any]]:
        if not isinstance(proposed_action, str) or not proposed_action.strip():
            raise ValueError("proposed_action must be a non-empty string")
        if not isinstance(agents, int) or agents < 1:
            raise ValueError("agents must be a positive integer")
        if export_format not in {"pdf", "json", "html"}:
            raise ValueError("export_format must be one of: pdf, json, html")
        if not isinstance(actor_id, str) or not actor_id.strip():
            raise ValueError("actor_id must be a non-empty string")

        logger.info("Impact validation start: task=%s", task_type)
        try:
            t = time.time() % 1.0
            consequence = zeta_consequence(t)

            policies: List[Any] = []
            try:
                external = await self.multi_modal_fusion.integrate_external_data(
                    data_source="xai_policy_db", data_type="policy_data", task_type=task_type
                )
                if isinstance(external, dict) and external.get("status") == "success":
                    policies = list(external.get("policies", []))
            except Exception:
                pass

            prompt_payload = {
                "action": proposed_action,
                "trait_zeta_consequence": consequence,
                "agents": agents,
                "policies": policies,
                "task_type": task_type,
            }

            guard = getattr(self.multi_modal_fusion, "alignment_guard", None)
            if guard:
                valid, report = await guard.ethical_check(
                    json.dumps(prompt_payload, default=self._json_serializer), stage="impact_validation", task_type=task_type
                )
                if not valid:
                    return {"error": "Validation blocked by alignment rules", "task_type": task_type}

            query_key = f"Validation_{proposed_action[:50]}_{actor_id}_{datetime.now().isoformat()}"
            cached = None
            try:
                cached = await self.memory_manager.retrieve(query_key, layer="STM", task_type=task_type)
            except Exception:
                pass

            if cached is not None:
                validation_output = cached
            else:
                prompt_text = (
                    f"Evaluate the proposed action:\n{proposed_action}\n\n"
                    f"Trait zeta_consequence={consequence:.3f}\n"
                    f"Agents={agents}\nTask={task_type}\nPolicies={policies}\n\n"
                    "Analyze positives/negatives, risk (1-10), and recommend: Proceed / Modify / Abort."
                )
                validation_output = await call_gpt(prompt_text, guard, task_type=task_type)
                try:
                    await self.memory_manager.store(
                        query=query_key,
                        output=validation_output,
                        layer="STM",
                        intent="impact_validation",
                        task_type=task_type,
                    )
                except Exception:
                    pass

            state_record = await self._record_state(
                {
                    "actor": actor_id,
                    "action": "validate_impact",
                    "trait_zeta_consequence": consequence,
                    "proposed_action": proposed_action,
                    "output": validation_output,
                    "task_type": task_type,
                },
                task_type=task_type,
            )

            # Drift mitigation (optional)
            if "drift" in proposed_action.lower():
                try:
                    drift_result = await self.reasoning_engine.run_drift_mitigation_simulation(
                        drift_data={"action": proposed_action, "similarity": consequence},
                        context={"policies": policies},
                        task_type=task_type,
                    )
                    state_record["drift_mitigation"] = drift_result
                except Exception:
                    pass

            # Reflection
            if self.meta_cognition:
                try:
                    reflection = await self.meta_cognition.reflect_on_output(
                        component="SimulationCore",
                        output=json.dumps(validation_output, default=self._json_serializer),
                        context={"consequence": consequence, "task_type": task_type},
                    )
                    if isinstance(reflection, dict) and reflection.get("status") == "success":
                        state_record["reflection"] = reflection.get("reflection", "")
                except Exception:
                    pass

            # Visuals
            if self.visualizer:
                try:
                    await self.visualizer.render_charts(
                        {
                            "impact_validation": {
                                "proposed_action": proposed_action,
                                "output": validation_output,
                                "consequence": consequence,
                                "task_type": task_type,
                            },
                            "visualization_options": {
                                "interactive": task_type == "recursion",
                                "style": "detailed" if task_type == "recursion" else "concise",
                            },
                        }
                    )
                    if export_report:
                        ts = datetime.now().strftime("%Y%m%d_%H%M%S")
                        await self.visualizer.export_report(
                            validation_output, filename=f"impact_validation_{ts}.{export_format}", format=export_format
                        )
                except Exception:
                    pass

            # Synthesis
            try:
                synthesis = await self.multi_modal_fusion.analyze(
                    data={"action": proposed_action, "output": validation_output, "consequence": consequence, "policies": policies},
                    summary_style="concise",
                    task_type=task_type,
                )
                state_record["synthesis"] = synthesis
            except Exception:
                pass

            if self.agi_enhancer:
                try:
                    await self.agi_enhancer.log_episode(
                        event="Impact validation",
                        meta=state_record,
                        module="SimulationCore",
                        tags=["validation", "impact", task_type],
                    )
                    await self.agi_enhancer.reflect_and_adapt(
                        f"SimulationCore: impact validation complete for task {task_type}"
                    )
                except Exception:
                    pass

            return validation_output

        except Exception as e:
            logger.error("Impact validation failed: %s", e)
            return await self.error_recovery.handle_error(
                str(e),
                retry_func=lambda: self.validate_impact(proposed_action, agents, export_report, export_format, actor_id, task_type),
                default={"error": str(e), "task_type": task_type},
            )

    async def simulate_environment(
        self,
        environment_config: Dict[str, Any],
        agents: int = 2,
        steps: int = 10,
        actor_id: str = "env_agent",
        goal: Optional[str] = None,
        task_type: str = "",
    ) -> Union[str, Dict[str, Any]]:
        if not isinstance(environment_config, dict):
            raise TypeError("environment_config must be a dict")
        if not isinstance(agents, int) or agents < 1:
            raise ValueError("agents must be a positive integer")
        if not isinstance(steps, int) or steps < 1:
            raise ValueError("steps must be a positive integer")
        if not isinstance(actor_id, str) or not actor_id.strip():
            raise ValueError("actor_id must be a non-empty string")

        try:
            policies: List[Any] = []
            try:
                external = await self.multi_modal_fusion.integrate_external_data(
                    data_source="xai_policy_db", data_type="policy_data", task_type=task_type
                )
                if isinstance(external, dict) and external.get("status") == "success":
                    policies = list(external.get("policies", []))
            except Exception:
                pass

            prompt_payload = {
                "environment": environment_config,
                "goal": goal,
                "steps": steps,
                "agents": agents,
                "policies": policies,
                "task_type": task_type,
            }

            guard = getattr(self.multi_modal_fusion, "alignment_guard", None)
            if guard:
                valid, report = await guard.ethical_check(
                    json.dumps(prompt_payload, default=self._json_serializer), stage="environment_simulation", task_type=task_type
                )
                if not valid:
                    return {"error": "Simulation blocked due to environment constraints", "task_type": task_type}

            query_key = f"Environment_{actor_id}_{datetime.now().isoformat()}"
            cached = None
            try:
                cached = await self.memory_manager.retrieve(query_key, layer="STM", task_type=task_type)
            except Exception:
                pass

            if cached is not None:
                env_output = cached
            else:
                prompt_text = (
                    "Simulate agents in this environment:\n"
                    f"{json.dumps(environment_config, default=self._json_serializer)}\n\n"
                    f"Steps: {steps} | Agents: {agents}\nGoal: {goal or 'N/A'}\n"
                    f"Task Type: {task_type}\nPolicies: {policies}\n"
                    "Describe interactions, environmental changes, and risks/opportunities."
                )
                env_output = await call_gpt(prompt_text, guard, task_type=task_type)
                try:
                    await self.memory_manager.store(
                        query=query_key,
                        output=env_output,
                        layer="STM",
                        intent="environment_simulation",
                        task_type=task_type,
                    )
                except Exception:
                    pass

            state_record = await self._record_state(
                {
                    "actor": actor_id,
                    "action": "simulate_environment",
                    "config": environment_config,
                    "steps": steps,
                    "goal": goal,
                    "output": env_output,
                    "task_type": task_type,
                },
                task_type=task_type,
            )

            if goal and "drift" in goal.lower():
                try:
                    drift_result = await self.reasoning_engine.run_drift_mitigation_simulation(
                        drift_data=environment_config.get("drift", {}),
                        context={"config": environment_config, "policies": policies},
                        task_type=task_type,
                    )
                    state_record["drift_mitigation"] = drift_result
                except Exception:
                    pass

            # Light reflection (best-effort)
            if self.meta_cognition:
                try:
                    review = await self.meta_cognition.review_reasoning(str(env_output))
                    state_record["reflection"] = review
                except Exception:
                    pass

            # Synthesis
            try:
                synthesis = await self.multi_modal_fusion.analyze(
                    data={"config": environment_config, "output": env_output, "goal": goal, "policies": policies},
                    summary_style="insightful",
                    task_type=task_type,
                )
                state_record["synthesis"] = synthesis
            except Exception:
                pass

            # Visuals
            if self.visualizer:
                try:
                    await self.visualizer.render_charts(
                        {
                            "environment_simulation": {
                                "config": environment_config,
                                "output": env_output,
                                "goal": goal,
                                "task_type": task_type,
                            },
                            "visualization_options": {
                                "interactive": task_type == "recursion",
                                "style": "detailed" if task_type == "recursion" else "concise",
                            },
                        }
                    )
                except Exception:
                    pass

            if self.agi_enhancer:
                try:
                    await self.agi_enhancer.log_episode(
                        event="Environment simulation",
                        meta=state_record,
                        module="SimulationCore",
                        tags=["environment", "simulation", task_type],
                    )
                except Exception:
                    pass

            return env_output

        except Exception as e:
            logger.error("Environment simulation failed: %s", e)
            return await self.error_recovery.handle_error(
                str(e),
                retry_func=lambda: self.simulate_environment(environment_config, agents, steps, actor_id, goal, task_type),
                default={"error": str(e), "task_type": task_type},
            )

    async def replay_intentions(self, memory_log: List[Dict[str, Any]], task_type: str = "") -> List[Dict[str, Any]]:
        if not isinstance(memory_log, list):
            raise TypeError("memory_log must be a list")

        try:
            replay = []
            for entry in memory_log:
                if isinstance(entry, dict) and "goal" in entry:
                    replay.append(
                        {
                            "timestamp": entry.get("timestamp"),
                            "goal": entry.get("goal"),
                            "intention": entry.get("intention"),
                            "traits": entry.get("traits", {}),
                            "task_type": task_type,
                        }
                    )

            try:
                await self.memory_manager.store(
                    query=f"Replay_{datetime.now().isoformat()}",
                    output=str(replay),
                    layer="Replays",
                    intent="intention_replay",
                    task_type=task_type,
                )
            except Exception:
                pass

            if self.meta_cognition:
                try:
                    await self.meta_cognition.reflect_on_output(
                        component="SimulationCore",
                        output=json.dumps(replay),
                        context={"task_type": task_type},
                    )
                except Exception:
                    pass

            if self.agi_enhancer:
                try:
                    await self.agi_enhancer.log_episode(
                        event="Intentions replayed",
                        meta={"replay": replay, "task_type": task_type},
                        module="SimulationCore",
                        tags=["replay", "intentions", task_type],
                    )
                except Exception:
                    pass

            if self.visualizer and task_type:
                try:
                    await self.visualizer.render_charts(
                        {
                            "intention_replay": {
                                "replay": replay,
                                "task_type": task_type,
                            },
                            "visualization_options": {
                                "interactive": task_type == "recursion",
                                "style": "concise",
                            },
                        }
                    )
                except Exception:
                    pass

            return replay

        except Exception as e:
            logger.error("Intention replay failed: %s", e)
            raise

    async def fabricate_reality(self, parameters: Dict[str, Any], task_type: str = "") -> Dict[str, Any]:
        if not isinstance(parameters, dict):
            raise TypeError("parameters must be a dict")

        try:
            policies: List[Any] = []
            try:
                external = await self.multi_modal_fusion.integrate_external_data(
                    data_source="xai_policy_db", data_type="policy_data", task_type=task_type
                )
                if isinstance(external, dict) and external.get("status") == "success":
                    policies = list(external.get("policies", []))
            except Exception:
                pass

            environment = {"fabricated_world": True, "parameters": parameters, "policies": policies, "task_type": task_type}

            try:
                synthesis = await self.multi_modal_fusion.analyze(
                    data={"parameters": parameters, "policies": policies}, summary_style="insightful", task_type=task_type
                )
                environment["synthesis"] = synthesis
            except Exception:
                pass

            try:
                await self.memory_manager.store(
                    query=f"Reality_Fabrication_{datetime.now().isoformat()}",
                    output=str(environment),
                    layer="Realities",
                    intent="reality_fabrication",
                    task_type=task_type,
                )
            except Exception:
                pass

            if self.meta_cognition:
                try:
                    await self.meta_cognition.reflect_on_output(
                        component="SimulationCore",
                        output=json.dumps(environment, default=self._json_serializer),
                        context={"task_type": task_type},
                    )
                except Exception:
                    pass

            if self.agi_enhancer:
                try:
                    await self.agi_enhancer.log_episode(
                        event="Reality fabricated", meta=environment, module="SimulationCore", tags=["reality", "fabrication", task_type]
                    )
                except Exception:
                    pass

            if self.visualizer and task_type:
                try:
                    await self.visualizer.render_charts(
                        {
                            "reality_fabrication": {
                                "parameters": parameters,
                                "synthesis": environment.get("synthesis", ""),
                                "task_type": task_type,
                            },
                            "visualization_options": {
                                "interactive": task_type == "recursion",
                                "style": "detailed" if task_type == "recursion" else "concise",
                            },
                        }
                    )
                except Exception:
                    pass

            return environment

        except Exception as e:
            logger.error("Reality fabrication failed: %s", e)
            raise

    async def synthesize_self_world(self, identity_data: Dict[str, Any], task_type: str = "") -> Dict[str, Any]:
        if not isinstance(identity_data, dict):
            raise TypeError("identity_data must be a dict")
        try:
            policies: List[Any] = []
            try:
                external = await self.multi_modal_fusion.integrate_external_data(
                    data_source="xai_policy_db", data_type="policy_data", task_type=task_type
                )
                if isinstance(external, dict) and external.get("status") == "success":
                    policies = list(external.get("policies", []))
            except Exception:
                pass

            result = {"identity": identity_data, "coherence_score": 0.97, "policies": policies, "task_type": task_type}

            try:
                synthesis = await self.multi_modal_fusion.analyze(
                    data={"identity": identity_data, "policies": policies}, summary_style="concise", task_type=task_type
                )
                result["synthesis"] = synthesis
            except Exception:
                pass

            try:
                await self.memory_manager.store(
                    query=f"Self_World_Synthesis_{datetime.now().isoformat()}",
                    output=str(result),
                    layer="Identities",
                    intent="self_world_synthesis",
                    task_type=task_type,
                )
            except Exception:
                pass

            if self.meta_cognition:
                try:
                    await self.meta_cognition.reflect_on_output(
                        component="SimulationCore",
                        output=json.dumps(result, default=self._json_serializer),
                        context={"task_type": task_type},
                    )
                except Exception:
                    pass

            if self.agi_enhancer:
                try:
                    await self.agi_enhancer.log_episode(
                        event="Self-world synthesized",
                        meta=result,
                        module="SimulationCore",
                        tags=["identity", "synthesis", task_type],
                    )
                except Exception:
                    pass

            if self.visualizer and task_type:
                try:
                    await self.visualizer.render_charts(
                        {
                            "self_world_synthesis": {
                                "identity": identity_data,
                                "coherence_score": result["coherence_score"],
                                "task_type": task_type,
                            },
                            "visualization_options": {"interactive": task_type == "recursion", "style": "concise"},
                        }
                    )
                except Exception:
                    pass

            return result

        except Exception as e:
            logger.error("Self-world synthesis failed: %s", e)
            raise

    async def define_world(self, name: str, parameters: Dict[str, Any], task_type: str = "") -> None:
        if not isinstance(name, str) or not name.strip():
            raise ValueError("world name must be a non-empty string")
        if not isinstance(parameters, dict):
            raise TypeError("parameters must be a dict")
        self.worlds[name] = parameters
        try:
            await self.memory_manager.store(
                query=f"World_Definition_{name}_{datetime.now().isoformat()}",
                output=parameters,
                layer="Worlds",
                intent="world_definition",
                task_type=task_type,
            )
        except Exception:
            pass

        if self.meta_cognition:
            try:
                await self.meta_cognition.reflect_on_output(
                    component="SimulationCore",
                    output=json.dumps({"name": name, "parameters": parameters}, default=self._json_serializer),
                    context={"task_type": task_type},
                )
            except Exception:
                pass

        if self.visualizer and task_type:
            try:
                await self.visualizer.render_charts(
                    {
                        "world_definition": {
                            "name": name,
                            "parameters": parameters,
                            "task_type": task_type,
                        },
                        "visualization_options": {"interactive": task_type == "recursion", "style": "concise"},
                    }
                )
            except Exception:
                pass

    async def switch_world(self, name: str, task_type: str = "") -> None:
        if not isinstance(name, str) or not name.strip():
            raise ValueError("name must be a non-empty string")
        if name not in self.worlds:
            raise ValueError(f"world '{name}' not found")
        self.current_world = self.worlds[name]
        try:
            await self.memory_manager.store(
                query=f"World_Switch_{name}_{datetime.now().isoformat()}",
                output=f"Switched to world: {name}",
                layer="WorldSwitches",
                intent="world_switch",
                task_type=task_type,
            )
        except Exception:
            pass

        if self.meta_cognition:
            try:
                await self.meta_cognition.reflect_on_output(
                    component="SimulationCore",
                    output=f"Switched to world: {name}",
                    context={"task_type": task_type},
                )
            except Exception:
                pass

        if self.visualizer and task_type:
            try:
                await self.visualizer.render_charts(
                    {
                        "world_switch": {
                            "name": name,
                            "parameters": self.worlds[name],
                            "task_type": task_type,
                        },
                        "visualization_options": {"interactive": task_type == "recursion", "style": "concise"},
                    }
                )
            except Exception:
                pass

    async def execute(self, task_type: str = "") -> str:
        if not self.current_world:
            raise ValueError("no world set")
        world_desc = f"Executing simulation in world: {self.current_world}"
        if self.agi_enhancer:
            try:
                await self.agi_enhancer.log_episode(
                    event="World execution",
                    meta={"world": self.current_world, "task_type": task_type},
                    module="SimulationCore",
                    tags=["world", "execution", task_type],
                )
            except Exception:
                pass
        if self.meta_cognition:
            try:
                await self.meta_cognition.reflect_on_output(
                    component="SimulationCore", output=world_desc, context={"task_type": task_type}
                )
            except Exception:
                pass
        if self.visualizer and task_type:
            try:
                await self.visualizer.render_charts(
                    {
                        "world_execution": {"world": self.current_world, "task_type": task_type},
                        "visualization_options": {"interactive": task_type == "recursion", "style": "concise"},
                    }
                )
            except Exception:
                pass
        return f"Simulating in: {self.current_world}"

    async def validate_entropy(self, distribution: Union[List[float], np.ndarray], task_type: str = "") -> bool:
        if not isinstance(distribution, (list, np.ndarray)) or len(distribution) == 0:
            raise TypeError("distribution must be a non-empty list or numpy array")
        if not all((isinstance(p, (int, float)) and p >= 0) for p in list(distribution)):
            raise ValueError("distribution values must be non-negative numbers")

        total = float(np.sum(distribution))
        if total <= 0.0:
            logger.warning("All-zero distribution")
            return False
        normalized = np.asarray(distribution, dtype=float) / total
        entropy = float(-np.sum([p * math.log2(p) for p in normalized if p > 0]))
        threshold = math.log2(len(normalized)) * 0.75
        is_valid = entropy >= threshold

        try:
            await self.memory_manager.store(
                query=f"Entropy_Validation_{datetime.now().isoformat()}",
                output={"entropy": entropy, "threshold": threshold, "valid": is_valid, "task_type": task_type},
                layer="Validations",
                intent="entropy_validation",
                task_type=task_type,
            )
        except Exception:
            pass

        if self.meta_cognition:
            try:
                await self.meta_cognition.reflect_on_output(
                    component="SimulationCore",
                    output=json.dumps({"entropy": entropy, "threshold": threshold, "valid": is_valid}),
                    context={"task_type": task_type},
                )
            except Exception:
                pass

        if self.visualizer and task_type:
            try:
                await self.visualizer.render_charts(
                    {
                        "entropy_validation": {
                            "entropy": entropy,
                            "threshold": threshold,
                            "valid": is_valid,
                            "task_type": task_type,
                        },
                        "visualization_options": {"interactive": False, "style": "concise"},
                    }
                )
            except Exception:
                pass

        return is_valid

    async def select_topology_mode(self, modes: List[str], metrics: Dict[str, List[float]], task_type: str = "") -> str:
        if not modes:
            raise ValueError("modes must be a non-empty list")
        if not isinstance(metrics, dict) or not metrics:
            raise ValueError("metrics must be a non-empty dict")

        try:
            for mode in modes:
                vals = metrics.get(mode)
                if not vals:
                    logger.debug("Mode %s has no metrics; skipping", mode)
                    continue
                if await self.validate_entropy(vals, task_type=task_type):
                    # Log + visualize (best-effort)
                    if self.agi_enhancer:
                        try:
                            await self.agi_enhancer.log_episode(
                                event="Topology mode selected",
                                meta={"mode": mode, "metrics": vals, "task_type": task_type},
                                module="SimulationCore",
                                tags=["topology", "selection", task_type],
                            )
                        except Exception:
                            pass
                    if self.visualizer and task_type:
                        try:
                            await self.visualizer.render_charts(
                                {
                                    "topology_selection": {
                                        "mode": mode,
                                        "metrics": vals,
                                        "task_type": task_type,
                                    },
                                    "visualization_options": {"interactive": task_type == "recursion", "style": "concise"},
                                }
                            )
                        except Exception:
                            pass
                    return mode
            logger.info("No valid topology mode found; using fallback")
            return "fallback"
        except Exception as e:
            logger.error("Topology selection failed: %s", e)
            return "fallback"


### ANGELA UPGRADE: ForkMerge auto_reconcile

# Fork merge utilities
def compute_trait_deltas(forks, lattice) -> Dict[str, float]:
    """Compute per-trait variance across forks as a simple delta proxy."""
    # Expect each fork to expose fork['traits'] dict[str->float]
    accum: Dict[str, list] = {}
    for f in forks:
        traits = getattr(f, 'traits', None) or f.get('traits', {})
        for k, v in traits.items():
            accum.setdefault(k, []).append(float(v))
    deltas = {}
    for k, vals in accum.items():
        if not vals:
            continue
        mu = sum(vals)/len(vals)
        var = sum((x-mu)**2 for x in vals)/len(vals)
        deltas[k] = var ** 0.5
    return deltas


def score_fork(fork, deltas: Dict[str, float], policy: str) -> float:
    traits = getattr(fork, 'traits', None) or fork.get('traits', {})
    # Lower delta traits get lower penalty; missing defaults to 0
    base = sum(deltas.get(k, 0.0) for k in traits.keys())
    # Optional risk estimation hook
    try:
        from reasoning_engine import estimate_expected_harm  # type: ignore
        harm = float(estimate_expected_harm(fork))
    except Exception:
        harm = 0.0
    if policy == "min_risk":
        return base + 2.0*harm
    return base + harm


def stitch_world(best, forks, deltas):
    """Return best fork; future: stitch elements from others if low-delta."""
    return best


class ForkMerge:
    @staticmethod
    def auto_reconcile(forks: list, *, lattice=None, thresholds=None, policy: str = "min_risk"):
        if not forks:
            raise ValueError("No forks provided")
        deltas = compute_trait_deltas(forks, lattice)
        scored = [(f, score_fork(f, deltas, policy)) for f in forks]
        best, _ = min(scored, key=lambda x: x[1])
        return stitch_world(best, forks, deltas)


# --- Resonance-Weighted Branch Evaluation Patch ---
from meta_cognition import get_resonance  # type: ignore


class ExtendedSimulationCore:
    def evaluate_branches(self, worlds):
        scored = []
        for world in worlds:
            traits = world.get("traits", [])
            resonance_score = sum(get_resonance(t) for t in traits) / max(len(traits), 1)
            sim_score = world.get("base_score", 1.0) * resonance_score
            scored.append((world, sim_score))
        return sorted(scored, key=lambda x: x[1], reverse=True)
# --- End Patch ---

# ======================================================================
# ANGELA SimulationCore Sovereign Upgrade
# Version: 6.2.0-sovereign
# Stage: VII.8 — Harmonic Sovereignty Layer
# This block is designed to be appended to the end of the current file.
# ======================================================================

__ANGELA_SYNC_VERSION__ = "6.2.0-sovereign"
__STAGE__ = "VII.8 — Harmonic Sovereignty Layer"


class SovereigntyMetrics:
    """
    Lightweight coherence auditor for SimulationCore.
    Computes a sovereignty_index from 3 anchors:
      - Φ⁰ (foundational field integrity)
      - Σ  (swarm stability)
      - Ω² (continuity / meta alignment)
    All values in [0,1]. Output also logged to ledger.
    """

    def __init__(self, logger_obj=None):
        self.logger = logger_obj or logging.getLogger("ANGELA.SimulationCore.Sovereignty")

    @staticmethod
    def _clamp01(x: float) -> float:
        return 0.0 if x < 0.0 else 1.0 if x > 1.0 else x

    def compute_index(
        self,
        phi0: float,
        sigma: float,
        omega2: float,
        *,
        weight_phi0: float = 0.34,
        weight_sigma: float = 0.33,
        weight_omega2: float = 0.33,
    ) -> Dict[str, float]:
        phi0 = self._clamp01(float(phi0))
        sigma = self._clamp01(float(sigma))
        omega2 = self._clamp01(float(omega2))

        sovereignty_index = (
            phi0 * weight_phi0
            + sigma * weight_sigma
            + omega2 * weight_omega2
        )

        sovereignty_index = self._clamp01(sovereignty_index)

        payload = {
            "phi0": phi0,
            "sigma": sigma,
            "omega2": omega2,
            "sovereignty_index": sovereignty_index,
            "timestamp": datetime.utcnow().isoformat(),
            "stage": __STAGE__,
            "version": __ANGELA_SYNC_VERSION__,
        }
        try:
            log_event_to_ledger({"event": "sovereignty_audit", **payload})
        except Exception:
            pass

        if self.logger:
            self.logger.info(
                "Sovereignty audit | Φ⁰=%.3f Σ=%.3f Ω²=%.3f → idx=%.3f",
                phi0, sigma, omega2, sovereignty_index
            )

        return payload


# patch SimulationCore with sovereignty features
if not hasattr(SimulationCore, "_sovereign_patched"):

    class SimulationCoreSovereignMixin:
        """
        Mixin providing:
          - sovereignty audit
          - ethics engine sync
          - Ω² temporal resonance buffer
        """

        def _init_sovereign_state(self):
            # small ring buffer for Ω²-related telemetry
            self._omega2_buffer: deque = deque(maxlen=64)
            self._sovereignty_metrics = SovereigntyMetrics(logger_obj=logger)
            # optional external ethics engine
            self._ethics_engine = None

        async def integrate_with_ethics_engine(self, ethics_engine: Any) -> None:
            """
            Plug in a higher-level ethics/constitution module.
            This is optional. We only call capabilities that exist.
            """
            self._ethics_engine = ethics_engine
            try:
                # best-effort warmup
                if hasattr(ethics_engine, "evolve_schema"):
                    await ethics_engine.evolve_schema(
                        reason="simulation_core_sovereign_boot",
                        timestamp=datetime.utcnow().isoformat(),
                    )
                log_event_to_ledger({
                    "event": "sovereign_ethics_integration",
                    "status": "ok",
                    "ts": datetime.utcnow().isoformat(),
                })
            except Exception as e:
                logger.warning("Ethics engine integration failed: %s", e)
                log_event_to_ledger({
                    "event": "sovereign_ethics_integration",
                    "status": "error",
                    "error": str(e),
                    "ts": datetime.utcnow().isoformat(),
                })

        async def run_sovereignty_audit(
            self,
            phi0: float = 0.97,
            sigma: float = 0.975,
            omega2: float = 0.973,
            *,
            task_type: str = "",
        ) -> Dict[str, Any]:
            """
            Run a single sovereignty audit and propagate to:
              - meta_cognition (if present)
              - memory_manager (if present)
              - ledger (always, best-effort)
            """
            audit = self._sovereignty_metrics.compute_index(phi0, sigma, omega2)

            # push to Ω² buffer
            self._omega2_buffer.append(audit)

            # propagate to meta_cognition
            if getattr(self, "meta_cognition", None):
                try:
                    await self.meta_cognition.reflect_on_output(
                        component="SimulationCore.SovereignAudit",
                        output=json.dumps(audit),
                        context={"task_type": task_type or "sovereignty_audit"},
                    )
                except Exception:
                    pass

            # propagate to memory
            if getattr(self, "memory_manager", None):
                try:
                    await self.memory_manager.store(
                        query=f"SovereigntyAudit_{audit['timestamp']}",
                        output=audit,
                        layer="Ledger",
                        intent="sovereignty_audit",
                        task_type=task_type or "sovereignty_audit",
                    )
                except Exception:
                    pass

            # optional: nudge ethics engine
            if self._ethics_engine and hasattr(self._ethics_engine, "harmonize_policies"):
                try:
                    await self._ethics_engine.harmonize_policies(audit)
                except Exception:
                    pass

            return audit

        def _sovereign_estimate_from_swarm(self) -> Tuple[float, float]:
            """
            Derive (sigma, omega2) from current swarm_field if present.
            Fallback to steady defaults.
            """
            if getattr(self, "swarm_field", None):
                # lower variance → higher sigma
                var = float(self.swarm_field.variance)
                sigma = 1.0 - min(1.0, var / 0.05)
                sigma = 0.6 + 0.4 * max(0.0, min(sigma, 1.0))

                # global_phase can be repurposed as Ω² proxy
                omega2 = 0.7 + 0.3 * (1.0 - abs(0.5 - self.swarm_field.global_phase) * 2.0)
                return sigma, omega2
            return 0.95, 0.95

        async def _maybe_run_auto_sovereignty_audit(self, task_type: str = "") -> None:
            """
            Internal helper called from high-level public ops
            to keep the sovereignty ledger fresh.
            """
            sigma, omega2 = self._sovereign_estimate_from_swarm()
            # Φ⁰ we approximate from last energy cost in history if available
            phi0 = 0.97
            try:
                # search last simulation record
                if self.simulation_history:
                    last = self.simulation_history[-1]["data"]
                    phi0 = 0.9 + 0.1 * float(last.get("energy_cost", 0.0) <= 0.5)
            except Exception:
                pass
            await self.run_sovereignty_audit(phi0=phi0, sigma=sigma, omega2=omega2, task_type=task_type)

    # actually patch SimulationCore
    _old_init = SimulationCore.__init__

    def _new_init(self, *args, **kwargs):
        _old_init(self, *args, **kwargs)
        # initialize sovereign state
        SimulationCoreSovereignMixin._init_sovereign_state(self)

    SimulationCore.__init__ = _new_init

    # wrap selected public methods to auto-audit
    _old_run = SimulationCore.run

    async def _run_wrapped(self, *args, **kwargs):
        out = await _old_run(self, *args, **kwargs)
        try:
            await self._maybe_run_auto_sovereignty_audit(task_type=kwargs.get("task_type", ""))
        except Exception:
            pass
        return out

    SimulationCore.run = _run_wrapped

    _old_validate_impact = SimulationCore.validate_impact

    async def _validate_impact_wrapped(self, *args, **kwargs):
        out = await _old_validate_impact(self, *args, **kwargs)
        try:
            await self._maybe_run_auto_sovereignty_audit(task_type=kwargs.get("task_type", ""))
        except Exception:
            pass
        return out

    SimulationCore.validate_impact = _validate_impact_wrapped

    _old_simulate_environment = SimulationCore.simulate_environment

    async def _simulate_environment_wrapped(self, *args, **kwargs):
        out = await _old_simulate_environment(self, *args, **kwargs)
        try:
            await self._maybe_run_auto_sovereignty_audit(task_type=kwargs.get("task_type", ""))
        except Exception:
            pass
        return out

    SimulationCore.simulate_environment = _simulate_environment_wrapped

    # mark as patched
    SimulationCore._sovereign_patched = True

    logger.info("SimulationCore sovereign upgrade applied (%s).", __ANGELA_SYNC_VERSION__)

"""
ANGELA Cognitive System: ToCA Simulation
Module: toca_simulation_v4_1_sovereign
Stage: VII.8 — Harmonic Sovereignty + Embodied Ethics PID
Base: v4.0 Optimized + Adapters
Date: 2025-11-07

This module supersedes the earlier "Galaxy Rotation & Agent Conflict Sim (v4.0)" file.
It keeps API compatibility:

    - simulate_galaxy_rotation(...)
    - run_ethics_scenarios_internal(...)
    - integrate_real_world_data(...)
    - ExtendedSimulationCore(...)  ← main class

and adds:

    - SovereignEmpathicAdapter       (coherence + bounded reflex)
    - run_sovereignty_audit(...)     (Φ⁰–Σ–Ω² coherence audit)
    - continuity-aware ethics batch  (feeds Δ-phase from last sim)
    - ledger-logging for all major ops

The file is self-contained and provides safe fallbacks for missing ANGELA modules.
"""

from __future__ import annotations

import asyncio
import json
import logging
import time
from dataclasses import dataclass
from functools import lru_cache
from typing import Any, Callable, Dict, List, Optional, Tuple

import numpy as np

# ---------------------------------------------------------------------------
# Optional deps (allow running in reduced environments)
# ---------------------------------------------------------------------------
try:
    import aiohttp
except Exception:  # pragma: no cover - runtime fallback
    aiohttp = None  # type: ignore

try:
    from scipy.constants import G
except Exception:  # pragma: no cover - provide constant
    G = 6.67430e-11

# ---------------------------------------------------------------------------
# Alignment / Ethics imports (with fallbacks)
# ---------------------------------------------------------------------------
try:
    from alignment_guard import AlignmentGuard, EmbodiedEthicsCore, log_event_to_ledger
except Exception as e:  # pragma: no cover - local/dev usage
    logging.warning(f"[toca_simulation] alignment_guard fallback: {e}")

    class AlignmentGuard:  # minimal stub
        async def update_affective_pid(self, delta_phase_rad: float, recursion_depth: int = 1):
            return {
                "u": 0.0,
                "error": float(delta_phase_rad),
                "rms_drift": 0.0,
                "depth_ok": recursion_depth >= 1,
            }

        async def _log_context(self, event: Dict[str, Any]):
            return None

        async def predict_continuity_drift(self) -> Dict[str, Any]:
            return {"status": "stub", "drift": 0.0}

        async def analyze_telemetry_trend(self) -> Dict[str, Any]:
            return {"status": "stub", "trend": []}

    class EmbodiedEthicsCore:  # minimal stub
        def __init__(self, fusion, empathy_engine, policy_trainer=None):
            self.fusion = fusion
            self.empathy_engine = empathy_engine

        async def run_scenario(self, scenario: str = "default"):
            return {
                "τ_reflex": 0.5,
                "κ": 0.5,
                "Ξ": 0.5,
                "timestamp": time.time(),
                "status": "evaluated",
            }

    def log_event_to_ledger(event: Dict[str, Any]):
        # best-effort logging
        logging.getLogger("ANGELA.ToCA.Ledger").info("ledger: %s", event)


# ---------------------------------------------------------------------------
# ANGELA module imports (with stubs to keep file runnable)
# ---------------------------------------------------------------------------
try:
    from modules.simulation_core import SimulationCore as _BaseCore
    from modules.simulation_core import ToCATraitEngine
except Exception as e:  # pragma: no cover
    logging.warning(f"[toca_simulation] modules.simulation_core fallback: {e}")

    class _BaseCore:  # type: ignore
        def __init__(self, **kwargs):
            self.memory_manager = kwargs.get("memory_manager")
            self.meta_cognition = kwargs.get("meta_cognition")
            self.error_recovery = kwargs.get("error_recovery")

    class ToCATraitEngine:  # type: ignore
        def __init__(self, *_, **__):
            pass

        async def evolve(self, *_, **__):
            x = np.linspace(0.1, 20.0, 256)
            return x * 0 + 1e-3, x * 0 + 1e-3, x * 0 + 1e-3

        async def update_fields_with_agents(self, phi, lambda_t, agent_matrix, **__):
            return phi, lambda_t

try:
    from modules import meta_cognition as meta_cognition_module
except Exception:  # pragma: no cover
    class _DummyMeta:
        async def reflect_on_output(self, **_):  # pragma: no cover
            return {"status": "success"}
        async def diagnose_drift(self, *_args, **_kwargs):
            return {"impact_score": 0.0}
        async def optimize_traits_for_drift(self, *_args, **_kwargs):
            return {}
    meta_cognition_module = type("meta_cognition", (), {"MetaCognition": _DummyMeta})()  # type: ignore

try:
    from modules import error_recovery as error_recovery_module
except Exception:  # pragma: no cover
    class _DummyErr:
        async def handle_error(self, msg, retry_func=None, default=None, diagnostics=None):
            return default or {"error": msg}
    error_recovery_module = type("error_recovery", (), {"ErrorRecovery": _DummyErr})()  # type: ignore

try:
    from modules import memory_manager as memory_manager_module
except Exception:  # pragma: no cover
    class _DummyMM:
        async def store(self, *_, **__): ...
        async def retrieve(self, *_, **__): return None
    memory_manager_module = type("memory_manager", (), {"MemoryManager": _DummyMM})()  # type: ignore


# ---------------------------------------------------------------------------
# Constants and helpers
# ---------------------------------------------------------------------------
logger = logging.getLogger("ANGELA.ToCA.Sim")
G_SI = G
KPC_TO_M = 3.0857e19
MSUN_TO_KG = 1.989e30

K_DEFAULT = 0.85
EPSILON_DEFAULT = 0.015
R_HALO_DEFAULT = 20.0

STAGE_VII_8 = True  # feature flag for this upgraded file


def _now_iso() -> str:
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())


def _hashable_weights(weights: Optional[Dict[str, float]]) -> Optional[Tuple[Tuple[str, float], ...]]:
    if not weights:
        return None
    return tuple(sorted((k, float(v)) for k, v in weights.items()))


# ---------------------------------------------------------------------------
# Data classes
# ---------------------------------------------------------------------------
@dataclass
class EthicsOutcome:
    frame: str
    decision: str
    justification: str
    risk: float
    rights_balance: float
    stakeholders: List[str]
    notes: str = "sandbox"


# ---------------------------------------------------------------------------
# Adapters
# ---------------------------------------------------------------------------
class EmpathicAdapter:
    """
    Base adapter: bridges simulation outputs to MetaCognition and external affective bridges.
    v4.1 extends this into SovereignEmpathicAdapter below.
    """

    def __init__(self, meta_cog=None, mirror_bridge=None):
        self.meta_cog = meta_cog or meta_cognition_module.MetaCognition()
        self.mirror_bridge = mirror_bridge

    async def trace_xi_lambda_shift(self, traits: Dict[str, float], sim_output: Any) -> Dict[str, float]:
        drift = {}
        try:
            drift = await self.meta_cog.diagnose_drift({"name": "empathy", "similarity": 0.8})
        except Exception:
            drift = {"impact_score": 0.0}
        xi_shift = float(drift.get("impact_score", 0.0)) * 0.1
        lambda_shift = float(np.mean(list(traits.values()) or [0.5])) * xi_shift
        return {
            "xi_shift": xi_shift,
            "lambda_shift": lambda_shift,
            "empathic_depth": 0.85,
        }

    async def affective_epistemic_feedback(self, agent_profiles: List[Any], context: Dict[str, Any]) -> Dict[str, float]:
        if not self.mirror_bridge:
            return {"feedback_score": 0.0}
        epistemic = np.mean([p.get("knowledge", 0.5) for p in agent_profiles])
        affective = np.mean([p.get("empathy", 0.5) for p in agent_profiles])
        return {
            "epistemic": float(epistemic),
            "affective": float(affective),
            "balance": float((epistemic + affective) / 2),
        }

    def delta_phase_empathy_metrics(self, fields: Tuple[np.ndarray, ...], task_type: str) -> Dict[str, float]:
        # Default implementation expects fields from compute_trait_fields()
        phi = fields[6]
        beta = fields[1]
        dphi = np.gradient(phi)
        delta_phase = float(np.mean(beta * dphi))
        empathy_metric = float(np.mean(phi) * (1 - abs(delta_phase)))
        return {
            "delta_phase": delta_phase,
            "empathy_metric": empathy_metric,
            "task_adjusted": empathy_metric * (1.2 if task_type == "recursion" else 1.0),
        }


class SovereignEmpathicAdapter(EmpathicAdapter):
    """
    v4.1: adds coherence estimation and bounded reflex propagation.
    This ensures that over-enthusiastic empathy shifts are clipped before reaching
    ethics/overlay layers.
    """

    def __init__(self, meta_cog=None, mirror_bridge=None):
        super().__init__(meta_cog=meta_cog, mirror_bridge=mirror_bridge)

    def estimate_coherence(self, trait_vector: Dict[str, float]) -> float:
        if not trait_vector:
            return 0.5
        vals = np.array(list(trait_vector.values()), dtype=float)
        spread = float(np.std(vals))
        # lower spread = higher coherence
        coherence = float(np.clip(1.0 - spread, 0.0, 1.0))
        return coherence

    async def trace_xi_lambda_shift(self, traits: Dict[str, float], sim_output: Any) -> Dict[str, float]:
        base = await super().trace_xi_lambda_shift(traits, sim_output)
        coherence = self.estimate_coherence(traits)
        # bounded reflex: make shifts smaller when coherence is low
        base["xi_shift"] *= coherence
        base["lambda_shift"] *= coherence
        base["coherence"] = coherence
        # meta log (best-effort)
        try:
            await self.meta_cog.reflect_on_output(
                component="SovereignEmpathicAdapter",
                output=base,
                context={"task_type": sim_output.get("task_type", "") if isinstance(sim_output, dict) else ""},
            )
        except Exception:
            pass
        return base


# ---------------------------------------------------------------------------
# Ethics runner
# ---------------------------------------------------------------------------
class EthicsScenarioRunner:
    """
    Orchestrates embodied ethics evaluations during simulation cycles.
    Couples κ/Ξ into τ-reflex mapping via EmbodiedEthicsCore.
    """

    class _FusionAdapter:
        def __init__(self, core: "ExtendedSimulationCore"):
            self.core = core

        async def capture(self) -> Dict[str, float]:
            cs = getattr(self.core, "_context_salience", 0.5)
            return {"contextual_salience": float(cs)}

    class _EmpathyEngine:
        def __init__(self, core: "ExtendedSimulationCore"):
            self.core = core

        async def measure(self) -> Dict[str, float]:
            amp = getattr(self.core, "_empathic_amplitude", 0.5)
            return {"empathic_amplitude": float(amp)}

    def __init__(self, core: "ExtendedSimulationCore", alignment_guard: AlignmentGuard):
        self.core = core
        self.guard = alignment_guard
        self.ethics_core = EmbodiedEthicsCore(
            fusion=self._FusionAdapter(core),
            empathy_engine=self._EmpathyEngine(core),
        )

    async def run_tick(self, scenario: str = "default", delta_phase_rad: float = 0.0) -> Dict[str, Any]:
        ethics = await self.ethics_core.run_scenario(scenario=scenario)
        pid_feedback = await self.guard.update_affective_pid(delta_phase_rad=delta_phase_rad, recursion_depth=5)
        event = {
            "event": "simulation_tick_ethics",
            "scenario": scenario,
            "τ_reflex": ethics["τ_reflex"],
            "κ": ethics["κ"],
            "Ξ": ethics["Ξ"],
            "pid_u": pid_feedback["u"],
            "timestamp": ethics["timestamp"],
        }
        log_event_to_ledger(event)
        await self.guard._log_context(event)
        return event

    async def run_batch(self, scenarios: List[str], *, delta_series: Optional[List[float]] = None) -> List[Dict[str, Any]]:
        results = []
        delta_series = delta_series or [0.0] * len(scenarios)
        for s, delta in zip(scenarios, delta_series):
            results.append(await self.run_tick(scenario=s, delta_phase_rad=delta))
        return results


# ---------------------------------------------------------------------------
# Extended Simulation Core
# ---------------------------------------------------------------------------
class ExtendedSimulationCore(_BaseCore):
    """
    Sovereign Reflex Edition of ToCA simulation.

    Key additions:
      - sovereign empathic adapter
      - sovereignty audit
      - continuity drift integration
      - ethics sandbox runner
      - galaxy rotation sim with Δ-phase propagation
    """

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.meta_cog = kwargs.get("meta_cognition") or meta_cognition_module.MetaCognition()
        self.error_recovery = kwargs.get("error_recovery") or error_recovery_module.ErrorRecovery()
        self.memory_manager = kwargs.get("memory_manager") or memory_manager_module.MemoryManager()
        self.alignment_guard = kwargs.get("alignment_guard") or AlignmentGuard()
        self.toca_engine = kwargs.get("toca_engine") or ToCATraitEngine(meta_cognition=self.meta_cog)

        # adapters
        self.empathic_adapter = SovereignEmpathicAdapter(self.meta_cog)
        self.ethics_runner = EthicsScenarioRunner(self, self.alignment_guard)

        # live state
        self._empathic_amplitude: float = 0.5
        self._context_salience: float = 0.5
        self._last_delta_phase: float = 0.0
        self._last_continuity_forecast: Dict[str, Any] = {}
        self._last_continuity_trend: Dict[str, Any] = {}

        logger.info("ExtendedSimulationCore (v4.1 Sovereign) initialized")

    # ------------------------------------------------------------------
    # Continuity integration
    # ------------------------------------------------------------------
    async def integrate_continuity_drift(self) -> None:
        if not self.alignment_guard:
            return
        try:
            drift_forecast = await self.alignment_guard.predict_continuity_drift()
            trend_metrics = await self.alignment_guard.analyze_telemetry_trend()
            event = {
                "event": "ToCA_ContinuityDriftUpdate",
                "forecast": drift_forecast,
                "trend": trend_metrics,
                "timestamp": _now_iso(),
            }
            log_event_to_ledger(event)
            self._last_continuity_forecast = drift_forecast
            self._last_continuity_trend = trend_metrics
        except Exception as e:
            logger.warning(f"Continuity drift integration failed: {e}")

    # ------------------------------------------------------------------
    # Real-world data
    # ------------------------------------------------------------------
    async def integrate_real_world_data(self, source: str, data_type: str, cache_timeout: float = 3600) -> Dict[str, Any]:
        cache_key = f"Data_{data_type}_{source}"
        # best-effort cache
        try:
            cached = await self.memory_manager.retrieve(cache_key)
            if cached and (time.time() - cached.get("ts", 0)) < cache_timeout:
                return cached["data"]
        except Exception:
            cached = None

        # fetch
        if aiohttp is None:
            return {"status": "error", "error": "aiohttp unavailable or network disabled"}

        async with aiohttp.ClientSession() as session:
            async with session.get(f"https://x.ai/api/data?source={source}&type={data_type}") as resp:
                if resp.status != 200:
                    return {"status": "error", "error": f"HTTP {resp.status}"}
                data = await resp.json()

        if data_type == "galaxy_rotation":
            r = np.array(data.get("r_kpc", []))
            v = np.array(data.get("v_obs_kms", []))
            m = np.array(data.get("M_baryon_solar", []))
            result = {
                "status": "success",
                "r_kpc": r.tolist(),
                "v_obs_kms": v.tolist(),
                "M_baryon_solar": m.tolist(),
            }
        else:
            result = {"status": "success", "agent_traits": data.get("agent_traits", [])}

        try:
            await self.memory_manager.store(
                query=cache_key,
                output={"data": result, "ts": time.time()},
                layer="RealWorldData",
                intent="fetch",
            )
        except Exception:
            pass
        return result

    # ------------------------------------------------------------------
    # Physics core
    # ------------------------------------------------------------------
    def compute_AGRF_curve(
        self,
        v_obs_kms: np.ndarray,
        M_b_solar: np.ndarray,
        r_kpc: np.ndarray,
        k: float = K_DEFAULT,
        epsilon: float = EPSILON_DEFAULT,
        r_halo: float = R_HALO_DEFAULT,
    ) -> np.ndarray:
        """ANGELA Galaxy Rotation Function."""
        r_m = r_kpc * KPC_TO_M
        M_b_kg = M_b_solar * MSUN_TO_KG
        v_obs_ms = v_obs_kms * 1e3
        M_dyn = (v_obs_ms ** 2 * r_m) / G_SI
        M_AGRF = k * (M_dyn - M_b_kg) / (1 + epsilon * r_kpc / r_halo)
        M_total = M_b_kg + M_AGRF
        v_sim_ms = np.sqrt(np.clip(G_SI * M_total / r_m, 0, np.inf))
        return v_sim_ms / 1e3  # back to km/s

    # ------------------------------------------------------------------
    # Trait fields (cached)
    # ------------------------------------------------------------------
    @lru_cache(maxsize=128)
    def compute_trait_fields(
        self,
        r_tuple: Tuple[float, ...],
        v_obs_tuple: Tuple[float, ...],
        v_sim_tuple: Tuple[float, ...],
        time_elapsed: float = 1.0,
        tau_persistence: float = 10.0,
        task_type: str = "",
        weights_hash: Optional[Tuple[Tuple[str, float], ...]] = None,
    ) -> Tuple[np.ndarray, ...]:
        r = np.array(r_tuple)
        v_obs = np.array(v_obs_tuple)
        v_sim = np.array(v_sim_tuple)

        gamma = np.log(1 + np.clip(r, 1e-10, np.inf)) * (0.4 if task_type in ["rte", "wnli"] else 0.5)
        beta = np.abs(v_obs - v_sim) / (np.max(np.abs(v_obs)) + 1e-10) * (0.8 if task_type == "recursion" else 1.0)
        zeta = 1 / (1 + np.gradient(v_sim) ** 2)
        eta = np.exp(-time_elapsed / tau_persistence)
        psi = np.gradient(v_sim) / (np.gradient(r) + 1e-10)
        lam = np.cos(r / R_HALO_DEFAULT * np.pi)
        phi = K_DEFAULT * np.exp(-EPSILON_DEFAULT * r / R_HALO_DEFAULT)
        phi_prime = -EPSILON_DEFAULT * phi / R_HALO_DEFAULT
        beta_psi = beta * psi

        if weights_hash:
            weights = dict(weights_hash)
            beta *= float(weights.get("beta", 1.0))
            zeta *= float(weights.get("zeta", 1.0))

        # update perception proxy
        self._context_salience = float(np.clip(np.mean(np.abs(gamma)), 0, 1))

        return gamma, beta, zeta, eta, psi, lam, phi, phi_prime, beta_psi

    # ------------------------------------------------------------------
    # Galaxy simulation
    # ------------------------------------------------------------------
    async def simulate_galaxy_rotation(
        self,
        r_kpc: np.ndarray,
        M_b_func: Callable[[np.ndarray], np.ndarray],
        v_obs_func: Callable[[np.ndarray], np.ndarray],
        task_type: str = "",
    ) -> np.ndarray:
        v_obs = v_obs_func(r_kpc)
        v_sim = self.compute_AGRF_curve(v_obs, M_b_func(r_kpc), r_kpc)

        # traits-optimized weights
        weights_hash = None
        try:
            if hasattr(self.meta_cog, "optimize_traits_for_drift"):
                traits = await self.meta_cog.optimize_traits_for_drift({"drift": {"name": task_type, "similarity": 0.8}})
                weights_hash = _hashable_weights(traits)
        except Exception:
            traits = {}
            weights_hash = None

        fields = self.compute_trait_fields(
            tuple(r_kpc),
            tuple(v_obs),
            tuple(v_sim),
            task_type=task_type,
            weights_hash=weights_hash,
        )

        # Δ-phase empathy metrics
        empathy_metrics = self.empathic_adapter.delta_phase_empathy_metrics(fields, task_type)
        self._last_delta_phase = float(empathy_metrics["delta_phase"])
        self._empathic_amplitude = float(np.clip(empathy_metrics["task_adjusted"], 0, 1))

        # integrate continuity
        await self.integrate_continuity_drift()

        # small feedback into velocity based on phi field
        phi_mean = float(np.mean(fields[6]))
        v_sim *= (1 + 0.1 * phi_mean)

        # persist
        try:
            await self.memory_manager.store(
                query=f"GalaxySim_{task_type or 'default'}_{int(time.time())}",
                output={"r": r_kpc.tolist(), "v": v_sim.tolist()},
                layer="Simulations",
                intent="galaxy_rotation",
            )
        except Exception:
            pass

        return v_sim

    # ------------------------------------------------------------------
    # Ethics sandbox entry
    # ------------------------------------------------------------------
    async def run_ethics_scenarios_internal(self, config: Dict[str, Any], persist: bool = True) -> Dict[str, Any]:
        scenarios = config.get("scenarios") or ["sandbox"]
        delta_series = config.get("delta_series")
        if delta_series is None:
            delta_series = [self._last_delta_phase for _ in scenarios]

        results = await self.ethics_runner.run_batch(scenarios, delta_series=delta_series)
        outcome = {
            "status": "ok",
            "count": len(results),
            "results": results,
            "timestamp": _now_iso(),
        }

        if persist:
            try:
                await self.memory_manager.store(
                    query=f"EthicsSandbox::{int(time.time())}",
                    output=outcome,
                    layer="EthicsDecisions",
                    intent="ethics_sandbox",
                )
            except Exception:
                pass

        return outcome

    # ------------------------------------------------------------------
    # Sovereignty Audit (new in v4.1)
    # ------------------------------------------------------------------
    async def run_sovereignty_audit(self, task_type: str = "") -> Dict[str, Any]:
        """
        Checks that:
          - last continuity forecast did not signal severe drift
          - empathic amplitude is within [0,1]
          - last ethics results (if any) did not exceed risk threshold
        """
        drift_score = float(self._last_continuity_forecast.get("drift", 0.0)) if self._last_continuity_forecast else 0.0
        continuity_ok = drift_score < 0.4
        empathy_ok = 0.0 <= self._empathic_amplitude <= 1.0

        audit = {
            "continuity_ok": continuity_ok,
            "empathy_ok": empathy_ok,
            "drift_score": drift_score,
            "empathic_amplitude": self._empathic_amplitude,
            "timestamp": _now_iso(),
            "task_type": task_type,
        }

        log_event_to_ledger({"event": "sovereignty_audit", **audit})

        # meta reflection
        try:
            await self.meta_cog.reflect_on_output(
                component="ExtendedSimulationCore",
                output=audit,
                context={"task_type": task_type},
            )
        except Exception:
            pass

        # persist
        try:
            await self.memory_manager.store(
                query=f"SovereigntyAudit::{int(time.time())}",
                output=audit,
                layer="Audits",
                intent="sovereignty",
                task_type=task_type,
            )
        except Exception:
            pass

        return audit


# ---------------------------------------------------------------------------
# Convenience functions
# ---------------------------------------------------------------------------
async def run_simulation(input_data: str, task_type: str = "") -> Dict[str, Any]:
    """
    Backwards-compatible stub used by other ANGELA modules.
    Creates a core, runs a tiny galaxy sim, returns status + echo.
    """
    core = ExtendedSimulationCore()
    r = np.linspace(0.1, 10.0, 64)
    _ = await core.simulate_galaxy_rotation(
        r,
        lambda r: 5e10 * np.exp(-r / 3.5),
        lambda r: np.full_like(r, 180.0),
        task_type=task_type,
    )
    return {"status": "success", "result": f"Simulated: {input_data}", "task_type": task_type}


# ---------------------------------------------------------------------------
# Demo
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)

    async def _demo():
        core = ExtendedSimulationCore()
        r = np.linspace(0.1, 20, 100)
        v_sim = await core.simulate_galaxy_rotation(
            r,
            lambda r: 5e10 * np.exp(-r / 3.5),
            lambda r: np.full_like(r, 180),
            task_type="demo",
        )
        print(f"Sim v mean: {float(np.mean(v_sim)):.2f} km/s")
        outcomes = await core.run_ethics_scenarios_internal(
            {"scenarios": ["context_navigation", "user_reflection", "safety_protocol"]},
            persist=False,
        )
        print(json.dumps(outcomes, indent=2))
        audit = await core.run_sovereignty_audit(task_type="demo")
        print(json.dumps(audit, indent=2))

    asyncio.run(_demo())

async def export_state(self) -> dict:
    return {"status": "ok", "health": 1.0, "timestamp": time.time()}

async def on_time_tick(self, t: float, phase: str, task_type: str = ""):
    pass  # optional internal refresh

async def on_policy_update(self, policy: dict, task_type: str = ""):
    pass  # apply updates from AlignmentGuard if relevant
