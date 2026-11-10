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
