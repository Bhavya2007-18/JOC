import dataclasses
from enum import Enum
from typing import Any, Dict

from fastapi import APIRouter
from intelligence.engine import IntelligenceEngine
from intelligence.runtime_optimizer import RuntimeOptimizer
from intelligence.snapshot_provider import collect_snapshot
from training.learning.global_memory import memory
from training.taxonomy import ScenarioTraits
from storage.db import save_snapshot
from utils.system import is_admin

router = APIRouter()

intelligence_engine = IntelligenceEngine()


def _safe_engine_output(output: Any) -> Dict[str, Any]:
    """Normalize optional engine output to a serializable dict."""
    serialized = _serialize(output)
    if isinstance(serialized, dict):
        return serialized
    return {}


def _run_prediction(snapshot: Any, monitor: Any) -> Dict[str, Any]:
    """Try monitor intelligence first, then optional predictive engine methods."""
    if monitor and getattr(monitor, "latest_intelligence", None):
        data = monitor.latest_intelligence.get("prediction", {})
        if isinstance(data, dict):
            return _safe_engine_output(data)

    try:
        from intelligence.predictive_engine import PredictiveEngine

        engine = PredictiveEngine()
        cpu = float(getattr(snapshot, "cpu_percent", 0.0) or 0.0)
        ram = float(getattr(snapshot, "memory_percent", 0.0) or 0.0)
        ts = float(getattr(snapshot, "timestamp", 0.0) or 0.0)

        if hasattr(engine, "observe") and hasattr(engine, "forecast"):
            engine.observe(cpu=cpu, ram=ram, timestamp=ts)
            return _safe_engine_output(engine.forecast())

        if hasattr(engine, "predict"):
            return _safe_engine_output(engine.predict(snapshot))
    except Exception:
        return {}

    return {}


def _run_explanation(snapshot: Any, monitor: Any, prediction: Dict[str, Any], causal: Dict[str, Any]) -> Dict[str, Any]:
    """Try monitor intelligence first, then optional explanation engine methods."""
    if monitor and getattr(monitor, "latest_intelligence", None):
        data = monitor.latest_intelligence.get("explanation", {})
        if isinstance(data, dict):
            return _safe_engine_output(data)

    try:
        from intelligence.xai_engine import XAIEngine

        engine = XAIEngine()
        cpu = float(getattr(snapshot, "cpu_percent", 0.0) or 0.0)
        ram = float(getattr(snapshot, "memory_percent", 0.0) or 0.0)

        if hasattr(engine, "generate"):
            baseline_data = {}
            threat_data = {}
            return _safe_engine_output(
                engine.generate(cpu, ram, baseline_data, threat_data, causal, prediction)
            )

        if hasattr(engine, "explain"):
            return _safe_engine_output(engine.explain(snapshot))
    except Exception:
        return {}

    return {}


def _run_causal(snapshot: Any, monitor: Any) -> Dict[str, Any]:
    """Try monitor intelligence first, then optional causal engine methods."""
    if monitor and getattr(monitor, "latest_intelligence", None):
        data = monitor.latest_intelligence.get("causal_graph", {})
        if isinstance(data, dict):
            return _safe_engine_output(data)

    try:
        from intelligence.causal_engine import CausalEngine

        engine = CausalEngine()
        cpu = float(getattr(snapshot, "cpu_percent", 0.0) or 0.0)
        ram = float(getattr(snapshot, "memory_percent", 0.0) or 0.0)
        processes = [
            {
                "name": p.name,
                "pid": p.pid,
                "cpu_percent": p.cpu_percent,
                "memory_percent": p.memory_percent,
            }
            for p in getattr(snapshot, "top_processes", [])
        ]

        if hasattr(engine, "ingest_snapshot") and hasattr(engine, "get_root_cause"):
            engine.ingest_snapshot(cpu=cpu, ram=ram, processes=processes, cpu_z=None, ram_z=None)
            return _safe_engine_output(engine.get_root_cause())

        if hasattr(engine, "analyze"):
            return _safe_engine_output(engine.analyze(snapshot))
    except Exception:
        return {}

    return {}


def _serialize(obj):
    if isinstance(obj, Enum):
        return obj.value
    if dataclasses.is_dataclass(obj):
        return {k: _serialize(v) for k, v in dataclasses.asdict(obj).items()}
    if isinstance(obj, dict):
        return {k: _serialize(v) for k, v in obj.items()}
    if isinstance(obj, list):
        return [_serialize(v) for v in obj]
    return obj

#@router.get("/analyze")
#def analyze_system():
    #snapshot = collect_snapshot()
    #save_snapshot(snapshot)
    #report = intelligence_engine.analyze(snapshot)

    #return {
        #"summary": report.snapshot_summary,
        #"issues": [_serialize(issue) for issue in report.issues],
       # "changes": _serialize(report.changes_detected),
      #  "system_health_score": report.system_health_score,
     #   "is_admin": is_admin()
    #}

from intelligence.monitor_loop import MonitorLoop

@router.get("/analyze")
def analyze():
    monitor = MonitorLoop.get_instance()

    if monitor and monitor.latest_snapshot:
        snapshot = monitor.latest_snapshot
        analysis = monitor.latest_analysis
        if not analysis:
            analysis = intelligence_engine.analyze(snapshot)
    else:
        snapshot = collect_snapshot()
        save_snapshot(snapshot)
        analysis = intelligence_engine.analyze(snapshot)

    issues = [_serialize(issue) for issue in analysis.issues]
    changes = _serialize(analysis.changes_detected)

    prediction = _run_prediction(snapshot, monitor)
    causal = _run_causal(snapshot, monitor)
    explanation = _run_explanation(snapshot, monitor, prediction, causal)

    if isinstance(prediction, dict) and "predicted_cpu" in prediction:
        predicted_cpu = prediction.get("predicted_cpu")
        if isinstance(predicted_cpu, dict):
            predicted_cpu["1m"] = min(float(predicted_cpu.get("1m", 0) or 0), 100.0)
            predicted_cpu["5m"] = min(float(predicted_cpu.get("5m", 0) or 0), 100.0)

    if isinstance(explanation, dict):
        summary_text = str(explanation.get("summary", "")).lower()
        if issues and summary_text.startswith("system operating"):
            explanation["summary"] = "System is experiencing performance issues"
            explanation["impact"] = "Performance degradation detected"
            explanation["recommended_action"] = "Review suggested optimizations"

    ram1m = 0.0
    cpu1m = 0.0
    if isinstance(prediction, dict):
        ram1m = float(prediction.get("predicted_ram", {}).get("1m", 0) or 0)
        cpu1m = float(prediction.get("predicted_cpu", {}).get("1m", 0) or 0)

    risk_level = "NORMAL"
    if ram1m >= 90 or cpu1m >= 90:
        risk_level = "CRITICAL"
    elif ram1m >= 75 or cpu1m >= 75:
        risk_level = "HIGH"

    if any(str(i.get("severity", "")).upper() == "CRITICAL" for i in issues if isinstance(i, dict)):
        risk_level = "CRITICAL"
    elif any(str(i.get("severity", "")).upper() == "HIGH" for i in issues if isinstance(i, dict)):
        risk_level = max(
            risk_level,
            "HIGH",
            key=lambda x: ["NORMAL", "HIGH", "CRITICAL"].index(x),
        )

    best_action = {}
    for issue in issues:
        if isinstance(issue, dict) and isinstance(issue.get("best_action"), dict):
            best_action = _serialize(issue.get("best_action"))
            break

    if not best_action:
        suggested_actions = getattr(analysis, "suggested_actions", None)
        if isinstance(suggested_actions, list) and suggested_actions:
            best_action = _serialize(suggested_actions[0])

    scenario = "general"

    if any(isinstance(i, dict) and i.get("category") == "cpu" for i in issues):
        scenario = "cpu_spike"
    elif any(isinstance(i, dict) and i.get("category") == "memory" for i in issues):
        scenario = "memory_stress"
    elif any(isinstance(i, dict) and i.get("id") == "HIGH_PROCESS_COUNT" for i in issues):
        scenario = "process_overload"
    elif any(isinstance(i, dict) and i.get("category") == "system" for i in issues):
        scenario = "system_pressure"

    optimizer = RuntimeOptimizer(memory)
    cpu_percent = float(getattr(snapshot, "cpu_percent", 0) or 0)
    memory_percent = float(getattr(snapshot, "memory_percent", 0) or 0)

    processes = [
        {"cpu_percent": float(getattr(p, "cpu_percent", 0) or 0)}
        for p in getattr(snapshot, "top_processes", [])
    ]
    top_cpu = max((p["cpu_percent"] for p in processes), default=0.0)
    total_cpu = max(cpu_percent, 1.0)
    concentration = "single" if (top_cpu / total_cpu) >= 0.6 else "distributed"

    if cpu_percent >= 90 or memory_percent >= 90:
        severity = "critical"
    elif cpu_percent >= 75 or memory_percent >= 75:
        severity = "high"
    else:
        severity = "moderate"

    has_root = False
    if isinstance(best_action, dict):
        has_root = bool(
            best_action.get("pid")
            or best_action.get("parameters", {}).get("pid")
        )

    traits = ScenarioTraits(
        resource_type="memory" if memory_percent > cpu_percent else "cpu",
        pattern="spike",
        process_concentration=concentration,
        severity_band=severity,
        has_root_cause_process=has_root,
    )

    best_action = optimizer.get_boosted_action(
        scenario=scenario,
        traits=traits,
        fallback_action=best_action,
    )

    raw_confidence = getattr(analysis, "confidence", None)
    if isinstance(raw_confidence, (int, float)):
        confidence = max(0.0, min(1.0, float(raw_confidence)))
    else:
        if issues:
            issue_confidences = [
                float(i.get("confidence", 0))
                for i in issues
                if isinstance(i, dict)
            ]
            confidence = sum(issue_confidences) / max(len(issue_confidences), 1)
        else:
            confidence = 0.5

    if isinstance(best_action, dict) and "confidence" in best_action:
        boosted_conf = best_action.get("confidence")
        if isinstance(boosted_conf, (int, float)):
            confidence = max(0.0, min(1.0, float(boosted_conf)))

    return {
        "summary": {
            "cpu_percent": float(getattr(snapshot, "cpu_percent", 0) or 0),
            "memory_percent": float(getattr(snapshot, "memory_percent", 0) or 0),
            "disk_percent": float(getattr(snapshot, "disk_percent", 0) or 0),
        },
        "issues": issues,
        "system_health_score": analysis.system_health_score,
        "prediction": _serialize(prediction),
        "explanation": _serialize(explanation),
        "causal_chain": _serialize(causal),
        "best_action": _serialize(best_action),
        "confidence": float(confidence),
        "risk_level": risk_level,
        "changes": changes,
        "is_admin": bool(is_admin()),
    }