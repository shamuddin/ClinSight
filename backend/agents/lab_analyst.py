from backend.core.state import AgentState
from backend.safety.rules import check_lab_thresholds
from datetime import datetime

async def lab_analyst_agent(state: AgentState) -> AgentState:
    """Agent 3: Critical value detection, pattern correlation."""
    audit = state.get("audit_log", [])
    labs = state.get("lab_values", {})
    units = state.get("lab_units", {})

    alerts = check_lab_thresholds(labs, units)
    patterns = _detect_patterns(alerts, labs)

    state["lab_alerts"] = alerts
    state["lab_patterns"] = patterns
    state["lab_correlation"] = {"status": "analyzed", "matches": len(alerts), "mismatches": 0}

    audit.append({
        "agent": "lab_analyst",
        "timestamp": datetime.utcnow().isoformat(),
        "action": "lab_analysis",
        "alerts_count": len(alerts),
        "patterns": patterns,
    })
    state["audit_log"] = audit
    return state


def _detect_patterns(alerts: list, labs: dict) -> list:
    patterns = []
    codes = {a["code"] for a in alerts}
    if "HIGH_WBC" in codes and "ELEVATED_LACTATE" in codes:
        patterns.append("SEPSIS_PATTERN")
    if "HYPOXEMIA" in codes and "ELEVATED_LACTATE" in codes:
        patterns.append("SHOCK_PATTERN")
    if "ELEVATED_TROPONIN" in codes and "HYPOXEMIA" in codes:
        patterns.append("MI_PATTERN")
    return patterns
