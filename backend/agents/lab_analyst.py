from backend.core.state import AgentState
from backend.agents.subgraphs import critical_value_detector, pattern_correlator
from datetime import datetime

async def lab_analyst_agent(state: AgentState) -> AgentState:
    """Agent 3: Critical value detection, pattern correlation.
    Delegates to subagents: Critical Value Detector, Pattern Correlator.
    """
    # Delegate to subagents
    state = critical_value_detector(state)
    state = pattern_correlator(state)

    audit_log = state.get("audit_log", [])
    audit_log.append({
        "agent": "lab_analyst",
        "timestamp": datetime.utcnow().isoformat(),
        "action": "lab_analysis",
        "alerts_count": len(state.get("lab_alerts", [])),
        "patterns": state.get("lab_patterns", []),
    })
    state["audit_log"] = audit_log
    return state
