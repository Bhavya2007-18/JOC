from typing import Optional

from fastapi import APIRouter, Query

from models.intelligence_models import (
    AnomaliesResponse,
    Anomaly,
    AnomalySeverity,
    BehaviorLogEntry,
    BehaviorProcessSnapshot,
    ConfidenceLevel,
    Decision,
    DecisionSuggestedAction,
    DecisionsResponse,
    FrequentAppInfo,
    HourlyUsageInfo,
    LogResponse,
    PatternsResponse,
    TimeSeriesPoint,
)
from services.intelligence import (
    append_log_entry,
    compute_patterns,
    detect_anomalies,
    generate_decisions,
)
from services.system_monitor import get_cpu_stats, get_memory_stats, get_top_processes
from intelligence.monitor_loop import MonitorLoop


router = APIRouter(prefix="/intelligence", tags=["intelligence"])


@router.post("/log", response_model=LogResponse)
def log_current_state() -> LogResponse:
    cpu = get_cpu_stats()
    memory = get_memory_stats()
    processes = get_top_processes(limit=5)

    entry_dict = append_log_entry(
        cpu_percent=float(cpu.get("usage_percent", 0.0)),
        memory_percent=float(memory.get("percent", 0.0)),
        top_processes=processes,
    )

    entry_model = BehaviorLogEntry(
        timestamp=entry_dict["timestamp"],
        hour_of_day=entry_dict["hour_of_day"],
        cpu_percent=entry_dict["cpu_percent"],
        memory_percent=entry_dict["memory_percent"],
        top_processes=[
            BehaviorProcessSnapshot(
                pid=proc["pid"],
                name=proc["name"],
                cpu_percent=proc["cpu_percent"],
                memory_percent=proc["memory_percent"],
            )
            for proc in entry_dict["top_processes"]
        ],
    )

    return LogResponse(success=True, entry=entry_model)


@router.get("/patterns", response_model=PatternsResponse)
def get_patterns(window_minutes: Optional[int] = Query(default=60, ge=1, le=1440)) -> PatternsResponse:
    window_seconds = None if window_minutes is None else window_minutes * 60
    patterns = compute_patterns(window_seconds=window_seconds)

    peak_hours = [
        HourlyUsageInfo(
            hour=item["hour"],
            average_cpu_percent=item["average_cpu_percent"],
            average_memory_percent=item["average_memory_percent"],
        )
        for item in patterns.get("peak_hours", [])
    ]

    frequent_apps = [
        FrequentAppInfo(
            name=item["name"],
            count=item["count"],
            average_cpu_percent=item["average_cpu_percent"],
        )
        for item in patterns.get("frequent_apps", [])
    ]

    timeseries = [
        TimeSeriesPoint(
            timestamp=item["timestamp"],
            cpu_percent=item["cpu_percent"],
            memory_percent=item["memory_percent"],
        )
        for item in patterns.get("cpu_memory_timeseries", [])
    ]

    return PatternsResponse(
        average_cpu_percent=patterns["average_cpu_percent"],
        average_memory_percent=patterns["average_memory_percent"],
        peak_hours=peak_hours,
        idle_hours=patterns.get("idle_hours", []),
        frequent_apps=frequent_apps,
        cpu_memory_timeseries=timeseries,
    )


@router.get("/anomalies", response_model=AnomaliesResponse)
def get_anomalies(window_minutes: Optional[int] = Query(default=60, ge=1, le=1440)) -> AnomaliesResponse:
    window_seconds = None if window_minutes is None else window_minutes * 60
    raw_anomalies = detect_anomalies(window_seconds=window_seconds)

    anomalies = [
        Anomaly(
            id=item["id"],
            type=item["type"],
            timestamp=item["timestamp"],
            description=item["description"],
            severity=AnomalySeverity(item["severity"]),
            data=item.get("data", {}),
        )
        for item in raw_anomalies
    ]

    return AnomaliesResponse(anomalies=anomalies)


@router.get("/decisions", response_model=DecisionsResponse)
def get_decisions(window_minutes: Optional[int] = Query(default=60, ge=1, le=1440)) -> DecisionsResponse:
    window_seconds = None if window_minutes is None else window_minutes * 60
    raw_decisions = generate_decisions(window_seconds=window_seconds)

    decisions = []
    for item in raw_decisions:
        confidence_value = item.get("confidence", "medium")
        actions = [
            DecisionSuggestedAction(
                action_type=action["action_type"],
                target=action["target"],
                parameters=action.get("parameters", {}),
            )
            for action in item.get("suggested_actions", [])
        ]
        decisions.append(
            Decision(
                decision=item["decision"],
                reason=item["reason"],
                confidence=ConfidenceLevel(confidence_value),
                data_used=item.get("data_used", {}),
                related_anomalies=item.get("related_anomalies", []),
                suggested_actions=actions,
            )
        )

    return DecisionsResponse(decisions=decisions)

@router.get("/threat")
def get_threat():
    monitor = MonitorLoop.get_instance()
    if monitor and hasattr(monitor, 'latest_intelligence'):
        return monitor.latest_intelligence.get("threat", {})
    return {"status": "loading_engines"}

@router.get("/prediction")
def get_prediction():
    monitor = MonitorLoop.get_instance()
    if monitor and hasattr(monitor, 'latest_intelligence'):
        return monitor.latest_intelligence.get("prediction", {})
    return {"status": "loading_engines"}

@router.get("/explanation")
def get_explanation():
    monitor = MonitorLoop.get_instance()
    if monitor and hasattr(monitor, 'latest_intelligence'):
        return monitor.latest_intelligence.get("explanation", {})
    return {"status": "loading_engines"}

@router.get("/causal-graph")
def get_causal_graph():
    monitor = MonitorLoop.get_instance()
    if monitor and hasattr(monitor, 'latest_intelligence'):
        return monitor.latest_intelligence.get("causal_graph", {})
    return {"nodes": [], "edges": [], "root_cause_node": None}

@router.get("/full")
def get_full_intelligence():
    monitor = MonitorLoop.get_instance()
    if monitor and hasattr(monitor, 'latest_intelligence'):
        return monitor.latest_intelligence
    return {"status": "loading_engines"}
