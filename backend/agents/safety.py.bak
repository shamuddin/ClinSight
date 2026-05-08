from backend.core.state import AgentState
from backend.agents.subgraphs import (
    contradiction_checker,
    hallucination_guard,
    bias_auditor,
    safety_merge,
)
from datetime import datetime

async def safety_agent(state: AgentState) -> AgentState:
    """Agent 4: Contradiction checker, hallucination guard, bias auditor (parallel in graph).
    Delegates to subagents: Contradiction Checker, Hallucination Guard, Bias Auditor, Safety Merge.
    """
    # Delegate to subagents
    state = contradiction_checker(state)
    state = hallucination_guard(state)
    state = bias_auditor(state)
    state = safety_merge(state)

    audit_log = state.get("audit_log", [])
    audit_log.append({
        "agent": "safety",
        "timestamp": datetime.utcnow().isoformat(),
        "action": "safety_review",
        "flags_total": len(state.get("merged_flags", [])),
        "downgrades": state.get("safety_downgrades", 0),
    })
    state["audit_log"] = audit_log
    return state
