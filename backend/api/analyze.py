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

    result = analysis

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

    fallback_action = {}
    result_issues = getattr(result, "issues", None)
    if isinstance(result_issues, list) and result_issues:
        first_issue_action = getattr(result_issues[0], "best_action", None)
        if isinstance(first_issue_action, dict):
            fallback_action = _serialize(first_issue_action)

    if not fallback_action:
        suggested_actions = getattr(result, "suggested_actions", None)
        if isinstance(suggested_actions, list) and suggested_actions:
            fallback_action = _serialize(suggested_actions[0])

    if isinstance(fallback_action, dict) and fallback_action:
        fallback_action.setdefault("source", "engine")

    cpu_percent = float(getattr(snapshot, "cpu_percent", 0) or 0)
    memory_percent = float(getattr(snapshot, "memory_percent", 0) or 0)

    top_processes = getattr(snapshot, "top_processes", [])
    max_process_memory = max(
        (float(getattr(p, "memory_percent", 0) or 0) for p in top_processes),
        default=0.0,
    )
    total_memory = max(memory_percent, 1.0)
    memory_is_distributed = max_process_memory < 0.3 * total_memory

    scenario = "cpu_spike"
    if any(isinstance(i, dict) and i.get("category") == "memory" for i in issues) or memory_percent > cpu_percent:
        scenario = "distributed_memory_leak" if memory_is_distributed else "memory_leak"

    if scenario == "distributed_memory_leak":
        if max_process_memory < 0.3 * total_memory:
            concentration = "distributed"
        else:
            concentration = "single"
    else:
        top_cpu = max(
            (float(getattr(p, "cpu_percent", 0) or 0) for p in top_processes),
            default=0.0,
        )
        total_cpu = max(cpu_percent, 1.0)
        concentration = "single" if (top_cpu / total_cpu) >= 0.6 else "distributed"

    if cpu_percent >= 90:
        severity = "critical"
    elif cpu_percent >= 75:
        severity = "high"
    else:
        severity = "moderate"

    has_root = False
    if isinstance(fallback_action, dict):
        has_root = bool(
            fallback_action.get("pid")
            or fallback_action.get("parameters", {}).get("pid")
        )

    traits = ScenarioTraits(
        resource_type="memory" if memory_percent > cpu_percent else "cpu",
        pattern="leak" if scenario in ["memory_leak", "distributed_memory_leak"] else "spike",
        process_concentration=concentration,
        severity_band=severity,
        has_root_cause_process=has_root,
    )

    optimizer = RuntimeOptimizer(memory)
    boosted_action = optimizer.get_boosted_action(
        scenario=scenario,
        traits=traits,
        fallback_action=fallback_action,
    )
    best_action = boosted_action if isinstance(boosted_action, dict) else {}

    if best_action and "source" not in best_action:
        best_action["source"] = "engine"

    multi_actions = []

    for issue in result.issues:
        try:
            fallback_action = getattr(issue, "best_action", None)

            if not isinstance(fallback_action, dict):
                continue

            category = getattr(issue, "category", "system")
            category_value = getattr(category, "value", category)
            issue_id = getattr(issue, "id", "")

            if category_value == "memory":
                scenario_name = "memory_leak"
            elif category_value == "cpu":
                scenario_name = "cpu_spike"
            elif issue_id == "STARTUP_LOAD":
                scenario_name = "startup_load"
            elif issue_id in ["HIGH_SERVICE_COUNT", "HEAVY_SERVICES"]:
                scenario_name = "service_overload"
            elif issue_id == "HIGH_PROCESS_COUNT":
                scenario_name = "process_overload"
            else:
                scenario_name = "system_misc"

            traits_local = ScenarioTraits(
                resource_type="memory" if memory_percent > cpu_percent else "cpu",
                pattern="leak" if scenario_name == "memory_leak" else "spike",
                process_concentration=concentration,
                severity_band=severity,
                has_root_cause_process=bool(
                    fallback_action.get("pid")
                    or fallback_action.get("parameters", {}).get("pid")
                ),
            )

            optimizer_issue = RuntimeOptimizer(memory)
            action = optimizer_issue.get_boosted_action(
                scenario=scenario_name,
                traits=traits_local,
                fallback_action=fallback_action,
            )
            if not isinstance(action, dict):
                action = fallback_action

            action_type = action.get("action_type")
            if not action_type:
                continue

            multi_actions.append({
                "issue_id": getattr(issue, "id", "unknown"),
                "category": str(getattr(issue, "category", "")),
                "action_type": action_type,
                "target": action.get("target"),
                "parameters": action.get("parameters", {}),
                "confidence": action.get("confidence", 0.5),
                "source": action.get("source", "per_issue_engine")
            })

        except Exception:
            continue

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

    if best_action and "confidence" not in best_action:
        best_action["confidence"] = float(confidence)

    if isinstance(best_action, dict) and best_action.get("action_type"):
        try:
            action_type = best_action.get("action_type")

            # Estimate impact (simple heuristic for now)
            estimated_improvement = 0.0

            if action_type == "kill_process":
                estimated_improvement = float(memory_percent or 0.0) * 0.1
            elif action_type == "system_tweak":
                estimated_improvement = float(cpu_percent or 0.0) * 0.05

            impact_score = float(estimated_improvement) * 0.7

            # Update memory using SAME scenario + traits already computed
            memory.update(
                scenario,
                traits,
                action_type,
                impact_score,
            )

        except Exception:
            # Never break API due to learning failure
            pass

    for issue in result.issues:
        try:
            if not issue.best_action:
                continue

            action = issue.best_action
            action_type = action.get("action_type")

            if not action_type:
                continue

            # Detect scenario based on issue category
            category = getattr(issue, "category", "system")
            category_value = getattr(category, "value", category)

            if category_value == "memory":
                scenario_name = "memory_leak"
            elif category_value == "cpu":
                scenario_name = "cpu_spike"
            else:
                scenario_name = "system_load"

            # Reuse same traits logic (copy from earlier traits block)
            traits_local = ScenarioTraits(
                resource_type=traits.resource_type,
                pattern=traits.pattern,
                process_concentration=traits.process_concentration,
                severity_band=traits.severity_band,
                has_root_cause_process=bool(
                    action.get("pid")
                    or action.get("parameters", {}).get("pid")
                ),
            )

            # Estimate impact (simple heuristic)
            est_improvement = 0.0

            if action_type == "kill_process":
                est_improvement = float(memory_percent or 0.0) * 0.1
            elif action_type == "system_tweak":
                est_improvement = float(cpu_percent or 0.0) * 0.05

            impact_score = float(est_improvement) * 0.7

            memory.update(
                scenario_name,
                traits_local,
                action_type,
                impact_score,
            )

        except Exception:
            continue

    insights_scenario = "memory_leak" if memory_percent > cpu_percent else "cpu_spike"

    top_cpu_insight = max(
        (float(getattr(p, "cpu_percent", 0) or 0) for p in top_processes),
        default=0.0,
    )
    total_cpu_insight = max(cpu_percent, 1.0)
    insights_concentration = "single" if (top_cpu_insight / total_cpu_insight) >= 0.6 else "distributed"

    if cpu_percent >= 90:
        insights_severity = "critical"
    elif cpu_percent >= 75:
        insights_severity = "high"
    else:
        insights_severity = "moderate"

    insights_traits = ScenarioTraits(
        resource_type="memory" if memory_percent > cpu_percent else "cpu",
        pattern="leak" if memory_percent > cpu_percent else "spike",
        process_concentration=insights_concentration,
        severity_band=insights_severity,
        has_root_cause_process=bool(
            isinstance(best_action, dict) and best_action.get("pid")
        ),
    )

    learned_action = memory.get_best_action(insights_scenario, insights_traits)
    learned_action_type = None
    if isinstance(learned_action, dict):
        learned_action_type = learned_action.get("action_type")

    avg_impact = None
    scenario_index = getattr(memory, "scenario_index", {})
    if isinstance(scenario_index, dict):
        scenario_stats = scenario_index.get(insights_scenario, {})
        if isinstance(scenario_stats, dict) and learned_action_type in scenario_stats:
            action_stats = scenario_stats.get(learned_action_type, {})
            if isinstance(action_stats, dict):
                raw_avg_impact = action_stats.get("avg_impact")
                if isinstance(raw_avg_impact, (int, float)):
                    avg_impact = float(raw_avg_impact)

    decision_source = best_action.get("source") if isinstance(best_action, dict) else None
    if decision_source == "memory_override":
        insights_explanation = "Memory override applied: learned action outperformed engine fallback."
    elif decision_source == "engine+memory":
        insights_explanation = "Engine action confirmed by learned memory and confidence boosted."
    elif decision_source == "memory":
        insights_explanation = "No engine fallback was available, so learned memory action was used."
    else:
        insights_explanation = "Engine decision used; no stronger learned override matched this state."

    engine_action = fallback_action.get("action_type") if isinstance(fallback_action, dict) else None
    final_action = best_action.get("action_type") if isinstance(best_action, dict) else None
    override = decision_source == "memory_override"

    engine_estimated = None
    if isinstance(fallback_action, dict):
        candidate_impact = fallback_action.get("estimated_impact")
        if not isinstance(candidate_impact, (int, float)):
            candidate_impact = fallback_action.get("avg_impact")
        if isinstance(candidate_impact, (int, float)):
            engine_estimated = float(candidate_impact)

    learning_insights = {
        "scenario_detected": insights_scenario,
        "matched_traits": {
            "resource_type": insights_traits.resource_type,
            "pattern": insights_traits.pattern,
            "process_concentration": insights_traits.process_concentration,
            "severity_band": insights_traits.severity_band,
        },
        "learned_action": learned_action_type,
        "avg_impact": avg_impact,
        "decision_source": decision_source,
        "explanation": insights_explanation,
        "engine_action": engine_action,
        "final_action": final_action,
        "override": override,
        "impact_comparison": {
            "learned_avg": avg_impact,
            "engine_estimated": engine_estimated,
        },
    }

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
        "recommended_actions": multi_actions,
        "confidence": float(confidence),
        "risk_level": risk_level,
        "learning_insights": learning_insights,
        "changes": changes,
        "is_admin": bool(is_admin()),
    }