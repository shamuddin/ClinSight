from backend.core.state import AgentState
from backend.agents.subgraphs import esi_scorer_sub, differential_builder
from datetime import datetime

async def clinical_documenter_agent(state: AgentState) -> AgentState:
    """Agent 5: ESI scorer, differential builder, report generation.
    Delegates to subagents: ESI Scorer, Differential Builder.
    """
    # Delegate to subagents
    state = esi_scorer_sub(state)
    state = differential_builder(state)

    actions = suggest_actions(state)
    state["suggested_actions"] = actions
    state["report"] = {
        "esi": {"level": state["esi_level"], "description": state["esi_description"], "rules": state["esi_rules_triggered"]},
        "differential": state["differential"],
        "actions": actions,
        "safety_summary": {
            "contradictions": len(state.get("contradictions", [])),
            "hallucinations": len(state.get("hallucination_flags", [])),
            "bias_flags": len(state.get("bias_flags", [])),
        }
    }

    audit_log = state.get("audit_log", [])
    audit_log.append({
        "agent": "clinical_documenter",
        "timestamp": datetime.utcnow().isoformat(),
        "action": "report_generation",
        "esi": state["esi_level"],
        "differential_count": len(state["differential"]),
    })
    state["audit_log"] = audit_log
    return state


def suggest_actions(state: AgentState) -> list[str]:
    esi = state.get("esi_level", 5)
    if esi == 1:
        return ["Immediate bedside evaluation", "Contact trauma/critical care team", "Prepare for intervention"]
    elif esi == 2:
        return ["Urgent physician assessment", "Consider ICU admission", "Serial vitals and labs"]
    elif esi == 3:
        return ["Physician evaluation within 30 minutes", "Order follow-up imaging if indicated"]
    elif esi == 4:
        return ["Standard ED workup", "Follow-up imaging if needed"]
    return ["Routine workup and disposition"]
