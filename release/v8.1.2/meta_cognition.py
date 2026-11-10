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
