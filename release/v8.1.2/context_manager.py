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
