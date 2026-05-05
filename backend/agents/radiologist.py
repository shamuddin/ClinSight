from backend.core.state import AgentState
from backend.agents.subgraphs import image_prep, pathology_analyzer
from datetime import datetime

async def radiologist_agent(state: AgentState) -> AgentState:
    """Agent 2: Image prep, pathology analysis, attention regions.
    Delegates to subagents: Image Prep, Pathology Analyzer.
    """
    audit = state.get("audit_log", [])

    # Delegate to subagents
    state = image_prep(state)
    state = await pathology_analyzer(state)

    audit_log = state.get("audit_log", [])
    audit_log.append({
        "agent": "radiologist",
        "timestamp": datetime.utcnow().isoformat(),
        "action": "image_analysis",
        "findings_count": len(state.get("findings", [])),
    })
    state["audit_log"] = audit_log
    return state
